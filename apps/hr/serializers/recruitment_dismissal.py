from django.db import transaction
from django.db.models import Max
from django.utils import timezone
from rest_framework import serializers

from apps.base.serializers import BaseModelSerializer

from ..models import Employee, RecruitmentDismissal
from ..services import get_active_recruitment_records

ALREADY_EMPLOYED_MESSAGE = (
    "Xodim allaqachon faol ishlamoqda, qayta ishga olib bo'lmaydi."
)


def ensure_employee_not_employed(employee):
    """Xodim qatorini qulflab, faol ishga olish yozuvi yo'qligini qayta tekshiradi.

    Bir vaqtda kelgan ikki so'rov ham `validate` dan o'tib ketmasligi uchun
    saqlashdan oldin, tranzaksiya ichida chaqiriladi.
    """
    Employee.objects.select_for_update().get(pk=employee.pk)
    if get_active_recruitment_records(employee):
        raise serializers.ValidationError({"employee": [ALREADY_EMPLOYED_MESSAGE]})


def ensure_employee_has_single_active_record(employee):
    """Xodim qatorini qulflab, aynan bitta faol ishga olish yozuvi borligini qayta tekshiradi.

    Bir vaqtda kelgan ikki bo'shatish so'rovi ikkalasi ham o'tib ketmasligi uchun
    saqlashdan oldin, tranzaksiya ichida chaqiriladi. Bo'shatish uchun manba yozuvni qaytaradi.
    """
    Employee.objects.select_for_update().get(pk=employee.pk)
    active_records = get_active_recruitment_records(employee)
    if not active_records:
        raise serializers.ValidationError(
            {"employee": [f"{employee.full_name}: hozir hech qayerda ishlamaydi."]}
        )
    if len(active_records) > 1:
        raise serializers.ValidationError(
            {
                "employee": [
                    f"{employee.full_name}: bir nechta filialda ishlaydi, alohida bo'shatilsin."
                ]
            }
        )
    return active_records[0]


def ensure_recruitment_date_after_dismissal(employee, rec_dism_date):
    """Ishga olish sanasi xodimning oxirgi bo'shatish sanasidan oldin bo'lmasligini tekshiradi.

    Aks holda yozuv yaratiladi, lekin holat hisobida xodim baribir "bo'shatilgan" bo'lib qoladi.
    """
    last_dismissal_date = RecruitmentDismissal.objects.filter(
        employee=employee,
        type=RecruitmentDismissal.Type.DISMISSAL,
        status=RecruitmentDismissal.Status.APPROVED,
        is_active=True,
    ).aggregate(last=Max("rec_dism_date"))["last"]
    if rec_dism_date and last_dismissal_date and rec_dism_date < last_dismissal_date:
        raise serializers.ValidationError(
            {
                "rec_dism_date": [
                    "Ishga olish sanasi xodimning oxirgi bo'shatilgan sanasidan "
                    f"({last_dismissal_date}) oldin bo'lishi mumkin emas."
                ]
            }
        )


