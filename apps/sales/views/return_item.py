from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import OrderingFilter

from apps.base.views import BaseManageViewSet

from ..filters import ReturnItemFilter
from ..models import ReturnItem
from ..serializers import ReturnItemSerializer


class ReturnItemViewSet(BaseManageViewSet):
    """Qaytarish qatorlari uchun CRUD ViewSet."""

    queryset = ReturnItem.objects.select_related("return_order", "order_item").active()
    serializer_class = ReturnItemSerializer
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_class = ReturnItemFilter
    ordering_fields = ["created_at"]

    def get_queryset(self):
        """`TenantBranchScopeMixin` `return_order__organization`/`return_order__branch`ni bilmaydi — qo'lda cheklaymiz."""
        queryset = super().get_queryset()

        user = getattr(self.request, "user", None)
        if (
            user
            and user.is_authenticated
            and not getattr(user, "is_system_admin", False)
        ):
            accessible_branch_ids = user.get_accessible_branches().values_list(
                "id", flat=True
            )
            queryset = queryset.filter(
                return_order__organization_id=user.organization_id,
                return_order__branch_id__in=accessible_branch_ids,
            )

        return queryset
