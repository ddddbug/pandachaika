# Generated by Django 2.1 on 2018-10-03 14:34

from django.db import migrations


def add_permissions(apps, schema_editor):
    pass


def remove_permissions(apps, schema_editor):
    """Reverse the above additions of permissions."""
    ContentType = apps.get_model('contenttypes.ContentType')
    Permission = apps.get_model('auth.Permission')
    try:
        content_type = ContentType.objects.get(
            model='wantedgallery',
            app_label='viewer',
        )
    except ContentType.DoesNotExist:
        return
    # This cascades to Group
    Permission.objects.filter(
        content_type=content_type,
        codename__in=('view_wanted_gallery', 'create_wanted_gallery', 'edit_wanted_gallery'),
    ).delete()


class Migration(migrations.Migration):

    dependencies = [
        ('viewer', '0068_auto_20181003_1128'),
    ]

    operations = [
        migrations.RunPython(remove_permissions, add_permissions),
    ]
