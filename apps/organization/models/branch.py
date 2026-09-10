from django.db import models

from apps.base.models import BaseModel

from .district import District
from .organization import Organization
from .region import Region


class Branch(BaseModel):
    """Filial — tashkilotning savdo nuqtasi."""

    organization = models.ForeignKey(
        Organization,
        on_delete=models.PROTECT,
        related_name="branches",
        db_index=True,
        verbose_name="Tashkilot",
    )
    name = models.CharField(max_length=255, verbose_name="Nomi")
    phone = models.CharField(
        max_length=50, blank=True, default="", verbose_name="Telefon"
    )
    region = models.ForeignKey(
        Region,
        on_delete=models.PROTECT,
        related_name="branches",
        db_index=True,
        verbose_name="Viloyat",
    )
    district = models.ForeignKey(
        District,
        on_delete=models.PROTECT,
        related_name="branches",
        db_index=True,
        verbose_name="Tuman",
    )
    address = models.TextField(blank=True, default="", verbose_name="Manzil")

    class Meta:
        db_table = "organization_branch"
        verbose_name = "Filial"
        verbose_name_plural = "Filiallar"

    def __str__(self):
        """Filial nomini qaytaradi."""
        return self.name
