# Generated by Django 2.1 on 2018-08-12 02:22

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('contenttypes', '0002_remove_content_type_name'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('viewer', '0060_gallery_reason'),
    ]

    operations = [
        migrations.CreateModel(
            name='EventLog',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('object_id', models.PositiveIntegerField(null=True)),
                ('action', models.CharField(db_index=True, max_length=50)),
                ('reason', models.CharField(blank=True, default='', max_length=200, null=True)),
                ('create_date', models.DateTimeField(db_index=True, default=django.utils.timezone.now)),
                ('content_type', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='contenttypes.ContentType')),
                ('user', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name_plural': 'Event logs',
                'ordering': ['-create_date'],
            },
        ),
        migrations.AlterField(
            model_name='gallery',
            name='gallery_container',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='gallery_contains', to='viewer.Gallery'),
        ),
        migrations.AlterField(
            model_name='gallery',
            name='status',
            field=models.SmallIntegerField(choices=[(1, 'Normal'), (4, 'Denied'), (5, 'Deleted')], db_index=True, default=1),
        ),
    ]
