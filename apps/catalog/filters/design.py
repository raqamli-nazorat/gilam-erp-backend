import django_filters

from apps.base.filters import UUIDInFilter

from ..models import Design


class DesignFilter(django_filters.FilterSet):
    name = django_filters.CharFilter(lookup_expr="icontains")
    quality = UUIDInFilter(field_name="quality_id", lookup_expr="in")
    start_date = django_filters.DateFilter(
        field_name="created_at", lookup_expr="gte", label="Yaratilgan sana (dan)"
    )
    end_date = django_filters.DateFilter(
        field_name="created_at", lookup_expr="lte", label="Yaratilgan sana (gacha)"
    )

    class Meta:
        model = Design
        fields = ["name", "quality", "start_date", "end_date"]
