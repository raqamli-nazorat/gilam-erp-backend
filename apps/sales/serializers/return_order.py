from apps.base.serializers import BaseModelSerializer

from ..models import ReturnOrder


class ReturnOrderSerializer(BaseModelSerializer):
    """Qaytarish hujjati uchun serializer — bog'liq obyektlar nested qaytariladi."""

    class Meta:
        model = ReturnOrder
        fields = [
            "id",
            "organization",
            "branch",
            "order",
            "customer",
            "refund_amount",
            "reason",
            "created_at",
            "updated_at",
        ]
        related_fields = {
            "organization": {"fields": ["id", "name"]},
            "branch": {"fields": ["id", "name"]},
            "order": {"fields": ["id"]},
            "customer": {"fields": ["id", "full_name"]},
        }
