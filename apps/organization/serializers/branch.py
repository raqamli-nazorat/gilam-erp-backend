from apps.base.serializers import BaseModelSerializer

from ..models import Branch


class BranchSerializer(BaseModelSerializer):
    """Filial uchun serializer — tashkilot, viloyat va tuman nested qaytariladi."""

    class Meta:
        model = Branch
        fields = [
            "id",
            "organization",
            "name",
            "phone",
            "region",
            "district",
            "address",
            "created_at",
            "updated_at",
        ]
        related_fields = {
            "organization": {"fields": ["id", "name"]},
            "region": {"fields": ["id", "name"]},
            "district": {"fields": ["id", "name"]},
        }
