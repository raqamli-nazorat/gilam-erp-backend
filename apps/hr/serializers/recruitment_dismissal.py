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
            branch
            and employee
            and employee.organization_id
            and branch.organization_id
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
