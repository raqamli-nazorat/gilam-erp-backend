from django.contrib.auth.models import Permission
from django.db.models import Q
from rest_framework import serializers

from apps.base.serializers import BaseModelSerializer

from ..models import Role
from .permission import PermissionSerializer

SYSTEM_APP_LABELS = {
    "admin",
    "auth",
    "sessions",
    "contenttypes",
    "django_celery_beat",
    "authtoken",
    "token_blacklist",
    "rest_framework_simplejwt",
}
SYSTEM_PERMISSIONS = {
    "organization.add_organization",
    "organization.delete_organization",
    "organization.add_country",
    "organization.change_country",
    "organization.delete_country",
    "organization.add_region",
    "organization.change_region",
    "organization.delete_region",
    "organization.add_district",
    "organization.change_district",
    "organization.delete_district",
}


class RoleSerializer(BaseModelSerializer):

    permissions_count = serializers.IntegerField(read_only=True)
    users_count = serializers.IntegerField(read_only=True)
    permissions_info = serializers.SerializerMethodField(read_only=True)
    permissions = serializers.PrimaryKeyRelatedField(
        queryset=Permission.objects.all(),
        many=True,
        write_only=True,
        required=False,
    )

    class Meta:
        model = Role
        fields = [
            "id",
            "name",
            "organization",
            "is_system",
            "permissions",
            "branches",
            "permissions_count",
            "users_count",
            "permissions_info",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["is_system"]
        related_fields = {
            "organization": {"fields": ["id", "name"]},
            "branches": {"fields": ["id", "name"]},
        }

    def get_permissions_info(self, obj):
        request = self.context.get("request")
        is_system_admin = (
            request and request.user and request.user.is_system_admin
        )

        perms = obj.permissions.select_related("content_type").exclude(
            content_type__app_label__in=SYSTEM_APP_LABELS
        )
        if not is_system_admin:
            system_q = Q()
            for sys_perm in SYSTEM_PERMISSIONS:
                app, code = sys_perm.split(".")
                system_q |= Q(content_type__app_label=app, codename=code)
            perms = perms.exclude(system_q)
        return PermissionSerializer(perms, many=True).data


    def validate_permissions(self, permissions):
        request = self.context.get("request")
        is_system_admin = (
            request and request.user and request.user.is_system_admin
        )

        if not is_system_admin:
            for perm in permissions:
                app_label = perm.content_type.app_label
                full_perm = f"{app_label}.{perm.codename}"
                if app_label in SYSTEM_APP_LABELS or full_perm in SYSTEM_PERMISSIONS:
                    raise serializers.ValidationError(
                        f"'{full_perm}' huquqi tizim darajasida bo'lib, tashkilot rollariga berilishi taqiqlangan."
                    )
        return permissions

    def create(self, validated_data):
        request = self.context.get("request")
        if request and request.user and not request.user.is_system_admin:
            validated_data["organization"] = request.user.organization
            validated_data["is_system"] = False
        return super().create(validated_data)
