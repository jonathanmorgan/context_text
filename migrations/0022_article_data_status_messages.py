# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('sourcenet', '0021_auto_20150309_1055'),
    ]

    operations = [
        migrations.AddField(
            model_name='article_data',
            name='status_messages',
            field=models.TextField(null=True, blank=True),
            preserve_default=True,
        ),
    ]
