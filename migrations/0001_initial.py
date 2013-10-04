# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Location'
        db.create_table(u'sourcenet_location', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=255, blank=True)),
            ('description', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('address', self.gf('django.db.models.fields.CharField')(max_length=255, blank=True)),
            ('city', self.gf('django.db.models.fields.CharField')(max_length=255, blank=True)),
            ('county', self.gf('django.db.models.fields.CharField')(max_length=255, blank=True)),
            ('state', self.gf('django.db.models.fields.CharField')(max_length=2, blank=True)),
            ('zip_code', self.gf('django.db.models.fields.CharField')(max_length=10, blank=True)),
        ))
        db.send_create_signal(u'sourcenet', ['Location'])

        # Adding model 'Topic'
        db.create_table(u'sourcenet_topic', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('description', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('last_modified', self.gf('django.db.models.fields.DateField')(auto_now=True, blank=True)),
        ))
        db.send_create_signal(u'sourcenet', ['Topic'])

        # Adding model 'Person'
        db.create_table(u'sourcenet_person', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('first_name', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('middle_name', self.gf('django.db.models.fields.CharField')(max_length=255, blank=True)),
            ('last_name', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('name_prefix', self.gf('django.db.models.fields.CharField')(max_length=255, null=True, blank=True)),
            ('name_suffix', self.gf('django.db.models.fields.CharField')(max_length=255, null=True, blank=True)),
            ('full_name_string', self.gf('django.db.models.fields.CharField')(max_length=255, null=True, blank=True)),
            ('gender', self.gf('django.db.models.fields.CharField')(max_length=6)),
            ('title', self.gf('django.db.models.fields.CharField')(max_length=255, blank=True)),
            ('nameparser_pickled', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('notes', self.gf('django.db.models.fields.TextField')(blank=True)),
        ))
        db.send_create_signal(u'sourcenet', ['Person'])

        # Adding model 'Organization'
        db.create_table(u'sourcenet_organization', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('description', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('location', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['sourcenet.Location'], null=True, blank=True)),
        ))
        db.send_create_signal(u'sourcenet', ['Organization'])

        # Adding model 'Person_Organization'
        db.create_table(u'sourcenet_person_organization', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('person', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['sourcenet.Person'])),
            ('organization', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['sourcenet.Organization'], null=True, blank=True)),
            ('title', self.gf('django.db.models.fields.CharField')(max_length=255, blank=True)),
        ))
        db.send_create_signal(u'sourcenet', ['Person_Organization'])

        # Adding model 'Document'
        db.create_table(u'sourcenet_document', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('description', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('organization', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['sourcenet.Organization'], null=True, blank=True)),
        ))
        db.send_create_signal(u'sourcenet', ['Document'])

        # Adding model 'Newspaper'
        db.create_table(u'sourcenet_newspaper', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('description', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('organization', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['sourcenet.Organization'])),
            ('newsbank_code', self.gf('django.db.models.fields.CharField')(max_length=255, null=True, blank=True)),
            ('sections_local_news', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('sections_sports', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
        ))
        db.send_create_signal(u'sourcenet', ['Newspaper'])

        # Adding model 'Article'
        db.create_table(u'sourcenet_article', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('unique_identifier', self.gf('django.db.models.fields.CharField')(max_length=255, blank=True)),
            ('source_string', self.gf('django.db.models.fields.CharField')(max_length=255, null=True, blank=True)),
            ('newspaper', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['sourcenet.Newspaper'], null=True, blank=True)),
            ('pub_date', self.gf('django.db.models.fields.DateField')()),
            ('section', self.gf('django.db.models.fields.CharField')(max_length=255, blank=True)),
            ('page', self.gf('django.db.models.fields.CharField')(max_length=255, null=True, blank=True)),
            ('author_string', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('author_varchar', self.gf('django.db.models.fields.CharField')(max_length=255, null=True, blank=True)),
            ('headline', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('corrections', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('edition', self.gf('django.db.models.fields.CharField')(max_length=255, null=True, blank=True)),
            ('index_terms', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('archive_source', self.gf('django.db.models.fields.CharField')(max_length=255, null=True, blank=True)),
            ('archive_id', self.gf('django.db.models.fields.CharField')(max_length=255, null=True, blank=True)),
            ('permalink', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('copyright', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('status', self.gf('django.db.models.fields.CharField')(default='new', max_length=255, null=True, blank=True)),
            ('is_local_news', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('is_sports', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('is_local_author', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('create_date', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('last_modified', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, blank=True)),
        ))
        db.send_create_signal(u'sourcenet', ['Article'])

        # Adding model 'Article_Notes'
        db.create_table(u'sourcenet_article_notes', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('article', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['sourcenet.Article'], unique=True)),
            ('type', self.gf('django.db.models.fields.CharField')(default='none', max_length=255, null=True, blank=True)),
            ('content', self.gf('django.db.models.fields.TextField')()),
            ('create_date', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('last_modified', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, blank=True)),
        ))
        db.send_create_signal(u'sourcenet', ['Article_Notes'])

        # Adding model 'Article_RawData'
        db.create_table(u'sourcenet_article_rawdata', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('article', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['sourcenet.Article'], unique=True)),
            ('type', self.gf('django.db.models.fields.CharField')(default='none', max_length=255, null=True, blank=True)),
            ('content', self.gf('django.db.models.fields.TextField')()),
            ('create_date', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('last_modified', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, blank=True)),
        ))
        db.send_create_signal(u'sourcenet', ['Article_RawData'])

        # Adding model 'Article_Text'
        db.create_table(u'sourcenet_article_text', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('article', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['sourcenet.Article'], unique=True)),
            ('type', self.gf('django.db.models.fields.CharField')(default='none', max_length=255, null=True, blank=True)),
            ('content', self.gf('django.db.models.fields.TextField')()),
            ('create_date', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('last_modified', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, blank=True)),
        ))
        db.send_create_signal(u'sourcenet', ['Article_Text'])

        # Adding model 'Article_Data'
        db.create_table(u'sourcenet_article_data', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('article', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['sourcenet.Article'])),
            ('coder', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'])),
            ('article_type', self.gf('django.db.models.fields.CharField')(default='news', max_length=255, blank=True)),
            ('is_sourced', self.gf('django.db.models.fields.BooleanField')(default=True)),
            ('can_code', self.gf('django.db.models.fields.BooleanField')(default=True)),
            ('status', self.gf('django.db.models.fields.CharField')(default='new', max_length=255, null=True, blank=True)),
            ('create_date', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('last_modified', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, blank=True)),
        ))
        db.send_create_signal(u'sourcenet', ['Article_Data'])

        # Adding M2M table for field topics on 'Article_Data'
        m2m_table_name = db.shorten_name(u'sourcenet_article_data_topics')
        db.create_table(m2m_table_name, (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('article_data', models.ForeignKey(orm[u'sourcenet.article_data'], null=False)),
            ('topic', models.ForeignKey(orm[u'sourcenet.topic'], null=False))
        ))
        db.create_unique(m2m_table_name, ['article_data_id', 'topic_id'])

        # Adding M2M table for field locations on 'Article_Data'
        m2m_table_name = db.shorten_name(u'sourcenet_article_data_locations')
        db.create_table(m2m_table_name, (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('article_data', models.ForeignKey(orm[u'sourcenet.article_data'], null=False)),
            ('location', models.ForeignKey(orm[u'sourcenet.location'], null=False))
        ))
        db.create_unique(m2m_table_name, ['article_data_id', 'location_id'])

        # Adding model 'Article_Author'
        db.create_table(u'sourcenet_article_author', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('article_data', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['sourcenet.Article_Data'])),
            ('person', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['sourcenet.Person'], null=True, blank=True)),
            ('author_type', self.gf('django.db.models.fields.CharField')(default='staff', max_length=255, null=True, blank=True)),
            ('organization_string', self.gf('django.db.models.fields.CharField')(max_length=255, null=True, blank=True)),
        ))
        db.send_create_signal(u'sourcenet', ['Article_Author'])

        # Adding model 'Article_Source'
        db.create_table(u'sourcenet_article_source', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('article_data', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['sourcenet.Article_Data'])),
            ('person', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['sourcenet.Person'], null=True, blank=True)),
            ('source_type', self.gf('django.db.models.fields.CharField')(max_length=255, null=True, blank=True)),
            ('title', self.gf('django.db.models.fields.CharField')(max_length=255, null=True, blank=True)),
            ('more_title', self.gf('django.db.models.fields.CharField')(max_length=255, null=True, blank=True)),
            ('organization', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['sourcenet.Organization'], null=True, blank=True)),
            ('document', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['sourcenet.Document'], null=True, blank=True)),
            ('source_contact_type', self.gf('django.db.models.fields.CharField')(max_length=255, null=True, blank=True)),
            ('source_capacity', self.gf('django.db.models.fields.CharField')(max_length=255, null=True, blank=True)),
            ('localness', self.gf('django.db.models.fields.CharField')(max_length=255, null=True, blank=True)),
            ('notes', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
        ))
        db.send_create_signal(u'sourcenet', ['Article_Source'])

        # Adding M2M table for field topics on 'Article_Source'
        m2m_table_name = db.shorten_name(u'sourcenet_article_source_topics')
        db.create_table(m2m_table_name, (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('article_source', models.ForeignKey(orm[u'sourcenet.article_source'], null=False)),
            ('topic', models.ForeignKey(orm[u'sourcenet.topic'], null=False))
        ))
        db.create_unique(m2m_table_name, ['article_source_id', 'topic_id'])

        # Adding model 'Source_Organization'
        db.create_table(u'sourcenet_source_organization', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('article_source', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['sourcenet.Article_Source'])),
            ('organization', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['sourcenet.Organization'], null=True, blank=True)),
            ('title', self.gf('django.db.models.fields.CharField')(max_length=255, blank=True)),
        ))
        db.send_create_signal(u'sourcenet', ['Source_Organization'])

        # Adding model 'Import_Error'
        db.create_table(u'sourcenet_import_error', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('unique_identifier', self.gf('django.db.models.fields.CharField')(max_length=255, blank=True)),
            ('archive_source', self.gf('django.db.models.fields.CharField')(max_length=255, null=True, blank=True)),
            ('item', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('message', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('exception', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('stack_trace', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('batch_identifier', self.gf('django.db.models.fields.CharField')(max_length=255, blank=True)),
            ('item_date', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
            ('status', self.gf('django.db.models.fields.CharField')(default='new', max_length=255, null=True, blank=True)),
            ('create_date', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('last_modified', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, blank=True)),
        ))
        db.send_create_signal(u'sourcenet', ['Import_Error'])

        # Adding model 'Temp_Section'
        db.create_table(u'sourcenet_temp_section', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=255, null=True, blank=True)),
            ('total_days', self.gf('django.db.models.fields.IntegerField')(default=0, null=True, blank=True)),
            ('total_articles', self.gf('django.db.models.fields.IntegerField')(default=0, null=True, blank=True)),
            ('in_house_articles', self.gf('django.db.models.fields.IntegerField')(default=0, null=True, blank=True)),
            ('external_articles', self.gf('django.db.models.fields.IntegerField')(default=0, null=True, blank=True)),
            ('external_booth', self.gf('django.db.models.fields.IntegerField')(default=0, null=True, blank=True)),
            ('total_pages', self.gf('django.db.models.fields.IntegerField')(default=0, null=True, blank=True)),
            ('in_house_pages', self.gf('django.db.models.fields.IntegerField')(default=0, null=True, blank=True)),
            ('in_house_authors', self.gf('django.db.models.fields.IntegerField')(default=0, null=True, blank=True)),
            ('percent_in_house', self.gf('django.db.models.fields.DecimalField')(default='0', null=True, max_digits=21, decimal_places=20, blank=True)),
            ('percent_external', self.gf('django.db.models.fields.DecimalField')(default='0', null=True, max_digits=21, decimal_places=20, blank=True)),
            ('average_articles_per_day', self.gf('django.db.models.fields.DecimalField')(default='0', null=True, max_digits=25, decimal_places=20, blank=True)),
            ('average_pages_per_day', self.gf('django.db.models.fields.DecimalField')(default='0', null=True, max_digits=25, decimal_places=20, blank=True)),
            ('average_in_house_articles_per_day', self.gf('django.db.models.fields.DecimalField')(default='0', null=True, max_digits=25, decimal_places=20, blank=True)),
            ('average_in_house_pages_per_day', self.gf('django.db.models.fields.DecimalField')(default='0', null=True, max_digits=25, decimal_places=20, blank=True)),
            ('start_date', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
            ('end_date', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
            ('create_date', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('last_modified', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, blank=True)),
        ))
        db.send_create_signal(u'sourcenet', ['Temp_Section'])


    def backwards(self, orm):
        # Deleting model 'Location'
        db.delete_table(u'sourcenet_location')

        # Deleting model 'Topic'
        db.delete_table(u'sourcenet_topic')

        # Deleting model 'Person'
        db.delete_table(u'sourcenet_person')

        # Deleting model 'Organization'
        db.delete_table(u'sourcenet_organization')

        # Deleting model 'Person_Organization'
        db.delete_table(u'sourcenet_person_organization')

        # Deleting model 'Document'
        db.delete_table(u'sourcenet_document')

        # Deleting model 'Newspaper'
        db.delete_table(u'sourcenet_newspaper')

        # Deleting model 'Article'
        db.delete_table(u'sourcenet_article')

        # Deleting model 'Article_Notes'
        db.delete_table(u'sourcenet_article_notes')

        # Deleting model 'Article_RawData'
        db.delete_table(u'sourcenet_article_rawdata')

        # Deleting model 'Article_Text'
        db.delete_table(u'sourcenet_article_text')

        # Deleting model 'Article_Data'
        db.delete_table(u'sourcenet_article_data')

        # Removing M2M table for field topics on 'Article_Data'
        db.delete_table(db.shorten_name(u'sourcenet_article_data_topics'))

        # Removing M2M table for field locations on 'Article_Data'
        db.delete_table(db.shorten_name(u'sourcenet_article_data_locations'))

        # Deleting model 'Article_Author'
        db.delete_table(u'sourcenet_article_author')

        # Deleting model 'Article_Source'
        db.delete_table(u'sourcenet_article_source')

        # Removing M2M table for field topics on 'Article_Source'
        db.delete_table(db.shorten_name(u'sourcenet_article_source_topics'))

        # Deleting model 'Source_Organization'
        db.delete_table(u'sourcenet_source_organization')

        # Deleting model 'Import_Error'
        db.delete_table(u'sourcenet_import_error')

        # Deleting model 'Temp_Section'
        db.delete_table(u'sourcenet_temp_section')


    models = {
        u'auth.group': {
            'Meta': {'object_name': 'Group'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '80'}),
            'permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'})
        },
        u'auth.permission': {
            'Meta': {'ordering': "(u'content_type__app_label', u'content_type__model', u'codename')", 'unique_together': "((u'content_type', u'codename'),)", 'object_name': 'Permission'},
            'codename': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['contenttypes.ContentType']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        u'auth.user': {
            'Meta': {'object_name': 'User'},
            'date_joined': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['auth.Group']", 'symmetrical': 'False', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_staff': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_superuser': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'user_permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'}),
            'username': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '30'})
        },
        u'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        u'sourcenet.article': {
            'Meta': {'ordering': "['pub_date', 'section', 'page']", 'object_name': 'Article'},
            'archive_id': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'archive_source': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'author_string': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'author_varchar': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'copyright': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'corrections': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'create_date': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'edition': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'headline': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'index_terms': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'is_local_author': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_local_news': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_sports': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'last_modified': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'newspaper': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['sourcenet.Newspaper']", 'null': 'True', 'blank': 'True'}),
            'page': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'permalink': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'pub_date': ('django.db.models.fields.DateField', [], {}),
            'section': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'source_string': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'status': ('django.db.models.fields.CharField', [], {'default': "'new'", 'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'unique_identifier': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'})
        },
        u'sourcenet.article_author': {
            'Meta': {'object_name': 'Article_Author'},
            'article_data': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['sourcenet.Article_Data']"}),
            'author_type': ('django.db.models.fields.CharField', [], {'default': "'staff'", 'max_length': '255', 'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'organization_string': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'person': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['sourcenet.Person']", 'null': 'True', 'blank': 'True'})
        },
        u'sourcenet.article_data': {
            'Meta': {'ordering': "['article', 'last_modified', 'create_date']", 'object_name': 'Article_Data'},
            'article': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['sourcenet.Article']"}),
            'article_type': ('django.db.models.fields.CharField', [], {'default': "'news'", 'max_length': '255', 'blank': 'True'}),
            'can_code': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'coder': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['auth.User']"}),
            'create_date': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_sourced': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'last_modified': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'locations': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['sourcenet.Location']", 'symmetrical': 'False', 'blank': 'True'}),
            'status': ('django.db.models.fields.CharField', [], {'default': "'new'", 'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'topics': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'to': u"orm['sourcenet.Topic']", 'null': 'True', 'blank': 'True'})
        },
        u'sourcenet.article_notes': {
            'Meta': {'ordering': "['article', 'last_modified', 'create_date']", 'object_name': 'Article_Notes'},
            'article': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['sourcenet.Article']", 'unique': 'True'}),
            'content': ('django.db.models.fields.TextField', [], {}),
            'create_date': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'last_modified': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'type': ('django.db.models.fields.CharField', [], {'default': "'none'", 'max_length': '255', 'null': 'True', 'blank': 'True'})
        },
        u'sourcenet.article_rawdata': {
            'Meta': {'ordering': "['article', 'last_modified', 'create_date']", 'object_name': 'Article_RawData'},
            'article': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['sourcenet.Article']", 'unique': 'True'}),
            'content': ('django.db.models.fields.TextField', [], {}),
            'create_date': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'last_modified': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'type': ('django.db.models.fields.CharField', [], {'default': "'none'", 'max_length': '255', 'null': 'True', 'blank': 'True'})
        },
        u'sourcenet.article_source': {
            'Meta': {'object_name': 'Article_Source'},
            'article_data': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['sourcenet.Article_Data']"}),
            'document': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['sourcenet.Document']", 'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'localness': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'more_title': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'notes': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'organization': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['sourcenet.Organization']", 'null': 'True', 'blank': 'True'}),
            'person': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['sourcenet.Person']", 'null': 'True', 'blank': 'True'}),
            'source_capacity': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'source_contact_type': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'source_type': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'topics': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'to': u"orm['sourcenet.Topic']", 'null': 'True', 'blank': 'True'})
        },
        u'sourcenet.article_text': {
            'Meta': {'ordering': "['article', 'last_modified', 'create_date']", 'object_name': 'Article_Text'},
            'article': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['sourcenet.Article']", 'unique': 'True'}),
            'content': ('django.db.models.fields.TextField', [], {}),
            'create_date': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'last_modified': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'type': ('django.db.models.fields.CharField', [], {'default': "'none'", 'max_length': '255', 'null': 'True', 'blank': 'True'})
        },
        u'sourcenet.document': {
            'Meta': {'object_name': 'Document'},
            'description': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'organization': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['sourcenet.Organization']", 'null': 'True', 'blank': 'True'})
        },
        u'sourcenet.import_error': {
            'Meta': {'object_name': 'Import_Error'},
            'archive_source': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'batch_identifier': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'create_date': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'exception': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'item': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'item_date': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'last_modified': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'message': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'stack_trace': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'status': ('django.db.models.fields.CharField', [], {'default': "'new'", 'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'unique_identifier': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'})
        },
        u'sourcenet.location': {
            'Meta': {'ordering': "['name', 'city', 'county', 'state', 'zip_code']", 'object_name': 'Location'},
            'address': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'city': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'county': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'description': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'state': ('django.db.models.fields.CharField', [], {'max_length': '2', 'blank': 'True'}),
            'zip_code': ('django.db.models.fields.CharField', [], {'max_length': '10', 'blank': 'True'})
        },
        u'sourcenet.newspaper': {
            'Meta': {'ordering': "['name']", 'object_name': 'Newspaper'},
            'description': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'newsbank_code': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'organization': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['sourcenet.Organization']"}),
            'sections_local_news': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'sections_sports': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'})
        },
        u'sourcenet.organization': {
            'Meta': {'ordering': "['name', 'location']", 'object_name': 'Organization'},
            'description': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'location': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['sourcenet.Location']", 'null': 'True', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'})
        },
        u'sourcenet.person': {
            'Meta': {'ordering': "['last_name', 'first_name', 'middle_name']", 'object_name': 'Person'},
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'full_name_string': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'gender': ('django.db.models.fields.CharField', [], {'max_length': '6'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'middle_name': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'name_prefix': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'name_suffix': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'nameparser_pickled': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'notes': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'})
        },
        u'sourcenet.person_organization': {
            'Meta': {'object_name': 'Person_Organization'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'organization': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['sourcenet.Organization']", 'null': 'True', 'blank': 'True'}),
            'person': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['sourcenet.Person']"}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'})
        },
        u'sourcenet.source_organization': {
            'Meta': {'object_name': 'Source_Organization'},
            'article_source': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['sourcenet.Article_Source']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'organization': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['sourcenet.Organization']", 'null': 'True', 'blank': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'})
        },
        u'sourcenet.temp_section': {
            'Meta': {'object_name': 'Temp_Section'},
            'average_articles_per_day': ('django.db.models.fields.DecimalField', [], {'default': "'0'", 'null': 'True', 'max_digits': '25', 'decimal_places': '20', 'blank': 'True'}),
            'average_in_house_articles_per_day': ('django.db.models.fields.DecimalField', [], {'default': "'0'", 'null': 'True', 'max_digits': '25', 'decimal_places': '20', 'blank': 'True'}),
            'average_in_house_pages_per_day': ('django.db.models.fields.DecimalField', [], {'default': "'0'", 'null': 'True', 'max_digits': '25', 'decimal_places': '20', 'blank': 'True'}),
            'average_pages_per_day': ('django.db.models.fields.DecimalField', [], {'default': "'0'", 'null': 'True', 'max_digits': '25', 'decimal_places': '20', 'blank': 'True'}),
            'create_date': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'end_date': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'external_articles': ('django.db.models.fields.IntegerField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'external_booth': ('django.db.models.fields.IntegerField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'in_house_articles': ('django.db.models.fields.IntegerField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'in_house_authors': ('django.db.models.fields.IntegerField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'in_house_pages': ('django.db.models.fields.IntegerField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'last_modified': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'percent_external': ('django.db.models.fields.DecimalField', [], {'default': "'0'", 'null': 'True', 'max_digits': '21', 'decimal_places': '20', 'blank': 'True'}),
            'percent_in_house': ('django.db.models.fields.DecimalField', [], {'default': "'0'", 'null': 'True', 'max_digits': '21', 'decimal_places': '20', 'blank': 'True'}),
            'start_date': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'total_articles': ('django.db.models.fields.IntegerField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'total_days': ('django.db.models.fields.IntegerField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'total_pages': ('django.db.models.fields.IntegerField', [], {'default': '0', 'null': 'True', 'blank': 'True'})
        },
        u'sourcenet.topic': {
            'Meta': {'ordering': "['name']", 'object_name': 'Topic'},
            'description': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'last_modified': ('django.db.models.fields.DateField', [], {'auto_now': 'True', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'})
        }
    }

    complete_apps = ['sourcenet']