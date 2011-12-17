#================================================================================
# Imports
#================================================================================

# python imports
import datetime
from decimal import Decimal
from decimal import getcontext
import gc
import logging
import pickle
import re

# nameparse import
# http://pypi.python.org/pypi/nameparser
from nameparser import HumanName

'''
Code sample:

from nameparser import HumanName
>>> test = HumanName( "Jonathan Scott Morgan" )
>>> test
<HumanName : [
        Title: '' 
        First: 'Jonathan' 
        Middle: 'Scott' 
        Last: 'Morgan' 
        Suffix: ''
]>
>>> import pickle
>>> test2 = pickle.dumps( test )
>>> test3 = pickle.loads( test2 )
>>> test3.__eq__( test2 )
False
>>> test3.__eq__( test )
True
>>> test3.first
u'Jonathan'
>>> test3.middle
u'Scott'
>>> test3.last
u'Morgan'
>>> test3.title
u''
>>> test3.suffix
u''
>>> if ( test3 == test ):
...     print( "True!" )
... else:
...     print( "False!" )
... 
True!
'''

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
import django.db


#================================================================================
# Shared variables and functions
#================================================================================

'''
Gross debugging code, shared across all models.
'''

DEBUG = True
STATUS_SUCCESS = "Success!"
DEFAULT_DATE_FORMAT = "%Y-%m-%d"
REGEX_BEGINS_WITH_BY = re.compile( r'^BY ', re.IGNORECASE )

def output_debug( message_IN, method_IN = "", indent_with_IN = "" ):
    
    '''
    Accepts message string.  If debug is on, passes it to print().  If not,
       does nothing for now.
    '''
    
    # declare variables
    my_message = ""

    # got a message?
    if ( message_IN ):
    
        # only print if debug is on.
        if ( DEBUG == True ):
        
            my_message = message_IN
        
            # got a method?
            if ( method_IN ):
            
                # We do - append to front of message.
                my_message = "In " + method_IN + ": " + my_message
                
            #-- END check to see if method passed in --#
            
            # indent?
            if ( indent_with_IN ):
                
                my_message = indent_with_IN + my_message
                
            #-- END check to see if we indent. --#
        
            # debug is on.  For now, just print.
            print( my_message )
            logging.debug( my_message )
        
        #-- END check to see if debug is on --#
    
    #-- END check to see if message. --#

#-- END method output_debug() --#


def get_dict_value( dict_IN, name_IN, default_IN = None ):

    '''
    Convenience method for getting value for name of dictionary entry that might
       or might not exist in dictionary.
    '''
    
    # return reference
    value_OUT = default_IN

    # got a dict?
    if ( dict_IN ):
    
        # got a name?
        if ( name_IN ):

            # name in dictionary?
            if ( name_IN in dict_IN ):
            
                # yup.  Get it.
                value_OUT = dict_IN[ name_IN ]
                
            else:
            
                # no.  Return default.
                value_OUT = default_IN
            
            #-- END check to see if start date in arguments --#
            
        else:
        
            value_OUT = default_IN
            
        #-- END check to see if name passed in. --#
        
    else:
    
        value_OUT = default_IN
        
    #-- END check to see if dict passed in. --#

    return value_OUT

#-- END method get_dict_value() --#


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

#= End Location Model ===========================================================

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
    name_prefix = models.CharField( max_length = 255, blank = True, null = True )
    name_suffix = models.CharField( max_length = 255, blank = True, null = True )
    full_name_string = models.CharField( max_length = 255, blank = True, null = True )
    gender = models.CharField( max_length = 6, choices = GENDER_CHOICES )
    title = models.CharField( max_length = 255, blank = True )
    nameparser_pickled = models.TextField( blank = True, null = True )
    notes = models.TextField( blank = True )

    # Meta-data for this class.
    class Meta:
        ordering = [ 'last_name', 'first_name', 'middle_name' ]


    #----------------------------------------------------------------------
    # static methods
    #----------------------------------------------------------------------
    
    
    @staticmethod
    def get_person_for_name( name_IN, create_if_no_match_IN = False ):
    
        '''
        This method accepts the full name of a person.  Uses NameParse object to
           parse name into prefix/title, first name, middle name(s), last name,
           and suffix.  Looks first for an exact person match.  If one found,
           returns it.  If none found, returns new Person instance with name
           stored in it.
        preconditions: None.
        postconditions: Looks first for an exact person match.  If one found,
           returns it.  If none found, returns new Person instance with name
           stored in it.  If multiple matches found, error, so will return None.
           If new Person instance returned, it will not have been saved.  If you
           want that person to be in the database, you have to save it yourself.
        '''
        
        # return reference
        instance_OUT = None
        
        # declare variables.
        me = "get_person_for_name"
        person_qs = None
        person_count = -1
        
        # got a name?
        if ( name_IN ):
        
            # try to retrieve person for name.
            person_qs = Person.look_up_person_from_name( name_IN )
            
            # got a match?
            person_count = person_qs.count()
            if ( person_count == 1 ):
            
                # got one match.  Return it.
                instance_OUT = person_qs.get()
                
                output_debug( "In " + me + ": found single match for name: " + name_IN )
                
            elif( person_count == 0 ):
            
                # no matches.  What do we do?
                if ( create_if_no_match_IN == True ):
                
                    # create new Person!
                    instance_OUT = Person()
                    
                    # store name
                    instance_OUT.set_name( name_IN )
                    
                    output_debug( "In " + me + ": no match for name: " + name_IN + "; so, creating new Person!" )
                    
                else:
                
                    # return None!
                    instance_OUT = None
                    
                    output_debug( "In " + me + ": no match for name: " + name_IN + "; so, returning Nones!" )
                    
                #-- END check to see if we create on no match. --#
                
            else:
            
                # Multiple matches.  Trouble.
                output_debug( "In " + me + ": multiple matches for name \"" + name_IN + ".  Returning None." )
                instance_OUT = None
            
            #-- END check count of persons returned. --#
            
        else:
        
            # No name passed in.  Nothing to return.
            output_debug( "In " + me + ": no name passed in, so returning None." )
            instance_OUT = None
        
        #-- END check for name string passed in. --#

        return instance_OUT
    
    #-- END method get_person_for_name() --#


    @staticmethod
    def look_up_person_from_name( name_IN = "" ):
    
        '''
        This method accepts the full name of a person.  Uses NameParse object to
           parse name into prefix/title, first name, middle name(s), last name,
           and suffix.  Looks first for an exact person match.  If one found,
           returns it.  If none found, if create flag is true, returns new Person
           instance with name stored in it.  If flag if false, returns None.
        preconditions: None.
        postconditions: If new Person instance returned, it will not have been
           saved.  If you want that person to be in the database, you have to
           save it yourself.
        '''
        
        # return reference
        qs_OUT = None
        
        # declare variables.
        me = "look_up_person_from_name"
        parsed_name = None
        prefix = ""
        first = ""
        middle = ""
        last = ""
        suffix = ""
        person_qs = None
        person_count = -1
                
        # got a name?
        if ( name_IN ):
        
            # yes.  Parse it using HumanName class from nameparser.
            parsed_name = HumanName( name_IN )          
            
            # Use parsed values to build a search QuerySet.  First, get values.
            prefix = parsed_name.title
            first = parsed_name.first
            middle = parsed_name.middle
            last = parsed_name.last
            suffix = parsed_name.suffix
            
            # build up queryset.
            qs_OUT = Person.objects.all()
            
            # got a prefix?
            if ( prefix ):
    
                # add value to query
                qs_OUT = qs_OUT.filter( name_prefix__iexact = prefix )
                
            #-- END check for prefix --#
            
            # first name
            if ( first ):
    
                # add value to query
                qs_OUT = qs_OUT.filter( first_name__iexact = first )
                
            #-- END check for first name --#
            
            # middle name
            if ( middle ):
    
                # add value to query
                qs_OUT = qs_OUT.filter( middle_name__iexact = middle )
                
            #-- END check for middle name --#

            # last name
            if ( last ):
    
                # add value to query
                qs_OUT = qs_OUT.filter( last_name__iexact = last )
                
            #-- END check for last name --#
            
            # suffix
            if ( suffix ):
    
                # add value to query
                qs_OUT = qs_OUT.filter( name_suffix__iexact = suffix )
                
            #-- END suffix --#
            
        else:
        
            # No name, returning None
            output_debug( "In " + me + ": no name passed in, returning None." )
        
        #-- END check to see if we have a name. --#
        
        return qs_OUT
    
    #-- END static method look_up_person_from_name() --#
    

    #----------------------------------------------------------------------
    # instance methods
    #----------------------------------------------------------------------

    def __unicode__( self ):
 
        # return reference
        string_OUT = ''
 
        if ( self.id ):
        
            string_OUT = str( self.id ) + " - "
            
        #-- END check to see if ID --#
                
        string_OUT = self.last_name + ', ' + self.first_name
        
        # middle name?
        if ( self.middle_name ):
        
            string_OUT += " " + self.middle_name
            
        #-- END middle name check --#

        if ( self.title ):
        
            string_OUT = string_OUT + " ( " + self.title + " )"
            
        #-- END check to see if we have a title. --#
 
        return string_OUT

    #-- END method __unicode__() --#


    def set_name( self, name_IN = "" ):
    
        '''
        This method accepts the full name of a person.  Uses NameParse object to
           parse name into prefix/title, first name, middle name(s), last name,
           and suffix.  Stores resulting parsed values in this instance, and also
           stores the pickled name object and the full name string.
        preconditions: None.
        postconditions: Updates values in this instance with values parsed out of
           name passed in.
        '''
        
        # declare variables.
        me = "set_name"
        parsed_name = None
        prefix = ""
        first = ""
        middle = ""
        last = ""
        suffix = ""
                
        # No name, returning None
        output_debug( "In " + me + ": storing name: " + name_IN )

        # got a name?
        if ( name_IN ):
        
            # yes.  Parse it using HumanName class from nameparser.
            parsed_name = HumanName( name_IN )          
            
            # Use parsed values to build a search QuerySet.  First, get values.
            prefix = parsed_name.title
            first = parsed_name.first
            middle = parsed_name.middle
            last = parsed_name.last
            suffix = parsed_name.suffix
            
            # got a prefix?
            if ( prefix ):
    
                # set value
                self.name_prefix = prefix
                
            #-- END check for prefix --#
            
            # first name
            if ( first ):
    
                # set value
                self.first_name = first
                
            #-- END check for first name --#
            
            # middle name
            if ( middle ):
    
                # set value
                self.middle_name = middle
                
            #-- END check for middle name --#

            # last name
            if ( last ):
    
                # set value
                self.last_name = last
                
            #-- END check for last name --#
            
            # suffix
            if ( suffix ):
    
                # set value
                self.name_suffix = suffix
                
            #-- END suffix --#
            
            # Finally, store the full name string (and the pickled object?).
            self.full_name_string = str( parsed_name )
            #self.nameparser_pickled = pickle.dumps( parsed_name )
            
        else:
        
            # No name, returning None
            output_debug( "In " + me + ": no name passed in, returning None." )
        
        #-- END check to see if we have a name. --#
        
    #-- END static method look_up_person_from_name() --#
    

