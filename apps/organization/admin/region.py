from django.contrib import admin

from apps.base.admin import BaseModelAdmin

from ..models import Region


@admin.register(Region)
class RegionAdmin(BaseModelAdmin):
    list_display = ("id", "name", "country", "is_active", "created_at")
    list_filter = ("is_active", "country", "created_at")
    search_fields = ("name", "country__name")
    ordering = ("-created_at",)
    autocomplete_fields = ("country",)
