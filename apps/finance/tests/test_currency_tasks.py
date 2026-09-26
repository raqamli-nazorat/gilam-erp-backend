from unittest.mock import patch

from django.conf import settings
from django.test import TestCase

from apps.finance.models import Currency, CurrencyLedger
from apps.finance.services.currency import BankUnavailable
from apps.finance.tasks import sync_currency_rates
from config.celery import app

TASK_NAME = "apps.finance.tasks.sync_currency_rates"
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
    }
]


class SyncCurrencyRatesTaskTestCase(TestCase):
    def setUp(self):
        Currency.objects.create(name="AQSh dollari", short_name="USD")

    @patch("apps.finance.services.currency.fetch_bank_rates", return_value=BANK_ROWS)
    def test_task_saves_today_rates_success(self, _bank):
        result = sync_currency_rates.apply()
        self.assertTrue(result.successful())
        self.assertEqual(result.get(), 1)
        self.assertEqual(CurrencyLedger.objects.count(), 1)

    @patch(
        "apps.finance.services.currency.fetch_bank_rates",
        side_effect=BankUnavailable(),
    )
    def test_task_bank_unavailable_fails_after_retries(self, _bank):
        result = sync_currency_rates.apply()
        self.assertTrue(result.failed())
        self.assertEqual(CurrencyLedger.objects.count(), 0)

    def test_beat_schedule_runs_registered_task_daily_success(self):
        app.loader.import_default_modules()
        entry = settings.CELERY_BEAT_SCHEDULE["sync-currency-rates-daily"]
        self.assertEqual(entry["task"], TASK_NAME)
        self.assertIn(TASK_NAME, app.tasks)
