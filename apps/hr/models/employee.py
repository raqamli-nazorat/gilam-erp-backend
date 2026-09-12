from django.db import models

from apps.base.models import BaseModel


class Employee(BaseModel):

    branch = models.ForeignKey(
        "organization.Branch",
        on_delete=models.PROTECT,
        related_name="employees",
        db_index=True,
        verbose_name="Filial",
    )
    full_name = models.CharField(max_length=255, verbose_name="F.I.Sh.")
    region = models.ForeignKey(
        "organization.Region",
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="employees",
        verbose_name="Viloyat",
    )
    district = models.ForeignKey(
        "organization.District",
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="employees",
        verbose_name="Tuman",
    )
    address = models.CharField(
        max_length=255, blank=True, default="", verbose_name="Manzil"
    )
    passport_seria = models.CharField(
        max_length=255, blank=True, default="", verbose_name="Passport seriyasi"
    )
    passport_number = models.CharField(
        max_length=255, blank=True, default="", verbose_name="Passport raqami"
    )
    jsshr = models.CharField(
        max_length=255, blank=True, default="", verbose_name="JSHSHIR"
    )
    stir = models.CharField(max_length=255, blank=True, default="", verbose_name="STIR")
    phone_number = models.CharField(
        max_length=255, blank=True, default="", verbose_name="Telefon raqami"
    )
    description = models.TextField(blank=True, default="", verbose_name="Tavsifi")

    class Meta:
        db_table = "hr_employee"
        verbose_name = "Xodim"
        verbose_name_plural = "Xodimlar"

    def __str__(self):
        return self.full_name
