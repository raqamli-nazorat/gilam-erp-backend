from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import OrderingFilter, SearchFilter

from apps.base.views import BaseManageViewSet

from ..filters import EmployeeFilter
from ..models import Employee
from ..serializers import EmployeeSerializer


class EmployeeViewSet(BaseManageViewSet):
    queryset = (
        Employee.objects.active()
        .select_related("organization", "branch", "region", "district")
    )
    serializer_class = EmployeeSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = EmployeeFilter
    search_fields = [
        "full_name",
        "phone_number",
        "passport_seria",
        "passport_number",
        "jsshr",
        "stir",
        "address",
    ]
    ordering_fields = ["full_name", "created_at"]
