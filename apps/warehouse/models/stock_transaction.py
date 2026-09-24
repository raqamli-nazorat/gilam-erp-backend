from django.db import models

from apps.base.models import BaseModel

from .carpet_roll import CarpetRoll
from .warehouse import Warehouse


class StockTransaction(BaseModel):
    """Ombor harakati auditi (kirim, chiqim, ko'chirish)."""

    class TransactionType(models.TextChoices):
        IN = "in", "Kirim"
        OUT = "out", "Chiqim"
        TRANSFER = "transfer", "Ko'chirish"

    class RefType(models.TextChoices):
        SALE = "sale", "Sotuv"
        RETURN = "return", "Qaytarish"
        PURCHASE = "purchase", "Xarid (kirim)"
        ADJUSTMENT = "adjustment", "Korrektirovka"
        TRANSFER = "transfer", "Ko'chirish"

    organization = models.ForeignKey(
        "organization.Organization",
        on_delete=models.PROTECT,
        related_name="stock_transactions",
        db_index=True,
        verbose_name="Tashkilot",
    )
    product_party = models.ForeignKey(
        "catalog.ProductParty",
        on_delete=models.PROTECT,
        related_name="stock_transactions",
        db_index=True,
        verbose_name="Mahsulot partiyasi",
    )
    roll = models.ForeignKey(
        CarpetRoll,
        on_delete=models.PROTECT,
        related_name="stock_transactions",
        null=True,
        blank=True,
        db_index=True,
        verbose_name="Rulon",
        help_text="Yo'lak (runner) bo'lsa, qaysi rulonda o'zgarish bo'ldi",
    )
    from_warehouse = models.ForeignKey(
        Warehouse,
        on_delete=models.PROTECT,
        related_name="stock_transactions_from",
        null=True,
        blank=True,
        verbose_name="Qaysi ombordan",
        help_text="Kirim bo'lsa bo'sh",
    )
    to_warehouse = models.ForeignKey(
        Warehouse,
        on_delete=models.PROTECT,
        related_name="stock_transactions_to",
        null=True,
        blank=True,
        verbose_name="Qaysi omborga",
        help_text="Chiqim bo'lsa bo'sh",
    )
    transaction_type = models.CharField(
        max_length=20,
        choices=TransactionType.choices,
        db_index=True,
        verbose_name="Harakat turi",
    )
    quantity = models.IntegerField(default=0, verbose_name="Soni (dona gilamlar uchun)")
    length_meters = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        verbose_name="Uzunligi, metr (yo'laklar uchun)",
    )
    ref_type = models.CharField(
        max_length=20,
        choices=RefType.choices,
        blank=True,
        default="",
        verbose_name="Bog'liq hujjat turi",
    )
    ref_id = models.UUIDField(
        null=True,
        blank=True,
        db_index=True,
        verbose_name="Bog'liq hujjat id'si",
        help_text="Masalan: Order.id, SupplierPurchase.id yoki ReturnOrder.id",
    )

    class Meta:
        db_table = "warehouse_stock_transaction"
        verbose_name = "Ombor harakati"
        verbose_name_plural = "Ombor harakatlari"
        indexes = [
            models.Index(fields=["ref_type", "ref_id"]),
        ]

    def __str__(self):
        return f"{self.get_transaction_type_display()} — {self.product_party}"
