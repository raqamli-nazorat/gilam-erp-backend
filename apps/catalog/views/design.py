from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import OrderingFilter, SearchFilter

from apps.base.views import BaseManageViewSet

from ..filters import DesignFilter
from ..models import Design
from ..serializers import DesignSerializer


class DesignViewSet(BaseManageViewSet):
    """Dizaynlar uchun CRUD ViewSet."""

    queryset = Design.objects.select_related("quality").active()
    serializer_class = DesignSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = DesignFilter
    search_fields = ["name", "description", "quality__name"]
    ordering_fields = ["name", "created_at"]
