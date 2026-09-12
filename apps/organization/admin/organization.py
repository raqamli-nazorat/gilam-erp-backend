from django.contrib import admin

from apps.base.admin import BaseModelAdmin

from ..models import Organization


@admin.register(Organization)
class OrganizationAdmin(BaseModelAdmin):
    list_display = (
        "id",
        "name",
        "inn",
        "phone",
        "director",
        "region",
        "district",
        "prefix",
        "is_active",
        "created_at",
    )
    list_filter = ("is_active", "region", "district", "created_at")
    search_fields = (
        "name",
        "inn",
        "phone",
        "director",
        "address",
        "prefix",
        "region__name",
        "district__name",
    )
    ordering = ("-created_at",)
    autocomplete_fields = ("region", "district")
