from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import OpenApiExample, extend_schema, extend_schema_view
from rest_framework.filters import OrderingFilter, SearchFilter

from apps.base.views import BaseManageViewSet

from ..filters import WorkScheduleFilter
from ..models import WorkSchedule
from ..serializers import WorkScheduleSerializer

DAYS_EXAMPLE = OpenApiExample(
    "Namuna: Dush-Juma smena",
    summary="days: 0=Dushanba, 1=Seshanba, 2=Chorshanba, 3=Payshanba, 4=Juma, 5=Shanba, 6=Yakshanba",
    description="Har bir raqam hafta kunini bildiradi (0 dan boshlanadi). "
    "Masalan [0, 1, 2, 3, 4] — Dushanbadan Jumagacha ishlaydigan smena.",
    value={
        "name": "Kechki smena",
        "description": "14:00-23:00, Dush-Juma",
        "from_hour": "14:00:00",
        "to_hour": "23:00:00",
        "days": [0, 1, 2, 3, 4],
    },
    request_only=True,
)


@extend_schema_view(
    create=extend_schema(examples=[DAYS_EXAMPLE]),
    update=extend_schema(examples=[DAYS_EXAMPLE]),
    partial_update=extend_schema(examples=[DAYS_EXAMPLE]),
)
class WorkScheduleViewSet(BaseManageViewSet):
    queryset = WorkSchedule.objects.all()
    serializer_class = WorkScheduleSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = WorkScheduleFilter
    search_fields = ["name", "description"]
    ordering_fields = ["name", "created_at", "updated_at"]
