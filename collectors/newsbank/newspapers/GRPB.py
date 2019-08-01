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

# imports - newsbank newspapers
from context_text.collectors.newsbank.newspapers.newsbank_newspaper import NewsbankNewspaper


# define GRPB newspaper class.
class GRPB( NewsbankNewspaper ):


    #===========================================================================
    # constants-ish
    #===========================================================================


    NEWSPAPER_NAME = 'The Grand Rapids Press'
    NEWSBANK_PLACE_CODE = 'GRPB'
    NEWSPAPER_ID = 1
    
    # name fragments for searching
    STRING_PAPER_NAME = "Grand Rapids Press"
    STRING_PAPER_NAME_LOWER = STRING_PAPER_NAME.lower()
    STRING_AUTHOR_SEPARATOR = " / "
    
    # affiliation strings - convert to regular expressions.
    # ! TODO - add in misspellings and errors.
    AFFILIATION_REGEX_THE_GRAND_RAPIDS_PRESS = re.compile( r'THE\s+GRAND\s+RAPIDS\s+PRESS$', re.IGNORECASE )
    AFFILIATION_REGEX_PAPER_NAME = AFFILIATION_REGEX_THE_GRAND_RAPIDS_PRESS
    AFFILIATION_REGEX_SPECIAL_TO = re.compile( r'SPECIAL\s+TO\s+THE\s+PRESS$', re.IGNORECASE )
    AFFILIATION_REGEX_BUREAU = re.compile( r'GRAND\s+RAPIDS\s+PRESS\s+.*\s+BUREAU$', re.IGNORECASE )
    AFFILIATION_REGEX_EDITOR = re.compile( r'PRESS\s+.*\s+EDITOR$', re.IGNORECASE )
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
    AUTHOR_THE_GRAND_RAPIDS_PRESS = "The Grand Rapids Press"
    STAFF_AUTHOR_STRINGS_LIST = [ AUTHOR_THE_GRAND_RAPIDS_PRESS ]

    # author info cleanup
    AUTHOR_INFO_CLEANUP_STATUS_ABORT_LIST = [ Article.CLEANUP_STATUS_AUTHOR_FIXED, Article.CLEANUP_STATUS_AUTHOR_AND_TEXT_FIXED, Article.CLEANUP_STATUS_COMPLETE ]

    # Sections
    LOCAL_SECTION_NAME_LIST = [ "Business", "City and Region", "Front Page", "Lakeshore", "Religion", "Special", "Sports", "State" ]
    GRP_LOCAL_SECTION_NAME_LIST = LOCAL_SECTION_NAME_LIST
    NEWS_SECTION_NAME_LIST = [ "Business", "City and Region", "Front Page", "Lakeshore", "Religion", "Special", "State" ]
    GRP_NEWS_SECTION_NAME_LIST = NEWS_SECTION_NAME_LIST
    LOCAL_NEWS_SECTION_NAME_LIST = NEWS_SECTION_NAME_LIST
    
    # In-house author string patterns
    AUTHOR_STRING_REGEX_BASE = r'.* */ *THE GRAND RAPIDS PRESS$'
    AUTHOR_STRING_REGEX_EDITOR = r'.* */ *PRESS .* EDITOR$'
    AUTHOR_STRING_REGEX_BUREAU = r'.* */ *GRAND RAPIDS PRESS .* BUREAU$'
    AUTHOR_STRING_REGEX_SPECIAL = r'.* */ *SPECIAL TO THE PRESS$'
    
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
        
    Q_GRP_IN_HOUSE_AUTHOR = Q_IN_HOUSE_AUTHOR
    
    # Columns are mixed in with news, you have to filter them out based on the
    #     index_term column containing the string "Column".
    # grp_article_qs = grp_article_qs.exclude( index_terms__icontains = "Column" )

    # DEBUG
    DEBUG_FLAG = True
    
    # logging
    LOGGER_NAME = "context_text.collectors.newsbank.newspapers.GRPB"
    

    #===========================================================================
    # ! ==> static methods
    #===========================================================================


    #===========================================================================
    # ! ==> class methods
    #===========================================================================

    
    @classmethod
    def derive_affiliation_from_author_string( cls, *args, **kwargs ):

        '''
        Method contains code used to originally populate the column
            `author_affiliation` from `author_string` in original article data.
        '''

        # declare variables
        grp_newspaper = None
        grp_article_qs = None
        article_count = None
        article_counter = None
        current_article = None
        author_string = None
        slash_index = None
        affiliation = None
        
        # lookup grp_newspaper
        grp_newspaper = Newspaper.objects.filter( pk = cls.NEWSPAPER_ID )

        # populate author_affiliation in Article table for GR Press.
        grp_article_qs = Article.objects.filter( newspaper = grp_newspaper )
        grp_article_qs = grp_article_qs.filter( author_string__contains = "/" )
        grp_article_qs = grp_article_qs.filter( author_affiliation__isnull = True )
        
        article_count = grp_article_qs.count()
        article_counter = 0
        for current_article in grp_article_qs:
        
            article_counter = article_counter + 1
        
            # output article.
            print( "- Article " + str( article_counter ) + " of " + str( article_count ) + ": " + str( current_article ) )
            
            # get author_string
            author_string = current_article.author_string
            
            # find "/"
            slash_index = author_string.find( "/" )
            
            # got one?
            if ( slash_index > -1 ):
            
                # yes.  get everything after the slash.
                affiliation = author_string[ ( slash_index + 1 ) : ]
                
                # strip off white space
                affiliation = affiliation.strip()
                
                print( "    - Affiliation = \"" + affiliation + "\"" )
                
                current_article.author_affiliation = affiliation
                current_article.save()
                
            #-- END check to see if "/" present.
            
        #-- END loop over articles. --#
        
    #-- END class method derive_affiliation_from_author_string --#


    #===========================================================================
    # ! ==> __init__() method
    #===========================================================================


    def __init__( self ):

        # call parent's __init__()
        super( GRPB, self ).__init__()

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
    # ! ==> instance methods, in alphabetical order
    #===========================================================================

    
#-- END class GRPB --#