from rest_framework import serializers

from apps.base.serializers import BaseModelSerializer

from ..models import Organization


class OrganizationSerializer(BaseModelSerializer):

    branches_count = serializers.SerializerMethodField()

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
