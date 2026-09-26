from rest_framework.routers import DefaultRouter

from .views import (
    AccrualRetentionDocumentViewSet,
    AccrualRetentionViewSet,
    CounterpartyTypeViewSet,
    CounterpartyViewSet,
    CurrencyLedgerViewSet,
    CurrencyViewSet,
)

router = DefaultRouter()
router.register(
    "counterparty-types", CounterpartyTypeViewSet, basename="counterpartytype"
)
router.register("counterparties", CounterpartyViewSet, basename="counterparty")
router.register("currencies", CurrencyViewSet, basename="currency")
router.register("currency-ledgers", CurrencyLedgerViewSet, basename="currencyledger")
router.register(
    "accrual-retentions", AccrualRetentionViewSet, basename="accrualretention"
)
router.register(
    "accrual-retention-documents",
    AccrualRetentionDocumentViewSet,
    basename="accrualretentiondocument",
)

urlpatterns = router.urls
