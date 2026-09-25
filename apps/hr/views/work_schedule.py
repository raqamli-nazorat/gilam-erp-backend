from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import OrderingFilter, SearchFilter

from apps.base.views import BaseManageViewSet

from ..filters import WorkScheduleFilter, WorkScheduleItemFilter
from ..models import WorkSchedule, WorkScheduleItem
from ..serializers import WorkScheduleItemSerializer, WorkScheduleSerializer


class WorkScheduleViewSet(BaseManageViewSet):
    queryset = WorkSchedule.objects.select_related("branch")
    serializer_class = WorkScheduleSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = WorkScheduleFilter
    search_fields = ["name", "description"]
    ordering_fields = ["name", "from_date", "to_date", "created_at", "updated_at"]


class WorkScheduleItemViewSet(BaseManageViewSet):
    queryset = WorkScheduleItem.objects.select_related("work_schedule")
    serializer_class = WorkScheduleItemSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = WorkScheduleItemFilter
    search_fields = ["name"]
    ordering_fields = ["name", "day_date", "created_at", "updated_at"]
