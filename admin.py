'''
Copyright 2010-2013 Jonathan Morgan

This file is part of http://github.com/jonathanmorgan/sourcenet.

sourcenet is free software: you can redistribute it and/or modify it under the terms of the GNU Lesser General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.

sourcenet is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.

You should have received a copy of the GNU Lesser General Public License along with http://github.com/jonathanmorgan/sourcenet. If not, see http://www.gnu.org/licenses/.
'''

# IMPORTANT!!! Any admin that contains a reference to an article should use
#    django-ajax-selects to include the article.  In a large set of articles,
#    the normal way of including a reference (a dropdown) will send the admin app
#    out to lunch trying to pull in all the entries for the dropdown.

# import code for AJAX select
from ajax_select import make_ajax_form
from ajax_select.admin import AjaxSelectAdmin

# Import models
from sourcenet.models import Project
from sourcenet.models import Location
from sourcenet.models import Topic
from sourcenet.models import Person
from sourcenet.models import Organization
from sourcenet.models import Person_Organization
from sourcenet.models import Document
from sourcenet.models import Newspaper
from sourcenet.models import Article_Author
#from sourcenet.models import Article_Location
from sourcenet.models import Article_Notes
from sourcenet.models import Article_RawData
from sourcenet.models import Article_Subject
from sourcenet.models import Article_Text
#from sourcenet.models import Article_Topic
#from sourcenet.models import Source_Organization
from sourcenet.models import Article
from sourcenet.models import Article_Data
from django.contrib import admin

admin.site.register( Project )
admin.site.register( Location )
admin.site.register( Topic )
#admin.site.register( Person )
#admin.site.register( Organization )
admin.site.register( Document )
admin.site.register( Newspaper )
#admin.site.register( Article )
#admin.site.register( Article_Author )
admin.site.register( Article_Notes )
admin.site.register( Article_RawData )
#admin.site.register( Article_Subject )
#admin.site.register( Article_Text )
#admin.site.register( Article_Topic )
#admin.site.register( Source_Organization )
#admin.site.register( Article_Location )
 

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

    list_display = ( 'name', 'location', 'description' )
    #list_display_links = ( 'headline', )
    list_filter = [ 'location' ]
    search_fields = [ 'name', 'location', 'description', 'id' ]
    #date_hierarchy = 'pub_date'

#-- END OrganizationAdmin admin model --#

admin.site.register( Organization, OrganizationAdmin )

class Person_OrganizationInline( admin.TabularInline ):
    model = Person_Organization

#-------------------------------------------------------------------------------
# Person admin definition
#-------------------------------------------------------------------------------

class PersonAdmin( admin.ModelAdmin ):
    fieldsets = [
        (
            None,
            { 'fields' : [ 'first_name', 'middle_name', 'last_name', 'gender', 'title', 'is_ambiguous', 'notes' ] }
        ),
    ]

    # removing the organizational affiliation from the person area, for now, to
    #    avoid coding confusion.
    #inlines = [
    #    Person_OrganizationInline,
    #]

    list_display = ( 'id', 'last_name', 'first_name', 'middle_name', 'title' )
    list_display_links = ( 'id', 'last_name', 'first_name', 'middle_name', )
    list_filter = [ 'last_name', 'first_name' ]
    search_fields = [ 'last_name', 'first_name', 'middle_name', 'title', 'id' ]
    #date_hierarchy = 'pub_date'

admin.site.register( Person, PersonAdmin )

class TopicInline( admin.TabularInline ):
    model = Topic
    ordering = [ "name" ]

class ArticleNotesInline( admin.StackedInline ):
    model = Article_Notes
    fk_name = 'article'

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
    fieldsets = [
        (
            None,
            {
                'fields' : [ 'unique_identifier', 'newspaper', 'pub_date', 'section', 'page', 'headline', 'status', 'tags' ]
            }
        ),
        ( 
            "More details (Optional)",
            {
                'fields' : [ 'index_terms'  ],
                'classes' : ( "collapse", )
            }
        ),
    ]

    inlines = [
        ArticleTextInline,
        ArticleNotesInline,
        ArticleRawDataInline
    ]

    list_display = ( 'newspaper', 'pub_date', 'unique_identifier', 'headline' )
    list_display_links = ( 'headline', )
    list_filter = [ 'pub_date', 'newspaper' ]
    search_fields = [ 'headline', 'unique_identifier', 'id' ]
    #search_fields = [ 'newspaper', 'coder', 'headline' ]
    #search_fields = [ 'newspaper.name', 'coder.last_name', 'coder.first_name', 'headline' ]
    date_hierarchy = 'pub_date'

admin.site.register( Article, ArticleAdmin )

class ArticleAuthorInline( admin.StackedInline ):

    # set up ajax-selects - for make_ajax_form, 1st argument is the model you
    #    are looking to make ajax selects form fields for; 2nd argument is a
    #    dict of pairs of field names in the model in argument 1 (with no quotes
    #    around them) mapped to lookup channels used to service them (lookup
    #    channels are defined in settings.py, implenented in a separate module -
    #    in this case, implemented in sourcenet.ajax-select-lookups.py
    form = make_ajax_form( Article_Author, dict( person = 'person' ) )

    model = Article_Author
    extra = 2
    fk_name = 'article_data'
    
#-- END class ArticleAuthorInline --#

#class Source_OrganizationInline( admin.TabularInline ):
#    model = Source_Organization
#    extra = 2
#    fk_name = 'source_organization'

