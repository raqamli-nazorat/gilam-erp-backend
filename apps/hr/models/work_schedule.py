from django.contrib.postgres.fields import ArrayField
from django.db import models

from apps.base.models import BaseModel


class Weekday(models.IntegerChoices):
    """Hafta kunlari — `WorkSchedule.work_days` massividagi qiymatlar."""

    MONDAY = 0, "Dushanba"
    TUESDAY = 1, "Seshanba"
    WEDNESDAY = 2, "Chorshanba"
    THURSDAY = 3, "Payshanba"
    FRIDAY = 4, "Juma"
    SATURDAY = 5, "Shanba"
    SUNDAY = 6, "Yakshanba"


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
    from_date = models.DateField(
        null=True, blank=True, verbose_name="Boshlanish sanasi"
    )
    to_date = models.DateField(null=True, blank=True, verbose_name="Tugash sanasi")
    from_hour = models.TimeField(verbose_name="Boshlanish vaqti")
    to_hour = models.TimeField(verbose_name="Tugash vaqti")
    work_days = ArrayField(
        models.PositiveSmallIntegerField(choices=Weekday.choices),
        default=list,
        verbose_name="Ish kunlari",
        help_text="0=Dushanba, 1=Seshanba, 2=Chorshanba, 3=Payshanba, "
        "4=Juma, 5=Shanba, 6=Yakshanba. Masalan: [0, 1, 2, 3, 4]",
    )

    class Meta:
        db_table = "hr_work_schedule"
        verbose_name = "Ish grafigi"
        verbose_name_plural = "Ish grafiklari"

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
        verbose_name="Ish grafigi",
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
        verbose_name = "Ish grafigi kuni"
        verbose_name_plural = "Ish grafigi kunlari"

    def __str__(self):
        return f"{self.name} — {self.day_date}"
