from django.db import models

from apps.base.models import BaseModel


class Country(BaseModel):

    name = models.CharField(max_length=255, verbose_name="Nomi")

    class Meta:
        db_table = "organization_country"
        verbose_name = "Davlat"
        verbose_name_plural = "Davlatlar"

    def __str__(self):
        return self.name
