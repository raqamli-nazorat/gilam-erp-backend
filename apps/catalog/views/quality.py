from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import OrderingFilter, SearchFilter

from apps.base.views import BaseManageViewSet

from ..filters import QualityFilter
from ..models import Quality
from ..serializers import QualitySerializer


class QualityViewSet(BaseManageViewSet):

    queryset = Quality.objects.all()
    serializer_class = QualitySerializer
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = QualityFilter
    search_fields = ["name", "description"]
    ordering_fields = ["name", "created_at"]
