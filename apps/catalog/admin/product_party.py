from django.contrib import admin

from apps.base.admin import BaseModelAdmin

from ..models import ProductParty


@admin.register(ProductParty)
class ProductPartyAdmin(BaseModelAdmin):
    list_display = (
        "id",
        "branch",
        "party_number",
        "name",
        "quality",
        "design",
        "color",
        "unit",
        "barcode",
        "is_runner",
        "price_per_sqm_purchase",
        "is_active",
        "created_at",
    )
    list_filter = (
        "is_active",
        "branch",
        "quality",
        "design",
        "color",
        "unit",
        "is_runner",
        "created_at",
    )
    search_fields = (
        "party_number",
        "name",
        "description",
        "barcode",
        "branch__name",
        "quality__name",
        "design__name",
    )
    ordering = ("-created_at",)
    autocomplete_fields = ("branch", "quality", "design", "color", "unit")
