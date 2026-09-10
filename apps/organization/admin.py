from django.contrib import admin

from apps.base.admin import BaseModelAdmin

from .models import (
    Branch,
    Country,
    District,
    Organization,
    Region,
)


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


@admin.register(Country)
class CountryAdmin(BaseModelAdmin):
    list_display = ("id", "name", "is_active", "created_at")
    list_filter = ("is_active", "created_at")
    search_fields = ("name",)
    ordering = ("-created_at",)


@admin.register(District)
class DistrictAdmin(BaseModelAdmin):
    list_display = ("id", "region", "name", "is_active", "created_at")
    list_filter = ("is_active", "region", "created_at")
    search_fields = ("name", "region__name")
    ordering = ("-created_at",)
    autocomplete_fields = ("region",)


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


@admin.register(Region)
class RegionAdmin(BaseModelAdmin):
    list_display = ("id", "name", "country", "is_active", "created_at")
    list_filter = ("is_active", "country", "created_at")
    search_fields = ("name", "country__name")
    ordering = ("-created_at",)
    autocomplete_fields = ("country",)
