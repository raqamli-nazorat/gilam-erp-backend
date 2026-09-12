from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import OrderingFilter, SearchFilter

from apps.base.views import BaseManageViewSet

from ..filters import ProductColorFilter
from ..models import ProductColor
from ..serializers import ProductColorSerializer


class ProductColorViewSet(BaseManageViewSet):

    queryset = ProductColor.objects.active()
    serializer_class = ProductColorSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = ProductColorFilter
    search_fields = ["name", "description", "color_hex"]
    ordering_fields = ["name", "created_at"]
