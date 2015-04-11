from __future__ import unicode_literals

'''
Copyright 2010-2015 Jonathan Morgan

This file is part of http://github.com/jonathanmorgan/sourcenet.

sourcenet is free software: you can redistribute it and/or modify it under the terms of the GNU Lesser General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.

sourcenet is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.

You should have received a copy of the GNU Lesser General Public License along with http://github.com/jonathanmorgan/sourcenet. If not, see http://www.gnu.org/licenses/.
'''

#================================================================================
# Imports
#================================================================================

# python imports
from abc import ABCMeta, abstractmethod
import datetime
from decimal import Decimal
from decimal import getcontext
import gc
import logging
import pickle
#import re

# nameparse import
# http://pypi.python.org/pypi/nameparser
from nameparser import HumanName

# BeautifulSoup import
from bs4 import BeautifulSoup
from bs4 import NavigableString

# taggit tagging APIs
from taggit.managers import TaggableManager

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
#import django
#django.setup()

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

# django encoding imports (for supporting 2 and 3).
import django.utils.encoding
from django.utils.encoding import python_2_unicode_compatible

# python_utilities - text cleanup
from python_utilities.beautiful_soup.beautiful_soup_helper import BeautifulSoupHelper
from python_utilities.strings.html_helper import HTMLHelper
from python_utilities.strings.string_helper import StringHelper

# python_utilities - logging
from python_utilities.logging.logging_helper import LoggingHelper

# python_utilities - sequences
from python_utilities.sequences.sequence_helper import SequenceHelper

#================================================================================
# Shared variables and functions
#================================================================================

'''
Gross debugging code, shared across all models.
'''

DEBUG = True
STATUS_SUCCESS = "Success!"
DEFAULT_DATE_FORMAT = "%Y-%m-%d"


def output_debug( message_IN, method_IN = "", indent_with_IN = "", logger_name_IN = "" ):
    
    '''
    Accepts message string.  If debug is on, logs it.  If not,
       does nothing for now.
    '''
    
    # declare variables
    my_message = ""
    my_logger = None
    my_logger_name = ""

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
        
            # debug is on.  Start logging rather than using print().
            #print( my_message )
            
            # got a logger name?
            my_logger_name = "sourcenet.models"
            if ( ( logger_name_IN is not None ) and ( logger_name_IN != "" ) ):
            
                # use logger name passed in.
                my_logger_name = logger_name_IN
                
            #-- END check to see if logger name --#
                
            # get logger
            my_logger = LoggingHelper.get_a_logger( my_logger_name )
            
            # log debug.
            my_logger.debug( my_message )
        
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
@python_2_unicode_compatible
class Project( models.Model ):

    # Django model properties.
    name = models.CharField( max_length = 255 )
    description = models.TextField( blank = True, null = True )

    # Meta-data for this class.
    class Meta:
        ordering = [ 'name' ]

    #----------------------------------------------------------------------
    # methods
    #----------------------------------------------------------------------

    def __str__( self ):
        # return reference
        string_OUT = ''
        delimiter = ''
        
        string_OUT = str( self.id ) + ": " + self.name

        return string_OUT
        
    #-- END method __str__() --#

#= End Project Model ===========================================================


# Locations
@python_2_unicode_compatible
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

    def __str__( self ):
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
@python_2_unicode_compatible
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

    def __str__( self ):
        string_OUT = self.name
        return string_OUT

#= End Topic Model =========================================================


# Abstract_Person model
@python_2_unicode_compatible
class Abstract_Person( models.Model ):

    #----------------------------------------------------------------------
    # constants-ish
    #----------------------------------------------------------------------    

    GENDER_CHOICES = (
        ( 'na', 'Unknown' ),
        ( 'female', 'Female' ),
        ( 'male', 'Male' )
    )
    
    # lookup status
    LOOKUP_STATUS_FOUND = "found"
    LOOKUP_STATUS_NEW = "new"
    LOOKUP_STATUS_NONE = "None"

    #----------------------------------------------------------------------
    # model fields and meta
    #----------------------------------------------------------------------

    first_name = models.CharField( max_length = 255, blank = True, null = True )
    middle_name = models.CharField( max_length = 255, blank = True, null = True )
    last_name = models.CharField( max_length = 255, blank = True, null = True )
    name_prefix = models.CharField( max_length = 255, blank = True, null = True )
    name_suffix = models.CharField( max_length = 255, blank = True, null = True )
    nickname = models.CharField( max_length = 255, blank = True, null = True )
    full_name_string = models.CharField( max_length = 255, blank = True, null = True )
    original_name_string = models.CharField( max_length = 255, blank = True, null = True )
    gender = models.CharField( max_length = 6, choices = GENDER_CHOICES, blank = True, null = True )
    title = models.CharField( max_length = 255, blank = True, null = True )
    nameparser_pickled = models.TextField( blank = True, null = True )
    is_ambiguous = models.BooleanField( default = False )
    notes = models.TextField( blank = True, null = True )
    
    # field to store how source was captured.
    capture_method = models.CharField( max_length = 255, blank = True, null = True )

    # time stamps.
    create_date = models.DateTimeField( auto_now_add = True )
    last_modified = models.DateTimeField( auto_now = True )

    # Meta-data for this class.
    class Meta:

        abstract = True
        ordering = [ 'last_name', 'first_name', 'middle_name' ]
        
    #-- END class Meta --#


    #----------------------------------------------------------------------
    # static methods
    #----------------------------------------------------------------------
    
    
    @staticmethod
    def HumanName_to_str( human_name_IN ):
    
        # return reference
        string_OUT = ""
    
        string_OUT += "HumanName: \"" + unicode( human_name_IN ) + "\"\n"
        string_OUT += "- title: " + human_name_IN.title + "\n"
        string_OUT += "- first: " + human_name_IN.first + "\n"
        string_OUT += "- middle: " + human_name_IN.middle + "\n"
        string_OUT += "- last: " + human_name_IN.last + "\n"
        string_OUT += "- suffix: " + human_name_IN.suffix + "\n"
        string_OUT += "- nickname: " + human_name_IN.nickname + "\n"
        
        return string_OUT
    
    #-- END static method HumanName_to_str() --#


    #----------------------------------------------------------------------
    # class methods
    #----------------------------------------------------------------------
    
    
    @classmethod
    def get_person_for_name( cls, name_IN, create_if_no_match_IN = False, parsed_name_IN = None, do_strict_match_IN = False ):
    
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
            person_qs = cls.look_up_person_from_name( name_IN, parsed_name_IN = parsed_name_IN, do_strict_match_IN = do_strict_match_IN )
            
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
                    instance_OUT = cls()
                    
                    # store name
                    instance_OUT.set_name( name_IN )
                    
                    output_debug( "In " + me + ": no match for name: " + name_IN + "; so, creating new Person instance (but not saving yet)!" )
                    
                else:
                
                    # return None!
                    instance_OUT = None
                    
                    output_debug( "In " + me + ": no match for name: " + name_IN + "; so, returning None!" )
                    
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


    @classmethod
    def get_person_lookup_status( cls, person_IN ):
        
        # return reference
        status_OUT = ""
        
        # declare variables
        
        if ( person_IN is not None ):
        
            if ( ( person_IN.id ) and ( person_IN.id > 0 ) ):
            
                # there is an ID, so this is not a new record.
                status_OUT = cls.LOOKUP_STATUS_FOUND
                
            else:
            
                # Person returne, but no ID, so this is a new record - not found.
                status_OUT = cls.LOOKUP_STATUS_NEW
                
            #-- END check to see if ID present in record returned. --#
                
        else:
        
            # None - either multiple matches (eek!) or error.
            status_OUT = cls.LOOKUP_STATUS_NONE
        
        #-- END check to see if None. --#
    
        return status_OUT
        
    #-- END class method get_person_lookup_status() --#


    @classmethod
    def look_up_person_from_name( cls, name_IN = "", parsed_name_IN = None, do_strict_match_IN = False ):
    
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
        nickname = ""
        strict_q = None
                
        # got a name?
        if ( name_IN ):
        
            # Got a pre-parsed name?
            if ( parsed_name_IN is not None ):

                # yes. Use it.
                parsed_name = parsed_name_IN
                
            else:
            
                # no. Parse name_IN using HumanName class from nameparser.
                parsed_name = HumanName( name_IN )
                
            #-- END check to see if pre-parsed name. --#         
            
            # Use parsed values to build a search QuerySet.  First, get values.
            prefix = parsed_name.title
            first = parsed_name.first
            middle = parsed_name.middle
            last = parsed_name.last
            suffix = parsed_name.suffix
            nickname = parsed_name.nickname
            
            # build up queryset.
            qs_OUT = cls.objects.all()
            
            # got a prefix?
            if ( prefix ):
    
                # add value to query
                qs_OUT = qs_OUT.filter( name_prefix__iexact = prefix )
                
            else:
            
                # are we being strict?
                if ( do_strict_match_IN == True ):
                
                    # yes - None or ""?
                    if ( ( prefix is None ) or ( prefix == "" ) ):
                    
                        # for None or "", match to either NULL OR "".
                        strict_q = Q( name_prefix__isnull = True ) | Q( name_prefix__iexact = "" )
                        qs_OUT = qs_OUT.filter( strict_q )
                        
                    else:
                    
                        # for anything else, what?  Stupid Python False values...
                        pass
                        
                    #-- END check to see what exact value of prefix is. --#
                
                #-- END check to see if strict. --#
            
            #-- END check for prefix --#
            
            # first name
            if ( first ):
    
                # add value to query
                qs_OUT = qs_OUT.filter( first_name__iexact = first )
                
            else:
            
                # are we being strict?
                if ( do_strict_match_IN == True ):
                
                    # yes - None or ""?
                    if ( ( first is None ) or ( first == "" ) ):
                    
                        # for None or "", match to either NULL OR "".
                        strict_q = Q( first_name__isnull = True ) | Q( first_name__iexact = "" )
                        qs_OUT = qs_OUT.filter( strict_q )
                        
                    else:
                    
                        # for anything else, what?  Stupid Python False values...
                        pass
                        
                    #-- END check to see what exact value of first is. --#
                
                #-- END check to see if strict. --#
            
            #-- END check for first name --#
            
            # middle name
            if ( middle ):
    
                # add value to query
                qs_OUT = qs_OUT.filter( middle_name__iexact = middle )
                
            else:
            
                # are we being strict?
                if ( do_strict_match_IN == True ):
                
                    # yes - None or ""?
                    if ( ( middle is None ) or ( middle == "" ) ):
                    
                        # for None or "", match to either NULL OR "".
                        strict_q = Q( middle_name__isnull = True ) | Q( middle_name__iexact = "" )
                        qs_OUT = qs_OUT.filter( strict_q )

                    else:
                    
                        # for anything else, what?  Stupid Python False values...
                        pass
                        
                    #-- END check to see what exact value of middle is. --#
                
                #-- END check to see if strict. --#
            
            #-- END check for middle name --#

            # last name
            if ( last ):
    
                # add value to query
                qs_OUT = qs_OUT.filter( last_name__iexact = last )
                
            else:
            
                # are we being strict?
                if ( do_strict_match_IN == True ):
                
                    # yes - None or ""?
                    if ( ( last is None ) or ( last == "" ) ):
                    
                        # for None or "", match to either NULL OR "".
                        strict_q = Q( last_name__isnull = True ) | Q( last_name__iexact = "" )
                        qs_OUT = qs_OUT.filter( strict_q )

                    else:
                    
                        # for anything else, what?  Stupid Python False values...
                        pass
                        
                    #-- END check to see what exact value of last is. --#
                
                #-- END check to see if strict. --#
            
            #-- END check for last name --#
            
            # suffix
            if ( suffix ):
    
                # add value to query
                qs_OUT = qs_OUT.filter( name_suffix__iexact = suffix )
                
            else:
            
                # are we being strict?
                if ( do_strict_match_IN == True ):
                
                    # yes - None or ""?
                    if ( ( suffix is None ) or ( suffix == "" ) ):
                    
                        # for None or "", match to either NULL OR "".
                        strict_q = Q( name_suffix__isnull = True ) | Q( name_suffix__iexact = "" )
                        qs_OUT = qs_OUT.filter( strict_q )

                    else:
                    
                        # for anything else, what?  Stupid Python False values...
                        pass
                        
                    #-- END check to see what exact value of suffix is. --#
                
                #-- END check to see if strict. --#
            
            #-- END suffix --#
            
            # nickname
            if ( nickname ):
    
                # add value to query
                qs_OUT = qs_OUT.filter( nickname__iexact = nickname )
                
            else:
            
                # are we being strict?
                if ( do_strict_match_IN == True ):
                
                    # yes - None or ""?
                    if ( ( nickname is None ) or ( nickname == "" ) ):
                    
                        # for None or "", match to either NULL OR "".
                        strict_q = Q( nickname__isnull = True ) | Q( nickname__iexact = "" )
                        qs_OUT = qs_OUT.filter( strict_q )

                    else:
                    
                        # for anything else, what?  Stupid Python False values...
                        pass
                        
                    #-- END check to see what exact value of nickname is. --#
                
                #-- END check to see if strict. --#
            
            #-- END nickname --#
            
        else:
        
            # No name, returning None
            output_debug( "In " + me + ": no name passed in, returning None." )
        
        #-- END check to see if we have a name. --#
        
        return qs_OUT
    
    #-- END static method look_up_person_from_name() --#
    

    @classmethod
    def standardize_name_part( cls, name_part_IN, remove_periods_IN = False ):
        
        '''
        Accepts string name part, does the following to standardize it, in this
        order:
           - removes any commas.
           - strips white space from the beginning and end.
           - More to come?
           
        preconditions: None.

        postconditions: None.
        '''
        
        # return reference
        name_part_OUT = ""
        
        # declare variables
        working_string = ""
        
        # start with name part passed in.
        working_string = name_part_IN
        
        # first, check to see if anything passed in.
        if ( ( working_string is not None ) and ( working_string != "" ) ):
        
            # remove commas.
            working_string = working_string.replace( ",", "" )
            
            # remove periods as well?
            if ( remove_periods_IN == True ):
            
                # yes.
                working_string = working_string.replace( ".", "" )
            
            #-- END check to see if remove periods --#
            
            # strip white space.
            working_string = working_string.strip()

        #-- END check to see if anything passed in. --#

        # return working_string.
        name_part_OUT = working_string

        return name_part_OUT
        
    #-- END method standardize_name_part() --#
        
        
    #----------------------------------------------------------------------
    # instance methods
    #----------------------------------------------------------------------

    def __str__( self ):
 
        # return reference
        string_OUT = ''
        
        # declare variables
        string_list = []
 
        if ( self.id ):
        
            string_OUT = str( self.id ) + " - "
            
        #-- END check to see if ID --#
                
        string_OUT += self.last_name + ', ' + self.first_name
        
        # middle name?
        if ( self.middle_name ):
        
            string_OUT += " " + self.middle_name
            
        #-- END middle name check --#

        if ( ( self.title ) or ( self.capture_method ) ):
        
            string_OUT += " ( "
        
            string_list = []
        
            if ( self.title ):
            
                # add title to list
                string_list.append( "title = " + self.title )
                
            #-- END check for title --#
            
            if ( self.capture_method ):
            
                # add capture method to the list.
                string_list.append( "capture_method = " + self.capture_method )
                
            #-- END check for capture_method --#
            
            string_OUT += "; ".join( string_list )

            string_OUT += " )"
            
        #-- END check to see if we have a title or capture_method. --#
 
        return string_OUT

    #-- END method __str__() --#


    def standardize_name_parts( self, remove_periods_IN = False ):
        
        '''
        This method looks at each part of a name and for each, calls the method
           standardize_name_part() to do the following to standardize it, in this
           order:
           - removes any commas.
           - strips white space from the beginning and end.
           - More to come?  Best list is in standardize_name_part()
           
        preconditions: None.

        postconditions: if needed, name parts in instance are updated to be
           standardized.  Instance is not saved.
        '''
        
        # return reference
        instance_OUT = None
        
        # declare variables
        me = "standardize_name_parts"
        
        # standardize name parts.
        if ( self.name_prefix ):
    
            self.name_prefix = self.standardize_name_part( self.name_prefix, remove_periods_IN )
            
        #-- END check to see if name_prefix.
        
        if ( self.first_name ):
    
            self.first_name = self.standardize_name_part( self.first_name, remove_periods_IN )
            
        #-- END check to see if first_name.
        
        if ( self.middle_name ):
    
            self.middle_name = self.standardize_name_part( self.middle_name, remove_periods_IN )
            
        #-- END check to see if middle_name.
        
        if ( self.last_name ):
    
            self.last_name = self.standardize_name_part( self.last_name, remove_periods_IN )
            
        #-- END check to see if last_name.
        
        if ( self.name_suffix ):
    
            self.name_suffix = self.standardize_name_part( self.name_suffix, remove_periods_IN )
            
        #-- END check to see if name_suffix.
        
        if ( self.nickname ):
    
            self.nickname = self.standardize_name_part( self.nickname, remove_periods_IN )
            
        #-- END check to see if nickname.
        
        return instance_OUT
        
    #-- END method clean_up_name_parts() --#


    def save( self, *args, **kwargs ):
        
        '''
        Overridden save() method that automatically creates a full name string
           for a person in case one is not specified.

        Note: looks like child classes don't have to override save method.
        '''
        
        # declare variables.
        name_HumanName = None
        generated_full_name_string = ""
        
        # standardize name parts
        self.standardize_name_parts()
        
        # Make HumanName() instance from this Person's name parts.
        name_HumanName = self.to_HumanName()
            
        # use it to update the full_name_string.
        self.full_name_string = unicode( name_HumanName )
        
        # call parent save() method.
        super( Abstract_Person, self ).save( *args, **kwargs )
        
    #-- END method save() --#


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
        nickname = ""
        standardized_hn = None
                
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
            nickname = parsed_name.nickname
            
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
            
            # nickname
            if ( nickname ):
    
                # set value
                self.nickname = nickname
                
            #-- END nickname --#
            
            # standardize name parts
            self.standardize_name_parts()
            
            # Finally, store the full name string (and the pickled object?).
            standardized_hn = self.to_HumanName()
            self.full_name_string = unicode( standardized_hn )
            #self.nameparser_pickled = pickle.dumps( standardized_hn )
            
        else:
        
            # No name, returning None
            output_debug( "In " + me + ": no name passed in, returning None." )
        
        #-- END check to see if we have a name. --#
        
    #-- END ethod set_name() --#
    

    def to_HumanName( self ):
        
        '''
        This method creates a nameparser HumanName() object instance, then uses
           the values from this Abstract_Person instance to populate it.  Returns
           the HumanName instance.
           
        preconditions: None.
        postconditions: None.
        '''
        
        # return reference
        instance_OUT = None
        
        # declare variables
        me = "to_HumanName"
        
        # make HumanString instance.
        instance_OUT = HumanName()

        # Use nested values to populate HumanName.
        if ( self.name_prefix ):
    
            instance_OUT.title = self.name_prefix
            
        #-- END check to see if name_prefix.
        
        if ( self.first_name ):
    
            instance_OUT.first = self.first_name
            
        #-- END check to see if first_name.
        
        if ( self.middle_name ):
    
            instance_OUT.middle = self.middle_name
            
        #-- END check to see if middle_name.
        
        if ( self.last_name ):
    
            instance_OUT.last = self.last_name
            
        #-- END check to see if last_name.
        
        if ( self.name_suffix ):
    
            instance_OUT.suffix = self.name_suffix
            
        #-- END check to see if name_suffix.
        
        if ( self.nickname ):
    
            instance_OUT.nickname = self.nickname
            
        #-- END check to see if nickname.
        
        return instance_OUT
        
    #-- END method to_HumanName() --#


