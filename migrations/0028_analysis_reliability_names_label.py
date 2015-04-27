# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('sourcenet', '0027_auto_20150424_0119'),
    ]

    operations = [
        migrations.AddField(
            model_name='analysis_reliability_names',
            name='label',
            field=models.CharField(max_length=255, null=True, blank=True),
        ),
    ]
