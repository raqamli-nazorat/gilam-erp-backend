from apps.base.serializers import BaseModelSerializer

from ..models import Supplier


class SupplierSerializer(BaseModelSerializer):
    """Yetkazuvchi uchun serializer — tashkilot nested qaytariladi."""

    class Meta:
        model = Supplier
        fields = [
            "id",
            "organization",
            "name",
            "phone",
            "address",
            "balance_debt",
            "created_at",
            "updated_at",
        ]
        related_fields = {
            "organization": {"fields": ["id", "name"]},
        }
