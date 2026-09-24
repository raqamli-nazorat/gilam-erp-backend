from rest_framework.routers import DefaultRouter

from .views import (
    CustomerViewSet,
    OrderItemViewSet,
    OrderViewSet,
    ReturnItemViewSet,
    ReturnOrderViewSet,
)

router = DefaultRouter()
router.register("customers", CustomerViewSet, basename="customer")
router.register("orders", OrderViewSet, basename="order")
router.register("order-items", OrderItemViewSet, basename="orderitem")
router.register("return-orders", ReturnOrderViewSet, basename="returnorder")
router.register("return-items", ReturnItemViewSet, basename="returnitem")

urlpatterns = router.urls
