from apps.base.serializers import BaseModelSerializer

from ..models import District


class DistrictSerializer(BaseModelSerializer):

    class Meta:
        model = District
        fields = ["id", "name", "region", "created_at", "updated_at"]
        related_fields = {"region": {"fields": ["id", "name"]}}
