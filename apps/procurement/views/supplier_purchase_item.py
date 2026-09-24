from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import OrderingFilter, SearchFilter

from apps.base.views import BaseManageViewSet

from ..filters import SupplierPurchaseItemFilter
from ..models import SupplierPurchaseItem
from ..serializers import (
    SupplierPurchaseItemCreateSerializer,
    SupplierPurchaseItemSerializer,
    SupplierPurchaseItemUpdateSerializer,
)
from ..services import recalculate_totals


class SupplierPurchaseItemViewSet(BaseManageViewSet):
    """Xarid qatorlari uchun CRUD ViewSet.

    `create`/`update`/`partial_update`/`destroy` — qatorga bog'liq xarid hujjatining
    `total_amount`/`debt_amount`ini avtomatik qayta hisoblaydi.
    """

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

    def get_serializer_class(self):
        if self.action == "create":
            return SupplierPurchaseItemCreateSerializer
        if self.action in ("update", "partial_update"):
            return SupplierPurchaseItemUpdateSerializer
        return super().get_serializer_class()

    def perform_destroy(self, instance):
        """Qatorni o'chiradi va hujjatning summalarini qayta hisoblaydi."""
        purchase = instance.purchase
        instance.delete()
        recalculate_totals(purchase)
