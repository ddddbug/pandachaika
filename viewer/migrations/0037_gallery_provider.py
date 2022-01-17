# -*- coding: utf-8 -*-
# Generated by Django 1.11.3 on 2017-07-17 21:00
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('viewer', '0036_wantedgallery_notify_when_found'),
    ]

    operations = [
        migrations.AddField(
            model_name='gallery',
            name='provider',
            field=models.CharField(blank=True, default='', max_length=50, null=True, verbose_name='Provider'),
        ),
    ]
