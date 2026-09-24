from django.db import models

from apps.base.models import BaseModel

from .warehouse import Warehouse


class CarpetRoll(BaseModel):
    """Gilam yo'lagi (runner) rulonining alohida hisobi."""

    class Status(models.TextChoices):
        ACTIVE = "active", "Faol"
        SOLD_OUT = "sold_out", "Tugagan"
        DAMAGED = "damaged", "Brak"

    product_party = models.ForeignKey(
        "catalog.ProductParty",
        on_delete=models.PROTECT,
        related_name="carpet_rolls",
        db_index=True,
        verbose_name="Mahsulot partiyasi",
    )
    warehouse = models.ForeignKey(
        Warehouse,
        on_delete=models.PROTECT,
        related_name="carpet_rolls",
        db_index=True,
        verbose_name="Ombor",
    )
    roll_number = models.CharField(
        max_length=100, unique=True, verbose_name="Rulon raqami"
    )
    initial_length_meters = models.DecimalField(
        max_digits=8, decimal_places=2, verbose_name="Boshlang'ich uzunligi (metr)"
    )
    current_length_meters = models.DecimalField(
        max_digits=8, decimal_places=2, verbose_name="Hozirgi qolgan uzunligi (metr)"
    )
    is_offcut = models.BooleanField(
        default=False, verbose_name="Qiyqim (katta rulondan kesilgan qoldiq)"
    )
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.ACTIVE,
        db_index=True,
        verbose_name="Holati",
    )

    class Meta:
        db_table = "warehouse_carpet_roll"
        verbose_name = "Rulon"
        verbose_name_plural = "Rulonlar"
        indexes = [
            models.Index(fields=["warehouse", "product_party"]),
        ]

    def __str__(self):
        return self.roll_number
