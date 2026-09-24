from apps.base.serializers import BaseModelSerializer

from ..models import InstallmentAgreement


class InstallmentAgreementSerializer(BaseModelSerializer):
    """Muddatli to'lov shartnomasi uchun serializer — bog'liq obyektlar nested qaytariladi."""

    class Meta:
        model = InstallmentAgreement
        fields = [
            "id",
            "organization",
            "order",
            "customer",
            "agreement_number",
            "total_amount",
            "down_payment",
            "remaining_amount",
            "number_of_months",
            "markup_pct",
            "status",
            "created_at",
            "updated_at",
        ]
        related_fields = {
            "organization": {"fields": ["id", "name"]},
            "order": {"fields": ["id"]},
            "customer": {"fields": ["id", "full_name"]},
        }
