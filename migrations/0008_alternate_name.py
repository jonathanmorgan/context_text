# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('sourcenet', '0007_auto_20150225_0019'),
    ]

    operations = [
        migrations.CreateModel(
            name='Alternate_Name',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('first_name', models.CharField(max_length=255)),
                ('middle_name', models.CharField(max_length=255, blank=True)),
                ('last_name', models.CharField(max_length=255)),
                ('name_prefix', models.CharField(max_length=255, null=True, blank=True)),
                ('name_suffix', models.CharField(max_length=255, null=True, blank=True)),
                ('full_name_string', models.CharField(max_length=255, null=True, blank=True)),
                ('gender', models.CharField(max_length=6, choices=[('na', 'Unknown'), ('female', 'Female'), ('male', 'Male')])),
                ('title', models.CharField(max_length=255, blank=True)),
                ('nameparser_pickled', models.TextField(null=True, blank=True)),
                ('is_ambiguous', models.BooleanField(default=False)),
                ('notes', models.TextField(blank=True)),
                ('person', models.ForeignKey(to='sourcenet.Person')),
            ],
            options={
                'ordering': ['last_name', 'first_name', 'middle_name'],
                'abstract': False,
            },
            bases=(models.Model,),
        ),
    ]
