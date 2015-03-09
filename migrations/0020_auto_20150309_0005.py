# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import datetime


class Migration(migrations.Migration):

    dependencies = [
        ('sourcenet', '0019_auto_20150308_1426'),
    ]

    operations = [
        migrations.AddField(
            model_name='article_author',
            name='create_date',
            field=models.DateTimeField(default=datetime.datetime(2015, 3, 9, 0, 5, 18, 57371), auto_now_add=True),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='article_author',
            name='last_modified',
            field=models.DateTimeField(default=datetime.datetime(2015, 3, 9, 0, 5, 31, 1201), auto_now=True),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='article_source',
            name='create_date',
            field=models.DateTimeField(default=datetime.datetime(2015, 3, 9, 0, 5, 43, 655467), auto_now_add=True),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='article_source',
            name='last_modified',
            field=models.DateTimeField(default=datetime.datetime(2015, 3, 9, 0, 5, 51, 360312), auto_now=True),
            preserve_default=False,
        ),
    ]
