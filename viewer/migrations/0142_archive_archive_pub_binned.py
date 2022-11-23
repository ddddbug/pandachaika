# Generated by Django 3.2.13 on 2022-05-21 00:01

from django.db import migrations, models
import django.db.models.expressions


class Migration(migrations.Migration):

    dependencies = [
        ('viewer', '0141_archive_binned'),
    ]

    operations = [
        migrations.AddIndex(
            model_name='archive',
            index=models.Index(django.db.models.expressions.OrderBy(django.db.models.expressions.F('create_date'), descending=True, nulls_last=True), django.db.models.expressions.OrderBy(django.db.models.expressions.F('public'), nulls_last=True), django.db.models.expressions.F('binned'), name='archive_pub_binned'),
        ),
    ]
