from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import OrderingFilter, SearchFilter

from apps.base.views import BaseManageViewSet

from ..filters import InstallmentAgreementFilter
from ..models import InstallmentAgreement
from ..serializers import InstallmentAgreementSerializer


class InstallmentAgreementViewSet(BaseManageViewSet):
    """Muddatli to'lov shartnomalari uchun CRUD ViewSet."""

    queryset = InstallmentAgreement.objects.select_related(
        "organization", "order", "customer"
    ).active()
    serializer_class = InstallmentAgreementSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = InstallmentAgreementFilter
    search_fields = ["agreement_number", "customer__full_name"]
    ordering_fields = ["created_at", "total_amount"]
