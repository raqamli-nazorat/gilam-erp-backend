from django.db import models

from apps.base.models import BaseModel


class WorkSchedule(BaseModel):
    name = models.CharField(max_length=100, verbose_name="Nomi")
    description = models.TextField(blank=True, default="", verbose_name="Tavsifi")
    from_hour = models.TimeField(verbose_name="Boshlanish vaqti")
    to_hour = models.TimeField(verbose_name="Tugash vaqti")
    is_monday = models.BooleanField(default=False, verbose_name="Dushanba")
    is_tuesday = models.BooleanField(default=False, verbose_name="Seshanba")
    is_wednesday = models.BooleanField(default=False, verbose_name="Chorshanba")
    is_thursday = models.BooleanField(default=False, verbose_name="Payshanba")
    is_friday = models.BooleanField(default=False, verbose_name="Juma")
    is_saturday = models.BooleanField(default=False, verbose_name="Shanba")
    is_sunday = models.BooleanField(default=False, verbose_name="Yakshanba")

    class Meta:
        db_table = "hr_work_schedule"
        verbose_name = "Ish grafigi"
        verbose_name_plural = "Ish grafiklari"

    def __str__(self):
        return self.name
