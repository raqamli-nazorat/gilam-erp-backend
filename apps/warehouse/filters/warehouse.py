import django_filters

from apps.base.filters import UUIDInFilter

from ..models import Warehouse


class WarehouseFilter(django_filters.FilterSet):
    name = django_filters.CharFilter(lookup_expr="icontains")
    branch = UUIDInFilter(field_name="branch_id", lookup_expr="in")
    start_date = django_filters.DateFilter(
        field_name="created_at", lookup_expr="gte", label="Yaratilgan sana (dan)"
    )
    end_date = django_filters.DateFilter(
        field_name="created_at", lookup_expr="lte", label="Yaratilgan sana (gacha)"
    )

    class Meta:
        model = Warehouse
        fields = ["name", "branch", "start_date", "end_date"]
