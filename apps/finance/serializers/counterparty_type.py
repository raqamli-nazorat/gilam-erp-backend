from rest_framework import serializers

from apps.base.serializers import BaseModelSerializer

from ..models import CounterpartyType


class CounterpartyTypeSerializer(BaseModelSerializer):
    """Kontragent turi uchun serializer."""

    status = serializers.BooleanField(source="is_active", read_only=True)

    class Meta:
        model = CounterpartyType
        fields = ["id", "name", "status", "created_at", "updated_at"]
