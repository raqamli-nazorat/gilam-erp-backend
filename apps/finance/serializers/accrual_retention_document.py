from django.db import transaction
from drf_spectacular.utils import extend_schema_field
from rest_framework import serializers

from apps.base.serializers import BaseModelSerializer
from apps.hr.models import Employee, RecruitmentDismissal
from apps.hr.services import get_latest_recruitment
from apps.organization.models import Branch
from apps.utils.validators import CANCEL_ATTACHMENT_VALIDATORS

from ..models import AccrualRetention, AccrualRetentionDocument
from ..services.accrual_document import ensure_draft, ensure_employees_employed


def validate_document_context(user, branch, employees, accrual_retention):
    """Hujjat uchun umumiy tekshiruvlar: filial ruxsati, xodim filiali, faolligi va ma'lumotnoma."""
    no_access = (
        not user.is_system_admin
        and not user.get_accessible_branches().filter(pk=branch.pk).exists()
    )
    if no_access:
        raise serializers.ValidationError(
            {"branch": "Sizda ushbu filial uchun ma'lumot yaratish huquqi yo'q."}
        )
    if not accrual_retention.is_active:
        raise serializers.ValidationError(
            {"accrual_retention": "Bu hisoblash / ushlab qolish faol emas."}
        )
    wrong_branch = [e.full_name for e in employees if e.branch_id != branch.pk]
    if wrong_branch:
        raise serializers.ValidationError(
            {
                "employee": "Xodim tanlangan filialga tegishli emas: "
                f"{', '.join(wrong_branch)}."
            }
        )
    ensure_employees_employed(employees)


class IdNameSerializer(serializers.Serializer):
    """`{id, name}` ko'rinishidagi qisqa obyekt (faqat hujjat uchun)."""

    id = serializers.UUIDField()
    name = serializers.CharField()


class SalaryTypeSerializer(serializers.Serializer):
    """Oylik turi: kod va o'zbekcha nomi (faqat hujjat uchun)."""

    value = serializers.CharField()
    label = serializers.CharField()


class DocumentEmployeeDetailsSerializer(serializers.Serializer):
    """Hujjat detailidagi "Xodim ma'lumotlari" bloki (faqat hujjat va format uchun)."""

    organization_info = IdNameSerializer(allow_null=True)
    position_info = IdNameSerializer(allow_null=True)
    card_number = serializers.CharField(allow_blank=True)
    hire_date = serializers.DateField(allow_null=True)
    salary_type = SalaryTypeSerializer(allow_null=True)
    fix_summa = serializers.DecimalField(
        max_digits=15, decimal_places=2, allow_null=True
    )
    fix_percent = serializers.DecimalField(
        max_digits=5, decimal_places=2, allow_null=True
    )
    phone_number = serializers.CharField(allow_blank=True)
    last_login = serializers.DateTimeField(allow_null=True)


