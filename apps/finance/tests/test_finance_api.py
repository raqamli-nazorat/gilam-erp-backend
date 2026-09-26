import datetime
from decimal import Decimal
from io import StringIO
from unittest.mock import patch

from django.core.management import call_command
from django.core.management.base import CommandError
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APITestCase

from apps.accounts.models import User
from apps.finance.models import (
    AccrualRetention,
    Counterparty,
    CounterpartyType,
    Currency,
    CurrencyLedger,
)
from apps.finance.services.currency import BankUnavailable

# Markaziy bank API javobi (tashqi servis — mock qilinadi)
BANK_ROWS = [
    {
        "Ccy": "USD",
        "CcyNm_UZ": "AQSH dollari",
        "CcyNm_EN": "US Dollar",
        "CcyNm_RU": "Доллар США",
        "CcyNm_UZC": "АҚШ доллари",
        "Nominal": "1",
        "Rate": "12500.50",
        "Diff": "10.00",
    },
    {
        "Ccy": "EUR",
        "CcyNm_UZ": "EVRO",
        "CcyNm_EN": "Euro",
        "CcyNm_RU": "Евро",
        "CcyNm_UZC": "ЕВРО",
        "Nominal": "1",
        "Rate": "13500.00",
        "Diff": "5.00",
    },
    {
        "Ccy": "VND",
        "CcyNm_UZ": "Vetnam dongi",
        "CcyNm_EN": "Dong",
        "CcyNm_RU": "Донг",
        "CcyNm_UZC": "Донг",
        "Nominal": "10",
        "Rate": "850.00",
        "Diff": "-1.00",
    },
]


