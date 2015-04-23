# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('sourcenet', '0024_auto_20150423_1610'),
    ]

    operations = [
        migrations.AddField(
            model_name='analysis_reliability_names',
            name='notes',
            field=models.TextField(null=True, blank=True),
        ),
    ]
