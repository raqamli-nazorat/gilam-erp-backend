from django.db import models

from apps.base.models import BaseModel


class Role(BaseModel):
    """Foydalanuvchi roli."""

    name = models.CharField(max_length=255, verbose_name="Nomi")

    class Meta:
        db_table = "accounts_role"
        verbose_name = "Rol"
        verbose_name_plural = "Rollar"

    def __str__(self):
        """Rol nomini qaytaradi."""
        return self.name
