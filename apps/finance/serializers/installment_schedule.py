from apps.base.serializers import BaseModelSerializer

from ..models import InstallmentSchedule


class InstallmentScheduleSerializer(BaseModelSerializer):
    """Oylik to'lov grafigi uchun serializer — shartnoma nested qaytariladi."""

    class Meta:
        model = InstallmentSchedule
        fields = [
            "id",
            "agreement",
            "payment_number",
            "due_date",
            "amount_to_pay",
            "paid_amount",
            "status",
            "created_at",
            "updated_at",
        ]
        related_fields = {
            "agreement": {"fields": ["id", "agreement_number"]},
        }
