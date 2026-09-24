from apps.base.serializers import BaseModelSerializer

from ..models import SupplierPurchaseItem


class SupplierPurchaseItemSerializer(BaseModelSerializer):
    """Xarid qatori uchun serializer — bog'liq obyektlar nested qaytariladi."""

    class Meta:
        model = SupplierPurchaseItem
        fields = [
            "id",
            "purchase",
            "product_party",
            "roll_number",
            "width",
            "length",
            "quantity",
            "total_length_meters",
            "price_per_sqm",
            "subtotal",
            "created_at",
            "updated_at",
        ]
        related_fields = {
            "purchase": {"fields": ["id"]},
            "product_party": {"fields": ["id", "name"]},
        }
