from django.urls import include, path

from apps.base.counts import CountsView

urlpatterns = [
    path("counts/", CountsView.as_view(), name="counts"),
    path("audits/", include("apps.audits.urls")),
    path("auth/", include("apps.accounts.auth_urls")),
    path("accounts/", include("apps.accounts.urls")),
    path("organization/", include("apps.organization.urls")),
    path("catalog/", include("apps.catalog.urls")),
    path("warehouse/", include("apps.warehouse.urls")),
    path("hr/", include("apps.hr.urls")),
    path("finance/", include("apps.finance.urls")),
]
