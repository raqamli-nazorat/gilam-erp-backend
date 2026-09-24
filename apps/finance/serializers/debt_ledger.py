from apps.base.serializers import BaseModelSerializer

from ..models import DebtLedger


class DebtLedgerSerializer(BaseModelSerializer):
    """Nasiya daftari uchun serializer — bog'liq obyektlar nested qaytariladi."""

    class Meta:
        model = DebtLedger
        fields = [
            "id",
            "organization",
            "customer",
            "order",
            "total_debt",
            "remaining_debt",
            "due_date",
            "status",
            "created_at",
            "updated_at",
        ]
        related_fields = {
            "organization": {"fields": ["id", "name"]},
            "customer": {"fields": ["id", "full_name"]},
            "order": {"fields": ["id"]},
        }
