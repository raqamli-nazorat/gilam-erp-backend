import datetime

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

    def test_create_currency_invalid_data(self):
        response = self.client.post("/api/v1/finance/currencies/", {}, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

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

    def test_create_currency_ledger_success(self):
        response = self.client.post(
            "/api/v1/finance/currency-ledgers/",
            {
                "currency": str(self.currency.id),
                "value": "12650.00",
                "day": "2026-09-02",
            },
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_currency_ledger_invalid_data(self):
        response = self.client.post(
            "/api/v1/finance/currency-ledgers/",
            {"currency": str(self.currency.id), "value": "-1", "day": "2026-09-02"},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_list_currency_ledgers_unauthenticated(self):
        self.client.force_authenticate(user=None)
        response = self.client.get("/api/v1/finance/currency-ledgers/")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


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
