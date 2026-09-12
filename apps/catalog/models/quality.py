from django.db import models

from apps.base.models import BaseModel


class Quality(BaseModel):

    name = models.CharField(max_length=100, verbose_name="Nomi")
    description = models.TextField(blank=True, default="", verbose_name="Tavsifi")

    class Meta:
        db_table = "catalog_quality"
        verbose_name = "Sifat"
        verbose_name_plural = "Sifatlar"

    def __str__(self):
        return self.name
