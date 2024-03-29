'''
Copyright 2010-present (currently 2020) Jonathan Morgan

This file is part of http://github.com/jonathanmorgan/context_text.

context_text is free software: you can redistribute it and/or modify it under the terms of the GNU Lesser General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.

context_text is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.

You should have received a copy of the GNU Lesser General Public License along with http://github.com/jonathanmorgan/context_text. If not, see http://www.gnu.org/licenses/.
'''

# IMPORTANT!!! Any admin that contains a reference to an article should use
#    autocomplete_fields to include the article.  In a large set of articles,
#    the normal way of including a reference (a dropdown) will send the admin app
#    out to lunch trying to pull in all the entries for the dropdown.

# core django imports
from django.contrib import admin
#from django.contrib.postgres import fields
from django.db import models

# django_json_widget imports
from django_json_widget.widgets import JSONEditorWidget

# Import models
from context_text.models import Article
from context_text.models import Article_Author
from context_text.models import Article_Data
from context_text.models import Article_Data_Notes
#from context_text.models import Article_Location
from context_text.models import Article_Notes
from context_text.models import Article_RawData
from context_text.models import Article_Subject
from context_text.models import Article_Text
#from context_text.models import Article_Topic
from context_text.models import Document
from context_text.models import Location
from context_text.models import NetworkDataOutputLog
from context_text.models import Newspaper
from context_text.models import Organization
from context_text.models import Person
from context_text.models import Person_External_UUID
from context_text.models import Person_Newspaper
from context_text.models import Person_Organization
from context_text.models import Project
#from context_text.models import Source_Organization
from context_text.models import Topic

# default admins
#admin.site.register( Article )
#admin.site.register( Article_Author )
#admin.site.register( Article_Data )
#admin.site.register( Article_Data_Notes )
#admin.site.register( Article_Location )
#admin.site.register( Article_Notes )
#admin.site.register( Article_RawData )
#admin.site.register( Article_Subject )
#admin.site.register( Article_Text )
#admin.site.register( Article_Topic )
admin.site.register( Document )
admin.site.register( Location )
#admin.site.register( NetworkDataOutputLog )
#admin.site.register( Newspaper )
#admin.site.register( Organization )
#admin.site.register( Person )
#admin.site.register( Person_External_UUID )
#admin.site.register( Person_Newspaper )
#admin.site.register( Person_Organization )
admin.site.register( Project )
#admin.site.register( Source_Organization )
admin.site.register( Topic )


#-------------------------------------------------------------------------------
# Organization admin definition
#-------------------------------------------------------------------------------

class OrganizationAdmin( admin.ModelAdmin ):

    fieldsets = [
        (
            None,
            {
                'fields' : [ 'name', 'description', 'location' ]
            }
        ),
    ]

    #inlines = [
    #    Source_OrganizationInline,
    #]

    list_display = ( 'id', 'name', 'location', 'description', 'create_date', 'last_modified' )
    list_display_links = ( 'id', 'name' )
    list_filter = [ 'location' ]
    search_fields = [ 'name', 'location', 'description', 'id' ]
    #date_hierarchy = 'pub_date'

#-- END OrganizationAdmin admin model --#

admin.site.register( Organization, OrganizationAdmin )


#-------------------------------------------------------------------------------
# Newspaper admin definition
#-------------------------------------------------------------------------------


class NewspaperAdmin( admin.ModelAdmin ):

    fieldsets = [
        (
            None,
            {
                'fields' : [ 'name', 'description', 'organization', 'newsbank_code', 'sections_local_news', 'sections_sports' ]
            }
        ),
    ]

    #inlines = [
    #    Source_OrganizationInline,
    #]

    list_display = ( 'id', 'name', 'newsbank_code', 'description' )
    list_display_links = ( 'id', 'name', 'newsbank_code' )
    #list_filter = [ 'location' ]
    search_fields = [ 'name', 'description', 'newsbank_code', 'sections_local_news', 'sections_sports', 'id' ]
    #date_hierarchy = 'pub_date'

#-- END OrganizationAdmin admin model --#

admin.site.register( Newspaper, NewspaperAdmin )


#-------------------------------------------------------------------------------
# Person admin definition
#-------------------------------------------------------------------------------


class Person_Organization_Inline( admin.TabularInline ):

    model = Person_Organization

#-- END Person_Organization_Inline model --#


class Person_External_UUID_Inline( admin.TabularInline ):

    model = Person_External_UUID
    extra = 1

#-- END Person_External_UUID_Inline model --#


class Person_Newspaper_Inline( admin.TabularInline ):

    model = Person_Newspaper
    extra = 1

#-- END Person_Newspaper_Inline model --#


