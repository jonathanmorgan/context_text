# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('sourcenet', '0017_article_source_quotation_value_with_attribution'),
    ]

    operations = [
        migrations.AddField(
            model_name='article',
            name='author_affilitaion',
            field=models.CharField(max_length=255, null=True, blank=True),
            preserve_default=True,
        ),
    ]
