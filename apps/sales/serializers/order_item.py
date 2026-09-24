from apps.base.serializers import BaseModelSerializer

from ..models import OrderItem


class OrderItemSerializer(BaseModelSerializer):
    """Chek qatori uchun serializer — bog'liq obyektlar nested qaytariladi."""

    class Meta:
        model = OrderItem
        fields = [
            "id",
            "order",
            "product_party",
            "roll",
            "warehouse",
            "width",
            "length",
            "sqm",
            "price_per_sqm",
            "item_subtotal",
            "overlock_length_meters",
            "overlock_price_per_meter",
            "overlock_cost",
            "quantity",
            "final_item_price",
            "created_at",
            "updated_at",
        ]
        related_fields = {
            "order": {"fields": ["id"]},
            "product_party": {"fields": ["id", "name"]},
            "roll": {"fields": ["id", "roll_number"]},
            "warehouse": {"fields": ["id", "name"]},
        }
