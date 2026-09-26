from django.contrib import admin

from apps.base.admin import BaseModelAdmin

from ..models import AccrualRetention


@admin.register(AccrualRetention)
class AccrualRetentionAdmin(BaseModelAdmin):
    list_display = (
        "id",
        "name",
        "type",
        "is_retention",
        "currency",
        "value",
        "is_active",
        "created_at",
    )
    list_filter = ("is_active", "type", "is_retention", "currency", "created_at")
    search_fields = ("name", "currency__name")
    ordering = ("-created_at",)
    autocomplete_fields = ("currency",)
