import django_filters

from apps.base.filters import UUIDInFilter

from ..models import Branch


class BranchFilter(django_filters.FilterSet):
    name = django_filters.CharFilter(lookup_expr="icontains")
    organization = UUIDInFilter(field_name="organization_id", lookup_expr="in")
    region = UUIDInFilter(field_name="region_id", lookup_expr="in")
    district = UUIDInFilter(field_name="district_id", lookup_expr="in")
    start_date = django_filters.DateFilter(
        field_name="created_at", lookup_expr="gte", label="Yaratilgan sana (dan)"
    )
    end_date = django_filters.DateFilter(
        field_name="created_at", lookup_expr="lte", label="Yaratilgan sana (gacha)"
    )

    class Meta:
        model = Branch
        fields = [
            "name",
            "organization",
            "region",
            "district",
            "start_date",
            "end_date",
        ]
