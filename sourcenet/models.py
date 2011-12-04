# python imports
import logging
from decimal import Decimal
from decimal import getcontext

# Django core imports
#from django.core.exceptions import DoesNotExist
from django.core.exceptions import ObjectDoesNotExist
from django.core.exceptions import MultipleObjectsReturned

# Django imports
from django.db import models
from django.contrib.auth.models import User

# Django query object for OR-ing selection criteria together.
from django.db.models import Q

# Dajngo object for interacting directly with database.
from django.db import connection

'''
Models for SourceNet, including some that are specific to the Grand Rapids Press.
'''

# Locations
class Location( models.Model ):

    # States to choose from.
    STATE_CHOICES = (
        ( 'AL', 'Alabama' ),
        ( 'AK', 'Alaska' ),
        ( 'AS', 'American Samoa' ),
        ( 'AZ', 'Arizona' ),
        ( 'AR', 'Arkansas' ),
        ( 'CA', 'California' ),
        ( 'CO', 'Colorado' ),
        ( 'CT', 'Connecticut' ),
        ( 'DE', 'Delaware' ),
        ( 'DC', 'District of Columbia' ),
        ( 'FM', 'Federated States of Micronesia' ),
        ( 'FL', 'Florida' ),
        ( 'GA', 'Georgia' ),
        ( 'GU', 'Guam' ),
        ( 'HI', 'Hawaii' ),
        ( 'ID', 'Idaho' ),
        ( 'IL', 'Illinois' ),
        ( 'IN', 'Indiana' ),
        ( 'IA', 'Iowa' ),
        ( 'KS', 'Kansas' ),
        ( 'KY', 'Kentucky' ),
        ( 'LA', 'Louisiana' ),
        ( 'ME', 'Maine' ),
        ( 'MH', 'Marshall Islands' ),
        ( 'MD', 'Maryland' ),
        ( 'MA', 'Massachusetts' ),
        ( 'MI', 'Michigan' ),
        ( 'MN', 'Minnesota' ),
        ( 'MS', 'Mississippi' ),
        ( 'MO', 'Missouri' ),
        ( 'MT', 'Montana' ),
        ( 'NE', 'Nebraska' ),
        ( 'NV', 'Nevada' ),
        ( 'NH', 'New Hampshire' ),
        ( 'NJ', 'New Jersey' ),
        ( 'NM', 'New Mexico' ),
        ( 'NY', 'New York' ),
        ( 'NC', 'North Carolina' ),
        ( 'ND', 'North Dakota' ),
        ( 'MP', 'Northern Mariana Islands' ),
        ( 'OH', 'Ohio' ),
        ( 'OK', 'Oklahoma' ),
        ( 'OR', 'Oregon' ),
        ( 'PW', 'Palau' ),
        ( 'PA', 'Pennsylvania' ),
        ( 'PR', 'Puerto Rico' ),
        ( 'RI', 'Rhode Island' ),
        ( 'SC', 'South Carolina' ),
        ( 'SD', 'South Dakota' ),
        ( 'TN', 'Tennessee' ),
        ( 'TX', 'Texasv' ),
        ( 'UT', 'Utah' ),
        ( 'VT', 'Vermont' ),
        ( 'VI', 'Virgin Islands' ),
        ( 'VA', 'Virginia' ),
        ( 'WA', 'Washington' ),
        ( 'WV', 'West Virginia' ),
        ( 'WI', 'Wisconsin' ),
        ( 'WY', 'Wyoming' )
    )

    name = models.CharField( max_length = 255, blank = True )
    description = models.TextField( blank=True )
    address = models.CharField( max_length = 255, blank = True )
    city = models.CharField( max_length = 255, blank = True )
    county = models.CharField( max_length = 255, blank = True )
    state = models.CharField( max_length = 2, choices = STATE_CHOICES, blank = True )
    zip_code = models.CharField( 'ZIP Code', max_length = 10, blank = True )

    # Meta-data for this class.
    class Meta:
        ordering = [ 'name', 'city', 'county', 'state', 'zip_code' ]

    #----------------------------------------------------------------------
    # methods
    #----------------------------------------------------------------------

    def __unicode__( self ):
        # return reference
        string_OUT = ''
        delimiter = ''

        # see what we can place in the string.
        if ( self.name != '' ):
            string_OUT = '"' + self.name + '"'
            delimiter = ', '

        if ( self.address != '' ):
            string_OUT = string_OUT + delimiter + self.address
            delimiter = ', '

        if ( self.city != '' ):
            string_OUT = string_OUT + delimiter + self.city
            delimiter = ', '

        if ( self.county != '' ):
            string_OUT = string_OUT + delimiter + self.county + " County"
            delimiter = ', '

        if ( self.state != '' ):
            string_OUT = string_OUT + delimiter + self.state
            delimiter = ', '

        if ( self.zip_code != '' ):
            string_OUT = string_OUT + delimiter + self.zip_code
            delimiter = ', '

        return string_OUT

#= End Location Model =========================================================

