# -*- coding: utf-8 -*-
# Generated by Django 1.11.3 on 2017-07-04 21:45
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('viewer', '0031_archive_public_date'),
    ]

    operations = [
        migrations.AddField(
            model_name='archive',
            name='reason',
            field=models.CharField(blank=True, default='backup', max_length=200, null=True, verbose_name='Reason'),
        ),
    ]
