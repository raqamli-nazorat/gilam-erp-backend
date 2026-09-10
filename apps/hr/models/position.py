from django.db import models

from apps.base.models import BaseModel


class Position(BaseModel):
    """Xodim lavozimi."""

    name = models.CharField(max_length=100, verbose_name="Nomi")
    description = models.TextField(blank=True, default="", verbose_name="Tavsifi")

    class Meta:
        db_table = "hr_position"
        verbose_name = "Lavozim"
        verbose_name_plural = "Lavozimlar"

    def __str__(self):
        """Lavozim nomini qaytaradi."""
        return self.name
