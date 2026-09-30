from django.db import migrations, models


def fill_tab_numbers(apps, schema_editor):
    """Mavjud xodimlarga yaratilgan sanasi tartibida tabel raqami beradi."""
    Employee = apps.get_model("hr", "Employee")
    for number, employee in enumerate(
        Employee.objects.order_by("created_at", "id"), start=1
    ):
        Employee.objects.filter(pk=employee.pk).update(tab_number=number)


class Migration(migrations.Migration):
    dependencies = [
        ("hr", "0014_employeetimesheet_tab_number"),
    ]

    operations = [
        migrations.AddField(
            model_name="employee",
            name="tab_number",
            field=models.PositiveIntegerField(
                editable=False, null=True, verbose_name="Tabel raqami"
            ),
        ),
        migrations.RunPython(fill_tab_numbers, migrations.RunPython.noop),
        migrations.AlterField(
            model_name="employee",
            name="tab_number",
            field=models.PositiveIntegerField(
                editable=False, unique=True, verbose_name="Tabel raqami"
            ),
        ),
    ]
