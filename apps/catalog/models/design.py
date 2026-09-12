from django.db import models

from apps.base.models import BaseModel

from .quality import Quality


class Design(BaseModel):

    quality = models.ForeignKey(
        Quality,
        on_delete=models.PROTECT,
        related_name="designs",
        db_index=True,
        verbose_name="Sifat",
    )
    name = models.CharField(max_length=100, verbose_name="Nomi")
    description = models.TextField(blank=True, default="", verbose_name="Tavsifi")

    class Meta:
        db_table = "catalog_design"
        verbose_name = "Dizayn"
        verbose_name_plural = "Dizaynlar"

    def __str__(self):
        return self.name


class DesignPhoto(BaseModel):

    design = models.ForeignKey(
        Design,
        on_delete=models.CASCADE,
        related_name="photos",
        db_index=True,
        verbose_name="Dizayn",
    )
    photo_path = models.CharField(max_length=255, verbose_name="Fayl yo'li")
    name = models.CharField(max_length=100, verbose_name="Nomi")
    description = models.TextField(blank=True, default="", verbose_name="Tavsifi")

    class Meta:
        db_table = "catalog_design_photo"
        verbose_name = "Dizayn fotosurati"
        verbose_name_plural = "Dizayn fotosuratlari"

    def __str__(self):
        return self.name
