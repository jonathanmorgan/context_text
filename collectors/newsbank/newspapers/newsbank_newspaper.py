# support Python 3:
from __future__ import unicode_literals

'''
Copyright 2019 - Jonathan Morgan

This file is part of http://github.com/jonathanmorgan/context_text.

context_text is free software: you can redistribute it and/or modify
it under the terms of the GNU Lesser General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

context_text is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU Lesser General Public License
along with http://github.com/jonathanmorgan/python_utilities.  If not, see
<http://www.gnu.org/licenses/>.
'''

'''
Usage:

'''

# regular expressions
#import re
import regex as re

# django imports

# Django query object for OR-ing selection criteria together.
from django.db.models import Q

# imports - python_utilities
from python_utilities.exceptions.exception_helper import ExceptionHelper
from python_utilities.logging.logging_helper import LoggingHelper
from python_utilities.status.status_container import StatusContainer
from python_utilities.strings.string_helper import StringHelper

# imports - django_messages
from django_messages.models import Message

# imports - context_text.article_coding
from context_text.article_coding.article_coder import ArticleCoder

# imports - context_text.models
from context_text.models import Article
from context_text.models import Article_Notes
from context_text.models import Article_Text
from context_text.models import Newspaper


# define GRPB newspaper class.
class NewsbankNewspaper( LoggingHelper ):


    '''
    Based on DTNB.  Instance methods for finding affiliation in the 1st or
        sometimes 2nd paragraph rather than the author string is still here, for
        reference, but could be stripped out:
        
        - analyze_author_info()
        - capture_author_info()
        - clean_up_author_info()
        - fix_author_info()
    '''

    #===========================================================================
    # constants-ish
    #===========================================================================

    EMPTY_PLACEHOLDER = "EMPTY"

    NEWSPAPER_NAME = EMPTY_PLACEHOLDER
    NEWSBANK_PLACE_CODE = None
    NEWSPAPER_ID = None
    
    # name fragments for searching
    STRING_PAPER_NAME = EMPTY_PLACEHOLDER
    STRING_PAPER_NAME_LOWER = STRING_PAPER_NAME.lower()
    STRING_AUTHOR_SEPARATOR = " / "
    
    # affiliation strings - convert to regular expressions.
    # ! TODO - add in misspellings and errors.
    AFFILIATION_REGEX_PAPER_NAME = None
    AFFILIATION_REGEX_SPECIAL_TO = None
    AFFILIATION_REGEX_BUREAU = None
    AFFILIATION_REGEX_EDITOR = None
    AFFILIATION_DEFAULT = NEWSPAPER_NAME
    
    # affiliation list is organized from most general to most specific, such
    #     that last match should be used.  "Special to The Grand Rapids Press"
    #     is after "The Grand Rapids Press" in the list, for example, so while
    #     "The Grand Rapids Press" will match, so will "Special to The Grand
    #     Rapids Press" subsequently.
    STAFF_AFFILIATION_REGEX_LIST = [
        AFFILIATION_REGEX_PAPER_NAME,
        AFFILIATION_REGEX_SPECIAL_TO,
        AFFILIATION_REGEX_BUREAU,
        AFFILIATION_REGEX_EDITOR
    ]

    # collective author strings
    # ! TODO - add in all collective author strings.
    STAFF_AUTHOR_STRINGS_LIST = []

    # Sections
    LOCAL_SECTION_NAME_LIST = []
    NEWS_SECTION_NAME_LIST = []
    LOCAL_NEWS_SECTION_NAME_LIST = NEWS_SECTION_NAME_LIST
    
    # In-house author string patterns
    AUTHOR_STRING_REGEX_BASE = r'.* */ *EXAMPLE PAPER NAME$'
    AUTHOR_STRING_REGEX_EDITOR = r'.* */ *PAPER .* EDITOR$'
    AUTHOR_STRING_REGEX_BUREAU = r'.* */ *PAPER .* BUREAU$'
    AUTHOR_STRING_REGEX_SPECIAL = r'.* */ *SPECIAL TO THE PAPER$'
    
    # make a list of the author string regular expressions
    AUTHOR_STRING_IN_HOUSE_REGEX_LIST = []
    AUTHOR_STRING_IN_HOUSE_REGEX_LIST.append( AUTHOR_STRING_REGEX_BASE )
    AUTHOR_STRING_IN_HOUSE_REGEX_LIST.append( AUTHOR_STRING_REGEX_EDITOR )
    AUTHOR_STRING_IN_HOUSE_REGEX_LIST.append( AUTHOR_STRING_REGEX_BUREAU )
    AUTHOR_STRING_IN_HOUSE_REGEX_LIST.append( AUTHOR_STRING_REGEX_SPECIAL )
    
    # compile individual values.
    AUTHOR_STRING_COMPILED_REGEX_BASE = re.compile( AUTHOR_STRING_REGEX_BASE, re.IGNORECASE )
    AUTHOR_STRING_COMPILED_REGEX_EDITOR = re.compile( AUTHOR_STRING_REGEX_EDITOR, re.IGNORECASE )
    AUTHOR_STRING_COMPILED_REGEX_BUREAU = re.compile( AUTHOR_STRING_REGEX_BUREAU, re.IGNORECASE )
    AUTHOR_STRING_COMPILED_REGEX_SPECIAL = re.compile( AUTHOR_STRING_REGEX_SPECIAL, re.IGNORECASE )

    # ! TODO - add in misspellings and errors.

    #Q_IN_HOUSE_AUTHOR = Q( author_varchar__iregex = r'.* */ *THE GRAND RAPIDS PRESS$' ) | Q( author_varchar__iregex = r'.* */ *PRESS .* EDITOR$' ) | Q( author_varchar__iregex = r'.* */ *GRAND RAPIDS PRESS .* BUREAU$' ) | Q( author_varchar__iregex = r'.* */ *SPECIAL TO THE PRESS$' )
    Q_IN_HOUSE_AUTHOR_STATIC = Q( author_varchar__iregex = AUTHOR_STRING_REGEX_BASE ) | Q( author_varchar__iregex = AUTHOR_STRING_REGEX_EDITOR ) | Q( author_varchar__iregex = AUTHOR_STRING_REGEX_BUREAU ) | Q( author_varchar__iregex = AUTHOR_STRING_REGEX_SPECIAL )

    # Build Q from list of in-house author_string regular expressions.
    Q_IN_HOUSE_AUTHOR = None
    q_current_regex = None
    for author_string_regex in AUTHOR_STRING_IN_HOUSE_REGEX_LIST:
    
        # create Q()
        q_current_regex = Q( author_varchar__iregex = author_string_regex )
    
        # anything in output variable?
        if ( Q_IN_HOUSE_AUTHOR is None ):
        
            # empty - set to the first thing.
            Q_IN_HOUSE_AUTHOR = q_current_regex
            
        else:
        
            # not empty - OR
            Q_IN_HOUSE_AUTHOR = Q_IN_HOUSE_AUTHOR | q_current_regex
            
        #-- END check to see if there is already a Q. --#
        
    #-- END loop over in-house author_string regular expressions. --#
        
    # DEBUG
    DEBUG_FLAG = True
    
    # logging
    LOGGER_NAME = "context_text.collectors.newsbank.newspapers.newsbank_newspaper"
    

    #===========================================================================
    # ! ==> static methods
    #===========================================================================


    #===========================================================================
    # ! ==> class methods
    #===========================================================================

    
    @classmethod
    def find_affiliation_in_string( cls, string_IN, default_affiliation_IN = None, return_all_matches_IN = False, *args, **kwargs ):
        
        '''
        Loops through cls.STAFF_AFFILIATION_REGEX_LIST, returns the last match found
            within the string passed in.  If optional parameter 
            return_all_matches_IN is True, returns list of matches ordered from
            most recent first ( [ 0 ] ) to least recent last.
        '''
        
        # return reference
        value_OUT = ""
        
        # call StringHelper regex function.
        value_OUT = StringHelper.find_regex_matches( string_IN,
                                                     cls.STAFF_AFFILIATION_REGEX_LIST,
                                                     default_value_IN = default_affiliation_IN,
                                                     return_all_matches_IN = return_all_matches_IN,
                                                     *args,
                                                     **kwargs )
        
        return value_OUT
        
    #-- END method find_affiliation_in_string() --#
    

    @classmethod
    def is_collective_byline( cls, string_IN, *args, **kwargs ):
        
        '''
        For now, looks for the author string passed in in the list of staff
            author strings.
        '''
        
        # return reference
        value_OUT = ""
        
        # call StringHelper is_in_string_list() function.
        value_OUT = StringHelper.is_in_string_list( string_IN, cls.STAFF_AUTHOR_STRINGS_LIST, ignore_case_IN = True )
        
        return value_OUT
        
    #-- END method is_collective_byline() --#
    

    @classmethod
    def is_staff_author_string( cls, string_IN, *args, **kwargs ):
        
        '''
        Uses find_affiliation_in_string() to look for affiliation in author
            string.  If it finds one, returns true - that is likely a staff
            author.  If it doesn't find one, returns False.
        '''
        
        # return reference
        value_OUT = ""
        
        # declare variables
        affiliation_value = ""
        
        # call StringHelper regex function.
        affiliation_value = cls.find_affiliation_in_string( cls,
                                                            string_IN,
                                                            default_value_IN = None,
                                                            return_all_matches_IN = False,
                                                            *args,
                                                            **kwargs )
                                                             
        # got anything back?
        if ( ( affiliation_value is not None ) and ( affiliation_value != "" ) ):
        
            # got something.
            value_OUT = True
            
        #-- END check to see if found an affiliation --#
        
        return value_OUT
        
    #-- END method is_staff_author_string() --#
    

    #===========================================================================
    # __init__() method
    #===========================================================================


    def __init__( self ):

        # call parent's __init__()
        super( NewsbankNewspaper, self ).__init__()

        # declare variables - logging
        self.logger_debug_flag = self.DEBUG_FLAG
        self.m_logger_name = self.LOGGER_NAME
        self.set_logger_name( self.LOGGER_NAME )
        self.logger_also_print_flag = True

        # debug
        self.debug = ""
        
        # exception helper
        self.exception_helper = None
        my_exception_helper = ExceptionHelper()
        #my_exception_helper.set_logging_level( logging.DEBUG )
        self.set_exception_helper( my_exception_helper )
        
        # default affiliation
        self.default_affiliation = None

    #-- END method __init__() --#


    #===========================================================================
    # instance methods, in alphabetical order
    #===========================================================================

    
    def get_exception_helper( self ):

        '''
        Returns this instance's ExceptionHelper instance.  If no value, returns None.
        '''
        
        # return reference
        value_OUT = None

        # declare variables

        # get value.
        value_OUT = self.exception_helper
        
        # got anything?
        if ( ( value_OUT is None ) or ( value_OUT == "" ) ):
        
            # no - return None.
            value_OUT = None
            
        #-- END check to see if we have a value. --#

        return value_OUT

    #-- END get_exception_helper() --#


    def remove_affiliation_from_author_string( self, author_string_IN, *args, **kwargs ):

        # return reference
        value_OUT = ""
        
        # declare variables
        author_string = ""
        author_string_affiliation = ""
        author_string_work = None

        # got an author_string_IN?
        if ( ( author_string_IN is not None ) and ( author_string_IN != "" ) ):
            
            author_string = author_string_IN
            
            # look for known affiliations in string passed in.
            author_string_affiliation = self.find_affiliation_in_string( author_string )
            if ( ( author_string_affiliation is not None )
                and ( author_string_affiliation != "" ) ):
                        
                # author affiliation is in the author_string.                      
                
                # Remove author_string_affiliation from author_string...
                author_string_work = author_string.replace( author_string_affiliation, "" )

                # ...also remove any semi-colons...
                author_string_work = author_string_work.replace( ";", "" )

                # ...and remove white space.
                author_string_work = author_string_work.strip()
                
                # return this.
                value_OUT = author_string_work
                
            else:
            
                # no affiliations found.  return what was passed in.
                value_OUT = author_string
            
            #-- END check to see if affiliation in author_string --#
            
        else:
        
            # nothing passed in.  Return it.
            value_OUT = author_string_IN
        
        #-- END check to see if author_string passed in. --#
        
        return value_OUT

    #-- END method remove_affiliation_from_author_string() --#

    
    def set_exception_helper( self, value_IN ):

        '''
        Accepts an ExceptionHelper instance, stores value passed in, returns the
           value.
        '''
        
        # return reference
        value_OUT = None

        # declare variables

        # store value.
        self.exception_helper = value_IN
        
        # get return value
        value_OUT = self.get_exception_helper()

        return value_OUT

    #-- END set_exception_helper() --#


#-- END class GRPB --#