from apps.base.serializers import BaseModelSerializer

from ..models import ReturnItem


class ReturnItemSerializer(BaseModelSerializer):
    """Qaytarish qatori uchun serializer — bog'liq obyektlar nested qaytariladi."""

    class Meta:
        model = ReturnItem
        fields = [
            "id",
            "return_order",
            "order_item",
            "quantity",
            "length_meters",
            "restock_status",
            "created_at",
            "updated_at",
        ]
        related_fields = {
            "return_order": {"fields": ["id"]},
            "order_item": {"fields": ["id"]},
        }
