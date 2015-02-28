# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('sourcenet', '0008_alternate_name'),
    ]

    operations = [
        migrations.AddField(
            model_name='alternate_name',
            name='nickname',
            field=models.CharField(max_length=255, null=True, blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='alternate_name',
            name='original_name_string',
            field=models.CharField(max_length=255, null=True, blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='person',
            name='nickname',
            field=models.CharField(max_length=255, null=True, blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='person',
            name='original_name_string',
            field=models.CharField(max_length=255, null=True, blank=True),
            preserve_default=True,
        ),
    ]
