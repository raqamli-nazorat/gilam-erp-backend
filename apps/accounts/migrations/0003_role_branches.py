from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0002_role_is_system_role_organization_role_permissions_and_more'),
        ('organization', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='role',
            name='branches',
            field=models.ManyToManyField(blank=True, help_text="Ushbu rol amal qiladigan filiallar (bo'sh bo'lsa butun tashkilot bo'yicha)", related_name='roles', to='organization.branch', verbose_name='Filiallar'),
        ),
    ]
