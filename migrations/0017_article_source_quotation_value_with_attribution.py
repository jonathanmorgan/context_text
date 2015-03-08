# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('sourcenet', '0016_auto_20150305_2337'),
    ]

    operations = [
        migrations.AddField(
            model_name='article_source_quotation',
            name='value_with_attribution',
            field=models.TextField(null=True, blank=True),
            preserve_default=True,
        ),
    ]
