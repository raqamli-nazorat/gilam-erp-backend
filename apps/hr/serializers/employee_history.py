from rest_framework import serializers


class EmployeeEmploymentHistorySerializer(serializers.Serializer):
    """Xodimning filiallar bo'yicha ish tarixi qatori (hisoblanadigan ma'lumot, model emas)."""

    organization = serializers.SerializerMethodField()
    branch = serializers.SerializerMethodField()
    position = serializers.SerializerMethodField()
    hired_at = serializers.DateField()
    is_employed = serializers.BooleanField()

    def get_organization(self, obj):
        organization = obj.get("organization")
        return (
            {"id": str(organization.id), "name": organization.name}
            if organization
            else None
        )

    def get_branch(self, obj):
        branch = obj.get("branch")
        return {"id": str(branch.id), "name": branch.name} if branch else None

    def get_position(self, obj):
        position = obj.get("position")
        return {"id": str(position.id), "name": position.name} if position else None
