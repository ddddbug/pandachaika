# Generated by Django 3.1.7 on 2021-03-10 01:05

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('viewer', '0097_auto_20210309_1633'),
    ]

    operations = [
        migrations.AlterField(
            model_name='gallerysubmitentry',
            name='submit_result',
            field=models.CharField(blank=True, default='', max_length=200, null=True),
        ),
    ]