#== END Person Model ===========================================================#


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
    newsbank_code = models.CharField( max_length = 255, null = True, blank = True )
    sections_local_news = models.TextField( blank = True, null = True )
    sections_sports = models.TextField( blank = True, null = True )
    
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

    #----------------------------------------------------------------------------
    # Constants-ish
    #----------------------------------------------------------------------------
    
    
    CODER_USERNAME_AUTOMATED = "automated"
    CODER_USER_AUTOMATED = User.objects.get( username = "automated" )
    
    # parameters that can be passed in to static 
    PARAM_AUTOPROC_ALL = "autoproc_all"
    PARAM_AUTOPROC_AUTHORS = "autoproc_authors"
    PARAM_START_DATE = "start_date"
    PARAM_END_DATE = "end_date"
    PARAM_SINGLE_DATE = "single_date"
    
    
    #----------------------------------------------------------------------------
    # Model fields (persisted in database)
    #----------------------------------------------------------------------------

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
    # text = models.TextField( blank = True ) - moved to related Article_Text instance.
    corrections = models.TextField( blank = True, null = True )
    edition = models.CharField( max_length = 255, blank = True, null = True )
    index_terms = models.TextField( blank = True, null = True )
    archive_source = models.CharField( max_length = 255, blank = True, null = True )
    archive_id = models.CharField( max_length = 255, blank = True, null = True )
    permalink = models.TextField( blank = True, null = True )
    copyright = models.TextField( blank = True, null = True )
    # notes = models.TextField( blank = True, null = True ) - moved to related Article_Notes instance.
    # raw_html = models.TextField( blank = True, null = True ) - moved to related Article_RawData instance.
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

    #----------------------------------------------------------------------------
    # Instance variables and meta-data
    #----------------------------------------------------------------------------

    # Meta-data for this class.
    class Meta:
        ordering = [ 'pub_date', 'section', 'page' ]

    #----------------------------------------------------------------------------
    # class methods
    #----------------------------------------------------------------------------


    @classmethod
    def process_articles( cls, *args, **kwargs ):

        '''
        Accepts parameters inside the kwargs argument.  Based on parameters,
           creates a QuerySet of articles to process, then calls the
           "do_automated_processing" on each, passing it the kwargs passed in to
           this process.
        Preconditions: dates passed in must be in "YYYY-MM-DD" format.
        Postconditions: All kinds of things can happen because of this method.
           There definitely are side-effects, database is updated.
        '''
        
        # return reference
        status_OUT = STATUS_SUCCESS
        
        # declare variables
        me = "classmethod process_articles"
        start_date_IN = None
        end_date_IN = None
        single_date_IN = None
        article_qs = None
        article_count = -1
        current_article = None
        current_status = ""
        articles_processed = -1
        
        # pull in parameters.
        start_date_IN = get_dict_value( kwargs, cls.PARAM_START_DATE )
        end_date_IN = get_dict_value( kwargs, cls.PARAM_END_DATE )
        single_date_IN = get_dict_value( kwargs, cls.PARAM_SINGLE_DATE )
        
        # build QuerySet
        article_qs = cls.objects.all()
        
        # process dates.
        # got a single date?
        if ( single_date_IN ):
            
            # yes - convert to datetime, then filter to publication date of just
            #    that day.
            single_date_IN = datetime.datetime.strptime( single_date_IN, DEFAULT_DATE_FORMAT )
            article_qs = article_qs.filter( pub_date = single_date_IN )
            
        # how about some sort of date range?
        elif ( ( start_date_IN ) or ( end_date_IN ) ):
            
            # got at least a start or end date - filter.
            if ( start_date_IN ):
                
                # filter on start date
                start_date_IN = datetime.datetime.strptime( start_date_IN, DEFAULT_DATE_FORMAT )
                article_qs = article_qs.filter( pub_date__gte = start_date_IN )
                
            #-- END check to see if start date. --#
            
            # end date.
            if ( end_date_IN ):
                
                # filter on start date
                end_date_IN = datetime.datetime.strptime( end_date_IN, DEFAULT_DATE_FORMAT )
                article_qs = article_qs.filter( pub_date__lte = end_date_IN )
                
            #-- END check to see if start date. --#
            
        #-- END date conditional. --#
        
        # Done creating QuerySet.  Got anything to process?
        article_count = article_qs.count()
        articles_processed = 0
        if ( article_count > 0 ):
            
            # Got something.  Loop over the QuerySet, calling the method
            #    do_automated_processing() on each one.
            for current_article in article_qs.iterator():
                
                # increment counter
                articles_processed += 1
                
                # call the method.
                current_status = current_article.do_automated_processing( *args, **kwargs )
                
                # see if status other than success
                if ( current_status != STATUS_SUCCESS ):
                    
                    # error - output
                    output_debug( "ERROR with article " + str( articles_processed ) + " of " + str( article_count ) + " - \"" + str( current_article ) + "\": " + current_status + "\n", me, "=== " )
                    
                else:
                    
                    # Success move on.
                    output_debug( "SUCCESS - Processed article " + str( articles_processed ) + " of " + str( article_count ) + " - \"" + str( current_article ) + "\"\n", me, "=== " )
                
                #-- END status processing. --#
                
            #-- END loop over articles. --#
            
        else:
            
            status_OUT = "Article QuerySet did not contain any articles, so nothing to process."
            
        #-- END check to see if anything to process. --#
                
        return status_OUT

    #-- END static method process_articles() --#


    #----------------------------------------------------------------------------
    # instance methods
    #----------------------------------------------------------------------------


    def __unicode__( self ):

        # start with stuff we should always have.
        string_OUT = str( self.id ) + " - " + self.pub_date.strftime( "%b %d, %Y" )
        
        # Got a section?
        if ( self.section ):
        
            # add section
            string_OUT += ", " + self.section
        
        #-- END check to see if section present.
        
        # Got a page?
        if ( self.page ):
        
            # add page.
            string_OUT += " ( " + str( self.page ) + " )"
            
        #-- END check to see if page. --#
        
        # Unique Identifier?
        if ( self.unique_identifier ):

            # Add UID
            string_OUT += ", UID: " + self.unique_identifier
            
        #-- END check for unique identifier
        
        # headline
        string_OUT += " - " + self.headline
        
        # got a related newspaper?
        if ( self.newspaper ):
        
            # Yes.  Append it.
            string_OUT += " ( " + self.newspaper.name + " )"
            
        elif ( self.source_string ):
        
            # Well, we have a source string.
            string_OUT += " ( " + self.source_string + " )"
            
        #-- END check to see if newspaper present. --#
        
        return string_OUT

    #-- END method __unicode__() --#
    
    
    def do_automated_processing( self, *args, **kwargs ):

        '''
        Accepts parameters to tell which parts of processing to implement, in
           **kwargs.  Tries to pull in any existing automated coding.  If none
           found, makes new coding record for user "automated".  Does requested
           coding, either "all", or just individual parts of records.  Returns
           status.
        preconditions: None
        postconditions: Updates related article_data record for "automated" user.
           If multiple article_coding records found for automated user, outputs
           error message, returns error status, does nothing.
        '''
    
        # return reference
        status_OUT = STATUS_SUCCESS
        
        # declare variables
        me = "do_automated_processing"
        process_all_IN = False
        process_authors_IN = False
        automated_user = None
        my_article_data = None
        latest_status = ""
        do_save_article = True
        do_save_data = False
        
        # parse params
        process_all_IN = get_dict_value( kwargs, self.PARAM_AUTOPROC_ALL, True )
        
        # if not process all, do we process any?
        if ( process_all_IN == False ):

            # how about authors?
            process_authors_IN = get_dict_value( kwargs, self.PARAM_AUTOPROC_AUTHORS, True )
            
        #-- END check to see if we set processing flags by item --#
        
        output_debug( "Input flags: process_all = \"" + str( process_all_IN ) + "\"; process_authors = \"" + str( process_authors_IN ) + "\"", me, "--- " )
        
        # first, see if we have article data for automated coder.
        automated_user = self.CODER_USER_AUTOMATED
        my_article_data = self.get_article_data_for_coder( automated_user )
        
        if ( my_article_data ):
        
            # we do.  Process stuff.
            
            # process authors?
            if ( ( process_all_IN == True ) or ( process_authors_IN == True ) ):
            
                # process authors.
                latest_status = my_article_data.process_author_string()
                do_save_data = True
                
                output_debug( "After calling process_author_string() - " + latest_status, me, "--- " )
                
            #-- End check to see if we process authors --#
            
            # Save Article_Data instance?
            if ( do_save_data ):
                
                my_article_data.save()
                
            #-- END check to see if we save article data --#
            
            # save the article, as well?
            if ( do_save_article == True ):
                
                # We do also save the article itself.
                self.save()
                
            #-- END check to see if we save article. --#
            
        else:
        
            # error making/retrieving article data.
            status_OUT = "No article data returned for automated user ( " + str( automated_user ) + " ).  Doing nothing."
            output_debug( status_OUT, me, "--- " )
            
        #-- END check to see if we have article data. --#
        
        return status_OUT
    
    #-- END method do_automated_processing() --#
    
    
    def get_article_data_for_coder( self, coder_IN = None, *args, **kwargs ):

        '''
        Checks to see if there is a nested article_data instance for the coder
           whose User instance is passed in.  If so, returns it.  If not, creates
           one, places minimum required for save inside, saves, then returns it.
        preconditions: Assumes that you are looking for a single coding record
           for a given user, and that the user won't have multiple.  If the user
           might have more than one coding record, just invoke:
           
           self.article_data_set.filter( coder = <user_instance> )
           
           to get a QuerySet, and see if it returns anything.  If not, call this
           method to create a new one for that user.
        postconditions: If user passed in doesn't have a article_data record,
           this will create one for him or her, save it, and then return it.
        '''
    
        # return reference
        instance_OUT = None
        
        # declare variables
        me = "get_article_data_for_coder"
        article_data_qs = None
        article_data_count = -1
        
        # Do we have a coder passed in?
        if ( coder_IN ):

            # first, see if we have an associated article_data instance already.
            article_data_qs = self.article_data_set.filter( coder = coder_IN )
            
            # what we got back?
            article_data_count = article_data_qs.count()
            
            # if 0, create new, populate, and save.
            if ( article_data_count == 0 ):
            
                # create instance
                instance_OUT = Article_Data()

                # populate
                instance_OUT.article = self
                instance_OUT.coder = coder_IN

                # save article_data instance.
                instance_OUT.save()
                
                output_debug( "Created article_data for " + str( coder_IN ) + ".", me )

            elif ( article_data_count == 1 ):
            
                # one found.  Get and return it.
                instance_OUT = article_data_qs.get()

                output_debug( "Found existing article_data for " + str( coder_IN ) + ".", me )
                
            elif ( article_data_count > 1 ):
            
                # found more than one.  Log error, suggest just pulling QuerySet.
                output_debug( "Found multiple article_data records for " + str( coder_IN ) + ".  Returning None.  If this is expected, try self.article_data_set.filter( coder = <user_instance> ) instead.", me )
                
            #-- END processing based on counts --#
            
        else:
        
            output_debug( "No coder passed in, returning None.", me )

        #-- END check to see if we have a coder --#
        
        return instance_OUT
    
    #-- END method get_article_data_for_coder() --#
    
    
    def set_notes( self, text_IN = "", do_save_IN = True, *args, **kwargs ):
        
        '''
        Accepts a piece of text.  Adds it as a related Article_RawData instance.
           If there is already an Article_RawData instance, we just replace that
           instance's content with the text passed in.  If not, we make one.
        Preconditions: Probably should do this after you've saved the article,
           so there is an ID in it, so this child class will know what article
           it is related to.
        Postconditions: Article_RawData instance is returned, saved if save flag
           is true.
        '''
        
        # return reference
        instance_OUT = None

        # declare variables
        me = "set_notes"
        current_qs = None
        current_count = -1
        current_content = None
        
        # get current text QuerySet
        current_qs = self.article_notes_set
        
        # how many do we have?
        current_count = current_qs.count()
        if ( current_count == 1 ):
            
            # One.  Get it.
            instance_OUT = current_qs.get()
            
        elif ( current_count == 0 ):
            
            # Nothing.  Make new one.
            instance_OUT = Article_Notes()
            instance_OUT.article = self
            instance_OUT.type = "text"
            
        else:
            
            # Either error or more than one (so error).
            output_debug( "Found more than one related Article_Notes.  Doing nothing.", me )
            
        #-- END check to see if have one or not. --#

        if ( instance_OUT ):

            # set the text in the instance.
            instance_OUT.content = text_IN
            
            # save?
            if ( do_save_IN == True ):
                
                # yes.
                instance_OUT.save()
                
            #-- END check to see if we save. --#

        #-- END check to see if instance. --#
        
        return instance_OUT

    #-- END method set_notes() --#
    

    def set_raw_html( self, text_IN = "", do_save_IN = True, *args, **kwargs ):
        
        '''
        Accepts a piece of text.  Adds it as a related Article_RawData instance.
           If there is already an Article_RawData instance, we just replace that
           instance's content with the text passed in.  If not, we make one.
        Preconditions: Probably should do this after you've saved the article,
           so there is an ID in it, so this child class will know what article
           it is related to.
        Postconditions: Article_RawData instance is returned, saved if save flag
           is true.
        '''
        
        # return reference
        instance_OUT = None

        # declare variables
        me = "set_raw_html"
        current_qs = None
        current_count = -1
        current_content = None
        
        # get current text QuerySet
        current_qs = self.article_rawdata_set
        
        # how many do we have?
        current_count = current_qs.count()
        if ( current_count == 1 ):
            
            # One.  Get it.
            instance_OUT = current_qs.get()
            
        elif ( current_count == 0 ):
            
            # Nothing.  Make new one.
            instance_OUT = Article_RawData()
            instance_OUT.article = self
            instance_OUT.type = "html"
            
        else:
            
            # Either error or more than one (so error).
            output_debug( "Found more than one related Article_RawData.  Doing nothing.", me )
            
        #-- END check to see if have one or not. --#

        if ( instance_OUT ):

            # set the text in the instance.
            instance_OUT.content = text_IN
            
            # save?
            if ( do_save_IN == True ):
                
                # yes.
                instance_OUT.save()
                
            #-- END check to see if we save. --#

        #-- END check to see if instance. --#
        
        return instance_OUT

    #-- END method set_raw_html() --#
    

    def set_text( self, text_IN = "", do_save_IN = True, *args, **kwargs ):
        
        '''
        Accepts a piece of text.  Adds it as a related Article_Text instance.
           If there is already an Article_Text instance, we just replace that
           instance's content with the text passed in.  If not, we make one.
        Preconditions: Probably should do this after you've saved the article,
           so there is an ID in it, so this child class will know what article
           it is related to.
        Postconditions: Article_Text instance is returned, saved if save flag
           is true.
        '''
        
        # return reference
        instance_OUT = None

        # declare variables
        me = "set_text"
        current_qs = None
        current_count = -1
        current_content = None
        
        # get current text QuerySet
        current_qs = self.article_text_set
        
        # how many do we have?
        current_count = current_qs.count()
        if ( current_count == 1 ):
            
            # One.  Get it.
            instance_OUT = current_qs.get()
            
        elif ( current_count == 0 ):
            
            # Nothing.  Make new one.
            instance_OUT = Article_Text()
            instance_OUT.article = self
            instance_OUT.type = "text"
            
        else:
            
            # Either error or more than one (so error).
            output_debug( "Found more than one related text.  Doing nothing.", me )
            
        #-- END check to see if have one or not. --#

        if ( instance_OUT ):

            # set the text in the instance.
            instance_OUT.content = text_IN
            
            # save?
            if ( do_save_IN == True ):
                
                # yes.
                instance_OUT.save()
                
            #-- END check to see if we save. --#

        #-- END check to see if instance. --#
        
        return instance_OUT

    #-- END method set_text() --#
    

