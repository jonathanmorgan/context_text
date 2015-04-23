# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('sourcenet', '0022_article_data_status_messages'),
    ]

    operations = [
        migrations.CreateModel(
            name='Analysis_Reliability_Names',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('person_name', models.CharField(max_length=255, null=True, blank=True)),
                ('name_type', models.CharField(max_length=255, null=True, blank=True)),
                ('coder1_detected', models.IntegerField(null=True, blank=True)),
                ('coder1_person_id', models.IntegerField(null=True, blank=True)),
                ('coder2_detected', models.IntegerField(null=True, blank=True)),
                ('coder2_person_id', models.IntegerField(null=True, blank=True)),
                ('coder3_detected', models.IntegerField(blank=True)),
                ('coder3_person_id', models.IntegerField(null=True, blank=True)),
                ('create_date', models.DateTimeField(auto_now_add=True)),
                ('last_modified', models.DateTimeField(auto_now=True)),
                ('article', models.ForeignKey(blank=True, to='sourcenet.Article', null=True)),
                ('coder1', models.ForeignKey(related_name='reliability_names_coder1_set', blank=True, to=settings.AUTH_USER_MODEL, null=True)),
                ('coder2', models.ForeignKey(related_name='reliability_names_coder2_set', blank=True, to=settings.AUTH_USER_MODEL, null=True)),
                ('coder3', models.ForeignKey(related_name='reliability_names_coder3_set', blank=True, to=settings.AUTH_USER_MODEL, null=True)),
                ('person', models.ForeignKey(blank=True, to='sourcenet.Person', null=True)),
            ],
            options={
                'ordering': ['article', 'name_type', 'person'],
            },
        ),
        migrations.AlterModelOptions(
            name='article_source_mention',
            options={'ordering': ['paragraph_number', 'last_modified', 'create_date']},
        ),
        migrations.AlterModelOptions(
            name='article_source_quotation',
            options={'ordering': ['paragraph_number', 'last_modified', 'create_date']},
        ),
    ]
