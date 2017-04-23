# -*- coding: utf-8 -*-
# Generated by Django 1.10.1 on 2017-04-01 12:36
from __future__ import unicode_literals

import apps.timeline.models
from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('contenttypes', '0002_remove_content_type_name'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Comment',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('text', models.TextField(blank=True, error_messages={'invalid': 'Please insert comment text up to 500 characters.'}, help_text='Comment text.', max_length=500, verbose_name='Text')),
                ('created', models.DateTimeField(default=django.utils.timezone.now, editable=False, verbose_name='Created')),
                ('approved', models.BooleanField(default=True, verbose_name='Approved')),
                ('author', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Comment',
                'ordering': ('-created',),
                'get_latest_by': 'created',
                'verbose_name_plural': 'Comments',
            },
        ),
        migrations.CreateModel(
            name='Post',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(blank=True, error_messages={'invalid': 'Please insert 100 character post title.'}, help_text='Post title.', max_length=100, verbose_name='Title')),
                ('body', models.TextField(error_messages={'invalid': 'Please insert post content up to 500 characters.'}, help_text='Post main text.', max_length=500, verbose_name='Body')),
                ('image', models.ImageField(blank=True, error_messages={'invalid': 'Please choose a valid format image.'}, help_text='Image full path.', upload_to=apps.timeline.models.image_full_path, verbose_name='Image')),
                ('created', models.DateTimeField(default=django.utils.timezone.now, editable=False, verbose_name='Created')),
                ('last_updated', models.DateTimeField(blank=True, null=True, verbose_name='Last updated')),
                ('author', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Post',
                'ordering': ('-created',),
                'get_latest_by': 'created',
                'verbose_name_plural': 'Posts',
            },
        ),
        migrations.CreateModel(
            name='Timeline',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateTimeField(editable=False, verbose_name='Date')),
                ('object_id', models.PositiveIntegerField()),
                ('content_type', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='contenttypes.ContentType')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Timeline',
                'verbose_name_plural': 'Timelines',
            },
        ),
        migrations.AddField(
            model_name='comment',
            name='post',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='timeline.Post'),
        ),
    ]
