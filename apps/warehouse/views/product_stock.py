from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import OrderingFilter, SearchFilter

from apps.base.views import BaseManageViewSet

from ..filters import ProductStockFilter
from ..models import ProductStock
from ..serializers import ProductStockSerializer


class ProductStockViewSet(BaseManageViewSet):
    """Ombor qoldiqlari uchun CRUD ViewSet."""

    queryset = ProductStock.objects.select_related(
        "warehouse", "product_party"
    ).active()
    serializer_class = ProductStockSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = ProductStockFilter
    search_fields = ["warehouse__name", "product_party__name"]
    ordering_fields = ["created_at", "quantity", "total_length_meters"]

    def get_queryset(self):
        """`TenantBranchScopeMixin` `warehouse__branch`ni bilmaydi — shuning uchun qo'lda cheklaymiz."""
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
            queryset = queryset.filter(warehouse__branch_id__in=accessible_branch_ids)

        return queryset
