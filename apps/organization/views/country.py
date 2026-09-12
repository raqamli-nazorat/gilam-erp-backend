from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import OrderingFilter, SearchFilter

from apps.base.views import BaseManageViewSet

from ..filters import CountryFilter
from ..models import Country
from ..serializers import CountrySerializer


class CountryViewSet(BaseManageViewSet):
    queryset = Country.objects.active()
    serializer_class = CountrySerializer
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = CountryFilter
    search_fields = ["name"]
    ordering_fields = ["name", "created_at"]
    safe_methods_unrestricted = True