# Topic model
class Topic( models.Model ):
    name = models.CharField( max_length = 255 )
    description = models.TextField( blank = True )
    last_modified = models.DateField( auto_now = True )

    # Meta-data for this class.
    class Meta:
        ordering = [ 'name' ]

    #----------------------------------------------------------------------
    # methods
    #----------------------------------------------------------------------

    def __unicode__( self ):
        string_OUT = self.name
        return string_OUT

#= End Topic Model =========================================================


# Person model
class Person( models.Model ):

    GENDER_CHOICES = (
        ( 'na', 'Unknown' ),
        ( 'female', 'Female' ),
        ( 'male', 'Male' )
    )

    first_name = models.CharField( max_length = 255 )
    middle_name = models.CharField( max_length = 255, blank = True )
    last_name = models.CharField( max_length = 255 )
    gender = models.CharField( max_length = 6, choices = GENDER_CHOICES )
    title = models.CharField( max_length = 255, blank = True )
    notes = models.TextField( blank = True )

    # Meta-data for this class.
    class Meta:
        ordering = [ 'last_name', 'first_name', 'middle_name' ]

    #----------------------------------------------------------------------
    # methods
    #----------------------------------------------------------------------

    def __unicode__( self ):
        # return reference
        string_OUT = ''
        string_OUT = self.last_name + ', ' + self.first_name + " " + self.middle_name
        if ( ( self.title is not None ) and ( self.title != '' ) ):
            string_OUT = string_OUT + " ( " + self.title + " )"
        return string_OUT

#= End Person Model =========================================================


# Orgnization model
class Organization( models.Model ):

    name = models.CharField( max_length = 255 )
    description = models.TextField( blank = True )
    location = models.ForeignKey( Location, blank = True, null = True )

    # Meta-data for this class.
    class Meta:
        ordering = [ 'name', 'location' ]

    #----------------------------------------------------------------------
    # methods
    #----------------------------------------------------------------------

    def __unicode__( self ):
        string_OUT = self.name
        return string_OUT

#= End Organization Model ======================================================


# Person_Organization model
class Person_Organization( models.Model ):

    person = models.ForeignKey( Person )
    organization = models.ForeignKey( Organization, blank = True, null = True )
    title = models.CharField( max_length = 255, blank = True )

    #----------------------------------------------------------------------
    # methods
    #----------------------------------------------------------------------

    def __unicode__( self ):
        string_OUT = self.organization.name
        if ( self.title != '' ):
            string_OUT = string_OUT + " ( " + self.title + " )"
        return string_OUT

#= End Person_Organization Model ======================================================


# Document model
class Document( models.Model ):

    name = models.CharField( max_length = 255 )
    description = models.TextField( blank = True)
    organization = models.ForeignKey( Organization, blank = True, null = True )

    #----------------------------------------------------------------------
    # methods
    #----------------------------------------------------------------------

    def __unicode__( self ):
        string_OUT = self.name
        return string_OUT

#= End Document Model ======================================================


# Newspaper model
class Newspaper( models.Model ):

    name = models.CharField( max_length = 255 )
    description = models.TextField( blank = True )
    organization = models.ForeignKey( Organization )
    #location = models.ForeignKey( Location )

    # Meta-data for this class.
    class Meta:
        ordering = [ 'name' ]

    #----------------------------------------------------------------------
    # methods
    #----------------------------------------------------------------------

    def __unicode__( self ):
        string_OUT = self.name
        return string_OUT

#= End Newspaper Model ======================================================


# Article_Topic model
#class Article_Topic( models.Model ):

#    topic = models.ForeignKey( Topic )
#    rank = models.IntegerField()

    #----------------------------------------------------------------------
    # methods
    #----------------------------------------------------------------------

#    def __unicode__( self ):
#        string_OUT = '%d - %s' % ( self.rank, self.topic.name )
#        return string_OUT

#= End Article_Topic Model ======================================================


