# Generated by Django 2.1 on 2018-10-03 14:28

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('viewer', '0067_auto_20181003_1058'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='wantedgallery',
            options={'ordering': ['-release_date'], 'permissions': (('edit_search_filter_wanted_gallery', 'Can edit wanted galleries search filter parameters'), ('edit_search_dates_wanted_gallery', 'Can edit wanted galleries search date parameters'), ('edit_search_notify_wanted_gallery', 'Can edit wanted galleries search notify parameter')), 'verbose_name_plural': 'Wanted galleries'},
        ),
    ]