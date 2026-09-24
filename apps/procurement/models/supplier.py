from django.db import models

from apps.base.models import BaseModel


class Supplier(BaseModel):
    """Ta'minotchi (zavod yoki diler)."""

    organization = models.ForeignKey(
        "organization.Organization",
        on_delete=models.PROTECT,
        related_name="suppliers",
        db_index=True,
        verbose_name="Tashkilot",
    )
    name = models.CharField(max_length=255, verbose_name="Nomi")
    phone = models.CharField(
        max_length=50, blank=True, default="", verbose_name="Telefon"
    )
    address = models.TextField(blank=True, default="", verbose_name="Manzil")
    balance_debt = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        default=0,
        verbose_name="Bizning yetkazuvchidan qarzimiz",
    )

    class Meta:
        db_table = "procurement_supplier"
        verbose_name = "Yetkazuvchi"
        verbose_name_plural = "Yetkazuvchilar"

    def __str__(self):
        return self.name
