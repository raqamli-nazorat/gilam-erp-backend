from django.urls import path, include

urlpatterns = [
    path("audits/", include("apps.audits.urls")),
]
