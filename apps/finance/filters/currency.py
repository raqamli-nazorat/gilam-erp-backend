import django_filters

from apps.base.filters import UUIDInFilter

from ..models import Currency, CurrencyLedger


class CurrencyFilter(django_filters.FilterSet):
    name = django_filters.CharFilter(lookup_expr="icontains")
    short_name = django_filters.CharFilter(lookup_expr="icontains")
    start_date = django_filters.DateFilter(
        field_name="created_at", lookup_expr="gte", label="Yaratilgan sana (dan)"
    )
    end_date = django_filters.DateFilter(
        field_name="created_at", lookup_expr="lte", label="Yaratilgan sana (gacha)"
    )

    class Meta:
        model = Currency
        fields = ["name", "short_name", "start_date", "end_date"]


class CurrencyLedgerFilter(django_filters.FilterSet):
    currency = UUIDInFilter(field_name="currency_id", lookup_expr="in")
    day_from = django_filters.DateFilter(
        field_name="day", lookup_expr="gte", label="Kurs sanasi (dan)"
    )
    day_to = django_filters.DateFilter(
        field_name="day", lookup_expr="lte", label="Kurs sanasi (gacha)"
    )
    start_date = django_filters.DateFilter(
        field_name="created_at", lookup_expr="gte", label="Yaratilgan sana (dan)"
    )
    end_date = django_filters.DateFilter(
        field_name="created_at", lookup_expr="lte", label="Yaratilgan sana (gacha)"
    )

    class Meta:
        model = CurrencyLedger
        fields = ["currency", "day_from", "day_to", "start_date", "end_date"]
