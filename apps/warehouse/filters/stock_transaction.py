import django_filters

from apps.base.filters import UUIDInFilter

from ..models import StockTransaction


class StockTransactionFilter(django_filters.FilterSet):
    organization = UUIDInFilter(field_name="organization_id", lookup_expr="in")
    product_party = UUIDInFilter(field_name="product_party_id", lookup_expr="in")
    roll = UUIDInFilter(field_name="roll_id", lookup_expr="in")
    from_warehouse = UUIDInFilter(field_name="from_warehouse_id", lookup_expr="in")
    to_warehouse = UUIDInFilter(field_name="to_warehouse_id", lookup_expr="in")
    transaction_type = django_filters.ChoiceFilter(
        choices=StockTransaction.TransactionType.choices
    )
    ref_type = django_filters.ChoiceFilter(choices=StockTransaction.RefType.choices)
    ref_id = django_filters.UUIDFilter()
    start_date = django_filters.DateFilter(
        field_name="created_at", lookup_expr="gte", label="Yaratilgan sana (dan)"
    )
    end_date = django_filters.DateFilter(
        field_name="created_at", lookup_expr="lte", label="Yaratilgan sana (gacha)"
    )

    class Meta:
        model = StockTransaction
        fields = [
            "organization",
            "product_party",
            "roll",
            "from_warehouse",
            "to_warehouse",
            "transaction_type",
            "ref_type",
            "ref_id",
            "start_date",
            "end_date",
        ]
