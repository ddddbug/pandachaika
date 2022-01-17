# Generated by Django 2.2.9 on 2019-12-20 19:41

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('viewer', '0088_auto_20191219_1018'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='wantedgallery',
            name='wanted_providers',
        ),
        migrations.AddField(
            model_name='wantedgallery',
            name='wanted_providers',
            field=models.ManyToManyField(blank=True, to='viewer.Provider'),
        ),
    ]
