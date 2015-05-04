# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('sourcenet', '0031_auto_20150501_2325'),
    ]

    operations = [
        migrations.AddField(
            model_name='article_author',
            name='original_person',
            field=models.ForeignKey(related_name='sourcenet_article_author_original_person_set', blank=True, to='sourcenet.Person', null=True),
        ),
        migrations.AddField(
            model_name='article_source',
            name='original_person',
            field=models.ForeignKey(related_name='sourcenet_article_source_original_person_set', blank=True, to='sourcenet.Person', null=True),
        ),
    ]
