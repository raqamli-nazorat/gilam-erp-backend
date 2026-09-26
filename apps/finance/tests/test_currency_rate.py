import datetime
from decimal import Decimal

from django.test import TestCase
from rest_framework.exceptions import ValidationError

from apps.finance.models import Currency, CurrencyLedger
from apps.finance.services.currency import get_rate


class GetRateTestCase(TestCase):
    def setUp(self):
        self.uzs = Currency.objects.create(name="So'm", short_name="UZS")
        self.usd = Currency.objects.create(name="Dollar", short_name="USD")

    def test_get_rate_uzs_returns_one(self):
        self.assertEqual(get_rate(self.uzs, datetime.date(2026, 1, 15)), Decimal(1))

    def test_get_rate_exact_day_success(self):
        CurrencyLedger.objects.create(
            currency=self.usd, day=datetime.date(2026, 1, 15), value=12500
        )
        self.assertEqual(
            get_rate(self.usd, datetime.date(2026, 1, 15)), Decimal("12500.00")
        )

    def test_get_rate_falls_back_to_previous_day(self):
        CurrencyLedger.objects.create(
            currency=self.usd, day=datetime.date(2026, 1, 14), value=12400
        )
        CurrencyLedger.objects.create(
            currency=self.usd, day=datetime.date(2026, 1, 10), value=12000
        )
        self.assertEqual(
            get_rate(self.usd, datetime.date(2026, 1, 17)), Decimal("12400.00")
        )

    def test_get_rate_ignores_future_rates(self):
        CurrencyLedger.objects.create(
            currency=self.usd, day=datetime.date(2026, 2, 1), value=13000
        )
        with self.assertRaises(ValidationError):
            get_rate(self.usd, datetime.date(2026, 1, 15))

    def test_get_rate_missing_raises(self):
        with self.assertRaises(ValidationError):
            get_rate(self.usd, datetime.date(2026, 1, 15))
