from django.db import models

from apps.base.models import BaseModel

from .supplier_purchase import SupplierPurchase


class SupplierPurchaseItem(BaseModel):
    """Xarid hujjatining qatori (bitta mahsulot partiyasi bo'yicha kirim)."""

    purchase = models.ForeignKey(
        SupplierPurchase,
        on_delete=models.CASCADE,
        related_name="items",
        db_index=True,
        verbose_name="Xarid hujjati",
    )
    product_party = models.ForeignKey(
        "catalog.ProductParty",
        on_delete=models.PROTECT,
        related_name="supplier_purchase_items",
        db_index=True,
        verbose_name="Mahsulot partiyasi",
    )
    roll_number = models.CharField(
        max_length=100,
        blank=True,
        default="",
        verbose_name="Rulon raqami",
        help_text="Kirim qilingan yo'lak (runner) bo'lsa, rulonning unikal raqami",
    )
    width = models.DecimalField(
        max_digits=8, decimal_places=2, verbose_name="Eni, metr"
    )
    length = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name="Bo'yi, metr",
        help_text="Yo'lak (runner) uchun bo'sh bo'lishi mumkin (faqat eni kelganda)",
    )
    quantity = models.PositiveIntegerField(
        default=1, verbose_name="Soni (dona gilam uchun)"
    )
    total_length_meters = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name="Rulon uzunligi, metr (yo'lak uchun)",
    )
    price_per_sqm = models.DecimalField(
        max_digits=15, decimal_places=2, verbose_name="Sotib olingan narx, 1 kv.m"
    )
    subtotal = models.DecimalField(
        max_digits=15, decimal_places=2, verbose_name="Qator summasi"
    )

    class Meta:
        db_table = "procurement_supplier_purchase_item"
        verbose_name = "Xarid qatori"
        verbose_name_plural = "Xarid qatorlari"

    def __str__(self):
        return f"{self.purchase} — {self.product_party}"
