from rest_framework import serializers

from apps.base.serializers import BaseModelSerializer

from ..models import Branch


class BranchSerializer(BaseModelSerializer):
    """Filial uchun serializer — tashkilot, viloyat va tuman nested qaytariladi."""

    warehouses_count = serializers.SerializerMethodField()
    status = serializers.BooleanField(source="is_active", read_only=True)

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
            "warehouses_count",
            "status",
            "created_at",
            "updated_at",
        ]
        related_fields = {
            "organization": {"fields": ["id", "name"]},
            "region": {"fields": ["id", "name"]},
            "district": {"fields": ["id", "name"]},
        }

    def get_warehouses_count(self, obj):
        """Filialga tegishli faol omborlar sonini qaytaradi."""
        annotated = obj.__dict__.get("warehouses_count")
        if annotated is not None:
            return annotated
        return obj.warehouses.filter(is_active=True).count()
