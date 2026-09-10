from django.contrib import admin

from apps.base.admin import BaseModelAdmin

from .models import (
    AccrualRetention,
    Counterparty,
    CounterpartyType,
    Currency,
    CurrencyLedger,
)


@admin.register(AccrualRetention)
class AccrualRetentionAdmin(BaseModelAdmin):
    list_display = (
        "id",
        "name",
        "type",
        "currency",
        "value",
        "is_active",
        "created_at",
    )
    list_filter = ("is_active", "type", "currency", "created_at")
    search_fields = ("name", "currency__name")
    ordering = ("-created_at",)
    autocomplete_fields = ("currency",)


@admin.register(Counterparty)
class CounterpartyAdmin(BaseModelAdmin):
    list_display = ("id", "name", "phone_number", "type", "is_active", "created_at")
    list_filter = ("is_active", "type", "created_at")
    search_fields = ("name", "phone_number", "type__name")
    ordering = ("-created_at",)
    autocomplete_fields = ("type",)


@admin.register(CounterpartyType)
class CounterpartyTypeAdmin(BaseModelAdmin):
    list_display = ("id", "name", "is_active", "created_at")
    list_filter = ("is_active", "created_at")
    search_fields = ("name",)
    ordering = ("-created_at",)


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
