# Generated by Django 5.1.3 on 2024-11-25 18:14

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0006_vacationrequest_backup_person_and_more'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AlterField(
            model_name='vacationrequest',
            name='backup_person',
            field=models.ForeignKey(blank=True, help_text='La persona que va a quedar a cargo de tus funciones mientras estás de vacaciones', null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='backup_person', to=settings.AUTH_USER_MODEL),
        ),
    ]