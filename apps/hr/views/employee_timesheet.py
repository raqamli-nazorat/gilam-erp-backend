from django.db.models import Count, Q
from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import extend_schema
from rest_framework.decorators import action
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.response import Response

from apps.base.views import BaseManageViewSet

from ..filters import EmployeeTimesheetFilter, EmployeeTimesheetItemFilter
from ..models import EmployeeTimesheet, EmployeeTimesheetItem
from ..serializers import EmployeeTimesheetItemSerializer, EmployeeTimesheetSerializer
from ..services.timesheet import approve_timesheet, cancel_timesheet, ensure_draft


class EmployeeTimesheetViewSet(BaseManageViewSet):
    """Xodimlar tabeli (filial va oy bo'yicha) uchun ViewSet."""

    queryset = (
        EmployeeTimesheet.objects.active()
        .select_related("branch")
        .annotate(items_count=Count("items", filter=Q(items__is_active=True)))
    )
    serializer_class = EmployeeTimesheetSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = EmployeeTimesheetFilter
    search_fields = ["branch__name"]
    ordering_fields = ["for_month", "created_at", "updated_at"]
    action_permissions = {
        "approve": ["hr.change_employeetimesheet"],
        "cancel": ["hr.change_employeetimesheet"],
    }

    def perform_destroy(self, instance):
        """Faqat qoralama tabelni o'chirishga ruxsat beradi."""
        ensure_draft(instance)
        super().perform_destroy(instance)

    @extend_schema(request=None, responses=EmployeeTimesheetSerializer)
    @action(detail=True, methods=["post"])
    def approve(self, request, pk=None):
        """Qoralama tabelni tasdiqlaydi."""
        timesheet = approve_timesheet(self.get_object())
        return Response(self.get_serializer(timesheet).data)

    @extend_schema(request=None, responses=EmployeeTimesheetSerializer)
    @action(detail=True, methods=["post"])
    def cancel(self, request, pk=None):
        """Tabelni bekor qiladi."""
        timesheet = cancel_timesheet(self.get_object())
        return Response(self.get_serializer(timesheet).data)


class EmployeeTimesheetItemViewSet(BaseManageViewSet):
    """Tabel qatorlari (xodimning kunlik davomati) uchun ViewSet."""

    queryset = EmployeeTimesheetItem.objects.active().select_related(
        "employee", "employee_timesheet"
    )
    serializer_class = EmployeeTimesheetItemSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = EmployeeTimesheetItemFilter
    search_fields = ["employee__full_name", "employee__phone_number"]
    ordering_fields = ["date", "created_at", "updated_at"]

    def get_queryset(self):
        """Qatorlarni foydalanuvchiga ruxsat etilgan filiallar tabellari bilan cheklaydi."""
        queryset = super().get_queryset()
        user = self.request.user
        if not user.is_authenticated or user.is_system_admin:
            return queryset
        return queryset.filter(
            employee_timesheet__branch__in=user.get_accessible_branches()
        )

    def perform_destroy(self, instance):
        """Faqat qoralama tabeldagi qatorni o'chirishga ruxsat beradi."""
        ensure_draft(instance.employee_timesheet)
        super().perform_destroy(instance)
