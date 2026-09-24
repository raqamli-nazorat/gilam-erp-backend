import django_filters

from apps.base.filters import UUIDInFilter

from ..models import ProductStock


class ProductStockFilter(django_filters.FilterSet):
    warehouse = UUIDInFilter(field_name="warehouse_id", lookup_expr="in")
    product_party = UUIDInFilter(field_name="product_party_id", lookup_expr="in")
    start_date = django_filters.DateFilter(
        field_name="created_at", lookup_expr="gte", label="Yaratilgan sana (dan)"
    )
    end_date = django_filters.DateFilter(
        field_name="created_at", lookup_expr="lte", label="Yaratilgan sana (gacha)"
    )

    class Meta:
        model = ProductStock
        fields = ["warehouse", "product_party", "start_date", "end_date"]
