from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import OrderingFilter, SearchFilter

from apps.base.views import BaseReadOnlyViewSet

from ..filters import EmployeeLedgerFilter
from ..models import EmployeeLedger
from ..serializers import EmployeeLedgerSerializer


class EmployeeLedgerViewSet(BaseReadOnlyViewSet):
    queryset = (
        EmployeeLedger.objects.active()
        .select_related("branch", "employee")
    )
    serializer_class = EmployeeLedgerSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = EmployeeLedgerFilter
    search_fields = [
        "employee__full_name",
        "employee__phone_number",
        "branch__name",
    ]
    ordering_fields = ["type", "created_at"]
