# Generated by Django 3.2.6 on 2021-08-17 20:19

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('viewer', '0124_alter_archive_origin'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='wantedgallery',
            name='provider',
        ),
    ]
