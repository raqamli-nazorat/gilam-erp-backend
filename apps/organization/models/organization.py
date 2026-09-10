from django.db import models

from apps.base.models import BaseModel

from .district import District
from .region import Region


class Organization(BaseModel):
    """Tashkilot — yuridik shaxs."""

    name = models.CharField(max_length=255, verbose_name="Nomi")
    inn = models.CharField(max_length=20, unique=True, verbose_name="INN")
    phone = models.CharField(
        max_length=50, blank=True, default="", verbose_name="Telefon"
    )
    director = models.CharField(
        max_length=50, blank=True, default="", verbose_name="Rahbar"
    )
    region = models.ForeignKey(
        Region,
        on_delete=models.PROTECT,
        related_name="organizations",
        db_index=True,
        verbose_name="Viloyat",
    )
    district = models.ForeignKey(
        District,
        on_delete=models.PROTECT,
        related_name="organizations",
        db_index=True,
        verbose_name="Tuman",
    )
    address = models.TextField(blank=True, default="", verbose_name="Manzil")
    prefix = models.CharField(
        max_length=255, blank=True, default="", verbose_name="Prefiks"
    )

    class Meta:
        db_table = "organization_organization"
        verbose_name = "Tashkilot"
        verbose_name_plural = "Tashkilotlar"

    def __str__(self):
        """Tashkilot nomini qaytaradi."""
        return self.name