#= End Article Model ============================================================


# Article_Content model
class Article_Content( models.Model ):

    CONTENT_TYPE_CHOICES = (
        ( "html", "HTML" ),
        ( "text", "Text" ),
        ( "other", "Other" ),
        ( "none", "None" )
    )

    #----------------------------------------------------------------------
    # model fields and meta
    #----------------------------------------------------------------------

    article = models.ForeignKey( Article, unique = True )
    type = models.CharField( max_length = 255, choices = CONTENT_TYPE_CHOICES, blank = True, null = True, default = "none" )
    content = models.TextField()
    create_date = models.DateTimeField( auto_now_add = True )
    last_modified = models.DateTimeField( auto_now = True )

    # meta class so we know this is an abstract class.
    class Meta:
        abstract = True
        ordering = [ 'article', 'last_modified', 'create_date' ]

    #----------------------------------------------------------------------
    # instance variables
    #----------------------------------------------------------------------

    content_description = "content"
    
    #----------------------------------------------------------------------------
    # methods
    #----------------------------------------------------------------------------

    def __unicode__( self ):

        # return reference
        string_OUT = ""
        
        if ( self.id ):
            
            string_OUT += str( self.id ) + " - "
            
        #-- END check to see if ID --#
             
        string_OUT += self.content_description
        
        if ( self.type ):
            
            string_OUT += " of type \"" + self.type + "\""
            
        #-- END check to see if there is a type --#
             
        string_OUT += " for article: " + str( self.article )
        
        return string_OUT

    #-- END method __unicode__() --#

#-- END abstract Article_Content model --#


# Article_Notes model
class Article_Notes( Article_Content ):

    def __unicode__( self ):

        # return reference
        string_OUT = ""
        
        # set content description
        self.content_description = "notes"
        
        # call string method.
        string_OUT = super( Article_Notes, self ).__unicode__()
                
        return string_OUT

    #-- END method __unicode__() --#

#-- END Article_Notes model --#


# Article_RawData model
class Article_RawData( Article_Content ):

    def __unicode__( self ):

        # return reference
        string_OUT = ""
        
        # set content description
        self.content_description = "raw data"
        
        # call string method.
        string_OUT = super( Article_RawData, self ).__unicode__()
        
        return string_OUT

    #-- END method __unicode__() --#

#-- END Article_RawData model --#


# Article_Text model
class Article_Text( Article_Content ):

    def __unicode__( self ):

        # return reference
        string_OUT = ""
        
        # set content description
        self.content_description = "text"
        
        # call string method.
        string_OUT = super( Article_Text, self ).__unicode__()
                
        return string_OUT

    #-- END method __unicode__() --#