class AccrualRetentionDocumentSerializer(BaseModelSerializer):
    """Xodimga hisoblash / ushlab qolish belgilash hujjati uchun serializer."""

    employee_details = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = AccrualRetentionDocument
        fields = [
            "id",
            "branch",
            "employee",
            "accrual_retention",
            "date",
            "status",
            "cancel_reason",
            "cancel_attachment",
            "employee_details",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["status", "cancel_reason", "cancel_attachment"]
        related_fields = {
            "branch": {"fields": ["id", "name"]},
            "employee": {"fields": ["id", "personnel_tab_number", "full_name"]},
            "accrual_retention": {
                "fields": ["id", "name", "type", "is_retention", "value", "currency"]
            },
        }

    def __init__(self, *args, **kwargs):
        """`employee_details` faqat detail (`retrieve`) javobida qoladi."""
        super().__init__(*args, **kwargs)
        view = self.context.get("view")
        if getattr(view, "action", None) != "retrieve":
            self.fields.pop("employee_details", None)

    @extend_schema_field(DocumentEmployeeDetailsSerializer)
    def get_employee_details(self, obj):
        """Xodimning tashkiloti, lavozimi, karta raqami, ish haqi turi, telefoni va oxirgi kirishi."""
        employee = obj.employee
        record = get_latest_recruitment(employee)
        account = getattr(employee, "user_account", None)
        organization = employee.organization
        salary_type = record.salary_type if record else None
        details = {
            "organization_info": organization
            and {"id": organization.pk, "name": organization.name},
            "position_info": record
            and {"id": record.position_id, "name": record.position.name},
            "card_number": record.card_number if record else "",
            "hire_date": record.rec_dism_date if record else None,
            "salary_type": salary_type
            and {
                "value": salary_type,
                "label": RecruitmentDismissal.SalaryType(salary_type).label,
            },
            "fix_summa": record.fix_summa if record else None,
            "fix_percent": record.fix_percent if record else None,
            "phone_number": employee.phone_number,
            "last_login": account.last_login if account else None,
        }
        return DocumentEmployeeDetailsSerializer(details).data

    def validate(self, attrs):
        """Qoralama holat, filial/xodim moslik, ishlayotganlik va ma'lumotnomani tekshiradi."""
        if self.instance is not None:
            ensure_draft(self.instance)
        branch = attrs.get("branch", getattr(self.instance, "branch", None))
        employee = attrs.get("employee", getattr(self.instance, "employee", None))
        accrual = attrs.get(
            "accrual_retention", getattr(self.instance, "accrual_retention", None)
        )
        validate_document_context(
            self.context["request"].user, branch, [employee], accrual
        )
        return attrs


class AccrualRetentionDocumentCancelSerializer(serializers.Serializer):
    """Bekor qilish so'rovi: sabab va asos hujjat (PDF/Excel) ixtiyoriy."""

    reason = serializers.CharField(required=False, allow_blank=True, default="")
    attachment = serializers.FileField(
        required=False, validators=CANCEL_ATTACHMENT_VALIDATORS
    )


class AccrualRetentionDocumentCountSerializer(serializers.Serializer):
    """Hujjatlar sonining status bo'yicha javobi (faqat hujjat uchun)."""

    all = serializers.IntegerField(help_text="Barcha hujjatlar soni.")
    draft = serializers.IntegerField(help_text="Qoralama.")
    approved = serializers.IntegerField(help_text="Tasdiqlangan.")
    cancelled = serializers.IntegerField(help_text="Bekor qilingan.")


class AccrualRetentionDocumentBulkCreateSerializer(serializers.Serializer):
    """Bir hisoblash / ushlab qolish turini bir nechta xodimga bir so'rovda belgilash uchun."""

    branch = serializers.PrimaryKeyRelatedField(queryset=Branch.objects.active())
    accrual_retention = serializers.PrimaryKeyRelatedField(
        queryset=AccrualRetention.objects.active()
    )
    date = serializers.DateTimeField()
    employees = serializers.ListField(
        child=serializers.PrimaryKeyRelatedField(queryset=Employee.objects.active()),
        allow_empty=False,
    )

    def validate_employees(self, value):
        """Bir xodim ro'yxatda ikki marta kelmasligini tekshiradi."""
        if len({employee.pk for employee in value}) != len(value):
            raise serializers.ValidationError(
                "Bir xodim ro'yxatda bir necha marta kiritilgan."
            )
        return value

    def validate(self, attrs):
        """Barcha xodimlar uchun umumiy tekshiruvlarni bajaradi."""
        validate_document_context(
            self.context["request"].user,
            attrs["branch"],
            attrs["employees"],
            attrs["accrual_retention"],
        )
        return attrs

    def create(self, validated_data):
        """Har bir xodimga alohida hujjat yaratadi (hammasi yoki hech narsa)."""
        employees = validated_data.pop("employees")
        with transaction.atomic():
            ids = [
                AccrualRetentionDocument.objects.create(
                    employee=employee, **validated_data
                ).pk
                for employee in employees
            ]
        return AccrualRetentionDocument.objects.filter(pk__in=ids).select_related(
            "branch", "employee", "accrual_retention"
        )
