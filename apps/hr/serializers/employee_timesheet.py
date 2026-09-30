from collections import defaultdict
from decimal import ROUND_HALF_UP, Decimal

from django.db import IntegrityError, transaction
from django.utils import timezone
from rest_framework import serializers

from apps.base.serializers import BaseModelSerializer

from ..models import (
    Employee,
    EmployeeTimesheet,
    EmployeeTimesheetItem,
    RecruitmentDismissal,
)
from ..models.employee_timesheet import current_year
from ..services.employee_status import employed_on, was_employed_on
from ..services.timesheet import ensure_draft

TIME_FIELDS = ["input_date", "output_lunch_date", "input_lunch_date", "output_date"]
MAX_BULK_ROWS = 2000
HOURS_KWARGS = {"min_value": 0, "max_value": 24}


def check_time_order(values):
    """Kelish/tushlik/ketish vaqtlari to'g'ri ketma-ketlikda ekanini tekshiradi.

    Xato bo'lsa `(maydon, xabar)` juftligini qaytaradi, aks holda `None`.
    """
    if bool(values["output_lunch_date"]) != bool(values["input_lunch_date"]):
        return "input_lunch_date", "Tushlik vaqti ikkalasi ham kiritilishi kerak."
    given = [values[name] for name in TIME_FIELDS if values[name]]
    if given != sorted(given):
        return (
            "non_field_errors",
            (
                "Vaqtlar tartibi noto'g'ri: kelish ≤ tushlikka chiqish ≤ "
                "tushlikdan kelish ≤ ketish bo'lishi kerak."
            ),
        )
    return None


def calculate_fact_hours(values):
    """Vaqtlardan haqiqiy ish soatini (tushlik ayirilgan holda) hisoblaydi."""
    if not (values["input_date"] and values["output_date"]):
        return None
    worked = values["output_date"] - values["input_date"]
    if values["output_lunch_date"] and values["input_lunch_date"]:
        worked -= values["input_lunch_date"] - values["output_lunch_date"]
    hours = Decimal(worked.total_seconds()) / Decimal(3600)
    return hours.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)


def check_branch_access(user, timesheet):
    """Foydalanuvchining tabel filialiga ruxsati borligini tekshiradi."""
    if user.is_system_admin:
        return
    if not user.get_accessible_branches().filter(pk=timesheet.branch_id).exists():
        raise serializers.ValidationError(
            {
                "employee_timesheet": "Sizda ushbu filial uchun ma'lumot yaratish huquqi yo'q."
            }
        )


def check_date_matches_timesheet(local_date, timesheet):
    """Qator sanasi tabel yili va oyiga mos kelishini tekshiradi; xato xabarini qaytaradi."""
    if local_date.year != timesheet.year:
        return "Sana tabel yiliga mos kelishi kerak."
    if local_date.month != timesheet.for_month:
        return "Sana tabel oyiga mos kelishi kerak."
    return None


