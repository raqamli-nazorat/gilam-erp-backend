from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import OrderingFilter, SearchFilter

from apps.base.views import BaseManageViewSet

from ..filters import CarpetRollFilter
from ..models import CarpetRoll
from ..serializers import CarpetRollSerializer


class CarpetRollViewSet(BaseManageViewSet):
    """Rulonlar uchun CRUD ViewSet."""

    queryset = CarpetRoll.objects.select_related("product_party", "warehouse").active()
    serializer_class = CarpetRollSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = CarpetRollFilter
    search_fields = ["roll_number", "product_party__name", "warehouse__name"]
    ordering_fields = ["roll_number", "created_at", "current_length_meters"]

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
