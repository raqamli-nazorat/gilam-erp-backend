from rest_framework.routers import DefaultRouter

from .views import ProductColorViewSet, QualityViewSet, UnitViewSet

router = DefaultRouter()
router.register("qualities", QualityViewSet, basename="quality")
router.register("units", UnitViewSet, basename="unit")
router.register("colors", ProductColorViewSet, basename="productcolor")

urlpatterns = router.urls
