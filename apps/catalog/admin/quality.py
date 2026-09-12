from django.contrib import admin

from apps.base.admin import BaseModelAdmin

from ..models import Quality


@admin.register(Quality)
class QualityAdmin(BaseModelAdmin):
    list_display = ("id", "name", "is_active", "created_at")
    list_filter = ("is_active", "created_at")
    search_fields = ("name", "description")
    ordering = ("-created_at",)
