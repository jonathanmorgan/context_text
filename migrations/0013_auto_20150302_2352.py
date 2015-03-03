# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('sourcenet', '0012_alternate_author_match_alternate_source_match'),
    ]

    operations = [
        migrations.CreateModel(
            name='Article_Source_Quotation',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('quotation', models.TextField(null=True, blank=True)),
                ('attribution_verb_word_index', models.IntegerField(default=0, null=True, blank=True)),
                ('attribution_verb_word_number', models.IntegerField(default=0, null=True, blank=True)),
                ('attribution_paragraph_number', models.IntegerField(default=0, null=True, blank=True)),
                ('attribution_speaker_name_string', models.TextField(null=True, blank=True)),
                ('is_speaker_name_pronoun', models.BooleanField(default=False)),
                ('attribution_speaker_name_index_range', models.CharField(max_length=255, null=True, blank=True)),
                ('attribution_speaker_name_word_range', models.CharField(max_length=255, null=True, blank=True)),
                ('capture_method', models.CharField(max_length=255, null=True, blank=True)),
                ('notes', models.TextField(null=True, blank=True)),
                ('article_source', models.ForeignKey(blank=True, to='sourcenet.Article_Source', null=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.RemoveField(
            model_name='article_source',
            name='attribution_paragraph_number',
        ),
        migrations.RemoveField(
            model_name='article_source',
            name='attribution_speaker_name_index_range',
        ),
        migrations.RemoveField(
            model_name='article_source',
            name='attribution_speaker_name_string',
        ),
        migrations.RemoveField(
            model_name='article_source',
            name='attribution_speaker_name_word_range',
        ),
        migrations.RemoveField(
            model_name='article_source',
            name='attribution_verb_word_index',
        ),
        migrations.RemoveField(
            model_name='article_source',
            name='attribution_verb_word_number',
        ),
        migrations.RemoveField(
            model_name='article_source',
            name='is_speaker_name_pronoun',
        ),
    ]
