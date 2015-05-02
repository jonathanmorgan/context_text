# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('sourcenet', '0029_auto_20150429_2347'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='analysis_reliability_ties',
            options={'ordering': ['person_type', 'person', 'relation_person']},
        ),
        migrations.RemoveField(
            model_name='analysis_reliability_ties',
            name='article',
        ),
    ]
