# -*- coding: utf-8 -*-
# Generated by Django 1.11.3 on 2017-07-20 16:25
from __future__ import unicode_literals

from django.db import migrations, models
import viewer.models


class Migration(migrations.Migration):

    dependencies = [
        ('viewer', '0037_gallery_provider'),
    ]

    operations = [
        migrations.AlterField(
            model_name='gallery',
            name='thumbnail',
            field=models.ImageField(blank=True, default='', height_field='thumbnail_height', max_length=500, upload_to=viewer.models.gallery_thumb_path_handler, width_field='thumbnail_width'),
        ),
    ]
