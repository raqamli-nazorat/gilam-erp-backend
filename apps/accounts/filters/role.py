import django_filters

from apps.base.filters import UUIDInFilter

from ..models import Role


class RoleFilter(django_filters.FilterSet):
    name = django_filters.CharFilter(lookup_expr="icontains")
    organization = UUIDInFilter(field_name="organization_id", lookup_expr="in")
    is_system = django_filters.BooleanFilter()

    class Meta:
        model = Role
        fields = ["name", "organization", "is_system"]
