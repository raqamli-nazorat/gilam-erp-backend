from django.db import models

from apps.base.models import BaseModel

from .country import Country


class Region(BaseModel):
    """Viloyat — davlatga bog'liq."""

    name = models.CharField(max_length=255, verbose_name="Nomi")
    country = models.ForeignKey(
        Country,
        on_delete=models.PROTECT,
        related_name="regions",
        db_index=True,
        verbose_name="Davlat",
    )

    class Meta:
        db_table = "organization_region"
        verbose_name = "Viloyat"
        verbose_name_plural = "Viloyatlar"

    def __str__(self):
        """Viloyat nomini qaytaradi."""
        return self.name
