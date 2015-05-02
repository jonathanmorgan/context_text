# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('sourcenet', '0030_auto_20150501_1837'),
    ]

    operations = [
        migrations.AddField(
            model_name='analysis_reliability_ties',
            name='coder1_id_list',
            field=models.CharField(max_length=255, null=True, blank=True),
        ),
        migrations.AddField(
            model_name='analysis_reliability_ties',
            name='coder2_id_list',
            field=models.CharField(max_length=255, null=True, blank=True),
        ),
        migrations.AddField(
            model_name='analysis_reliability_ties',
            name='coder3_id_list',
            field=models.CharField(max_length=255, null=True, blank=True),
        ),
        migrations.AddField(
            model_name='analysis_reliability_ties',
            name='relation_person_name',
            field=models.CharField(max_length=255, null=True, blank=True),
        ),
        migrations.AddField(
            model_name='analysis_reliability_ties',
            name='relation_person_type',
            field=models.CharField(max_length=255, null=True, blank=True),
        ),
    ]