# Article model
class Article( models.Model ):

    unique_identifier = models.CharField( max_length = 255, blank = True )
    source_string = models.CharField( max_length = 255, blank = True, null = True )
    newspaper = models.ForeignKey( Newspaper, blank = True, null = True )
    pub_date = models.DateField()
    section = models.CharField( max_length = 255, blank = True )
    #page = models.IntegerField( blank = True )
    page = models.CharField( max_length = 255, blank = True, null = True )
    author_string = models.TextField( blank = True, null = True )
    author_varchar = models.CharField( max_length = 255, blank = True, null = True )
    headline = models.CharField( max_length = 255 )
    # What is this? - author = models.CharField( max_length = 255, blank = True, null = True )
    text = models.TextField( blank = True )
    corrections = models.TextField( blank = True, null = True )
    edition = models.CharField( max_length = 255, blank = True, null = True )
    index_terms = models.TextField( blank = True, null = True )
    archive_source = models.CharField( max_length = 255, blank = True, null = True )
    archive_id = models.CharField( max_length = 255, blank = True, null = True )
    permalink = models.TextField( blank = True, null = True )
    copyright = models.TextField( blank = True, null = True )
    notes = models.TextField( blank = True, null = True )
    raw_html = models.TextField( blank = True, null = True )
    status = models.CharField( max_length = 255, blank = True, null = True, default = "new" )
    is_local_news = models.BooleanField( default = 0 )
    is_sports = models.BooleanField( default = 0 )
    is_local_author = models.BooleanField( default = 0 )
    create_date = models.DateTimeField( auto_now_add = True )
    last_modified = models.DateTimeField( auto_now = True )

    #topics = models.ManyToManyField( Article_Topic )
    #authors = models.ManyToManyField( Article_Author )
    #sources = models.ManyToManyField( Article_Source )
    #locations = models.ManyToManyField( Article_Location, blank = True )

    # Meta-data for this class.
    class Meta:
        ordering = [ 'pub_date', 'section', 'page' ]

    #----------------------------------------------------------------------
    # methods
    #----------------------------------------------------------------------

    def __unicode__( self ):
        string_OUT = str( self.id ) + " - " + self.newspaper.name + " (" + self.pub_date.strftime( "%b %d, %Y" ) + ", " + self.section + str( self.page ) + ", UID: " + self.unique_identifier + ") - " + self.headline
        return string_OUT

    #-- END method __unicode__() --#

#= End Article Model ===========================================================


# Article_Data model
class Article_Data( models.Model ):

    # declaring a few "constants"
    ARTICLE_TYPE_NEWS_TO_ID_MAP = {
        'news' : 1,
        'sports' : 2,
        'feature' : 3,
        'opinion' : 4,
        'other' : 99
    }

    ARTICLE_TYPE_CHOICES = (
        ( "news", "News" ),
        ( "sports", "Sports" ),
        ( "feature", "Feature" ),
        ( "opinion", "Opinion" ),
        ( "other", "Other" )
    )

    article = models.ForeignKey( Article )
    coder = models.ForeignKey( User )
    topics = models.ManyToManyField( Topic )
    locations = models.ManyToManyField( Location, blank = True )
    article_type = models.CharField( max_length = 255, choices = ARTICLE_TYPE_CHOICES, blank = True, default = 'news' )
    is_sourced = models.BooleanField( default = 1 )
    can_code = models.BooleanField( default = 1 )
    status = models.CharField( max_length = 255, blank = True, null = True, default = "new" )
    create_date = models.DateTimeField( auto_now_add = True )
    last_modified = models.DateTimeField( auto_now = True )

    #topics = models.ManyToManyField( Article_Topic )
    #authors = models.ManyToManyField( Article_Author )
    #sources = models.ManyToManyField( Article_Source )
    #locations = models.ManyToManyField( Article_Location, blank = True )

    # Meta-data for this class.
    class Meta:
        ordering = [ 'article', 'last_modified', 'create_date' ]

    #----------------------------------------------------------------------
    # methods
    #----------------------------------------------------------------------

    def __unicode__( self ):
        string_OUT = str( self.id ) + " - " + self.newspaper.name + " (" + self.pub_date.strftime( "%b %d, %Y" ) + ", " + self.section + str( self.page ) + ", UID: " + self.unique_identifier + ") - " + self.headline
        return string_OUT

    #-- END method __unicode__() --#


    def get_source_counts_by_type( self ):

        '''
            Method: get_source_counts_by_type
            Retrieves all sources, loops over them and creates a dictionary that maps
               source types to the count of that type of source in this article.
            preconditions: the instance needs to have an article loaded in it.
            postconditions: returns dictionary that maps each source type to the count
               of sources of that type in this article.
            
            Returns:
               - dictionary - dictionary that maps each source type to the count of sources of that type in this article.
        '''

        # return reference
        counts_OUT = {}

        # declare variables
        types_dictionary = None
        current_type = ''
        #current_type_id = ''
        article_sources = None
        current_source = None
        current_source_type = ''
        current_type_count = -1

        # grab types from Article_Source
        types_dictionary = Article_Source.SOURCE_TYPE_TO_ID_MAP

        # populate output dictionary with types
        for current_type in types_dictionary.iterkeys():

            counts_OUT[ current_type ] = 0

        #-- END loop over source types --#

        # now get sources, loop over them, and for each, get source type, add
        #    one to the value in the hash for that type.
        article_sources = self.article_source_set.all()

        for current_source in article_sources:

            # get type for source
            current_source_type = current_source.source_type

            # retrieve value for that source from the dictionary
            if current_source_type in counts_OUT:

                # source type is in the dictionary.  Retrieve value.
                current_type_count = counts_OUT[ current_source_type ]

                # increment
                current_type_count += 1

                # store new value.
                counts_OUT[ current_source_type ] = current_type_count

            else:

                # source type not in dictionary.  Hmmm.  Set its entry to 1.
                counts_OUT[ current_source_type ] = 1

            #-- END conditional to increment count for current type.

        #-- END loop over sources --#

        return counts_OUT

    #-- END method get_source_counts_by_type() --#

#= End Article_Data Model ===========================================================


