# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding field 'Articles_To_Migrate.article'
        db.add_column(u'sourcenet_articles_to_migrate', 'article',
                      self.gf('django.db.models.fields.related.ForeignKey')(to=orm['sourcenet.Article'], null=True, blank=True),
                      keep_default=False)


    def backwards(self, orm):
        # Deleting field 'Articles_To_Migrate.article'
        db.delete_column(u'sourcenet_articles_to_migrate', 'article_id')


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
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'related_name': "u'user_set'", 'blank': 'True', 'to': u"orm['auth.Group']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_staff': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_superuser': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'user_permissions': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'related_name': "u'user_set'", 'blank': 'True', 'to': u"orm['auth.Permission']"}),
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
            'Meta': {'ordering': "[u'pub_date', u'section', u'page']", 'object_name': 'Article'},
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
            'status': ('django.db.models.fields.CharField', [], {'default': "u'new'", 'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'unique_identifier': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'})
        },
        u'sourcenet.article_author': {
            'Meta': {'object_name': 'Article_Author'},
            'article_data': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['sourcenet.Article_Data']"}),
            'author_type': ('django.db.models.fields.CharField', [], {'default': "u'staff'", 'max_length': '255', 'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'organization_string': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'person': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['sourcenet.Person']", 'null': 'True', 'blank': 'True'})
        },
        u'sourcenet.article_data': {
            'Meta': {'ordering': "[u'article', u'last_modified', u'create_date']", 'object_name': 'Article_Data'},
            'article': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['sourcenet.Article']"}),
            'article_type': ('django.db.models.fields.CharField', [], {'default': "u'news'", 'max_length': '255', 'blank': 'True'}),
            'can_code': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'coder': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['auth.User']"}),
            'create_date': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_sourced': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'last_modified': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'locations': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['sourcenet.Location']", 'symmetrical': 'False', 'blank': 'True'}),
            'status': ('django.db.models.fields.CharField', [], {'default': "u'new'", 'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'topics': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'to': u"orm['sourcenet.Topic']", 'null': 'True', 'blank': 'True'})
        },
        u'sourcenet.article_notes': {
            'Meta': {'ordering': "[u'article', u'last_modified', u'create_date']", 'object_name': 'Article_Notes'},
            'article': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['sourcenet.Article']", 'unique': 'True'}),
            'content': ('django.db.models.fields.TextField', [], {}),
            'create_date': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'last_modified': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'type': ('django.db.models.fields.CharField', [], {'default': "u'none'", 'max_length': '255', 'null': 'True', 'blank': 'True'})
        },
        u'sourcenet.article_rawdata': {
            'Meta': {'ordering': "[u'article', u'last_modified', u'create_date']", 'object_name': 'Article_RawData'},
            'article': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['sourcenet.Article']", 'unique': 'True'}),
            'content': ('django.db.models.fields.TextField', [], {}),
            'create_date': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'last_modified': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'type': ('django.db.models.fields.CharField', [], {'default': "u'none'", 'max_length': '255', 'null': 'True', 'blank': 'True'})
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
            'Meta': {'ordering': "[u'article', u'last_modified', u'create_date']", 'object_name': 'Article_Text'},
            'article': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['sourcenet.Article']", 'unique': 'True'}),
            'content': ('django.db.models.fields.TextField', [], {}),
            'create_date': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'last_modified': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'type': ('django.db.models.fields.CharField', [], {'default': "u'none'", 'max_length': '255', 'null': 'True', 'blank': 'True'})
        },
        u'sourcenet.articles_to_migrate': {
            'Meta': {'ordering': "[u'pub_date', u'section', u'page']", 'object_name': 'Articles_To_Migrate'},
            'article': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['sourcenet.Article']", 'null': 'True', 'blank': 'True'}),
            'article_type': ('django.db.models.fields.CharField', [], {'default': "u'news'", 'max_length': '255', 'blank': 'True'}),
            'can_code': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'coder': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['auth.User']"}),
            'headline': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_sourced': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'newspaper': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['sourcenet.Newspaper']", 'null': 'True', 'blank': 'True'}),
            'page': ('django.db.models.fields.IntegerField', [], {'blank': 'True'}),
            'pub_date': ('django.db.models.fields.DateField', [], {}),
            'section': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'text': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'unique_identifier': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'})
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
            'status': ('django.db.models.fields.CharField', [], {'default': "u'new'", 'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'unique_identifier': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'})
        },
        u'sourcenet.location': {
            'Meta': {'ordering': "[u'name', u'city', u'county', u'state', u'zip_code']", 'object_name': 'Location'},
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
            'Meta': {'ordering': "[u'name']", 'object_name': 'Newspaper'},
            'description': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'newsbank_code': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'organization': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['sourcenet.Organization']"}),
            'sections_local_news': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'sections_sports': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'})
        },
        u'sourcenet.organization': {
            'Meta': {'ordering': "[u'name', u'location']", 'object_name': 'Organization'},
            'description': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'location': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['sourcenet.Location']", 'null': 'True', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'})
        },
        u'sourcenet.person': {
            'Meta': {'ordering': "[u'last_name', u'first_name', u'middle_name']", 'object_name': 'Person'},
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
            'Meta': {'ordering': "[u'name']", 'object_name': 'Topic'},
            'description': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'last_modified': ('django.db.models.fields.DateField', [], {'auto_now': 'True', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'})
        }
    }

    complete_apps = ['sourcenet']