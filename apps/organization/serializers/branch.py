from rest_framework import serializers

from apps.base.serializers import BaseModelSerializer

from ..models import Branch


class BranchEmployeeSerializer(serializers.Serializer):
    """Filial detali uchun xodimning qisqa ma'lumoti (lavozim oxirgi faol ishga olish yozuvidan)."""

    id = serializers.UUIDField()
    full_name = serializers.CharField()
    position = serializers.SerializerMethodField()
    phone_number = serializers.CharField()

    def get_position(self, obj):
        """Xodimning oxirgi faol ishga olish yozuvidagi lavozim nomini qaytaradi."""
        return getattr(obj, "latest_position_name", None) or ""


class BranchWarehouseSerializer(serializers.Serializer):
    """Filial detali uchun omborning qisqa ma'lumoti."""

    id = serializers.UUIDField()
    name = serializers.CharField()
    address = serializers.CharField()


class BranchSerializer(BaseModelSerializer):
    warehouses_count = serializers.SerializerMethodField()
    employees_count = serializers.SerializerMethodField()
    employees = serializers.SerializerMethodField()
    warehouses = serializers.SerializerMethodField()

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
            "employees",
            "warehouses",
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

    def get_employees(self, obj):
        """Filialga tegishli faol xodimlar ro'yxati (view'da prefetch qilingan)."""
        return BranchEmployeeSerializer(obj.employees.all(), many=True).data

    def get_warehouses(self, obj):
        """Filialga tegishli faol omborlar ro'yxati (view'da prefetch qilingan)."""
        return BranchWarehouseSerializer(obj.warehouses.all(), many=True).data
