from rest_framework import serializers

from apps.base.serializers import BaseModelSerializer

from ..models import CounterpartyType


class CounterpartyTypeSerializer(BaseModelSerializer):

    class Meta:
        model = CounterpartyType
        fields = ["id", "name", "created_at", "updated_at"]

