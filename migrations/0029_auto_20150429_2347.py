# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('sourcenet', '0028_analysis_reliability_names_label'),
    ]

    operations = [
        migrations.CreateModel(
            name='Analysis_Reliability_Ties',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('person_name', models.CharField(max_length=255, null=True, blank=True)),
                ('person_type', models.CharField(max_length=255, null=True, blank=True)),
                ('relation_type', models.CharField(max_length=255, null=True, blank=True)),
                ('coder1_mention_count', models.IntegerField(null=True, blank=True)),
                ('coder2_mention_count', models.IntegerField(null=True, blank=True)),
                ('coder3_mention_count', models.IntegerField(null=True, blank=True)),
                ('label', models.CharField(max_length=255, null=True, blank=True)),
                ('notes', models.TextField(null=True, blank=True)),
                ('create_date', models.DateTimeField(auto_now_add=True)),
                ('last_modified', models.DateTimeField(auto_now=True)),
                ('article', models.ForeignKey(blank=True, to='sourcenet.Article', null=True)),
                ('coder1', models.ForeignKey(related_name='reliability_ties_coder1_set', blank=True, to=settings.AUTH_USER_MODEL, null=True)),
                ('coder2', models.ForeignKey(related_name='reliability_ties_coder2_set', blank=True, to=settings.AUTH_USER_MODEL, null=True)),
                ('coder3', models.ForeignKey(related_name='reliability_ties_coder3_set', blank=True, to=settings.AUTH_USER_MODEL, null=True)),
                ('person', models.ForeignKey(related_name='reliability_ties_from_set', blank=True, to='sourcenet.Person', null=True)),
                ('relation_person', models.ForeignKey(related_name='reliability_ties_to_set', blank=True, to='sourcenet.Person', null=True)),
            ],
            options={
                'ordering': ['article', 'person_type', 'person', 'relation_person'],
            },
        ),
        migrations.AddField(
            model_name='analysis_reliability_names',
            name='coder1_source_type',
            field=models.CharField(max_length=255, null=True, blank=True),
        ),
        migrations.AddField(
            model_name='analysis_reliability_names',
            name='coder2_source_type',
            field=models.CharField(max_length=255, null=True, blank=True),
        ),
        migrations.AddField(
            model_name='analysis_reliability_names',
            name='coder3_source_type',
            field=models.CharField(max_length=255, null=True, blank=True),
        ),
    ]
