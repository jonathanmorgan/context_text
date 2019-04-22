# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('context_text', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='article_subject_quotation',
            name='quotation_type',
            field=models.CharField(max_length=255, null=True, blank=True),
        ),
    ]
