# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('sourcenet', '0013_auto_20150302_2352'),
    ]

    operations = [
        migrations.CreateModel(
            name='Article_Data_Notes',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('content_type', models.CharField(default='none', max_length=255, null=True, blank=True, choices=[('canonical', 'Canonical'), ('text', 'Text'), ('html', 'HTML'), ('json', 'JSON'), ('xml', 'XML'), ('other', 'Other'), ('none', 'None')])),
                ('content', models.TextField()),
                ('status', models.CharField(max_length=255, null=True, blank=True)),
                ('source', models.CharField(max_length=255, null=True, blank=True)),
                ('content_description', models.TextField(null=True, blank=True)),
                ('create_date', models.DateTimeField(auto_now_add=True)),
                ('last_modified', models.DateTimeField(auto_now=True)),
                ('article_data', models.ForeignKey(to='sourcenet.Article_Data')),
            ],
            options={
                'ordering': ['article_data', 'last_modified', 'create_date'],
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='article_notes',
            name='content_description',
            field=models.TextField(null=True, blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='article_notes',
            name='source',
            field=models.CharField(max_length=255, null=True, blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='article_rawdata',
            name='content_description',
            field=models.TextField(null=True, blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='article_rawdata',
            name='source',
            field=models.CharField(max_length=255, null=True, blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='article_text',
            name='content_description',
            field=models.TextField(null=True, blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='article_text',
            name='source',
            field=models.CharField(max_length=255, null=True, blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='article_notes',
            name='article',
            field=models.ForeignKey(to='sourcenet.Article'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='article_notes',
            name='content_type',
            field=models.CharField(default='none', max_length=255, null=True, blank=True, choices=[('canonical', 'Canonical'), ('text', 'Text'), ('html', 'HTML'), ('json', 'JSON'), ('xml', 'XML'), ('other', 'Other'), ('none', 'None')]),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='article_rawdata',
            name='content_type',
            field=models.CharField(default='none', max_length=255, null=True, blank=True, choices=[('canonical', 'Canonical'), ('text', 'Text'), ('html', 'HTML'), ('json', 'JSON'), ('xml', 'XML'), ('other', 'Other'), ('none', 'None')]),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='article_text',
            name='content_type',
            field=models.CharField(default='none', max_length=255, null=True, blank=True, choices=[('canonical', 'Canonical'), ('text', 'Text'), ('html', 'HTML'), ('json', 'JSON'), ('xml', 'XML'), ('other', 'Other'), ('none', 'None')]),
            preserve_default=True,
        ),
    ]
