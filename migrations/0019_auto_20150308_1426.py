# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('sourcenet', '0018_article_author_affilitaion'),
    ]

    operations = [
        migrations.RenameField(
            model_name='article',
            old_name='author_affilitaion',
            new_name='author_affiliation',
        ),
    ]
