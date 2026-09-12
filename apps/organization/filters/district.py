import django_filters

from apps.base.filters import UUIDInFilter

from ..models import District


class DistrictFilter(django_filters.FilterSet):
    name = django_filters.CharFilter(lookup_expr="icontains")
    region = UUIDInFilter(field_name="region_id", lookup_expr="in")

    class Meta:
        model = District
        fields = ["name", "region"]
