from django.db import models

from apps.base.models import BaseModel

from .design import Design
from .product_color import ProductColor
from .quality import Quality
from .unit import Unit


class ProductParty(BaseModel):

    branch = models.ForeignKey(
        "organization.Branch",
        on_delete=models.PROTECT,
        related_name="product_parties",
        db_index=True,
        verbose_name="Filial",
    )
    party_number = models.CharField(
        max_length=100,
        blank=True,
        default="",
        verbose_name="Partiya raqami",
    )
    name = models.CharField(max_length=100, verbose_name="Nomi")
    quality = models.ForeignKey(
        Quality,
        on_delete=models.PROTECT,
        related_name="product_parties",
        db_index=True,
        verbose_name="Sifat",
    )
    design = models.ForeignKey(
        Design,
        on_delete=models.PROTECT,
        related_name="product_parties",
        db_index=True,
        verbose_name="Dizayn",
    )
    color = models.ForeignKey(
        ProductColor,
        on_delete=models.PROTECT,
        related_name="product_parties",
        db_index=True,
        verbose_name="Rang",
    )
    unit = models.ForeignKey(
        Unit,
        on_delete=models.PROTECT,
        related_name="product_parties",
        db_index=True,
        verbose_name="O'lchov birligi",
    )
    description = models.TextField(blank=True, default="", verbose_name="Tavsifi")

    barcode = models.CharField(
        max_length=100,
        unique=True,
        null=True,
        blank=True,
        verbose_name="Shtrix-kod",
    )
    is_runner = models.BooleanField(
        default=False, db_index=True, verbose_name="Yo'lak (runner)"
    )
    price_per_sqm_purchase = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        verbose_name="1 kv.m tannarx (kirish narxi)",
    )
    price_per_sqm_sale = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        verbose_name="1 kv.m sotuv narxi",
    )

    class Meta:
        db_table = "catalog_product_party"
        verbose_name = "Mahsulot partiyasi"
        verbose_name_plural = "Mahsulot partiyalari"

    def __str__(self):
        return f"{self.name} ({self.party_number})" if self.party_number else self.name
