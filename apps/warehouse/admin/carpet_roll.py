from django.contrib import admin

from apps.base.admin import BaseModelAdmin

from ..models import CarpetRoll


@admin.register(CarpetRoll)
class CarpetRollAdmin(BaseModelAdmin):
    list_display = (
        "id",
        "roll_number",
        "product_party",
        "warehouse",
        "current_length_meters",
        "status",
        "is_active",
        "created_at",
    )
    list_filter = ("is_active", "status", "is_offcut", "warehouse", "created_at")
    search_fields = ("roll_number", "product_party__name", "warehouse__name")
    ordering = ("-created_at",)
    autocomplete_fields = ("product_party", "warehouse")
