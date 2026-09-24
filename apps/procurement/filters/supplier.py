import django_filters

from apps.base.filters import UUIDInFilter

from ..models import Supplier


class SupplierFilter(django_filters.FilterSet):
    name = django_filters.CharFilter(lookup_expr="icontains")
    organization = UUIDInFilter(field_name="organization_id", lookup_expr="in")
    start_date = django_filters.DateFilter(
        field_name="created_at", lookup_expr="gte", label="Yaratilgan sana (dan)"
    )
    end_date = django_filters.DateFilter(
        field_name="created_at", lookup_expr="lte", label="Yaratilgan sana (gacha)"
    )

    class Meta:
        model = Supplier
        fields = ["name", "organization", "start_date", "end_date"]
