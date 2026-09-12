from rest_framework.routers import DefaultRouter

from .views import CounterpartyTypeViewSet

router = DefaultRouter()
router.register(
    "counterparty-types", CounterpartyTypeViewSet, basename="counterpartytype"
)

urlpatterns = router.urls
