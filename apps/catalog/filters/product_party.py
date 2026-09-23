import django_filters

from apps.base.filters import UUIDInFilter

from ..models import ProductParty


class ProductPartyFilter(django_filters.FilterSet):
    name = django_filters.CharFilter(lookup_expr="icontains")
    party_number = django_filters.CharFilter(lookup_expr="icontains")
    barcode = django_filters.CharFilter(lookup_expr="icontains")
    branch = UUIDInFilter(field_name="branch_id", lookup_expr="in")
    quality = UUIDInFilter(field_name="quality_id", lookup_expr="in")
    design = UUIDInFilter(field_name="design_id", lookup_expr="in")
    color = UUIDInFilter(field_name="color_id", lookup_expr="in")
    unit = UUIDInFilter(field_name="unit_id", lookup_expr="in")
    is_runner = django_filters.BooleanFilter()
    start_date = django_filters.DateFilter(
        field_name="created_at", lookup_expr="gte", label="Yaratilgan sana (dan)"
    )
    end_date = django_filters.DateFilter(
        field_name="created_at", lookup_expr="lte", label="Yaratilgan sana (gacha)"
    )

    class Meta:
        model = ProductParty
        fields = [
            "name",
            "party_number",
            "barcode",
            "branch",
            "quality",
            "design",
            "color",
            "unit",
            "is_runner",
            "start_date",
            "end_date",
        ]
