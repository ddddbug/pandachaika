# Generated by Django 3.2.13 on 2022-06-06 04:05

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('viewer', '0144_archive_archive_pub2_binned'),
    ]

    operations = [
        migrations.AddField(
            model_name='gallery',
            name='first_gallery',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='newer_galleries', to='viewer.gallery'),
        ),
        migrations.AddField(
            model_name='gallery',
            name='parent_gallery',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='children_galleries', to='viewer.gallery'),
        ),
        migrations.CreateModel(
            name='GalleryProviderData',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('origin', models.CharField(choices=[(1, 'Native'), (2, 'Processed'), (3, 'Other')], max_length=10)),
                ('data_type', models.CharField(choices=[('text', 'Text'), ('float', 'Float'), ('int', 'Integer'), ('date', 'Date'), ('duration', 'Duration'), ('bool', 'Boolean')], max_length=10)),
                ('value_text', models.TextField(blank=True, null=True)),
                ('value_float', models.FloatField(blank=True, null=True)),
                ('value_int', models.IntegerField(blank=True, null=True)),
                ('value_date', models.DateTimeField(blank=True, null=True)),
                ('value_duration', models.DurationField(blank=True, null=True)),
                ('value_bool', models.BooleanField(blank=True, null=True)),
                ('gallery', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='viewer.gallery')),
            ],
            options={
                'verbose_name_plural': 'Gallery provider datas',
                'unique_together': {('gallery', 'name')},
            },
        ),
    ]
