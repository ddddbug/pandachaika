# Generated by Django 2.2.9 on 2019-12-26 14:56

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('viewer', '0089_auto_20191220_1641'),
    ]

    operations = [
        migrations.AddField(
            model_name='artist',
            name='twitter_handle',
            field=models.CharField(blank=True, default='', max_length=50, null=True),
        ),
    ]