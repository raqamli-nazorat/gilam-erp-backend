import django.core.validators
from django.db import migrations, models
from django.db.models import Count
from django.utils import timezone

import apps.hr.models.employee_timesheet


def fill_years(apps, schema_editor):
    """Eski tabellar yilini: birinchi qator sanasidan, bo'lmasa yaratilgan sanadan oladi."""
    Timesheet = apps.get_model("hr", "EmployeeTimesheet")
    Item = apps.get_model("hr", "EmployeeTimesheetItem")
    for timesheet in Timesheet.objects.all():
        first_date = (
            Item.objects.filter(employee_timesheet=timesheet, is_active=True)
            .order_by("date")
            .values_list("date", flat=True)
            .first()
        )
        year = timezone.localtime(first_date or timesheet.created_at).year
        Timesheet.objects.filter(pk=timesheet.pk).update(year=year)


def ensure_no_duplicates(apps, schema_editor):
    """Bir filial, yil va oyda bir nechta faol tabel bo'lsa, migratsiyani to'xtatadi."""
    Timesheet = apps.get_model("hr", "EmployeeTimesheet")
    duplicates = (
        Timesheet.objects.filter(is_active=True)
        .exclude(status="cancelled")
        .order_by()
        .values("branch_id", "year", "for_month")
        .annotate(total=Count("id"))
        .filter(total__gt=1)
    )
    if duplicates:
        rows = ", ".join(
            f"filial={row['branch_id']} yil={row['year']} oy={row['for_month']} "
            f"({row['total']} ta)"
            for row in duplicates
        )
        raise RuntimeError(
            "Bir filial, yil va oyda bir nechta faol tabel bor. Avval ortiqchasini "
            f"bekor qiling yoki o'chiring: {rows}"
        )


class Migration(migrations.Migration):
    dependencies = [
        ("hr", "0012_calculatingsalary_cancel_reason_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="employeetimesheet",
            name="year",
            field=models.PositiveSmallIntegerField(
                db_index=True,
                default=apps.hr.models.employee_timesheet.current_year,
                validators=[
                    django.core.validators.MinValueValidator(2000),
                    django.core.validators.MaxValueValidator(2100),
                ],
                verbose_name="Yil",
            ),
        ),
        migrations.RunPython(fill_years, migrations.RunPython.noop),
        migrations.RunPython(ensure_no_duplicates, migrations.RunPython.noop),
        migrations.AddConstraint(
            model_name="employeetimesheet",
            constraint=models.UniqueConstraint(
                condition=models.Q(
                    ("is_active", True),
                    models.Q(("status", "cancelled"), _negated=True),
                ),
                fields=("branch", "year", "for_month"),
                name="unique_live_timesheet_per_branch_month",
            ),
        ),
    ]
