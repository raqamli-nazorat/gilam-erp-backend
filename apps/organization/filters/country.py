import django_filters

from ..models import Country


class CountryFilter(django_filters.FilterSet):
    name = django_filters.CharFilter(lookup_expr="icontains")

    class Meta:
        model = Country
        fields = ["name"]
