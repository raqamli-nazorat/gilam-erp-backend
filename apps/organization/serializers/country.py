from apps.base.serializers import BaseModelSerializer

from ..models import Country


class CountrySerializer(BaseModelSerializer):
    """Davlat ma'lumotnomasi uchun serializer."""

    class Meta:
        model = Country
        fields = ["id", "name", "created_at", "updated_at"]
