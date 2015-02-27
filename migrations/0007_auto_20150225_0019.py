# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('sourcenet', '0006_auto_20150107_1520'),
    ]

    operations = [
        migrations.CreateModel(
            name='Person_External_UUID',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=255, null=True, blank=True)),
                ('UUID', models.TextField(null=True, blank=True)),
                ('source', models.CharField(max_length=255, null=True, blank=True)),
                ('notes', models.TextField(null=True, blank=True)),
                ('person', models.ForeignKey(to='sourcenet.Person')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Person_Newspaper',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('notes', models.TextField(null=True, blank=True)),
                ('newspaper', models.ForeignKey(blank=True, to='sourcenet.Newspaper', null=True)),
                ('person', models.ForeignKey(to='sourcenet.Person')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='article_author',
            name='match_confidence_level',
            field=models.DecimalField(default=0.0, null=True, max_digits=11, decimal_places=10, blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='article_source',
            name='match_confidence_level',
            field=models.DecimalField(default=0.0, null=True, max_digits=11, decimal_places=10, blank=True),
            preserve_default=True,
        ),
    ]
