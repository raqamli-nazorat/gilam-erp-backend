import django_filters

from apps.base.filters import UUIDInFilter

from ..models import User


class UserFilter(django_filters.FilterSet):
    full_name = django_filters.CharFilter(lookup_expr="icontains")
    phone_number = django_filters.CharFilter(lookup_expr="icontains")
    role = UUIDInFilter(field_name="role_id", lookup_expr="in")
    organization = UUIDInFilter(field_name="organization_id", lookup_expr="in")
    branch = UUIDInFilter(field_name="branch_id", lookup_expr="in")
    employee = UUIDInFilter(field_name="employee_id", lookup_expr="in")

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
