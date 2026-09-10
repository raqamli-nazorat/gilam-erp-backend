from django.db import models

from apps.base.models import BaseModel

from .region import Region


class District(BaseModel):
    """Tuman — viloyatga bog'liq."""

    region = models.ForeignKey(
        Region,
        on_delete=models.PROTECT,
        related_name="districts",
        db_index=True,
        verbose_name="Viloyat",
    )
    name = models.CharField(max_length=255, verbose_name="Nomi")

    class Meta:
        db_table = "organization_district"
        verbose_name = "Tuman"
        verbose_name_plural = "Tumanlar"

    def __str__(self):
        """Tuman nomini qaytaradi."""
        return self.name
