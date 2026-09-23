from rest_framework import serializers

from apps.base.serializers import BaseModelSerializer

from ..models import Organization


class OrganizationBranchSerializer(serializers.Serializer):
    """Tashkilot detali uchun filialning qisqa ma'lumoti."""

    id = serializers.UUIDField()
    name = serializers.CharField()
    phone = serializers.CharField()
    address = serializers.CharField()
    is_closed = serializers.BooleanField()


class OrganizationSerializer(BaseModelSerializer):
    branches_count = serializers.SerializerMethodField()
    branches_active_count = serializers.SerializerMethodField()
    branches_closed_count = serializers.SerializerMethodField()
    branches = serializers.SerializerMethodField()

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
            "is_suspended",
            "suspension_reason",
            "branches_count",
            "branches_active_count",
            "branches_closed_count",
            "branches",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["is_suspended", "suspension_reason"]

        related_fields = {
            "region": {"fields": ["id", "name"]},
            "district": {"fields": ["id", "name"]},
        }

    def get_branches_count(self, obj):
        annotated = obj.__dict__.get("branches_count")
        if annotated is not None:
            return annotated
        return obj.branches.filter(is_active=True).count()

    def get_branches_active_count(self, obj):
        annotated = obj.__dict__.get("branches_active_count")
        if annotated is not None:
            return annotated
        return obj.branches.filter(is_active=True, is_closed=False).count()

    def get_branches_closed_count(self, obj):
        annotated = obj.__dict__.get("branches_closed_count")
        if annotated is not None:
            return annotated
        return obj.branches.filter(is_active=True, is_closed=True).count()

    def get_branches(self, obj):
        """Shu tashkilotga tegishli faol filiallar ro'yxati (view'da prefetch qilingan)."""
        return OrganizationBranchSerializer(obj.branches.all(), many=True).data
