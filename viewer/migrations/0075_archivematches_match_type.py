# Generated by Django 2.2 on 2019-04-04 15:26

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('viewer', '0074_auto_20190402_1152'),
    ]

    operations = [
        migrations.AddField(
            model_name='archivematches',
            name='match_type',
            field=models.CharField(blank=True, default='', max_length=40, null=True, verbose_name='Match type'),
        ),
    ]