class PersonAdmin( admin.ModelAdmin ):

    # ajax-based autocomplete
    autocomplete_fields = [ 'organization' ]

    fieldsets = [
        (
            None,
            { "fields" : [ "first_name", "middle_name", "last_name", "gender", "title", "organization", "is_ambiguous", "notes" ] }
        ),
        (
            "More details (Optional)",
            {
                "fields" : [ "more_title", "organization_string", "more_organization" ],
                "classes" : ( "collapse", )
            }
        ),
    ]

    # removing the organizational affiliation from the person area, for now, to
    #    avoid coding confusion.
    inlines = [
    #    Person_Organization_Inline,
        Person_Newspaper_Inline,
        Person_External_UUID_Inline,
    ]

    list_display = ( 'id', 'last_name', 'first_name', 'middle_name', 'title' )
    list_display_links = ( 'id', 'last_name', 'first_name', 'middle_name', )
    list_filter = [ 'last_name', 'first_name' ]
    search_fields = [ 'last_name', 'first_name', 'middle_name', 'title', 'id' ]
    #date_hierarchy = 'pub_date'

admin.site.register( Person, PersonAdmin )

class Person_External_UUIDAdmin( admin.ModelAdmin ):

    # ajax-based autocomplete
    autocomplete_fields = [ 'person' ]

    fieldsets = [
        (
            None,
            { "fields" : [ "person", "name", "uuid", "source", "id_type", "tags", "notes" ] }
        ),
    ]

    list_display = ( 'id', 'person', 'name', 'uuid', 'source', 'id_type' )
    list_display_links = ( 'id', 'name' )
    list_filter = [ 'name', 'source', 'id_type' ]
    search_fields = [ 'name', 'uuid', 'source', 'id_type', 'notes', 'person__id', 'id' ]
    #date_hierarchy = 'pub_date'

admin.site.register( Person_External_UUID, Person_External_UUIDAdmin )

class TopicInline( admin.TabularInline ):
    model = Topic
    ordering = [ "name" ]

class ArticleNotesInline( admin.StackedInline ):

    model = Article_Notes
    extra = 1
    fk_name = 'article'

#-- END inline class ArticleNotesInline --#

class ArticleRawDataInline( admin.StackedInline ):
    model = Article_RawData
    fk_name = 'article'

class ArticleTextInline( admin.StackedInline ):
    model = Article_Text
    fk_name = 'article'

#class LocationInline( admin.StackedInline ):
#    model = Article_Location
#    extra = 2
#    fk_name = 'article'

#-------------------------------------------------------------------------------
# Article admin definition
#-------------------------------------------------------------------------------

class ArticleAdmin( admin.ModelAdmin ):

    formfield_overrides = {
        models.JSONField: { 'widget': JSONEditorWidget },
    }

    fieldsets = [
        (
            None,
            {
                'fields' : [ 'unique_identifier', 'newspaper', 'pub_date', 'section', 'page', 'headline', 'author_string', 'author_varchar', 'author_name', 'author_affiliation', 'status', 'tags' ]
            }
        ),
        (
            "More details (Optional)",
            {
                'fields' : [ 'details_json', 'index_terms', 'cleanup_status', 'file_path'  ],
                'classes' : ( "collapse", )
            }
        ),
    ]

    inlines = [
        ArticleTextInline,
        ArticleNotesInline,
        ArticleRawDataInline
    ]

    list_display = ( 'id', 'newspaper', 'section', 'pub_date', 'unique_identifier', 'headline' )
    list_display_links = ( 'id', 'headline', )
    list_filter = [ 'pub_date', 'newspaper', 'section' ]
    search_fields = [ 'headline', 'unique_identifier', 'id' ]
    #search_fields = [ 'newspaper', 'coder', 'headline' ]
    #search_fields = [ 'newspaper.name', 'coder.last_name', 'coder.first_name', 'headline' ]
    date_hierarchy = 'pub_date'

admin.site.register( Article, ArticleAdmin )

#-------------------------------------------------------------------------------
# Article_Content abstract class admin definition
#-------------------------------------------------------------------------------

class Article_ContentAdmin( admin.ModelAdmin ):

    # ajax-based autocomplete
    autocomplete_fields = [ 'article' ]

    fieldsets = [
        (
            None,
            {
                'fields' : [ 'article', 'content', 'content_type', 'status' ]
            }
        ),
    ]

    list_display = ( 'id', 'content_type', 'status', 'article' )
    list_display_links = ( 'id', 'article', )
    list_filter = [ 'content_type', 'status' ]
    search_fields = [ 'content', ]
    #date_hierarchy = 'pub_date'

#-- END admin class Article_ContentAdmin --#

# ! register all descendents of Article_Content and Unique_Article_Content
admin.site.register( Article_Text, Article_ContentAdmin )
admin.site.register( Article_Notes, Article_ContentAdmin )
admin.site.register( Article_RawData, Article_ContentAdmin )


