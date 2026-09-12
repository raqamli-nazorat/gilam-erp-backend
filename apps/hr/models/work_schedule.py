from django.db import models

from apps.base.models import BaseModel


class WorkSchedule(BaseModel):

    branch = models.ForeignKey(
        "organization.Branch",
        on_delete=models.PROTECT,
        related_name="work_schedules",
        db_index=True,
        verbose_name="Filial",
    )
    name = models.CharField(max_length=100, verbose_name="Nomi")
    description = models.TextField(blank=True, default="", verbose_name="Tavsifi")
    from_date = models.DateField(verbose_name="Boshlanish sanasi")
    to_date = models.DateField(verbose_name="Tugash sanasi")
    from_hour = models.TimeField(verbose_name="Boshlanish vaqti")
    to_hour = models.TimeField(verbose_name="Tugash vaqti")

    class Meta:
        db_table = "hr_work_schedule"
        verbose_name = "Ish jadvali"
        verbose_name_plural = "Ish jadvallari"

    def __str__(self):
        return self.name


class WorkScheduleItem(BaseModel):

    class DayType(models.TextChoices):
        FULL_HOLIDAY = "full_holiday", "To'liq bayram"
        PARTIAL_WORKDAY = "partial_workday", "Qisman ish kuni"
        FULL_WORKDAY = "full_workday", "To'liq ish kuni"

    work_schedule = models.ForeignKey(
        WorkSchedule,
        on_delete=models.CASCADE,
        related_name="items",
        db_index=True,
        verbose_name="Ish jadvali",
    )
    name = models.CharField(max_length=100, verbose_name="Nomi")
    day_type = models.CharField(
        max_length=20,
        choices=DayType.choices,
        db_index=True,
        verbose_name="Kun turi",
    )
    day_date = models.DateField(verbose_name="Sana")
    from_hour = models.TimeField(verbose_name="Boshlanish vaqti")
    to_hour = models.TimeField(verbose_name="Tugash vaqti")

    class Meta:
        db_table = "hr_work_schedule_item"
        verbose_name = "Ish jadvali kuni"
        verbose_name_plural = "Ish jadvali kunlari"

    def __str__(self):
        return f"{self.day_date} — {self.get_day_type_display()}"