#-- END Article_Text model --#


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
    topics = models.ManyToManyField( Topic, blank = True, null = True )
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

    #----------------------------------------------------------------------------
    # methods
    #----------------------------------------------------------------------------

    def __unicode__( self ):

        string_OUT = str( self.id ) + " - " + str( self.article )
        
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


    def process_author_string( self ):
    
        '''
        This method parses the contents of the parent article's author_string
           variable.  Breaks out the organizational affiliation portion of the
           author string (the part after the "/", then splits on commas and
           ampersands to detect multiple authors.  For each author, uses the
           NameParse object to parse their name into prefix/title, first name,
           middle name(s), last name, and suffix.  Looks first for an exact
           person match.  If one found, creates an Article_Author instance to
           link that person to this instance.  If none found, creates a new
           Person, associates it with this instance, then searches for
           potential duplicates, associating any found with the newly created
           Person record.
        preconditions: Assumes that there is an associated article.  If not,
           there will be an exception.
        '''
        
        # return reference
        status_OUT = STATUS_SUCCESS
        
        # declare variables.
        me = "process_author_string"
        my_article = None
        author_string = ""
        author_parts = None
        author_parts_length = -1
        author_organization = ""
        author_name_list = []
        author_and_part = ""
        author_comma_part = ""
        author_name = ""
        author_person = None
        article_author = None
        article_author_qs = None
        
        # get related article.
        if ( self.article ):
        
            # got an article
            my_article = self.article
            
            # get author_string
            author_string = my_article.author_string
            
            # got an author string?
            if ( author_string ):
            
                output_debug( "Processing author string: \"" + author_string + "\"", me, "--- " )
                
                # got an author string.  Parse it.  First, break out organization.
                # split author string on "/"
                author_parts = author_string.split( '/' )
                
                # got two parts?
                author_parts_length = len( author_parts )
                if ( author_parts_length == 2 ):
                
                    # we do.  2nd part = organization
                    author_organization = author_parts[ 1 ]
                    author_organization = author_organization.strip()
                    
                    # first part is author string we look at going forward.
                    author_string = author_parts[ 0 ]
                    author_string = author_string.strip()
                    
                    # also, if string starts with "By ", remove it.
                    author_string = re.sub( REGEX_BEGINS_WITH_BY, "", author_string )
                    
                elif ( ( author_parts_length == 0 ) or ( author_parts_length > 2 ) ):
                
                    # error.  what to do?
                    status_OUT = "ERROR - in " + me + ": splitting on '/' resulted in either an empty array or more than two things.  This isn't right ( " + my_article.author_string + " )."
                    
                #-- END check results of splitting on "/"
                
                # Got something in author_string?
                if ( author_string ):

                    # after splitting, we have a string.  Now need to split on
                    #    "," and " and ".  First, split on " and ".
                    for author_and_part in author_string.split( " and " ):
                    
                        # try splitting on comma.
                        author_parts = author_and_part.split( "," )
                        
                        # got any?
                        if ( len( author_parts ) > 0 ):
                        
                            # yes.  Add each as a name.
                            for author_comma_part in author_parts:
                            
                                # add name to list of names.
                                author_name_list.append( author_comma_part )
                                
                            #-- END loop over authors separated by commas. --#
                            
                        else:
                        
                            # no comma-delimited names.  Add current string to
                            #    name list.
                            author_name_list.append( author_and_part )
                            
                        #-- END check to see if comma-delimited names --#
                        
                    #-- END loop over and-delimited split of authors --#
                    
                    # time to start testing.  Print out the array.
                    output_debug( "In " + me + ": Author list: " + str( author_name_list ) )

                    # For each name in array, see if we already have a matching
                    #    person.
                    for author_name in author_name_list:
                    
                        # first, call Person method to find matching person for
                        #    name.
                        author_person = Person.get_person_for_name( author_name, True )
                        
                        # got a person?
                        if ( author_person ):

                            # if no ID, is new.  Save to database.
                            if ( not( author_person.id ) ):
                            
                                # no ID.  Save the record.
                                author_person.save()
                                output_debug( "In " + me + ": saving new person - " + str( author_person ) )
                                
                            #-- END check to see if new Person. --#
                            
                            # Now, we need to deal with Article_Author instance.
                            #    First, see if there already is one for this
                            #    name.  If so, do nothing.  If not, make one.
                            article_author_qs = self.article_author_set.filter( person = author_person )
                            
                            # got anything?
                            if ( article_author_qs.count() == 0 ):
                                                         
                                # no - add - including organization string.
                                article_author = Article_Author()
                                article_author.article_data = self
                                article_author.person = author_person
                                article_author.organization_string = author_organization
                                article_author.save()
                                
                                output_debug( "In " + me + ": adding Article_Author instance for " + str( author_person ) + "." )

                            else:
                            
                                output_debug( "In " + me + ": Article_Author instance already exists for " + str( author_person ) + "." )
                                
                            #-- END check if need new Article_Author instance --#
    
                        else:
                        
                            output_debug( "In " + me + ": error - no matching person found - must have been a problem looking up name \"" + author_name + "\"" )
    
                        #-- END check to see if person found. --#
                    
                    #-- END loop over author names. --#

                else:                
                    
                    # error.  what to do?
                    status_OUT = "ERROR - in " + me + ": after splitting on '/', no author string left.  Not a standard byline ( " + my_article.author_string + " )."
 
                #-- END check to see if anything in author string.
            
            else:
            
                # No author string - error.
                status_OUT = "ERROR - in " + me + ": no author string, so nothing to do."
            
            #-- END check to see if author string. --#
        
        else:
        
            # No related article. Error.
            status_OUT = "ERROR - in " + me + ": no related article, so nothing to do."
        
        #-- END check to see if we have a related article. --#
        
        return status_OUT
    
    #-- END method process_author_string() --#
    

#= End Article_Data Model =======================================================


