from django.contrib import admin

from apps.base.admin import BaseModelAdmin

from .models import (
    Design,
    DesignPhoto,
    ProductColor,
    ProductParty,
    Quality,
    Unit,
)


@admin.register(Design)
class DesignAdmin(BaseModelAdmin):
    list_display = ("id", "quality", "name", "is_active", "created_at")
    list_filter = ("is_active", "quality", "created_at")
    search_fields = ("name", "description", "quality__name")
    ordering = ("-created_at",)
    autocomplete_fields = ("quality",)


@admin.register(DesignPhoto)
class DesignPhotoAdmin(BaseModelAdmin):
    list_display = ("id", "design", "photo_path", "name", "is_active", "created_at")
    list_filter = ("is_active", "design", "created_at")
    search_fields = ("photo_path", "name", "description", "design__name")
    ordering = ("-created_at",)
    autocomplete_fields = ("design",)


@admin.register(ProductColor)
class ProductColorAdmin(BaseModelAdmin):
    list_display = ("id", "name", "color_hex", "is_active", "created_at")
    list_filter = ("is_active", "created_at")
    search_fields = ("name", "description", "color_hex")
    ordering = ("-created_at",)


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


@admin.register(Quality)
class QualityAdmin(BaseModelAdmin):
    list_display = ("id", "name", "is_active", "created_at")
    list_filter = ("is_active", "created_at")
    search_fields = ("name", "description")
    ordering = ("-created_at",)


@admin.register(Unit)
class UnitAdmin(BaseModelAdmin):
    list_display = ("id", "name", "is_active", "created_at")
    list_filter = ("is_active", "created_at")
    search_fields = ("name", "description")
    ordering = ("-created_at",)
