# Generated by Django 2.1 on 2018-08-09 03:39

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('viewer', '0059_gallery_origin'),
    ]

    operations = [
        migrations.AddField(
            model_name='gallery',
            name='reason',
            field=models.CharField(blank=True, default='', max_length=200, null=True),
        ),
    ]