from rest_framework import serializers

from apps.base.serializers import BaseModelSerializer

from ..models import Unit


class UnitSerializer(BaseModelSerializer):

    class Meta:
        model = Unit
        fields = ["id", "name", "description", "created_at", "updated_at"]

