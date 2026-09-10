from django.db import models

from apps.base.models import BaseModel

from .currency import Currency


class AccrualRetention(BaseModel):
    """Hisoblash va ushlab qolish — oylik hisob-kitobda qo'llaniladi.

    Boshqa valyuta tanlansa, hisob-kitobda qiymat joriy kurs bo'yicha UZS ga
    aylantiriladi (oylik UZS dan hisoblanadi).
    """

    class Type(models.TextChoices):
        PERCENT = "percent", "Foiz"
        FIX_SUMMA = "fix_summa", "Belgilangan summa"

    name = models.CharField(max_length=255, verbose_name="Nomi")
    type = models.CharField(
        max_length=20,
        choices=Type.choices,
        db_index=True,
        verbose_name="Turi",
    )
    currency = models.ForeignKey(
        Currency,
        on_delete=models.PROTECT,
        related_name="accrual_retentions",
        db_index=True,
        verbose_name="Valyuta",
    )
    value = models.DecimalField(
        max_digits=15, decimal_places=2, default=0, verbose_name="Qiymati"
    )

    class Meta:
        db_table = "finance_accrual_retention"
        verbose_name = "Hisoblash / ushlab qolish"
        verbose_name_plural = "Hisoblash / ushlab qolishlar"

    def __str__(self):
        """Nomini qaytaradi."""
        return self.name
