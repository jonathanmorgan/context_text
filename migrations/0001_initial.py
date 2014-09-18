# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings
from decimal import Decimal


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Article',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('unique_identifier', models.CharField(max_length=255, blank=True)),
                ('source_string', models.CharField(max_length=255, null=True, blank=True)),
                ('pub_date', models.DateField()),
                ('section', models.CharField(max_length=255, blank=True)),
                ('page', models.CharField(max_length=255, null=True, blank=True)),
                ('author_string', models.TextField(null=True, blank=True)),
                ('author_varchar', models.CharField(max_length=255, null=True, blank=True)),
                ('headline', models.CharField(max_length=255)),
                ('corrections', models.TextField(null=True, blank=True)),
                ('edition', models.CharField(max_length=255, null=True, blank=True)),
                ('index_terms', models.TextField(null=True, blank=True)),
                ('archive_source', models.CharField(max_length=255, null=True, blank=True)),
                ('archive_id', models.CharField(max_length=255, null=True, blank=True)),
                ('permalink', models.TextField(null=True, blank=True)),
                ('copyright', models.TextField(null=True, blank=True)),
                ('status', models.CharField(default='new', max_length=255, null=True, blank=True)),
                ('is_local_news', models.BooleanField(default=0)),
                ('is_sports', models.BooleanField(default=0)),
                ('is_local_author', models.BooleanField(default=0)),
                ('create_date', models.DateTimeField(auto_now_add=True)),
                ('last_modified', models.DateTimeField(auto_now=True)),
            ],
            options={
                'ordering': ['pub_date', 'section', 'page'],
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Article_Author',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('author_type', models.CharField(default='staff', max_length=255, null=True, blank=True, choices=[('staff', 'News Staff'), ('editorial', 'Editorial Staff'), ('government', 'Government Official'), ('business', 'Business Representative'), ('organization', 'Other Organization Representative'), ('public', 'Member of the Public'), ('other', 'Other')])),
                ('organization_string', models.CharField(max_length=255, null=True, blank=True)),
            ],
            options={
                'abstract': False,
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Article_Data',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('article_type', models.CharField(default='news', max_length=255, blank=True, choices=[('news', 'News'), ('sports', 'Sports'), ('feature', 'Feature'), ('opinion', 'Opinion'), ('other', 'Other')])),
                ('is_sourced', models.BooleanField(default=True)),
                ('can_code', models.BooleanField(default=True)),
                ('status', models.CharField(default='new', max_length=255, null=True, blank=True)),
                ('create_date', models.DateTimeField(auto_now_add=True)),
                ('last_modified', models.DateTimeField(auto_now=True)),
                ('article', models.ForeignKey(to='sourcenet.Article')),
                ('coder', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ['article', 'last_modified', 'create_date'],
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Article_Notes',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('type', models.CharField(default='none', max_length=255, null=True, blank=True, choices=[('html', 'HTML'), ('text', 'Text'), ('other', 'Other'), ('none', 'None')])),
                ('content', models.TextField()),
                ('create_date', models.DateTimeField(auto_now_add=True)),
                ('last_modified', models.DateTimeField(auto_now=True)),
                ('article', models.ForeignKey(to='sourcenet.Article', unique=True)),
            ],
            options={
                'ordering': ['article', 'last_modified', 'create_date'],
                'abstract': False,
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Article_RawData',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('type', models.CharField(default='none', max_length=255, null=True, blank=True, choices=[('html', 'HTML'), ('text', 'Text'), ('other', 'Other'), ('none', 'None')])),
                ('content', models.TextField()),
                ('create_date', models.DateTimeField(auto_now_add=True)),
                ('last_modified', models.DateTimeField(auto_now=True)),
                ('article', models.ForeignKey(to='sourcenet.Article', unique=True)),
            ],
            options={
                'ordering': ['article', 'last_modified', 'create_date'],
                'abstract': False,
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Article_Source',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('source_type', models.CharField(blank=True, max_length=255, null=True, choices=[('anonymous', 'Anonymous/Unnamed'), ('individual', 'Individual Person'), ('organization', 'Organization'), ('document', 'Document'), ('other', 'Other')])),
                ('title', models.CharField(max_length=255, null=True, blank=True)),
                ('more_title', models.CharField(max_length=255, null=True, blank=True)),
                ('source_contact_type', models.CharField(blank=True, max_length=255, null=True, choices=[('direct', 'Direct contact'), ('event', 'Press conference/event'), ('past_quotes', 'Past quotes/statements'), ('document', 'Press release/document'), ('other', 'Other')])),
                ('source_capacity', models.CharField(blank=True, max_length=255, null=True, choices=[('government', 'Government Source'), ('police', 'Police Source'), ('business', 'Business Source'), ('labor', 'Labor Source'), ('education', 'Education Source'), ('organization', 'Other Organization Source'), ('expert', 'Expert Opinion'), ('individual', 'Personal Opinion'), ('other', 'Other')])),
                ('localness', models.CharField(blank=True, max_length=255, null=True, choices=[('none', 'None'), ('local', 'Local'), ('state', 'State'), ('national', 'National'), ('international', 'International'), ('other', 'Other')])),
                ('notes', models.TextField(null=True, blank=True)),
                ('article_data', models.ForeignKey(to='sourcenet.Article_Data')),
            ],
            options={
                'abstract': False,
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Article_Text',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('type', models.CharField(default='none', max_length=255, null=True, blank=True, choices=[('html', 'HTML'), ('text', 'Text'), ('other', 'Other'), ('none', 'None')])),
                ('content', models.TextField()),
                ('create_date', models.DateTimeField(auto_now_add=True)),
                ('last_modified', models.DateTimeField(auto_now=True)),
                ('article', models.ForeignKey(to='sourcenet.Article', unique=True)),
            ],
            options={
                'ordering': ['article', 'last_modified', 'create_date'],
                'abstract': False,
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Articles_To_Migrate',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('unique_identifier', models.CharField(max_length=255, blank=True)),
                ('pub_date', models.DateField()),
                ('section', models.CharField(max_length=255, blank=True)),
                ('page', models.IntegerField(blank=True)),
                ('headline', models.CharField(max_length=255)),
                ('text', models.TextField(blank=True)),
                ('is_sourced', models.BooleanField(default=True)),
                ('can_code', models.BooleanField(default=True)),
                ('article_type', models.CharField(default='news', max_length=255, blank=True, choices=[('news', 'News'), ('sports', 'Sports'), ('feature', 'Feature'), ('opinion', 'Opinion'), ('other', 'Other')])),
                ('article', models.ForeignKey(blank=True, to='sourcenet.Article', null=True)),
                ('coder', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ['pub_date', 'section', 'page'],
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Document',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=255)),
                ('description', models.TextField(blank=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Import_Error',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('unique_identifier', models.CharField(max_length=255, blank=True)),
                ('archive_source', models.CharField(max_length=255, null=True, blank=True)),
                ('item', models.TextField(null=True, blank=True)),
                ('message', models.TextField(null=True, blank=True)),
                ('exception', models.TextField(null=True, blank=True)),
                ('stack_trace', models.TextField(null=True, blank=True)),
                ('batch_identifier', models.CharField(max_length=255, blank=True)),
                ('item_date', models.DateTimeField(null=True, blank=True)),
                ('status', models.CharField(default='new', max_length=255, null=True, blank=True)),
                ('create_date', models.DateTimeField(auto_now_add=True)),
                ('last_modified', models.DateTimeField(auto_now=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Location',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=255, blank=True)),
                ('description', models.TextField(blank=True)),
                ('address', models.CharField(max_length=255, blank=True)),
                ('city', models.CharField(max_length=255, blank=True)),
                ('county', models.CharField(max_length=255, blank=True)),
                ('state', models.CharField(blank=True, max_length=2, choices=[('AL', 'Alabama'), ('AK', 'Alaska'), ('AS', 'American Samoa'), ('AZ', 'Arizona'), ('AR', 'Arkansas'), ('CA', 'California'), ('CO', 'Colorado'), ('CT', 'Connecticut'), ('DE', 'Delaware'), ('DC', 'District of Columbia'), ('FM', 'Federated States of Micronesia'), ('FL', 'Florida'), ('GA', 'Georgia'), ('GU', 'Guam'), ('HI', 'Hawaii'), ('ID', 'Idaho'), ('IL', 'Illinois'), ('IN', 'Indiana'), ('IA', 'Iowa'), ('KS', 'Kansas'), ('KY', 'Kentucky'), ('LA', 'Louisiana'), ('ME', 'Maine'), ('MH', 'Marshall Islands'), ('MD', 'Maryland'), ('MA', 'Massachusetts'), ('MI', 'Michigan'), ('MN', 'Minnesota'), ('MS', 'Mississippi'), ('MO', 'Missouri'), ('MT', 'Montana'), ('NE', 'Nebraska'), ('NV', 'Nevada'), ('NH', 'New Hampshire'), ('NJ', 'New Jersey'), ('NM', 'New Mexico'), ('NY', 'New York'), ('NC', 'North Carolina'), ('ND', 'North Dakota'), ('MP', 'Northern Mariana Islands'), ('OH', 'Ohio'), ('OK', 'Oklahoma'), ('OR', 'Oregon'), ('PW', 'Palau'), ('PA', 'Pennsylvania'), ('PR', 'Puerto Rico'), ('RI', 'Rhode Island'), ('SC', 'South Carolina'), ('SD', 'South Dakota'), ('TN', 'Tennessee'), ('TX', 'Texasv'), ('UT', 'Utah'), ('VT', 'Vermont'), ('VI', 'Virgin Islands'), ('VA', 'Virginia'), ('WA', 'Washington'), ('WV', 'West Virginia'), ('WI', 'Wisconsin'), ('WY', 'Wyoming')])),
                ('zip_code', models.CharField(max_length=10, verbose_name='ZIP Code', blank=True)),
            ],
            options={
                'ordering': ['name', 'city', 'county', 'state', 'zip_code'],
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Newspaper',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=255)),
                ('description', models.TextField(blank=True)),
                ('newsbank_code', models.CharField(max_length=255, null=True, blank=True)),
                ('sections_local_news', models.TextField(null=True, blank=True)),
                ('sections_sports', models.TextField(null=True, blank=True)),
            ],
            options={
                'ordering': ['name'],
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Organization',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=255)),
                ('description', models.TextField(blank=True)),
                ('location', models.ForeignKey(blank=True, to='sourcenet.Location', null=True)),
            ],
            options={
                'ordering': ['name', 'location'],
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Person',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('first_name', models.CharField(max_length=255)),
                ('middle_name', models.CharField(max_length=255, blank=True)),
                ('last_name', models.CharField(max_length=255)),
                ('name_prefix', models.CharField(max_length=255, null=True, blank=True)),
                ('name_suffix', models.CharField(max_length=255, null=True, blank=True)),
                ('full_name_string', models.CharField(max_length=255, null=True, blank=True)),
                ('gender', models.CharField(max_length=6, choices=[('na', 'Unknown'), ('female', 'Female'), ('male', 'Male')])),
                ('title', models.CharField(max_length=255, blank=True)),
                ('nameparser_pickled', models.TextField(null=True, blank=True)),
                ('is_ambiguous', models.BooleanField(default=False)),
                ('notes', models.TextField(blank=True)),
            ],
            options={
                'ordering': ['last_name', 'first_name', 'middle_name'],
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Person_Organization',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('title', models.CharField(max_length=255, blank=True)),
                ('organization', models.ForeignKey(blank=True, to='sourcenet.Organization', null=True)),
                ('person', models.ForeignKey(to='sourcenet.Person')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Source_Organization',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('title', models.CharField(max_length=255, blank=True)),
                ('article_source', models.ForeignKey(to='sourcenet.Article_Source')),
                ('organization', models.ForeignKey(blank=True, to='sourcenet.Organization', null=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Temp_Section',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=255, null=True, blank=True)),
                ('total_days', models.IntegerField(default=0, null=True, blank=True)),
                ('total_articles', models.IntegerField(default=0, null=True, blank=True)),
                ('in_house_articles', models.IntegerField(default=0, null=True, blank=True)),
                ('external_articles', models.IntegerField(default=0, null=True, blank=True)),
                ('external_booth', models.IntegerField(default=0, null=True, blank=True)),
                ('total_pages', models.IntegerField(default=0, null=True, blank=True)),
                ('in_house_pages', models.IntegerField(default=0, null=True, blank=True)),
                ('in_house_authors', models.IntegerField(default=0, null=True, blank=True)),
                ('percent_in_house', models.DecimalField(default=Decimal('0'), null=True, max_digits=21, decimal_places=20, blank=True)),
                ('percent_external', models.DecimalField(default=Decimal('0'), null=True, max_digits=21, decimal_places=20, blank=True)),
                ('average_articles_per_day', models.DecimalField(default=Decimal('0'), null=True, max_digits=25, decimal_places=20, blank=True)),
                ('average_pages_per_day', models.DecimalField(default=Decimal('0'), null=True, max_digits=25, decimal_places=20, blank=True)),
                ('average_in_house_articles_per_day', models.DecimalField(default=Decimal('0'), null=True, max_digits=25, decimal_places=20, blank=True)),
                ('average_in_house_pages_per_day', models.DecimalField(default=Decimal('0'), null=True, max_digits=25, decimal_places=20, blank=True)),
                ('start_date', models.DateTimeField(null=True, blank=True)),
                ('end_date', models.DateTimeField(null=True, blank=True)),
                ('create_date', models.DateTimeField(auto_now_add=True)),
                ('last_modified', models.DateTimeField(auto_now=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Topic',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=255)),
                ('description', models.TextField(blank=True)),
                ('last_modified', models.DateField(auto_now=True)),
            ],
            options={
                'ordering': ['name'],
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='newspaper',
            name='organization',
            field=models.ForeignKey(to='sourcenet.Organization'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='document',
            name='organization',
            field=models.ForeignKey(blank=True, to='sourcenet.Organization', null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='articles_to_migrate',
            name='newspaper',
            field=models.ForeignKey(blank=True, to='sourcenet.Newspaper', null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='article_source',
            name='document',
            field=models.ForeignKey(blank=True, to='sourcenet.Document', null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='article_source',
            name='organization',
            field=models.ForeignKey(blank=True, to='sourcenet.Organization', null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='article_source',
            name='person',
            field=models.ForeignKey(blank=True, to='sourcenet.Person', null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='article_source',
            name='topics',
            field=models.ManyToManyField(to='sourcenet.Topic', null=True, blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='article_data',
            name='locations',
            field=models.ManyToManyField(to='sourcenet.Location', blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='article_data',
            name='topics',
            field=models.ManyToManyField(to='sourcenet.Topic', null=True, blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='article_author',
            name='article_data',
            field=models.ForeignKey(to='sourcenet.Article_Data'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='article_author',
            name='person',
            field=models.ForeignKey(blank=True, to='sourcenet.Person', null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='article',
            name='newspaper',
            field=models.ForeignKey(blank=True, to='sourcenet.Newspaper', null=True),
            preserve_default=True,
        ),
    ]
