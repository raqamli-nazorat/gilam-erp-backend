from django.contrib import admin

from apps.base.admin import BaseModelAdmin

from ..models import ProductColor


@admin.register(ProductColor)
class ProductColorAdmin(BaseModelAdmin):
    list_display = ("id", "name", "color_hex", "is_active", "created_at")
    list_filter = ("is_active", "created_at")
    search_fields = ("name", "description", "color_hex")
    ordering = ("-created_at",)
