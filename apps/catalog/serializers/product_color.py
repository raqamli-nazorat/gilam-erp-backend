from rest_framework import serializers

from apps.base.serializers import BaseModelSerializer

from ..models import ProductColor


class ProductColorSerializer(BaseModelSerializer):

    status = serializers.BooleanField(source="is_active", read_only=True)

    class Meta:
        model = ProductColor
        fields = [
            "id",
            "name",
            "description",
            "color_hex",
            "status",
            "created_at",
            "updated_at",
        ]
