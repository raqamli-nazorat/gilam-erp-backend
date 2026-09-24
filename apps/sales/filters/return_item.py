import django_filters

from apps.base.filters import UUIDInFilter

from ..models import ReturnItem


class ReturnItemFilter(django_filters.FilterSet):
    return_order = UUIDInFilter(field_name="return_order_id", lookup_expr="in")
    order_item = UUIDInFilter(field_name="order_item_id", lookup_expr="in")
    restock_status = django_filters.ChoiceFilter(
        choices=ReturnItem.RestockStatus.choices
    )
    start_date = django_filters.DateFilter(
        field_name="created_at", lookup_expr="gte", label="Yaratilgan sana (dan)"
    )
    end_date = django_filters.DateFilter(
        field_name="created_at", lookup_expr="lte", label="Yaratilgan sana (gacha)"
    )

    class Meta:
        model = ReturnItem
        fields = [
            "return_order",
            "order_item",
            "restock_status",
            "start_date",
            "end_date",
        ]
