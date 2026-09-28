from django.db import models

from apps.base.models import BaseModel
from apps.utils.validators import CANCEL_ATTACHMENT_VALIDATORS

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
    cancel_reason = models.TextField(
        blank=True, default="", verbose_name="Bekor qilish sababi"
    )
    cancel_attachment = models.FileField(
        upload_to="finance/accrual_documents/cancel/%Y/%m/",
        null=True,
        blank=True,
        validators=CANCEL_ATTACHMENT_VALIDATORS,
        verbose_name="Bekor qilish hujjati",
        help_text="Bekor qilish asosi (PDF yoki Excel, 10 MB gacha)",
    )

    class Meta:
        db_table = "finance_accrual_retention_document"
        verbose_name = "Hisoblash / ushlab qolish hujjati"
        verbose_name_plural = "Hisoblash / ushlab qolish hujjatlari"

    def __str__(self):
        return f"{self.employee} — {self.accrual_retention} ({self.date:%Y-%m-%d})"
