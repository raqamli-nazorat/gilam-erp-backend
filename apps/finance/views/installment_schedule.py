from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import OrderingFilter

from apps.base.views import BaseManageViewSet

from ..filters import InstallmentScheduleFilter
from ..models import InstallmentSchedule
from ..serializers import InstallmentScheduleSerializer


class InstallmentScheduleViewSet(BaseManageViewSet):
    """Oylik to'lov grafiklari uchun CRUD ViewSet."""

    queryset = InstallmentSchedule.objects.select_related("agreement").active()
    serializer_class = InstallmentScheduleSerializer
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_class = InstallmentScheduleFilter
    ordering_fields = ["due_date", "payment_number", "created_at"]

    def get_queryset(self):
        """`TenantBranchScopeMixin` `agreement__organization`ni bilmaydi — qo'lda cheklaymiz."""
        queryset = super().get_queryset()

        user = getattr(self.request, "user", None)
        if (
            user
            and user.is_authenticated
            and not getattr(user, "is_system_admin", False)
        ):
            queryset = queryset.filter(agreement__organization_id=user.organization_id)

        return queryset