#== END Abstract_Person Model ===========================================================#


# Person model
@python_2_unicode_compatible
class Person( Abstract_Person ):

    # Properties from Abstract_Person:
    '''
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
    is_ambiguous = models.BooleanField( default = False )
    notes = models.TextField( blank = True )
    '''

    #----------------------------------------------------------------------
    # instance methods
    #----------------------------------------------------------------------

    def __str__( self ):
 
        # return reference
        string_OUT = ''
        
        if ( self.id ):
        
            string_OUT = str( self.id ) + " - "
            
        #-- END check to see if ID --#
                
        string_OUT += str( self.last_name ) + ', ' + str( self.first_name )        
        # middle name?
        if ( self.middle_name ):
        
            string_OUT += " " + self.middle_name
            
        #-- END middle name check --#

        if ( self.title ):
        
            string_OUT = string_OUT + " ( " + self.title + " )"
            
        #-- END check to see if we have a title. --#
 
        return string_OUT

    #-- END method __str__() --#
    

    def associate_newspaper( self, newspaper_IN, notes_IN = None ):
        
        '''
        Accepts newspaper instance of newspaper in which this person has either
           written or been quoted, plus optional notes to be stored with the
           association.  Checks to see if that newspaper is already associated
           with the person.  If no, creates association.  If yes, returns
           existing record.  If error, returns None.
        '''
        
        # return reference
        instance_OUT = None
        
        # declare variables
        me = "associate_newspaper"
        related_newspaper_qs = None
        related_newspaper_count = -1
        debug_message = ""
        
        # got a newspaper?
        if ( newspaper_IN is not None ):
        
            # see if Person_Newspaper for this newspaper.
            related_newspaper_qs = self.person_newspaper_set.filter( newspaper = newspaper_IN )
            
            # got a match?
            related_newspaper_count = related_newspaper_qs.count()
            if ( related_newspaper_count == 0 ):
            
                # No. Relate newspaper to person.
                instance_OUT = Person_Newspaper()
    
                # set values
                instance_OUT.person = self
                instance_OUT.newspaper = newspaper_IN
                
                if ( notes_IN is not None ):

                    instance_OUT.notes = notes_IN
                    
                #-- END check to see if notes. --#
                
                # save.
                instance_OUT.save()

                debug_message = "In Person." + me + ": ----> created tie from " + str( self ) + " to newspaper " + str( newspaper_IN )
                output_debug( debug_message )
            
            else:
            
                # return reference.  Use get().  If more than one, error, so
                #    exception is fine.
                instance_OUT = related_newspaper_qs.get()

                debug_message = "In Person." + me + ": ----> tie exists from " + str( self ) + " to newspaper " + str( newspaper_IN )
                output_debug( debug_message )
            
            # -- END check to see if Person_Newspaper for current paper. --#
            
        #-- END check to see if newspaper passed in. --#
        
        return instance_OUT
        
    #-- END method associate_newspaper() --#
    

    def associate_external_uuid( self, uuid_IN, source_IN, name_IN = None, notes_IN = None ):
        
        '''
        Accepts UUID for the person from an external system (the source), plus
           optional name and notes on the UUID.  Checks to see if that UUID is
           already associated with the person.  If no, creates association.  If
           yes, returns existing record.  If error, returns None.
        '''
        
        # return reference
        instance_OUT = None
        
        # declare variables
        me = "associate_external_uuid"
        related_uuid_qs = None
        related_uuid_count = -1
        debug_message = ""
        
        # got a UUID value?
        if ( ( uuid_IN is not None ) and ( uuid_IN != "" ) ):
        
            # we do.  See if person is already associated with the UUID.
            related_uuid_qs = self.person_external_uuid_set.filter( uuid = uuid_IN )
            
            # got a match?
            related_uuid_count = related_uuid_qs.count()
            if ( related_uuid_count == 0 ):
            
                # not yet associated.  Make Person_External_UUID association.
                instance_OUT = Person_External_UUID()

                # set values
                instance_OUT.person = self
                instance_OUT.uuid = uuid_IN
                
                if ( source_IN is not None ):

                    instance_OUT.source = source_IN
                    
                #-- END check to see if name passed in. --#

                if ( name_IN is not None ):

                    instance_OUT.name = name_IN
                    
                #-- END check to see if name passed in. --#
                    
                if ( notes_IN is not None ):

                    instance_OUT.notes = notes_IN
                    
                #-- END check to see if name passed in. --#
                
                # save.
                instance_OUT.save()

                debug_message = "In Person." + me + ": ----> created tie from " + str( self ) + " to UUID " + uuid_IN
                output_debug( debug_message )
            
            else:
            
                # return reference.  Use get().  If more than one, error, so
                #    exception is fine.
                instance_OUT = related_uuid_qs.get()

                debug_message = "In Person." + me + ": ----> tie exists from " + str( self ) + " to UUID " + uuid_IN
                output_debug( debug_message )
            
            #-- END check to see if UUID match. --#
        
        #-- END check to see if external UUID --#

        return instance_OUT
        
    #-- END method associate_external_uuid() --#
    

#== END Person Model ===========================================================#


# Alternate_Name model
@python_2_unicode_compatible
class Alternate_Name( Abstract_Person ):

    '''
    Model that can be used to hold alternate names for a given person.
       For now, no way to tie to newspaper or external UUID.  And not used at the
       moment.  But, planning ahead...
    '''

    # Properties from Abstract_Person:
    '''
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
    is_ambiguous = models.BooleanField( default = False )
    notes = models.TextField( blank = True )
    '''
    
    person = models.ForeignKey( Person )

    #----------------------------------------------------------------------
    # instance methods
    #----------------------------------------------------------------------

    def __str__( self ):
 
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

    #-- END method __str__() --#
    

#== END Alternate_Name Model ===========================================================#


# Orgnization model
@python_2_unicode_compatible
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

    def __str__( self ):
        string_OUT = self.name
        return string_OUT

#= End Organization Model ======================================================


# Person_Organization model
@python_2_unicode_compatible
class Person_Organization( models.Model ):

    person = models.ForeignKey( Person )
    organization = models.ForeignKey( Organization, blank = True, null = True )
    title = models.CharField( max_length = 255, blank = True )

    #----------------------------------------------------------------------
    # methods
    #----------------------------------------------------------------------

    def __str__( self ):
        string_OUT = self.organization.name
        if ( self.title != '' ):
            string_OUT = string_OUT + " ( " + self.title + " )"
        return string_OUT

#= End Person_Organization Model ======================================================


# Document model
@python_2_unicode_compatible
class Document( models.Model ):

    name = models.CharField( max_length = 255 )
    description = models.TextField( blank = True)
    organization = models.ForeignKey( Organization, blank = True, null = True )

    #----------------------------------------------------------------------
    # methods
    #----------------------------------------------------------------------

    def __str__( self ):
        string_OUT = self.name
        return string_OUT

#= End Document Model ======================================================


# Newspaper model
@python_2_unicode_compatible
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

    def __str__( self ):
        string_OUT = self.name
        return string_OUT

#= End Newspaper Model ======================================================


# Article_Topic model
#@python_2_unicode_compatible
#class Article_Topic( models.Model ):

    #topic = models.ForeignKey( Topic )
    #rank = models.IntegerField()

    #----------------------------------------------------------------------
    # methods
    #----------------------------------------------------------------------

    #def __str__( self ):

    #    string_OUT = '%d - %s' % ( self.rank, self.topic.name )
    #    return string_OUT
        
    #-- END __str__() method --#

#= End Article_Topic Model ======================================================


# Person_External_UUID model
@python_2_unicode_compatible
class Person_External_UUID( models.Model ):

    person = models.ForeignKey( Person )
    name = models.CharField( max_length = 255, null = True, blank = True )
    uuid = models.TextField( blank = True, null = True )
    source = models.CharField( max_length = 255, null = True, blank = True )
    notes = models.TextField( blank = True, null = True )

    #----------------------------------------------------------------------
    # methods
    #----------------------------------------------------------------------


    def __str__( self ):
        
        # return reference
        string_OUT = ""
        
        # declare variables
        prefix_string = ""
        
        if ( self.id ):
        
            # yes. output.
            string_OUT += str( self.id )
            prefix_string = " - "

        #-- END check to see if ID --#

        if ( self.name ):
        
            string_OUT += prefix_string + self.name
            prefix_string = " - "
            
        #-- END check to see if newspaper. --#
            
        if ( self.source ):
        
            string_OUT += prefix_string + " ( " + self.source + " )"
            prefix_string = " - "
            
        #-- END check to see if newspaper. --#
            
        if ( self.uuid ):
        
            string_OUT += prefix_string + self.uuid
            prefix_string = " - "
            
        #-- END check to see if newspaper. --#
            
        return string_OUT
        
    #-- END method __str__() --#


#= End Person_External_UUID Model ======================================================


# Person_Newspaper model
@python_2_unicode_compatible
class Person_Newspaper( models.Model ):

    person = models.ForeignKey( Person )
    newspaper = models.ForeignKey( Newspaper, blank = True, null = True )
    notes = models.TextField( blank = True, null = True )

    #----------------------------------------------------------------------
    # methods
    #----------------------------------------------------------------------


    def __str__( self ):
        
        # return reference
        string_OUT = ""
        
        # declare variables
        prefix_string = ""
        
        if ( self.id ):
        
            # yes. output.
            string_OUT += str( self.id )
            prefix_string = " - "

        #-- END check to see if ID --#

        if ( self.newspaper ):
        
            string_OUT += prefix_string + self.newspaper.name
            prefix_string = " - "
            
        #-- END check to see if newspaper. --#
            
        if ( self.person ):
        
            string_OUT += prefix_string + str( self.person.id )
            prefix_string = " - "
            
        #-- END check to see if newspaper. --#
            
        return string_OUT
        
    #-- END method __str__() --#


#= End Person_Newspaper Model ======================================================


