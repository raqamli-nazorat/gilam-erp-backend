from django.core.validators import FileExtensionValidator
from django.db import models

from apps.base.models import BaseModel
from apps.utils.validators import FileSizeValidator

from .employee import Employee
from .position import Position


class RecruitmentDismissal(BaseModel):
    class Type(models.TextChoices):
        RECRUITMENT = "recruitment", "Ishga olish"
        DISMISSAL = "dismissal", "Ishdan chiqarish"

    class SalaryType(models.TextChoices):
        FIXED_AMOUNT = "fixed_amount", "Belgilangan summa"
        SALES_PERCENT = "sales_percent", "Savdodan foiz"
        FOUNDER = "founder", "Asoschi"

    type = models.CharField(
        max_length=20,
        choices=Type.choices,
        db_index=True,
        verbose_name="Turi",
    )
    branch = models.ForeignKey(
        "organization.Branch",
        on_delete=models.PROTECT,
        related_name="recruitment_dismissals",
        db_index=True,
        verbose_name="Filial",
    )
    employee = models.ForeignKey(
        Employee,
        on_delete=models.PROTECT,
        related_name="recruitment_dismissals",
        db_index=True,
        verbose_name="Xodim",
    )
    position = models.ForeignKey(
        Position,
        on_delete=models.PROTECT,
        related_name="recruitment_dismissals",
        db_index=True,
        verbose_name="Lavozim",
    )
    card_number = models.CharField(max_length=255, verbose_name="Karta raqami")
    card_image = models.CharField(
        max_length=255, blank=True, default="", verbose_name="Karta rasmi"
    )
    salary_type = models.CharField(
        max_length=20,
        choices=SalaryType.choices,
        verbose_name="Oylik turi",
    )
    fix_summa = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name="Belgilangan summa",
    )
    fix_percent = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name="Belgilangan foiz",
    )
    rec_dism_date = models.DateField(verbose_name="Hujjat sanasi")
    dismissal_reason = models.TextField(
        blank=True, default="", verbose_name="Bo'shatish sababi"
    )
    extra_summa = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name="Qo'shimcha summa",
    )
    extra_percent = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name="Qo'shimcha foiz",
    )
    attachment = models.FileField(
        upload_to="hr/recruitment_dismissals/%Y/%m/",
        blank=True,
        null=True,
        validators=[
            FileExtensionValidator(["pdf", "xls", "xlsx"]),
            FileSizeValidator(max_size_mb=10),
        ],
        verbose_name="Asos hujjat",
        help_text="Ishga olish/bo'shatish uchun asos bo'lgan hujjat (PDF yoki Excel, 10 MB gacha)",
    )

    class Meta:
        db_table = "hr_recruitment_dismissal"
        verbose_name = "Ishga olish / bo'shatish"
        verbose_name_plural = "Ishga olish / bo'shatishlar"

    def __str__(self):
        return f"{self.employee} — {self.get_type_display()}"
