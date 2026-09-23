from rest_framework.routers import DefaultRouter

from .views import (
    DesignViewSet,
    ProductColorViewSet,
    ProductPartyViewSet,
    QualityViewSet,
    UnitViewSet,
)

router = DefaultRouter()
router.register("qualities", QualityViewSet, basename="quality")
router.register("units", UnitViewSet, basename="unit")
router.register("colors", ProductColorViewSet, basename="productcolor")
router.register("designs", DesignViewSet, basename="design")
router.register("product-parties", ProductPartyViewSet, basename="productparty")

urlpatterns = router.urls