# Article model
@python_2_unicode_compatible
class Article( models.Model ):

    #----------------------------------------------------------------------------
    # Constants-ish
    #----------------------------------------------------------------------------
    
    
    # parameters that can be passed in to class methods 
    PARAM_AUTOPROC_ALL = "autoproc_all"
    PARAM_AUTOPROC_AUTHORS = "autoproc_authors"

    # LOOKUP parameters
    #==================

    # newspaper filter (expects instance of Newspaper model)
    PARAM_NEWSPAPER_ID = "newspaper_id"
    PARAM_NEWSPAPER_NEWSBANK_CODE = "newspaper_newsbank_code"
    PARAM_NEWSPAPER_INSTANCE = "newspaper"

    # date range parameters, for article lookup.
    PARAM_START_DATE = "start_date"
    PARAM_END_DATE = "end_date"
    PARAM_SINGLE_DATE = "single_date"
    DEFAULT_DATE_FORMAT = "%Y-%m-%d"    
    
    # section selection parameters.
    PARAM_SECTION_NAME = "section_name"
    PARAM_SECTION_NAME_LIST = "section_name_list"
    PARAM_CUSTOM_SECTION_Q = "custom_section_q"
    PARAM_JUST_PROCESS_ALL = "just_process_all" # set to True if just want sum of all sections, not records for each individual section.  If False, processes each section individually, then generates the "all" record.

    # other article parameters.
    PARAM_CUSTOM_ARTICLE_Q = "custom_article_q"
    
    # Django queryset parameters
    #===========================

    # variables for building nuanced queries in django.
    # Will be specific to each paper, so using Grand Rapids Press as example.

    # Grand Rapids Press
    GRP_LOCAL_SECTION_NAME_LIST = [ "Business", "City and Region", "Front Page", "Lakeshore", "Religion", "Special", "Sports", "State" ]
    GRP_NEWS_SECTION_NAME_LIST = [ "Business", "City and Region", "Front Page", "Lakeshore", "Religion", "Special", "State" ]
    Q_GRP_IN_HOUSE_AUTHOR = Q( author_varchar__iregex = r'.* */ *THE GRAND RAPIDS PRESS$' ) | Q( author_varchar__iregex = r'.* */ *PRESS .* EDITOR$' ) | Q( author_varchar__iregex = r'.* */ *GRAND RAPIDS PRESS .* BUREAU$' ) | Q( author_varchar__iregex = r'.* */ *SPECIAL TO THE PRESS$' )
    
    
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
    author_affiliation = models.CharField( max_length = 255, blank = True, null = True )
    headline = models.CharField( max_length = 255 )
    # What is this? - author = models.CharField( max_length = 255, blank = True, null = True )

    # text = models.TextField( blank = True ) - moved to related Article_Text instance.
    # - to retrieve Article_Text instance for this Article: self.article_text_set.get()

    corrections = models.TextField( blank = True, null = True )
    edition = models.CharField( max_length = 255, blank = True, null = True )
    index_terms = models.TextField( blank = True, null = True )
    archive_source = models.CharField( max_length = 255, blank = True, null = True )
    archive_id = models.CharField( max_length = 255, blank = True, null = True )
    permalink = models.TextField( blank = True, null = True )
    copyright = models.TextField( blank = True, null = True )

    # notes = models.TextField( blank = True, null = True ) - moved to related Article_Notes instance.
    # - to retrieve Article_Notes instance for this Article: self.article_notes_set.get()

    # raw_html = models.TextField( blank = True, null = True ) - moved to related Article_RawData instance.
    # - to retrieve Article_RawData instance for this Article: self.article_rawdata_set.get()

    # tags!
    tags = TaggableManager( blank = True )

    status = models.CharField( max_length = 255, blank = True, null = True, default = "new" )
    is_local_news = models.BooleanField( default = 0 )
    is_sports = models.BooleanField( default = 0 )
    is_local_author = models.BooleanField( default = 0 )
    create_date = models.DateTimeField( auto_now_add = True )
    last_modified = models.DateTimeField( auto_now = True )

    # we have the option of adding these relations here, at an article level,
    #    but for now assuming they are to be coded in Article_Data, not here, so
    #    we can track agreement, compare coding from different coders.
    #topics = models.ManyToManyField( Article_Topic )
    #authors = models.ManyToManyField( Article_Author )
    #sources = models.ManyToManyField( Article_Source )
    #locations = models.ManyToManyField( Article_Location, blank = True )

    #----------------------------------------------------------------------------
    # Meta class
    #----------------------------------------------------------------------------

    # Meta-data for this class.
    class Meta:
        ordering = [ 'pub_date', 'section', 'page' ]

    #----------------------------------------------------------------------------
    # class methods
    #----------------------------------------------------------------------------


    @classmethod
    def add_section_filter_to_article_qs( cls, section_list_IN = [], qs_IN = None, *args, **kwargs ):
        
        '''
        Accepts section name and query string.  If "all", adds a filter to
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
        me = "add_section_filter_to_article_qs"
        my_section_list = ""
        
        # got a query set?
        if ( qs_IN ):
        
            # use the one passed in.
            qs_OUT = qs_IN
            
            #output_debug( "QuerySet passed in, using it.", me, "*** " )
        
        else:
        
            # No.  Make one.
            qs_OUT = cls.objects.all()
            
            #output_debug( "No QuerySet passed in, using fresh one.", me, "*** " )
        
        #-- END check to see if query set passed in --#
        
        # get section name.
        my_section_list = section_list_IN
        
        # add filter for name being in the list
        qs_OUT = qs_OUT.filter( section__in = my_section_list )
                
        return qs_OUT
        
    #-- END method add_section_filter_to_article_qs() --#


    @classmethod
    def create_q_article_date_range( cls, start_date_IN = "", end_date_IN = "", *args, **kwargs ):
    
        '''
        Accepts string start and end dates (YYYY-MM-DD format). in the keyword
           arguments.  Creates a Q() instance that filters dates based on start
           and end date passed in. If both are missing, does nothing.  If one or
           other passed in, filters accordingly.
        Preconditions: Dates must be strings in YYYY-MM-DD format.
        Postconditions: Returns the Q() instance - to use it, you must pass it
           to a QuerySet's filter method.  If neither start nor end dates are
           passed in, returns None.
        '''
        
        # return reference
        q_OUT = None
        
        # declare variables
        start_date = ""
        end_date = ""
        
        # retrieve dates
        # start date
        start_date = start_date_IN
        if ( start_date == "" ):

            # no start date passed in. Check in the kwargs.
            if ( cls.PARAM_START_DATE in kwargs ):
        
                # yup.  Use it.
                start_date = kwargs[ cls.PARAM_START_DATE ]
        
            #-- END check to see if start date in arguments --#

        #-- END check to see if start date passed in. --#
        
        # end date
        end_date = end_date_IN
        if( end_date == "" ):
            
            # no end date passed in.  Check in kwargs.
            if ( cls.PARAM_END_DATE in kwargs ):
        
                # yup.  Use it.
                end_date = kwargs[ cls.PARAM_END_DATE ]
        
            #-- END check to see if end date in arguments --#

        #-- END check to see if end date passed in.

        if ( ( start_date ) and ( end_date ) ):
        
            # both start and end.
            q_OUT = Q( pub_date__gte = datetime.datetime.strptime( start_date, cls.DEFAULT_DATE_FORMAT ) )
            q_OUT = q_OUT & Q( pub_date__lte = datetime.datetime.strptime( end_date, cls.DEFAULT_DATE_FORMAT ) )
        
        elif( start_date ):
        
            # just start date
            q_OUT = Q( pub_date__gte = datetime.datetime.strptime( start_date, cls.DEFAULT_DATE_FORMAT ) )
        
        elif( end_date ):
        
            # just end date
            q_OUT = Q( pub_date__lte = datetime.datetime.strptime( end_date, cls.DEFAULT_DATE_FORMAT ) )
        
        #-- END conditional to see what we got. --#

        return q_OUT
    
    #-- END method create_q_article_date_range() --#


    @classmethod
    def filter_articles( cls, qs_IN = None, *args, **kwargs ):
        
        '''
        Accepts parameters in kwargs.  Uses arguments to filter a QuerySet of
           articles, which it subsequently returns.  Currently, you can pass
           this method a section name list and date range start and end dates.
           You can also pass in an optional QuerySet instance.  If QuerySet
           passed in, this method appends filters to it.  If not, starts with
           a new QuerySet.
        Preconditions: None.
        Postconditions: returns the QuerySet passed in with filters added as
           specified by arguments.  If no QuerySet passed in, creates new
           Article QuerySet, returns it with filters added.
        '''
        
        # return reference
        qs_OUT = None
        
        # declare variables
        me = "filter_articles"
        newspaper_ID_IN = None
        newspaper_newsbank_code_IN = None
        newspaper_instance = None
        q_date_range = None
        section_name_list_IN = None
        custom_q_IN = None

        # got a query set?
        if ( qs_IN ):
        
            # use the one passed in.
            qs_OUT = qs_IN
            
            #output_debug( "QuerySet passed in, using it.", me, "*** " )
        
        else:
        
            # No.  Make one.
            qs_OUT = cls.objects.all()
            
            #output_debug( "No QuerySet passed in, using fresh one.", me, "*** " )
        
        #-- END check to see if query set passed in --#

        # newspapers
        #-----------

        # try to update QuerySet for selected newspaper.
        if ( cls.PARAM_NEWSPAPER_ID in kwargs ):
    
            # yup.  Use it.
            newspaper_ID_IN = kwargs[ cls.PARAM_NEWSPAPER_ID ]
            newspaper_instance = Newspaper.objects.get( pk = newspaper_ID_IN )
    
        #-- END check to see if newspaper instance in arguments --#

        # try to update QuerySet for selected newspaper.
        if ( cls.PARAM_NEWSPAPER_NEWSBANK_CODE in kwargs ):
    
            # yup.  Use it.
            newspaper_newsbank_code_IN = kwargs[ cls.PARAM_NEWSPAPER_NEWSBANK_CODE ]
            newspaper_instance = Newspaper.objects.get( newsbank_code = newspaper_newsbank_code_IN )
    
        #-- END check to see if newspaper instance in arguments --#

        # try to update QuerySet for selected newspaper.
        if ( cls.PARAM_NEWSPAPER_INSTANCE in kwargs ):
    
            # yup.  Use it.
            newspaper_instance = kwargs[ cls.PARAM_NEWSPAPER_INSTANCE ]
    
        #-- END check to see if newspaper instance in arguments --#

        # got a newspaper instance?
        if ( newspaper_instance ):

            # Yes.  Filter.
            qs_OUT = qs_OUT.filter( newspaper = newspaper_instance )

        # date range
        #-----------

        # try to get Q() for start and end dates.
        q_date_range = cls.create_q_article_date_range( "", "", *args, **kwargs )

        # got a Q()?
        if ( q_date_range ):

            # Yes.  Add it to query set.
            qs_OUT = qs_OUT.filter( q_date_range )

        #-- END check to see if date range present.

        # Sections
        #---------

        # try to update QuerySet for selected sections.
        if ( cls.PARAM_SECTION_NAME_LIST in kwargs ):
    
            # yup.  Use it.
            section_name_list_IN = kwargs[ cls.PARAM_SECTION_NAME_LIST ]
            qs_OUT = cls.add_section_filter_to_article_qs( section_name_list_IN, qs_OUT )
    
        #-- END check to see if start date in arguments --#

        # Custom-built Q() object
        #------------------------
        # try to update QuerySet for selected sections.
        if ( cls.PARAM_CUSTOM_ARTICLE_Q in kwargs ):

            # Get the Q and filter with it.
            custom_q_IN = kwargs[ cls.PARAM_CUSTOM_ARTICLE_Q ]

            # got something in the parameter?
            if ( custom_q_IN ):

                # yes.  Filter.
                qs_OUT = qs_OUT.filter( custom_q_IN )

            #-- END check to see if custom Q() present. --#

        #-- END check to see if Custom Q argument present --#

        return qs_OUT
        
    #-- END method filter_articles() --#


    #----------------------------------------------------------------------------
    # instance methods
    #----------------------------------------------------------------------------


    def __str__( self ):

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

    #-- END method __str__() --#
    
    
    def get_article_data_for_coder( self, coder_IN = None, coder_type_IN = "", *args, **kwargs ):

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
            
            # got a coder type?
            if ( ( coder_type_IN is not None ) and ( coder_type_IN != "" ) ):
            
                # yes.  filter on it, as well.
                article_data_qs = article_data_qs.filter( coder_type = coder_type_IN )
            
            #-- END check to see if coder type present. --#
            
            # what we got back?
            article_data_count = article_data_qs.count()
            
            # if 0, create new, populate, and save.
            if ( article_data_count == 0 ):
            
                # create instance
                instance_OUT = Article_Data()

                # populate
                instance_OUT.article = self
                instance_OUT.coder = coder_IN

                # got a coder type?
                if ( ( coder_type_IN is not None ) and ( coder_type_IN != "" ) ):
                
                    # yes.  save it.
                    instance_OUT.coder_type = coder_type_IN
                
                #-- END check to see if coder type present. --#

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
            instance_OUT.content_type = "text"
            
        else:
            
            # Either error or more than one (so error).
            output_debug( "Found more than one related Article_Notes.  Doing nothing.", me )
            
        #-- END check to see if have one or not. --#

        if ( instance_OUT ):

            # set the text in the instance.
            instance_OUT.set_content( text_IN )
            
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
            instance_OUT.content_type = "html"
            
        else:
            
            # Either error or more than one (so error).
            output_debug( "Found more than one related Article_RawData.  Doing nothing.", me )
            
        #-- END check to see if have one or not. --#

        if ( instance_OUT ):

            # set the text in the instance.
            instance_OUT.set_content( text_IN )
            
            # save?
            if ( do_save_IN == True ):
                
                # yes.
                instance_OUT.save()
                
            #-- END check to see if we save. --#

        #-- END check to see if instance. --#
        
        return instance_OUT

    #-- END method set_raw_html() --#
    

    def set_text( self, text_IN = "", do_save_IN = True, clean_text_IN = True, *args, **kwargs ):
        
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
        cleaned_text = ""
        
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
            instance_OUT.content_type = "canonical"
            
        else:
            
            # Either error or more than one (so error).
            output_debug( "Found more than one related text.  Doing nothing.", me )
            
        #-- END check to see if have one or not. --#

        if ( instance_OUT ):

            # set the text in the instance.
            instance_OUT.set_text( text_IN, clean_text_IN )
            
            # save?
            if ( do_save_IN == True ):
                
                # yes.
                instance_OUT.save()
                
            #-- END check to see if we save. --#

        #-- END check to see if instance. --#
        
        return instance_OUT

    #-- END method set_text() --#
    

#= End Article Model ============================================================


# Abstract_Related_Content model
@python_2_unicode_compatible
class Abstract_Related_Content( models.Model ):

    # Content types:
    CONTENT_TYPE_CANONICAL = 'canonical'
    CONTENT_TYPE_TEXT = 'text'
    CONTENT_TYPE_HTML = 'html'
    CONTENT_TYPE_JSON = 'json'
    CONTENT_TYPE_XML = 'xml'
    CONTENT_TYPE_OTHER = 'other'
    CONTENT_TYPE_NONE = 'none'
    CONTENT_TYPE_DEFAULT = CONTENT_TYPE_TEXT
    
    CONTENT_TYPE_CHOICES = (
        ( CONTENT_TYPE_CANONICAL, "Canonical" ),
        ( CONTENT_TYPE_TEXT, "Text" ),
        ( CONTENT_TYPE_HTML, "HTML" ),
        ( CONTENT_TYPE_JSON, "JSON" ),
        ( CONTENT_TYPE_XML, "XML" ),
        ( CONTENT_TYPE_OTHER, "Other" ),
        ( CONTENT_TYPE_NONE, "None" )
    )

    #----------------------------------------------------------------------
    # model fields and meta
    #----------------------------------------------------------------------

    #article = models.ForeignKey( Article, unique = True )
    content_type = models.CharField( max_length = 255, choices = CONTENT_TYPE_CHOICES, blank = True, null = True, default = "none" )
    content = models.TextField()
    status = models.CharField( max_length = 255, blank = True, null = True )
    source = models.CharField( max_length = 255, blank = True, null = True )
    content_description = models.TextField( blank = True, null = True )
    create_date = models.DateTimeField( auto_now_add = True )
    last_modified = models.DateTimeField( auto_now = True )

    # meta class so we know this is an abstract class.
    class Meta:
        abstract = True
        ordering = [ 'last_modified', 'create_date' ]

    #----------------------------------------------------------------------
    # NOT instance variables
    # Class variables - overriden by __init__() per instance if same names, but
    #    if not set there, shared!
    #----------------------------------------------------------------------


    #bs_helper = None
    

    #----------------------------------------------------------------------------
    # methods
    #----------------------------------------------------------------------------


    def __init__( self, *args, **kwargs ):
        
        # call parent __init()__ first.
        super( Abstract_Related_Content, self ).__init__( *args, **kwargs )

        # then, initialize variable.
        self.bs_helper = None
        
    #-- END method __init__() --#


    def get_bs_helper( self ):
    
        # return reference
        instance_OUT = None
        
        # get instance.
        instance_OUT = self.bs_helper
                
        # got one?
        if ( not( instance_OUT ) ):
        
            # no.  Create and store.
            self.bs_helper = BeautifulSoupHelper()
            
            # try again.  If nothing this time, nothing we can do.  Return it.
            instance_OUT = self.bs_helper
            
        #-- END check to see if regex is stored in instance --#

        return instance_OUT
    
    #-- END method get_bs_helper() --#


    def get_content( self, *args, **kwargs ):
        
        '''
        Returns content nested in this instance.
        Preconditions: None
        Postconditions: None
        
        Returns the content exactly as it is stored in the instance.
        '''
        
        # return reference
        content_OUT = None

        # declare variables
        me = "get_content"

        # return the content.
        content_OUT = self.content
                
        return content_OUT

    #-- END method get_content() --#


    def set_content( self, value_IN = "", *args, **kwargs ):
        
        '''
        Accepts a piece of text.  Stores it in this instance's content variable.
        Preconditions: None
        Postconditions: None
        
        Returns the content as it is stored in the instance.
        '''
        
        # return reference
        value_OUT = None

        # declare variables
        me = "set_content"

        # set the text in the instance.
        self.content = value_IN
        
        # return the content.
        value_OUT = self.content
                
        return value_OUT

    #-- END method set_content() --#
    

    def to_string( self ):

        # return reference
        string_OUT = ""
        
        if ( self.id ):
            
            string_OUT += str( self.id ) + " - "
            
        #-- END check to see if ID --#
             
        if ( self.content_description ):
        
            string_OUT += self.content_description
            
        #-- END check to see if content_description --#
        
        if ( self.content_type ):
            
            string_OUT += " of type \"" + self.content_type + "\""
            
        #-- END check to see if there is a type --#
        
        return string_OUT

    #-- END method __str__() --#


    def __str__( self ):

        # return reference
        string_OUT = ""
        
        string_OUT = self.to_string()
        
        return string_OUT

    #-- END method __str__() --#


#-- END abstract Abstract_Article_Content model --#


# Article_Content model
@python_2_unicode_compatible
class Article_Content( Abstract_Related_Content ):

    #----------------------------------------------------------------------
    # model fields and meta
    #----------------------------------------------------------------------

    # allow more than one related piece of "Article_Content" per article.
    article = models.ForeignKey( Article )

    # meta class so we know this is an abstract class.
    class Meta:
        abstract = True
        ordering = [ 'article', 'last_modified', 'create_date' ]

    #----------------------------------------------------------------------------
    # instance methods
    #----------------------------------------------------------------------------


    def to_string( self ):

        # return reference
        string_OUT = ""
        
        if ( self.id ):
            
            string_OUT += str( self.id ) + " - "
            
        #-- END check to see if ID --#
             
        if ( self.content_description ):
        
            string_OUT += self.content_description
            
        #-- END check to see if content_description --#
        
        if ( self.content_type ):
            
            string_OUT += " of type \"" + self.content_type + "\""
            
        #-- END check to see if there is a type --#
             
        string_OUT += " for article: " + str( self.article )
        
        return string_OUT

    #-- END method to_string() --#


    def __str__( self ):

        # return reference
        string_OUT = ""
        
        string_OUT = self.to_string()
        
        return string_OUT

    #-- END method __str__() --#


#-- END abstract Article_Content model --#


# Unique_Article_Content model
@python_2_unicode_compatible
class Unique_Article_Content( Abstract_Related_Content ):

    #----------------------------------------------------------------------
    # model fields and meta
    #----------------------------------------------------------------------

    # only allow one related piece of "Unique_Article_Content" per article.
    article = models.ForeignKey( Article, unique = True )

    # meta class so we know this is an abstract class.
    class Meta:
        abstract = True
        ordering = [ 'article', 'last_modified', 'create_date' ]

    #----------------------------------------------------------------------------
    # instance methods
    #----------------------------------------------------------------------------


    def to_string( self ):

        # return reference
        string_OUT = ""
        
        if ( self.id ):
            
            string_OUT += str( self.id ) + " - "
            
        #-- END check to see if ID --#
             
        if ( self.content_description ):
        
            string_OUT += self.content_description
            
        #-- END check to see if content_description --#
        
        if ( self.content_type ):
            
            string_OUT += " of type \"" + self.content_type + "\""
            
        #-- END check to see if there is a type --#
             
        string_OUT += " for article: " + str( self.article )
        
        return string_OUT

    #-- END method to_string() --#


    def __str__( self ):

        # return reference
        string_OUT = ""
        
        string_OUT = self.to_string()
        
        return string_OUT

    #-- END method __str__() --#


#-- END abstract Unique_Article_Content model --#


# Article_Notes model
@python_2_unicode_compatible
class Article_Notes( Article_Content ):

    def __str__( self ):

        # return reference
        string_OUT = ""
        
        # set content description
        self.content_description = "notes"
        
        # call string method.
        string_OUT = super( Article_Notes, self ).to_string()
                
        return string_OUT

    #-- END method __str__() --#

#-- END Article_Notes model --#


# Article_RawData model
@python_2_unicode_compatible
class Article_RawData( Unique_Article_Content ):

    def __str__( self ):

        # return reference
        string_OUT = ""
        
        # set content description
        self.content_description = "raw data"
        
        # call string method.
        string_OUT = super( Article_RawData, self ).to_string()
        
        return string_OUT

    #-- END method __str__() --#

#-- END Article_RawData model --#


# Article_Text model
@python_2_unicode_compatible
class Article_Text( Unique_Article_Content ):

    #----------------------------------------------------------------------------
    # Constants-ish
    #----------------------------------------------------------------------------
    

    # Body Text Cleanup
    #==================
    
    BODY_TEXT_ALLOWED_TAGS = [ 'p', ]
    BODY_TEXT_ALLOWED_ATTRS = {
        'p' : [ 'id', ],
    }
    
    # Names for dictionary of results of find_in_text() (FIT) method.
    FIT_CANONICAL_INDEX_LIST = "canonical_index_list"
    FIT_TEXT_INDEX_LIST = "index_list"
    FIT_FIRST_WORD_NUMBER_LIST = "first_word_number_list"
    FIT_LAST_WORD_NUMBER_LIST = "last_word_number_list"
    FIT_PARAGRAPH_NUMBER_LIST = "paragraph_number_list"
    
 
    #----------------------------------------------------------------------------
    # class methods
    #----------------------------------------------------------------------------


    @classmethod
    def clean_body_text( cls, body_text_IN = "", *args, **kwargs ):
    
        '''
        Accepts body text string.  Removes extra white space, then removes HTML
           other than <p> tags.  Returns cleaned string.
        '''
        
        # return reference
        body_text_OUT = ""
        
        # declare variables
        allowed_tags = None
        allowed_attrs = None
        
        # start with text passed in.
        body_text_OUT = body_text_IN
        
        # use bleach to strip out HTML.
        allowed_tags = cls.BODY_TEXT_ALLOWED_TAGS
        allowed_attrs = cls.BODY_TEXT_ALLOWED_ATTRS
        body_text_OUT = HTMLHelper.remove_html( body_text_OUT, allowed_tags, allowed_attrs )
        
        # compact white space
        body_text_OUT = StringHelper.replace_white_space( body_text_OUT, ' ' )

        return body_text_OUT
        
    #-- END class method clean_body_text() --#


    @classmethod
    def convert_string_to_word_list( cls, string_IN ):
        
        '''
        Accepts a string, for now, just calls ".split()" on it to split it on
           white space.  Eventually, might make it fancier (deal better with
           punctuation, for example, at least optionally).
        Returns list of words if no errors, None if error.
        '''
        
        # return reference
        word_list_OUT = []
        
        # got a string?
        if ( ( string_IN is not None ) and ( string_IN != "" ) ):
        
            # split the string.
            word_list_OUT = string_IN.split()
        
        else:
        
            # no string.  Return None.
            word_list_OUT = None
            
        #-- END check to see if string. --#
        
        return word_list_OUT
        
    #-- END class method convert_string_to_word_list() --#
    

    @classmethod
    def process_paragraph_contents( cls, paragraph_element_list_IN, bs_helper_IN = None, *args, **kwargs ):
  
        '''
        Accepts a list of the contents of a paragraph.  Loops over them and
           pulls them all together into one string.  Returns the string.
           
        Params:
        - paragraph_element_list_IN - list of BeautifulSoup4 elements that from an article paragraph.
        '''
        
        # return reference
        string_OUT = ""
        
        # declare variables
        paragraph_text_list = []
        current_paragraph_text = ""
        my_bs_helper = ""
        
        # initialize BeautifulSoup helper
        if ( bs_helper_IN != None ):
        
            # BSHelper passed in.
            my_bs_helper = bs_helper_IN
        
        else:

            # no helper passed in.  Create one.
            my_bs_helper = BeautifulSoupHelper()
            
        #-- END BeautifulSoupHelper init. --#

        # got anything in list?
        if ( len( paragraph_element_list_IN ) > 0 ):

            # yes - process elements of paragraph, add to paragraph list.
            paragraph_text_list = []
            for paragraph_element in paragraph_element_list_IN:
            
                # convert current element to just text.  Is it NavigableString?
                if ( isinstance( paragraph_element, NavigableString ) ):
                
                    # it is NavigableString - convert it to string.
                    current_paragraph_text = unicode( paragraph_element )
                
                else:
                
                    # not text - just grab all the text out of it.
                    #current_paragraph_text = ' '.join( paragraph_element.findAll( text = True ) )
                    #current_paragraph_text = paragraph_element.get_text( " ", strip = True )
                    current_paragraph_text = HTMLHelper.remove_html( str( paragraph_element ) )                        

                #-- END check to see if current element is text. --#
    
                # clean up - convert HTML entities
                current_paragraph_text = my_bs_helper.convert_html_entities( current_paragraph_text )
                
                # strip out extra white space
                current_paragraph_text = StringHelper.replace_white_space( current_paragraph_text )
                
                # got any paragraph text?
                current_paragraph_text = current_paragraph_text.strip()
                if ( ( current_paragraph_text != None ) and ( current_paragraph_text != "" ) ):
                
                    # yes.  Add to paragraph text.
                    paragraph_text_list.append( current_paragraph_text )
                    
                #-- END check to see if any text. --#
            
            #-- END loop over paragraph elements. --#
            
            # convert paragraph list to string
            paragraph_text = ' '.join( paragraph_text_list )
            
            # return paragraph text
            string_OUT = paragraph_text
                
        #-- END check to see if anything in list. --#
        
        return string_OUT
        
    #-- END method process_paragraph_contents() --#


    #----------------------------------------------------------------------------
    # instance methods
    #----------------------------------------------------------------------------


    def __str__( self ):

        # return reference
        string_OUT = ""
        
        # set content description
        self.content_description = "text"
        
        # call string method.
        string_OUT = super( Article_Text, self ).to_string()
                
        return string_OUT

    #-- END method __str__() --#

    
    def find_in_canonical_text( self, string_IN, do_multi_graph_check_IN = True ):
        
        '''
        Accepts a string that we want to locate in the nested article text.
        If found, returns a list of the indices of positions in the string where
           the string was found (could be more than one).  If not found, returns
           empty list.  If error, returns None.
        '''
        
        # return reference.
        list_OUT = []

        # declare variables
        me = "find_in_canonical_text"
        index_OUT = -1
        my_text = ""
        match_count = -1
        loop_count = -1
        keep_looping = False
        plain_text_index_list = []
        plain_text_count = -1
        remaining_word_list = []
        current_word_list = []
        match_count = -1
        matching_index_list = []
        current_index = -1
        
        # declare variables - multi-graf check - start removing wrods from
        #    beginning to test for case where start of string is end of
        #    paragraph.
        original_word_list = None
        reduced_word_list = None
        removed_word_list = None
        reduced_word_count = -1
        reduced_string = ""
        multi_graph_match_list = []
        multi_graph_match_count = -1
        continue_reducing = True
        reduced_match_index = -1
        first_word = ""
        first_word_index = -1
        removed_word = ""
        removed_word_index = -1
        removed_word_count = -1
        removed_word_match_counter = -1
        
        # got a string?
        if ( ( string_IN is not None ) and ( string_IN != "" ) ):
        
            # get text
            my_text = self.get_content()
            
            # first step is to try to find the string, as-is.
            list_OUT = StringHelper.find_substring_match_list( my_text, string_IN )
            
            # sanity check in case string spans multiple paragraphs.
            
            # sanity check.  Got anything?
            match_count = len( list_OUT )
            if ( match_count < 1 ):
            
                # no.  See if the string is in the plain text.
                plain_text_index_list = self.find_in_plain_text( string_IN )
                plain_text_count = len( plain_text_index_list )
                if ( plain_text_count > 0 ):
                
                    output_debug( "In " + me + ": WARNING - string being searched for is in text, likely spans paragraphs." )
                
                    # it is in the text.  So, start to build up string word by
                    #    word, looking for indexes where it matches the string.
                    #    Keep looping until number that match are 0 or 1.
                    
                    # split string into words.
                    remaining_word_list = self.convert_string_to_word_list( string_IN )
                    current_word_list = []
                    
                    # loop until 0 or 1 matches.
                    keep_looping = True
                    loop_count = 0
                    while keep_looping == True:
                    
                        # increment loop count
                        loop_count = loop_count + 1
                    
                        # empty matching_index_list
                        matching_index_list = []
                        
                        # add word to current list.
                        current_word_list.append( remaining_word_list[ 0 ] )
                        
                        # strip off the first item from remaining_word_list
                        del( remaining_word_list[ 0 ] )
                    
                        # make string from current_word_list.
                        current_string = " ".join( current_word_list )
                
                        output_debug( "--> In " + me + ": loop #" + str( loop_count ) + " - looking for: " + current_string )
                
                        # loop over the paragraph list.
                        for current_index in StringHelper.find_substring_iter( my_text, current_string ):
                        
                            # add match index to list.
                            matching_index_list.append( current_index )
                        
                        #-- END loop over paragraph list. --#
                        
                        # get count of matches.
                        match_count = len( matching_index_list )
                    
                        # short circuit in case of looking for something that is
                        #    duplicated exactly in two places in the text.
                        remaining_word_count = len( remaining_word_list )
                        if ( remaining_word_count == 0 ):
                        
                            # At this point, there are no more words to add, so
                            #    the current state is final.  Fall out of loop.
                            keep_looping = False 
                        
                        else:
                        
                            # more words to add... Do we have a match?
                            if ( match_count > 1 ):
                            
                                # still multiple matches - keep looking.
                                keep_looping = True
    
                            else:
                            
                                # only 1 or 0 matches.  At this point we fall
                                #    out and see what happened.
                                keep_looping = False

                            #-- END check to see if match yet or not --#
                            
                        #-- END check to see if no more words left. --#

                    #-- END loop to find starting paragraph. --#

                    # !find_in_canonical_text() - spans paragraphs?
                    # check if spans paragraphs.  In case of first word
                    #    in one paragraph, rest of string in another, start
                    #    removing words from the front and recursive-ish-ly
                    #    calling this method, to see if we can at least get
                    #    an idea of where it is.
                    if ( ( match_count == 0 ) and ( do_multi_graph_check_IN == True ) ):
                    
                        # convert original string to word list.
                        original_word_list = self.convert_string_to_word_list( string_IN )
                        
                        # start reduced_word_list at original_word_list.
                        reduced_word_list = list( original_word_list )
                        
                        # start removed_word_list as an empty list.
                        removed_word_list = []

                        # initialize loop variables.
                        multi_graph_match_list = []
                        multi_graph_match_count = -1
                        continue_reducing = True

                        # loop, removing one word from beginning of reduced list
                        #    each time, then calling this method, with the flag
                        #    to do_multi_graph_check_IN set to False.
                        while continue_reducing == True:
                        
                            # take first word in reduced_word_list, add it to
                            #    removed_word_list, then remove it from
                            #    reduced_word_list.
                            removed_word_list.append( reduced_word_list[ 0 ] )
                            del( reduced_word_list[ 0 ] )
                            
                            # first, check if we are out of words.
                            reduced_word_count = len( reduced_word_list )
                            if ( reduced_word_count > 0 ):

                                # call this method with reduced string
                                reduced_string = " ".join( reduced_word_list )
                                multi_graph_match_list = self.find_in_canonical_text( reduced_string, False )
                                
                                # what we got?
                                if ( multi_graph_match_list is not None ):
                                
                                    # got a list back.  Matches?
                                    multi_graph_match_count = len( multi_graph_match_list )
                                    if ( multi_graph_match_count == 0 ):
                                    
                                        # no match.  Keep looping.
                                        continue_reducing = True
                                        
                                    elif ( multi_graph_match_count >= 1 ):
                                    
                                        # one or more matches.  Once you get 
                                        #    matches, stop.  string is only
                                        #    getting shorter.  Will have to deal
                                        #    with multiples outside of loop.
                                        continue_reducing = False

                                    else:
                                    
                                        # error - should never get here.  Stop
                                        #    looping.
                                        continue_reducing = False
                                        output_debug( "In " + me + ": ERROR - error in child call to " + me + "() - length of list returned is not >= 0.  Falling out." )

                                    #-- END check to see how many matches. --#
                                
                                else:
                                
                                    # error in child call.  Stop looping.
                                    continue_reducing = False
                                    output_debug( "In " + me + ": ERROR - error in child call to " + me + "() - None returned rather than a list.  Falling out." )
                                
                                #-- END check to see if list is None --#
                                
                            else:
                            
                                # reduced word count is 0. End of line.
                                continue_reducing = False
                                
                            #-- END check to see if any words left in reduced word list. --#
                            
                        #-- END loop to reduce and search for string. --#
                        
                        # OK.  See if we have a match list.
                        if ( multi_graph_match_list is not None ):
                        
                            # got more than 0?
                            multi_graph_match_count = len( multi_graph_match_list )
                            if ( multi_graph_match_count > 0 ):
                            
                                # got something.  for each match, then, need to
                                #    loop over the removed words and look for
                                #    each in the overall string, from the right,
                                #    starting with the match index, until one of
                                #    the matches is not between the first word
                                #    and the match index (fail) or you run out
                                #    of words (match).
                                for reduced_match_index in multi_graph_match_list:
                                    
                                    # look for first word.
                                    first_word = original_word_list[ 0 ]
                                    first_word_index = my_text.rfind( first_word, 0, reduced_match_index )
                                    most_recent_index = first_word_index - 1
                                    
                                    # first word found?
                                    if ( first_word_index >= 0 ):
                                    
                                        # loop over the removed words.
                                        removed_word_count = len( removed_word_list )
                                        removed_word_match_counter = 0
                                        for removed_word in removed_word_list:
    
                                            # get index for removed word.
                                            removed_word_index = my_text.rfind( removed_word, 0, reduced_match_index )
                                            
                                            # make sure it is greater than
                                            #    most_recent_index.
                                            if ( removed_word_index > most_recent_index ):
                                            
                                                # removed word is in correct
                                                #    range - increment counter.
                                                removed_word_match_counter += 1
                                                output_debug( "In " + me + ": in sanity check - for reduced match index = " + str( reduced_match_index ) + ", word ( \"" + removed_word + "\" ) is at index " + str( removed_word_index ) + " which is between previous index ( " + str( most_recent_index ) + " ) and start of reduced match ( " + str( reduced_match_index ) + " ).  OK so far..." )

                                            else:
                                            
                                                # not in range.  Don't increment
                                                #    counter, no match.
                                                output_debug( "In " + me + ": in sanity check - for reduced match index = " + str( reduced_match_index ) + ", word ( \"" + removed_word + "\" ) is at index " + str( removed_word_index ) + " which is not between previous index ( " + str( most_recent_index ) + " ) and start of reduced match ( " + str( reduced_match_index ) + " ).  No match." )
                                                
                                            #-- END check to see if removed word is in right place. --#
                                            
                                            # set most_recent_index to
                                            #    removed_word_index
                                            most_recent_index = removed_word_index
                                        
                                        #-- END loop over removed words. --#
                                        
                                        # is removed_word_match_counter equal to
                                        #    removed_word_count?
                                        if ( removed_word_match_counter == removed_word_count ):
                                        
                                            # yes.  This is a match.
                                            matching_index_list.append( first_word_index )
                                        
                                        #-- END check to see if removed words indicate match --#
                                        
                                    #-- END check to see if first word found. --#
                                    
                                #-- END loop over multi-graph match list --#

                            else:
                            
                                # nothing in list.  Leave match_count and
                                #    matching_index_list as-is.
                                pass
                                
                            #-- END check to see if matches. --#
                        
                        #-- END check to see if multi-graph match list --#
                        
                    #-- END check to see if no matches at this point. --#
                    
                    # so, got one match, or none.
                    match_count = len( matching_index_list )
                    if ( match_count >= 1 ):
                    
                        # found one or more indexes - add each to output list.
                        for current_index in matching_index_list:

                            list_OUT.append( current_index )
                            
                        #-- END loop over index matches. --#
                        
                    elif ( match_count == 0 ):
                    
                        # no match - return empty list.
                        list_OUT = []
                        
                    else:
                    
                        # not 0 or >= 1 - error.
                        output_debug( "In " + me + ": found " + str( next_count ) + " matches for string.  Returning None." )
                        list_OUT = None
                        
                    #-- END check to see if we found match. --#
                
                #-- END check to see if string is in the text --#
            
            #-- END sanity check to see if got anything --#
        
        else:
        
            # no string.  Return None.
            list_OUT = None
            
        #-- END check to see if string. --#
        
        return list_OUT
        
    #-- END method find_in_canonical_text() --#
        
        
    def find_in_paragraph_list( self, string_IN, do_multi_graph_check_IN = True  ):
        
        '''
        Accepts a string we want to locate in one of the paragraphs inside this
           article text.
        If found, returns a list of the numbers of paragraphs that contains the
           string passed in, where paragraphs are numbered starting with 1.  If
           not found, returns empty list.  If error, returns None.
        '''
        
        # return reference.
        list_OUT = []
        
        # declare variables
        me = "find_in_paragraph_list"
        index_OUT = -1
        my_paragraph_list = []
        paragraph_counter = -1
        current_paragraph = ""
        match_count = -1
        plain_text_index_list = []
        plain_text_count = -1
        current_paragraph_list = []
        next_paragraph_list = []
        next_count = -1
        loop_count = -1
        keep_looping = False
        remaining_word_list = []
        current_word_list = []
        current_string = ""
        remaining_word_count = -1
        matching_paragraph_list = []
        match_count = -1
        current_paragraph_text = ""
        
        # declare variables - multi-graf check - start removing wrods from
        #    beginning to test for case where start of string is end of
        #    paragraph.
        original_word_list = None
        reduced_word_list = None
        removed_word_list = None
        multi_graph_match_list = []
        multi_graph_match_count = -1
        continue_reducing = True
        reduced_word_count = -1
        reduced_string = ""
        removed_string = ""
        removed_string_match_list = []
        preceding_paragraph_number = -1
        preceding_paragraph_index = -1
        preceding_paragraph_text = ""
        
        # got a string?
        if ( ( string_IN is not None ) and ( string_IN != "" ) ):
        
            # get paragraph list
            my_paragraph_list = self.get_paragraph_list()
            
            # loop over paragraphs
            paragraph_counter = 0
            for current_paragraph in my_paragraph_list:

                # increment counter
                paragraph_counter = paragraph_counter + 1

                # first step is to try to find the string, as-is.
                if string_IN in current_paragraph:
                
                    # found it.  this is the paragraph.
                    list_OUT.append( paragraph_counter )
                    
                #-- END check to see if found in current paragraph. --#
                
            #-- END loop over paragraphs --#
            
            # sanity check in case string spans multiple paragraphs.

            # Got anything?
            match_count = len( list_OUT )
            if ( match_count < 1 ):
            
                # no.  See if the string is in the plain text.
                plain_text_index_list = self.find_in_plain_text( string_IN )
                plain_text_count = len( plain_text_index_list )
                if ( plain_text_count > 0 ):
                
                    output_debug( "In " + me + ": WARNING - string being searched for is in text, likely spans paragraphs." )
                
                    # split string into words.
                    remaining_word_list = self.convert_string_to_word_list( string_IN )
                    current_word_list = []
                    
                    # it is in the text.  So, start to build up string word by
                    #    word, looking for paragraphs that match as we go.  Keep
                    #    looping until number that match are 0 or 1.
                    current_paragraph_list = my_paragraph_list
                    next_count = len( current_paragraph_list )
                    keep_looping = True
                    loop_count = 0
                    while keep_looping == True:
                    
                        # increment loop count
                        loop_count = loop_count + 1
                        
                        # empty next_paragraph_list
                        next_paragraph_list = []
                                                
                        # add word to current list.
                        current_word_list.append( remaining_word_list[ 0 ] )
                        
                        # strip off the first item from remaining_word_list
                        del( remaining_word_list[ 0 ] )
                    
                        # make string from current_word_list.
                        current_string = " ".join( current_word_list )
                        
                        output_debug( "--> In " + me + ": loop #" + str( loop_count ) + " - looking for: " + current_string )
                
                        # loop over the paragraph list.
                        for current_paragraph in current_paragraph_list:
                        
                            # is string in paragraph?
                            if current_string in current_paragraph:
                            
                                # yes - add paragraph to next list.
                                next_paragraph_list.append( current_paragraph )
                                
                            #-- END check to see if string is in paragraph --#
                        
                        #-- END loop over paragraph list. --#
                        
                        # switch next_paragraph_list to my_paragraph_list.
                        current_paragraph_list = next_paragraph_list
                        next_count = len( current_paragraph_list )
                        
                        # Keep looping?
                        
                        # short circuit in case of looking for something that is
                        #    duplicated exactly in two places in the text.
                        remaining_word_count = len( remaining_word_list )
                        if ( remaining_word_count == 0 ):
                        
                            # At this point, there are no more words to add, so
                            #    the current state is final.  Fall out of loop.
                            keep_looping = False 
                        
                        else:
                        
                            # more words to add... Do we have a match?
                            if ( next_count > 1 ):
                            
                                # still multiple matches - keep looking.
                                keep_looping = True
    
                            else:
                            
                                # only 1 or 0 matches.  At this point we fall
                                #    out and see what happened.
                                keep_looping = False

                            #-- END check to see if match yet or not --#
                            
                        #-- END check to see if no more words left. --#
                    
                    #-- END loop to find starting paragraph. --#

                    # put list of remaining paragraphs in
                    #    matching_paragraph_list and get count of matches.
                    matching_paragraph_list = list( current_paragraph_list )
                    match_count = len( matching_paragraph_list )

                    # !find_in_paragraph_list() - spans paragraphs?
                    # check if spans paragraphs.  In case of first word
                    #    in one paragraph, rest of string in another, start
                    #    removing words from the front and recursive-ish-ly
                    #    calling this method, to see if we can at least get
                    #    an idea of where it is.
                    if ( ( match_count == 0 ) and ( do_multi_graph_check_IN == True ) ):
                    
                        # convert original string to word list.
                        original_word_list = self.convert_string_to_word_list( string_IN )
                        
                        # start reduced_word_list at original_word_list.
                        reduced_word_list = list( original_word_list )
                        
                        # start removed_word_list as an empty list.
                        removed_word_list = []

                        # initialize loop variables.
                        multi_graph_match_list = []
                        multi_graph_match_count = -1
                        continue_reducing = True

                        # loop, removing one word from beginning of reduced list
                        #    each time, then calling this method, with the flag
                        #    to do_multi_graph_check_IN set to False.
                        while continue_reducing == True:
                        
                            # take first word in reduced_word_list, add it to
                            #    removed_word_list, then remove it from
                            #    reduced_word_list.
                            removed_word_list.append( reduced_word_list[ 0 ] )
                            del( reduced_word_list[ 0 ] )
                            
                            # first, check if we are out of words.
                            reduced_word_count = len( reduced_word_list )
                            if ( reduced_word_count > 0 ):

                                # call this method with reduced string
                                reduced_string = " ".join( reduced_word_list )
                                multi_graph_match_list = self.find_in_paragraph_list( reduced_string, False )
                                
                                # what we got?
                                if ( multi_graph_match_list is not None ):
                                
                                    # got a list back.  Matches?
                                    multi_graph_match_count = len( multi_graph_match_list )
                                    if ( multi_graph_match_count == 0 ):
                                    
                                        # no match.  Keep looping.
                                        continue_reducing = True
                                        
                                    elif ( multi_graph_match_count >= 1 ):
                                    
                                        # one or more matches.  Once you get 
                                        #    matches, stop.  string is only
                                        #    getting shorter.  Will have to deal
                                        #    with multiples outside of loop.
                                        continue_reducing = False

                                    else:
                                    
                                        # error - should never get here.  Stop
                                        #    looping.
                                        continue_reducing = False
                                        output_debug( "In " + me + ": ERROR - error in child call to " + me + "() - length of list returned is not >= 0.  Falling out." )

                                    #-- END check to see how many matches. --#
                                
                                else:
                                
                                    # error in child call.  Stop looping.
                                    continue_reducing = False
                                    output_debug( "In " + me + ": ERROR - error in child call to " + me + "() - None returned rather than a list.  Falling out." )
                                
                                #-- END check to see if list is None --#
                                
                            else:
                            
                                # reduced word count is 0. End of line.
                                continue_reducing = False
                                
                            #-- END check to see if any words left in reduced word list. --#
                            
                        #-- END loop to reduce and search for string. --#
                        
                        # OK.  See if we have a match list.
                        if ( multi_graph_match_list is not None ):
                        
                            # got more than 0?
                            multi_graph_match_count = len( multi_graph_match_list )
                            if ( multi_graph_match_count > 0 ):
                            
                                # got something.  for each match, then, need to
                                #    look for string of removed words in list of
                                #    paragraphs.  If removed word string is in
                                #    the paragraph before the current match (at
                                #    least in the list of matches, if not the
                                #    only one), then match!  If not, no match.
                                for reduced_match_index in multi_graph_match_list:
                                    
                                    # just look for the string made up of the
                                    #    removed words.
                                    removed_string = " ".join( removed_word_list )
                                    
                                    # call this method, telling it not to do any
                                    #    multi-paragraph checking.
                                    removed_string_match_list = self.find_in_paragraph_list( removed_string, False )
                                    
                                    # is reduced_match_index - 1 (paragraph
                                    #    before match) in list?
                                    preceding_paragraph_number = reduced_match_index - 1
                                    if ( preceding_paragraph_number in removed_string_match_list ):
                                    
                                        # got a match.  Get paragraph text for
                                        #    that preceding paragraph.
                                        
                                        # get index of preceding paragraph.
                                        preceding_paragraph_index = preceding_paragraph_number - 1

                                        # get text for that paragraph.
                                        preceding_paragraph_text = my_paragraph_list[ preceding_paragraph_index ]
                                        
                                        # add text to matching_paragraph_list
                                        matching_paragraph_list.append( preceding_paragraph_text )
                                        output_debug( "In " + me + ": in sanity check - for reduced match paragraph # = " + str( reduced_match_index ) + ", removed words ( \"" + removed_string + "\" ) are in graph(s): " + str( removed_string_match_list ) + ", which includes the previous graph ( " + str( preceding_paragraph_number ) + " ) - this is a match." )
                        
                                    else:
                                    
                                        # not a match.
                                        output_debug( "In " + me + ": in sanity check - for reduced match paragraph # = " + str( reduced_match_index ) + ", removed words ( \"" + removed_string + "\" ) are in graphs: " + str( removed_string_match_list ) + ", none of which is the previous graph ( " + str( preceding_paragraph_number ) + " ) - this is not a match." )
                                        
                                    #-- END check to see if match for removed text is in previous paragraph. --#
                                    
                                #-- END loop over multi-graph match list --#

                            else:
                            
                                # nothing in list.  Leave match_count and
                                #    matching_index_list as-is.
                                pass
                                
                            #-- END check to see if matches. --#
                        
                        #-- END check to see if multi-graph match list --#
                        
                    #-- END check to see if no matches at this point. --#
                    
                    # so, loop is done.  How many matches?
                    match_count = len( matching_paragraph_list )
                    if ( match_count >= 1 ):
                    
                        # found one or more paragraphs - look up index of each
                        #    in my_paragraph_list, add that plus 1 to the list.
                        for current_paragraph_text in matching_paragraph_list:

                            index_OUT = my_paragraph_list.index( current_paragraph_text )
                            index_OUT = index_OUT + 1
                        
                            # add to output list.
                            list_OUT.append( index_OUT )
                            
                        #-- END loop over paragraph list. --#
                        
                    elif ( match_count == 0 ):
                    
                        # no match - return empty list.
                        list_OUT = []
                        
                    else:
                    
                        # not 0 or >= 1 - what to do?
                        output_debug( "In " + me + ": found " + str( match_count ) + " matches for string.  Returning None." )
                        list_OUT = None
                        
                    #-- END check to see if we found paragraph. --#
                
                #-- END check to see if string is in the text --#
            
            #-- END sanity check to see if got anything --#
            
        else:
        
            # no string.  Return None.
            list_OUT = None
            
        #-- END check to see if string. --#
        
        return list_OUT
        
    #-- END method find_in_paragraph_list() --#
        
        
    def find_in_plain_text( self, string_IN ):
        
        '''
        Accepts a string that we want to locate in the nested article text with
           all HTML and markup removed ("plain text").
        If found, returns the index of the start of the string inside the
           plain text for this article.  If not found, returns -1.  If error,
           returns None.
        '''
        
        # return reference.
        list_OUT = []
        
        # declare variables.
        my_text = ""
        
        # got a string?
        if ( ( string_IN is not None ) and ( string_IN != "" ) ):
        
            # get text
            my_text = self.get_content_sans_html()
            
            # first step is to try to find the string, as-is.
            list_OUT = StringHelper.find_substring_match_list( my_text, string_IN )
            
        else:
        
            # no string.  Return None.
            list_OUT = None
            
        #-- END check to see if string. --#
        
        return list_OUT
        
    #-- END method find_in_plain_text() --#
        
        
    def find_in_text( self, string_IN, requested_items_IN = None ):
        
        '''
        Accepts a string that we want to locate in the nested article text.
           If not found, returns None.  If found, returns a dictionary with the
           following values:
           - FIT_CANONICAL_INDEX_LIST = "canonical_index_list" - list of
              index(ices) of start of the string passed in in the canonical text
              for this article.
           - FIT_TEXT_INDEX_LIST = "index_list" - index(ices) of the start of
              the string passed in in the plain text for this article.
           - FIT_FIRST_WORD_NUMBER_LIST = "first_word_number_list" - the
              number(s) of the word in this article, when converted to a word
              list, of the first word in the string passed in.  Number, not
              index (so index + 1).
           - FIT_LAST_WORD_NUMBER_LIST = "last_word_number_list" - the number(s)
              of the word in this article, when converted to a word list, of the
              last word in the string passed in.  Number, not index
              (so index + 1).
           - FIT_PARAGRAPH_NUMBER_LIST = "paragraph_number_list" - list of the
              number (s) of the paragraph in this article that contains the
              string (or, if it spans multiple paragraphs, the start of this
              string).
        '''
        
        # return reference
        dict_OUT = {}
        
        # declare variables
        me = "find_in_text"
        items_to_process = []
        temp_dictionary = {}
        current_value = None
        
        # do we have a string?
        if ( ( string_IN is not None ) and ( string_IN != "" ) ):
        
            # got any requested items?
            if ( ( requested_items_IN is not None ) and ( len( requested_items_IN ) > 0 ) ):
            
                # yes.  use this as list of items to process.
                items_to_process = requested_items_IN
                
            else:
            
                # no - process all items.
                items_to_process = []
                items_to_process.append( self.FIT_CANONICAL_INDEX_LIST )
                items_to_process.append( self.FIT_TEXT_INDEX_LIST )
                items_to_process.append( self.FIT_FIRST_WORD_NUMBER_LIST )
                items_to_process.append( self.FIT_LAST_WORD_NUMBER_LIST )
                items_to_process.append( self.FIT_PARAGRAPH_NUMBER_LIST )

            #-- END check to see which items we process. --#
            
            # go item by item.

            # FIT_CANONICAL_INDEX_LIST
            if ( self.FIT_CANONICAL_INDEX_LIST in items_to_process ):
            
                # find the index of the start of the string in the canonical
                #    text for this article (paragraphs preserved as <p> tags).
                current_value = self.find_in_canonical_text( string_IN )
                dict_OUT[ self.FIT_CANONICAL_INDEX_LIST ] = current_value
            
            #-- END FIT_CANONICAL_INDEX_LIST --#

            # FIT_TEXT_INDEX_LIST
            if ( self.FIT_TEXT_INDEX_LIST in items_to_process ):
            
                # find the index of the start of the string in the plain text
                #    for this article.
                current_value = self.find_in_plain_text( string_IN )
                dict_OUT[ self.FIT_TEXT_INDEX_LIST ] = current_value
            
            #-- END FIT_TEXT_INDEX_LIST --#
            
            # FIT_FIRST_WORD_NUMBER_LIST and/or FIT_LAST_WORD_NUMBER_LIST
            if ( ( self.FIT_FIRST_WORD_NUMBER_LIST in items_to_process ) or ( self.FIT_LAST_WORD_NUMBER_LIST in items_to_process ) ):
            
                # find the position in the list of words in this article for the
                #    first and last words in the string passed in (also can
                #    approximate word count from this, as well).
                temp_dictionary = self.find_in_word_list( string_IN )
                
                # will return a dictionary with first and last number.
                if ( self.FIT_FIRST_WORD_NUMBER_LIST in items_to_process ):
                
                    # get value and store it in output dictionary.
                    current_value = temp_dictionary[ self.FIT_FIRST_WORD_NUMBER_LIST ]
                    dict_OUT[ self.FIT_FIRST_WORD_NUMBER_LIST ] = current_value
                
                #-- END check to see if we return number of first word in word list. --#
            
                # will return a dictionary with first and last number.
                if ( self.FIT_LAST_WORD_NUMBER_LIST in items_to_process ):
                
                    # get value and store it in output dictionary.
                    current_value = temp_dictionary[ self.FIT_LAST_WORD_NUMBER_LIST ]
                    dict_OUT[ self.FIT_LAST_WORD_NUMBER_LIST ] = current_value
                
                #-- END check to see if we return number of first word in word list. --#
            
            #-- FIT_FIRST_WORD_NUMBER_LIST and/or FIT_LAST_WORD_NUMBER_LIST --#

            # FIT_PARAGRAPH_NUMBER_LIST
            if ( self.FIT_PARAGRAPH_NUMBER_LIST in items_to_process ):
            
                # find the number of the paragraph in this article that contains
                #    the string passed in.  If through some error or insanity
                #    the string starts in one paragraph and ends in another,
                #    will find the paragraph in which it starts.
                current_value = self.find_in_paragraph_list( string_IN )
                dict_OUT[ self.FIT_PARAGRAPH_NUMBER_LIST ] = current_value
            
            #-- END FIT_PARAGRAPH_NUMBER_LIST --#
        
        else:
        
            # no string passed in, return None.
            dict_OUT = None
            
        #-- END check to see if string passed in. --#
        
        return dict_OUT
        
    #-- END method find_in_text() --#
            
                
    def find_in_word_list( self, string_IN ):
        
        '''
        Accepts a string we want to locate in the word list based on this
           article text.
        Returns a dictionary that contains two name-value pairs:
           - FIT_FIRST_WORD_NUMBER_LIST = "first_word_number_list" - the
              number(s) of the word in this article, when converted to a word
              list, of the first word in the string passed in.  Number, not
              index (so index + 1).
           - FIT_LAST_WORD_NUMBER_LIST = "last_word_number_list" - the number(s)
              of the word in this article, when converted to a word list, of the
              last word in the string passed in.  Number, not index
              (so index + 1).
        If not found, each will contain a value of -1.  If error, returns None.
        '''
        
        # return reference.
        dict_OUT = {}
        first_word_list_OUT = []
        last_word_list_OUT = []
        first_word_OUT = -1
        last_word_OUT = -1
        my_word_list = []
        string_word_list = []
        match_list = []
        match_index = -1
        string_word_count = -1
        
        # got a string?
        if ( ( string_IN is not None ) and ( string_IN != "" ) ):
        
            # get paragraph list
            my_word_list = self.get_word_list()
            
            # convert string into a word list.
            string_word_list = self.convert_string_to_word_list( string_IN )
            
            # try the KnuthMorrisPratt algorithm from Python Cookbook 2nd Ed.
            for match_index in SequenceHelper.KnuthMorrisPratt( my_word_list, string_word_list ):
            
                # append match to list.
                match_list.append( match_index )
                
            #-- END loop over matches. --#
            
            # got anything?
            if ( len( match_list ) > 0 ):
            
                # yes - loop over matches.
                for match_index in match_list:
                
                    # add 1 - want word number, not word index.
                    first_word_OUT = match_index + 1
                    
                    # get word count
                    string_word_count = len( string_word_list )
                    
                    # for last word, set it to match_index + word count
                    last_word_OUT = match_index + string_word_count
                    
                    # add to lists.
                    first_word_list_OUT.append( first_word_OUT )
                    last_word_list_OUT.append( last_word_OUT )
                    
                #-- END loop over matches. --#
                
            else:
            
                # no match - return empty lists.
                first_word_list_OUT = []
                last_word_list_OUT = []
                
            #-- END check to see if match. --#
            
            # build return dictionary.
            dict_OUT = {}
            dict_OUT[ self.FIT_FIRST_WORD_NUMBER_LIST ] = first_word_list_OUT
            dict_OUT[ self.FIT_LAST_WORD_NUMBER_LIST ] = last_word_list_OUT
                        
        else:
        
            # no string.  Return None.
            dict_OUT = None
            
        #-- END check to see if string. --#
        
        return dict_OUT
        
    #-- END method find_in_word_list() --#
        
        
    def get_content_sans_html( self, *args, **kwargs ):
        
        '''
        Returns content nested in this instance but with ALL HTML removed.
        Preconditions: None
        Postconditions: None
        
        Returns the content exactly as it is stored in the instance.
        '''
        
        # return reference
        content_OUT = None

        # declare variables
        me = "get_content_sans_html"

        # get the content.
        content_OUT = self.content
        
        # strip all HTML
        content_OUT = HTMLHelper.remove_html( content_OUT )
                
        return content_OUT

    #-- END method get_content_sans_html() --#


    def get_paragraph_list( self, *args, **kwargs ):
        
        '''
        Looks in nested content for paragraph tags.  Returns a list of the text
           in paragraph tags, in the same order as they appeared in the content,
           with no nested HTML.  If no <p> tags, returns a list with a single item - all of the text.
        Preconditions: None
        Postconditions: None
        
        Returns a list of the paragraphs in the content.
        '''
        
        # return reference
        list_OUT = []

        # declare variables
        me = "get_paragraph_list"
        my_content = ""
        content_bs = None
        p_tag_list = []
        p_tag_count = -1
        current_p_tag = None
        current_p_tag_id = ""
        current_p_tag_contents = ""

        # get the content.
        my_content = self.content
        
        # create a BeautifulSoup instance that contains it.
        content_bs = BeautifulSoup( my_content )
        
        # get all the <p> tags.
        p_tag_list = content_bs.find_all( 'p' )
        
        # how many?
        p_tag_count = len( p_tag_list )
        
        # got any at all?
        if ( p_tag_count > 0 ):

            # yes - prepopulate list, so we can assign positions based on "id"
            #    attribute values.
            list_OUT = [ None ] * p_tag_count
            
            # loop!
            for current_p_tag in p_tag_list:
            
                # get id attribute value and contents.
                current_p_tag_id = int( current_p_tag[ "id" ] )
                current_p_tag_contents = self.make_paragraph_string( current_p_tag.contents )
        
                # add contents to output list at position of "id".
                list_OUT[ current_p_tag_id - 1 ] = current_p_tag_contents
                
            #-- END loop over p-tags. --#
            
        else:
        
            # none at all.  Just return content in first item of list.
            list_OUT.append( my_content )
        
        #-- END check to see if any p-tags
        
        return list_OUT

    #-- END method get_paragraph_list() --#


    def get_word_list( self, *args, **kwargs ):
        
        '''
        Creates list of words contained in nested content.  Returns a list of
           the words in the Article_Text, with each word added as an item in the
           list, in the same order as they appeared in the content, with no
           nested HTML.
        Preconditions: None
        Postconditions: None
        
        Returns a list of the words in the content.
        '''
        
        # return reference
        list_OUT = []

        # declare variables
        me = "get_paragraph_list"
        my_content = ""
        cleaned_content = ""
        word_list = []
        word_count = -1
        word_counter = -1
        current_word = ""

        # get the content.
        my_content = self.content
        
        # get the content with no HTML.
        cleaned_content = HTMLHelper.remove_html( my_content )
        
        # and clean up white space.
        cleaned_content = StringHelper.replace_white_space( cleaned_content )
        
        # split the string on white space.
        word_list = self.convert_string_to_word_list( cleaned_content )
        
        # how many we got?
        word_count = len( word_list )
        
        # check to see that we have some words.
        if ( word_count > 0 ):

            # yes - prepopulate list, so we can assign positions based on "id"
            #    attribute values.
            list_OUT = [ None ] * word_count
            
            # loop!
            word_counter = 0
            for current_word in word_list:
            
                # add word to list
                list_OUT[ word_counter ] = current_word
                
                # increment word counter
                word_counter = word_counter + 1
                
            #-- END loop over words. --#
            
        else:
        
            # none at all.  Just return content in first item of list.
            list_OUT.append( my_content )
        
        #-- END check to see if any words
        
        return list_OUT

    #-- END method get_word_list() --#


    def make_paragraph_string( self, paragraph_element_list_IN, *args, **kwargs ):
  
        '''
        Accepts a list of the contents of a paragraph.  Loops over them and
           pulls them all together into one string.  Returns the string.
           
        Params:
        - paragraph_element_list_IN - list of BeautifulSoup4 elements that from an article paragraph.
        '''
        
        # return reference
        string_OUT = ""
        
        # declare variables
        my_bs_helper = ""
        
        # initialize BeautifulSoup helper
        my_bs_helper = self.get_bs_helper()

        # call class method
        string_OUT = self.process_paragraph_contents( paragraph_element_list_IN, my_bs_helper )
        
        return string_OUT
        
    #-- END method make_paragraph_string() --#


    def save(self, *args, **kwargs):
        
        '''
        Overriding save() method so that we always clean self.content before
           storing it in database.
        '''
        
        # declare variables
        my_content = ""
        
        # get content
        my_content = self.get_content()
        
        # clean that content
        self.set_text( my_content, True )
        
        # call parent save() method
        super( Article_Text, self).save( *args, **kwargs )

    #-- END overriden save() method --#


    def set_text( self, text_IN = "", clean_text_IN = True, *args, **kwargs ):
        
        '''
        Accepts a piece of text.  If asked, we clean the text, then we store
           it in this instance's content variable.
        Preconditions: None
        Postconditions: None
        
        Returns the text as it is stored in the instance.
        '''
        
        # return reference
        text_OUT = None

        # declare variables
        me = "set_content"
        text_value = ""

        # clean text?
        if ( clean_text_IN == True ):
        
            # yes.
            text_value = self.clean_body_text( text_IN )
                            
        else:
        
            # no just use what was passed in.
            text_value = text_IN
        
        #-- END check to see if we clean... --#

        # set the text in the instance and return the content.
        text_OUT = self.set_content( text_value )
                
        return text_OUT

    #-- END method set_text() --#
    

#-- END Article_Text model --#


# Article_Data model
@python_2_unicode_compatible
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
    
    STATUS_NEW = "new"
    STATUS_COMPLETE = "complete"
    STATUS_SERVICE_ERROR = "service_error"
    STATUS_UNKNOWN_ERROR = "unknown_error"
    STATUS_DEFAULT = STATUS_NEW

    article = models.ForeignKey( Article )
    coder = models.ForeignKey( User )
    coder_type = models.CharField( max_length = 255, blank = True, null = True )
    topics = models.ManyToManyField( Topic, blank = True, null = True )
    locations = models.ManyToManyField( Location, blank = True )
    article_type = models.CharField( max_length = 255, choices = ARTICLE_TYPE_CHOICES, blank = True, default = 'news' )
    is_sourced = models.BooleanField( default = True )
    can_code = models.BooleanField( default = True )
    status = models.CharField( max_length = 255, blank = True, null = True, default = STATUS_DEFAULT )
    status_messages = models.TextField( blank = True, null = True )
    create_date = models.DateTimeField( auto_now_add = True )
    last_modified = models.DateTimeField( auto_now = True )

    # Was saving topics and location per article, not referencing shared topic
    #    or location tables.  No longer (see topics and locations above).
    #topics = models.ManyToManyField( Article_Topic, blank = True, null = True )
    #locations = models.ManyToManyField( Article_Location, blank = True, null = True )

    # Changed to having a separate join table, not ManyToMany auto-generated one.
    #authors = models.ManyToManyField( Article_Author )
    #sources = models.ManyToManyField( Article_Source )
    
    # field to store how source was captured.
    capture_method = models.CharField( max_length = 255, blank = True, null = True )
    
    # related projects:
    projects = models.ManyToManyField( Project )

    # Meta-data for this class.
    class Meta:
        ordering = [ 'article', 'last_modified', 'create_date' ]

    #----------------------------------------------------------------------------
    # instance methods
    #----------------------------------------------------------------------------

    def __str__( self ):

        string_OUT = str( self.id ) + " - " + str( self.article )
        
        return string_OUT

    #-- END method __str__() --#


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
    
    
    def set_status( self, status_IN, status_message_IN = None ):
        
        '''
        Accepts status value and status message.  Stores status in "status"
           field.  Appends status_message to "status_messages" field, preceded
           by a newline if field is not empty.  Returns status.
        '''
        
        # return reference
        status_OUT = ""
        
        # got a status?
        if ( status_IN is not None ):
        
            # yes.  store it.
            self.status = status_IN
            
        #-- END check to see if status. --#

        # got message?
        if ( ( status_message_IN is not None ) and ( status_message_IN != "" ) ):
            
            # yes.  Anything currently in message?
            if ( ( self.status_messages is not None ) and ( self.status_messages != "" ) ):
            
                self.status_messages += "\n" + status_message_IN
                
            else:
            
                self.status_messages = status_message_IN
                    
            #-- END check to see if we need a newline. --#
                    
        #-- END check to see if message. --#
        
        status_OUT = self.status
        
        return status_OUT
        
    #-- END method set_status() --#
    

#= End Article_Data Model =======================================================


# Article_Content model
@python_2_unicode_compatible
class Article_Data_Notes( Abstract_Related_Content ):

    #----------------------------------------------------------------------
    # model fields and meta
    #----------------------------------------------------------------------

    # allow more than one related piece of "Article_Content" per article.
    article_data = models.ForeignKey( Article_Data )

    # meta class with ordering.
    class Meta:

        ordering = [ 'article_data', 'last_modified', 'create_date' ]

    #-- END nested Meta class --#

    #----------------------------------------------------------------------------
    # instance methods
    #----------------------------------------------------------------------------


    def to_string( self ):

        # return reference
        string_OUT = ""
        
        if ( self.id ):
            
            string_OUT += str( self.id ) + " - "
            
        #-- END check to see if ID --#
             
        if ( self.content_description ):
        
            string_OUT += self.content_description
            
        #-- END check to see if content_description --#
        
        if ( self.content_type ):
            
            string_OUT += " of type \"" + self.content_type + "\""
            
        #-- END check to see if there is a type --#
             
        string_OUT += " for article_data: " + str( self.article_data )
        
        return string_OUT

    #-- END method to_string() --#


    def __str__( self ):

        # return reference
        string_OUT = ""
        
        string_OUT = self.to_string()
        
        return string_OUT

    #-- END method __str__() --#


#-- END abstract Article_Data_Notes model --#


# Article_Person model
@python_2_unicode_compatible
class Article_Person( models.Model ):


    #----------------------------------------------------------------------
    # constants-ish
    #----------------------------------------------------------------------    

    #RELATION_TYPE_CHOICES = (
    #    ( "author", "Article Author" ),
    #    ( "source", "Article Source" )
    #)

    #----------------------------------------------------------------------------
    # model fields and meta
    #----------------------------------------------------------------------------

    article_data = models.ForeignKey( Article_Data )
    person = models.ForeignKey( Person, blank = True, null = True )
    #relation_type = models.CharField( max_length = 255, choices = RELATION_TYPE_CHOICES )

    # capture match confidence - start with 1 or 0, but leave room for
    #    decimal values.
    match_confidence_level = models.DecimalField( max_digits = 11, decimal_places = 10, blank = True, null = True, default = 0.0 )

    # field to store how person was captured.
    capture_method = models.CharField( max_length = 255, blank = True, null = True )
    
    # time stamps.
    create_date = models.DateTimeField( auto_now_add = True )
    last_modified = models.DateTimeField( auto_now = True )

    # meta class so we know this is an abstract class.
    class Meta:

        abstract = True

    #----------------------------------------------------------------------------
    # NOT Instance variables
    # Class variables - overriden by __init__() per instance if same names, but
    #    if not set there, shared!
    #----------------------------------------------------------------------------


    # variable to hold list of multiple potentially matching persons, if more
    #    than one found when lookup is attempted by Article_Coder.
    #person_match_list = []


    #----------------------------------------------------------------------------
    # instance methods
    #----------------------------------------------------------------------------

    
    def __init__( self, *args, **kwargs ):
        
        # call parent __init()__ first.
        super( Article_Person, self ).__init__( *args, **kwargs )

        # then, initialize variable.
        self.person_match_list = []
        
    #-- END method __init__() --#


    def __str__( self ):
        
        # return reference
        string_OUT = ""
        
        if ( self.id ):
        
            string_OUT += str( self.id ) + " - "
            
        #-- END check to see if id --#
        
        if ( self.person is not None ):
        
            string_OUT += self.person.last_name + ", " + self.person.first_name
        
        else:
        
            string_OUT += 'empty Article_Person instance'
        
        #-- END check to see if person. --#
        
        return string_OUT
    
    #-- END method __str__() --#


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


    @abstractmethod
    def process_alternate_matches( self ):
        
        '''
        If there are matches in the variable person_match_list, loops over them
           and deals with each appropriately.  person_match_list is a list of 
           Person instances of people who might be a match for a given name
           string.  This method is abstract, so the child classes can each
           define how they deal with multiple matches.
        '''
        
        print( "++++++++ In Article_Person process_alternate_matches() ++++++++" )
        
        pass
        
    #-- END function process_alternate_matches() --#
    

    def save( self, *args, **kwargs ):
        
        '''
        Overridden save() method that calls process_alternate_matches() after
           django's save() method.

        Note: looks like child classes don't have to override save method.
        '''

        #print( "++++++++ In Article_Person save() ++++++++" )
        
        # declare variables.
        
        # call parent save() method.
        super( Article_Person, self ).save( *args, **kwargs )

        # call process_alternate_matches
        self.process_alternate_matches()
        
    #-- END method save() --#


#= END Article_Person Model ======================================================


# Article_Author model
@python_2_unicode_compatible
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
    # instance methods
    #----------------------------------------------------------------------


    def __str__( self ):
        
        # return reference
        string_OUT = ""
        
        if ( self.id ):
        
            string_OUT += str( self.id ) + " - "
            
        #-- END check to see if id --#
        
        if ( self.person is not None ):
        
            string_OUT += self.person.last_name + ", " + self.person.first_name + " ( id = " + str( self.person.id ) + "; type = " + self.author_type + "; capture_method = " + str( self.person.capture_method ) + " )"
        
        else:
        
            string_OUT += self.author_type
            
        #-- END check to see if we have a person. --#
        
        return string_OUT

    #-- END __str__() method --#


    def process_alternate_matches( self ):
        
        '''
        If there are matches in the variable person_match_list, loops over them
           and deals with each appropriately.  person_match_list is a list of 
           Person instances of people who might be a match for a given name
           string.  For each, this method:
           - checks to see if there is an Alternate_Author_Match present for
              that person.
           - if so, moves on.
           - if not, makes one.
        '''

        #print( "@@@@@@@@ In Article_Author process_alternate_matches() @@@@@@@@" )
        
        #define variables
        person_list = None
        person_count = -1
        current_person = ""
        alt_match_qs = None
        alt_match_count = -1
        alt_author_match = None
        
        # get person list
        person_list = self.person_match_list
        
        # got anything?
        if ( person_list is not None ):

            # get count
            person_count = len( person_list )
            if ( person_count > 0 ):
            
                # loop
                for current_person in person_list:
                
                    # see if there is already an Alternate_Author_Match for the
                    #    Person.
                    alt_match_qs = self.alternate_author_match_set.filter( person = current_person )
                    
                    # got one?
                    alt_match_count = alt_match_qs.count()
                    if ( alt_match_count == 0 ):
                    
                        # no.  Make one.
                        alt_author_match = Alternate_Author_Match()
                        alt_author_match.article_author = self
                        alt_author_match.person = current_person
                        alt_author_match.save()
                        
                    # Eventually, might want to check if more than one...
                        
                    #-- END check to see if match present. --#
                
                #-- END loop over persons --#
                
            #-- END check to see if anything in the list. --#
            
        #-- END check to see if list is present. --#
        
    #-- END function process_alternate_matches() --#
    

#= End Article_Author Model ======================================================


# Alternate_Author_Match model
@python_2_unicode_compatible
class Alternate_Author_Match( models.Model ):

    #----------------------------------------------------------------------------
    # model fields and meta
    #----------------------------------------------------------------------------


    article_author = models.ForeignKey( Article_Author, blank = True, null = True )
    person = models.ForeignKey( Person, blank = True, null = True )


    #----------------------------------------------------------------------
    # instance methods
    #----------------------------------------------------------------------


    def __str__( self ):
        
        # return reference
        string_OUT = ""
        
        # got id?
        if ( self.id ):
        
            string_OUT = str( self.id ) + " - "
            
        #-- END check for ID. --#

        if ( self.article_author ):
        
            string_OUT += str( aelf.article_author ) + " alternate = "
        
        #-- END check to see if article_author. --#
        
        # got associated person?  We'd better...
        if ( self.person ):
        
            string_OUT += self.person.last_name + ", " + self.person.first_name
        
        #-- END check to see if we have a person. --#
        
        return string_OUT

    #-- END __str__() method --#


#= End Alternate_Author_Match Model ======================================================


# Article_Source model
@python_2_unicode_compatible
class Article_Source( Article_Person ):

    PARAM_SOURCE_CAPACITY_INCLUDE_LIST = 'include_capacities'
    PARAM_SOURCE_CAPACITY_EXCLUDE_LIST = 'exclude_capacities'

    # Source type stuff
    SOURCE_TYPE_ANONYMOUS = 'anonymous'
    SOURCE_TYPE_INDIVIDUAL = 'individual'
    SOURCE_TYPE_ORGANIZATION = 'organization'
    SOURCE_TYPE_DOCUMENT = 'document'
    SOURCE_TYPE_OTHER = 'other'
    
    SOURCE_TYPE_TO_ID_MAP = {
        SOURCE_TYPE_ANONYMOUS : 1,
        SOURCE_TYPE_INDIVIDUAL : 2,
        SOURCE_TYPE_ORGANIZATION : 3,
        SOURCE_TYPE_DOCUMENT : 4,
        SOURCE_TYPE_OTHER : 5
    }

    SOURCE_TYPE_CHOICES = (
        ( SOURCE_TYPE_ANONYMOUS, "Anonymous/Unnamed" ),
        ( SOURCE_TYPE_INDIVIDUAL, "Individual Person" ),
        ( SOURCE_TYPE_ORGANIZATION, "Organization" ),
        ( SOURCE_TYPE_DOCUMENT, "Document" ),
        ( SOURCE_TYPE_OTHER, "Other" )
    )

    # Source contact type stuff
    SOURCE_CONTACT_TYPE_DIRECT = 'direct'
    SOURCE_CONTACT_TYPE_EVENT = 'event'
    SOURCE_CONTACT_TYPE_PAST_QUOTES = 'past_quotes'
    SOURCE_CONTACT_TYPE_DOCUMENT = 'document'
    SOURCE_CONTACT_TYPE_OTHER = 'other'

    SOURCE_CONTACT_TYPE_TO_ID_MAP = {
        SOURCE_CONTACT_TYPE_DIRECT : 1,
        SOURCE_CONTACT_TYPE_EVENT : 2,
        SOURCE_CONTACT_TYPE_PAST_QUOTES : 3,
        SOURCE_CONTACT_TYPE_DOCUMENT : 4,
        SOURCE_CONTACT_TYPE_OTHER : 5
    }

    SOURCE_CONTACT_TYPE_CHOICES = (
        ( SOURCE_CONTACT_TYPE_DIRECT, "Direct contact" ),
        ( SOURCE_CONTACT_TYPE_EVENT, "Press conference/event" ),
        ( SOURCE_CONTACT_TYPE_PAST_QUOTES, "Past quotes/statements" ),
        ( SOURCE_CONTACT_TYPE_DOCUMENT, "Press release/document" ),
        ( SOURCE_CONTACT_TYPE_OTHER, "Other" )
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
    
    # fields to track locations of data this coding was based on within
    #    article.  References are based on results of ParsedArticle.parse().
    #attribution_verb_word_index = models.IntegerField( blank = True, null = True, default = 0 )
    #attribution_verb_word_number = models.IntegerField( blank = True, null = True, default = 0 )
    #attribution_paragraph_number = models.IntegerField( blank = True, null = True, default = 0 )
    #attribution_speaker_name_string = models.TextField( blank = True, null = True )
    #is_speaker_name_pronoun = models.BooleanField( default = False )
    #attribution_speaker_name_index_range = models.CharField( max_length = 255, blank = True, null = True )
    #attribution_speaker_name_word_range = models.CharField( max_length = 255, blank = True, null = True )
    
    # field to store how source was captured. - parent
    #capture_method = models.CharField( max_length = 255, blank = True, null = True )
    
    

    #----------------------------------------------------------------------
    # methods
    #----------------------------------------------------------------------

    def __str__( self ):

        # return reference
        string_OUT = ''
        
        # declare variables
        temp_string = ""
        separator = ""

        if ( self.id ):
        
            string_OUT += str( self.id ) + " - "
        
        #-- END check to see if ID --#
        
        if ( self.source_type == "individual" ):

            if ( self.person is not None ):

                # last name
                temp_string = self.person.last_name
                if ( ( temp_string is not None ) and ( temp_string != "" ) ):
                
                    string_OUT += temp_string
                    separator = ", "
                    
                #-- END last name --#
                
                # first name
                temp_string = self.person.first_name
                if ( ( temp_string is not None ) and ( temp_string != "" ) ):
                
                    string_OUT += separator + temp_string
                    separator = ", "
                    
                #-- END first name --#
                
                # there will be an ID, and fine to just output "None" if no
                #    capture_method.
                string_OUT += " ( id = " + str( self.person.id ) + "; capture_method = " + str( self.person.capture_method ) + " )"

            else:

                if ( self.title != '' ):

                    string_OUT += self.title

                else:

                    string_OUT += "individual"

                #-- END check to see if title --#

            #-- END check to see if person --#

        elif ( self.source_type == "organization" ):

            if ( self.organization is not None ):

                string_OUT += self.organization.name

            else:

                string_OUT += self.title

            #-- END check to see if organization --#

        elif ( self.source_type == "document" ):

            if ( self.document is not None ):

                string_OUT += self.document.name

            else:

                string_OUT += self.notes

            #-- END check to see if Document --#

        #elif ( self.source_type == "anonymous" ):
        #    string_OUT =
        
        #-- END check to see what type of source --#

        string_OUT = string_OUT + " (" + self.source_type + ")"

        return string_OUT

    #-- END method __str__() --#


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
    

    def process_alternate_matches( self ):
        
        '''
        If there are matches in the variable person_match_list, loops over them
           and deals with each appropriately.  person_match_list is a list of 
           Person instances of people who might be a match for a given name
           string.  For each, this method:
           - checks to see if there is an Alternate_Author_Match present for
              that person.
           - if so, moves on.
           - if not, makes one.
        '''

        #print( "&&&&&&&& In Article_Source process_alternate_matches() &&&&&&&&" )
        
        #define variables
        person_list = None
        person_count = -1
        current_person = ""
        alt_match_qs = None
        alt_match_count = -1
        alt_author_match = None
        
        # get person list
        person_list = self.person_match_list
        
        # got anything?
        if ( person_list is not None ):

            # get count
            person_count = len( person_list )
            if ( person_count > 0 ):
            
                # loop
                for current_person in person_list:
                
                    # see if there is already an Alternate_Source_Match for the
                    #    Person.
                    alt_match_qs = self.alternate_source_match_set.filter( person = current_person )
                    
                    # got one?
                    alt_match_count = alt_match_qs.count()
                    if ( alt_match_count == 0 ):
                    
                        # no.  Make one.
                        alt_author_match = Alternate_Source_Match()
                        alt_author_match.article_source = self
                        alt_author_match.person = current_person
                        alt_author_match.save()
                        
                    # Eventually, might want to check if more than one...
                        
                    #-- END check to see if match present. --#
                
                #-- END loop over persons --#
                
            #-- END check to see if anything in the list. --#
            
        #-- END check to see if list is present. --#
        
    #-- END function process_alternate_matches() --#


#= End Article_Source Model ======================================================


# Alternate_Source_Match model
@python_2_unicode_compatible
class Alternate_Source_Match( models.Model ):

    #----------------------------------------------------------------------------
    # model fields and meta
    #----------------------------------------------------------------------------


    article_source = models.ForeignKey( Article_Source, blank = True, null = True )
    person = models.ForeignKey( Person, blank = True, null = True )


    #----------------------------------------------------------------------
    # instance methods
    #----------------------------------------------------------------------


    def __str__( self ):
        
        # return reference
        string_OUT = ""
        
        # got id?
        if ( self.id ):
        
            string_OUT = str( self.id ) + " - "
            
        #-- END check for ID. --#

        if ( self.article_source ):
        
            string_OUT += str( self.article_source ) + " alternate = "
        
        #-- END check to see if article_source. --#
        
        # got associated person?  We'd better...
        if ( self.person ):
        
            string_OUT += self.person.last_name + ", " + self.person.first_name
        
        #-- END check to see if we have a person. --#
        
        return string_OUT

    #-- END __str__() method --#


#= End Alternate_Source_Match Model ======================================================


# Abstract_Selected_Text model
@python_2_unicode_compatible
class Abstract_Selected_Text( models.Model ):

    '''
    This abstract class is used to store text that has been selected from inside
       a larger text document.  It holds details on the text found, the text
       around it, and the method used to single out the text.  Can be extended to
       reference a Foreign Key of the container in which this text was found.
    '''

    #----------------------------------------------------------------------------
    # model fields and meta
    #----------------------------------------------------------------------------


    # basics - value, text before and after the value, length and index of value.
    value = models.TextField( blank = True, null = True )
    value_in_context = models.TextField( blank = True, null = True )
    value_index = models.IntegerField( blank = True, null = True, default = 0 )
    value_length = models.IntegerField( blank = True, null = True, default = 0 )
    canonical_index = models.IntegerField( blank = True, null = True, default = 0 )
    value_word_number_start = models.IntegerField( blank = True, null = True, default = 0 )
    value_word_number_end = models.IntegerField( blank = True, null = True, default = 0 )
    paragraph_number = models.IntegerField( blank = True, null = True, default = 0 )
    context_before = models.TextField( blank = True, null = True )
    context_after = models.TextField( blank = True, null = True )

    # field to store how source was captured.
    capture_method = models.CharField( max_length = 255, blank = True, null = True )
    
    # additional identifying information
    uuid = models.TextField( blank = True, null = True )
    uuid_name = models.CharField( max_length = 255, null = True, blank = True )

    # other notes.
    notes = models.TextField( blank = True, null = True )

    # time stamps.
    create_date = models.DateTimeField( auto_now_add = True )
    last_modified = models.DateTimeField( auto_now = True )

    # meta class so we know this is an abstract class.
    class Meta:

        abstract = True
        ordering = [ 'last_modified', 'create_date' ]
        
    #-- END inner class Meta --#
        

    #----------------------------------------------------------------------
    # instance methods
    #----------------------------------------------------------------------


    def __str__( self ):
        
        # return reference
        string_OUT = ""
        
        # got id?
        if ( self.id ):
        
            string_OUT = str( self.id ) + " - "
            
        #-- END check for ID. --#

        if ( self.value_offset ):
        
            string_OUT += " ( index: " + str( self.value_offset ) + " ) : "
        
        #-- END check to see if article_source. --#
        
        # got associated text?...
        if ( self.value ):
        
            string_OUT += self.value
                
        #-- END check to see if we have a value. --#
        
        return string_OUT

    #-- END __str__() method --#
    
    
    def build_details_list( self ):
        
        '''
        Pulls together details on this selected text, one item to a list
           element.  If present in instance, includes:
           - graf - paragraph_number
           - from word - starting word number
           - to word - ending word number
           - index - start character index in plain-text.
        '''
        
        # return reference
        list_OUT = []
        
        if ( self.paragraph_number ):
        
            list_OUT.append( "graf: " + str( self.paragraph_number ) )
            
        #-- END check to see if paragraph_number --#
        
        if ( self.value_word_number_start ):
        
            list_OUT.append( "from word: " + str( self.value_word_number_start ) )
            
        #-- END check to see if value_word_number_start --#
        
        if ( self.value_word_number_end ):
        
            list_OUT.append( "to word: " + str( self.value_word_number_end ) )
            
        #-- END check to see if value_word_number_end --#
        
        if ( self.value_index ):
        
            list_OUT.append( "index: " + str( self.value_index ) )
            
        #-- END check to see if value_index --#
        
        return list_OUT
        
    #-- END method build_details_list --#
    


#-- END abstract class Abstract_Selected_Text --#


# Article_Source_Quotation model
@python_2_unicode_compatible
class Article_Source_Mention( Abstract_Selected_Text ):

    #----------------------------------------------------------------------------
    # model fields and meta
    #----------------------------------------------------------------------------


    # source in a given article whom this quote belongs to.
    article_source = models.ForeignKey( Article_Source, blank = True, null = True )
    
    # is name a pronoun?
    is_speaker_name_pronoun = models.BooleanField( default = False )


    #----------------------------------------------------------------------
    # instance methods
    #----------------------------------------------------------------------


    def __str__( self ):
        
        # return reference
        string_OUT = ""
        
        # declare variables
        details_list = []
        
        # got id?
        if ( self.id ):
        
            string_OUT = str( self.id ) + " - "
            
        #-- END check for ID. --#

        details_list = self.build_details_list()
        
        # got anything in list?
        if ( len( details_list ) > 0 ):
        
            string_OUT += " ( " + "; ".join( details_list ) + " ) - "
        
        #-- END check to see if got anything in list --#

        if ( self.article_source ):
        
            string_OUT += str( self.article_source ) + " : "
        
        #-- END check to see if article_source. --#
        
        # got associated text?...
        if ( self.value_in_context ):
        
            string_OUT += self.value_in_context
        
        elif ( self.value ):
        
            string_OUT += self.value
                
        #-- END check to see if we have a quotation. --#
        
        return string_OUT

    #-- END __str__() method --#

#= End Article_Source_Mention Model ======================================================


# Article_Source_Quotation model
@python_2_unicode_compatible
class Article_Source_Quotation( Abstract_Selected_Text ):

    #----------------------------------------------------------------------------
    # model fields and meta
    #----------------------------------------------------------------------------


    # source in a given article whom this quote belongs to.
    article_source = models.ForeignKey( Article_Source, blank = True, null = True )
    
    # value_with_attribution
    value_with_attribution = models.TextField( blank = True, null = True )
    
    # fields to track locations of data this coding was based on within
    #    article.  References are based on results of ParsedArticle.parse().
    attribution_verb_word_index = models.IntegerField( blank = True, null = True, default = 0 )
    attribution_verb_word_number = models.IntegerField( blank = True, null = True, default = 0 )
    attribution_paragraph_number = models.IntegerField( blank = True, null = True, default = 0 )
    attribution_speaker_name_string = models.TextField( blank = True, null = True )
    is_speaker_name_pronoun = models.BooleanField( default = False )
    attribution_speaker_name_index_range = models.CharField( max_length = 255, blank = True, null = True )
    attribution_speaker_name_word_range = models.CharField( max_length = 255, blank = True, null = True )
    

    #----------------------------------------------------------------------
    # instance methods
    #----------------------------------------------------------------------


    def __str__( self ):
        
        # return reference
        string_OUT = ""
        
        # declare variables
        details_list = []
        
        # got id?
        if ( self.id ):
        
            string_OUT = str( self.id ) + " - "
            
        #-- END check for ID. --#

        details_list = self.build_details_list()
        
        # got anything in list?
        if ( len( details_list ) > 0 ):
        
            string_OUT += " ( " + "; ".join( details_list ) + " ) - "
        
        #-- END check to see if got anything in list --#

        if ( self.article_source ):
        
            string_OUT += str( self.article_source ) + " : "
        
        #-- END check to see if article_source. --#
        
        # got associated quotation?...
        if ( self.value ):
        
            string_OUT += self.value
                
        #-- END check to see if we have a quotation. --#
        
        return string_OUT

    #-- END __str__() method --#

#= End Article_Source_Quotation Model ======================================================


# Source_Organization model
@python_2_unicode_compatible
class Source_Organization( models.Model ):

    article_source = models.ForeignKey( Article_Source )
    organization = models.ForeignKey( Organization, blank = True, null = True )
    title = models.CharField( max_length = 255, blank = True )

    #----------------------------------------------------------------------
    # instance methods
    #----------------------------------------------------------------------

    def __str__( self ):
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

#    def __str__( self ):

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

#    def __str__( self ):
        #string_OUT = self.rank + " - " + self.location.name
#        string_OUT = '%d - %s' % ( self.rank, self.location.name )
#        return string_OUT

#= End Article_Location Model ======================================================


# Import_Error model
@python_2_unicode_compatible
class Import_Error( models.Model ):

    unique_identifier = models.CharField( max_length = 255, blank = True )
    archive_source = models.CharField( max_length = 255, blank = True, null = True )
    item = models.TextField( blank = True, null = True )
    message = models.TextField( blank = True, null = True )
    exception = models.TextField( blank = True, null = True )
    stack_trace = models.TextField( blank = True, null = True )
    batch_identifier = models.CharField( max_length = 255, blank = True )
    item_date = models.DateTimeField( blank = True, null = True )
    status = models.CharField( max_length = 255, blank = True, null = True, default = "new" )
    create_date = models.DateTimeField( auto_now_add = True )
    last_modified = models.DateTimeField( auto_now = True )

    #----------------------------------------------------------------------
    # methods
    #----------------------------------------------------------------------

    def __str__( self ):
        #string_OUT = self.rank + " - " + self.location.name
        string_OUT = '%d - %s (%s): %s' % ( self.id, self.unique_identifier, self.item, self.message )
        return string_OUT

#= End Import_Error Model ======================================================


# Temp_Section model
@python_2_unicode_compatible
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
    # model fields
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

    def __str__( self ):

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

    #-- END method __str__() --#

    
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


#= End Temp_Section Model ======================================================#


@python_2_unicode_compatible
class Articles_To_Migrate( models.Model ):

    ARTICLE_TYPE_CHOICES = (
        ( "news", "News" ),
        ( "sports", "Sports" ),
        ( "feature", "Feature" ),
        ( "opinion", "Opinion" ),
        ( "other", "Other" )
    )

    article = models.ForeignKey( Article, blank = True, null = True )
    unique_identifier = models.CharField( max_length = 255, blank = True )
    coder = models.ForeignKey( User )
    newspaper = models.ForeignKey( Newspaper, blank = True, null = True )
    pub_date = models.DateField()
    section = models.CharField( max_length = 255, blank = True )
    page = models.IntegerField( blank = True )
    headline = models.CharField( max_length = 255 )
    text = models.TextField( blank = True )
    is_sourced = models.BooleanField( default = True )
    can_code = models.BooleanField( default = True )
    article_type = models.CharField( max_length = 255, choices = ARTICLE_TYPE_CHOICES, blank = True, default = 'news' )

    #----------------------------------------------------------------------------
    # Meta class
    #----------------------------------------------------------------------------

    # Meta-data for this class.
    class Meta:
        ordering = [ 'pub_date', 'section', 'page' ]


    #----------------------------------------------------------------------------
    # instance methods
    #----------------------------------------------------------------------------


    def __str__( self ):

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

    #-- END method __str__() --#
     

#= END Articles_To_Migrate model ===============================================#

