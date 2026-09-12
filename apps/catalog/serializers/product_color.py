from rest_framework import serializers

from apps.base.serializers import BaseModelSerializer

from ..models import ProductColor


class ProductColorSerializer(BaseModelSerializer):

    class Meta:
        model = ProductColor
        fields = [
            "id",
            "name",
            "description",
            "color_hex",
            "created_at",
            "updated_at",
        ]

