# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('sourcenet', '0025_analysis_reliability_names_notes'),
    ]

    operations = [
        migrations.AlterField(
            model_name='analysis_reliability_names',
            name='coder3_detected',
            field=models.IntegerField(null=True, blank=True),
        ),
    ]
