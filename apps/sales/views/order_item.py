from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import OrderingFilter, SearchFilter

from apps.base.views import BaseManageViewSet

from ..filters import OrderItemFilter
from ..models import OrderItem
from ..serializers import OrderItemSerializer


class OrderItemViewSet(BaseManageViewSet):
    """Chek qatorlari uchun CRUD ViewSet."""

    queryset = OrderItem.objects.select_related(
        "order", "product_party", "roll", "warehouse"
    ).active()
    serializer_class = OrderItemSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = OrderItemFilter
    search_fields = ["product_party__name"]
    ordering_fields = ["created_at"]

    def get_queryset(self):
        """`TenantBranchScopeMixin` `order__organization`/`order__branch`ni bilmaydi — qo'lda cheklaymiz."""
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
                order__organization_id=user.organization_id,
                order__branch_id__in=accessible_branch_ids,
            )

        return queryset
