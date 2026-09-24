from django.db import models

from apps.base.models import BaseModel

from .warehouse import Warehouse


class ProductStock(BaseModel):
    """Ombordagi mahsulot qoldig'i (dona va/yoki metr bo'yicha)."""

    warehouse = models.ForeignKey(
        Warehouse,
        on_delete=models.PROTECT,
        related_name="product_stocks",
        db_index=True,
        verbose_name="Ombor",
    )
    product_party = models.ForeignKey(
        "catalog.ProductParty",
        on_delete=models.PROTECT,
        related_name="product_stocks",
        db_index=True,
        verbose_name="Mahsulot partiyasi",
    )
    quantity = models.PositiveIntegerField(
        default=0, verbose_name="Soni (dona gilamlar uchun)"
    )
    total_length_meters = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        verbose_name="Jami uzunligi, metr (yo'laklar uchun)",
    )

    class Meta:
        db_table = "warehouse_product_stock"
        verbose_name = "Ombor qoldig'i"
        verbose_name_plural = "Ombor qoldiqlari"
        constraints = [
            models.UniqueConstraint(
                fields=["warehouse", "product_party"],
                name="unique_warehouse_product_party_stock",
            )
        ]

    def __str__(self):
        return f"{self.warehouse} — {self.product_party}"
