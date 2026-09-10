"""
Accounts app ViewSet'lari uchun FilterSet klasslari.
"""

import django_filters

from apps.base.filters import UUIDInFilter

from .models import Role, User


class RoleFilter(django_filters.FilterSet):
    """Rollarni nomi bo'yicha filtrlaydi."""

    name = django_filters.CharFilter(lookup_expr="icontains")

    class Meta:
        model = Role
        fields = ["name"]


class UserFilter(django_filters.FilterSet):
    """Foydalanuvchilarni F.I.Sh., telefon, rol, filial va staff holati bo'yicha filtrlaydi."""

    full_name = django_filters.CharFilter(lookup_expr="icontains")
    phone_number = django_filters.CharFilter(lookup_expr="icontains")
    role = UUIDInFilter(field_name="role_id", lookup_expr="in")
    branch = UUIDInFilter(field_name="branch_id", lookup_expr="in")

    class Meta:
        model = User
        fields = ["full_name", "phone_number", "role", "branch", "is_staff"]
