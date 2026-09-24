from django.db import models

from apps.base.models import BaseModel

from .customer import Customer
from .order import Order


class ReturnOrder(BaseModel):
    """Tovar qaytarib olish (vozvrat) jurnali."""

    organization = models.ForeignKey(
        "organization.Organization",
        on_delete=models.PROTECT,
        related_name="return_orders",
        db_index=True,
        verbose_name="Tashkilot",
    )
    branch = models.ForeignKey(
        "organization.Branch",
        on_delete=models.PROTECT,
        related_name="return_orders",
        db_index=True,
        verbose_name="Filial",
    )
    order = models.ForeignKey(
        Order,
        on_delete=models.PROTECT,
        related_name="return_orders",
        db_index=True,
        verbose_name="Sotuv cheki",
        help_text="Qaysi sotuv cheki bo'yicha qaytarildi",
    )
    customer = models.ForeignKey(
        Customer,
        on_delete=models.PROTECT,
        related_name="return_orders",
        null=True,
        blank=True,
        db_index=True,
        verbose_name="Mijoz",
    )
    refund_amount = models.DecimalField(
        max_digits=15, decimal_places=2, verbose_name="Mijozga qaytarilgan summa"
    )
    reason = models.TextField(blank=True, default="", verbose_name="Sababi")

    class Meta:
        db_table = "sales_return_order"
        verbose_name = "Qaytarish hujjati"
        verbose_name_plural = "Qaytarish hujjatlari"

    def __str__(self):
        return f"{self.order} — {self.refund_amount}"
