from apps.base.serializers import BaseModelSerializer

from ..models import Organization


class OrganizationSerializer(BaseModelSerializer):
    """Tashkilot uchun serializer — viloyat va tuman nested qaytariladi."""

    class Meta:
        model = Organization
        fields = [
            "id",
            "name",
            "inn",
            "phone",
            "director",
            "region",
            "district",
            "address",
            "prefix",
            "created_at",
            "updated_at",
        ]
        related_fields = {
            "region": {"fields": ["id", "name"]},
            "district": {"fields": ["id", "name"]},
        }
