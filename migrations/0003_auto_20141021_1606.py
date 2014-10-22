# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('sourcenet', '0002_auto_20141021_1409'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='article_notes',
            name='type',
        ),
        migrations.RemoveField(
            model_name='article_rawdata',
            name='type',
        ),
        migrations.RemoveField(
            model_name='article_text',
            name='type',
        ),
        migrations.AddField(
            model_name='article_notes',
            name='content_type',
            field=models.CharField(default='none', max_length=255, null=True, blank=True, choices=[('canonical', 'Canonical'), ('html', 'HTML'), ('text', 'Text'), ('other', 'Other'), ('none', 'None')]),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='article_rawdata',
            name='content_type',
            field=models.CharField(default='none', max_length=255, null=True, blank=True, choices=[('canonical', 'Canonical'), ('html', 'HTML'), ('text', 'Text'), ('other', 'Other'), ('none', 'None')]),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='article_text',
            name='content_type',
            field=models.CharField(default='none', max_length=255, null=True, blank=True, choices=[('canonical', 'Canonical'), ('html', 'HTML'), ('text', 'Text'), ('other', 'Other'), ('none', 'None')]),
            preserve_default=True,
        ),
    ]