class RecruitmentDismissalSerializer(BaseModelSerializer):
    class Meta:
        model = RecruitmentDismissal
        fields = [
            "id",
            "type",
            "status",
            "branch",
            "employee",
            "position",
            "card_number",
            "card_image",
            "salary_type",
            "fix_summa",
            "fix_percent",
            "rec_dism_date",
            "dismissal_reason",
            "extra_summa",
            "extra_percent",
            "created_at",
            "updated_at",
        ]
        related_fields = {
            "branch": {"fields": ["id", "name"]},
            "employee": {"fields": ["id", "full_name", "phone_number"]},
            "position": {"fields": ["id", "name"]},
        }
        read_only_fields = ["status"]

    def validate(self, attrs):
        request = self.context.get("request")
        user = getattr(request, "user", None) if request else None

        if self.instance:
            # Yozuv turi va xodimini o'zgartirib, ikkinchi faol yozuv yaratib bo'lmaydi
            for field in ("type", "employee"):
                if field in attrs and attrs[field] != getattr(self.instance, field):
                    raise serializers.ValidationError(
                        {field: ["Mavjud yozuvda bu maydonni o'zgartirib bo'lmaydi."]}
                    )

        branch = attrs.get("branch") or (
            self.instance.branch if self.instance else None
        )
        employee = attrs.get("employee") or (
            self.instance.employee if self.instance else None
        )

        if user and not getattr(user, "is_system_admin", False):
            if employee and employee.organization_id != user.organization_id:
                raise serializers.ValidationError(
                    {"employee": ["Xodim sizning tashkilotingizga tegishli emas."]}
                )
            if branch and branch.organization_id != user.organization_id:
                raise serializers.ValidationError(
                    {"branch": ["Filial sizning tashkilotingizga tegishli emas."]}
                )
        elif (
            branch and employee and employee.organization_id and branch.organization_id
        ):
            if employee.organization_id != branch.organization_id:
                raise serializers.ValidationError(
                    {
                        "employee": [
                            "Xodim va filial bir xil tashkilotga tegishli bo'lishi kerak."
                        ]
                    }
                )

        return attrs

    def create(self, validated_data):
        """`_actor`ni saqlashdan oldin belgilaydi — signal orqali User blok/unblok uchun."""
        instance = RecruitmentDismissal(**validated_data)
        request = self.context.get("request")
        instance._actor = getattr(request, "user", None) if request else None
        instance.save()
        return instance


class EmployeeRecruitmentSerializer(BaseModelSerializer):
    """Xodimni ishga olish uchun — `type` body'ga kiritilmaydi, avtomatik "recruitment" qo'yiladi."""

    class Meta:
        model = RecruitmentDismissal
        fields = [
            "id",
            "status",
            "employee",
            "branch",
            "position",
            "card_number",
            "salary_type",
            "fix_summa",
            "fix_percent",
            "rec_dism_date",
            "extra_summa",
            "extra_percent",
        ]
        related_fields = {
            "branch": {"fields": ["id", "name"]},
            "employee": {"fields": ["id", "full_name", "phone_number"]},
            "position": {"fields": ["id", "name"]},
        }

    def validate(self, attrs):
        request = self.context.get("request")
        user = getattr(request, "user", None) if request else None

        branch = attrs.get("branch") or (
            self.instance.branch if self.instance else None
        )
        employee = attrs.get("employee") or (
            self.instance.employee if self.instance else None
        )

        if user and not getattr(user, "is_system_admin", False):
            if employee and employee.organization_id != user.organization_id:
                raise serializers.ValidationError(
                    {"employee": ["Xodim sizning tashkilotingizga tegishli emas."]}
                )
            if branch and branch.organization_id != user.organization_id:
                raise serializers.ValidationError(
                    {"branch": ["Filial sizning tashkilotingizga tegishli emas."]}
                )
        elif (
            branch and employee and employee.organization_id and branch.organization_id
        ):
            if employee.organization_id != branch.organization_id:
                raise serializers.ValidationError(
                    {
                        "employee": [
                            "Xodim va filial bir xil tashkilotga tegishli bo'lishi kerak."
                        ]
                    }
                )

        if employee and get_active_recruitment_records(employee):
            raise serializers.ValidationError({"employee": [ALREADY_EMPLOYED_MESSAGE]})
        if employee:
            ensure_recruitment_date_after_dismissal(
                employee, attrs.get("rec_dism_date")
            )

        return attrs

    def create(self, validated_data):
        """`type`ni "recruitment" qilib belgilaydi va `_actor`ni saqlaydi.

        Xodim qatori qulflanib, faol yozuv qayta tekshiriladi (bir vaqtdagi so'rovlardan himoya).
        """
        validated_data["type"] = RecruitmentDismissal.Type.RECRUITMENT
        instance = RecruitmentDismissal(**validated_data)
        request = self.context.get("request")
        instance._actor = getattr(request, "user", None) if request else None
        with transaction.atomic():
            ensure_employee_not_employed(validated_data["employee"])
            instance.save()
        return instance


