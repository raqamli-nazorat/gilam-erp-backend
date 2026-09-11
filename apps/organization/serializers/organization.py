from rest_framework import serializers

from apps.base.serializers import BaseModelSerializer

from ..models import Organization


class OrganizationSerializer(BaseModelSerializer):
    """Tashkilot uchun serializer — viloyat va tuman nested qaytariladi."""

    branches_count = serializers.SerializerMethodField()
    status = serializers.BooleanField(source="is_active", read_only=True)

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
            "branches_count",
            "status",
            "created_at",
            "updated_at",
        ]
        related_fields = {
            "region": {"fields": ["id", "name"]},
            "district": {"fields": ["id", "name"]},
        }

    def get_branches_count(self, obj):
        """Tashkilotga tegishli faol filiallar sonini qaytaradi."""
        annotated = obj.__dict__.get("branches_count")
        if annotated is not None:
            return annotated
        return obj.branches.filter(is_active=True).count()
