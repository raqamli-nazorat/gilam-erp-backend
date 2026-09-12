from rest_framework import serializers

from apps.base.serializers import BaseModelSerializer

from ..models import User


class UserSerializer(BaseModelSerializer):

    password = serializers.CharField(
        write_only=True, min_length=8, style={"input_type": "password"}
    )
    organization = serializers.SerializerMethodField(read_only=True)
    branch = serializers.SerializerMethodField(read_only=True)

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
            "is_staff",
            "created_at",
            "updated_at",
        ]
        related_fields = {
            "role": {"fields": ["id", "name"]},
            "employee": {"fields": ["id", "full_name"]},
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance is not None:
            self.fields["password"].required = False

    def get_organization(self, obj):
        org = obj.organization
        if org:
            return {"id": str(org.id), "name": org.name}
        return None

    def get_branch(self, obj):
        br = obj.branch
        if br:
            return {"id": str(br.id), "name": br.name}
        return None

    def validate_role(self, role):
        request = self.context.get("request")
        if request and request.user and not request.user.is_system_admin:
            if role and role.organization_id != request.user.organization_id:
                raise serializers.ValidationError("Ushbu rolni biriktirish huquqi yo'q.")
        return role

    def validate_employee(self, employee):
        if employee:
            existing_user = User.objects.filter(employee=employee)
            if self.instance:
                existing_user = existing_user.exclude(id=self.instance.id)
            if existing_user.exists():
                raise serializers.ValidationError(
                    "Ushbu xodimga allaqachon akkaunt ochilgan."
                )

            request = self.context.get("request")
            if request and request.user and not request.user.is_system_admin:
                if employee.organization_id != request.user.organization_id:
                    raise serializers.ValidationError(
                        "Ushbu xodim sizning tashkilotingizga tegishli emas."
                    )
        return employee

    def create(self, validated_data):
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
