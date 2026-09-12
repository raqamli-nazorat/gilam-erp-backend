from apps.base.serializers import BaseModelSerializer

from ..models import Country


class CountrySerializer(BaseModelSerializer):

    class Meta:
        model = Country
        fields = ["id", "name", "created_at", "updated_at"]
