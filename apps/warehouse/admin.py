from django.contrib import admin

from apps.base.admin import BaseModelAdmin

from .models import Warehouse


@admin.register(Warehouse)
class WarehouseAdmin(BaseModelAdmin):
    list_display = ("id", "branch", "name", "is_active", "created_at")
    list_filter = ("is_active", "branch", "created_at")
    search_fields = ("name", "address", "branch__name")
    ordering = ("-created_at",)
    autocomplete_fields = ("branch",)
