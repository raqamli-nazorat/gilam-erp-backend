from django.contrib import admin

from apps.base.admin import BaseModelAdmin

from ..models import CounterpartyType


@admin.register(CounterpartyType)
class CounterpartyTypeAdmin(BaseModelAdmin):
    list_display = ("id", "name", "is_active", "created_at")
    list_filter = ("is_active", "created_at")
    search_fields = ("name",)
    ordering = ("-created_at",)
