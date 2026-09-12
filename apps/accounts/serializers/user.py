from rest_framework import serializers

from apps.base.serializers import BaseModelSerializer

from ..models import User


class UserSerializer(BaseModelSerializer):

    password = serializers.CharField(
        write_only=True, min_length=8, style={"input_type": "password"}
    )

    class Meta:
        model = User
        fields = [
            "id",
            "full_name",
            "phone_number",
            "password",
            "role",
            "organization",
            "branch",
            "employee",
            "all_branches",
            "is_staff",
            "created_at",
            "updated_at",
        ]
        related_fields = {
            "role": {"fields": ["id", "name"]},
            "organization": {"fields": ["id", "name"]},
            "branch": {"fields": ["id", "name"]},
            "employee": {"fields": ["id", "full_name"]},
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance is not None:
            self.fields["password"].required = False

    def validate_role(self, role):
        request = self.context.get("request")
        if request and request.user and not request.user.is_system_admin:
            if role and role.organization_id != request.user.organization_id:
                raise serializers.ValidationError("Ushbu rolni biriktirish huquqi yo'q.")
        return role

    def validate_branch(self, branch):
        request = self.context.get("request")
        if request and request.user and not request.user.is_system_admin:
            if branch:
                accessible_ids = set(
                    request.user.get_accessible_branches().values_list("id", flat=True)
                )
                if branch.id not in accessible_ids:
                    raise serializers.ValidationError(
                        "Sizda ushbu filialni biriktirish huquqi yo'q."
                    )
        return branch

    def create(self, validated_data):
        request = self.context.get("request")
        if request and request.user and not request.user.is_system_admin:
            validated_data["organization"] = request.user.organization

        password = validated_data.pop("password")
        user = User(**validated_data)
        user.set_password(password)
        user.save()
        return user

    def update(self, instance, validated_data):
        password = validated_data.pop("password", None)
        user = super().update(instance, validated_data)
        if password:
            user.set_password(password)
            user.save(update_fields=["password", "updated_at"])
        return user
