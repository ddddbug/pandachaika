# Generated by Django 3.2.5 on 2021-08-17 01:09

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('viewer', '0118_alter_archivemanageentry_options'),
    ]

    operations = [
        migrations.AddField(
            model_name='archivemanageentry',
            name='mark_date',
            field=models.DateTimeField(default=django.utils.timezone.now),
        ),
    ]
