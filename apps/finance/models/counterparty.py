from django.db import models

from apps.base.models import BaseModel


class CounterpartyType(BaseModel):

    name = models.CharField(max_length=255, verbose_name="Nomi")

    class Meta:
        db_table = "finance_counterparty_type"
        verbose_name = "Kontragent turi"
        verbose_name_plural = "Kontragent turlari"

    def __str__(self):
        return self.name


class Counterparty(BaseModel):

    name = models.CharField(max_length=255, verbose_name="Nomi")
    phone_number = models.CharField(
        max_length=50, blank=True, default="", verbose_name="Telefon raqami"
    )
    type = models.ForeignKey(
        CounterpartyType,
        on_delete=models.PROTECT,
        related_name="counterparties",
        db_index=True,
        verbose_name="Turi",
    )

    class Meta:
        db_table = "finance_counterparty"
        verbose_name = "Kontragent"
        verbose_name_plural = "Kontragentlar"

    def __str__(self):
        return self.name
