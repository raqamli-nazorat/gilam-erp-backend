from django.db import models

from apps.base.models import BaseModel
from apps.utils.validators import CANCEL_ATTACHMENT_VALIDATORS

from .employee import Employee
from .employee_timesheet import EmployeeTimesheet


class CalculatingSalary(BaseModel):
    Month = EmployeeTimesheet.Month

    class Status(models.TextChoices):
        DRAFT = "draft", "Qoralama"
        APPROVED = "approved", "Tasdiqlangan"
        CANCELLED = "cancelled", "Bekor qilingan"

    branch = models.ForeignKey(
        "organization.Branch",
        on_delete=models.PROTECT,
        related_name="calculating_salaries",
        db_index=True,
        verbose_name="Filial",
    )
    employee = models.ForeignKey(
        Employee,
        on_delete=models.PROTECT,
        related_name="calculating_salaries",
        db_index=True,
        verbose_name="Xodim",
    )
    for_month = models.PositiveSmallIntegerField(
        choices=Month.choices, db_index=True, verbose_name="Oy"
    )
    amount = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        default=0,
        verbose_name="Summa (UZS)",
    )
    currency = models.ForeignKey(
        "finance.Currency",
        on_delete=models.PROTECT,
        related_name="calculating_salaries",
        db_index=True,
        verbose_name="Valyuta",
    )
    currency_amount = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        default=0,
        verbose_name="Valyutadagi summa",
    )
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.DRAFT,
        db_index=True,
        verbose_name="Holati",
    )
    cancel_reason = models.TextField(
        blank=True, default="", verbose_name="Bekor qilish sababi"
    )
    cancel_attachment = models.FileField(
        upload_to="hr/calculating_salaries/cancel/%Y/%m/",
        null=True,
        blank=True,
        validators=CANCEL_ATTACHMENT_VALIDATORS,
        verbose_name="Bekor qilish hujjati",
        help_text="Bekor qilish asosi (PDF yoki Excel, 10 MB gacha)",
    )

    class Meta:
        db_table = "hr_calculating_salary"
        verbose_name = "Oylik hisobi"
        verbose_name_plural = "Oylik hisoblari"

    def __str__(self):
        return f"{self.employee} — {self.get_for_month_display()}"
