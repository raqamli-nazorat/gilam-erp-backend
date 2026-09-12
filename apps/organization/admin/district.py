from django.contrib import admin

from apps.base.admin import BaseModelAdmin

from ..models import District


@admin.register(District)
class DistrictAdmin(BaseModelAdmin):
    list_display = ("id", "region", "name", "is_active", "created_at")
    list_filter = ("is_active", "region", "created_at")
    search_fields = ("name", "region__name")
    ordering = ("-created_at",)
    autocomplete_fields = ("region",)
