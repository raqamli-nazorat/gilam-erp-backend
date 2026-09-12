from apps.base.serializers import BaseModelSerializer

from ..models import Region


class RegionSerializer(BaseModelSerializer):

    class Meta:
        model = Region
        fields = ["id", "name", "country", "created_at", "updated_at"]
        related_fields = {"country": {"fields": ["id", "name"]}}
