# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('sourcenet', '0033_auto_20150611_0155'),
    ]

    operations = [
        migrations.CreateModel(
            name='Article_Subject',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('match_confidence_level', models.DecimalField(default=0.0, null=True, max_digits=11, decimal_places=10, blank=True)),
                ('capture_method', models.CharField(max_length=255, null=True, blank=True)),
                ('create_date', models.DateTimeField(auto_now_add=True)),
                ('last_modified', models.DateTimeField(auto_now=True)),
                ('source_type', models.CharField(blank=True, max_length=255, null=True, choices=[('anonymous', 'Anonymous/Unnamed'), ('individual', 'Individual Person'), ('organization', 'Organization'), ('document', 'Document'), ('other', 'Other')])),
                ('subject_type', models.CharField(blank=True, max_length=255, null=True, choices=[('mentioned', 'Subject Mentioned'), ('quoted', 'Source Quoted')])),
                ('title', models.CharField(max_length=255, null=True, blank=True)),
                ('more_title', models.CharField(max_length=255, null=True, blank=True)),
                ('source_contact_type', models.CharField(blank=True, max_length=255, null=True, choices=[('direct', 'Direct contact'), ('event', 'Press conference/event'), ('past_quotes', 'Past quotes/statements'), ('document', 'Press release/document'), ('other', 'Other')])),
                ('source_capacity', models.CharField(blank=True, max_length=255, null=True, choices=[('government', 'Government Source'), ('police', 'Police Source'), ('business', 'Business Source'), ('labor', 'Labor Source'), ('education', 'Education Source'), ('organization', 'Other Organization Source'), ('expert', 'Expert Opinion'), ('individual', 'Personal Opinion'), ('other', 'Other')])),
                ('localness', models.CharField(blank=True, max_length=255, null=True, choices=[('none', 'None'), ('local', 'Local'), ('state', 'State'), ('national', 'National'), ('international', 'International'), ('other', 'Other')])),
                ('notes', models.TextField(null=True, blank=True)),
                ('article_data', models.ForeignKey(to='sourcenet.Article_Data')),
                ('document', models.ForeignKey(blank=True, to='sourcenet.Document', null=True)),
                ('organization', models.ForeignKey(blank=True, to='sourcenet.Organization', null=True)),
                ('original_person', models.ForeignKey(related_name='sourcenet_article_subject_original_person_set', blank=True, to='sourcenet.Person', null=True)),
                ('person', models.ForeignKey(blank=True, to='sourcenet.Person', null=True)),
                ('topics', models.ManyToManyField(to='sourcenet.Topic', blank=True)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Article_Subject_Mention',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('value', models.TextField(null=True, blank=True)),
                ('value_in_context', models.TextField(null=True, blank=True)),
                ('value_index', models.IntegerField(default=0, null=True, blank=True)),
                ('value_length', models.IntegerField(default=0, null=True, blank=True)),
                ('canonical_index', models.IntegerField(default=0, null=True, blank=True)),
                ('value_word_number_start', models.IntegerField(default=0, null=True, blank=True)),
                ('value_word_number_end', models.IntegerField(default=0, null=True, blank=True)),
                ('paragraph_number', models.IntegerField(default=0, null=True, blank=True)),
                ('context_before', models.TextField(null=True, blank=True)),
                ('context_after', models.TextField(null=True, blank=True)),
                ('capture_method', models.CharField(max_length=255, null=True, blank=True)),
                ('uuid', models.TextField(null=True, blank=True)),
                ('uuid_name', models.CharField(max_length=255, null=True, blank=True)),
                ('notes', models.TextField(null=True, blank=True)),
                ('create_date', models.DateTimeField(auto_now_add=True)),
                ('last_modified', models.DateTimeField(auto_now=True)),
                ('is_speaker_name_pronoun', models.BooleanField(default=False)),
                ('article_subject', models.ForeignKey(blank=True, to='sourcenet.Article_Subject', null=True)),
            ],
            options={
                'ordering': ['paragraph_number', 'last_modified', 'create_date'],
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Article_Subject_Quotation',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('value', models.TextField(null=True, blank=True)),
                ('value_in_context', models.TextField(null=True, blank=True)),
                ('value_index', models.IntegerField(default=0, null=True, blank=True)),
                ('value_length', models.IntegerField(default=0, null=True, blank=True)),
                ('canonical_index', models.IntegerField(default=0, null=True, blank=True)),
                ('value_word_number_start', models.IntegerField(default=0, null=True, blank=True)),
                ('value_word_number_end', models.IntegerField(default=0, null=True, blank=True)),
                ('paragraph_number', models.IntegerField(default=0, null=True, blank=True)),
                ('context_before', models.TextField(null=True, blank=True)),
                ('context_after', models.TextField(null=True, blank=True)),
                ('capture_method', models.CharField(max_length=255, null=True, blank=True)),
                ('uuid', models.TextField(null=True, blank=True)),
                ('uuid_name', models.CharField(max_length=255, null=True, blank=True)),
                ('notes', models.TextField(null=True, blank=True)),
                ('create_date', models.DateTimeField(auto_now_add=True)),
                ('last_modified', models.DateTimeField(auto_now=True)),
                ('value_with_attribution', models.TextField(null=True, blank=True)),
                ('attribution_verb_word_index', models.IntegerField(default=0, null=True, blank=True)),
                ('attribution_verb_word_number', models.IntegerField(default=0, null=True, blank=True)),
                ('attribution_paragraph_number', models.IntegerField(default=0, null=True, blank=True)),
                ('attribution_speaker_name_string', models.TextField(null=True, blank=True)),
                ('is_speaker_name_pronoun', models.BooleanField(default=False)),
                ('attribution_speaker_name_index_range', models.CharField(max_length=255, null=True, blank=True)),
                ('attribution_speaker_name_word_range', models.CharField(max_length=255, null=True, blank=True)),
                ('article_subject', models.ForeignKey(blank=True, to='sourcenet.Article_Subject', null=True)),
            ],
            options={
                'ordering': ['paragraph_number', 'last_modified', 'create_date'],
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Subject_Organization',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('title', models.CharField(max_length=255, blank=True)),
                ('article_subject', models.ForeignKey(to='sourcenet.Article_Subject')),
                ('organization', models.ForeignKey(blank=True, to='sourcenet.Organization', null=True)),
            ],
        ),
        migrations.RenameModel(
            old_name='Alternate_Source_Match',
            new_name='Alternate_Subject_Match',
        ),
        migrations.RemoveField(
            model_name='article_source',
            name='article_data',
        ),
        migrations.RemoveField(
            model_name='article_source',
            name='document',
        ),
        migrations.RemoveField(
            model_name='article_source',
            name='organization',
        ),
        migrations.RemoveField(
            model_name='article_source',
            name='original_person',
        ),
        migrations.RemoveField(
            model_name='article_source',
            name='person',
        ),
        migrations.RemoveField(
            model_name='article_source',
            name='topics',
        ),
        migrations.RemoveField(
            model_name='article_source_mention',
            name='article_source',
        ),
        migrations.RemoveField(
            model_name='article_source_quotation',
            name='article_source',
        ),
        migrations.RemoveField(
            model_name='source_organization',
            name='article_source',
        ),
        migrations.RemoveField(
            model_name='source_organization',
            name='organization',
        ),
        migrations.RemoveField(
            model_name='alternate_subject_match',
            name='article_source',
        ),
        migrations.DeleteModel(
            name='Article_Source',
        ),
        migrations.DeleteModel(
            name='Article_Source_Mention',
        ),
        migrations.DeleteModel(
            name='Article_Source_Quotation',
        ),
        migrations.DeleteModel(
            name='Source_Organization',
        ),
        migrations.AddField(
            model_name='alternate_subject_match',
            name='article_subject',
            field=models.ForeignKey(blank=True, to='sourcenet.Article_Subject', null=True),
        ),
    ]
