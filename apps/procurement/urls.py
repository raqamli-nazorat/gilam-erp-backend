from rest_framework.routers import DefaultRouter

from .views import (
    SupplierPurchaseItemViewSet,
    SupplierPurchaseViewSet,
    SupplierViewSet,
)

router = DefaultRouter()
router.register("suppliers", SupplierViewSet, basename="supplier")
router.register("purchases", SupplierPurchaseViewSet, basename="supplierpurchase")
router.register(
    "purchase-items", SupplierPurchaseItemViewSet, basename="supplierpurchaseitem"
)

urlpatterns = router.urls
