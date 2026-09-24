import django_filters

from apps.base.filters import UUIDInFilter

from ..models import ReturnOrder


class ReturnOrderFilter(django_filters.FilterSet):
    organization = UUIDInFilter(field_name="organization_id", lookup_expr="in")
    branch = UUIDInFilter(field_name="branch_id", lookup_expr="in")
    order = UUIDInFilter(field_name="order_id", lookup_expr="in")
    customer = UUIDInFilter(field_name="customer_id", lookup_expr="in")
    start_date = django_filters.DateFilter(
        field_name="created_at", lookup_expr="gte", label="Yaratilgan sana (dan)"
    )
    end_date = django_filters.DateFilter(
        field_name="created_at", lookup_expr="lte", label="Yaratilgan sana (gacha)"
    )

    class Meta:
        model = ReturnOrder
        fields = [
            "organization",
            "branch",
            "order",
            "customer",
            "start_date",
            "end_date",
        ]
