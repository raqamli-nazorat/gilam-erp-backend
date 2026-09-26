import django_filters

from apps.base.filters import UUIDInFilter

from ..models import AccrualRetention


class AccrualRetentionFilter(django_filters.FilterSet):
    name = django_filters.CharFilter(lookup_expr="icontains")
    is_retention = django_filters.BooleanFilter(
        label="Ushlab qolish (true) / hisoblash (false)"
    )
    currency = UUIDInFilter(field_name="currency_id", lookup_expr="in")
    start_date = django_filters.DateFilter(
        field_name="created_at", lookup_expr="gte", label="Yaratilgan sana (dan)"
    )
    end_date = django_filters.DateFilter(
        field_name="created_at", lookup_expr="lte", label="Yaratilgan sana (gacha)"
    )

    class Meta:
        model = AccrualRetention
        fields = ["name", "type", "is_retention", "currency", "start_date", "end_date"]
