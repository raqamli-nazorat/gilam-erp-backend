from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import OrderingFilter, SearchFilter

from apps.base.views import BaseManageViewSet

from ..filters import SupplierPurchaseItemFilter
from ..models import SupplierPurchaseItem
from ..serializers import SupplierPurchaseItemSerializer


class SupplierPurchaseItemViewSet(BaseManageViewSet):
    """Xarid qatorlari uchun CRUD ViewSet."""

    queryset = SupplierPurchaseItem.objects.select_related(
        "purchase", "product_party"
    ).active()
    serializer_class = SupplierPurchaseItemSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = SupplierPurchaseItemFilter
    search_fields = ["roll_number", "product_party__name"]
    ordering_fields = ["created_at"]

    def get_queryset(self):
        """`TenantBranchScopeMixin` `purchase__organization`ni bilmaydi — qo'lda cheklaymiz."""
        queryset = super().get_queryset()

        user = getattr(self.request, "user", None)
        if (
            user
            and user.is_authenticated
            and not getattr(user, "is_system_admin", False)
        ):
            queryset = queryset.filter(purchase__organization_id=user.organization_id)

        return queryset
