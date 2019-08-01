# support Python 3:
from __future__ import unicode_literals

'''
Copyright 2016 - Jonathan Morgan

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


# define DTNB newspaper class.
class DTNB( NewsbankNewspaper ):


    #===========================================================================
    # constants-ish
    #===========================================================================


    NEWSPAPER_NAME = 'The Detroit News'
    NEWSBANK_PLACE_CODE = 'DTNB'
    NEWSPAPER_ID = 2
    
    # name fragments for searching
    STRING_PAPER_NAME = "Detroit News"
    STRING_PAPER_NAME_LOWER = STRING_PAPER_NAME.lower()
    STRING_AUTHOR_SEPARATOR = " / "
    
    # affiliation strings - convert to regular expressions.
    # ! TODO - add in misspellings and errors.
    AFFILIATION_REGEX_THE_DETROIT_NEWS = re.compile( r"The\s+Detroit\s+News", re.IGNORECASE )
    AFFILIATION_REGEX_PAPER_NAME = AFFILIATION_REGEX_THE_DETROIT_NEWS
    AFFILIATION_REGEX_SPECIAL_TO = re.compile( r"Special\s+to\s+The\s+Detroit\s+News", re.IGNORECASE )
    AFFILIATION_REGEX_BUREAU = re.compile( r"Detroit News\s+.*\s+Bureau", re.IGNORECASE )
    AFFILIATION_REGEX_EDITOR = re.compile( r"Detroit News\s+.*\s+Editor", re.IGNORECASE )
    AFFILIATION_DEFAULT = NEWSPAPER_NAME
    
    # affiliation list is organized from most general to most specific, such
    #     that last match should be used.  "Special to The Detroit News" is
    #     after "The Detroit News" in the list, for example, so while "The
    #     Detroit News" will match, so will "Special to The Detroit News"
    #     subsequently.
    STAFF_AFFILIATION_REGEX_LIST = [
        AFFILIATION_REGEX_PAPER_NAME,
        AFFILIATION_REGEX_SPECIAL_TO,
        AFFILIATION_REGEX_BUREAU,
        AFFILIATION_REGEX_EDITOR
    ]

    # collective author strings
    AUTHOR_THE_DETROIT_NEWS = "The Detroit News"
    AUTHOR_DETROIT_NEWS_STAFF = "Detroit News staff"
    AUTHOR_THE_DETROIT_NEWS_STAFF = "The Detroit News Staff"
    AUTHOR_STAFF_REPORTS = "Detroit News staff reports"
    AUTHOR_STAFF_AND_WIRE = "Detroit News staff and wire reports"
    AUTHOR_WIRE_REPORTS = "Detroit News wire reports"
    AUTHOR_WIRE_SERVICES = "Detroit News wire services"
    STAFF_AUTHOR_STRINGS_LIST = [ AUTHOR_THE_DETROIT_NEWS, AUTHOR_DETROIT_NEWS_STAFF, AUTHOR_THE_DETROIT_NEWS_STAFF, AUTHOR_STAFF_REPORTS, AUTHOR_STAFF_AND_WIRE, AUTHOR_WIRE_REPORTS, AUTHOR_WIRE_SERVICES ]

    # author info cleanup
    AUTHOR_INFO_CLEANUP_STATUS_ABORT_LIST = [ Article.CLEANUP_STATUS_AUTHOR_FIXED, Article.CLEANUP_STATUS_AUTHOR_AND_TEXT_FIXED, Article.CLEANUP_STATUS_COMPLETE ]

    # Sections
    LOCAL_SECTION_NAME_LIST = [ "Business", "Metro", "Nation", "Sports" ]
    NEWS_SECTION_NAME_LIST = [ "Business", "Metro", "Nation" ]
    LOCAL_NEWS_SECTION_NAME_LIST = NEWS_SECTION_NAME_LIST
    
    # In-house author string patterns
    AUTHOR_STRING_REGEX_BASE = r'.*\s*/\s*the\s*detroit\s*news$'
    #AUTHOR_STRING_REGEX_EDITOR = r'.* */ *PRESS .* EDITOR$'
    AUTHOR_STRING_REGEX_BUREAU = r'.*\s*/\s*detroit\s*news\s*.*\s*bureau$'
    AUTHOR_STRING_REGEX_SPECIAL = r'.*\s*/\s*special\s*to\s*the\s*detroit\s*news$'
    
    # make a list of the author string regular expressions
    AUTHOR_STRING_IN_HOUSE_REGEX_LIST = []
    AUTHOR_STRING_IN_HOUSE_REGEX_LIST.append( AUTHOR_STRING_REGEX_BASE )
    #AUTHOR_STRING_IN_HOUSE_REGEX_LIST.append( AUTHOR_STRING_REGEX_EDITOR )
    AUTHOR_STRING_IN_HOUSE_REGEX_LIST.append( AUTHOR_STRING_REGEX_BUREAU )
    AUTHOR_STRING_IN_HOUSE_REGEX_LIST.append( AUTHOR_STRING_REGEX_SPECIAL )
    
    # compile individual values.
    AUTHOR_STRING_COMPILED_REGEX_BASE = re.compile( AUTHOR_STRING_REGEX_BASE, re.IGNORECASE )
    #AUTHOR_STRING_COMPILED_REGEX_EDITOR = re.compile( AUTHOR_STRING_REGEX_EDITOR, re.IGNORECASE )
    AUTHOR_STRING_COMPILED_REGEX_BUREAU = re.compile( AUTHOR_STRING_REGEX_BUREAU, re.IGNORECASE )
    AUTHOR_STRING_COMPILED_REGEX_SPECIAL = re.compile( AUTHOR_STRING_REGEX_SPECIAL, re.IGNORECASE )

    # ! TODO - add in misspellings and errors.
    # ! TODO - build Q from compiled RE.
    #Q_IN_HOUSE_AUTHOR = Q( author_varchar__iregex = r'.*\s*/\s*the\s*detroit\s*news$' ) | Q( author_varchar__iregex = r'.*\s*/\s*detroit\s*news\s*.*\s*bureau$' ) | Q( author_varchar__iregex = r'.*\s*/\s*special\s*to\s*the\s*detroit\s*news$' )
    Q_IN_HOUSE_AUTHOR_STATIC = Q( author_varchar__iregex = AUTHOR_STRING_REGEX_BASE ) | Q( author_varchar__iregex = AUTHOR_STRING_REGEX_BUREAU ) | Q( author_varchar__iregex = AUTHOR_STRING_REGEX_SPECIAL )

    # Try to build Q from list of in-house author_string regular expressions.
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

    # Columns are mixed in with news, you have to filter them out by Columnist
    #     name.
    COLUMNIST_LAURA_BERMAN = "Laura Berman"
    COLUMNIST_DANIEL_HOWES = "Daniel Howes"
    COLUMNIST_NAME_LIST = [ COLUMNIST_LAURA_BERMAN, COLUMNIST_DANIEL_HOWES ]

    # DEBUG
    DEBUG_FLAG = True
    
    # logging
    LOGGER_NAME = "context_text.collectors.newsbank.newspapers.DTNB"
    
    # better anomaly detail
    AUTHOR_ANOMALY_DETAIL_ARTICLE_ID = "article_id"
    AUTHOR_ANOMALY_DETAIL_AUTHOR_STRING = "author_string"
    AUTHOR_ANOMALY_DETAIL_GRAF_1 = "graf_1"
    AUTHOR_ANOMALY_DETAIL_GRAF_2 = "graf_2"
    
    # StatusContainer status tags - capture_author_info()
    STATUS_TAG_AUTHOR_NAME_GRAF_1_MISMATCH = "author_name_graf_1_mismatch"
    STATUS_TAG_GRAF_2_UNKNOWN_AFFILIATION = "graf_2_unknown_affiliation"
    STATUS_TAG_USED_DEFAULT_AFFILIATION = "used_default_affiliation"
    STATUS_TAG_UPDATED_AUTHOR_STRING = "updated_author_string"
    STATUS_TAG_NO_ARTICLE = "no_article"
    STATUS_TAG_AUTHOR_NAME_GRAF_1_AFFILIATION_MISMATCH = "author_name_graf_1_affiliation_mismatch"
    
    # StatusContainer status tags - clean_up_author_info()
    STATUS_TAG_COLLECTIVE_BYLINE = "collective_byline"
    STATUS_TAG_AFFILIATION_IN_AUTHOR_STRING = "affiliation_in_author_string"
    STATUS_TAG_REMOVED_AFFILIATION_STILL_FAILED = "removed_affiliation_still_failed"
    STATUS_TAG_AFFILIATION_NOT_IN_AUTHOR_STRING = "affiliation_not_in_author_string"
    STATUS_TAG_NOT_AFFILIATION_MISSING = "not_affiliation_missing"
    STATUS_TAG_AUTHOR_MATCHES_GRAF_1 = "author_matches_graf_1"
    STATUS_TAG_AUTHOR_MATCHES_GRAF_1_CI = "author_matches_graf_1_ci"
    STATUS_TAG_GRAF_1_STRING_IN_AUTHOR_CI = "graf_1_string_in_author_ci"


    #===========================================================================
    # ! ==> static methods
    #===========================================================================


    #===========================================================================
    # ! ==> class methods
    #===========================================================================

    
    #===========================================================================
    # __init__() method
    #===========================================================================


    def __init__( self ):

        # call parent's __init__()
        super( DTNB, self ).__init__()

        # declare variables - logging
        self.logger_debug_flag = self.DEBUG_FLAG
        self.m_logger_name = self.LOGGER_NAME
        self.set_logger_name( self.LOGGER_NAME )
        self.logger_also_print_flag = True

        # auditing variables.
        self.article_count = 0
        self.article_counter = 0
        self.article_id_list = []
        #self.last_article_processed = None
        
        # init graf 1 author summary info
        self.graf_1_has_name_count = 0
        self.graf_1_has_name_id_list = []
        self.graf_1_has_name_section_list = []
        self.graf_1_no_name_id_list = []
        self.graf_1_no_name_section_list = []
        self.graf_1_no_name_detail_list = []
        self.graf_1_no_name_yes_author_count = 0
        
        # init graf 1 by summary info
        self.graf_1_has_by_count = 0
        self.graf_1_has_by_id_list = []
        self.graf_1_has_by_section_list = []
        self.graf_1_no_by_id_list = []
        self.graf_1_no_by_section_list = []
        self.graf_1_no_by_detail_list = []
        self.graf_1_no_by_yes_author_count = 0
        
        # init graf 2 summary info
        self.graf_2_has_DN_count = 0
        self.graf_2_has_DN_id_list = []
        self.graf_2_has_DN_section_list = []
        self.graf_2_no_DN_id_list = []
        self.graf_2_no_DN_section_list = []
        self.graf_2_no_DN_detail_list = []
        
        # audit case of author's name different in database, body of article.
        self.case_mismatch_article_list = []
        self.case_mismatch_count = 0

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

    
    def analyze_author_info( self, article_qs_IN, *args, **kwargs ):
        
        # declare variables
        me = "analyze_author_info"
        debug_string = ""
        article_qs = None
        newspaper_instance = None
        current_article = None
        
        # declare variables - processing a given article
        current_article_id = -1
        section_string = ""
        author_string = ""
        author_string_lower = ""
        
        # declare variables - examining existing author string
        author_part_list = []
        author_part = None
        author_part_count = -1
        author_part_counter = -1
        author_name = ""
        author_affiliation = ""
        author_info = None
        author_name_string = ""
        is_collective_byline = False
        affiliation_list = ""
        
        # declare variables - finding author in text
        find_string = ""
        article_text = None
        find_string = ""
        author_FIT_values = None
        author_FIT_status = None
        author_FIT_status_count = -1
        is_author_in_article = False
        plain_text_index_list = None
        plain_text_match_count = -1
        ignore_case_match_list = None
        ignore_case_match_count = -1

        # declare variables - look in paragraphs
        paragraph_list = []
        graf_1 = ""
        graf_1_lower = ""
        graf_2 = ""
        graf_2_lower = ""
        
        # declare variables - better anomaly tracking.
        error_detail_dict = {}
        
        # reset analysis variables
        self.reset_analysis_variables()
        
        # got a QuerySet?
        if ( article_qs_IN is not None ):
        
            # use it.
            article_qs = article_qs_IN
            
        else:
        
            # no - all Detroit News articles!
            newspaper_instance = Newspaper.objects.filter( newsbank_code = self.NEWSBANK_PLACE_CODE )
            article_qs = Article.objects.filter( newspaper = newspaper_instance )
            
        #-- END check to see if QuerySet passed in. --#
        
        # get article count
        self.article_count = article_qs.count()
                        
        # ! LOOP over articles
        for current_article in article_qs:
        
            self.article_counter = self.article_counter + 1
        
            # output article.
            print( "\nArticle " + str( self.article_counter ) + " of " + str( self.article_count ) + ": " + str( current_article ) + "\n" )
            
            # store off article data
            current_article_id = current_article.id
            author_string = current_article.author_string
            author_string_lower = author_string.lower()
            section_string = current_article.section
            
            # set up search
            find_string = author_string
            
            # get article text for article.
            article_text = current_article.article_text_set.get()
            
            # retrieve first two paragraphs
            paragraph_list = article_text.get_paragraph_list()
            
            # get and output paragraphs 1 and 2:
            graf_1 = paragraph_list[ 0 ]
            graf_1_lower = graf_1.lower()
            graf_2 = paragraph_list[ 1 ]
            graf_2_lower = graf_2.lower()
        
            # ! look for author name in article - FIT
        
            # first, is there an author string.
            if ( ( author_string is not None ) and ( author_string != "" ) ):
            
                # ! investigate value in author_string
                
                # contains "detroit news"?
                if ( self.STRING_PAPER_NAME_LOWER in author_string_lower ):
                
                    # already has paper name in it.  Is there a slash?
                    if ( "/" in author_string_lower ):
                    
                        # there is a slash - already processed? split on slash.
                        author_part_list = author_string_lower.split( "/" )
                        
                        # which part is the paper name in?
                        author_part_count = len( author_part_list )
                        author_part_counter = 0
                        for author_part in author_part_list:
                        
                            # increment counter
                            author_part_counter += 1
                            
                            # see if paper name is in this part.
                            if ( self.STRING_PAPER_NAME_LOWER in author_part ):
                            
                                # it is.
                                debug_string = "Affiliation \"" + author_part + "\" found in author part " + str( author_part_counter ) + " of " + str( author_part_count )
                                self.output_debug_message( debug_string, me )
                                
                            #-- END check to see if affiliation in author string --#
                            
                        #-- END loop over author parts. --#
                        
                    # how about semi-colon?
                    elif ( ";" in author_string_lower ):

                        # there is a slash - already processed? split on slash.
                        author_part_list = author_string_lower.split( "/" )
                        
                        # which part is the paper name in?
                        author_part_count = len( author_part_list )
                        author_part_counter = 0
                        for author_part in author_part_list:
                        
                            # increment counter
                            author_part_counter += 1
                            
                            # see if paper name is in this part.
                            if ( self.STRING_PAPER_NAME_LOWER in author_part ):
                            
                                # it is.
                                debug_string = "Affiliation \"" + author_part + "\" found in author part " + str( author_part_counter ) + " of " + str( author_part_count )
                                self.output_debug_message( debug_string, me )
                                
                            #-- END check to see if affiliation in author string --#
                            
                        #-- END loop over author parts. --#
                        
                    else:
                    
                        # no known delimiter.  Look for author name in 1st graf,
                        #     see if it is present in the author_string...
                        author_info = ArticleCoder.parse_author_string( graf_1 )

                        # got anything back?
                        if ( ( author_info is not None ) and (  ArticleCoder.AUTHOR_INFO_AUTHOR_NAME_STRING in author_info ) ):

                            # retrieve author_name_string
                            author_name_string = author_info[ ArticleCoder.AUTHOR_INFO_AUTHOR_NAME_STRING ]

                            # check if the name retrieved from first paragraph
                            #     is the same as the author_string.
                            if ( author_name_string.lower() in author_string_lower ):
                            
                                # it is there - use author_name_string
                                debug_string = "Author name from graf 1 ( \"" + author_name_string + "\" ) present in author_string ( \"" + author_string + "\" )"
                                self.output_debug_message( debug_string, me )
                            
                            #-- END check to see if graf 1 name is in author_string --#
                            
                        #-- END check to see if author name string in author info --#
                        
                        # ...and then, look for known affiliations in the author
                        #     string.
                        affiliation_list = self.find_affiliation_in_string( author_string, return_all_matches_IN = True )
                        if ( ( affiliation_list is not None ) and ( len( affiliation_list ) > 0 ) ):
                        
                            # first item is the affiliation
                            author_affiliation = affiliation_list[ 0 ]
                            debug_string = "Found affiliation ( \"" + author_affiliation + "\" ) in author string ( \"" + author_string + "\" ) - affiliation list: " + str( affiliation_list )
                            self.output_debug_message( debug_string, me )
                            
                            # ! now, if no name string, try removing affiliation,
                            #     then parsing as name string, and see if
                            #     any characters left.  If so, can call this the
                            #     name...

                        #-- END check to see if known affiliation is in author string --#
                        
                    #-- END check to see if we can figure out name string, affiliation. --#
                
                #-- END check to see if paper name is in author string --#
            
                # ! look for author name in text.
            
                # check to make sure the author name is in the text!
                author_FIT_values = article_text.find_in_text( find_string )
                
                print( "====> Used Article_Text.find_in_text() to looking for author name ( \"" + find_string + "\" ): " + str( author_FIT_values ) )
            
                # anything at all returned?  None = no value passed in...
                if ( author_FIT_values is not None ):
                
                    # get status count.
                    author_FIT_status = Article_Text.validate_FIT_results( author_FIT_values )
                    author_FIT_status_count = len( author_FIT_status )
                
                    # found it?
                    if ( author_FIT_status_count == 0 ):
                        
                        # yes - one match.
                        is_author_in_article = True
                        
                    else:
                
                        # statuses.  Start with plain text list and see if 0 or more than 1
                        #     matches.
                        plain_text_index_list = author_FIT_values.get( Article_Text.FIT_TEXT_INDEX_LIST, [] )
                        plain_text_match_count = len( plain_text_index_list )
                        
                        # how many matches?
                        if ( plain_text_match_count > 0 ):
                        
                            # one or more.
                            is_author_in_article = True
                            
                        elif ( plain_text_match_count == 0 ):
                        
                            # no matches.
                            is_author_in_article = False
                            
                        else:
                        
                            # not sure what is going on, but no matches.
                            is_author_in_article = False
                        
                        #-- END check to see how many plain text matches --#
                        
                        # sanity check - if 0, try to find the name converted to lower case in
                        #     the article, all converted to lower case.
                        if ( is_author_in_article == False ):
                        
                            # Do a search that ignores case.
                            ignore_case_match_list = article_text.find_in_plain_text( find_string, ignore_case_IN = True )
                            ignore_case_match_count = len( ignore_case_match_list )
                            
                            # any matches?
                            if ( ignore_case_match_count > 0 ):
                            
                                # yes - there is a case problem.
                                is_author_in_article = True
                                
                                # case mismatch - should log or record this.
                                self.case_mismatch_article_list.append( current_article )
                                self.case_mismatch_count += 1
                                
                            else:
                            
                                # no match ignoring case - looks like no match (or spelling
                                #     problem, which we can't do anything about for now).
                                is_author_in_article = False
                            
                            #-- END check to see if the name is there, but case is different.
                            
                        #-- END sanity check to see if there is a problem with case --#
                        
                    #-- END evaluation of attempt to find author's name in article. --#
                    
                else:
                
                    # FIT returned None.  No value passed in?
                    is_author_in_article = False
                    print( "========> call to FIT for author name \"" + str( author_string ) + "\" returned None.  Not sure how we got here." )
                
                #-- END check to see if FIT returned None. --#
                
            else:
            
                # no author string, so not in article.
                is_author_in_article = False
                print( "====> No author name ( \"" + str( author_string ) + "\" ), so skipping call to FIT." )
                
            #-- END check to see if author name present. --#
            
            # ! is author name in text?
            if ( is_author_in_article == True ):
            
                print( "====> Paragraph 1: " + graf_1 )
                
                # Does graf_1 contain author's name
                if ( author_string.lower() in graf_1_lower ):
                
                    # yes it does.  Increment counter
                    self.graf_1_has_name_count += 1
            
                    # store article ID
                    self.graf_1_has_name_id_list.append( current_article_id )
            
                    # add section to list.
                    if ( section_string not in self.graf_1_has_name_section_list ):
                    
                        # not there yet - add it.
                        self.graf_1_has_name_section_list.append( section_string )
                    
                    #-- END check to see if section already in list. --#
                    
                    print( "========> Paragraph 1 contains name \"" + str( author_string ) + "\"!" )
            
                else:
                
                    # no name in graf 1 - store article ID
                    self.graf_1_no_name_id_list.append( current_article_id )
            
                    # add section to list.
                    if ( section_string not in self.graf_1_no_name_section_list ):
                    
                        # not there yet - add it.
                        self.graf_1_no_name_section_list.append( section_string )
                    
                    #-- END check to see if section already in list. --#
                    
                    # build dict of author_string, graf 1, and graf 2.
                    error_detail_dict = {}
                    error_detail_dict[ self.AUTHOR_ANOMALY_DETAIL_ARTICLE_ID ] = current_article_id
                    error_detail_dict[ self.AUTHOR_ANOMALY_DETAIL_AUTHOR_STRING ] = author_string
                    error_detail_dict[ self.AUTHOR_ANOMALY_DETAIL_GRAF_1 ] = graf_1
                    error_detail_dict[ self.AUTHOR_ANOMALY_DETAIL_GRAF_2 ] = graf_2
                    
                    # append it to the list.
                    self.graf_1_no_name_detail_list.append( error_detail_dict )
                        
                #-- END check to see if contains author name. --#
            
                # Does graf_1 contain the word "by"
                if ( "by" in graf_1_lower ):
                
                    # yes it does.  Increment counter
                    self.graf_1_has_by_count += 1
            
                    # store article ID
                    self.graf_1_has_by_id_list.append( current_article_id )
            
                    # add section to list.
                    if ( section_string not in self.graf_1_has_by_section_list ):
                    
                        # not there yet - add it.
                        self.graf_1_has_by_section_list.append( section_string )
                    
                    #-- END check to see if section already in list. --#
                    
                    print( "========> Paragraph 1 contains \"by\"!" )
            
                else:
                
                    # no "by" in graf 1 - store article ID
                    self.graf_1_no_by_id_list.append( current_article_id )
            
                    # add section to list.
                    if ( section_string not in self.graf_1_no_by_section_list ):
                    
                        # not there yet - add it.
                        self.graf_1_no_by_section_list.append( section_string )
                    
                    #-- END check to see if section already in list. --#
                    
                    # build dict of author_string, graf 1, and graf 2.
                    error_detail_dict = {}
                    error_detail_dict[ self.AUTHOR_ANOMALY_DETAIL_ARTICLE_ID ] = current_article_id
                    error_detail_dict[ self.AUTHOR_ANOMALY_DETAIL_AUTHOR_STRING ] = author_string
                    error_detail_dict[ self.AUTHOR_ANOMALY_DETAIL_GRAF_1 ] = graf_1
                    error_detail_dict[ self.AUTHOR_ANOMALY_DETAIL_GRAF_2 ] = graf_2
                    
                    # not there yet - add it.
                    self.graf_1_no_by_detail_list.append( error_detail_dict )
                        
                    # Even though no "by", is name here?
                    if ( author_string.lower() in graf_1_lower ):
                    
                        # yup.  Make a note.
                        self.graf_1_no_by_yes_author_count += 1
                        
                    #-- END check to see if name is there even though "by" is not --#
                    
                #-- END check to see if contains "by".
            
                print( "====> Paragraph 2: " + graf_2 )
                
                # Does graf_2 contain the words "Detroit News"
                if ( self.STRING_PAPER_NAME_LOWER in graf_2_lower ):
                
                    # yes it does.  Increment counter
                    self.graf_2_has_DN_count += 1
                    
                    # store article ID
                    self.graf_2_has_DN_id_list.append( current_article_id )
            
                    # add section to list.
                    if ( section_string not in self.graf_2_has_DN_section_list ):
                    
                        # not there yet - add it.
                        self.graf_2_has_DN_section_list.append( section_string )
                    
                    #-- END check to see if section already in list. --#
                    
                    print( "========> Paragraph 2 contains \"" + self.STRING_PAPER_NAME_LOWER + "\"!" )
            
                else:
                
                    # no "detroit news" in graf 2 - store article ID
                    self.graf_2_no_DN_id_list.append( current_article_id )
            
                    # add section to list.
                    if ( section_string not in self.graf_2_no_DN_section_list ):
                    
                        # not there yet - add it.
                        self.graf_2_no_DN_section_list.append( section_string )
                    
                    #-- END check to see if section already in list. --#
                    
                    # build dict of author_string, graf 1, and graf 2.
                    error_detail_dict = {}
                    error_detail_dict[ self.AUTHOR_ANOMALY_DETAIL_ARTICLE_ID ] = current_article_id
                    error_detail_dict[ self.AUTHOR_ANOMALY_DETAIL_AUTHOR_STRING ] = author_string
                    error_detail_dict[ self.AUTHOR_ANOMALY_DETAIL_GRAF_1 ] = graf_1
                    error_detail_dict[ self.AUTHOR_ANOMALY_DETAIL_GRAF_2 ] = graf_2
                    
                    # not there yet - add it.
                    self.graf_2_no_DN_detail_list.append( error_detail_dict )
                        
                #-- END check to see if contains "detroit news".
                
            else:
            
                # author name not in article.
                print( "====> author name ( \"" + find_string + "\" ) not in article." )
        
            #-- END check to see if author name is in the article. --#
            
            # add IDs to article_id_list
            self.article_id_list.append( str( current_article.id ) )
            
            # output the tags.
            print( "====> Tags for article " + str( current_article.id ) + " : " + str( current_article.tags.all() ) )
           
        #-- END loop over articles. --#
        
    #-- END method analyze_author_info() --#


    def capture_author_info( self,
                             article_IN,
                             save_changes_IN = True,
                             require_affiliation_IN = True,
                             default_affiliation_IN = None,
                             *args,
                             **kwargs ):
                                    
        '''
        Accepts Detroit News Article pulled in from Newsbank, then tries to
            capture more detailed author information from the article's first
            two paragraphs.
            
        Basic pattern for Detroit News is that the author_string field has just
            name of the reporter, and then reporter's name and their affiliation
            are in the body of the article in the first (name) and second
            (affiliation) paragraphs.
            
        This method checks to make sure this is the case.  Returns an intance of
            StatusContainer with status_code set to "success" if OK, "error" if
            it finds anything unexpected.  Also includes a list of status tags
            and status messages that capture the details of processing.
            
            Possible tags:
            - self.STATUS_TAG_AUTHOR_NAME_GRAF_1_MISMATCH - added if author name is not the same in author_string and graf 1.
            - self.STATUS_TAG_GRAF_2_UNKNOWN_AFFILIATION - could not find a known affiliation in paragraph 2.
            - self.STATUS_TAG_USED_DEFAULT_AFFILIATION - applied default affiliation since no affiliation found.
            - self.STATUS_TAG_UPDATED_AUTHOR_STRING - processing resulted in an updated author_string.
            - self.STATUS_TAG_NO_ARTICLE - no article passed in.  Self-inflicted wound.
            
        Postconditions:
            - success: This method updates article and article text if it thinks
                it understands what is going on in the article and returns no
                status messages in list.  Updates if standard pattern
                encountered:
                - if author name detected, place it in author_name
                - if author affiliation detected, place it in author_affiliation
                - place combined author and affiliation string, separated by a "/", in both author_string and author_varchar.
                - update the cleanup_status field to "author_fixed".
                - remove paragraphs from beginning of article text that contain author and/or affiliation
            
            - error: If it gets confused, this method will capture its confusion
                in status messages, set cleanup_status to "author_error",
                store status messages in an Article_Notes instance, make no 
                other changes, and return.
        '''
        
        # return reference
        status_OUT = StatusContainer()
        
        # declare variables
        me = "capture_author_info"
        debug_message = ""
        status_message = ""
        
        # declare variables - variables to hold final values for article
        my_author_name = ""
        my_author_affiliation = ""
        my_author_string = ""
        original_author_string = ""
        
        # declare variables - process control
        notes_message = ""
        notes_list = []
        grafs_to_delete_list = []
        is_affiliation_required = False
        default_affiliation = ""
        
        # declare variables - article data
        current_article_id = -1
        author_string = ""
        author_string_lower = ""
        section_string = ""
        cleanup_status = ""
        find_string = ""
        article_text = None
        paragraph_list = None
        graf_1 = ""
        graf_1_lower = ""
        graf_2 = ""
        graf_2_lower = ""
        
        # declare variables - comparing author_string to graf 1
        graf_1_author_info = {}
        graf_1_as_author_string = ""
        author_string_affiliation = ""
        author_string_work = ""
        graf_1_affiliation = ""
        graf_1_work = ""
        graf_2_affiliation = ""
        
        # declare variables - graf 2 - affiliation
        affiliation_value = ""
        contains_paper_name = False
        
        # init status
        status_OUT.status_code = StatusContainer.STATUS_CODE_SUCCESS
        status_OUT.process_name = me

        # first, check to make sure we have an article.
        if ( article_IN is not None ):
        
            # got one. store reference in arbitrary variable name (code used to
            #     be in a loop).
            current_article = article_IN
        
            # log article info.
            debug_message = "Cleaning up author info for article: " + str( current_article )
            self.output_debug_message( debug_message, me )

            # ! retrieve article data
            current_article_id = current_article.id
            author_string = current_article.author_string
            original_author_string = author_string
            author_string_lower = author_string.lower()
            section_string = current_article.section
            cleanup_status = current_article.cleanup_status
            
            # first, see if author info has already been captured.
            if ( cleanup_status not in self.AUTHOR_INFO_CLEANUP_STATUS_ABORT_LIST ):
            
                #--------------------------------------------------------------#
                # ! ==> cleanup setup
                #--------------------------------------------------------------#
                
                # require affiliation?
                is_affiliation_required = require_affiliation_IN

                # set up search
                find_string = author_string
                
                # get article text for article.
                article_text = current_article.article_text_set.get()
                
                # retrieve first two paragraphs
                paragraph_list = article_text.get_paragraph_list()
                
                # get and output paragraphs 1 and 2:
                graf_1 = paragraph_list[ 0 ]
                graf_1_lower = graf_1.lower()
                graf_2 = paragraph_list[ 1 ]
                graf_2_lower = graf_2.lower()
                
                # check whether author_string, graf_1, and graf_2 contain
                #     affiliation (we'll use it on down).
                author_string_affiliation = self.find_affiliation_in_string( author_string )
                graf_1_affiliation = self.find_affiliation_in_string( graf_1 )
                graf_2_affiliation = self.find_affiliation_in_string( graf_2 )
                
                #--------------------------------------------------------------#
                # ! ==> author name (graf 1)
                #--------------------------------------------------------------#
                
                # first, parse contents of graf 1 to get rid of "By"
                graf_1_author_info = ArticleCoder.parse_author_string( graf_1 )
                graf_1_as_author_string = graf_1_author_info[ ArticleCoder.AUTHOR_INFO_AUTHOR_NAME_STRING ]
                
                # check to see if the author_string is one of those that denote
                #     collective staff authorship.
                
                # make sure there is an author string.
                if ( ( author_string is not None ) and ( author_string != "" ) ):
                    
                    # yes - check it for collective byline.
                    is_collective_byline = self.is_collective_byline( author_string )
                    
                else:
                
                    # no author_string - see if graf 1 is collective byline.
                    #     (sometimes with collective byline, there is no
                    #     author_string, but the author in graf 1 is collective
                    #     byline).
                    is_collective_byline = self.is_collective_byline( graf_1_as_author_string )
                    
                #-- END check to see if collective byline --#
                
                #--------------------------------------------------------------#
                # collective byline?  Might include an affiliation string.
                #--------------------------------------------------------------#
                
                if ( is_collective_byline == True ):
                
                    # ! --> IS collective byline
                    
                    # with collective byline, use the byline as the author name.

                    # is it in author_string...?
                    if ( ( author_string is not None ) and ( author_string != "" ) ):
                        
                        # yes - store it and make note.
                        my_author_name = author_string

                        # make a note.
                        notes_message = "author_string \"" + author_string + "\" is a collective byline, so processing it special - just use the author_string as-is, and don't look at the 2nd paragraph."
                        notes_list.append( notes_message )
    
                    # ...or is it in graf 1?
                    else:
                    
                        # not in author string, so must be in graf 1 - store it
                        #     and make note.
                        my_author_name = graf_1

                        # make a note.
                        notes_message = "graf 1 \"" + graf_1 + "\" is a collective byline, so processing it special - just use graf_1 as author name as-is, and don't look at the 2nd paragraph."
                        notes_list.append( notes_message )
                        
                    #-- END check to see if collective byline --#

                    # ...and there is no affiliation.
                    my_author_affiliation = None
                    
                    # if graf_1_lower = my_author_name.lower(), remove graf 1.
                    if ( graf_1_lower == my_author_name.lower() ):
                    
                        # same - remove graf 1.
                        grafs_to_delete_list.append( 1 )
                        
                        # make a note.
                        notes_message = "my_author_name ( \"" + my_author_name + "\" ) is same as 1st paragraph ( \"" + graf_1 + "\" ), so removing first paragraph."
                        notes_list.append( notes_message )
    
                    #-- END check to see if we remove graf 1. --#
                    
                    # NOTE - don't do anything to graf 2.
                
                else:
                
                    # ! --> NOT collective byline
                    
                    # ! ----> if affiliation present, remove it
                    if ( ( graf_1_affiliation is not None )
                        and ( graf_1_affiliation != "" ) ):
                        
                        # affiliation is present.  Remove it from author string.
                        
                        # Remove graf_1_affiliation from graf_1_as_author_string...
                        graf_1_as_author_string = self.remove_affiliation_from_author_string( graf_1_as_author_string )
    
                    #-- END check to see if graf 1 has affiliation. --#
                    
                    if ( ( author_string_affiliation is not None )
                        and ( author_string_affiliation != "" ) ):
                        
                        # affiliation is present.  Remove it from author string.
                        
                        # Remove author_string_affiliation from author_string...
                        author_string = self.remove_affiliation_from_author_string( author_string )
                        author_string_lower = author_string.lower()
    
                    #-- END check to see if graf 1 has affiliation. --#
                    
                    # ! ----> Did either contain affiliation?
                    if ( ( ( author_string_affiliation is not None ) and ( author_string_affiliation != "" ) )
                        or ( ( graf_1_affiliation is not None ) and ( graf_1_affiliation != "" ) ) ):
                    
                        # Did they both contain affiliation?  Sometimes
                        #     both graf 1 and author_string contain affiliation, and
                        #     no affiliation in paragraph 2.
                        if ( ( author_string_affiliation is not None )
                            and ( author_string_affiliation != "" )
                            and ( graf_1_affiliation is not None )
                            and ( graf_1_affiliation != "" ) ):
                            
                            # They do both have affiliation.
                            notes_message = "Affiliation found in both graf 1 ( \"" + graf_1_affiliation + "\" ) and author_string ( \"" + author_string_affiliation + "\" )."
        
                            # Is it the same affiliation?
                            if ( author_string_affiliation == graf_1_affiliation ):
                            
                                # same affiliation.  Set my_author_affiliation.
                                my_author_affiliation = author_string_affiliation
                                default_affiliation = author_string_affiliation
                                
                                # and no longer need affiliation from 2nd paragraph.
                                is_affiliation_required = False
                                
                                # add detail to note.
                                notes_message += "  Using affiliation retrieved from author_string as default."
                            
                            else:
                            
                                # different affiliations?  ERROR.
                                notes_message += "  BUT, they are different!  ERROR!"
                                
                                # Create message
                                Message.create_message( "In article " + str( current_article_id ) + ": " + notes_message,
                                                        application_IN = self.LOGGER_NAME,
                                                        status_IN = Message.STATUS_ERROR )
                                                        
                                # This is an error.  update status.
                                status_OUT.status_code = StatusContainer.STATUS_CODE_ERROR
                                status_OUT.add_tag( self.STATUS_TAG_AUTHOR_NAME_GRAF_1_AFFILIATION_MISMATCH )
                                status_OUT.add_message( notes_message )
                            
                            #-- END check to see if affiliation 
                            
                            # Store to Article_Notes
                            notes_list.append( notes_message )
                        
                        elif ( ( graf_1_affiliation is not None )
                            and ( graf_1_affiliation != "" ) ):
                            
                            # affiliation in graf 1.  Use it.
                            my_author_affiliation = graf_1_affiliation
                            default_affiliation = graf_1_affiliation
                            
                            # and no longer need affiliation from 2nd paragraph.
                            is_affiliation_required = False
                            
                            # add detail to note.
                            notes_message = "Using affiliation retrieved from graf 1 ( \"" + graf_1_affiliation + "\" ) as default."
                            
                            # Store to Article_Notes
                            notes_list.append( notes_message )
        
                        elif ( ( author_string_affiliation is not None )
                            and ( author_string_affiliation != "" ) ):
                            
                            # affiliation in author_string.  Use it.
                            my_author_affiliation = author_string_affiliation
                            default_affiliation = author_string_affiliation
                            
                            # and no longer need affiliation from 2nd paragraph.
                            is_affiliation_required = False
                            
                            # add detail to note.
                            notes_message = "Using affiliation retrieved from author_string ( \"" + author_string_affiliation + "\" ) as default."
            
                            # Store to Article_Notes
                            notes_list.append( notes_message )
    
                        #-- END check to see if both graf 1 and author_string had affiliation --#
    
                    #-- END check to see if affiliation found in author_string or graf 1 --#
    
                    # now that we've cleaned out affiliations, check again to
                    #     see if the author_string is one of those that
                    #     denote collective staff authorship.
                    is_collective_byline = self.is_collective_byline( author_string )
                    
                    # ! ----> do author_string and graf 1 match?
                    
                    if ( ( ( author_string_lower is not None ) and ( author_string_lower != "" ) )
                        and ( ( graf_1_as_author_string is not None ) and ( graf_1_as_author_string ) ) ):
                        
                        # check to see if author_string matches graf_1, ignoring
                        #      case (it should).
                        if ( author_string_lower == graf_1_as_author_string.lower() ):
                    
                            # it does.
                            
                            # use author name from author string.
                            my_author_name = author_string
                            
                            # ...and we want to remove the first paragraph...
                            grafs_to_delete_list.append( 1 )
                            
                            # ...and make a note.
                            notes_message = "Removing graf 1 - author_string ( \"" + author_string + "\" ) same as name in graf 1 ( \"" + graf_1_as_author_string + "\" )."
                            notes_list.append( notes_message )                    
                            
                        else:
                        
                            # it does not.  ERROR.
                            notes_message = "ERROR - original author_string ( \"" + author_string + "\" ) not the same as name in graf 1 ( \"" + graf_1_as_author_string + "\" ).  graf 1 contents = \"" + graf_1 + "\"."
                            notes_list.append( notes_message )
        
                            # Create message
                            Message.create_message( "In article " + str( current_article_id ) + ": " + notes_message,
                                                    application_IN = self.LOGGER_NAME,
                                                    status_IN = Message.STATUS_ERROR )
                        
                            # and add that to the status list.
                            status_OUT.status_code = StatusContainer.STATUS_CODE_ERROR
                            status_OUT.add_tag( self.STATUS_TAG_AUTHOR_NAME_GRAF_1_MISMATCH )
                            status_OUT.add_message( notes_message )
                            
                            # see if the string from graf 1 is "in" author_string
                            if ( graf_1_as_author_string.lower() in author_string_lower ):
                            
                                # graf 1 string is in author_string - odd.  ERROR.
                                notes_message = "ERROR - name in graf 1 ( \"" + graf_1_as_author_string + "\" ) is in author_string ( \"" + author_string + "\" ), but they are not the same.  graf 1 contents = \"" + graf_1 + "\"."
                                notes_list.append( notes_message )
            
                                # Create message
                                Message.create_message( "In article " + str( current_article_id ) + ": " + notes_message,
                                                        application_IN = self.LOGGER_NAME,
                                                        status_IN = Message.STATUS_ERROR )
                            
                                # and add that to the status list.
                                status_OUT.status_code = StatusContainer.STATUS_CODE_ERROR
                                status_OUT.add_tag( self.STATUS_TAG_GRAF_1_STRING_IN_AUTHOR_CI )
                                status_OUT.add_message( notes_message )
                            
                            #-- END check to see if graf 1 is just name. --#
        
                        #-- END check to see if graf 1 = author_string --#
                        
                    else:
                    
                        # one or the other or both author strings are missing.
                        #     Error.
                        notes_message = "ERROR - either graf 1 ( \"" + graf_1_as_author_string + "\" ) or author_string ( \"" + author_string_lower + "\" ) is empty (or both are empty).  This should not happen."
                        notes_list.append( notes_message )
    
                        # Create message
                        Message.create_message( "In article " + str( current_article_id ) + ": " + notes_message,
                                                application_IN = self.LOGGER_NAME,
                                                status_IN = Message.STATUS_ERROR )
                    
                        # and add that to the status list.
                        status_OUT.status_code = StatusContainer.STATUS_CODE_ERROR
                        status_OUT.add_tag( self.STATUS_TAG_GRAF_1_STRING_IN_AUTHOR_CI )
                        status_OUT.add_message( notes_message )
                        
                    #-- END check to see if both author_string and graf 1 are not empty --# 
                    
                    # ! ==> author affiliation (graf 2)
                    
                    # first, check if collective byline.  If so, no affiliation,
                    #     ignore graf 2.
                    if ( is_collective_byline == False ):
                    
                        # check to see if the contents of graph 2 contain a known
                        #     affiliation, or if it at least contains "detroit news".
                        affiliation_value = self.find_affiliation_in_string( graf_2 )
                        contains_paper_name = self.STRING_PAPER_NAME_LOWER in graf_2_lower
                        
                        # Was an affiliation found?
                        if ( ( affiliation_value is not None ) and ( affiliation_value != "" ) ):
                        
                            # found an affiliation.  Is it the entire contents
                            #     of graf 2?
                            if ( affiliation_value.lower() == graf_2_lower ):

                                # yes again - looks like an affiliation.  use it.
                                my_author_affiliation = graf_2
                
                                # ...and we want to remove the second paragraph...
                                grafs_to_delete_list.append( 2 )
                                
                                # ...and make a note.
                                notes_message = "Removing graf 2 - graf 2 ( contents = \"" + graf_2 + "\" ) contains a known affiliation ( affiliation_value = \"" + str( affiliation_value ) + "\" ) and nothing else.  Affiliation assigned to author."
                                notes_list.append( notes_message )
                                
                            else:
                            
                                # affiliation is not the entire contents of graf
                                #     2.  Could be a mention in a larger
                                #     paragraph.  Because of this, err on the
                                #     side of caution.
                                notes_message = "graf 2 ( contents = \"" + graf_2 + "\" ) contains a known affiliation ( affiliation_value = \"" + str( affiliation_value ) + "\" ), but also has other text.  In case it is part of a sentence, not using graf 2 as the affiliation."
                                notes_list.append( notes_message )                                
                                
                            #-- END check to see if affiliation is graf 2 --#
                            
                        else:
                        
                            # note that no affiliation found in graf 2.
                            notes_message = "graf 2 ( contents = \"" + graf_2 + "\" ) does not contain a known affiliation.  If it does contain paper name \"" + self.STRING_PAPER_NAME_LOWER + "\" ( contains_paper_name = \"" + str( contains_paper_name ) + "\" ), this could be an indicator of an affiliation variation we haven't encountered yet, or it could be that the affiliation string was in a sentence.  Since the 2nd is a possibilty, we err on the side of caution and don't use graf 2 as affiliation."
                            notes_list.append( notes_message )
                            
                        #-- END check to see if affiliation found in graf 2 --#
                                
                        # got an affiliation?
                        if ( ( my_author_affiliation is None ) or ( my_author_affiliation == "" ) ):
                        
                            # no.  ERROR.
                            notes_message = "WARNING - graf_2 ( contents = \"" + graf_2 + "\"; contains paper name \"" + self.STRING_PAPER_NAME_LOWER + "\"?: " + str( contains_paper_name ) + " ) does not contain a known affiliation.  This might not be an error, but it is non-standard."
                            
                            # do we require an affiliation?
                            if ( is_affiliation_required == True ):
                            
                                # Create message
                                Message.create_message( notes_message,
                                                        application_IN = self.LOGGER_NAME,
                                                        status_IN = Message.STATUS_ERROR )
                            
                                # and update the status container (doesn't update other
                                #     than to set cleanup_status to an error status).
                                status_OUT.status_code = StatusContainer.STATUS_CODE_ERROR
                                status_OUT.add_tag( self.STATUS_TAG_GRAF_2_UNKNOWN_AFFILIATION )
                                status_OUT.add_message( notes_message )
                                
                            else:
                            
                                # is there a default?
                                if ( ( default_affiliation is not None ) and ( default_affiliation != "" ) ):
                                
                                    # there is.  Use that.
                                    my_author_affiliation = default_affiliation
                                
                                    # and update the status container with a tag and
                                    #     message.
                                    notes_message += "  Using default affiliation of " + default_affiliation + "."
                                    status_OUT.add_tag( self.STATUS_TAG_USED_DEFAULT_AFFILIATION )
                                    status_OUT.add_message( notes_message )
        
                                #-- END check to see if default.
                            
                            #-- END check to see if we save if no affiliation --#
                            
                            # add the notes message.
                            notes_list.append( notes_message )
        
                        #-- END check to see if graf 2 looks like an affiliation --#
                        
                    else:
                    
                        # add a note to explain.
                        notes_message = "cleaned author_string contained a collective byline ( \"" + author_string + "\" ), so no need to process paragraph 2 or set an author_affiliation."
                        notes_list.append( notes_message )
                    
                    #-- END check to see if collective byline --#

                #-- END check to see if collective byline --#
                    
                # ! update article
                
                # do we update Article (if status messages, then error)?
                if ( status_OUT.is_success() == True ):
                
                    # yes.  store author name and affiliation in article.
                    current_article.set_author_name( my_author_name, do_rebuild_IN = False )
                    current_article.set_author_affiliation( my_author_affiliation, do_rebuild_IN = False )

                    # rebuild author_string and author_varchar.
                    my_author_string = current_article.rebuild_author_string()
                    
                    # did this change anything?
                    if ( my_author_string != original_author_string ):
                    
                        # yes.  Add a note.
                        notes_message = "Updated author_string from \"" + original_author_string + "\" to \"" + my_author_string + "\"."
                        notes_list.append( notes_message )
                        
                        # And add to status info.
                        status_OUT.add_tag( self.STATUS_TAG_UPDATED_AUTHOR_STRING )
                        status_OUT.add_message( notes_message )

                    #-- END check to see if we updated author_string. --#
                    
                    # ...set status to "author_fixed"...
                    current_article.cleanup_status = Article.CLEANUP_STATUS_AUTHOR_FIXED
    
                    # ...save() changes to database?...
                    if ( save_changes_IN == True ):
                    
                        # save.
                        current_article.save()
                        
                    #-- END check to see if we save --#
                    
                    # ...and remove paragraphs from Article_Text?
                    if ( ( grafs_to_delete_list is not None ) and ( len( grafs_to_delete_list ) > 0 ) ):
                        
                        # remove paragraphs...
                        article_text.remove_paragraphs( grafs_to_delete_list )
                        
                        # ...and save() changes to database?
                        if ( save_changes_IN == True ):
                    
                            # save.
                            article_text.save()
                        
                        #-- END check to see if we save --#
                        
                    #-- END check to see if paragraphs flagged for removal. --#

                else:
                
                    # error.  update status on article...
                    current_article.cleanup_status = Article.CLEANUP_STATUS_AUTHOR_ERROR
                    
                    # ...and save() changes to database?
                    if ( save_changes_IN == True ):

                        # save.
                        current_article.save()
                        
                    #-- END check to see if we save --#
                    
                #-- END check to see if we update the article. --#
                
                # got any notes?
                if ( ( notes_list is not None ) and ( len( notes_list ) > 0 ) ):
                
                    # yes.  Add a note.
                    note_string = "\n- ".join( notes_list )
                    note_string = "- " + note_string
                    
                    debug_string = "====> Notes:\n" + note_string
                    self.output_debug_message( debug_string, me )

                    # are we saving changes?
                    if ( save_changes_IN == True ):

                        # yes - persist notes to database.
                        current_article.create_notes( text_IN = note_string )
                        
                    #-- END check to see if we are saving changes. --#
                    
                #-- END check to see if we have notes to save. --#
                
            else:
            
                # This article has already been processed.  It won't go well
                #     running this a second time on a given article.
                status_message = "In " + me + ": author information has already been captured."
                status_OUT.status_code = StatusContainer.STATUS_CODE_SUCCESS
                status_OUT.add_message( status_message )
            
            #-- END check to see if already has been captured. --#
                    
        else:
        
            # no article, can't clean.
            status_message = "In " + me + ": no article passed in, so can't clean up author information."
            status_OUT.status_code = StatusContainer.STATUS_CODE_ERROR
            status_OUT.add_tag( self.STATUS_TAG_NO_ARTICLE )
            status_OUT.add_message( status_message )
            
        #-- END check to see if article. --#
        
        return status_OUT
        
    #-- END method capture_author_info() --#
                                

    def clean_up_author_info( self,
                              article_IN,
                              save_changes_IN = True,
                              *args,
                              **kwargs ):
                                    
        '''
        Accepts Detroit News Article pulled in from Newsbank, then tries to
            clean up author string, remove author information from body of
            article, then update the article's database record to reflect actual
            author information.
            
        Basic pattern for Detroit News is that the author_string field has just
            name of the reporter, and then reporter's name and their affiliation
            are in the body of the article in the first (name) and second
            (affiliation) paragraphs.  There are many variations on this:
            
        So, this method aims for the most common case first - name is in author
            string and first paragraph, affiliation is in second paragraph.
            If this breaks down, then this method attempts to figure out which
            of the alternate patterns we have.  If it thinks it understands, it
            will make updates accordingly.  If not, it will set cleanup_status
            to "author_error" and move on.
            
        Postconditions:
            - success: This method updates article and article text if it thinks
                it understands what is going on in the article and returns no
                status messages in list.  Updates if standard pattern
                encountered:
                - if author name detected, place it in author_name
                - if author affiliation detected, place it in author_affiliation
                - place combined author and affiliation string, separated by a "/", in both author_string and author_varchar.
                - update the cleanup_status field to "author_fixed".
                - remove paragraphs from beginning of article text that contain author and/or affiliation
            
            - error: If it gets confused, this method will capture its confusion
                in status messages, set cleanup_status to "author_error",
                store status messages in an Article_Notes instance, make no 
                other changes, and return.
        '''
        
        # return reference
        status_OUT = StatusContainer()
        
        # declare variables
        me = "clean_up_author_info"
        status_message = ""
        capture_status = None
        capture_status_list = []
        
        # declare variables - article data
        cleanup_status = ""
        
        # declare variables - trying to fix non-standard articles
        keep_trying = True
        retry_capture_status = None
        retry_capture_status_list = None
        
        # evaluate if just missing affiliation.
        tag_count = -1
        is_affiliation_missing = False
        valid_affiliation = ""
        is_valid_affiliation = False
        
        # init status
        status_OUT.status_code = StatusContainer.STATUS_CODE_SUCCESS
        status_OUT.process_name = me
        
        # first, check to make sure we have an article.
        if ( article_IN is not None ):
        
            # ! check cleanup_status
            
            # got one. store reference in arbitrary variable name (code used to
            #     be in a loop).
            current_article = article_IN
            cleanup_status = current_article.cleanup_status
            
            # first, see if author info has already been captured.
            if ( cleanup_status not in self.AUTHOR_INFO_CLEANUP_STATUS_ABORT_LIST ):
            
                # log article info.
                debug_message = "Cleaning up author info for article: " + str( current_article )
                self.output_debug_message( debug_message, me )
                
                # ! try capture_author_info()
                
                # first try capture_author_info(), to see if this fits the standard
                #     pattern: graf 1 = name, graf 2 = affiliation.
                capture_status = self.capture_author_info( current_article, save_changes_IN = save_changes_IN )
                capture_status_list = capture_status.get_message_list()

                # store status
                status_OUT.add_status_container( capture_status )
                
                # errors?
                if ( capture_status.is_error() == True ):
    
                    # yes - see if just missing affiliation.
                    tag_count = capture_status.get_tag_count()
                    is_affiliation_missing = capture_status.has_tag( self.STATUS_TAG_GRAF_2_UNKNOWN_AFFILIATION )
                    if ( ( tag_count == 1 ) and ( is_affiliation_missing == True ) ):

                        # missing affiliation.  Try again with default?
                        if ( ( self.default_affiliation is not None ) and ( self.default_affiliation != "" ) ):
                        
                            # make sure the affiliation is valid.
                            valid_affiliation = self.find_affiliation_in_string( self.default_affiliation )
                            if ( ( valid_affiliation is not None ) and ( valid_affiliation != "" ) ):

                                # retry, setting affiliation to default.
                                retry_capture_status = self.capture_author_info( current_article, save_changes_IN = save_changes_IN, require_affiliation_IN = False, default_affiliation_IN = self.NEWSPAPER_NAME )
                        
                                # errors?
                                if ( retry_capture_status.is_error() == True ):
                                
                                    # not just that the affiliation was missing.  Error.
                                    keep_trying = True
                                    
                                else:
                                
                                    # it was missing affiliation.  Set it to default.
                                    keep_trying = False
                                    status_OUT.add_status_container( retry_capture_status )
                                
                                #-- END check to see if problem was affiliation missing --#
                                
                            else:
                            
                                # default affiliation provided is unknown.
                                keep_trying = True
                            
                            #-- END check to see if affiliation is valid --#
                            
                        else:
                        
                            # no default affiliation.  Can't set one.  Error.
                            keep_trying = True
                        
                        #-- END check to see if default affiliation present. --#
                        
                    else:
                    
                        # not just missing affiliation.  Error.
                        keep_trying = True
                    
                    #-- END check to see if just missing affiliation. --#

                else:
                
                    # standard cleanup worked.
                    keep_trying = False
                
                #-- END check to see if standard cleanup worked --#
                
                # set overall status based on keep_trying.
                if ( keep_trying == True ):
                
                    # still problems.  Error.
                    status_message = "In " + me + ": Unable to clean up author data.  Status stored in nested status_container_list.  Look there for more details."
                    status_OUT.status_code = StatusContainer.STATUS_CODE_ERROR
                    status_OUT.add_message( status_message )
                    
                else:
                
                    # Success!
                    status_message = "In " + me + ": Successfully cleaned up author data."
                    status_OUT.status_code = StatusContainer.STATUS_CODE_SUCCESS
                    status_OUT.add_message( status_message )
                    
                #-- END check of overall status. --#
            
            else:
                        
                # This article has already been processed.  It won't go well
                #     running this a second time on a given article.
                status_message = "In " + me + ": author information has already been captured."
                status_OUT.status_code = StatusContainer.STATUS_CODE_SUCCESS
                status_OUT.add_message( status_message )
            
            #-- END check to see if already cleaned up. --#
        
        else:
        
            # no article, can't clean.
            status_message = "In " + me + ": no article passed in, so can't clean up author information."
            status_OUT.status_code = StatusContainer.STATUS_CODE_ERROR
            status_OUT.add_message( status_message )
            
        #-- END check to see if article. --#
        
        return status_OUT
        
    #-- END method clean_up_author_info() --#
                                

    def fix_author_info( self, article_qs_IN, ignore_cleanup_status_IN = False, *args, **kwargs ):
        
        '''
        Accepts QuerySet of articles and optional flag to ignore whether a given
            article has already been cleaned up.  Loops over articles.  If a
            given article has already been cleaned up, skips it.  If not, calls
            class method clean_up_author_info(), passing it the article.
            
        Postconditions: Articles are cleaned up, results are saved.
        '''
        
        # return reference
        status_list_OUT = []
        
        # declare variables.
        me = "fix_author_info"
        status_message = ""
        article_count = -1
        current_article = None
        cleanup_status = ""
        cleanup_status_list = []
        cleanup_status_count = -1
        
        # first, we check to see if we have a QuerySet
        if ( article_qs_IN is not None ):
        
            # yes.  Anything in it?
            article_count = article_qs_IN.count()
            if ( article_count > 0 ):
            
                # loop.
                for current_article in article_qs_IN:
                
                    # check cleanup status
                    cleanup_status = current_article.cleanup_status
                    if ( ( cleanup_status is None )
                        or ( cleanup_status == "" )
                        or ( cleanup_status == Article.CLEANUP_STATUS_NEW )
                        or ( ignore_cleanup_status_IN == True ) ):
                        
                        # process it!
                        cleanup_status_list = self.clean_up_author_info( current_article )
                        
                        # success?
                        cleanup_status_count = len( cleanup_status_list )
                        if ( cleanup_status_count == 0 ):
                        
                            # no messages.  Save.
                            current_article.save()
                            
                        else:
                            
                            # got messages.  Add them to list to return.
                            status_list_OUT.extend( cleanup_status_list )
                            
                        #-- END check to see if error messages. --#
                
                    #-- END check to see if we process article --#
                
                #-- END loop over articles --#
            
            else:
            
                # nothing passed in?
                status_message = "In " + me + ": empty QuerySet passed in, so nothing to do."
                status_list_OUT.append( status_message )
            
            #-- END check to see if anything in QuerySet --#
        
        else:
        
            # nothing passed in?
            status_message = "In " + me + ": no article QuerySet passed in, so can't process."
            status_list_OUT.append( status_message )
        
        #-- END check to see if QuerySet --#
        
        return status_list_OUT
        
    #-- END method fix_author_info() --#


    def reset_analysis_variables( self ):
        
        # clear out article count variables.
        self.article_count = 0
        self.article_counter = 0
        self.article_id_list = []
        
        # init graf 1 author summary info
        self.graf_1_has_name_count = 0
        self.graf_1_has_name_id_list = []
        self.graf_1_has_name_section_list = []
        self.graf_1_no_name_id_list = []
        self.graf_1_no_name_section_list = []
        self.graf_1_no_name_detail_list = []
        self.graf_1_no_name_yes_author_count = 0
        
        # init graf 1 by summary info
        self.graf_1_has_by_count = 0
        self.graf_1_has_by_id_list = []
        self.graf_1_has_by_section_list = []
        self.graf_1_no_by_id_list = []
        self.graf_1_no_by_section_list = []
        self.graf_1_no_by_detail_list = []
        self.graf_1_no_by_yes_author_count = 0
        
        # init graf 2 summary info
        self.graf_2_has_DN_count = 0
        self.graf_2_has_DN_id_list = []
        self.graf_2_has_DN_section_list = []
        self.graf_2_no_DN_id_list = []
        self.graf_2_no_DN_section_list = []
        
        # audit case of author's name different in database, body of article.
        self.case_mismatch_article_list = []
        self.case_mismatch_count = 0

    #-- END method reset_analysis_variables() --#

    
#-- END class DTNB --#