# Generated by Django 3.2 on 2021-04-14 23:53

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('viewer', '0099_auto_20210329_1722'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='gallery',
            options={'permissions': (('publish_gallery', 'Can publish available galleries'), ('private_gallery', 'Can set private available galleries'), ('download_gallery', 'Can download present galleries'), ('mark_delete_gallery', 'Can mark galleries as deleted'), ('manage_missing_archives', 'Can manage missing archives'), ('view_submitted_gallery', 'Can view submitted galleries'), ('approve_gallery', 'Can approve submitted galleries'), ('wanted_gallery_found', 'Can be notified of new wanted gallery matches'), ('crawler_adder', 'Can add links to the crawler with more options')), 'verbose_name_plural': 'galleries'},
        ),
    ]
