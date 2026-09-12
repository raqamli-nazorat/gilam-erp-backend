from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import OrderingFilter, SearchFilter

from apps.base.views import BaseManageViewSet

from ..filters import RecruitmentDismissalFilter
from ..models import RecruitmentDismissal
from ..serializers import RecruitmentDismissalSerializer


class RecruitmentDismissalViewSet(BaseManageViewSet):
    queryset = (
        RecruitmentDismissal.objects.active()
        .select_related("branch", "employee", "position")
    )
    serializer_class = RecruitmentDismissalSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = RecruitmentDismissalFilter
    search_fields = [
        "employee__full_name",
        "employee__phone_number",
        "position__name",
        "branch__name",
        "card_number",
        "dismissal_reason",
    ]
    ordering_fields = ["rec_dism_date", "created_at"]
