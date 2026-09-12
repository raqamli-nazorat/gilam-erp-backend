from rest_framework import serializers

from apps.base.serializers import BaseModelSerializer

from ..models import Position


class PositionSerializer(BaseModelSerializer):

    class Meta:
        model = Position
        fields = ["id", "name", "description", "created_at", "updated_at"]

