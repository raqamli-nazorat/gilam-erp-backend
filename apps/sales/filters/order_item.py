import django_filters

from apps.base.filters import UUIDInFilter

from ..models import OrderItem


class OrderItemFilter(django_filters.FilterSet):
    order = UUIDInFilter(field_name="order_id", lookup_expr="in")
    product_party = UUIDInFilter(field_name="product_party_id", lookup_expr="in")
    warehouse = UUIDInFilter(field_name="warehouse_id", lookup_expr="in")
    roll = UUIDInFilter(field_name="roll_id", lookup_expr="in")
    start_date = django_filters.DateFilter(
        field_name="created_at", lookup_expr="gte", label="Yaratilgan sana (dan)"
    )
    end_date = django_filters.DateFilter(
        field_name="created_at", lookup_expr="lte", label="Yaratilgan sana (gacha)"
    )

    class Meta:
        model = OrderItem
        fields = [
            "order",
            "product_party",
            "warehouse",
            "roll",
            "start_date",
            "end_date",
        ]
