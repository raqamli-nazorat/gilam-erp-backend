from apps.base.serializers import BaseModelSerializer

from ..models import Region


class RegionSerializer(BaseModelSerializer):
    """Viloyat uchun serializer — `country` yoziladi, `country_info` qaytadi."""

    class Meta:
        model = Region
        fields = ["id", "name", "country", "created_at", "updated_at"]
        related_fields = {"country": {"fields": ["id", "name"]}}
