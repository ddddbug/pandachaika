# Generated by Django 2.1.4 on 2019-01-05 20:36

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('viewer', '0072_auto_20181210_1420'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='eventlog',
            options={'ordering': ['-create_date'], 'permissions': (('read_all_logs', 'Can view a general log from all users'),), 'verbose_name_plural': 'Event logs'},
        ),
    ]