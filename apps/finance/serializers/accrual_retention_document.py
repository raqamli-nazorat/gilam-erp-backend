from django.db import transaction
from rest_framework import serializers

from apps.base.serializers import BaseModelSerializer
from apps.hr.models import Employee
from apps.organization.models import Branch

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


class AccrualRetentionDocumentSerializer(BaseModelSerializer):
    """Xodimga hisoblash / ushlab qolish belgilash hujjati uchun serializer."""

    class Meta:
        model = AccrualRetentionDocument
        fields = [
            "id",
            "branch",
            "employee",
            "accrual_retention",
            "date",
            "status",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["status"]
        related_fields = {
            "branch": {"fields": ["id", "name"]},
            "employee": {"fields": ["id", "full_name"]},
            "accrual_retention": {
                "fields": ["id", "name", "type", "is_retention", "value", "currency"]
            },
        }

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
