from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import OrderingFilter, SearchFilter

from apps.base.views import BaseManageViewSet

from ..filters import CounterpartyTypeFilter
from ..models import CounterpartyType
from ..serializers import CounterpartyTypeSerializer


class CounterpartyTypeViewSet(BaseManageViewSet):

    queryset = CounterpartyType.objects.all()
    serializer_class = CounterpartyTypeSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = CounterpartyTypeFilter
    search_fields = ["name"]
    ordering_fields = ["name", "created_at"]
