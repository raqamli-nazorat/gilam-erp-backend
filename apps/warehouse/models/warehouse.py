from django.db import models

from apps.base.models import BaseModel


class Warehouse(BaseModel):
    """Ombor — filialga tegishli (masalan: Asosiy ombor, Vitrina/Shourum)."""

    branch = models.ForeignKey(
        "organization.Branch",
        on_delete=models.PROTECT,
        related_name="warehouses",
        db_index=True,
        verbose_name="Filial",
    )
    name = models.CharField(max_length=255, verbose_name="Nomi")
    address = models.TextField(blank=True, default="", verbose_name="Manzil")

    class Meta:
        db_table = "warehouse_warehouse"
        verbose_name = "Ombor"
        verbose_name_plural = "Omborlar"

    def __str__(self):
        """Ombor nomini qaytaradi."""
        return self.name
