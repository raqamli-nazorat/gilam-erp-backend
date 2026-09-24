import django_filters

from apps.base.filters import UUIDInFilter

from ..models import SupplierPurchaseItem


class SupplierPurchaseItemFilter(django_filters.FilterSet):
    purchase = UUIDInFilter(field_name="purchase_id", lookup_expr="in")
    product_party = UUIDInFilter(field_name="product_party_id", lookup_expr="in")
    roll_number = django_filters.CharFilter(lookup_expr="icontains")
    start_date = django_filters.DateFilter(
        field_name="created_at", lookup_expr="gte", label="Yaratilgan sana (dan)"
    )
    end_date = django_filters.DateFilter(
        field_name="created_at", lookup_expr="lte", label="Yaratilgan sana (gacha)"
    )

    class Meta:
        model = SupplierPurchaseItem
        fields = ["purchase", "product_party", "roll_number", "start_date", "end_date"]
