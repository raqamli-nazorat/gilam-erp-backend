import django_filters

from apps.base.filters import UUIDInFilter

from ..models import Counterparty


class CounterpartyFilter(django_filters.FilterSet):
    name = django_filters.CharFilter(lookup_expr="icontains")
    phone_number = django_filters.CharFilter(lookup_expr="icontains")
    type = UUIDInFilter(field_name="type_id", lookup_expr="in")
    start_date = django_filters.DateFilter(
        field_name="created_at", lookup_expr="gte", label="Yaratilgan sana (dan)"
    )
    end_date = django_filters.DateFilter(
        field_name="created_at", lookup_expr="lte", label="Yaratilgan sana (gacha)"
    )

    class Meta:
        model = Counterparty
        fields = ["name", "phone_number", "type", "start_date", "end_date"]
