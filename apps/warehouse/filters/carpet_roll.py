import django_filters

from apps.base.filters import UUIDInFilter

from ..models import CarpetRoll


class CarpetRollFilter(django_filters.FilterSet):
    roll_number = django_filters.CharFilter(lookup_expr="icontains")
    product_party = UUIDInFilter(field_name="product_party_id", lookup_expr="in")
    warehouse = UUIDInFilter(field_name="warehouse_id", lookup_expr="in")
    status = django_filters.ChoiceFilter(choices=CarpetRoll.Status.choices)
    is_offcut = django_filters.BooleanFilter()
    start_date = django_filters.DateFilter(
        field_name="created_at", lookup_expr="gte", label="Yaratilgan sana (dan)"
    )
    end_date = django_filters.DateFilter(
        field_name="created_at", lookup_expr="lte", label="Yaratilgan sana (gacha)"
    )

    class Meta:
        model = CarpetRoll
        fields = [
            "roll_number",
            "product_party",
            "warehouse",
            "status",
            "is_offcut",
            "start_date",
            "end_date",
        ]
