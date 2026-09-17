import django_filters

from apps.base.filters import UUIDInFilter

from ..models import User, UserBlockLog


class UserFilter(django_filters.FilterSet):
    full_name = django_filters.CharFilter(lookup_expr="icontains")
    phone_number = django_filters.CharFilter(lookup_expr="icontains")
    role = UUIDInFilter(field_name="role_id", lookup_expr="in")
    organization = UUIDInFilter(
        field_name="employee__organization_id", lookup_expr="in"
    )
    branch = UUIDInFilter(field_name="employee__branch_id", lookup_expr="in")
    employee = UUIDInFilter(field_name="employee_id", lookup_expr="in")
    is_blocked = django_filters.BooleanFilter(method="filter_is_blocked")

    def filter_is_blocked(self, queryset, name, value):
        """`get_queryset` dagi `latest_block_type` annotatsiyasi bo'yicha filtrlaydi."""
        if value:
            return queryset.filter(latest_block_type=UserBlockLog.Type.BLOCK)
        return queryset.exclude(latest_block_type=UserBlockLog.Type.BLOCK)

    class Meta:
        model = User
        fields = [
            "full_name",
            "phone_number",
            "role",
            "organization",
            "branch",
            "employee",
            "is_staff",
        ]
