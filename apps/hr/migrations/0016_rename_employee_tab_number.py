from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("hr", "0015_employee_tab_number"),
    ]

    operations = [
        migrations.RenameField(
            model_name="employee",
            old_name="tab_number",
            new_name="personnel_tab_number",
        ),
    ]
