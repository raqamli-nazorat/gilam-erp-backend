from apps.base.serializers import BaseModelSerializer

from ..models import Warehouse


class WarehouseSerializer(BaseModelSerializer):
    """Ombor uchun serializer — filial nested qaytariladi."""

    class Meta:
        model = Warehouse
        fields = [
            "id",
            "branch",
            "name",
            "address",
            "created_at",
            "updated_at",
        ]
        related_fields = {
            "branch": {"fields": ["id", "name"]},
        }
