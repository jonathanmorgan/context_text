# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import datetime


class Migration(migrations.Migration):

    dependencies = [
        ('sourcenet', '0015_auto_20150303_2313'),
    ]

    operations = [
        migrations.CreateModel(
            name='Article_Source_Mention',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('value', models.TextField(null=True, blank=True)),
                ('value_in_context', models.TextField(null=True, blank=True)),
                ('value_length', models.IntegerField(default=0, null=True, blank=True)),
                ('value_index', models.IntegerField(default=0, null=True, blank=True)),
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
                ('article_source', models.ForeignKey(blank=True, to='sourcenet.Article_Source', null=True)),
            ],
            options={
                'ordering': ['last_modified', 'create_date'],
                'abstract': False,
            },
            bases=(models.Model,),
        ),
        migrations.AlterModelOptions(
            name='article_source_quotation',
            options={'ordering': ['last_modified', 'create_date']},
        ),
        migrations.RenameField(
            model_name='article_source_quotation',
            old_name='quotation',
            new_name='value',
        ),
        migrations.AddField(
            model_name='article_source_quotation',
            name='canonical_index',
            field=models.IntegerField(default=0, null=True, blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='article_source_quotation',
            name='context_after',
            field=models.TextField(null=True, blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='article_source_quotation',
            name='context_before',
            field=models.TextField(null=True, blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='article_source_quotation',
            name='create_date',
            field=models.DateTimeField(default=datetime.datetime(2015, 3, 5, 23, 37, 45, 351052), auto_now_add=True),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='article_source_quotation',
            name='last_modified',
            field=models.DateTimeField(default=datetime.datetime(2015, 3, 5, 23, 37, 54, 932507), auto_now=True),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='article_source_quotation',
            name='paragraph_number',
            field=models.IntegerField(default=0, null=True, blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='article_source_quotation',
            name='value_in_context',
            field=models.TextField(null=True, blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='article_source_quotation',
            name='value_index',
            field=models.IntegerField(default=0, null=True, blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='article_source_quotation',
            name='value_length',
            field=models.IntegerField(default=0, null=True, blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='article_source_quotation',
            name='value_word_number_end',
            field=models.IntegerField(default=0, null=True, blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='article_source_quotation',
            name='value_word_number_start',
            field=models.IntegerField(default=0, null=True, blank=True),
            preserve_default=True,
        ),
    ]
