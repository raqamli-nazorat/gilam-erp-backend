from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import OrderingFilter, SearchFilter

from apps.base.views import BaseManageViewSet

from ..filters import WorkScheduleFilter
from ..models import WorkSchedule
from ..serializers import WorkScheduleSerializer


class WorkScheduleViewSet(BaseManageViewSet):
    queryset = WorkSchedule.objects.all()
    serializer_class = WorkScheduleSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = WorkScheduleFilter
    search_fields = ["name", "description"]
    ordering_fields = ["name", "created_at", "updated_at"]
