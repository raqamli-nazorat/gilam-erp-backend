from django.db import models

from apps.base.models import BaseModel

from .order import Order


class OrderItem(BaseModel):
    """Sotuv chekining qatori (gilam sotuvining o'lcham tafsilotlari bilan)."""

    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name="items",
        db_index=True,
        verbose_name="Chek",
    )
    product_party = models.ForeignKey(
        "catalog.ProductParty",
        on_delete=models.PROTECT,
        related_name="order_items",
        db_index=True,
        verbose_name="Mahsulot partiyasi",
    )
    roll = models.ForeignKey(
        "warehouse.CarpetRoll",
        on_delete=models.PROTECT,
        related_name="order_items",
        null=True,
        blank=True,
        db_index=True,
        verbose_name="Rulon",
        help_text="Kesilgan yo'lak bo'lsa, qaysi jismoniy rulondan kesildi",
    )
    warehouse = models.ForeignKey(
        "warehouse.Warehouse",
        on_delete=models.PROTECT,
        related_name="order_items",
        db_index=True,
        verbose_name="Ombor",
        help_text="Qaysi ombordan mahsulot kamaydi",
    )
    width = models.DecimalField(
        max_digits=8, decimal_places=2, verbose_name="Sotilgan eni, metr"
    )
    length = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        verbose_name="Sotilgan bo'yi, metr",
        help_text="Yo'lak bo'lsa kesib berilgan uzunlik",
    )
    sqm = models.DecimalField(
        max_digits=10, decimal_places=2, verbose_name="Kvadrat metr"
    )
    price_per_sqm = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        verbose_name="Sotilgan paytdagi 1 kv.m narxi",
    )
    item_subtotal = models.DecimalField(
        max_digits=15, decimal_places=2, verbose_name="Qator summasi"
    )
    overlock_length_meters = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        default=0,
        verbose_name="Tikilgan chet uzunligi, metr",
    )
    overlock_price_per_meter = models.DecimalField(
        max_digits=15, decimal_places=2, default=0, verbose_name="Ovirlok, 1 metr narxi"
    )
    overlock_cost = models.DecimalField(
        max_digits=15, decimal_places=2, default=0, verbose_name="Jami ovirlok narxi"
    )
    quantity = models.PositiveIntegerField(
        default=1, verbose_name="Soni (tayyor o'lchamli dona gilamlar uchun)"
    )
    final_item_price = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        verbose_name="Yakuniy qator narxi",
        help_text="(item_subtotal + overlock_cost) * quantity",
    )

    class Meta:
        db_table = "sales_order_item"
        verbose_name = "Chek qatori"
        verbose_name_plural = "Chek qatorlari"

    def __str__(self):
        return f"{self.order} — {self.product_party}"
