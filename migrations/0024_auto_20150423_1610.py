# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('sourcenet', '0023_auto_20150423_1601'),
    ]

    operations = [
        migrations.AlterField(
            model_name='article_data',
            name='topics',
            field=models.ManyToManyField(to='sourcenet.Topic', blank=True),
        ),
        migrations.AlterField(
            model_name='article_source',
            name='topics',
            field=models.ManyToManyField(to='sourcenet.Topic', blank=True),
        ),
    ]
