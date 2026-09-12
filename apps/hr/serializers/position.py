from rest_framework import serializers

from apps.base.serializers import BaseModelSerializer

from ..models import Position


class PositionSerializer(BaseModelSerializer):
    """Xodim lavozimi uchun serializer."""

    status = serializers.BooleanField(source="is_active", read_only=True)

    class Meta:
        model = Position
        fields = ["id", "name", "description", "status", "created_at", "updated_at"]
