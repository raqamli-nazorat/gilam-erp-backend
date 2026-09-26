from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models

from apps.base.models import BaseModel

from .district import District
from .organization import Organization
from .region import Region


class Branch(BaseModel):
    organization = models.ForeignKey(
        Organization,
        on_delete=models.PROTECT,
        related_name="branches",
        db_index=True,
        verbose_name="Tashkilot",
    )
    name = models.CharField(max_length=255, verbose_name="Nomi")
    phone = models.CharField(
        max_length=50, blank=True, default="", verbose_name="Telefon"
    )
    region = models.ForeignKey(
        Region,
        on_delete=models.PROTECT,
        related_name="branches",
        db_index=True,
        verbose_name="Viloyat",
    )
    district = models.ForeignKey(
        District,
        on_delete=models.PROTECT,
        related_name="branches",
        db_index=True,
        verbose_name="Tuman",
    )
    address = models.TextField(blank=True, default="", verbose_name="Manzil")
    is_closed = models.BooleanField(
        default=False,
        db_index=True,
        verbose_name="Yopilgan",
        help_text="Filial yopilganligi holati",
    )
    closing_reason = models.TextField(
        blank=True,
        default="",
        verbose_name="Yopilish sababi",
    )
    latitude = models.DecimalField(
        max_digits=10,
        decimal_places=7,
        null=True,
        blank=True,
        verbose_name="Kenglik (Latitude)",
    )
    longitude = models.DecimalField(
        max_digits=10,
        decimal_places=7,
        null=True,
        blank=True,
        verbose_name="Uzunlik (Longitude)",
    )
    radius = models.PositiveIntegerField(
        default=50,
        validators=[MinValueValidator(50), MaxValueValidator(500)],
        verbose_name="Radius (metr)",
    )

    class Meta:
        db_table = "organization_branch"
        verbose_name = "Filial"
        verbose_name_plural = "Filiallar"
        permissions = [
            ("close_branch", "Filialni yopish"),
            ("open_branch", "Filialni ochish"),
        ]

    def __str__(self):
        return self.name
