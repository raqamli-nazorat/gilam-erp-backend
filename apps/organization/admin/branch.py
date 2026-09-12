from django.contrib import admin

from apps.base.admin import BaseModelAdmin

from ..models import Branch


@admin.register(Branch)
class BranchAdmin(BaseModelAdmin):
    list_display = (
        "id",
        "organization",
        "name",
        "phone",
        "region",
        "district",
        "is_active",
        "created_at",
    )
    list_filter = ("is_active", "organization", "region", "district", "created_at")
    search_fields = (
        "name",
        "phone",
        "address",
        "organization__name",
        "region__name",
        "district__name",
    )
    ordering = ("-created_at",)
    autocomplete_fields = ("organization", "region", "district")
