from django.urls import include, path

urlpatterns = [
    path("audits/", include("apps.audits.urls")),
    path("auth/", include("apps.accounts.auth_urls")),
    path("accounts/", include("apps.accounts.urls")),
    path("organization/", include("apps.organization.urls")),
]
