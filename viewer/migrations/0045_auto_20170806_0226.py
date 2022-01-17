# -*- coding: utf-8 -*-
# Generated by Django 1.11.3 on 2017-08-06 02:26
from __future__ import unicode_literals

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('viewer', '0044_auto_20170806_0129'),
    ]

    operations = [
        migrations.AddField(
            model_name='provider',
            name='create_date',
            field=models.DateTimeField(auto_now_add=True, default=django.utils.timezone.now),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='provider',
            name='last_modified',
            field=models.DateTimeField(auto_now=True, null=True),
        ),
    ]