# Article_Person model
class Article_Person( models.Model ):

    #RELATION_TYPE_CHOICES = (
    #    ( "author", "Article Author" ),
    #    ( "source", "Article Source" )
    #)

    article_data = models.ForeignKey( Article_Data )
    person = models.ForeignKey( Person, blank = True, null = True )
    #relation_type = models.CharField( max_length = 255, choices = RELATION_TYPE_CHOICES )

    # meta class so we know this is an abstract class.
    class Meta:
        abstract = True

    #----------------------------------------------------------------------
    # methods
    #----------------------------------------------------------------------


    def __unicode__( self ):
        
        # return reference
        string_OUT = ""
        
        if ( self.person is not None ):
        
            string_OUT = self.person.last_name + ", " + self.person.first_name
        
        else:
        
            string_OUT = 'empty Article_Person instance'
        
        #-- END check to see if person. --#
        
        return string_OUT
    
    #-- END method __unicode__() --#


    def get_article_info( self ):
    
        '''
        Returns information on the article associated with this person.
        '''

        # return reference
        string_OUT = ''

        # declare variables
        article_instance = None

        # get article instance
        article_instance = self.article_data.article

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

    author_type = models.CharField( max_length = 255, choices = AUTHOR_TYPE_CHOICES, default = "staff", blank = True, null = True )
    organization_string = models.CharField( max_length = 255, blank = True, null = True )


    #----------------------------------------------------------------------
    # methods
    #----------------------------------------------------------------------


    def __unicode__( self ):
        
        if ( self.person is not None ):
        
            string_OUT = self.person.last_name + ", " + self.person.first_name + " (" + self.author_type + ")"
        
        else:
        
            string_OUT = self.author_type
            
        #-- END check to see if we have a person. --#
        
        return string_OUT

    #-- END __unicode__() method --#


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

    source_type = models.CharField( max_length = 255, choices = SOURCE_TYPE_CHOICES, blank = True, null = True )
    title = models.CharField( max_length = 255, blank = True, null = True )
    more_title = models.CharField( max_length = 255, blank = True, null = True )
    organization = models.ForeignKey( Organization, blank = True, null = True )
    document = models.ForeignKey( Document, blank = True, null = True )
    topics = models.ManyToManyField( Topic, blank = True, null = True )
    source_contact_type = models.CharField( max_length = 255, choices = SOURCE_CONTACT_TYPE_CHOICES, blank = True, null = True )
    source_capacity = models.CharField( max_length = 255, choices = SOURCE_CAPACITY_CHOICES, blank = True, null = True )
    #count_direct_quote = models.IntegerField( "Count direct quotes", default = 0 )
    #count_indirect_quote = models.IntegerField( "Count indirect quotes", default = 0 )
    #count_from_press_release = models.IntegerField( "Count quotes from press release", default = 0 )
    #count_spoke_at_event = models.IntegerField( "Count quotes from public appearances", default = 0 )
    #count_other_use_of_source = models.IntegerField( "Count other uses of source", default = 0 )
    localness = models.CharField( max_length = 255, choices = LOCALNESS_CHOICES, blank = True, null = True )
    notes = models.TextField( blank = True, null = True )

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
    stack_trace = models.TextField( blank = True, null = True )
    batch_identifier = models.CharField( max_length = 255, blank = True )
    item_date = models.DateTimeField( blank = True, null = True )
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

    # Section Name constants.
    NEWS_SECTION_NAME_LIST = [ "Business", "City and Region", "Front Page", "Lakeshore", "Religion", "Special", "Sports", "State" ]
    SECTION_NAME_ALL = "all"
    
    # variables for building nuanced queries in django.
    # query for bylines of in-house authors.
    Q_IN_HOUSE_AUTHOR = Q( author_varchar__iregex = r'.* */ *THE GRAND RAPIDS PRESS$' ) | Q( author_varchar__iregex = r'.* */ *PRESS .* EDITOR$' ) | Q( author_varchar__iregex = r'.* */ *GRAND RAPIDS PRESS .* BUREAU$' ) | Q( author_varchar__iregex = r'.* */ *SPECIAL TO THE PRESS$' )
    
    # date range params
    PARAM_START_DATE = "start_date"
    PARAM_END_DATE = "end_date"
    DEFAULT_DATE_FORMAT = "%Y-%m-%d"
    
    # other article parameters.
    PARAM_CUSTOM_ARTICLE_Q = "custom_article_q"
    
    # section selection parameters.
    PARAM_SECTION_NAME = "section_name"
    PARAM_CUSTOM_SECTION_Q = "custom_section_q"
    PARAM_JUST_PROCESS_ALL = "just_process_all" # set to True if just want sum of all sections, not records for each individual section.  If False, processes each section individually, then generates the "all" record.
    
    # property names for dictionaries of output information.
    OUTPUT_DAY_COUNT = "day_count"
    OUTPUT_ARTICLE_COUNT = "article_count"
    OUTPUT_PAGE_COUNT = "page_count"
    OUTPUT_ARTICLES_PER_DAY = "articles_per_day"
    OUTPUT_PAGES_PER_DAY = "pages_per_day"

    #----------------------------------------------------------------------
    # instance variables
    #----------------------------------------------------------------------

    name = models.CharField( max_length = 255, blank = True, null = True )
    total_days = models.IntegerField( blank = True, null = True, default = 0 )
    total_articles = models.IntegerField( blank = True, null = True, default = 0 )
    in_house_articles = models.IntegerField( blank = True, null = True, default = 0 )
    external_articles = models.IntegerField( blank = True, null = True, default = 0 )
    external_booth = models.IntegerField( blank = True, null = True, default = 0 )
    total_pages = models.IntegerField( blank = True, null = True, default = 0 )
    in_house_pages = models.IntegerField( blank = True, null = True, default = 0 )
    in_house_authors = models.IntegerField( blank = True, null = True, default = 0 )
    percent_in_house = models.DecimalField( max_digits = 21, decimal_places = 20, blank = True, null = True, default = Decimal( '0' ) )
    percent_external = models.DecimalField( max_digits = 21, decimal_places = 20, blank = True, null = True, default = Decimal( '0' ) )
    average_articles_per_day = models.DecimalField( max_digits = 25, decimal_places = 20, blank = True, null = True, default = Decimal( '0' ) )
    average_pages_per_day = models.DecimalField( max_digits = 25, decimal_places = 20, blank = True, null = True, default = Decimal( '0' ) )
    average_in_house_articles_per_day = models.DecimalField( max_digits = 25, decimal_places = 20, blank = True, null = True, default = Decimal( '0' ) )
    average_in_house_pages_per_day = models.DecimalField( max_digits = 25, decimal_places = 20, blank = True, null = True, default = Decimal( '0' ) )
    start_date = models.DateTimeField( blank = True, null = True )
    end_date = models.DateTimeField( blank = True, null = True )
    
    create_date = models.DateTimeField( auto_now_add = True )
    last_modified = models.DateTimeField( auto_now = True )

    #----------------------------------------------------------------------
    # instance methods
    #----------------------------------------------------------------------

    def __unicode__( self ):

        # build the whole string except the id prefix.  Let DEBUG dictate level
        #    of detail.
        if ( DEBUG == True ):
        
            # high detail.
            string_OUT = '%s: tot_day = %d; tot_art = %d; in_art = %d; ext_art= %d; ext_booth = %d; tot_page = %d; in_page = %d; in_auth = %d; avg_art = %f; avg_page = %f; avg_ih_art = %f; avg_ih_page = %f; per_in = %f; per_ext = %f; start = %s; end = %s' % ( self.name + ": ", self.total_days, self.total_articles, self.in_house_articles, self.external_articles, self.external_booth, self.total_pages, self.in_house_pages, self.in_house_authors, self.average_articles_per_day, self.average_pages_per_day, self.average_in_house_articles_per_day, self.average_in_house_pages_per_day, self.percent_in_house, self.percent_external, str( self.start_date ), str( self.end_date ) )
            
        else:
        
            # less detail.
            string_OUT = '%s: tot_art = %d; in_art = %d; ext_art= %d; ext_booth = %d; in_auth = %d; per_in = %f; per_ext = %f; start = %s; end = %s' % ( self.name, self.total_articles, self.in_house_articles, self.external_articles, self.external_booth, self.in_house_authors, self.percent_in_house, self.percent_external, str( self.start_date ), str( self.end_date ) )
            
        #-- Decide what level of detail based on debug or not --#

        # add on ID if one present.
        if ( self.id ):
        
            string_OUT = str( self.id ) + " - " + string_OUT
            
        #-- END check to see if there is an ID. --#
        
        return string_OUT

    #-- END method __unicode__() --#

    
    def add_section_name_filter_to_article_qs( self, qs_IN = None, *args, **kwargs ):
        
        '''
        Checks section name in this instance.  If "all", adds a filter to
           QuerySet where section just has to be one of those in the list of
           locals.  If not all, adds a filter to limit the section to the name.
        Preconditions: instance must have a name set.
        Postconditions: returns the QuerySet passed in with an additional filter
           for section name.  If no QuerySet passed in, creates new Article
           QuerySet, returns it with filter added.
        '''
        
        # return reference
        qs_OUT = None
        
        # declare variables
        me = "add_section_name_filter_to_article_qs"
        my_section_name = ""
        
        # got a query set?
        if ( qs_IN ):
        
            # use the one passed in.
            qs_OUT = qs_IN
            
            #output_debug( "QuerySet passed in, using it.", me, "*** " )
        
        else:
        
            # No.  Make one.
            qs_OUT = Article.objects.all()
            
            #output_debug( "No QuerySet passed in, using fresh one.", me, "*** " )
        
        #-- END check to see if query set passed in --#
        
        # get section name.
        my_section_name = self.name
        
        # see if section name is "all".
        if ( my_section_name == Temp_Section.SECTION_NAME_ALL ):
            
            # add filter for name being in the list
            qs_OUT = qs_OUT.filter( section__in = Temp_Section.NEWS_SECTION_NAME_LIST )
            
        else:
            
            # just limit to the name.
            qs_OUT = qs_OUT.filter( section = self.name )
            
        #-- END check to see if section name is "all" --#
        
        return qs_OUT
        
    #-- END method add_section_name_filter_to_article_qs() --#


    def append_shared_article_qs_params( self, query_set_IN = None, *args, **kwargs ):
    
        # return reference
        qs_OUT = None
        
        # declare variables
        me = "append_shared_article_qs_params"
        date_range_q = None
        custom_q_IN = None
        
        # got a query set?
        if ( query_set_IN ):
        
            # use the one passed in.
            qs_OUT = query_set_IN
            
            #output_debug( "QuerySet passed in, using it.", me, "*** " )
        
        else:
        
            # No.  Make one.
            qs_OUT = Article.objects.all()
            
            #output_debug( "No QuerySet passed in, using fresh one.", me, "*** " )
        
        #-- END check to see if query set passed in --#
        
        # date range
        date_range_q = self.create_q_article_date_range( *args, **kwargs )
        
        if ( date_range_q ):
        
            # yup. add it to query.
            qs_OUT = qs_OUT.filter( date_range_q )
            
        # end date range check.
        
        # got a custom Q passed in?
        if ( self.PARAM_CUSTOM_ARTICLE_Q in kwargs ):
        
            # yup.  Get it.
            custom_q_IN = kwargs[ self.PARAM_CUSTOM_ARTICLE_Q ]
            
            # anything there?
            if ( custom_q_IN ):
                
                # add it to the output QuerySet
                qs_OUT = qs_OUT.filter( custom_q_IN )
                
            #-- END check to see if custom Q() populated --#
        
        #-- END check to see if start date in arguments --#        
        
        # try deferring the text and raw_html fields.
        #qs_OUT.defer( 'text', 'raw_html' )
        
        return qs_OUT
    
    #-- END method append_shared_article_qs_params() --#


    def calculate_average_pages_articles_per_day( self, query_set_IN, *args, **kwargs ):
    
        '''
        Retrieves pages in current section that have local writers on them for
           each day, then averages the counts over the number of days. Returns
           the average.
        Preconditions: Must have a start and end date.  If not, returns -1.
        '''
    
        # return reference
        values_OUT = {}
        
        # Declare variables
        me = "calculate_average_pages_articles_per_day"
        daily_article_qs = None
        start_date_IN = None
        end_date_IN = None
        start_date = None
        end_date = None
        qs_article_count = -1
        current_date = None
        current_timedelta = None
        page_dict = None
        day_page_count_list = None
        day_article_count_list = None
        current_page = ""
        current_page_count = -1
        daily_page_count = -1
        daily_article_count = -1
        overall_time_delta = None
        day_count = -1
        current_count = -1
        total_page_count = -1
        total_article_count = -1
        
        # get start and end date.
        start_date_IN = get_dict_value( kwargs, Temp_Section.PARAM_START_DATE, None )
        end_date_IN = get_dict_value( kwargs, Temp_Section.PARAM_END_DATE, None )
        
        # do we have dates?
        if ( ( start_date_IN ) and ( end_date_IN ) ):
            
            # we do.  Convert them to datetime.
            start_date = datetime.datetime.strptime( start_date_IN, self.DEFAULT_DATE_FORMAT )
            end_date = datetime.datetime.strptime( end_date_IN, self.DEFAULT_DATE_FORMAT )
        
            # initialize list of counts.
            day_page_count_list = []
            day_article_count_list = []
        
            # then, loop one day at a time.
            current_date = start_date
            current_timedelta = end_date - current_date
            
            # loop over dates as long as difference between current and end is 0
            #    or greater.
            while ( current_timedelta.days > -1 ):
            
                # today's page map
                page_dict = {}
                daily_page_count = 0
                daily_article_count = 0
                output_debug( "Processing " + str( current_date ), me )
            
                # get articles for current date.add current date to list.
                article_qs = query_set_IN.filter( pub_date = current_date )
                
                # check if we have anything in the QuerySet
                qs_article_count = article_qs.count()
                output_debug( "Article count: " + str( qs_article_count ), me, "--- " )
                
                # only process if there is something in the QuerySet
                if ( qs_article_count > 0 ):
                
                    for article in article_qs.iterator():
                        
                        # get the page for the current article.
                        current_page = article.page
                        
                        # get current page article, increment, and store.
                        current_page_article_count = get_dict_value( page_dict, current_page, 0 )
                        current_page_article_count += 1
                        page_dict[ current_page ] = current_page_article_count
                        
                    #-- END loop over articles for current day. --#
                    
                    # Now, loop over the pages (not the same as number of
                    #    articles - likely will be fewer, with multiple
                    #    articles per page), adding them up and outputting counts
                    #    for each page.
                    output_debug( "Page count: " + str( len( page_dict ) ), me, "--- " )
                    for current_page, current_page_article_count in page_dict.items():
                    
                        # add 1 to page count
                        daily_page_count += 1
                        daily_article_count += current_page_article_count
                        
                        # output page and count.
                        output_debug( current_page + ", " + str( current_page_article_count ), me, "--- " )
                        
                    #-- END loop over pages for a day.
                    
                    # Output average articles per page if page count is not 0.
                    if ( daily_page_count > 0 ):
                    
                        output_debug( "Average articles per page: " + str( daily_article_count / daily_page_count ), me )
                        
                    #-- END check to make sure we don't divide by 0. --#
                
                #-- END check to see if there are any articles. --#

                # Always add a count for each day to the lists, even if it is 0.
                day_page_count_list.append( daily_page_count )
                day_article_count_list.append( daily_article_count )
                
                # increment the date and re-calculate timedelta.
                current_date = current_date + datetime.timedelta( days = 1 )
                current_timedelta = end_date - current_date
                
            #-- END loop over days --#

            # initialize count holders
            total_page_count = 0
            total_article_count = 0
            
            # get day count
            # day_count = len( day_page_count_list )
            if ( start_date_IN == end_date_IN ):
                
                day_count = 1
                
            else:
                
                overall_time_delta = end_date - start_date
                day_count = overall_time_delta.days + 1
                
            #-- END try to get number of days set correctly. --#
            
            output_debug( "Day Count: " + str( day_count ), me, "--- " )
            
            # loop to get totals for page and article counts.
            for current_count in day_article_count_list:
                
                # add current count to total_page_count
                total_article_count += current_count
                
            #-- END loop over page counts --#
            
            # loop to get totals for page and article counts.
            for current_count in day_page_count_list:
                
                # add current count to total_page_count
                total_page_count += current_count
                
            #-- END loop over page counts --#
            
            # Populate output values.
            values_OUT[ Temp_Section.OUTPUT_DAY_COUNT ] = day_count
            values_OUT[ Temp_Section.OUTPUT_ARTICLE_COUNT ] = total_article_count
            values_OUT[ Temp_Section.OUTPUT_ARTICLES_PER_DAY ] = Decimal( total_article_count ) / Decimal( day_count )
            values_OUT[ Temp_Section.OUTPUT_PAGE_COUNT ] = total_page_count
            values_OUT[ Temp_Section.OUTPUT_PAGES_PER_DAY ] = Decimal( total_page_count ) / Decimal( day_count )                
                
        #-- END check to see if we have required variables. --#
        
        #output_debug( "Query: " + str( article_qs.query ), me, "---===>" )
        
        return values_OUT
        
    #-- END method calculate_average_pages_articles_per_day() --#


    def create_q_article_date_range( self, *args, **kwargs ):
    
        '''
        Accepts a start and end date in the keyword arguments.  Creates a Q()
           instance that filters dates based on start and end date passed in. If
           both are missing, does nothing.  If on or other passed in, filters
           accordingly.
        Preconditions: Dates must be in YYYY-MM-DD format.
        Postconditions: None.
        '''
        
        # return reference
        q_OUT = None
        
        # declare variables
        start_date_IN = ""
        end_date_IN = ""
        
        # retrieve dates
        # start date
        if ( self.PARAM_START_DATE in kwargs ):
        
            # yup.  Get it.
            start_date_IN = kwargs[ self.PARAM_START_DATE ]
        
        #-- END check to see if start date in arguments --#
        
        # end date
        if ( self.PARAM_END_DATE in kwargs ):
        
            # yup.  Get it.
            end_date_IN = kwargs[ self.PARAM_END_DATE ]
        
        #-- END check to see if end date in arguments --#
        
        if ( ( start_date_IN ) and ( end_date_IN ) ):
        
            # both start and end.
            q_OUT = Q( pub_date__gte = datetime.datetime.strptime( start_date_IN, self.DEFAULT_DATE_FORMAT ) )
            q_OUT = q_OUT & Q( pub_date__lte = datetime.datetime.strptime( end_date_IN, self.DEFAULT_DATE_FORMAT ) )
        
        elif( start_date_IN ):
        
            # just start date
            q_OUT = Q( pub_date__gte = datetime.datetime.strptime( start_date_IN, self.DEFAULT_DATE_FORMAT ) )
        
        elif( end_date_IN ):
        
            # just end date
            q_OUT = Q( pub_date__lte = datetime.datetime.strptime( end_date_IN, self.DEFAULT_DATE_FORMAT ) )
        
        #-- END conditional to see what we got. --#

        return q_OUT
    
    #-- END method create_q_article_date_range() --#


    def get_daily_averages( self, *args, **kwargs ):
    
        '''
        Retrieves pages in current section then averages the counts of pages and
           articles over the number of days. Returns
           the average.
        Preconditions: Must have a start and end date.  If not, returns -1.
        Postconditions: Returns a dictionary with two values in it, average
           articles per day and average pages per day.  Also stores the values
           in the current instance, so the calling method need not deal that.
        '''
    
        # return reference
        values_OUT = -1
        
        # Declare variables
        me = "get_daily_averages"
        base_article_qs = None
        daily_article_qs = None
        start_date_IN = None
        end_date_IN = None
        averages_dict = None
        day_count = None
        page_count = None
        pages_per_day = None
        articles_per_day = None
        
        # get start and end date.
        start_date_IN = get_dict_value( kwargs, Temp_Section.PARAM_START_DATE, None )
        end_date_IN = get_dict_value( kwargs, Temp_Section.PARAM_END_DATE, None )
        
        output_debug( "Getting daily averages for " + start_date_IN + " to " + end_date_IN, me, ">>> " )
        
        output_debug( "State of object entering method: " + str( self ), me, ">>> " )

        # do we have dates?
        if ( ( start_date_IN ) and ( end_date_IN ) ):
            
            # add shared filter parameters - for now, just date range.
            base_article_qs = self.append_shared_article_qs_params( *args, **kwargs )
    
            # get current section articles.
            #base_article_qs = base_article_qs.filter( section = self.name )
            base_article_qs = self.add_section_name_filter_to_article_qs( base_article_qs, *args, **kwargs )
            
            # call method to calculate averages.
            averages_dict = self.calculate_average_pages_articles_per_day( base_article_qs, *args, **kwargs )
            
            output_debug( "Averages returned: " + str( averages_dict ), me, ">>> " )
            
            # bust out the values.
            values_OUT = averages_dict
            day_count = averages_dict.get( Temp_Section.OUTPUT_DAY_COUNT, Decimal( "0" ) )
            page_count = averages_dict.get( Temp_Section.OUTPUT_PAGE_COUNT, Decimal( "0" ) )
            articles_per_day = averages_dict.get( Temp_Section.OUTPUT_ARTICLES_PER_DAY, Decimal( "0" ) )
            pages_per_day = averages_dict.get( Temp_Section.OUTPUT_PAGES_PER_DAY, Decimal( "0" ) )
            
            # Store values in this instance.
            self.total_days = day_count
            self.total_pages = page_count
            self.average_articles_per_day = articles_per_day
            self.average_pages_per_day = pages_per_day
        
        #-- END conditional to make sure we have start and end dates --#

        output_debug( "State of object before leaving method: " + str( self ), me, ">>> " )

        return values_OUT
        
    #-- END method get_daily_averages() --#


    def get_daily_in_house_averages( self, *args, **kwargs ):
    
        '''
        Retrieves pages in current section that have local writers on them for
           each day, then averages the counts over the number of days. Returns
           the average.
        Preconditions: Must have a start and end date.  If not, returns -1.
        Postconditions: Returns a dictionary with two values in it, average
           articles per day and average pages per day.  Also stores the values
           in the current instance, so the calling method need not deal that.
        '''
    
        # return reference
        values_OUT = -1
        
        # Declare variables
        me = "get_daily_in_house_averages"
        base_article_qs = None
        daily_article_qs = None
        start_date_IN = None
        end_date_IN = None
        averages_dict = None
        day_count = None
        page_count = None
        pages_per_day = None
        articles_per_day = None
        
        # get start and end date.
        start_date_IN = get_dict_value( kwargs, Temp_Section.PARAM_START_DATE, None )
        end_date_IN = get_dict_value( kwargs, Temp_Section.PARAM_END_DATE, None )
        
        output_debug( "Getting daily IN-HOUSE averages for " + start_date_IN + " to " + end_date_IN, me, ">>> " )
        
        output_debug( "State of object entering method: " + str( self ), me, ">>> " )

        # do we have dates?
        if ( ( start_date_IN ) and ( end_date_IN ) ):
            
            # add shared filter parameters - for now, just date range.
            base_article_qs = self.append_shared_article_qs_params( *args, **kwargs )
    
            # get in-house articles in current section articles.
            base_article_qs = self.add_section_name_filter_to_article_qs( base_article_qs, *args, **kwargs )
            base_article_qs = base_article_qs.filter( Temp_Section.Q_IN_HOUSE_AUTHOR )
            
            # call method to calculate averages.
            averages_dict = self.calculate_average_pages_articles_per_day( base_article_qs, *args, **kwargs )
            
            output_debug( "Averages returned: " + str( averages_dict ), me, ">>> " )

            # bust out the values.
            values_OUT = averages_dict
            day_count = averages_dict.get( Temp_Section.OUTPUT_DAY_COUNT, Decimal( "0" ) )
            page_count = averages_dict.get( Temp_Section.OUTPUT_PAGE_COUNT, Decimal( "0" ) )
            articles_per_day = averages_dict.get( Temp_Section.OUTPUT_ARTICLES_PER_DAY, Decimal( "0" ) )
            pages_per_day = averages_dict.get( Temp_Section.OUTPUT_PAGES_PER_DAY, Decimal( "0" ) )
            
            # Store values in this instance.
            self.total_days = day_count
            self.in_house_pages = page_count
            self.average_in_house_articles_per_day = articles_per_day
            self.average_in_house_pages_per_day = pages_per_day
        

        #-- END conditional to make sure we have start and end dates --#

        output_debug( "State of object before leaving method: " + str( self ), me, ">>> " )

        return values_OUT
        
    #-- END method get_daily_in_house_averages() --#


    def get_external_article_count( self, *args, **kwargs ):
    
        '''
        Retrieves count of articles in the current section whose "author_varchar"
           column indicate that the articles were not written by the Grand
           Rapids Press newsroom.
        '''
    
        # return reference
        value_OUT = -1
        
        # Declare variables
        me = "get_external_article_count"
        article_qs = None 
        position = ""
       
        # add shared filter parameters - for now, just date range.
        article_qs = self.append_shared_article_qs_params( article_qs, *args, **kwargs )
        
        # exclude bylines of local authors.
        article_qs = article_qs.exclude( Temp_Section.Q_IN_HOUSE_AUTHOR )

        # include just this section.
        article_qs = self.add_section_name_filter_to_article_qs( article_qs, *args, **kwargs )

        #output_debug( "Query: " + str( article_qs.query ), me, "---===>" )

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
        me = "get_external_booth_count"
        article_qs = None
        author_q = None
        
        # add shared filter parameters - for now, just date range.
        article_qs = self.append_shared_article_qs_params( article_qs, *args, **kwargs )
        
        # only get articles by news service.
        author_q = Q( author_varchar__iregex = r'.* */ *GRAND RAPIDS PRESS NEWS SERVICE$' )
        article_qs = article_qs.filter( author_q )
        
        # limit to current section.
        article_qs = self.add_section_name_filter_to_article_qs( article_qs, *args, **kwargs )
        
        #output_debug( "Query: " + str( article_qs.query ), me, "---===>" )
        
        # get count.
        value_OUT = article_qs.count()
        
        return value_OUT
        
    #-- END method get_external_booth_count --#


    def get_in_house_article_count( self, *args, **kwargs ):
    
        '''
        Retrieves count of articles in the current section whose "author_varchar"
           column indicate that the articles were written by the actual Grand
           Rapids Press newsroom.
        '''
    
        # return reference
        value_OUT = -1
        
        # Declare variables
        me = "get_in_house_article_count"
        article_qs = None
        
        # get articles.
        #article_qs = Article.objects.filter( Q( section = self.name ), Temp_Section.Q_IN_HOUSE_AUTHOR )
        article_qs = self.add_section_name_filter_to_article_qs( *args, **kwargs )
        article_qs = article_qs.filter( Temp_Section.Q_IN_HOUSE_AUTHOR )
        
        # add shared filter parameters - for now, just date range.
        article_qs = self.append_shared_article_qs_params( article_qs, *args, **kwargs )
        #output_debug( "Query: " + str( article_qs.query ), me, "---===>" )
        
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
        name_list_string = ""
        my_row = None
        start_date_IN = ""
        end_date_IN = ""
        
        # get database cursor
        my_cursor = connection.cursor()
        
        # create SQL query string
        query_string = "SELECT COUNT( DISTINCT CONVERT( LEFT( author_varchar, LOCATE( ' / ', author_varchar ) ), CHAR ) ) as name_count"
        query_string += " FROM sourcenet_article"
        
        # add in ability to either look for "all" or a single section name.
        if ( self.name == Temp_Section.SECTION_NAME_ALL ):

            # start IN statement.
            query_string += " WHERE section IN ( "
            
            # make list of section names.
            name_list_string = "', '".join( Temp_Section.NEWS_SECTION_NAME_LIST )
            
            # check if there is anything in that list.
            if ( name_list_string ):
            
                # there is.  add quotes to beginning and end.
                name_list_string = "'" + name_list_string + "'"
                
            #-- END check to see if we have anything in list. --#
            
            # add list to IN, then close out IN statement.
            query_string += name_list_string + " )"            
            
        else:
            
            # not all, so just limit to current name.
            query_string += " WHERE section = '" + self.name + "'"
            
        #-- END check to see if "all" --#
        
        query_string += "     AND"
        query_string += "     ("
        query_string += "         ( UPPER( author_varchar ) REGEXP '.* */ *THE GRAND RAPIDS PRESS$' )"
        query_string += "         OR ( UPPER( author_varchar ) REGEXP '.* */ *PRESS .* EDITOR$' )"
        query_string += "         OR ( UPPER( author_varchar ) REGEXP '.* */ *GRAND RAPIDS PRESS .* BUREAU$' )"
        query_string += "         OR ( UPPER( author_varchar ) REGEXP '.* */ *SPECIAL TO THE PRESS$' )"
        query_string += "     )"

        # retrieve dates
        # start date
        if ( self.PARAM_START_DATE in kwargs ):
        
            # yup.  Get it.
            start_date_IN = kwargs[ self.PARAM_START_DATE ]
        
        #-- END check to see if start date in arguments --#
        
        # end date
        if ( self.PARAM_END_DATE in kwargs ):
        
            # yup.  Get it.
            end_date_IN = kwargs[ self.PARAM_END_DATE ]
        
        #-- END check to see if end date in arguments --#
        
        if ( ( start_date_IN ) and ( end_date_IN ) ):
        
            # both start and end.
            query_string += "     AND ( ( pub_date >= '" + start_date_IN + "' ) AND ( pub_date <= '" + end_date_IN + "' ) )"
        
        elif( start_date_IN ):
        
            # just start date
            query_string += "     AND ( pub_date >= '" + start_date_IN + "' )"
        
        elif( end_date_IN ):
        
            # just end date
            query_string += "     AND ( pub_date <= '" + end_date_IN + "' )"
        
        #-- END conditional to see what we got. --#

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
        #article_qs = Article.objects.filter( section = self.name )
        article_qs = self.add_section_name_filter_to_article_qs( *args, **kwargs )
        
        # add shared filter parameters - for now, just date range.
        article_qs = self.append_shared_article_qs_params( article_qs, *args, **kwargs )

        # get count.
        value_OUT = article_qs.count()
        
        return value_OUT
        
    #-- END method get_total_article_count --#
    

    def process_column_values( self, do_save_IN = False, *args, **kwargs ):
    
        '''
        Generates values for all columns for section name passed in.
        '''
    
        # return reference
        status_OUT = STATUS_SUCCESS
        
        # Declare variables
        me = "process_column_values"
        my_total_articles = -1
        my_in_house_articles = -1
        my_external_articles = -1
        my_external_booth = -1
        my_in_house_authors = -1
        my_percent_in_house = -1
        my_percent_external = -1
        my_averages = None
        my_in_house_averages = None
        debug_string = ""
        
        # start and end date?
        start_date_IN = None
        end_date_IN = None
        
        # retrieve dates
        # start date
        if ( self.PARAM_START_DATE in kwargs ):
        
            # yup.  Get it.
            start_date_IN = kwargs[ self.PARAM_START_DATE ]
            start_date_IN = datetime.datetime.strptime( start_date_IN, self.DEFAULT_DATE_FORMAT )
            output_debug( "*** Start date = " + str( start_date_IN ) + "\n", me )
            
        else:
        
            # No start date.
            output_debug( "No start date!", me, "*** " )
        
        #-- END check to see if start date in arguments --#
        
        # end date
        if ( self.PARAM_END_DATE in kwargs ):
        
            # yup.  Get it.
            end_date_IN = kwargs[ self.PARAM_END_DATE ]
            end_date_IN = datetime.datetime.strptime( end_date_IN, self.DEFAULT_DATE_FORMAT )
            output_debug( "*** End date = " + str( end_date_IN ) + "\n", me )
            
        else:
        
            # No end date.
            output_debug( "No end date!", me, "*** " )
        
        #-- END check to see if end date in arguments --#

        # initialize Decimal Math
        getcontext().prec = 20
        
        # get values.
        my_total_articles = self.get_total_article_count( *args, **kwargs )
        my_in_house_articles = self.get_in_house_article_count( *args, **kwargs )
        my_external_articles = self.get_external_article_count( *args, **kwargs )
        my_external_booth = self.get_external_booth_count( *args, **kwargs )
        my_in_house_authors = self.get_in_house_author_count( *args, **kwargs )
        my_averages = self.get_daily_averages( *args, **kwargs )
        my_in_house_averages = self.get_daily_in_house_averages( *args, **kwargs )

        # derive additional values

        # percent of articles that are in-house
        if ( ( my_in_house_articles >= 0 ) and ( my_total_articles > 0 ) ):

            # divide in-house by total
            my_percent_in_house = Decimal( my_in_house_articles ) / Decimal( my_total_articles )
            
        else:
        
            # either no in-house or total is 0.  Set to 0.
            my_percent_in_house = Decimal( "0.0" )
            
        #-- END check to make sure values are OK for calculating percent --#
        
        # percent of articles that are external
        if ( ( my_external_articles >= 0 ) and ( my_total_articles > 0 ) ):

            # divide external by total
            my_percent_external = Decimal( my_external_articles ) / Decimal( my_total_articles )
            
        else:
        
            # either no external or total is 0.  Set to 0.
            my_percent_external = Decimal( "0.0" )
            
        #-- END check to make sure values are OK for calculating percent --#
       
        # set values
        self.total_articles = my_total_articles
        self.in_house_articles = my_in_house_articles
        self.external_articles = my_external_articles
        self.external_booth = my_external_booth
        self.in_house_authors = my_in_house_authors

        if ( my_percent_in_house ):
            self.percent_in_house = my_percent_in_house
        #-- END check if we have in-house percent --#

        if ( my_percent_external ):
            self.percent_external = my_percent_external
        #-- END check to see if we have percent external --#

        self.start_date = start_date_IN
        self.end_date = end_date_IN

        # save?
        if ( do_save_IN == True ):
        
            # output contents.
            debug_string = '%s: tot_day = %d; tot_art = %d; in_art = %d; ext_art= %d; ext_booth = %d; tot_page = %d; in_page = %d; in_auth = %d; avg_art = %f; avg_page = %f; avg_ih_art = %f; avg_ih_page = %f; per_in = %f; per_ext = %f; start = %s; end = %s' % ( "Before save, contents of variables for " + self.name + ": ", self.total_days, my_total_articles, my_in_house_articles, my_external_articles, my_external_booth, self.total_pages, self.in_house_pages, my_in_house_authors, self.average_articles_per_day, self.average_pages_per_day, self.average_in_house_articles_per_day, self.average_in_house_pages_per_day, my_percent_in_house, my_percent_external, str( start_date_IN ), str( end_date_IN ) )
            output_debug( debug_string, me, "===>" )
            output_debug( "Contents of instance: " + str( self ), me, "===>" )
            
            # save
            save_result = self.save()
            
            output_debug( "save() result: " + str( save_result ), me, "*** " )
        
        #-- END check to see if we save or not. --#
        
        return status_OUT
        
    #-- END method process_column_values --#


    #----------------------------------------------------------------------
    # class methods
    #----------------------------------------------------------------------

    @classmethod
    def find_instance( self, *args, **kwargs ):
    
        '''
        Generates values for all columns for section name passed in.
        '''
    
        # return reference
        instance_OUT = None
        
        # Declare variables
        me = "get_instance_for_name"
        result_qs = None
        result_count = -1

        # incoming parameters
        section_name_IN = ""
        start_date_IN = None
        end_date_IN = None
        custom_q_IN = None
        
        # start with Empty QuerySet
        result_qs = self.objects.all()
        
        # retrieve parameters
        # section name
        if ( self.PARAM_SECTION_NAME in kwargs ):
        
            # yup.  Get it.
            section_name_IN = kwargs[ self.PARAM_SECTION_NAME ]
            result_qs = result_qs.filter( name = section_name_IN )
            output_debug( "Requested section name = " + str( section_name_IN ), me, "*** " )
            
        else:
        
            # No start date.
            output_debug( "No section name!", me, "*** " )
        
        #-- END check to see if start date in arguments --#
        
        # start date
        if ( self.PARAM_START_DATE in kwargs ):
        
            # yup.  Get it.
            start_date_IN = kwargs[ self.PARAM_START_DATE ]
            start_date_IN = datetime.datetime.strptime( start_date_IN, self.DEFAULT_DATE_FORMAT )
            result_qs = result_qs.filter( start_date = start_date_IN )
            output_debug( "Start date = " + str( start_date_IN ), me, "*** " )
            
        else:
        
            # No start date.
            output_debug( "No start date!\n", me, "*** " )
        
        #-- END check to see if start date in arguments --#
        
        # end date
        if ( self.PARAM_END_DATE in kwargs ):
        
            # yup.  Get it.
            end_date_IN = kwargs[ self.PARAM_END_DATE ]
            end_date_IN = datetime.datetime.strptime( end_date_IN, self.DEFAULT_DATE_FORMAT )
            result_qs = result_qs.filter( end_date = end_date_IN )
            output_debug( "End date = " + str( end_date_IN ), me, "*** " )
            
        else:
        
            # No end date.
            output_debug( "No end date!\n", me, "*** " )
        
        #-- END check to see if end date in arguments --#

        # got a custom Q passed in?
        if ( self.PARAM_CUSTOM_SECTION_Q in kwargs ):
        
            # yup.  Get it.
            custom_q_IN = kwargs[ self.PARAM_CUSTOM_SECTION_Q ]
            
            # anything there?
            if ( custom_q_IN ):
                
                # add it to the output QuerySet
                result_qs = result_qs.filter( custom_q_IN )
                
            #-- END check to see if custom Q() populated --#
        
        #-- END check to see if custom Q() in arguments --#        

        # try to get Temp_Section instance
        try:
        
            instance_OUT = result_qs.get()

        except MultipleObjectsReturned:

            # error!
            output_debug( "ERROR - more than one match for name \"" + name_IN + "\" when there should only be one.  Returning nothing.", me )

        except ObjectDoesNotExist:

            # either nothing or negative count (either implies no match).
            #    Return new instance.
            instance_OUT = Temp_Section()
            instance_OUT.name = section_name_IN

            # got a start date?
            if ( start_date_IN ):
                
                instance_OUT.start_date = start_date_IN
                
            #-- END check to see if we have a start date. --#
            
            # got an end date?
            if ( end_date_IN ):
                
                instance_OUT.end_date = end_date_IN
                
            #-- END check to see if we have an end date. --#
            
        #-- END try to retrieve instance for name passed in. --#
            
        return instance_OUT
        
    #-- END class method find_instance --#


    @classmethod
    def process_section_date_range( cls, *args, **kwargs ):
 
        # declare variables
        me = "process_section_date_range"
        start_date_IN = ""
        end_date_IN = ""
        skip_individual_sections_IN = False
        save_stats = True
        section_params = {}
        current_section_name = ""
        current_instance = None
        
        # Get start and end dates
        start_date_IN = get_dict_value( kwargs, cls.PARAM_START_DATE, None )
        end_date_IN = get_dict_value( kwargs, cls.PARAM_END_DATE, None )

        # check if we only want to create "all" records, so skip individual
        #    sections.
        skip_individual_sections_IN = get_dict_value( kwargs, cls.PARAM_JUST_PROCESS_ALL, False )

        # got dates?
        if ( ( start_date_IN ) and ( end_date_IN ) ):

            # store in params.
            section_params[ cls.PARAM_START_DATE ] = start_date_IN
            section_params[ cls.PARAM_END_DATE ] = end_date_IN
            
            # process records for individual sections?
            if( skip_individual_sections_IN == False ):
                    
                # loop over list of section names that are local news or sports.
                for current_section_name in cls.NEWS_SECTION_NAME_LIST:
                
                    # set section name
                    section_params[ cls.PARAM_SECTION_NAME ] = current_section_name
                
                    # get instance
                    current_instance = cls.find_instance( **section_params )
    
                    # process values and save
                    current_instance.process_column_values( save_stats, **section_params )
                    
                    # output current instance.
                    output_debug( "Finished processing section " + current_section_name + " - " + str( current_instance ) + "\n\n", me, "\n\n=== " )
                    
                    # memory management.
                    gc.collect()
                    django.db.reset_queries()
                    
                #-- END loop over sections. --#

            #-- END check to see if just want to update "all" rows. --#
            
            # Then, do the "all"
            # set section name
            section_params[ cls.PARAM_SECTION_NAME ] = Temp_Section.SECTION_NAME_ALL
        
            # get instance
            current_instance = cls.find_instance( **section_params )

            # process values and save
            current_instance.process_column_values( save_stats, **section_params )
            
            # output current instance.
            output_debug( "Finished processing section " + current_section_name + " - " + str( current_instance ) + "\n\n", me, "\n\n=== " )
            
            # memory management.
            gc.collect()
            django.db.reset_queries()
            
        #-- END check to make sure we have dates. --#
        
    #-- END method process_section_date_range() --#


    @classmethod
    def process_section_date_range_day_by_day( cls, *args, **kwargs ):

        # declare variables
        me = "process_section_date_range_day_by_day"
        start_date_IN = ""
        end_date_IN = ""
        skip_individual_sections_IN = False
        start_date = None
        end_date = None
        save_stats = True
        daily_params = {}
        current_section_name = ""
        current_date = None
        current_timedelta = None
        current_instance = None
        
        
        # Get start and end dates
        start_date_IN = get_dict_value( kwargs, cls.PARAM_START_DATE, None )
        end_date_IN = get_dict_value( kwargs, cls.PARAM_END_DATE, None )
        
        # check if we only want to create "all" records, so skip individual
        #    sections.
        skip_individual_sections_IN = get_dict_value( kwargs, cls.PARAM_JUST_PROCESS_ALL, False )

        # got dates?
        if ( ( start_date_IN ) and ( end_date_IN ) ):
            
            # Convert start and end dates to datetime.
            start_date = datetime.datetime.strptime( start_date_IN, cls.DEFAULT_DATE_FORMAT )
            end_date = datetime.datetime.strptime( end_date_IN, cls.DEFAULT_DATE_FORMAT )
        
            # then, loop one day at a time.
            current_date = start_date
            current_timedelta = end_date - current_date
        
            # loop over dates as long as difference between current and end is 0
            #    or greater.
            while ( current_timedelta.days > -1 ):
            
                # current date
                output_debug( "Processing " + str( current_date ), me )
                    
                # set start and end date in kwargs to current_date
                daily_params[ cls.PARAM_START_DATE ] = current_date.strftime( cls.DEFAULT_DATE_FORMAT )
                daily_params[ cls.PARAM_END_DATE ] = current_date.strftime( cls.DEFAULT_DATE_FORMAT )
        
                # process records for individual sections?
                if( skip_individual_sections_IN == False ):
                    
                    # yes - loop over list of section names that are local news or sports.
                    for current_section_name in cls.NEWS_SECTION_NAME_LIST:
                    
                        # set section name
                        daily_params[ cls.PARAM_SECTION_NAME ] = current_section_name
                
                        # get an instance
                        current_instance = cls.find_instance( **daily_params )
                    
                        # process values and save
                        current_instance.process_column_values( save_stats, **daily_params )
                        
                        # output current instance.
                        output_debug( "Finished processing section " + current_section_name + "\n\n", me, "\n\n=== " )
                        
                    #-- END loop over sections. --#
                    
                #-- END check to see if just want to update "all" rows. --#
                
                # process "all"
                # set section name
                daily_params[ cls.PARAM_SECTION_NAME ] = cls.SECTION_NAME_ALL
        
                # get an instance
                current_instance = cls.find_instance( **daily_params )
            
                # process values and save
                current_instance.process_column_values( save_stats, **daily_params )
                
                # output current instance.
                output_debug( "Finished processing section " + current_section_name + "\n\n", me, "\n\n=== " )
            
                # Done with this date.  Moving on.
                output_debug( "Finished processing date " + str( current_date ) + " - " + str( current_instance ) + "\n\n", me, "\n\n=== " )
                
                # increment the date and re-calculate timedelta.
                current_date = current_date + datetime.timedelta( days = 1 )
                current_timedelta = end_date - current_date
                
                # memory management.
                gc.collect()
                django.db.reset_queries()
                    
            #-- END loop over dates in date range --#
           
        #-- END check to make sure we have start and end date. --#
        
    #-- END method process_section_date_range_day_by_day() --#


#= End Temp_Section Model ======================================================