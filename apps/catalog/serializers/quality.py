from rest_framework import serializers

from apps.base.serializers import BaseModelSerializer

from ..models import Quality


class QualitySerializer(BaseModelSerializer):

    class Meta:
        model = Quality
        fields = ["id", "name", "description", "created_at", "updated_at"]

