import django_filters

from apps.base.filters import UUIDInFilter

from ..models import Order


class OrderFilter(django_filters.FilterSet):
    organization = UUIDInFilter(field_name="organization_id", lookup_expr="in")
    branch = UUIDInFilter(field_name="branch_id", lookup_expr="in")
    customer = UUIDInFilter(field_name="customer_id", lookup_expr="in")
    seller = UUIDInFilter(field_name="seller_id", lookup_expr="in")
    payment_status = django_filters.ChoiceFilter(choices=Order.PaymentStatus.choices)
    order_status = django_filters.ChoiceFilter(choices=Order.OrderStatus.choices)
    start_date = django_filters.DateFilter(
        field_name="created_at", lookup_expr="gte", label="Yaratilgan sana (dan)"
    )
    end_date = django_filters.DateFilter(
        field_name="created_at", lookup_expr="lte", label="Yaratilgan sana (gacha)"
    )

    class Meta:
        model = Order
        fields = [
            "organization",
            "branch",
            "customer",
            "seller",
            "payment_status",
            "order_status",
            "start_date",
            "end_date",
        ]
