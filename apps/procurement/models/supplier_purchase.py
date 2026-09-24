from django.db import models

from apps.base.models import BaseModel

from .supplier import Supplier


class SupplierPurchase(BaseModel):
    """Ta'minotchidan omborga mahsulot kirimi (xarid hujjati)."""

    organization = models.ForeignKey(
        "organization.Organization",
        on_delete=models.PROTECT,
        related_name="supplier_purchases",
        db_index=True,
        verbose_name="Tashkilot",
    )
    supplier = models.ForeignKey(
        Supplier,
        on_delete=models.PROTECT,
        related_name="purchases",
        db_index=True,
        verbose_name="Yetkazuvchi",
    )
    warehouse = models.ForeignKey(
        "warehouse.Warehouse",
        on_delete=models.PROTECT,
        related_name="supplier_purchases",
        db_index=True,
        verbose_name="Ombor",
    )
    total_amount = models.DecimalField(
        max_digits=15, decimal_places=2, verbose_name="Jami summa"
    )
    paid_amount = models.DecimalField(
        max_digits=15, decimal_places=2, default=0, verbose_name="To'langan summa"
    )
    debt_amount = models.DecimalField(
        max_digits=15, decimal_places=2, default=0, verbose_name="Qarz summa"
    )

    class Meta:
        db_table = "procurement_supplier_purchase"
        verbose_name = "Xarid hujjati"
        verbose_name_plural = "Xarid hujjatlari"

    def __str__(self):
        return f"{self.supplier} — {self.total_amount}"
