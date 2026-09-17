from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.decorators import action
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.response import Response

from apps.base.views import BaseManageViewSet

from ..filters import EmployeeFilter
from ..models import Employee
from ..serializers import EmployeeEmploymentHistorySerializer, EmployeeSerializer
from ..services import (
    annotate_employee_status,
    get_employee_employment_history,
    get_employee_status_counts,
)


class EmployeeViewSet(BaseManageViewSet):
    queryset = annotate_employee_status(
        Employee.objects.active().select_related(
            "organization", "branch", "region", "district"
        )
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

    @action(detail=False, methods=["get"])
    def counts(self, request):
        queryset = self.filter_queryset(self.get_queryset())
        return Response(get_employee_status_counts(queryset))

    @action(detail=True, methods=["get"], url_path="employment-history")
    def employment_history(self, request, pk=None):
        employee = self.get_object()
        history = get_employee_employment_history(employee)
        serializer = EmployeeEmploymentHistorySerializer(history, many=True)
        return Response(serializer.data)
