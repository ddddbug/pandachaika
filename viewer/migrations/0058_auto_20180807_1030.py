# Generated by Django 2.1 on 2018-08-07 14:30

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('viewer', '0057_auto_20180807_1027'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='archive',
            options={'permissions': (('publish_archive', 'Can publish available archives'), ('match_archive', 'Can match unmatched archives'), ('upload_with_metadata_archive', 'Can upload a file with an associated metadata source'))},
        ),
    ]
