from django.db import models

from apps.base.models import BaseModel


class Unit(BaseModel):

    name = models.CharField(max_length=100, verbose_name="Nomi")
    description = models.TextField(blank=True, default="", verbose_name="Tavsifi")

    class Meta:
        db_table = "catalog_unit"
        verbose_name = "O'lchov birligi"
        verbose_name_plural = "O'lchov birliklari"

    def __str__(self):
        return self.name
