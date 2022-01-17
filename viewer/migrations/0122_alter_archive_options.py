# Generated by Django 3.2.5 on 2021-08-17 01:22

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('viewer', '0121_alter_archivemanageentry_mark_extra'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='archive',
            options={'permissions': (('publish_archive', 'Can publish available archives'), ('manage_archive', 'Can manage available archives'), ('mark_archive', 'Can mark available archives'), ('view_marks', 'Can view archive marks'), ('match_archive', 'Can match archives'), ('update_metadata', 'Can update metadata'), ('recalc_fileinfo', 'Can recalculate file info'), ('upload_with_metadata_archive', 'Can upload a file with an associated metadata source'), ('expand_archive', 'Can extract and reduce archives'))},
        ),
    ]
