from rest_framework.routers import DefaultRouter

from .views import (
    CounterpartyTypeViewSet,
    DebtLedgerViewSet,
    InstallmentAgreementViewSet,
    InstallmentScheduleViewSet,
    PaymentViewSet,
)

router = DefaultRouter()
router.register(
    "counterparty-types", CounterpartyTypeViewSet, basename="counterpartytype"
)
router.register("payments", PaymentViewSet, basename="payment")
router.register("debt-ledgers", DebtLedgerViewSet, basename="debtledger")
router.register(
    "installment-agreements",
    InstallmentAgreementViewSet,
    basename="installmentagreement",
)
router.register(
    "installment-schedules",
    InstallmentScheduleViewSet,
    basename="installmentschedule",
)

urlpatterns = router.urls
