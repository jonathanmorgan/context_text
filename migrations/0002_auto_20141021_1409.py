# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('sourcenet', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Project',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=255)),
                ('description', models.TextField(null=True, blank=True)),
            ],
            options={
                'ordering': ['name'],
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='article_data',
            name='projects',
            field=models.ManyToManyField(to='sourcenet.Project'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='article_source',
            name='attribution_paragraph_number',
            field=models.IntegerField(default=0, null=True, blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='article_source',
            name='attribution_speaker_name_index_range',
            field=models.CharField(max_length=255, null=True, blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='article_source',
            name='attribution_speaker_name_string',
            field=models.TextField(null=True, blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='article_source',
            name='attribution_speaker_name_word_range',
            field=models.CharField(max_length=255, null=True, blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='article_source',
            name='attribution_verb_word_index',
            field=models.IntegerField(default=0, null=True, blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='article_source',
            name='attribution_verb_word_number',
            field=models.IntegerField(default=0, null=True, blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='article_source',
            name='capture_method',
            field=models.CharField(max_length=255, null=True, blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='article_source',
            name='is_speaker_name_pronoun',
            field=models.BooleanField(default=False),
            preserve_default=True,
        ),
    ]
