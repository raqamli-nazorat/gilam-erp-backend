from rest_framework import serializers

from apps.base.serializers import BaseModelSerializer

from ..models import Branch


class BranchSerializer(BaseModelSerializer):

    warehouses_count = serializers.SerializerMethodField()

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
            "created_at",
            "updated_at",
        ]

        related_fields = {
            "organization": {"fields": ["id", "name"]},
            "region": {"fields": ["id", "name"]},
            "district": {"fields": ["id", "name"]},
        }

    def get_warehouses_count(self, obj):
        annotated = obj.__dict__.get("warehouses_count")
        if annotated is not None:
            return annotated
        return obj.warehouses.filter(is_active=True).count()
