from django.contrib.postgres.fields import ArrayField
from django.db import models

from apps.base.models import BaseModel


class Weekday(models.IntegerChoices):
    """Hafta kunlari — `WorkSchedule.days` massividagi qiymatlar."""

    MONDAY = 0, "Dushanba"
    TUESDAY = 1, "Seshanba"
    WEDNESDAY = 2, "Chorshanba"
    THURSDAY = 3, "Payshanba"
    FRIDAY = 4, "Juma"
    SATURDAY = 5, "Shanba"
    SUNDAY = 6, "Yakshanba"


class WorkSchedule(BaseModel):
    name = models.CharField(max_length=100, verbose_name="Nomi")
    description = models.TextField(blank=True, default="", verbose_name="Tavsifi")
    from_hour = models.TimeField(verbose_name="Boshlanish vaqti")
    to_hour = models.TimeField(verbose_name="Tugash vaqti")
    days = ArrayField(
        models.PositiveSmallIntegerField(choices=Weekday.choices),
        default=list,
        blank=True,
        verbose_name="Hafta kunlari",
        help_text="Ish kunlari ro'yxati: 0=Dushanba, 1=Seshanba, 2=Chorshanba, "
        "3=Payshanba, 4=Juma, 5=Shanba, 6=Yakshanba. Masalan: [0, 1, 2, 3, 4]",
    )

    class Meta:
        db_table = "hr_work_schedule"
        verbose_name = "Ish grafigi"
        verbose_name_plural = "Ish grafiklari"

    def __str__(self):
        return self.name
