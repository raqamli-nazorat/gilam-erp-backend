from apps.base.serializers import BaseModelSerializer

from ..models import Customer


class CustomerSerializer(BaseModelSerializer):
    """Mijoz uchun serializer — tashkilot nested qaytariladi."""

    class Meta:
        model = Customer
        fields = [
            "id",
            "organization",
            "full_name",
            "phone",
            "address",
            "balance_debt",
            "loyalty_discount_pct",
            "created_at",
            "updated_at",
        ]
        related_fields = {
            "organization": {"fields": ["id", "name"]},
        }