class ArticleSubjectInline( admin.StackedInline ):

    # set up ajax-selects - for make_ajax_form, 1st argument is the model you
    #    are looking to make ajax selects form fields for; 2nd argument is a
    #    dict of pairs of field names in the model in argument 1 (with no quotes
    #    around them) mapped to lookup channels used to service them (lookup
    #    channels are defined in settings.py, implenented in a separate module -
    #    in this case, implemented in sourcenet.ajax-select-lookups.py
    form = make_ajax_form( Article_Subject, dict( person = 'person', organization = 'organization' ) )

    model = Article_Subject
    extra = 2
    fk_name = 'article_data'
    fieldsets = [
        (
            None,
            {
                'fields' : [ 'subject_type', 'source_type', 'person', 'title', 'more_title', 'organization', 'document', 'source_contact_type', 'source_capacity', 'localness' ]
            }
        ),
        (
            "Notes (Optional)",
            {
                'fields' : [ 'notes' ],
                'classes' : ( "collapse", )
            }
        ),
    ]

#-- END class ArticleSubjectInline --#


#-------------------------------------------------------------------------------
# Article Data admin definition
#-------------------------------------------------------------------------------

class Article_TextAdmin( admin.ModelAdmin ):

    # set up ajax-selects - for make_ajax_form, 1st argument is the model you
    #    are looking to make ajax selects form fields for; 2nd argument is a
    #    dict of pairs of field names in the model in argument 1 (with no quotes
    #    around them) mapped to lookup channels used to service them (lookup
    #    channels are defined in settings.py, implenented in a separate module -
    #    in this case, implemented in sourcenet.ajax-select-lookups.py
    form = make_ajax_form( Article_Text, dict( article = 'article' ) )

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

admin.site.register( Article_Text, Article_TextAdmin )


#-------------------------------------------------------------------------------
# Article Data admin definition
#-------------------------------------------------------------------------------

class Article_DataAdmin( admin.ModelAdmin ):

    # set up ajax-selects - for make_ajax_form, 1st argument is the model you
    #    are looking to make ajax selects form fields for; 2nd argument is a
    #    dict of pairs of field names in the model in argument 1 (with no quotes
    #    around them) mapped to lookup channels used to service them (lookup
    #    channels are defined in settings.py, implenented in a separate module -
    #    in this case, implemented in sourcenet.ajax-select-lookups.py
    form = make_ajax_form( Article_Data, dict( article = 'article' ) )

    fieldsets = [
        (
            None,
            {
                'fields' : [ 'article', 'coder', 'projects', 'topics', 'article_type', 'is_sourced', 'can_code', 'status' ]
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
    ]

    list_display = ( 'id', 'coder', 'create_date', 'article_type', 'status' )
    list_display_links = ( 'id', )
    list_filter = [ 'coder' ]
    search_fields = [ 'id' ]
    #search_fields = [ 'newspaper', 'coder', 'headline' ]
    #search_fields = [ 'newspaper.name', 'coder.last_name', 'coder.first_name', 'headline' ]
    date_hierarchy = 'create_date'

admin.site.register( Article_Data, Article_DataAdmin )

#-------------------------------------------------------------------------------
# Article Source admin definition
#-------------------------------------------------------------------------------

class Article_SubjectAdmin( admin.ModelAdmin ):

    # set up ajax-selects - for make_ajax_form, 1st argument is the model you
    #    are looking to make ajax selects form fields for; 2nd argument is a
    #    dict of pairs of field names in the model in argument 1 (with no quotes
    #    around them) mapped to lookup channels used to service them (lookup
    #    channels are defined in settings.py, implenented in a separate module -
    #    in this case, implemented in sourcenet.ajax-select-lookups.py
    form = make_ajax_form( Article_Subject, dict( person = 'person', organization = 'organization' ) )

    fieldsets = [
        (
            None,
            {
                'fields' : [ 'article_data', 'subject_type', 'source_type', 'person', 'title', 'organization', 'more_title', 'document', 'source_contact_type', 'source_capacity', 'localness' ]
            }
        ),
        (
            "Notes (Optional)",
            {
                'fields' : [ 'notes' ],
                'classes' : ( "collapse", )
            }
        ),
    ]

    #inlines = [
    #    Source_OrganizationInline,
    #]

    list_display = ( 'person', 'subject_type', 'organization', 'article_data' )
    #list_display_links = ( 'headline', )
    list_filter = [ 'person', 'subject_type', 'organization', 'article_data' ]
    #search_fields = [ 'article', 'person', 'organization' ]
    #date_hierarchy = 'pub_date'

#-- END Article_SubjectAdmin admin model --#

admin.site.register( Article_Subject, Article_SubjectAdmin )

#-------------------------------------------------------------------------------
# Article Author admin definition
#-------------------------------------------------------------------------------

class Article_AuthorAdmin( admin.ModelAdmin ):

    # set up ajax-selects - for make_ajax_form, 1st argument is the model you
    #    are looking to make ajax selects form fields for; 2nd argument is a
    #    dict of pairs of field names in the model in argument 1 (with no quotes
    #    around them) mapped to lookup channels used to service them (lookup
    #    channels are defined in settings.py, implenented in a separate module -
    #    in this case, implemented in sourcenet.ajax-select-lookups.py
    form = make_ajax_form( Article_Author, dict( person = 'person' ) )

    fieldsets = [
        (
            None,
            { 'fields' : [ 'article_data', 'author_type', 'person' ] }
        ),
    ]

    #inlines = [
    #    Source_OrganizationInline,
    #]

    list_display = ( 'person', 'article_data' )
    #list_display_links = ( 'headline', )
    list_filter = [ 'person', 'article_data' ]
    #search_fields = [ 'article', 'person' ]
    #date_hierarchy = 'pub_date'

#-- END Article_AuthorAdmin admin model --#

admin.site.register( Article_Author, Article_AuthorAdmin )
