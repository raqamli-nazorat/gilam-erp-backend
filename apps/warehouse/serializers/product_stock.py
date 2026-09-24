from apps.base.serializers import BaseModelSerializer

from ..models import ProductStock


class ProductStockSerializer(BaseModelSerializer):
    """Ombor qoldig'i uchun serializer — ombor va mahsulot partiyasi nested qaytariladi."""

    class Meta:
        model = ProductStock
        fields = [
            "id",
            "warehouse",
            "product_party",
            "quantity",
            "total_length_meters",
            "created_at",
            "updated_at",
        ]
        related_fields = {
            "warehouse": {"fields": ["id", "name"]},
            "product_party": {"fields": ["id", "name"]},
        }
