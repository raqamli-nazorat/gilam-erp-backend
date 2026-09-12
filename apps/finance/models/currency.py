from django.db import models

from apps.base.models import BaseModel


class Currency(BaseModel):

    name = models.CharField(max_length=255, verbose_name="Nomi")
    short_name = models.CharField(max_length=255, verbose_name="Qisqa nomi")

    class Meta:
        db_table = "finance_currency"
        verbose_name = "Valyuta"
        verbose_name_plural = "Valyutalar"

    def __str__(self):
        return self.short_name


class CurrencyLedger(BaseModel):

    currency = models.ForeignKey(
        Currency,
        on_delete=models.PROTECT,
        related_name="ledgers",
        db_index=True,
        verbose_name="Valyuta",
    )
    value = models.DecimalField(
        max_digits=15, decimal_places=2, default=0, verbose_name="Qiymati"
    )
    day = models.DateField(verbose_name="Sana")

    class Meta:
        db_table = "finance_currency_ledger"
        verbose_name = "Valyuta kursi"
        verbose_name_plural = "Valyuta kurslari"

    def __str__(self):
        return f"{self.currency} — {self.day}: {self.value}"
