from rest_framework.routers import DefaultRouter

from .views import (
    CarpetRollViewSet,
    ProductStockViewSet,
    StockTransactionViewSet,
    WarehouseViewSet,
)

router = DefaultRouter()
router.register("warehouses", WarehouseViewSet, basename="warehouse")
router.register("product-stocks", ProductStockViewSet, basename="productstock")
router.register("carpet-rolls", CarpetRollViewSet, basename="carpetroll")
router.register(
    "stock-transactions", StockTransactionViewSet, basename="stocktransaction"
)

urlpatterns = router.urls
