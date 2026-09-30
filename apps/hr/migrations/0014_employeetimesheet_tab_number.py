from django.db import migrations, models


def fill_tab_numbers(apps, schema_editor):
    """Mavjud tabellarga yaratilgan sanasi tartibida tabel raqami beradi."""
    Timesheet = apps.get_model("hr", "EmployeeTimesheet")
    for number, timesheet in enumerate(
        Timesheet.objects.order_by("created_at", "id"), start=1
    ):
        Timesheet.objects.filter(pk=timesheet.pk).update(tab_number=number)


class Migration(migrations.Migration):
    dependencies = [
        ("hr", "0013_employeetimesheet_year_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="employeetimesheet",
            name="tab_number",
            field=models.PositiveIntegerField(
                editable=False, null=True, verbose_name="Tabel raqami"
            ),
        ),
        migrations.RunPython(fill_tab_numbers, migrations.RunPython.noop),
        migrations.AlterField(
            model_name="employeetimesheet",
            name="tab_number",
            field=models.PositiveIntegerField(
                editable=False, unique=True, verbose_name="Tabel raqami"
            ),
        ),
    ]
