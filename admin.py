'''
Copyright 2010-2013 Jonathan Morgan

This file is part of http://github.com/jonathanmorgan/sourcenet.

sourcenet is free software: you can redistribute it and/or modify it under the terms of the GNU Lesser General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.

sourcenet is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.

You should have received a copy of the GNU Lesser General Public License along with http://github.com/jonathanmorgan/sourcenet. If not, see http://www.gnu.org/licenses/.
'''

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
from sourcenet.models import Article_Source
from sourcenet.models import Article_Text
#from sourcenet.models import Article_Topic
#from sourcenet.models import Source_Organization
from sourcenet.models import Article
from sourcenet.models import Article_Data
from django.contrib import admin

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
#admin.site.register( Article_Source )
admin.site.register( Article_Text )
#admin.site.register( Article_Topic )
#admin.site.register( Source_Organization )
#admin.site.register( Article_Location )
 

#-------------------------------------------------------------------------------
# Organization admin definition
#-------------------------------------------------------------------------------

class OrganizationAdmin( admin.ModelAdmin ):

    fieldsets = [
        ( None,                 { 'fields' : [ 'name', 'description', 'location' ] } ),
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
        ( None,                 { 'fields' : [ 'first_name', 'middle_name', 'last_name', 'gender', 'title', 'notes' ] } ),
    ]

    # removing the organizational affiliation from the person area, for now, to
    #    avoid coding confusion.
    #inlines = [
    #    Person_OrganizationInline,
    #]

    list_display = ( 'last_name', 'first_name', 'middle_name', 'title' )
    #list_display_links = ( 'headline', )
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
        ( None,
            {
                'fields' : [ 'unique_identifier', 'newspaper', 'pub_date', 'section', 'page', 'headline', 'status' ]
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
    model = Article_Author
    extra = 2
    fk_name = 'article_data'

#class Source_OrganizationInline( admin.TabularInline ):
#    model = Source_Organization
#    extra = 2
#    fk_name = 'source_organization'

class ArticleSourceInline( admin.StackedInline ):
    model = Article_Source
    extra = 2
    fk_name = 'article_data'
    fieldsets = [
        ( None,                 { 'fields' : [ 'source_type', 'person', 'title', 'organization', 'more_title', 'document', 'source_contact_type', 'source_capacity', 'localness' ] } ),
        ( "Notes (Optional)",
            {
                'fields' : [ 'notes' ],
                'classes' : ( "collapse", )
            }
        ),
    ]

#-------------------------------------------------------------------------------
# Article Data admin definition
#-------------------------------------------------------------------------------

class Article_DataAdmin( admin.ModelAdmin ):
    fieldsets = [
        ( None,
            {
                'fields' : [ 'coder', 'topics', 'article_type', 'is_sourced', 'can_code', 'status' ]
            }
        ),
        ( "Article Locations (Optional)",
            {
                'fields' : [ 'locations'  ],
                'classes' : ( "collapse", )
            }
        ),
    ]

    inlines = [
        #TopicInline,
        ArticleAuthorInline,
        ArticleSourceInline,
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

class Article_SourceAdmin( admin.ModelAdmin ):

    fieldsets = [
        ( None,                 { 'fields' : [ 'article_data', 'source_type', 'person', 'title', 'organization', 'more_title', 'document', 'source_contact_type', 'source_capacity', 'localness' ] } ),
        ( "Notes (Optional)",
            {
                'fields' : [ 'notes' ],
                'classes' : ( "collapse", )
            }
        ),
    ]

    #inlines = [
    #    Source_OrganizationInline,
    #]

    list_display = ( 'person', 'organization', 'article_data' )
    #list_display_links = ( 'headline', )
    list_filter = [ 'person', 'organization', 'article_data' ]
    #search_fields = [ 'article', 'person', 'organization' ]
    #date_hierarchy = 'pub_date'

#-- END Article_SourceAdmin admin model --#

admin.site.register( Article_Source, Article_SourceAdmin )

#-------------------------------------------------------------------------------
# Article Author admin definition
#-------------------------------------------------------------------------------

class Article_AuthorAdmin( admin.ModelAdmin ):

    fieldsets = [
        ( None, { 'fields' : [ 'article_data', 'author_type', 'person' ] } ),
    ]

    #inlines = [
    #    Source_OrganizationInline,
    #]

    list_display = ( 'person', 'article_data' )
    #list_display_links = ( 'headline', )
    list_filter = [ 'person', 'article_data' ]
    #search_fields = [ 'article', 'person' ]
    #date_hierarchy = 'pub_date'

#-- END Article_SourceAdmin admin model --#

admin.site.register( Article_Author, Article_AuthorAdmin )