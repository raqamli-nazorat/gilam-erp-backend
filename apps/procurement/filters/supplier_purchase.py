import django_filters

from apps.base.filters import UUIDInFilter

from ..models import SupplierPurchase


class SupplierPurchaseFilter(django_filters.FilterSet):
    organization = UUIDInFilter(field_name="organization_id", lookup_expr="in")
    supplier = UUIDInFilter(field_name="supplier_id", lookup_expr="in")
    warehouse = UUIDInFilter(field_name="warehouse_id", lookup_expr="in")
    start_date = django_filters.DateFilter(
        field_name="created_at", lookup_expr="gte", label="Yaratilgan sana (dan)"
    )
    end_date = django_filters.DateFilter(
        field_name="created_at", lookup_expr="lte", label="Yaratilgan sana (gacha)"
    )

    class Meta:
        model = SupplierPurchase
        fields = ["organization", "supplier", "warehouse", "start_date", "end_date"]
