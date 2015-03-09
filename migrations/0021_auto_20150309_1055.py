# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import datetime


class Migration(migrations.Migration):

    dependencies = [
        ('sourcenet', '0020_auto_20150309_0005'),
    ]

    operations = [
        migrations.AddField(
            model_name='alternate_name',
            name='capture_method',
            field=models.CharField(max_length=255, null=True, blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='alternate_name',
            name='create_date',
            field=models.DateTimeField(default=datetime.datetime(2015, 3, 9, 10, 54, 27, 796127), auto_now_add=True),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='alternate_name',
            name='last_modified',
            field=models.DateTimeField(default=datetime.datetime(2015, 3, 9, 10, 54, 38, 388694), auto_now=True),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='article_author',
            name='capture_method',
            field=models.CharField(max_length=255, null=True, blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='article_data',
            name='capture_method',
            field=models.CharField(max_length=255, null=True, blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='person',
            name='capture_method',
            field=models.CharField(max_length=255, null=True, blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='person',
            name='create_date',
            field=models.DateTimeField(default=datetime.datetime(2015, 3, 9, 10, 54, 55, 115900), auto_now_add=True),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='person',
            name='last_modified',
            field=models.DateTimeField(default=datetime.datetime(2015, 3, 9, 10, 55, 6, 865401), auto_now=True),
            preserve_default=False,
        ),
    ]
