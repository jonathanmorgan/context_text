# -*- coding: utf-8 -*-
# Generated by Django 1.9.2 on 2016-02-10 22:11
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('context_text', '0006_auto_20160209_2322'),
    ]

    operations = [
        migrations.AddField(
            model_name='alternate_name',
            name='more_organization',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='alternate_name',
            name='more_title',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='alternate_name',
            name='organization_string',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
        migrations.AddField(
            model_name='person',
            name='more_organization',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='person',
            name='more_title',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='person',
            name='organization_string',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
    ]