# Article_Person model
class Article_Person( models.Model ):

    #RELATION_TYPE_CHOICES = (
    #    ( "author", "Article Author" ),
    #    ( "source", "Article Source" )
    #)

    article = models.ForeignKey( Article_Data )
    person = models.ForeignKey( Person, blank = True, null = True )
    #relation_type = models.CharField( max_length = 255, choices = RELATION_TYPE_CHOICES )

    # meta class so we know this is an abstract class.
    class Meta:
        abstract = True

    #----------------------------------------------------------------------
    # methods
    #----------------------------------------------------------------------

    def __unicode__( self ):
        if ( self.person is not None ):
            string_OUT = self.person.last_name + ", " + self.person.first_name
        else:
            string_OUT = 'empty Article_Person instance'
        return string_OUT

    #
    # Returns information on the article associated with this person.
    #
    def get_article_info( self ):

        # return reference
        string_OUT = ''

        # declare variables
        article_instance = None

        # get article instance
        article_instance = self.article

        string_OUT = str( article_instance )

        return string_OUT

    #-- END method get_article_info() --#

    get_article_info.short_description = 'Article Info.'

    #
    # Returns information on the article associated with this person.
    #
    def get_person_id( self ):

        # return reference
        id_OUT = ''

        # declare variables
        my_person = None

        # get current person.
        my_person = self.person

        # see if there is a person
        if ( my_person is not None ):

            # are we also loading the person?
            id_OUT = my_person.id

        #-- END check to make sure source has a person.

        return id_OUT

    #-- END method get_person_id() --#


    def is_connected( self, param_dict_IN = None ):

        """
            Method: is_connected()

            Purpose: accepts a parameter dictionary for specifying more rigorous
               ways of including or ommitting connections.  In Article_Person,
               and in child Article_Author, just always returns true if there is
               a person reference.  In Article_Source, examines the
               categorization of the source to determine if the source is
               eligible to be classified as "connected" to the authors of the
               story.  If "connected", returns True.  If not, returns False.  By
               default, "Connected" = source of type "individual" with contact
               type of "direct" or "event".  Eventually we can make this more
               nuanced, allow filtering here based on input parameters, and
               allow different types of connections to be requested.  For now,
               just need it to work.

            Params:
            - param_dict_IN - source whose connectedness we need to check.

            Returns:
            - boolean - If "connected", returns True.  If not, returns False.
        """

        # return reference
        is_connected_OUT = True

        # declare variables
        current_person_id = ''

        # does the source have a person ID?
        current_person_id = self.get_person_id()
        if ( not ( current_person_id ) ):

            # no person ID, so can't make a relation
            is_connected_OUT = False

        #-- END check to see if there is an associated person --#

        return is_connected_OUT

    #-- END method is_connected() --#


#= END Article_Person Model ======================================================


# Article_Author model
class Article_Author( Article_Person ):

    AUTHOR_TYPE_TO_ID_MAP = {
        "staff" : 1,
        "editorial" : 2,
        "government" : 3,
        "business" : 4,
        "organization" : 5,
        "public" : 6,
        "other" : 7
    }

    AUTHOR_TYPE_CHOICES = (
        ( "staff", "News Staff" ),
        ( "editorial", "Editorial Staff" ),
        ( "government", "Government Official" ),
        ( "business", "Business Representative" ),
        ( "organization", "Other Organization Representative" ),
        ( "public", "Member of the Public" ),
        ( "other", "Other" )
    )

    author_type = models.CharField( max_length = 255, choices = AUTHOR_TYPE_CHOICES )

    #----------------------------------------------------------------------
    # methods
    #----------------------------------------------------------------------

    def __unicode__( self ):
        if ( self.person is not None ):
            string_OUT = self.person.last_name + ", " + self.person.first_name + " (" + self.author_type + ")"
        else:
            string_OUT = self.author_type
        return string_OUT

#= End Article_Author Model ======================================================


