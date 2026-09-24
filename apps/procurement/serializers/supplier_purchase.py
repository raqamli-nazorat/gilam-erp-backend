from apps.base.serializers import BaseModelSerializer

from ..models import SupplierPurchase


class SupplierPurchaseSerializer(BaseModelSerializer):
    """Xarid hujjati uchun serializer — bog'liq obyektlar nested qaytariladi."""

    class Meta:
        model = SupplierPurchase
        fields = [
            "id",
            "organization",
            "supplier",
            "warehouse",
            "total_amount",
            "paid_amount",
            "debt_amount",
            "created_at",
            "updated_at",
        ]
        related_fields = {
            "organization": {"fields": ["id", "name"]},
            "supplier": {"fields": ["id", "name"]},
            "warehouse": {"fields": ["id", "name"]},
        }
