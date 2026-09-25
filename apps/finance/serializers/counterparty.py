from apps.base.serializers import BaseModelSerializer

from ..models import Counterparty


class CounterpartySerializer(BaseModelSerializer):
    """Kontragent uchun serializer — turi nested qaytariladi."""

    class Meta:
        model = Counterparty
        fields = ["id", "name", "phone_number", "type", "created_at", "updated_at"]
        related_fields = {"type": {"fields": ["id", "name"]}}
