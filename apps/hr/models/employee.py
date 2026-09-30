from django.db import connection, models, transaction
from django.db.models import Max

from apps.base.models import BaseModel

# Xodim tabel raqamini berishda ishlatiladigan PostgreSQL advisory lock kaliti
EMPLOYEE_TAB_NUMBER_LOCK = 7302


class Employee(BaseModel):
    organization = models.ForeignKey(
        "organization.Organization",
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="employees",
        db_index=True,
        verbose_name="Tashkilot",
    )
    branch = models.ForeignKey(
        "organization.Branch",
        on_delete=models.PROTECT,
        null=True,
        blank=True,
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
    personnel_tab_number = models.PositiveIntegerField(
        unique=True, editable=False, verbose_name="Tabel raqami"
    )

    def save(self, *args, **kwargs):
        """Yangi xodimga avtomatik ketma-ket tabel raqami beradi."""
        if self._state.adding and self.personnel_tab_number is None:
            with transaction.atomic():
                # Bir vaqtda yaratishda bir xil raqam chiqmasligi uchun qulflanadi
                with connection.cursor() as cursor:
                    cursor.execute(
                        "SELECT pg_advisory_xact_lock(%s)", [EMPLOYEE_TAB_NUMBER_LOCK]
                    )
                last = Employee.objects.aggregate(last=Max("personnel_tab_number"))[
                    "last"
                ]
                self.personnel_tab_number = (last or 0) + 1
                return super().save(*args, **kwargs)
        return super().save(*args, **kwargs)

    class Meta:
        db_table = "hr_employee"
        verbose_name = "Xodim"
        verbose_name_plural = "Xodimlar"

    def __str__(self):
        return self.full_name
