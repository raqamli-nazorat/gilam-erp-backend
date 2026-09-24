from apps.base.serializers import BaseModelSerializer

from ..models import Order


class OrderSerializer(BaseModelSerializer):
    """Sotuv cheki uchun serializer — bog'liq obyektlar nested qaytariladi."""

    class Meta:
        model = Order
        fields = [
            "id",
            "organization",
            "branch",
            "customer",
            "seller",
            "cashier",
            "total_amount",
            "discount_amount",
            "final_amount",
            "paid_amount",
            "debt_amount",
            "payment_status",
            "order_status",
            "overlock_included",
            "delivery_required",
            "delivery_address",
            "delivery_date",
            "created_at",
            "updated_at",
        ]
        related_fields = {
            "organization": {"fields": ["id", "name"]},
            "branch": {"fields": ["id", "name"]},
            "customer": {"fields": ["id", "full_name"]},
            "seller": {"fields": ["id", "full_name"]},
            "cashier": {"fields": ["id", "full_name"]},
        }