# Article_Source model
class Article_Source( Article_Person ):

    PARAM_SOURCE_CAPACITY_INCLUDE_LIST = 'include_capacities'
    PARAM_SOURCE_CAPACITY_EXCLUDE_LIST = 'exclude_capacities'

    # Source type stuff
    SOURCE_TYPE_INDIVIDUAL = 'individual'
    SOURCE_TYPE_TO_ID_MAP = {
        "anonymous" : 1,
        SOURCE_TYPE_INDIVIDUAL : 2,
        "organization" : 3,
        "document" : 4,
        "other" : 5
    }

    SOURCE_TYPE_CHOICES = (
        ( "anonymous", "Anonymous/Unnamed" ),
        ( SOURCE_TYPE_INDIVIDUAL, "Individual Person" ),
        ( "organization", "Organization" ),
        ( "document", "Document" ),
        ( "other", "Other" )
    )

    # Source contact type stuff
    SOURCE_CONTACT_TYPE_DIRECT = 'direct'
    SOURCE_CONTACT_TYPE_EVENT = 'event'

    SOURCE_CONTACT_TYPE_TO_ID_MAP = {
        SOURCE_CONTACT_TYPE_DIRECT : 1,
        SOURCE_CONTACT_TYPE_EVENT : 2,
        "past_quotes" : 3,
        "document" : 4,
        "other" : 5
    }

    SOURCE_CONTACT_TYPE_CHOICES = (
        ( SOURCE_CONTACT_TYPE_DIRECT, "Direct contact" ),
        ( SOURCE_CONTACT_TYPE_EVENT, "Press conference/event" ),
        ( "past_quotes", "Past quotes/statements" ),
        ( "document", "Press release/document" ),
        ( "other", "Other" )
    )

    # Source capacity stuff
    SOURCE_CAPACITY_TO_ID_MAP = {
        "government" : 1,
        "police" : 2,
        #"legal" : "?",
        "business" : 3,
        "labor" : 4,
        "education" : 5,
        "organization" : 6,
        "expert" : 7,
        "individual" : 8,
        "other" : 9
    }

    SOURCE_CAPACITY_CHOICES = (
        ( "government", "Government Source" ),
        ( "police", "Police Source" ),
        #( "legal", "Legal Source" ),
        ( "business", "Business Source" ),
        ( "labor", "Labor Source" ),
        ( "education", "Education Source" ),
        ( "organization", "Other Organization Source" ),
        ( "expert", "Expert Opinion" ),
        ( "individual", "Personal Opinion" ),
        ( "other", "Other" )
    )

    # localness stuff
    LOCALNESS_TO_ID_MAP = {
        "none" : 1,
        "local" : 2,
        #"regional" : "?",
        "state" : 3,
        "national" : 4,
        "international" : 5,
        "other" : 6
    }

    LOCALNESS_CHOICES = (
        ( "none", "None" ),
        ( "local", "Local" ),
        #( "regional", "Regional" ),
        ( "state", "State" ),
        ( "national", "National" ),
        ( "international", "International" ),
        ( "other", "Other" )
    )

    source_type = models.CharField( max_length = 255, choices = SOURCE_TYPE_CHOICES )
    title = models.CharField( max_length = 255, blank = True )
    more_title = models.CharField( max_length = 255, blank = True )
    organization = models.ForeignKey( Organization, blank = True, null = True )
    document = models.ForeignKey( Document, blank = True, null = True )
    topics = models.ManyToManyField( Topic, blank = True )
    source_contact_type = models.CharField( max_length = 255, choices = SOURCE_CONTACT_TYPE_CHOICES )
    source_capacity = models.CharField( max_length = 255, choices = SOURCE_CAPACITY_CHOICES )
    #count_direct_quote = models.IntegerField( "Count direct quotes", default = 0 )
    #count_indirect_quote = models.IntegerField( "Count indirect quotes", default = 0 )
    #count_from_press_release = models.IntegerField( "Count quotes from press release", default = 0 )
    #count_spoke_at_event = models.IntegerField( "Count quotes from public appearances", default = 0 )
    #count_other_use_of_source = models.IntegerField( "Count other uses of source", default = 0 )
    localness = models.CharField( max_length = 255, choices = LOCALNESS_CHOICES )
    notes = models.TextField( blank = True )

    #----------------------------------------------------------------------
    # methods
    #----------------------------------------------------------------------

    def __unicode__( self ):
        # return reference
        string_OUT = ''

        if ( self.source_type == "individual" ):
            if ( self.person is not None ):
                string_OUT = self.person.last_name + ", " + self.person.first_name
            else:
                if ( self.title != '' ):
                    string_OUT = self.title
                else:
                    string_OUT = "individual"
        elif ( self.source_type == "organization" ):
            if ( self.organization is not None ):
                string_OUT = self.organization.name
            else:
                string_OUT = self.title
        elif ( self.source_type == "document" ):
            if ( self.document is not None ):
                string_OUT = self.document.name
            else:
                string_OUT = self.notes
        #elif ( self.source_type == "anonymous" ):
        #    string_OUT =

        string_OUT = string_OUT + " (" + self.source_type + ")"

        return string_OUT

    #-- END method __unicode__() --#


    def is_connected( self, param_dict_IN = None ):

        """
            Method: is_connected()

            Purpose: accepts a parameter dictionary, examines its categorization
               to determine if the source is eligible to be classified as
               "connected" to the authors of the story.  If "connected", returns
               True.  If not, returns False.  By default, "Connected" = source
               of type "individual" with contact type of "direct" or "event".
               The parameter dictionary allows one to extend the filtering
               options here without changing the method signature.  First
               add-ons are include and exclude lists for source capacity.
               Eventually we should move everything that is in this method into
               params, so defaults aren't set in code.  For now, just need it to
               work.

            Params:
            - source_IN - source whose connectedness we need to check.

            Returns:
            - boolean - If "connected", returns True.  If not, returns False.
        """

        # return reference
        is_connected_OUT = True

        # declare variables
        current_source_type = ''
        current_source_contact_type = ''
        current_source_capacity = ''
        capacity_in_list_IN = None
        capacity_not_in_list_IN = None

        # first, call parent method (takes care of checking to see if there is a
        #    person in the person reference).
        is_connected_OUT = super( Article_Source, self ).is_connected( param_dict_IN )

        # Now, check the source type, contact type.
        current_source_type = self.source_type
        current_source_contact_type = self.source_contact_type

        # correct source type?
        if ( current_source_type != Article_Source.SOURCE_TYPE_INDIVIDUAL ):

            # no.  Set output flag to false.
            is_connected_OUT = False

        #-- END check of source type --#

        # contact type OK?
        if ( ( current_source_contact_type != Article_Source.SOURCE_CONTACT_TYPE_DIRECT ) and ( current_source_contact_type != Article_Source.SOURCE_CONTACT_TYPE_EVENT ) ):

            # contact type not direct or event.  This person is not connected.
            is_connected_OUT = False

        #-- END contact type check. --#

        # Got a param dict?
        if ( param_dict_IN is not None ):

            # we have a dict.  Do we have list of source capacities to either
            #    include or exclude?
            if Article_Source.PARAM_SOURCE_CAPACITY_INCLUDE_LIST in param_dict_IN:
                
                # get include list.
                capacity_in_list_IN = param_dict_IN[ Article_Source.PARAM_SOURCE_CAPACITY_INCLUDE_LIST ]

                # see if our capacity is in the include list.
                current_source_capacity = self.source_capacity

                if current_source_capacity not in capacity_in_list_IN:

                    # not in include list, so not connected.
                    is_connected_OUT = False

                #-- END check to see if we fail the test. --#

            #-- END check to see if we have an include list. --#

            if Article_Source.PARAM_SOURCE_CAPACITY_EXCLUDE_LIST in param_dict_IN:

                # get include list.
                capacity_not_in_list_IN = param_dict_IN[ Article_Source.PARAM_SOURCE_CAPACITY_EXCLUDE_LIST ]

                # see if our capacity is in the include list.
                current_source_capacity = self.source_capacity

                if current_source_capacity in capacity_not_in_list_IN:

                    # capacity is in the exclude list, so not connected.
                    is_connected_OUT = False

                #-- END check to see if we fail the test. --#

            #-- END check to see if we have an exclude list. --#

        #-- END check to see if we have params passed in. --#

        return is_connected_OUT

    #-- END method is_connected() --#
    