#-------------------------------------------------------------------------------
# Article_Data admin definition
#-------------------------------------------------------------------------------

class ArticleAuthorInline( admin.StackedInline ):

    # ajax-based autocomplete
    autocomplete_fields = [ 'person', 'organization' ]

    model = Article_Author
    extra = 1
    fk_name = 'article_data'

    fieldsets = [
        (
            None,
            {
                'fields' : [ 'author_type', 'person', 'name', 'verbatim_name', 'lookup_name', 'title', 'more_title', 'organization', 'organization_string', 'more_organization' ]
            }
        ),
        (
            "More Detail",
            {
                'fields' : [ 'capture_method', 'match_confidence_level', 'match_status', 'original_person', 'notes' ],
                'classes' : ( "collapse", )
            }
        ),
    ]

#-- END class ArticleAuthorInline --#

#class Source_OrganizationInline( admin.TabularInline ):
#    model = Source_Organization
#    extra = 2
#    fk_name = 'source_organization'

class ArticleSubjectInline( admin.StackedInline ):

    # ajax-based autocomplete
    autocomplete_fields = [ 'person', 'organization' ]

    model = Article_Subject
    extra = 1
    fk_name = 'article_data'
    fieldsets = [
        (
            None,
            {
                'fields' : [ 'subject_type', 'source_type', 'person', 'name', 'verbatim_name', 'lookup_name', 'title', 'more_title', 'organization', 'organization_string', 'more_organization' ]
            }
        ),
        (
            "More Detail",
            {
                'fields' : [ 'capture_method', 'match_confidence_level', 'match_status', 'original_person', 'document', 'source_contact_type', 'source_capacity', 'localness', 'notes' ],
                'classes' : ( "collapse", )
            }
        ),
    ]

#-- END class ArticleSubjectInline --#


class Article_Data_Article_Data_NotesInline( admin.StackedInline ):

    # ajax-based autocomplete
    autocomplete_fields = [ 'article_data' ]

    formfield_overrides = {
        models.JSONField: {'widget': JSONEditorWidget},
    }

    model = Article_Data_Notes
    extra = 1
    fk_name = 'article_data'

    fieldsets = [
        (
            None,
            {
                'fields' : [ 'content', 'content_json', 'content_type', 'status', 'source', 'tags' ]
            }
        ),
        (
            "More Detail",
            {
                'fields' : [ 'note_type', 'source_identifier', 'content_description' ],
                'classes' : ( "collapse", )
            }
        ),
    ]

#-- END inline class Article_Data_Article_Data_NotesInline --#

class Article_DataAdmin( admin.ModelAdmin ):

    # ajax-based autocomplete
    autocomplete_fields = [ 'article' ]

    fieldsets = [
        (
            None,
            {
                'fields' : [ 'article', 'coder', 'coder_type', 'projects', 'topics', 'article_type', 'is_sourced', 'can_code', 'status' ]
            }
        ),
        (
            "Article Locations (Optional)",
            {
                'fields' : [ 'locations'  ],
                'classes' : ( "collapse", )
            }
        ),
    ]

    inlines = [
        #TopicInline,
        ArticleAuthorInline,
        ArticleSubjectInline,
        #LocationInline
        Article_Data_Article_Data_NotesInline,
    ]

    list_display = ( 'id', 'my_article_id', 'coder', 'create_date', 'article_type', 'status' )
    list_display_links = ( 'id', )
    list_filter = [ 'coder' ]
    search_fields = [ 'id' ]
    #search_fields = [ 'newspaper', 'coder', 'headline' ]
    #search_fields = [ 'newspaper.name', 'coder.last_name', 'coder.first_name', 'headline' ]
    date_hierarchy = 'create_date'

admin.site.register( Article_Data, Article_DataAdmin )

#-------------------------------------------------------------------------------
# Article_Subject admin definition
#-------------------------------------------------------------------------------

class Article_SubjectAdmin( admin.ModelAdmin ):

    # ajax-based autocomplete
    autocomplete_fields = [ 'article_data', 'person', 'organization' ]

    fieldsets = [
        (
            None,
            {
                'fields' : [ 'article_data', 'tags', 'subject_type', 'source_type', 'person', 'name', 'verbatim_name', 'lookup_name', 'title', 'more_title', 'organization', 'organization_string', 'more_organization' ]
            }
        ),
        (
            "More Detail",
            {
                'fields' : [ 'capture_method', 'match_confidence_level', 'match_status', 'original_person', 'document', 'source_contact_type', 'source_capacity', 'localness', 'notes' ],
                'classes' : ( "collapse", )
            }
        ),
    ]

    #inlines = [
    #    Source_OrganizationInline,
    #]

    list_display = ( 'id', 'subject_type', 'person', 'article_data' )
    list_display_links = ( 'id', 'person', )
    list_filter = [ 'subject_type', 'article_data__coder', 'article_data__article__newspaper' ]
    search_fields = [ 'name', 'verbatim_name', 'lookup_name', 'id' ]
    #date_hierarchy = 'pub_date'

