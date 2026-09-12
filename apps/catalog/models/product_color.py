from django.db import models

from apps.base.models import BaseModel


class ProductColor(BaseModel):

    name = models.CharField(max_length=100, verbose_name="Nomi")
    description = models.TextField(blank=True, default="", verbose_name="Tavsifi")
    color_hex = models.CharField(
        max_length=7, blank=True, default="", verbose_name="HEX rang (#RRGGBB)"
    )

    class Meta:
        db_table = "catalog_product_color"
        verbose_name = "Rang"
        verbose_name_plural = "Ranglar"

    def __str__(self):
        return self.name