class EmployeeTimesheetSerializer(BaseModelSerializer):
    items_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = EmployeeTimesheet
        fields = [
            "id",
            "tab_number",
            "branch",
            "year",
            "for_month",
            "status",
            "items_count",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["status", "tab_number"]
        related_fields = {
            "branch": {"fields": ["id", "name"]},
        }

    def validate(self, attrs):
        """Holat, davrni o'zgartirish va bir filial+yil+oy uchun yagonalikni tekshiradi."""
        if self.instance is not None:
            ensure_draft(self.instance)
            self._ensure_period_unchanged(attrs)
        self._ensure_unique(attrs)
        return attrs

    def _ensure_period_unchanged(self, attrs):
        """Qatorlari bor tabelning filiali, yili yoki oyini o'zgartirishni taqiqlaydi."""
        changed = any(
            name in attrs and attrs[name] != getattr(self.instance, name)
            for name in ("branch", "year", "for_month")
        )
        has_items = EmployeeTimesheetItem.objects.active().filter(
            employee_timesheet=self.instance
        )
        if changed and has_items.exists():
            raise serializers.ValidationError(
                "Qatorlari bor tabelning filiali, yili yoki oyini o'zgartirib bo'lmaydi."
            )

    def _ensure_unique(self, attrs):
        """Bir filial, yil va oy uchun faqat bitta (bekor qilinmagan) tabel bo'lishi kerak."""
        current = self.instance
        branch = attrs.get("branch", getattr(current, "branch", None))
        year = attrs.get("year", getattr(current, "year", None)) or current_year()
        month = attrs.get("for_month", getattr(current, "for_month", None))
        duplicates = (
            EmployeeTimesheet.objects.active()
            .filter(branch=branch, year=year, for_month=month)
            .exclude(status=EmployeeTimesheet.Status.CANCELLED)
        )
        if current is not None:
            duplicates = duplicates.exclude(pk=current.pk)
        if duplicates.exists():
            raise serializers.ValidationError(
                "Bu filial, yil va oy uchun tabel allaqachon mavjud."
            )

    def create(self, validated_data):
        """Bir vaqtda kelgan ikkinchi so'rovni bazadagi cheklov orqali xatoga aylantiradi."""
        try:
            with transaction.atomic():
                return super().create(validated_data)
        except IntegrityError:
            raise serializers.ValidationError(
                "Bu filial, yil va oy uchun tabel allaqachon mavjud."
            )


class EmployeeTimesheetItemSerializer(BaseModelSerializer):
    class Meta:
        model = EmployeeTimesheetItem
        fields = [
            "id",
            "employee_timesheet",
            "employee",
            "date",
            "work_hour_in_plan",
            "input_date",
            "output_lunch_date",
            "input_lunch_date",
            "output_date",
            "work_hour_in_fact",
            "created_at",
            "updated_at",
        ]
        extra_kwargs = {
            "work_hour_in_plan": HOURS_KWARGS,
            "work_hour_in_fact": HOURS_KWARGS,
        }
        related_fields = {
            "employee_timesheet": {
                "fields": ["id", "branch", "year", "for_month", "status"]
            },
            "employee": {"fields": ["id", "full_name"]},
        }

    def _value(self, attrs, name):
        """Yangi qiymatni, bo'lmasa mavjud obyektdagi qiymatni qaytaradi."""
        return attrs.get(name, getattr(self.instance, name, None))

    def validate(self, attrs):
        """Tabel holati, yil/oy, filial, xodim ishlaganligi, kun takri va vaqt tartibini tekshiradi."""
        timesheet = self._value(attrs, "employee_timesheet")
        employee = self._value(attrs, "employee")
        date = self._value(attrs, "date")

        self._validate_timesheet(attrs, timesheet)
        check_branch_access(self.context["request"].user, timesheet)
        self._validate_employee_and_date(timesheet, employee, date)
        self._validate_time_order(attrs)
        self._fill_fact_hours(attrs)
        return attrs

    def _validate_timesheet(self, attrs, timesheet):
        """Tabel(lar) qoralama holatda ekanini tekshiradi."""
        ensure_draft(timesheet)
        if self.instance is not None:
            ensure_draft(self.instance.employee_timesheet)

    def _validate_employee_and_date(self, timesheet, employee, date):
        """Xodim filiali va ishlaganligi, sana yil/oyi va kun takrorini tekshiradi."""
        if employee.branch_id != timesheet.branch_id:
            raise serializers.ValidationError(
                {"employee": "Xodim tabel filialiga tegishli emas."}
            )
        local_date = timezone.localtime(date).date()
        date_error = check_date_matches_timesheet(local_date, timesheet)
        if date_error:
            raise serializers.ValidationError({"date": date_error})
        if not was_employed_on(employee, timesheet.branch, local_date):
            raise serializers.ValidationError(
                {"employee": "Xodim shu sanada bu filialda ishlamagan."}
            )
        duplicates = EmployeeTimesheetItem.objects.active().filter(
            employee_timesheet=timesheet, employee=employee, date__date=local_date
        )
        if self.instance is not None:
            duplicates = duplicates.exclude(pk=self.instance.pk)
        if duplicates.exists():
            raise serializers.ValidationError(
                {"date": "Bu xodim uchun shu kunga qator allaqachon mavjud."}
            )

    def _validate_time_order(self, attrs):
        """Kelish/tushlik/ketish vaqtlari to'g'ri ketma-ketlikda ekanini tekshiradi."""
        values = {name: self._value(attrs, name) for name in TIME_FIELDS}
        error = check_time_order(values)
        if error:
            field, message = error
            raise serializers.ValidationError(
                message if field == "non_field_errors" else {field: message}
            )

    def _fill_fact_hours(self, attrs):
        """`work_hour_in_fact` berilmasa, vaqtlardan avtomatik hisoblaydi."""
        times_sent = any(name in attrs for name in TIME_FIELDS)
        if "work_hour_in_fact" in attrs or not (self.instance is None or times_sent):
            return
        values = {name: self._value(attrs, name) for name in TIME_FIELDS}
        hours = calculate_fact_hours(values)
        if hours is not None:
            attrs["work_hour_in_fact"] = hours


class TimesheetRowSerializer(serializers.Serializer):
    """`bulk-create` ichidagi bitta qator (xodim va kun) ma'lumotlari."""

    employee = serializers.UUIDField()
    date = serializers.DateTimeField()
    work_hour_in_plan = serializers.DecimalField(
        max_digits=5, decimal_places=2, required=False, allow_null=True, **HOURS_KWARGS
    )
    input_date = serializers.DateTimeField(required=False, allow_null=True)
    output_lunch_date = serializers.DateTimeField(required=False, allow_null=True)
    input_lunch_date = serializers.DateTimeField(required=False, allow_null=True)
    output_date = serializers.DateTimeField(required=False, allow_null=True)
    work_hour_in_fact = serializers.DecimalField(
        max_digits=5, decimal_places=2, required=False, allow_null=True, **HOURS_KWARGS
    )


class EmployeeTimesheetItemBulkCreateSerializer(serializers.Serializer):
    """Bir tabelga bir nechta qatorni bir so'rovda qo'shadi (hammasi yoki hech narsa)."""

    employee_timesheet = serializers.PrimaryKeyRelatedField(
        queryset=EmployeeTimesheet.objects.active().select_related("branch")
    )
    items = TimesheetRowSerializer(
        many=True, allow_empty=False, max_length=MAX_BULK_ROWS
    )

    def validate(self, attrs):
        """Tabel holati/ruxsati va har bir qatorni tekshiradi; xatolar qator tartibi bilan qaytadi."""
        timesheet = attrs["employee_timesheet"]
        ensure_draft(timesheet)
        check_branch_access(self.context["request"].user, timesheet)

        rows = attrs["items"]
        context = self._load_context(timesheet, rows)
        seen = set()
        errors = []
        for row in rows:
            row_errors = self._check_row(timesheet, row, context, seen)
            errors.append(row_errors)
        if any(errors):
            raise serializers.ValidationError({"items": errors})
        return attrs

    def _load_context(self, timesheet, rows):
        """Tekshiruv uchun xodimlar, ish tarixi va mavjud qatorlarni bir necha so'rov bilan oladi."""
        employee_ids = {row["employee"] for row in rows}
        employees = {
            employee.pk: employee
            for employee in Employee.objects.active().filter(pk__in=employee_ids)
        }
        history = defaultdict(list)
        records = (
            RecruitmentDismissal.objects.filter(
                branch=timesheet.branch,
                employee_id__in=employee_ids,
                status=RecruitmentDismissal.Status.APPROVED,
                is_active=True,
            )
            .order_by("employee_id", "-rec_dism_date", "-created_at")
            .values_list("employee_id", "rec_dism_date", "type")
        )
        for employee_id, record_date, record_type in records:
            history[employee_id].append((record_date, record_type))
        existing = {
            (employee_id, timezone.localtime(date).date())
            for employee_id, date in EmployeeTimesheetItem.objects.active()
            .filter(employee_timesheet=timesheet, employee_id__in=employee_ids)
            .values_list("employee_id", "date")
        }
        return {"employees": employees, "history": history, "existing": existing}

    def _check_row(self, timesheet, row, context, seen):
        """Bitta qatorni tekshiradi va xatolar lug'atini qaytaradi (bo'sh bo'lsa xato yo'q)."""
        employee = context["employees"].get(row["employee"])
        if employee is None:
            return {"employee": ["Xodim topilmadi."]}
        if employee.branch_id != timesheet.branch_id:
            return {"employee": ["Xodim tabel filialiga tegishli emas."]}
        local_date = timezone.localtime(row["date"]).date()
        date_error = check_date_matches_timesheet(local_date, timesheet)
        if date_error:
            return {"date": [date_error]}
        if not employed_on(context["history"][employee.pk], local_date):
            return {"employee": ["Xodim shu sanada bu filialda ishlamagan."]}
        key = (employee.pk, local_date)
        if key in context["existing"] or key in seen:
            return {"date": ["Bu xodim uchun shu kunga qator allaqachon mavjud."]}
        seen.add(key)
        values = {name: row.get(name) for name in TIME_FIELDS}
        error = check_time_order(values)
        if error:
            return {error[0]: [error[1]]}
        if row.get("work_hour_in_fact") is None:
            row["work_hour_in_fact"] = calculate_fact_hours(values)
        return {}

    @transaction.atomic
    def create(self, validated_data):
        """Qatorlarni birma-bir yaratadi (audit yozuvlari saqlansin), xato bo'lsa hammasi bekor."""
        timesheet = validated_data["employee_timesheet"]
        created = []
        for row in validated_data["items"]:
            data = dict(row)
            employee_id = data.pop("employee")
            created.append(
                EmployeeTimesheetItem.objects.create(
                    employee_timesheet=timesheet, employee_id=employee_id, **data
                )
            )
        return EmployeeTimesheetItem.objects.filter(
            pk__in=[item.pk for item in created]
        ).select_related("employee", "employee_timesheet__branch")


class EmployeeTimesheetCountSerializer(serializers.Serializer):
    """Tabellar sonining status bo'yicha javobi (faqat hujjat uchun)."""

    all = serializers.IntegerField(help_text="Barcha tabellar soni.")
    draft = serializers.IntegerField(help_text="Qoralama.")
    approved = serializers.IntegerField(help_text="Tasdiqlangan.")
    cancelled = serializers.IntegerField(help_text="Bekor qilingan.")
