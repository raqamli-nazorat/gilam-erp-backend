from django.urls import include, path

urlpatterns = [
    path("audits/", include("apps.audits.urls")),
    # Domen app'lar — ViewSet/router tayyor bo'lgach ochiladi:
    # path("accounts/", include("apps.accounts.urls")),
    # path("organization/", include("apps.organization.urls")),
    # path("catalog/", include("apps.catalog.urls")),
    # path("warehouse/", include("apps.warehouse.urls")),
    # path("sales/", include("apps.sales.urls")),
    # path("finance/", include("apps.finance.urls")),
    # path("procurement/", include("apps.procurement.urls")),
    # path("hr/", include("apps.hr.urls")),
]