#= End Article_Source Model ======================================================


# Source_Organization model
class Source_Organization( models.Model ):

    article_source = models.ForeignKey( Article_Source )
    organization = models.ForeignKey( Organization, blank = True, null = True )
    title = models.CharField( max_length = 255, blank = True )

    #----------------------------------------------------------------------
    # methods
    #----------------------------------------------------------------------

    def __unicode__( self ):
        # return reference
        string_OUT = ''

        # got an organization?
        if ( self.organization is not None ):
            string_OUT = self.organization.name

        # got a title?
        if ( self.title != '' ):
            string_OUT = string_OUT + " ( " + self.title + " )"
        return string_OUT

#= End Source_Organization Model ======================================================


# Source_Organization model
#class Source_Organization( models.Model ):

#    article_source = models.ForeignKey( Article_Source, blank = True, null = True )
#    organization = models.ForeignKey( Organization, blank = True, null = True )
#    title = models.CharField( max_length = 255, blank = True )

    #----------------------------------------------------------------------
    # methods
    #----------------------------------------------------------------------

#    def __unicode__( self ):

        # return reference
#        string_OUT = ''

        # declare variables
#        delimiter = ''

        # figure out how to present
#        if ( self.organization is not None ):
#            string_OUT = string_OUT + self.organization.name
#            delimiter = ' - '
#        if ( self.title != '' ):
#            string_OUT = string_OUT + delimiter + self.title

#        return string_OUT

#= End Source_Organization Model ======================================================


# Article_Location model
#class Article_Location( models.Model ):

#    article = models.ForeignKey( Article )
#    location = models.ForeignKey( Location )
#    rank = models.IntegerField()

    #----------------------------------------------------------------------
    # methods
    #----------------------------------------------------------------------

#    def __unicode__( self ):
        #string_OUT = self.rank + " - " + self.location.name
#        string_OUT = '%d - %s' % ( self.rank, self.location.name )
#        return string_OUT

#= End Article_Location Model ======================================================


# Import_Error model
class Import_Error( models.Model ):

    unique_identifier = models.CharField( max_length = 255, blank = True )
    archive_source = models.CharField( max_length = 255, blank = True, null = True )
    item = models.TextField( blank = True, null = True )
    message = models.TextField( blank = True, null = True )
    exception = models.TextField( blank = True, null = True )
    batch_identifier = models.CharField( max_length = 255, blank = True )
    create_date = models.DateTimeField( auto_now_add = True )
    last_modified = models.DateTimeField( auto_now = True )

    #----------------------------------------------------------------------
    # methods
    #----------------------------------------------------------------------

    def __unicode__( self ):
        #string_OUT = self.rank + " - " + self.location.name
        string_OUT = '%d - %s (%s): %s' % ( self.id, self.unique_identifier, self.item, self.message )
        return string_OUT

