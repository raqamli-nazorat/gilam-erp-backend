from apps.base.serializers import BaseModelSerializer

from ..models import Payment


class PaymentSerializer(BaseModelSerializer):
    """To'lov uchun serializer — bog'liq obyektlar nested qaytariladi."""

    class Meta:
        model = Payment
        fields = [
            "id",
            "organization",
            "order",
            "installment_agreement",
            "customer",
            "amount",
            "payment_method",
            "payment_type",
            "created_at",
            "updated_at",
        ]
        related_fields = {
            "organization": {"fields": ["id", "name"]},
            "order": {"fields": ["id"]},
            "installment_agreement": {"fields": ["id", "agreement_number"]},
            "customer": {"fields": ["id", "full_name"]},
        }