class EmployeeDismissalSerializer(BaseModelSerializer):
    """Xodimni ishdan bo'shatish uchun — `employee` tanlanadi, faqat sabab kiritiladi.

    `branch`, `position`, `card_number`, `salary_type` kabi maydonlar xodimning
    hozirgi faol ishlash yozuvidan avtomatik ko'chiriladi.
    """

    dismissal_reason = serializers.CharField(required=True, allow_blank=False)

    class Meta:
        model = RecruitmentDismissal
        fields = ["id", "status", "employee", "dismissal_reason"]
        related_fields = {
            "employee": {"fields": ["id", "full_name", "phone_number"]},
        }

    def validate(self, attrs):
        request = self.context.get("request")
        user = getattr(request, "user", None) if request else None
        employee = attrs.get("employee")

        if (
            user
            and not getattr(user, "is_system_admin", False)
            and employee
            and employee.organization_id != user.organization_id
        ):
            raise serializers.ValidationError(
                {"employee": ["Xodim sizning tashkilotingizga tegishli emas."]}
            )

        active_records = get_active_recruitment_records(employee)

        if not active_records:
            raise serializers.ValidationError(
                {"employee": ["Xodim hozir hech qayerda ishlamaydi."]}
            )
        if len(active_records) > 1:
            raise serializers.ValidationError(
                {
                    "employee": [
                        "Xodim bir nechta filialda ishlaydi, ishdan bo'shatish uchun administrator bilan bog'laning."
                    ]
                }
            )

        attrs["_source_record"] = active_records[0]
        return attrs

    def create(self, validated_data):
        """`type`ni "dismissal" qilib, qolgan maydonlarni joriy ishlash yozuvidan ko'chirib saqlaydi."""
        validated_data.pop("_source_record")
        request = self.context.get("request")
        with transaction.atomic():
            source = ensure_employee_has_single_active_record(
                validated_data["employee"]
            )
            validated_data.update(
                {
                    "type": RecruitmentDismissal.Type.DISMISSAL,
                    "branch": source.branch,
                    "position": source.position,
                    "card_number": source.card_number,
                    "salary_type": source.salary_type,
                    "fix_summa": source.fix_summa,
                    "fix_percent": source.fix_percent,
                    "rec_dism_date": timezone.now().date(),
                }
            )
            instance = RecruitmentDismissal(**validated_data)
            instance._actor = getattr(request, "user", None) if request else None
            instance.save()
        return instance


class RecruitmentDismissalListSerializer(BaseModelSerializer):
    """Ishga olish/bo'shatish ro'yxati uchun — faqat kerakli maydonlar, tekis (ID'siz) ko'rinishda."""

    employee_name = serializers.CharField(source="employee.full_name", read_only=True)
    organization_name = serializers.CharField(
        source="employee.organization.name", read_only=True
    )
    branch_name = serializers.CharField(source="branch.name", read_only=True)
    position_name = serializers.CharField(source="position.name", read_only=True)

    class Meta:
        model = RecruitmentDismissal
        fields = [
            "id",
            "rec_dism_date",
            "status",
            "employee_name",
            "organization_name",
            "branch_name",
            "position_name",
            "created_at",
            "updated_at",
        ]


