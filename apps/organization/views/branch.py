from django.db.models import Count, Prefetch, Q
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.response import Response

from apps.base.views import BaseManageViewSet
from apps.hr.models import Employee
from apps.hr.services import annotate_latest_position
from apps.warehouse.models import Warehouse

from ..filters import BranchFilter
from ..models import Branch
from ..serializers import BranchSerializer


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

    def get_queryset(self):
        """`TenantBranchScopeMixin` skoupidan keyin, detal uchun xodim/ombor ro'yxatlarini prefetch qiladi."""
        queryset = super().get_queryset()

        if self.action == "retrieve":
            queryset = queryset.prefetch_related(
                Prefetch(
                    "employees",
                    queryset=annotate_latest_position(
                        Employee.objects.active()
                    ).order_by("full_name"),
                ),
                Prefetch(
                    "warehouses",
                    queryset=Warehouse.objects.active().order_by("name"),
                ),
            )

        return queryset

    @property
    def serializer_fields(self):
        """Ro'yxatda xodim/ombor ro'yxatlarini (N+1 oldini olish uchun) chiqarmaydi."""
        if self.action == "list":
            return [
                "id",
                "organization",
                "name",
                "phone",
                "region",
                "district",
                "address",
                "is_closed",
                "closing_reason",
                "warehouses_count",
                "employees_count",
                "created_at",
                "updated_at",
            ]
        return None

    @action(detail=False, methods=["get"])
    def count(self, request):
        queryset = self.filter_queryset(self.get_queryset())
        return Response(
            {
                "active": queryset.filter(is_closed=False).count(),
                "closed": queryset.filter(is_closed=True).count(),
            }
        )

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
