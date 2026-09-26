from django.db import models

from apps.base.models import BaseModel

from .accrual_retention import AccrualRetention


class AccrualRetentionDocument(BaseModel):
    class Status(models.TextChoices):
        DRAFT = "draft", "Qoralama"
        APPROVED = "approved", "Tasdiqlangan"
        CANCELLED = "cancelled", "Bekor qilingan"

    branch = models.ForeignKey(
        "organization.Branch",
        on_delete=models.PROTECT,
        related_name="accrual_retention_documents",
        db_index=True,
        verbose_name="Filial",
    )
    employee = models.ForeignKey(
        "hr.Employee",
        on_delete=models.PROTECT,
        related_name="accrual_retention_documents",
        db_index=True,
        verbose_name="Xodim",
    )
    accrual_retention = models.ForeignKey(
        AccrualRetention,
        on_delete=models.PROTECT,
        related_name="documents",
        db_index=True,
        verbose_name="Hisoblash / ushlab qolish",
    )
    date = models.DateTimeField(db_index=True, verbose_name="Sana")
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.DRAFT,
        db_index=True,
        verbose_name="Holati",
    )

    class Meta:
        db_table = "finance_accrual_retention_document"
        verbose_name = "Hisoblash / ushlab qolish hujjati"
        verbose_name_plural = "Hisoblash / ushlab qolish hujjatlari"

    def __str__(self):
        return f"{self.employee} — {self.accrual_retention} ({self.date:%Y-%m-%d})"
