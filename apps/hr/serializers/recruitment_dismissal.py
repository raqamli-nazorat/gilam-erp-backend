from django.db import transaction
from rest_framework import serializers

from apps.base.serializers import BaseModelSerializer

from ..models import RecruitmentDismissal


class RecruitmentDismissalSerializer(BaseModelSerializer):
    class Meta:
        model = RecruitmentDismissal
        fields = [
            "id",
            "type",
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
            "attachment",
            "created_at",
            "updated_at",
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

        return attrs

    def create(self, validated_data):
        """`_actor`ni saqlashdan oldin belgilaydi — signal orqali User blok/unblok uchun."""
        instance = RecruitmentDismissal(**validated_data)
        request = self.context.get("request")
        instance._actor = getattr(request, "user", None) if request else None
        instance.save()
        return instance


class RecruitmentDismissalBulkCreateSerializer(serializers.Serializer):
    """Bir nechta xodimni bitta so'rovda ishga olish/bo'shatish uchun."""

    items = RecruitmentDismissalSerializer(many=True)

    def validate_items(self, value):
        """Ro'yxat bo'sh bo'lmasligini tekshiradi."""
        if not value:
            raise serializers.ValidationError(
                "Kamida bitta xodim ma'lumoti kiritilishi kerak."
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
                instance = RecruitmentDismissal(**item_data)
                instance._actor = actor
                instance.save()
                instances.append(instance)
        return instances
