from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import OrderingFilter, SearchFilter

from apps.base.views import BaseManageViewSet

from ..filters import PaymentFilter
from ..models import Payment
from ..serializers import PaymentSerializer


class PaymentViewSet(BaseManageViewSet):
    """To'lovlar uchun CRUD ViewSet."""

    queryset = Payment.objects.select_related(
        "organization", "order", "installment_agreement", "customer"
    ).active()
    serializer_class = PaymentSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = PaymentFilter
    search_fields = ["customer__full_name"]
    ordering_fields = ["created_at", "amount"]
