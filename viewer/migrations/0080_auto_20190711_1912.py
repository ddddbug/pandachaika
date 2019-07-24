# Generated by Django 2.2.3 on 2019-07-11 23:12

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('viewer', '0079_archive_original_filename'),
    ]

    operations = [
        migrations.CreateModel(
            name='ArchiveGroup',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=500)),
                ('title_slug', models.SlugField(unique=True)),
                ('details', models.TextField(blank=True, default='', null=True)),
                ('position', models.PositiveIntegerField(default=1)),
                ('public', models.BooleanField(default=False)),
                ('create_date', models.DateTimeField(auto_now_add=True)),
                ('last_modified', models.DateTimeField(auto_now=True, null=True)),
            ],
            options={
                'verbose_name_plural': 'Archive groups',
                'ordering': ['position'],
            },
        ),
        migrations.CreateModel(
            name='ArchiveGroupEntry',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(blank=True, max_length=500, null=True)),
                ('position', models.PositiveIntegerField(default=1)),
                ('archive', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='viewer.Archive')),
                ('archive_group', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='viewer.ArchiveGroup')),
            ],
            options={
                'verbose_name_plural': 'Archive group entries',
                'ordering': ['position'],
            },
        ),
        migrations.AddField(
            model_name='archivegroup',
            name='archives',
            field=models.ManyToManyField(blank=True, default='', related_name='archive_group', through='viewer.ArchiveGroupEntry', to='viewer.Archive'),
        ),
    ]
