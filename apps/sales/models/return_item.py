from django.db import models

from apps.base.models import BaseModel

from .order_item import OrderItem
from .return_order import ReturnOrder


class ReturnItem(BaseModel):
    """Qaytarish hujjatining qatori."""

    class RestockStatus(models.TextChoices):
        RESTOCKED = "restocked", "Omborga qaytarildi"
        DAMAGED_SCRAP = "damaged_scrap", "Brak (hisobdan o'chirildi)"

    return_order = models.ForeignKey(
        ReturnOrder,
        on_delete=models.CASCADE,
        related_name="items",
        db_index=True,
        verbose_name="Qaytarish hujjati",
    )
    order_item = models.ForeignKey(
        OrderItem,
        on_delete=models.PROTECT,
        related_name="return_items",
        db_index=True,
        verbose_name="Sotilgan chek qatori",
    )
    quantity = models.PositiveIntegerField(
        default=1, verbose_name="Soni (dona gilamlar uchun)"
    )
    length_meters = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        verbose_name="Qaytarilgan uzunligi, metr (yo'laklar uchun)",
    )
    restock_status = models.CharField(
        max_length=20,
        choices=RestockStatus.choices,
        db_index=True,
        verbose_name="Holati",
    )

    class Meta:
        db_table = "sales_return_item"
        verbose_name = "Qaytarish qatori"
        verbose_name_plural = "Qaytarish qatorlari"

    def __str__(self):
        return f"{self.return_order} — {self.order_item}"
