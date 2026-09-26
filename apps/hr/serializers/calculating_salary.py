from django.utils import timezone
from rest_framework import serializers

from apps.base.serializers import BaseModelSerializer
from apps.organization.models import Branch

from ..models import CalculatingSalary
from ..services.salary import ensure_draft


class CalculatingSalarySerializer(BaseModelSerializer):
    """Xodim oylik hisobi (bitta qator) uchun serializer."""

    class Meta:
        model = CalculatingSalary
        fields = [
            "id",
            "branch",
            "employee",
            "for_month",
            "amount",
            "currency",
            "currency_amount",
            "status",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["status"]
        extra_kwargs = {
            "amount": {"min_value": 0},
            "currency_amount": {"min_value": 0},
        }
        related_fields = {
            "branch": {"fields": ["id", "name"]},
            "employee": {"fields": ["id", "full_name"]},
            "currency": {"fields": ["id", "name", "short_name"]},
        }

    def validate(self, attrs):
        """Qoralama holat, xodim filiali va valyuta faolligini tekshiradi."""
        if self.instance is not None:
            ensure_draft(self.instance)
        branch = attrs.get("branch", getattr(self.instance, "branch", None))
        employee = attrs.get("employee", getattr(self.instance, "employee", None))
        currency = attrs.get("currency", getattr(self.instance, "currency", None))
        if employee.branch_id != branch.pk:
            raise serializers.ValidationError(
                {"employee": "Xodim tanlangan filialga tegishli emas."}
            )
        if not currency.is_active:
            raise serializers.ValidationError({"currency": "Valyuta faol emas."})
        return attrs


class CalculatingSalaryCalculateSerializer(serializers.Serializer):
    """Filial va oy bo'yicha oylikni avtomatik hisoblash so'rovi."""

    branch = serializers.PrimaryKeyRelatedField(queryset=Branch.objects.active())
    for_month = serializers.ChoiceField(choices=CalculatingSalary.Month.choices)
    year = serializers.IntegerField(
        required=False,
        min_value=2000,
        max_value=2100,
        help_text="Hisoblanadigan yil (berilmasa — joriy yil).",
    )

    def validate_branch(self, branch):
        """Foydalanuvchining shu filialga ruxsati borligini tekshiradi."""
        user = self.context["request"].user
        if (
            not user.is_system_admin
            and not user.get_accessible_branches().filter(pk=branch.pk).exists()
        ):
            raise serializers.ValidationError(
                "Sizda ushbu filial uchun ma'lumot yaratish huquqi yo'q."
            )
        return branch

    def validate(self, attrs):
        """Yil berilmasa, joriy yilni qo'yadi."""
        attrs.setdefault("year", timezone.localdate().year)
        return attrs
