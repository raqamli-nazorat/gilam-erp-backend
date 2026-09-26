"""Markaziy bank (cbu.uz) kunlik kurslari va valyutalarni qidirish."""

from datetime import date
from decimal import Decimal

import requests
from django.utils import timezone
from rest_framework.exceptions import APIException, ValidationError

from ..constants import BANK_CURRENCIES
from ..models import Currency, CurrencyLedger

CBU_DAY_URL = "https://cbu.uz/uz/arkhiv-kursov-valyut/json/all/{day}/"
REQUEST_TIMEOUT = 15


class BankUnavailable(APIException):
    """Markaziy bankdan ma'lumot olib bo'lmaganda."""

    status_code = 503
    default_detail = "Markaziy bankdan ma'lumot olib bo'lmadi."
    default_code = "bank_unavailable"


def fetch_bank_rates(day: date) -> list[dict]:
    """Markaziy bank API'sidan berilgan kun kurslarini oladi."""
    try:
        response = requests.get(
            CBU_DAY_URL.format(day=day.isoformat()),
            headers={"User-Agent": "Mozilla/5.0"},
            timeout=REQUEST_TIMEOUT,
        )
        response.raise_for_status()
        return response.json()
    except (requests.RequestException, ValueError) as exc:
        raise BankUnavailable() from exc


def search_currencies(query: str = "") -> list[dict]:
    """Tayyor ro'yxatdan valyutalarni kod yoki nom (uz/en/ru) bo'yicha qidiradi."""
    query = query.strip().lower()
    return [
        {"short_name": code, "name": name_uz}
        for code, name_uz, name_en, name_ru in BANK_CURRENCIES
        if query in f"{code} {name_uz} {name_en} {name_ru}".lower()
    ]


def rates_from_rows(rows: list[dict]) -> dict[str, Decimal]:
    """Bank qatorlarini {kod: 1 birlik uchun so'mdagi qiymat} ko'rinishiga keltiradi."""
    return {
        row["Ccy"]: (Decimal(row["Rate"]) / Decimal(row["Nominal"])).quantize(
            Decimal("0.01")
        )
        for row in rows
    }


def sync_ledgers(day: date | None = None) -> list[CurrencyLedger]:
    """Bankdan kursni olib, bazadagi valyutalar uchun shu kun ledger'ini yaratadi/yangilaydi."""
    day = day or timezone.localdate()
    rows = fetch_bank_rates(day)
    if not rows:
        raise ValidationError({"day": "Bu sana uchun Markaziy bank kursi topilmadi."})
    rates = rates_from_rows(rows)
    currencies = list(Currency.objects.active().filter(short_name__in=rates))
    existing = {
        ledger.currency_id: ledger
        for ledger in CurrencyLedger.objects.active()
        .select_related("currency")
        .filter(day=day, currency__in=currencies)
    }
    ledgers = []
    for currency in currencies:
        value = rates[currency.short_name]
        ledger = existing.get(currency.id)
        if ledger is None:
            ledger = CurrencyLedger.objects.create(
                currency=currency, day=day, value=value
            )
        else:
            ledger.value = value
            ledger.save(update_fields=["value", "updated_at"])
        ledgers.append(ledger)
    return ledgers
