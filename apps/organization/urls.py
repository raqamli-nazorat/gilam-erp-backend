from rest_framework.routers import DefaultRouter

from .views import (
    BranchViewSet,
    CountryViewSet,
    DistrictViewSet,
    OrganizationViewSet,
    RegionViewSet,
)

router = DefaultRouter()
router.register("countries", CountryViewSet, basename="country")
router.register("regions", RegionViewSet, basename="region")
router.register("districts", DistrictViewSet, basename="district")
router.register("organizations", OrganizationViewSet, basename="organization")
router.register("branches", BranchViewSet, basename="branch")

urlpatterns = router.urls
