from django.db import models

from apps.base.models import BaseModel


class Customer(BaseModel):
    """Mijoz."""

    organization = models.ForeignKey(
        "organization.Organization",
        on_delete=models.PROTECT,
        related_name="customers",
        db_index=True,
        verbose_name="Tashkilot",
    )
    full_name = models.CharField(max_length=255, verbose_name="F.I.Sh.")
    phone = models.CharField(max_length=50, verbose_name="Telefon")
    address = models.TextField(blank=True, default="", verbose_name="Manzil")
    balance_debt = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        default=0,
        verbose_name="Nasiya balansi",
    )
    loyalty_discount_pct = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=0,
        verbose_name="Doimiy chegirma foizi",
    )

    class Meta:
        db_table = "sales_customer"
        verbose_name = "Mijoz"
        verbose_name_plural = "Mijozlar"
        indexes = [
            models.Index(fields=["organization", "phone"]),
        ]

    def __str__(self):
        return self.full_name
