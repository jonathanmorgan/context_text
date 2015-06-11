# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('sourcenet', '0032_auto_20150503_2256'),
    ]

    operations = [
        migrations.AddField(
            model_name='analysis_reliability_names',
            name='coder1_article_data_id',
            field=models.IntegerField(null=True, blank=True),
        ),
        migrations.AddField(
            model_name='analysis_reliability_names',
            name='coder2_article_data_id',
            field=models.IntegerField(null=True, blank=True),
        ),
        migrations.AddField(
            model_name='analysis_reliability_names',
            name='coder3_article_data_id',
            field=models.IntegerField(null=True, blank=True),
        ),
    ]