#= End Import_Error Model ======================================================


# Temp_Section model
class Temp_Section( models.Model ):

    #----------------------------------------------------------------------
    # constants-ish
    #----------------------------------------------------------------------

    NEWS_SECTION_NAME_LIST = [ "Business", "City and Region", "Front Page", "Lakeshore", "Religion", "Special", "Sports", "State" ]
    
    # variables for building nuanced queries in django.
    # query for bylines of in-house authors.
    Q_IN_HOUSE_AUTHOR = Q( author_varchar__iregex = r'.* */ *THE GRAND RAPIDS PRESS$' ) | Q( author_varchar__iregex = r'.* */ *PRESS .* EDITOR$' ) | Q( author_varchar__iregex = r'.* */ *GRAND RAPIDS PRESS .* BUREAU$' ) | Q( author_varchar__iregex = r'.* */ *SPECIAL TO THE PRESS$' )

    #----------------------------------------------------------------------
    # instance variables
    #----------------------------------------------------------------------

    name = models.CharField( max_length = 255, blank = True, null = True )
    total_articles = models.IntegerField( blank = True, null = True, default = 0 )
    in_house_articles = models.IntegerField( blank = True, null = True, default = 0 )
    external_articles = models.IntegerField( blank = True, null = True, default = 0 )
    external_booth = models.IntegerField( blank = True, null = True, default = 0 )
    in_house_authors = models.IntegerField( blank = True, null = True, default = 0 )
    percent_in_house = models.DecimalField( max_digits = 21, decimal_places = 20, blank = True, null = True, default = 0 )
    percent_external = models.DecimalField( max_digits = 21, decimal_places = 20, blank = True, null = True, default = 0 )
    
    create_date = models.DateTimeField( auto_now_add = True )
    last_modified = models.DateTimeField( auto_now = True )

    #----------------------------------------------------------------------
    # instance methods
    #----------------------------------------------------------------------

    def __unicode__( self ):
    
        #string_OUT = self.rank + " - " + self.location.name
        string_OUT = '%d - %s' % ( self.id, self.name )
        return string_OUT

    #-- END method __unicode__() --#


    def get_external_article_count( self, *args, **kwargs ):
    
        '''
        Retrieves count of articles in the current section whose "author_varchar"
           column indicate that the articles were not written by the Grand
           Rapids Press newsroom.
        '''
    
        # return reference
        value_OUT = -1
        
        # Declare variables
        article_qs = None 
        name_q = None
        author_q = None
       
        # get articles.
        name_q = Q( section = self.name )
        author_q =  Temp_Section.Q_IN_HOUSE_AUTHOR
        
        #logging.debug( str( name_q ) )
        #logging.debug( str( author_q ) )
        
        article_qs = Article.objects.filter( name_q )
        article_qs = article_qs.exclude( author_q )
        
        #logging.debug( article_qs.query )
        
        # get count.
        value_OUT = article_qs.count()
        
        return value_OUT
        
    #-- END method get_external_article_count --#


    def get_external_booth_count( self, *args, **kwargs ):
    
        '''
        Retrieves count of articles in the current section whose "author_varchar"
           column indicate that the articles were not written by the Grand
           Rapids Press newsroom, but were implemented in another Booth company
           newsroom.
        '''
    
        # return reference
        value_OUT = -1
        
        # Declare variables
        article_qs = None
        name_q = None
        author_q = None
        
        # get articles.
        name_q = Q( section = self.name )
        author_q =  Q( author_varchar__iregex = r'.* */ *GRAND RAPIDS PRESS NEWS SERVICE$' )
        
        #logging.debug( str( name_q ) )
        #logging.debug( str( author_q ) )
        
        article_qs = Article.objects.filter( name_q, author_q )
        
        # get count.
        value_OUT = article_qs.count()
        
        return value_OUT
        
    #-- END method get_external_article_count --#


    def get_in_house_article_count( self, *args, **kwargs ):
    
        '''
        Retrieves count of articles in the current section whose "author_varchar"
           column indicate that the articles were written by the actual Grand
           Rapids Press newsroom.
        '''
    
        # return reference
        value_OUT = -1
        
        # Declare variables
        article_qs = None 
        
        # get articles.
        article_qs = Article.objects.filter( Q( section = self.name ), Temp_Section.Q_IN_HOUSE_AUTHOR )
        
        # get count.
        value_OUT = article_qs.count()
        
        return value_OUT
        
    #-- END method get_in_house_article_count --#


    def get_in_house_author_count( self, *args, **kwargs ):
    
        '''
        Retrieves count of distinct author strings (including joint bylines
           separate from either individual's name, and including misspellings)
           of articles in the current section whose "author_varchar" column
           indicate that the articles were implemented by the actual Grand
           Rapids Press newsroom.
        '''
    
        # return reference
        value_OUT = -1
        
        # Declare variables
        my_cursor = None
        query_string = ""
        my_row = None
        
        # get database cursor
        my_cursor = connection.cursor()
        
        # create SQL query string
        query_string = "SELECT COUNT( DISTINCT CONVERT( LEFT( author_varchar, LOCATE( ' / ', author_varchar ) ), CHAR ) ) as name_count"
        query_string += " FROM sourcenet_article"
        query_string += " WHERE section = '" + self.name + "'"
        query_string += "     AND"
        query_string += "     ("
        query_string += "         ( UPPER( author_varchar ) REGEXP '.* */ *THE GRAND RAPIDS PRESS$' )"
        query_string += "         OR ( UPPER( author_varchar ) REGEXP '.* */ *PRESS .* EDITOR$' )"
        query_string += "         OR ( UPPER( author_varchar ) REGEXP '.* */ *GRAND RAPIDS PRESS .* BUREAU$' )"
        query_string += "         OR ( UPPER( author_varchar ) REGEXP '.* */ *SPECIAL TO THE PRESS$' )"
        query_string += "     )"
        
        # execute query.
        my_cursor.execute( query_string )
        
        # get the row that is returned.
        my_row = my_cursor.fetchone()
        
        # get count.
        value_OUT = my_row[ 0 ]
        
        return value_OUT
        
    #-- END method get_in_house_author_count --#


    def get_total_article_count( self, *args, **kwargs ):
    
        '''
        Retrieves count of articles whose "section" column contain the current
           section instance's name.
        '''
    
        # return reference
        value_OUT = -1
        
        # Declare variables
        article_qs = None 
        
        # get articles.
        article_qs = Article.objects.filter( section = self.name )
        
        # get count.
        value_OUT = article_qs.count()
        
        return value_OUT
        
    #-- END method get_total_article_count --#
    

    def process_column_values( self, do_save_IN = False, *args, **kwargs ):
    
        '''
        Generates values for all columns for section name passed in.
        '''
    
        # return reference
        status_OUT = "Success!"
        
        # Declare variables
        my_total_articles = -1
        my_in_house_articles = -1
        my_external_articles = -1
        my_external_booth = -1
        my_in_house_authors = -1
        my_percent_in_house = -1
        my_percent_external = -1
        
        # initialize Decimal Math
        getcontext().prec = 20
        
        # get values.
        my_total_articles = self.get_total_article_count()
        my_in_house_articles = self.get_in_house_article_count()
        my_external_articles = self.get_external_article_count()
        my_external_booth = self.get_external_booth_count()
        my_in_house_authors = self.get_in_house_author_count()

        # derive additional values

        # percent of articles that are in-house
        if ( ( my_in_house_articles >= 0 ) and ( my_total_articles > 0 ) ):

            # divide in-house by total
            my_percent_in_house = Decimal( my_in_house_articles ) / Decimal( my_total_articles )
            
        else:
        
            # either no in-house or total is 0.  Set to 0.
            my_percent_in_house = 0
            
        #-- END check to make sure values are OK for calculating percent --#
        
        # percent of articles that are external
        if ( ( my_external_articles >= 0 ) and ( my_total_articles > 0 ) ):

            # divide external by total
            my_percent_external = Decimal( my_external_articles ) / Decimal( my_total_articles )
            
        else:
        
            # either no external or total is 0.  Set to 0.
            my_percent_external = 0
            
        #-- END check to make sure values are OK for calculating percent --#
        
        # set values
        self.total_articles = my_total_articles
        self.in_house_articles = my_in_house_articles
        self.external_articles = my_external_articles
        self.external_booth = my_external_booth
        self.in_house_authors = my_in_house_authors
        self.percent_in_house = my_percent_in_house
        self.percent_external = my_percent_external
        
        # save?
        if ( do_save_IN == True ):
        
            # save.
            self.save()
        
        #-- END check to see if we save or not. --#
        
        return status_OUT
        
    #-- END method process_column_values --#


    #----------------------------------------------------------------------
    # class methods
    #----------------------------------------------------------------------

    @classmethod
    def get_instance_for_name( self, name_IN = "",  *args, **kwargs ):
    
        '''
        Generates values for all columns for section name passed in.
        '''
    
        # return reference
        instance_OUT = None
        
        # Declare variables
        me = "get_instance_for_name"
        result_qs = None
        result_count = -1
        
        # got a name?
        if ( name_IN ):

            # try to get Temp_Section instance with name = name_IN
            try:
            
                instance_OUT = self.objects.get( name = name_IN )

            except MultipleObjectsReturned:

                # error!
                loging.debug( "In " + me + ": ERROR - more than one match for name \"" + name_IN + "\" when there should only be one.  Returning nothing." )

            except ObjectDoesNotExist:

                # either nothing or negative count (either implies no match).
                #    Return new instance.
                instance_OUT = Temp_Section()
                instance_OUT.name = name_IN
                
            #-- END try to retrieve instance for name passed in. --#
            
        #-- END check to see if name passed in --#
        
        return instance_OUT
        
    #-- END class method get_instance_for_name --#


#= End Temp_Section Model ======================================================