#-- END Article_SubjectAdmin admin model --#

admin.site.register( Article_Subject, Article_SubjectAdmin )

#-------------------------------------------------------------------------------
# Article Author admin definition
#-------------------------------------------------------------------------------

class Article_AuthorAdmin( admin.ModelAdmin ):

    # ajax-based autocomplete
    autocomplete_fields = [ 'article_data', 'person', 'organization' ]

    fieldsets = [
        (
            None,
            {
                'fields' : [ 'article_data', 'tags', 'author_type', 'person', 'name', 'verbatim_name', 'lookup_name', 'title', 'more_title', 'organization', 'organization_string', 'more_organization' ]
            }
        ),
        (
            "More Detail",
            {
                'fields' : [ 'capture_method', 'match_confidence_level', 'match_status', 'original_person', 'notes' ],
                'classes' : ( "collapse", )
            }
        ),
    ]

    #inlines = [
    #    Source_OrganizationInline,
    #]

    list_display = ( 'id', 'author_type', 'person', 'article_data' )
    list_display_links = ( 'id', 'person', )
    list_filter = [ 'author_type' ]
    search_fields = [ 'name', 'verbatim_name', 'lookup_name', 'id' ]
    #search_fields = [ 'article', 'person' ]
    #date_hierarchy = 'pub_date'

#-- END Article_AuthorAdmin admin model --#

admin.site.register( Article_Author, Article_AuthorAdmin )


#-------------------------------------------------------------------------------
# Article_Data_Notes admin definition
#-------------------------------------------------------------------------------

class Article_Data_NotesAdmin( admin.ModelAdmin ):

    # ajax-based autocomplete
    autocomplete_fields = [ 'article_data' ]

    formfield_overrides = {
        models.JSONField: {'widget': JSONEditorWidget},
    }

    fieldsets = [
        (
            None,
            {
                'fields' : [ 'article_data', 'content', 'content_json', 'content_type', 'status', 'source', 'tags' ]
            }
        ),
        (
            "More Detail",
            {
                'fields' : [ 'note_type', 'source_identifier', 'content_description' ],
                'classes' : ( "collapse", )
            }
        ),
    ]

    list_display = ( 'id', 'last_modified', 'content_type', 'status', 'article_data', 'source', 'note_type',  )
    list_display_links = ( 'id', 'article_data', )
    list_filter = [ 'content_type', 'status', 'note_type' ]
    search_fields = [ 'content', 'source', 'source_identifier', 'note_type', 'id' ]
    #date_hierarchy = 'pub_date'

admin.site.register( Article_Data_Notes, Article_Data_NotesAdmin )

#-------------------------------------------------------------------------------
# NetworkDataOutputLog admin definition
#-------------------------------------------------------------------------------

class NetworkDataOutputLogAdmin( admin.ModelAdmin ):

    formfield_overrides = {
        models.JSONField: { 'widget': JSONEditorWidget },
    }

    fieldsets = [
        (
            None,
            {
                'fields' : [ 'label', 'description', 'request_type', 'status', 'status_message', 'tags' ]
            }
        ),
        (
            "Data Spec",
            {
                'fields' : [ 'data_spec_json_hash', 'data_spec_json' ],
                'classes' : ( "collapse", )
            }
        ),
        (
            "Network Data",
            {
                'fields' : [ 'network_data_content_type', 'network_data_format', 'network_data_hash', 'network_data' ],
                'classes' : ( "collapse", )
            }
        ),
        (
            "More Details (Optional)",
            {
                'fields' : [ 'notes' ],
                'classes' : ( "collapse", )
            }
        ),
    ]

    list_display = (
        'id',
        'label',
        'request_type',
        'network_data_format',
        'create_date',
        'last_modified'
    )
    list_display_links = ( 'id', 'label' )
    list_filter = [ 'request_type', 'network_data_format', 'network_data_content_type' ]
    search_fields = [ 'label', 'description', 'notes', 'request_type', 'network_data_format', 'network_data_content_type', 'id' ]
    #search_fields = [ 'newspaper', 'coder', 'headline' ]
    #search_fields = [ 'newspaper.name', 'coder.last_name', 'coder.first_name', 'headline' ]
    date_hierarchy = 'create_date'

admin.site.register( NetworkDataOutputLog, NetworkDataOutputLogAdmin )

