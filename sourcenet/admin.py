from mysite.sourcenet.models import Location
from mysite.sourcenet.models import Topic
from mysite.sourcenet.models import Person
from mysite.sourcenet.models import Organization
from mysite.sourcenet.models import Person_Organization
from mysite.sourcenet.models import Document
from mysite.sourcenet.models import Newspaper
#from mysite.sourcenet.models import Article_Topic
from mysite.sourcenet.models import Article_Author
from mysite.sourcenet.models import Article_Source
#from mysite.sourcenet.models import Article_Location
#from mysite.sourcenet.models import Source_Organization
from mysite.sourcenet.models import Article
from django.contrib import admin

admin.site.register( Location )
admin.site.register( Topic )
#admin.site.register( Person )
#admin.site.register( Organization )
admin.site.register( Document )
admin.site.register( Newspaper )
#admin.site.register( Article )
#admin.site.register( Article_Topic )
#admin.site.register( Article_Author )
#admin.site.register( Article_Source )
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

class ArticleAuthorInline( admin.StackedInline ):
    model = Article_Author
    extra = 2
    fk_name = 'article'

#class Source_OrganizationInline( admin.TabularInline ):
#    model = Source_Organization
#    extra = 2
#    fk_name = 'source_organization'

class ArticleSourceInline( admin.StackedInline ):
    model = Article_Source
    extra = 2
    fk_name = 'article'
    fieldsets = [
        ( None,                 { 'fields' : [ 'source_type', 'person', 'title', 'organization', 'more_title', 'document', 'source_contact_type', 'source_capacity', 'localness' ] } ),
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
                'fields' : [ 'coder', 'unique_identifier', 'newspaper', 'pub_date', 'section', 'page', 'headline', 'topics', 'article_type', 'is_sourced', 'can_code' ]
            }
        ),
        ( "Article Locations and Text (Optional)",
            {
                'fields' : [ 'locations', 'text'  ],
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

    list_display = ( 'coder', 'newspaper', 'pub_date', 'unique_identifier', 'headline' )
    list_display_links = ( 'headline', )
    list_filter = [ 'pub_date', 'newspaper', 'coder' ]
    search_fields = [ 'headline', 'unique_identifier', 'id' ]
    #search_fields = [ 'newspaper', 'coder', 'headline' ]
    #search_fields = [ 'newspaper.name', 'coder.last_name', 'coder.first_name', 'headline' ]
    date_hierarchy = 'pub_date'

admin.site.register( Article, ArticleAdmin )

#-------------------------------------------------------------------------------
# Article Source admin definition
#-------------------------------------------------------------------------------

class Article_SourceAdmin( admin.ModelAdmin ):

    fieldsets = [
        ( None,                 { 'fields' : [ 'article', 'source_type', 'person', 'title', 'organization', 'more_title', 'document', 'source_contact_type', 'source_capacity', 'localness' ] } ),
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

    list_display = ( 'person', 'organization', 'article' )
    #list_display_links = ( 'headline', )
    list_filter = [ 'person', 'organization', 'article' ]
    #search_fields = [ 'article', 'person', 'organization' ]
    #date_hierarchy = 'pub_date'

#-- END Article_SourceAdmin admin model --#

admin.site.register( Article_Source, Article_SourceAdmin )

#-------------------------------------------------------------------------------
# Article Author admin definition
#-------------------------------------------------------------------------------

class Article_AuthorAdmin( admin.ModelAdmin ):

    fieldsets = [
        ( None,                 { 'fields' : [ 'article', 'author_type', 'person' ] } ),
    ]

    #inlines = [
    #    Source_OrganizationInline,
    #]

    list_display = ( 'person', 'article' )
    #list_display_links = ( 'headline', )
    list_filter = [ 'person', 'article' ]
    #search_fields = [ 'article', 'person' ]
    #date_hierarchy = 'pub_date'

#-- END Article_SourceAdmin admin model --#

admin.site.register( Article_Author, Article_AuthorAdmin )