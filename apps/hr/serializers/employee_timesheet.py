from decimal import ROUND_HALF_UP, Decimal

from django.utils import timezone
from rest_framework import serializers

from apps.base.serializers import BaseModelSerializer

from ..models import EmployeeTimesheet, EmployeeTimesheetItem
from ..services.timesheet import ensure_draft

TIME_FIELDS = ["input_date", "output_lunch_date", "input_lunch_date", "output_date"]


class EmployeeTimesheetSerializer(BaseModelSerializer):
    items_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = EmployeeTimesheet
        fields = [
            "id",
            "branch",
            "for_month",
            "status",
            "items_count",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["status"]
        related_fields = {
            "branch": {"fields": ["id", "name"]},
        }

    def validate(self, attrs):
        """Qoralama bo'lmagan tabelni o'zgartirishni taqiqlaydi."""
        if self.instance is not None:
            ensure_draft(self.instance)
        return attrs


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
        related_fields = {
            "employee_timesheet": {"fields": ["id", "branch", "for_month", "status"]},
            "employee": {"fields": ["id", "full_name"]},
        }

    def _value(self, attrs, name):
        """Yangi qiymatni, bo'lmasa mavjud obyektdagi qiymatni qaytaradi."""
        return attrs.get(name, getattr(self.instance, name, None))

    def validate(self, attrs):
        """Tabel holati, oy, filial, kun takrori va vaqt tartibini tekshiradi."""
        timesheet = self._value(attrs, "employee_timesheet")
        employee = self._value(attrs, "employee")
        date = self._value(attrs, "date")

        self._validate_timesheet(attrs, timesheet)
        self._validate_scope(timesheet)
        self._validate_employee_and_date(timesheet, employee, date)
        self._validate_time_order(attrs)
        self._fill_fact_hours(attrs)
        return attrs

    def _validate_timesheet(self, attrs, timesheet):
        """Tabel(lar) qoralama holatda ekanini tekshiradi."""
        ensure_draft(timesheet)
        if self.instance is not None:
            ensure_draft(self.instance.employee_timesheet)

    def _validate_scope(self, timesheet):
        """Foydalanuvchi shu tabel filialiga ruxsati borligini tekshiradi."""
        user = self.context["request"].user
        if user.is_system_admin:
            return
        if not user.get_accessible_branches().filter(pk=timesheet.branch_id).exists():
            raise serializers.ValidationError(
                {
                    "employee_timesheet": "Sizda ushbu filial uchun ma'lumot yaratish huquqi yo'q."
                }
            )

    def _validate_employee_and_date(self, timesheet, employee, date):
        """Xodim filiali, sana oyi va kun takrorini tekshiradi."""
        if employee.branch_id != timesheet.branch_id:
            raise serializers.ValidationError(
                {"employee": "Xodim tabel filialiga tegishli emas."}
            )
        local_date = timezone.localtime(date).date()
        if local_date.month != timesheet.for_month:
            raise serializers.ValidationError(
                {"date": "Sana tabel oyiga mos kelishi kerak."}
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
        if bool(values["output_lunch_date"]) != bool(values["input_lunch_date"]):
            raise serializers.ValidationError(
                {"input_lunch_date": "Tushlik vaqti ikkalasi ham kiritilishi kerak."}
            )
        given = [values[name] for name in TIME_FIELDS if values[name]]
        if given != sorted(given):
            raise serializers.ValidationError(
                "Vaqtlar tartibi noto'g'ri: kelish ≤ tushlikka chiqish ≤ "
                "tushlikdan kelish ≤ ketish bo'lishi kerak."
            )

    def _fill_fact_hours(self, attrs):
        """`work_hour_in_fact` berilmasa, vaqtlardan avtomatik hisoblaydi."""
        times_sent = any(name in attrs for name in TIME_FIELDS)
        if "work_hour_in_fact" in attrs or not (self.instance is None or times_sent):
            return
        values = {name: self._value(attrs, name) for name in TIME_FIELDS}
        if not (values["input_date"] and values["output_date"]):
            return
        worked = values["output_date"] - values["input_date"]
        if values["output_lunch_date"] and values["input_lunch_date"]:
            worked -= values["input_lunch_date"] - values["output_lunch_date"]
        hours = Decimal(worked.total_seconds()) / Decimal(3600)
        attrs["work_hour_in_fact"] = hours.quantize(
            Decimal("0.01"), rounding=ROUND_HALF_UP
        )
