from apps.base.serializers import BaseModelSerializer

from ..models import Design


class DesignSerializer(BaseModelSerializer):
    """Gilam dizayni uchun serializer — sifat nested qaytariladi."""

    class Meta:
        model = Design
        fields = [
            "id",
            "quality",
            "name",
            "description",
            "created_at",
            "updated_at",
        ]
        related_fields = {"quality": {"fields": ["id", "name"]}}
