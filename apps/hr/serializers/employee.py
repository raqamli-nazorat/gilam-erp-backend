from rest_framework import serializers

from apps.base.serializers import BaseModelSerializer

from ..models import Employee


class EmployeeSerializer(BaseModelSerializer):

    class Meta:
        model = Employee
        fields = [
            "id",
            "organization",
            "branch",
            "full_name",
            "region",
            "district",
            "address",
            "passport_seria",
            "passport_number",
            "jsshr",
            "stir",
            "phone_number",
            "description",
            "created_at",
            "updated_at",
        ]
        extra_kwargs = {
            "organization": {"required": False},
        }
        related_fields = {
            "organization": {"fields": ["id", "name"]},
            "branch": {"fields": ["id", "name"]},
            "region": {"fields": ["id", "name"]},
            "district": {"fields": ["id", "name"]},
        }

    def validate(self, attrs):
        request = self.context.get("request")
        user = getattr(request, "user", None) if request else None

        if user and not getattr(user, "is_system_admin", False):
            attrs["organization"] = user.organization
        elif "organization" not in attrs and (
            not self.instance or not self.instance.organization
        ):
            raise serializers.ValidationError(
                {"organization": ["Tashkilot tanlanishi shart."]}
            )

        org = attrs.get("organization") or (
            self.instance.organization if self.instance else None
        )
        branch = attrs.get("branch")
        if branch and org and branch.organization_id != org.id:
            raise serializers.ValidationError(
                {"branch": ["Tanlangan filial ushbu tashkilotga tegishli emas."]}
            )

        region = attrs.get("region")
        district = attrs.get("district")
        if district and region and district.region_id != region.id:
            raise serializers.ValidationError(
                {"district": ["Tanlangan tuman ushbu viloyatga tegishli emas."]}
            )

        return attrs
