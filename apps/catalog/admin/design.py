from django.contrib import admin

from apps.base.admin import BaseModelAdmin

from ..models import Design, DesignPhoto


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
