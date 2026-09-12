from rest_framework import serializers

from apps.base.serializers import BaseModelSerializer

from ..models import Quality


class QualitySerializer(BaseModelSerializer):
    """Gilam sifati uchun serializer."""

    status = serializers.BooleanField(source="is_active", read_only=True)

    class Meta:
        model = Quality
        fields = ["id", "name", "description", "status", "created_at", "updated_at"]
