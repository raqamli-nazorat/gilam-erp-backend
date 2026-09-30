from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import connection, models, transaction
from django.db.models import Max
from django.utils import timezone

from apps.base.models import BaseModel

from .employee import Employee

# Tabel raqamini berishda ishlatiladigan PostgreSQL advisory lock kaliti
TAB_NUMBER_LOCK = 7301


def current_year():
    """Joriy (mahalliy) yilni qaytaradi — tabel yili standart qiymati."""
    return timezone.localdate().year


class EmployeeTimesheet(BaseModel):
    class Month(models.IntegerChoices):
        JANUARY = 1, "Yanvar"
        FEBRUARY = 2, "Fevral"
        MARCH = 3, "Mart"
        APRIL = 4, "Aprel"
        MAY = 5, "May"
        JUNE = 6, "Iyun"
        JULY = 7, "Iyul"
        AUGUST = 8, "Avgust"
        SEPTEMBER = 9, "Sentabr"
        OCTOBER = 10, "Oktabr"
        NOVEMBER = 11, "Noyabr"
        DECEMBER = 12, "Dekabr"

    class Status(models.TextChoices):
        DRAFT = "draft", "Qoralama"
        APPROVED = "approved", "Tasdiqlangan"
        CANCELLED = "cancelled", "Bekor qilingan"

    branch = models.ForeignKey(
        "organization.Branch",
        on_delete=models.PROTECT,
        related_name="employee_timesheets",
        db_index=True,
        verbose_name="Filial",
    )
    year = models.PositiveSmallIntegerField(
        default=current_year,
        validators=[MinValueValidator(2000), MaxValueValidator(2100)],
        db_index=True,
        verbose_name="Yil",
    )
    for_month = models.PositiveSmallIntegerField(
        choices=Month.choices, db_index=True, verbose_name="Oy"
    )
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.DRAFT,
        db_index=True,
        verbose_name="Holati",
    )

    tab_number = models.PositiveIntegerField(
        unique=True, editable=False, verbose_name="Tabel raqami"
    )

    def save(self, *args, **kwargs):
        """Yangi tabelga avtomatik ketma-ket tabel raqami beradi."""
        if self._state.adding and self.tab_number is None:
            with transaction.atomic():
                # Bir vaqtda yaratishda bir xil raqam chiqmasligi uchun qulflanadi
                with connection.cursor() as cursor:
                    cursor.execute(
                        "SELECT pg_advisory_xact_lock(%s)", [TAB_NUMBER_LOCK]
                    )
                last = EmployeeTimesheet.objects.aggregate(last=Max("tab_number"))[
                    "last"
                ]
                self.tab_number = (last or 0) + 1
                return super().save(*args, **kwargs)
        return super().save(*args, **kwargs)

    class Meta:
        db_table = "hr_employee_timesheet"
        verbose_name = "Xodimlar tabeli"
        verbose_name_plural = "Xodimlar tabellari"
        constraints = [
            models.UniqueConstraint(
                fields=["branch", "year", "for_month"],
                condition=models.Q(is_active=True) & ~models.Q(status="cancelled"),
                name="unique_live_timesheet_per_branch_month",
            )
        ]

    def __str__(self):
        return f"{self.branch} — {self.year} {self.get_for_month_display()}"


class EmployeeTimesheetItem(BaseModel):
    employee_timesheet = models.ForeignKey(
        EmployeeTimesheet,
        on_delete=models.CASCADE,
        related_name="items",
        db_index=True,
        verbose_name="Tabel",
    )
    employee = models.ForeignKey(
        Employee,
        on_delete=models.PROTECT,
        related_name="timesheet_items",
        db_index=True,
        verbose_name="Xodim",
    )
    date = models.DateTimeField(verbose_name="Sana")
    work_hour_in_plan = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name="Rejadagi ish soati",
    )
    input_date = models.DateTimeField(
        null=True, blank=True, verbose_name="Kelgan vaqti"
    )
    output_lunch_date = models.DateTimeField(
        null=True, blank=True, verbose_name="Tushlikka chiqqan vaqti"
    )
    input_lunch_date = models.DateTimeField(
        null=True, blank=True, verbose_name="Tushlikdan kelgan vaqti"
    )
    output_date = models.DateTimeField(
        null=True, blank=True, verbose_name="Ketgan vaqti"
    )
    work_hour_in_fact = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name="Haqiqiy ish soati",
    )

    class Meta:
        db_table = "hr_employee_timesheet_item"
        verbose_name = "Tabel qatori"
        verbose_name_plural = "Tabel qatorlari"

    def __str__(self):
        return f"{self.employee} — {self.date:%Y-%m-%d}"
