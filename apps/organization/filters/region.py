import django_filters

from apps.base.filters import UUIDInFilter

from ..models import Region


class RegionFilter(django_filters.FilterSet):
    name = django_filters.CharFilter(lookup_expr="icontains")
    country = UUIDInFilter(field_name="country_id", lookup_expr="in")

    class Meta:
        model = Region
        fields = ["name", "country"]
