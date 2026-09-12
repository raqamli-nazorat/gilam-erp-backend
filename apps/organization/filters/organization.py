import django_filters

from apps.base.filters import UUIDInFilter

from ..models import Organization


class OrganizationFilter(django_filters.FilterSet):
    name = django_filters.CharFilter(lookup_expr="icontains")
    inn = django_filters.CharFilter(lookup_expr="icontains")
    region = UUIDInFilter(field_name="region_id", lookup_expr="in")
    district = UUIDInFilter(field_name="district_id", lookup_expr="in")
    branches_count_min = django_filters.NumberFilter(
        field_name="branches_count", lookup_expr="gte", label="Filiallar soni (dan)"
    )
    branches_count_max = django_filters.NumberFilter(
        field_name="branches_count", lookup_expr="lte", label="Filiallar soni (gacha)"
    )
    start_date = django_filters.DateFilter(
        field_name="created_at", lookup_expr="gte", label="Yaratilgan sana (dan)"
    )
    end_date = django_filters.DateFilter(
        field_name="created_at", lookup_expr="lte", label="Yaratilgan sana (gacha)"
    )

    class Meta:
        model = Organization
        fields = [
            "name",
            "inn",
            "region",
            "district",
            "branches_count_min",
            "branches_count_max",
            "start_date",
            "end_date",
        ]
