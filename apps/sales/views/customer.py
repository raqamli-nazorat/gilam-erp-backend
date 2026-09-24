from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import OrderingFilter, SearchFilter

from apps.base.views import BaseManageViewSet

from ..filters import CustomerFilter
from ..models import Customer
from ..serializers import CustomerSerializer


class CustomerViewSet(BaseManageViewSet):
    """Mijozlar uchun CRUD ViewSet."""

    queryset = Customer.objects.select_related("organization").active()
    serializer_class = CustomerSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = CustomerFilter
    search_fields = ["full_name", "phone", "address"]
    ordering_fields = ["full_name", "created_at"]