class CounterpartyTypeAPITestCase(APITestCase):
    def setUp(self):
        self.user = User.objects.create_superuser(
            phone_number="+998901112233",
            password="StrongPass123",
            full_name="Test Admin",
        )
        self.client.force_authenticate(self.user)
        self.counterparty_type = CounterpartyType.objects.create(
            name="Yetkazib beruvchi"
        )

    def test_list_counterparty_types_success(self):
        response = self.client.get("/api/v1/finance/counterparty-types/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 1)

    def test_create_counterparty_type_success(self):
        response = self.client.post(
            "/api/v1/finance/counterparty-types/",
            {"name": "Xaridor"},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(CounterpartyType.objects.filter(name="Xaridor").exists())

    def test_create_counterparty_type_invalid_data(self):
        response = self.client.post(
            "/api/v1/finance/counterparty-types/", {}, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_delete_counterparty_type_soft_delete(self):
        response = self.client.delete(
            f"/api/v1/finance/counterparty-types/{self.counterparty_type.id}/"
        )
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.counterparty_type.refresh_from_db()
        self.assertFalse(self.counterparty_type.is_active)
        list_response = self.client.get("/api/v1/finance/counterparty-types/")
        self.assertEqual(list_response.data["count"], 0)

    def test_list_counterparty_types_unauthenticated(self):
        self.client.force_authenticate(user=None)
        response = self.client.get("/api/v1/finance/counterparty-types/")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class FinanceBaseAPITestCase(APITestCase):
    def setUp(self):
        patcher = patch(
            "apps.finance.services.currency.fetch_bank_rates", return_value=BANK_ROWS
        )
        self.bank = patcher.start()
        self.addCleanup(patcher.stop)
        self.user = User.objects.create_superuser(
            phone_number="+998901112244",
            password="StrongPass123",
            full_name="Test Admin",
        )
        self.client.force_authenticate(self.user)
        self.currency = Currency.objects.create(name="AQSh dollari", short_name="USD")


class CurrencyAPITestCase(FinanceBaseAPITestCase):
    def test_list_currencies_success(self):
        response = self.client.get("/api/v1/finance/currencies/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 1)

    def test_create_currency_success(self):
        response = self.client.post(
            "/api/v1/finance/currencies/",
            {"name": "O'zbekiston so'mi", "short_name": "UZS"},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(Currency.objects.filter(short_name="UZS").exists())

    def test_create_currency_uppercases_short_name_success(self):
        response = self.client.post(
            "/api/v1/finance/currencies/",
            {"name": "EVRO", "short_name": "eur"},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(Currency.objects.filter(short_name="EUR").exists())

    def test_create_currency_invalid_data(self):
        response = self.client.post("/api/v1/finance/currencies/", {}, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_currency_unknown_code_invalid_data(self):
        response = self.client.post(
            "/api/v1/finance/currencies/",
            {"name": "Noma'lum", "short_name": "XXX"},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_currency_duplicate_invalid_data(self):
        response = self.client.post(
            "/api/v1/finance/currencies/",
            {"name": "AQSh dollari", "short_name": "USD"},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_available_currencies_search_by_code_success(self):
        response = self.client.get(
            "/api/v1/finance/currencies/available/", {"search": "usd"}
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["short_name"], "USD")
        self.assertTrue(response.data[0]["exists"])

    def test_available_currencies_search_by_name_success(self):
        response = self.client.get(
            "/api/v1/finance/currencies/available/", {"search": "euro"}
        )
        self.assertEqual(response.data[0]["short_name"], "EUR")
        self.assertFalse(response.data[0]["exists"])

    def test_available_does_not_call_bank_success(self):
        self.client.get("/api/v1/finance/currencies/available/", {"search": "usd"})
        self.bank.assert_not_called()

    def test_delete_currency_soft_delete(self):
        response = self.client.delete(f"/api/v1/finance/currencies/{self.currency.id}/")
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.currency.refresh_from_db()
        self.assertFalse(self.currency.is_active)
        list_response = self.client.get("/api/v1/finance/currencies/")
        self.assertEqual(list_response.data["count"], 0)

    def test_delete_currency_not_found(self):
        self.currency.delete()
        response = self.client.delete(f"/api/v1/finance/currencies/{self.currency.id}/")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_delete_currency_unauthenticated(self):
        self.client.force_authenticate(user=None)
        response = self.client.delete(f"/api/v1/finance/currencies/{self.currency.id}/")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_available_currencies_unauthenticated(self):
        self.client.force_authenticate(user=None)
        response = self.client.get("/api/v1/finance/currencies/available/")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_list_currencies_unauthenticated(self):
        self.client.force_authenticate(user=None)
        response = self.client.get("/api/v1/finance/currencies/")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class CurrencyLedgerAPITestCase(FinanceBaseAPITestCase):
    def test_list_currency_ledgers_success(self):
        CurrencyLedger.objects.create(
            currency=self.currency, value=12500, day=datetime.date(2026, 9, 1)
        )
        response = self.client.get("/api/v1/finance/currency-ledgers/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 1)
        self.assertEqual(
            response.data["results"][0]["currency_info"]["short_name"], "USD"
        )

    def test_filter_currency_ledgers_by_short_name_success(self):
        eur = Currency.objects.create(name="EVRO", short_name="EUR")
        day = datetime.date(2026, 9, 1)
        CurrencyLedger.objects.create(currency=self.currency, value=12500, day=day)
        CurrencyLedger.objects.create(currency=eur, value=13500, day=day)
        response = self.client.get(
            "/api/v1/finance/currency-ledgers/", {"short_name": "eur"}
        )
        self.assertEqual(response.data["count"], 1)

    def test_create_currency_ledger_manually_not_allowed(self):
        response = self.client.post(
            "/api/v1/finance/currency-ledgers/",
            {"currency": str(self.currency.id), "value": "1", "day": "2026-09-02"},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_list_currency_ledgers_unauthenticated(self):
        self.client.force_authenticate(user=None)
        response = self.client.get("/api/v1/finance/currency-ledgers/")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class CurrencyLedgerSyncAPITestCase(FinanceBaseAPITestCase):
    url = "/api/v1/finance/currency-ledgers/sync/"

    def test_sync_creates_ledger_only_for_existing_currencies_success(self):
        response = self.client.post(self.url, {"day": "2026-09-01"}, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 1)
        ledger = CurrencyLedger.objects.get(currency=self.currency)
        self.assertEqual(ledger.value, Decimal("12500.50"))

    def test_sync_skips_deleted_currency_success(self):
        self.currency.delete()
        response = self.client.post(self.url, {"day": "2026-09-01"}, format="json")
        self.assertEqual(response.data["count"], 0)
        self.assertEqual(CurrencyLedger.objects.count(), 0)

    def test_sync_divides_rate_by_nominal_success(self):
        vnd = Currency.objects.create(name="Vetnam dongi", short_name="VND")
        self.client.post(self.url, {"day": "2026-09-01"}, format="json")
        self.assertEqual(
            CurrencyLedger.objects.get(currency=vnd).value, Decimal("85.00")
        )

    def test_sync_without_day_uses_today_success(self):
        response = self.client.post(self.url, {}, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(CurrencyLedger.objects.get().day, timezone.localdate())

    def test_sync_twice_updates_same_ledger_success(self):
        self.client.post(self.url, {"day": "2026-09-01"}, format="json")
        self.bank.return_value = [{**BANK_ROWS[0], "Rate": "12600.00"}]
        self.client.post(self.url, {"day": "2026-09-01"}, format="json")
        self.assertEqual(CurrencyLedger.objects.count(), 1)
        self.assertEqual(CurrencyLedger.objects.get().value, Decimal("12600.00"))

    def test_sync_future_day_invalid_data(self):
        response = self.client.post(self.url, {"day": "2999-01-01"}, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_sync_no_bank_data_invalid_data(self):
        self.bank.return_value = []
        response = self.client.post(self.url, {"day": "2026-09-01"}, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_sync_bank_unavailable_error(self):
        self.bank.side_effect = BankUnavailable()
        response = self.client.post(self.url, {"day": "2026-09-01"}, format="json")
        self.assertEqual(response.status_code, status.HTTP_503_SERVICE_UNAVAILABLE)

    def test_sync_unauthenticated(self):
        self.client.force_authenticate(user=None)
        response = self.client.post(self.url, {}, format="json")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_command_saves_today_rates_success(self):
        out = StringIO()
        call_command("sync_currency_rates", stdout=out)
        self.assertEqual(CurrencyLedger.objects.count(), 1)
        self.assertIn("1 ta valyuta", out.getvalue())

    def test_command_bank_unavailable_error(self):
        self.bank.side_effect = BankUnavailable()
        with self.assertRaises(CommandError):
            call_command("sync_currency_rates")


class AccrualRetentionAPITestCase(FinanceBaseAPITestCase):
    def test_list_accrual_retentions_success(self):
        AccrualRetention.objects.create(
            name="Soliq",
            type=AccrualRetention.Type.PERCENT,
            currency=self.currency,
            value=12,
        )
        response = self.client.get("/api/v1/finance/accrual-retentions/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 1)

    def test_create_accrual_retention_success(self):
        response = self.client.post(
            "/api/v1/finance/accrual-retentions/",
            {
                "name": "Bonus",
                "type": "fix_summa",
                "currency": str(self.currency.id),
                "value": "500000.00",
            },
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_accrual_retention_percent_over_100_invalid_data(self):
        response = self.client.post(
            "/api/v1/finance/accrual-retentions/",
            {
                "name": "Xato foiz",
                "type": "percent",
                "currency": str(self.currency.id),
                "value": "150.00",
            },
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_list_accrual_retentions_unauthenticated(self):
        self.client.force_authenticate(user=None)
        response = self.client.get("/api/v1/finance/accrual-retentions/")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class CounterpartyAPITestCase(FinanceBaseAPITestCase):
    def setUp(self):
        super().setUp()
        self.type = CounterpartyType.objects.create(name="Yetkazib beruvchi")

    def test_list_counterparties_success(self):
        Counterparty.objects.create(name="Urgut fabrika", type=self.type)
        response = self.client.get("/api/v1/finance/counterparties/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 1)
        self.assertEqual(
            response.data["results"][0]["type_info"]["name"], "Yetkazib beruvchi"
        )

    def test_create_counterparty_success(self):
        response = self.client.post(
            "/api/v1/finance/counterparties/",
            {
                "name": "Eron optom",
                "phone_number": "+998901234567",
                "type": str(self.type.id),
            },
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_counterparty_invalid_data(self):
        response = self.client.post(
            "/api/v1/finance/counterparties/", {}, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_list_counterparties_unauthenticated(self):
        self.client.force_authenticate(user=None)
        response = self.client.get("/api/v1/finance/counterparties/")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
