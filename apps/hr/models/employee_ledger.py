from django.db import models

from apps.base.models import BaseModel

from .employee import Employee


class EmployeeLedger(BaseModel):
    """Xodim harakatlari daftari — ishga olish, bo'shatish, lavozim o'zgarishi."""

    class Type(models.TextChoices):
        RECRUITMENT = "recruitment", "Ishga olish"
        DISMISSAL_WORK = "dismissal_work", "Ishdan bo'shatish"
        CHANGE_POSITION = "change_position", "Lavozim o'zgarishi"

    branch = models.ForeignKey(
        "organization.Branch",
        on_delete=models.PROTECT,
        related_name="employee_ledgers",
        db_index=True,
        verbose_name="Filial",
    )
    employee = models.ForeignKey(
        Employee,
        on_delete=models.PROTECT,
        related_name="ledgers",
        db_index=True,
        verbose_name="Xodim",
    )
    type = models.CharField(
        max_length=20,
        choices=Type.choices,
        db_index=True,
        verbose_name="Turi",
    )

    class Meta:
        db_table = "hr_employee_ledger"
        verbose_name = "Xodim daftari yozuvi"
        verbose_name_plural = "Xodim daftari yozuvlari"

    def __str__(self):
        """Xodim va harakat turini qaytaradi."""
        return f"{self.employee} — {self.get_type_display()}"
