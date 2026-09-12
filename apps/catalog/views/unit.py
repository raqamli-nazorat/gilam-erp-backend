from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import OrderingFilter, SearchFilter

from apps.base.views import BaseManageViewSet

from ..filters import UnitFilter
from ..models import Unit
from ..serializers import UnitSerializer


class UnitViewSet(BaseManageViewSet):

    queryset = Unit.objects.active()
    serializer_class = UnitSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = UnitFilter
    search_fields = ["name", "description"]
    ordering_fields = ["name", "created_at"]
