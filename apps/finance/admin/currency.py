from django.contrib import admin

from apps.base.admin import BaseModelAdmin

from ..models import Currency, CurrencyLedger


@admin.register(Currency)
class CurrencyAdmin(BaseModelAdmin):
    list_display = ("id", "name", "short_name", "is_active", "created_at")
    list_filter = ("is_active", "created_at")
    search_fields = ("name", "short_name")
    ordering = ("-created_at",)


@admin.register(CurrencyLedger)
class CurrencyLedgerAdmin(BaseModelAdmin):
    list_display = ("id", "currency", "value", "day", "is_active", "created_at")
    list_filter = ("is_active", "currency", "created_at")
    search_fields = ("currency__name",)
    ordering = ("-created_at",)
    autocomplete_fields = ("currency",)