class RecruitmentDismissalBulkCreateSerializer(serializers.Serializer):
    """Bir nechta xodimni bitta so'rovda ishga olish uchun — `type` avtomatik "recruitment"."""

    items = EmployeeRecruitmentSerializer(many=True)

    def validate_items(self, value):
        """Ro'yxat bo'sh bo'lmasligini va bir xodim ikki marta kelmasligini tekshiradi."""
        if not value:
            raise serializers.ValidationError(
                "Kamida bitta xodim ma'lumoti kiritilishi kerak."
            )
        employee_ids = [item["employee"].pk for item in value]
        if len(employee_ids) != len(set(employee_ids)):
            raise serializers.ValidationError(
                "Bir xodim ro'yxatda bir necha marta kiritilgan."
            )
        return value

    def create(self, validated_data):
        """Har bir yozuvni alohida saqlaydi — signal (EmployeeLedger) ishlashi uchun bulk_create ishlatilmaydi."""
        items_data = validated_data["items"]
        request = self.context.get("request")
        actor = getattr(request, "user", None) if request else None
        instances = []
        with transaction.atomic():
            for item_data in items_data:
                ensure_employee_not_employed(item_data["employee"])
                item_data["type"] = RecruitmentDismissal.Type.RECRUITMENT
                instance = RecruitmentDismissal(**item_data)
                instance._actor = actor
                instance.save()
                instances.append(instance)
        return instances


class RecruitmentDismissalBulkDismissSerializer(serializers.Serializer):
    """Bir nechta xodimni bitta so'rovda, umumiy sabab bilan ishdan bo'shatish uchun."""

    employees = serializers.PrimaryKeyRelatedField(
        queryset=Employee.objects.active(), many=True
    )
    dismissal_reason = serializers.CharField(
        required=False, allow_blank=True, default=""
    )
    status = serializers.ChoiceField(
        choices=RecruitmentDismissal.Status.choices,
        required=False,
        default=RecruitmentDismissal.Status.APPROVED,
    )

    def validate_employees(self, value):
        """Ro'yxat bo'sh bo'lmasligini va bir xodim ikki marta kelmasligini tekshiradi."""
        if not value:
            raise serializers.ValidationError("Kamida bitta xodim tanlanishi kerak.")
        employee_ids = [employee.pk for employee in value]
        if len(employee_ids) != len(set(employee_ids)):
            raise serializers.ValidationError(
                "Bir xodim ro'yxatda bir necha marta kiritilgan."
            )
        return value

    def validate(self, attrs):
        request = self.context.get("request")
        user = getattr(request, "user", None) if request else None
        errors = []

        for employee in attrs["employees"]:
            if (
                user
                and not getattr(user, "is_system_admin", False)
                and employee.organization_id != user.organization_id
            ):
                errors.append(
                    f"{employee.full_name}: sizning tashkilotingizga tegishli emas."
                )
                continue

            active_records = get_active_recruitment_records(employee)
            if not active_records:
                errors.append(f"{employee.full_name}: hozir hech qayerda ishlamaydi.")
                continue
            if len(active_records) > 1:
                errors.append(
                    f"{employee.full_name}: bir nechta filialda ishlaydi, alohida bo'shatilsin."
                )
                continue

        if errors:
            raise serializers.ValidationError({"employees": errors})

        return attrs

    def create(self, validated_data):
        """Har bir xodim uchun umumiy sabab bilan alohida yozuv yaratadi.

        Xodim qatori qulflanib, faol yozuv qayta tekshiriladi (bir vaqtdagi so'rovlardan himoya).
        """
        employees = validated_data["employees"]
        dismissal_reason = validated_data.get("dismissal_reason", "")
        record_status = validated_data.get(
            "status", RecruitmentDismissal.Status.APPROVED
        )
        request = self.context.get("request")
        actor = getattr(request, "user", None) if request else None
        today = timezone.now().date()

        instances = []
        with transaction.atomic():
            for employee in employees:
                source = ensure_employee_has_single_active_record(employee)
                instance = RecruitmentDismissal(
                    type=RecruitmentDismissal.Type.DISMISSAL,
                    status=record_status,
                    employee=employee,
                    branch=source.branch,
                    position=source.position,
                    card_number=source.card_number,
                    salary_type=source.salary_type,
                    fix_summa=source.fix_summa,
                    fix_percent=source.fix_percent,
                    rec_dism_date=today,
                    dismissal_reason=dismissal_reason,
                )
                instance._actor = actor
                instance.save()
                instances.append(instance)
        return instances
