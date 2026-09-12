from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import OrderingFilter, SearchFilter

from apps.base.views import BaseManageViewSet

from ..filters import WorkScheduleFilter
from ..models import WorkSchedule
from ..serializers import WorkScheduleSerializer


class WorkScheduleViewSet(BaseManageViewSet):
    queryset = (
        WorkSchedule.objects.active()
        .select_related("branch")
        .prefetch_related("items")
    )
    serializer_class = WorkScheduleSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = WorkScheduleFilter
    search_fields = ["name", "description", "branch__name"]
    ordering_fields = ["name", "from_date", "to_date", "created_at"]
