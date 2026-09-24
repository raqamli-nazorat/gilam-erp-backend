from apps.base.serializers import BaseModelSerializer

from ..models import StockTransaction


class StockTransactionSerializer(BaseModelSerializer):
    """Ombor harakati uchun serializer — bog'liq obyektlar nested qaytariladi."""

    class Meta:
        model = StockTransaction
        fields = [
            "id",
            "organization",
            "product_party",
            "roll",
            "from_warehouse",
            "to_warehouse",
            "transaction_type",
            "quantity",
            "length_meters",
            "ref_type",
            "ref_id",
            "created_at",
            "updated_at",
        ]
        related_fields = {
            "organization": {"fields": ["id", "name"]},
            "product_party": {"fields": ["id", "name"]},
            "roll": {"fields": ["id", "roll_number"]},
            "from_warehouse": {"fields": ["id", "name"]},
            "to_warehouse": {"fields": ["id", "name"]},
        }
