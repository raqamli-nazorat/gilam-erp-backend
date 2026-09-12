from django.db.models import Count, Q
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.response import Response

from apps.base.views import BaseManageViewSet

from ..filters import BranchFilter
from ..models import Branch
from ..serializers import BranchSerializer
from ..services import get_branch_status_counts


class BranchViewSet(BaseManageViewSet):

    queryset = (
        Branch.objects.active()
        .select_related("organization", "region", "district")
        .annotate(
            warehouses_count=Count(
                "warehouses", filter=Q(warehouses__is_active=True), distinct=True
            ),
            employees_count=Count(
                "employees", filter=Q(employees__is_active=True), distinct=True
            ),
        )
    )
    serializer_class = BranchSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = BranchFilter
    search_fields = ["name", "phone", "address", "organization__name"]
    ordering_fields = ["name", "created_at"]
    action_permissions = {
        "close": ["organization.close_branch"],
        "open": ["organization.open_branch"],
    }

    @action(detail=False, methods=["get"])
    def counts(self, request):
        return Response(get_branch_status_counts())

    @action(detail=True, methods=["patch"])
    def close(self, request, pk=None):
        reason = request.data.get("reason") or request.data.get("closing_reason")
        if not reason or not str(reason).strip():
            return Response(
                {"reason": ["Yopilish sababini kiritish majburiy."]},
                status=status.HTTP_400_BAD_REQUEST,
            )

        branch = self.get_object()
        branch.is_closed = True
        branch.closing_reason = str(reason).strip()
        branch.save(update_fields=["is_closed", "closing_reason", "updated_at"])
        return Response(
            {
                "id": str(branch.id),
                "name": branch.name,
                "is_closed": branch.is_closed,
                "closing_reason": branch.closing_reason,
                "detail": "Filial yopildi.",
            },
            status=status.HTTP_200_OK,
        )

    @action(detail=True, methods=["patch"])
    def open(self, request, pk=None):
        branch = self.get_object()
        branch.is_closed = False
        branch.closing_reason = ""
        branch.save(update_fields=["is_closed", "closing_reason", "updated_at"])
        return Response(
            {
                "id": str(branch.id),
                "name": branch.name,
                "is_closed": branch.is_closed,
                "closing_reason": branch.closing_reason,
                "detail": "Filial qayta ochildi.",
            },
            status=status.HTTP_200_OK,
        )
