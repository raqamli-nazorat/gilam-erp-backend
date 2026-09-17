from django.db import models

from apps.base.models import BaseModel


class UserBlockLog(BaseModel):
    class Type(models.TextChoices):
        BLOCK = "block", "Bloklash"
        UNBLOCK = "unblock", "Blokdan chiqarish"

    user = models.ForeignKey(
        "accounts.User",
        on_delete=models.CASCADE,
        related_name="block_logs",
        db_index=True,
        verbose_name="Foydalanuvchi",
    )
    type = models.CharField(
        max_length=10,
        choices=Type.choices,
        db_index=True,
        verbose_name="Turi",
    )
    reason = models.TextField(blank=True, default="", verbose_name="Sababi")
    actor = models.ForeignKey(
        "accounts.User",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="performed_block_logs",
        verbose_name="Bajaruvchi",
    )

    class Meta:
        db_table = "accounts_user_block_log"
        verbose_name = "Bloklash yozuvi"
        verbose_name_plural = "Bloklash yozuvlari"

    def __str__(self):
        return f"{self.user} — {self.get_type_display()}"
