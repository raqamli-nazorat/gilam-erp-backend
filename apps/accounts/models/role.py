from django.db import models

from apps.base.models import BaseModel


class Role(BaseModel):

    name = models.CharField(max_length=255, verbose_name="Nomi")
    organization = models.ForeignKey(
        "organization.Organization",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="roles",
        db_index=True,
        verbose_name="Tashkilot",
        help_text="NULL bo'lsa tizim darajasidagi rol (masalan: Super Admin)",
    )
    is_system = models.BooleanField(
        default=False,
        verbose_name="Tizim roli",
        help_text="O'chirib bo'lmaydigan asosiy rol (masalan, dastlabki Admin roli)",
    )
    permissions = models.ManyToManyField(
        "auth.Permission",
        blank=True,
        related_name="custom_roles",
        verbose_name="Huquqlar",
    )
    branches = models.ManyToManyField(
        "organization.Branch",
        blank=True,
        related_name="roles",
        verbose_name="Filiallar",
        help_text="Ushbu rol amal qiladigan filiallar (bo'sh bo'lsa butun tashkilot bo'yicha)",
    )

    class Meta:
        db_table = "accounts_role"
        verbose_name = "Rol"
        verbose_name_plural = "Rollar"

    def __str__(self):
        return self.name
