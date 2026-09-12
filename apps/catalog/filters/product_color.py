import django_filters

from ..models import ProductColor


class ProductColorFilter(django_filters.FilterSet):
    name = django_filters.CharFilter(lookup_expr="icontains")
    start_date = django_filters.DateFilter(
        field_name="created_at", lookup_expr="gte", label="Yaratilgan sana (dan)"
    )
    end_date = django_filters.DateFilter(
        field_name="created_at", lookup_expr="lte", label="Yaratilgan sana (gacha)"
    )

    class Meta:
        model = ProductColor
        fields = ["name", "start_date", "end_date"]
