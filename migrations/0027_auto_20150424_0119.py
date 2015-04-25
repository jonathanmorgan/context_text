# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('sourcenet', '0026_auto_20150424_0117'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='analysis_reliability_names',
            options={'ordering': ['article', 'person_type', 'person']},
        ),
        migrations.RenameField(
            model_name='analysis_reliability_names',
            old_name='name_type',
            new_name='person_type',
        ),
    ]
