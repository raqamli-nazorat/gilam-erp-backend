from rest_framework import serializers

from apps.base.serializers import BaseModelSerializer

from ..models import Branch


class BranchSerializer(BaseModelSerializer):

    warehouses_count = serializers.SerializerMethodField()
    employees_count = serializers.SerializerMethodField()

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
            "is_closed",
            "closing_reason",
            "warehouses_count",
            "employees_count",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["is_closed", "closing_reason"]

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

    def get_employees_count(self, obj):
        annotated = obj.__dict__.get("employees_count")
        if annotated is not None:
            return annotated
        return obj.employees.filter(is_active=True).count()
