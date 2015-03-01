# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('sourcenet', '0009_auto_20150228_1403'),
    ]

    operations = [
        migrations.RenameField(
            model_name='person_external_uuid',
            old_name='UUID',
            new_name='uuid',
        ),
    ]
