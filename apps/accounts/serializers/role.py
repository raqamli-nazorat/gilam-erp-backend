from apps.base.serializers import BaseModelSerializer

from ..models import Role


class RoleSerializer(BaseModelSerializer):
    """Foydalanuvchi roli uchun serializer."""

    class Meta:
        model = Role
        fields = ["id", "name", "created_at", "updated_at"]
