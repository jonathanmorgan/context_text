# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('sourcenet', '0011_auto_20150301_1211'),
    ]

    operations = [
        migrations.CreateModel(
            name='Alternate_Author_Match',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('article_author', models.ForeignKey(blank=True, to='sourcenet.Article_Author', null=True)),
                ('person', models.ForeignKey(blank=True, to='sourcenet.Person', null=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Alternate_Source_Match',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('article_source', models.ForeignKey(blank=True, to='sourcenet.Article_Source', null=True)),
                ('person', models.ForeignKey(blank=True, to='sourcenet.Person', null=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
    ]
