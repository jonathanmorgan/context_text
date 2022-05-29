from __future__ import unicode_literals

'''
Copyright 2010-2016 Jonathan Morgan

This file is part of http://github.com/jonathanmorgan/context_text.

context_text is free software: you can redistribute it and/or modify it under the terms of the GNU Lesser General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.

context_text is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.

You should have received a copy of the GNU Lesser General Public License along with http://github.com/jonathanmorgan/context_text. If not, see http://www.gnu.org/licenses/.
'''

#===============================================================================
# imports (in alphabetical order by package, then by name)
#===============================================================================


# python base imports
import calendar
#from datetime import date
import datetime

# django classes
from django.contrib.auth.models import User
from django.db.models import Q

# python_utilities
from python_utilities.parameters.param_container import ParamContainer
from python_utilities.rate_limited.basic_rate_limited import BasicRateLimited

# context
from context.shared.context_base import ContextBase

#===============================================================================
# classes (in alphabetical order by name)
#===============================================================================

# object --> LoggingHelper --> ExceptionHelper --> BasicRateLimited --> ContextBase --> ContextTextBase
class ContextTextBase( ContextBase ):


    #---------------------------------------------------------------------------
    # ! ==> CONSTANTS-ish
    #---------------------------------------------------------------------------

    # django_config properties - context_text-db-admin application
    DJANGO_CONFIG_APPLICATION_CONTEXT_TEXT_DB_ADMIN = "context_text-db-admin"

    # django_config properties - context_text-UI-article-code application
    DJANGO_CONFIG_APPLICATION_ARTICLE_CODE = "context_text-UI-article-code"
    DJANGO_CONFIG_PROP_ARTICLE_TEXT_RENDER_TYPE = "article_text_render_type"
    DJANGO_CONFIG_PROP_ARTICLE_TEXT_IS_PREFORMATTED = "article_text_is_preformatted"
    DJANGO_CONFIG_PROP_ARTICLE_TEXT_WRAP_IN_P = "article_text_wrap_in_p"

    # django_config property values - article_text_render_type
    DJANGO_CONFIG_PROP_DO_OUTPUT_TABLE_HTML = "do_output_table_html"
    DJANGO_CONFIG_ARTICLE_TEXT_RENDER_TYPE_TABLE = "table"
    DJANGO_CONFIG_ARTICLE_TEXT_RENDER_TYPE_RAW = "raw"
    DJANGO_CONFIG_ARTICLE_TEXT_RENDER_TYPE_CUSTOM = "custom"
    DJANGO_CONFIG_ARTICLE_TEXT_RENDER_TYPE_PDF = "pdf"
    DJANGO_CONFIG_ARTICLE_TEXT_RENDER_TYPE_DEFAULT = DJANGO_CONFIG_ARTICLE_TEXT_RENDER_TYPE_RAW
    DJANGO_CONFIG_ARTICLE_TEXT_RENDER_TYPE_VALUE_LIST = []
    DJANGO_CONFIG_ARTICLE_TEXT_RENDER_TYPE_VALUE_LIST.append( DJANGO_CONFIG_ARTICLE_TEXT_RENDER_TYPE_RAW )
    DJANGO_CONFIG_ARTICLE_TEXT_RENDER_TYPE_VALUE_LIST.append( DJANGO_CONFIG_ARTICLE_TEXT_RENDER_TYPE_TABLE )
    DJANGO_CONFIG_ARTICLE_TEXT_RENDER_TYPE_VALUE_LIST.append( DJANGO_CONFIG_ARTICLE_TEXT_RENDER_TYPE_CUSTOM )
    DJANGO_CONFIG_ARTICLE_TEXT_RENDER_TYPE_VALUE_LIST.append( DJANGO_CONFIG_ARTICLE_TEXT_RENDER_TYPE_PDF )

    # django_config property values - find in text (FIT)
    DJANGO_CONFIG_NAME_INCLUDE_FIND_IN_ARTICLE_TEXT = "include_find_in_article_text"
    DJANGO_CONFIG_NAME_DEFAULT_FIND_LOCATION = "default_find_location"
    DJANGO_CONFIG_NAME_IGNORE_WORD_LIST = "ignore_word_list"
    DJANGO_CONFIG_NAME_HIGHLIGHT_WORD_LIST = "highlight_word_list"
    DJANGO_CONFIG_NAME_BE_CASE_SENSITIVE = "be_case_sensitive"

    # View response dictionary keys
    VIEW_RESPONSE_KEY_PAGE_STATUS_MESSAGE_LIST = "page_status_message_list"
    VIEW_RESPONSE_KEY_ARTICLE_INSTANCE = "article_instance"
    VIEW_RESPONSE_KEY_ARTICLE_TEXT = "article_text"
    VIEW_RESPONSE_KEY_ARTICLE_CONTENT = "article_content"
    VIEW_RESPONSE_KEY_ARTICLE_TEXT_CUSTOM = "article_text_custom"
    VIEW_RESPONSE_KEY_ARTICLE_TEXT_TYPE = "article_text_type"

    # View response dictionary keys - article text
    VIEW_RESPONSE_KEY_ARTICLE_TEXT_RENDER_TYPE = DJANGO_CONFIG_PROP_ARTICLE_TEXT_RENDER_TYPE
    VIEW_RESPONSE_KEY_ARTICLE_TEXT_IS_PREFORMATTED = DJANGO_CONFIG_PROP_ARTICLE_TEXT_IS_PREFORMATTED
    VIEW_RESPONSE_KEY_ARTICLE_TEXT_WRAP_IN_P = DJANGO_CONFIG_PROP_ARTICLE_TEXT_WRAP_IN_P
    VIEW_RESPONSE_KEY_DO_OUTPUT_TABLE_HTML = DJANGO_CONFIG_PROP_DO_OUTPUT_TABLE_HTML

    # View response dictionary keys - find in text (FIT)
    VIEW_RESPONSE_KEY_INCLUDE_FIND_IN_ARTICLE_TEXT = DJANGO_CONFIG_NAME_INCLUDE_FIND_IN_ARTICLE_TEXT
    VIEW_RESPONSE_KEY_DEFAULT_FIND_LOCATION = DJANGO_CONFIG_NAME_DEFAULT_FIND_LOCATION
    VIEW_RESPONSE_KEY_IGNORE_WORD_LIST = DJANGO_CONFIG_NAME_IGNORE_WORD_LIST
    VIEW_RESPONSE_KEY_HIGHLIGHT_WORD_LIST = DJANGO_CONFIG_NAME_HIGHLIGHT_WORD_LIST
    VIEW_RESPONSE_KEY_BE_CASE_SENSITIVE = DJANGO_CONFIG_NAME_BE_CASE_SENSITIVE

    # View HTML INPUT IDs.
    INPUT_ID_TEXT_TO_FIND_IN_ARTICLE = "text-to-find-in-article"

    # defaults - moved to parent
    #DEFAULT_DATE_FORMAT = "%Y-%m-%d"

    # standard date parameter names
    PARAM_SINGLE_DATE = 'single_date'
    PARAM_START_DATE = 'start_date'   # publication date - articles will be included that were published on or after this date.
    PARAM_END_DATE = 'end_date'   # publication date - articles will be included that were published on or before this date.
    PARAM_DATE_RANGE = 'date_range'   # For date range fields, enter any number of paired date ranges, where dates are in the format YYYY-MM-DD, dates are separated by the string " to ", and each pair of dates is separated by two pipes ("||").  Example: 2009-12-01 to 2009-12-31||2010-02-01 to 2010-02-28


    # network selection parameters we expect.
    PARAM_NEWSPAPER_ID = "newspaper_id"  # ID of newspaper whose articles we want.
    PARAM_NEWSPAPER_NEWSBANK_CODE = "newspaper_newsbank_code"  # Newsbank Code of newspaper whose articles we want.
    PARAM_NEWSPAPER_INSTANCE = "newspaper"  # Newspaper instance whose articles we want.
    PARAM_NEWSPAPER_ID_IN_LIST = "newspaper_id_in_list"  # list of IDs of Newspapers whose articles we want.
    PARAM_PUBLICATION_LIST = 'publications'   # list of IDs of newspapers you want included.
    PARAM_TOPIC_LIST = 'topics'   # list of IDs of topics whose data you want included.
    PARAM_SECTION_NAME = 'section_name'   # list of tag values that you want included.
    PARAM_SECTION_NAME_LIST = 'section_name_list'  # list of names of sections you want included articles to be members of.
    PARAM_SECTION_LIST = 'section_list'   # alternate for list of names of sections you want included articles to be members of.
    PARAM_TAGS_IN_LIST = "tags_in_list_IN"  # comma-delimited string list of tag values that you want included.
    PARAM_TAGS_NOT_IN_LIST = "tags_not_in_list_IN"  # comma-delimited string list of tag values that you want excluded.
    PARAM_TAG_LIST = 'tags_list'   # comma-delimited string list of Article tag values that you want included.
    PARAM_UNIQUE_ID_LIST = 'unique_identifiers'   # list of unique identifiers of articles whose data you want included.
    PARAM_ARTICLE_ID_LIST = 'article_id_list'   # list of ids of articles whose data you want included.
    PARAM_CUSTOM_ARTICLE_Q = 'custom_article_q'  # pre-built Q() instance to use to filter articles.  Can be anything you want!
    PARAM_GET_DISTINCT_RECORDS = "get_distinct_records"  # For whatever model is being queried or filtered, only get one instance of a record that has a given ID.
    PARAM_EXCLUDE_PERSONS_WITH_TAGS_IN_LIST = 'exclude_persons_with_tags_in_list'   # comma-delimited string list of Article_Subject and Article_Author tag values you want excluded when creating network data.
    PARAM_INCLUDE_PERSONS_WITH_SINGLE_WORD_NAME = 'include_persons_with_single_word_name'   # boolean, do we include Article_Subject and Article_Author people with a single word verbatim_name.
    PARAM_NAME_DATABASE_OUTPUT = "database_output"
    PARAM_NETWORK_INCLUDE_RENDER_DETAILS = 'network_include_render_details'
    PARAM_DB_ADD_TIMESTAMP_TO_LABEL = "db_add_timestamp_to_label"

    # Article_Data filter parameters.
    PARAM_CODERS = "coders"
    PARAM_CODER_TYPE_FILTER_TYPE = "coder_type_filter_type"
    PARAM_CODER_TYPES_LIST = "coder_types_list"

    # params for processing articles
    PARAM_APPLY_TAGS_LIST = 'apply_tags_list'

    # types of params.
    PARAM_TYPE_INT = ParamContainer.PARAM_TYPE_INT
    PARAM_TYPE_LIST = ParamContainer.PARAM_TYPE_LIST
    PARAM_TYPE_STRING = ParamContainer.PARAM_TYPE_STRING

    # Dictionary of parameters to their types, for use in debug method.
    PARAM_NAME_TO_TYPE_MAP = {}

    # variables for choosing yes or no.
    CHOICE_YES = 'yes'
    CHOICE_NO = 'no'
    CHOICE_YES_OR_NO_VALUE_LIST = list()
    CHOICE_YES_OR_NO_VALUE_LIST.append( CHOICE_YES )
    CHOICE_YES_OR_NO_VALUE_LIST.append( CHOICE_NO )

    # choices for yes or no decision.
    CHOICES_YES_OR_NO_LIST = [
        ( CHOICE_NO, "No" ),
        ( CHOICE_YES, "Yes" )
    ]

    # automated coder user
    CODER_USERNAME_AUTOMATED = "automated"
    CODER_USER_AUTOMATED = None

    # ground truth coding user
    CODER_USERNAME_GROUND_TRUTH = "ground_truth"
    CODER_USER_GROUND_TRUTH = None

    # Filtering Article_Data on coder_type.
    CODER_TYPE_FILTER_TYPE_NONE = "none"
    CODER_TYPE_FILTER_TYPE_AUTOMATED = "automated"
    CODER_TYPE_FILTER_TYPE_ALL = "all"
    CODER_TYPE_FILTER_TYPE_DEFAULT = CODER_TYPE_FILTER_TYPE_NONE

    # Tags
    TAG_LOCAL_HARD_NEWS = "local_hard_news"

    # Tags - Article_Person
    TAG_SINGLE_NAME_PART = "single_name_part"
    TAG_SINGLE_NAME_MISMATCH_WITH_PERSON = "single_name_mismatch_with_person"
    TAG_ME_SINGLE_NAME_PERSON_MULTI = "me_single_name_person_multi"

    #--------------------------------------------------------------------------#
    # ! ----> export --> network output

    PARAM_NAME_OUTPUT_TYPE = "output_type"

    NETWORK_DATA_FORMAT_SIMPLE_MATRIX = "simple_matrix"
    NETWORK_DATA_FORMAT_CSV_MATRIX = "csv_matrix"
    NETWORK_DATA_FORMAT_TAB_DELIMITED_MATRIX = "tab_delimited_matrix"
    NETWORK_DATA_FORMAT_DEFAULT = NETWORK_DATA_FORMAT_TAB_DELIMITED_MATRIX

    NETWORK_DATA_FORMAT_CHOICES_LIST = [
        ( NETWORK_DATA_FORMAT_SIMPLE_MATRIX, "Simple Matrix" ),
        ( NETWORK_DATA_FORMAT_CSV_MATRIX, "CSV Matrix" ),
        ( NETWORK_DATA_FORMAT_TAB_DELIMITED_MATRIX, "Tab-Delimited Matrix" ),
    ]

    #--------------------------------------------------------------------------#
    # ! ----> Context

    # ! --------> Entities

    # entity identifier types - testing
    CONTEXT_ENTITY_ID_TYPE_NAME_DOES_NOT_EXIST = "calliope_tree_frog"

    # entity identifier types - general
    CONTEXT_ENTITY_ID_TYPE_PERMALINK = "permalink"

    # entity identifier types - articles
    CONTEXT_ENTITY_ID_TYPE_ARTICLE_ARCHIVE_IDENTIFIER = "article_archive_identifier"
    CONTEXT_ENTITY_ID_TYPE_ARTICLE_NEWSBANK_ID = "article_newsbank_id"
    CONTEXT_ENTITY_ID_TYPE_ARTICLE_SOURCENET_ID = "article_sourcenet_id"

    # entity identifier types - newspaper
    CONTEXT_ENTITY_ID_TYPE_NEWSPAPER_NEWSBANK_CODE = "newspaper_newsbank_code"
    CONTEXT_ENTITY_ID_TYPE_NEWSPAPER_SOURCENET_ID = "newspaper_sourcenet_id"

    # entity identifier types - organization
    CONTEXT_ENTITY_ID_TYPE_ORGANIZATION_SOURCENET_ID = "organization_sourcenet_id"

    # entity identifier types - person
    CONTEXT_ENTITY_ID_TYPE_NAME_PERSON_OPEN_CALAIS_UUID = "person_open_calais_uuid"
    CONTEXT_ENTITY_ID_TYPE_NAME_PERSON_SOURCENET_ID = "person_sourcenet_id"

    # entity identifier types - default
    CONTEXT_ENTITY_ID_TYPE_DEFAULT = CONTEXT_ENTITY_ID_TYPE_PERMALINK

    # Entity Type slugs
    CONTEXT_ENTITY_TYPE_SLUG_ARTICLE = "article"
    CONTEXT_ENTITY_TYPE_SLUG_NEWSPAPER = "newspaper"
    CONTEXT_ENTITY_TYPE_SLUG_ORGANIZATION = "organization"
    CONTEXT_ENTITY_TYPE_SLUG_PERSON = "person"

    # ! --------> trait names
    CONTEXT_TRAIT_NAME_CODER_ID = "sourcenet-coder-User-id"
    CONTEXT_TRAIT_NAME_CODER_TYPE = "coder_type"
    CONTEXT_TRAIT_NAME_CODER_USERNAME = "sourcenet-coder-User-username"
    CONTEXT_TRAIT_NAME_DESCRIPTION = "description"
    CONTEXT_TRAIT_NAME_FIRST_NAME = "first_name"
    CONTEXT_TRAIT_NAME_FULL_NAME = "full_name"
    CONTEXT_TRAIT_NAME_GENDER = "gender"
    CONTEXT_TRAIT_NAME_LAST_NAME = "last_name"
    CONTEXT_TRAIT_NAME_MIDDLE_NAME = "middle_name"
    CONTEXT_TRAIT_NAME_NAME = "name"
    CONTEXT_TRAIT_NAME_NAME_PREFIX = "name_prefix"
    CONTEXT_TRAIT_NAME_NAME_SUFFIX = "name_suffix"
    CONTEXT_TRAIT_NAME_PUB_DATE = "pub_date"
    CONTEXT_TRAIT_NAME_SECTIONS_LOCAL_NEWS = "sections_local_news"
    CONTEXT_TRAIT_NAME_SECTIONS_SPORTS = "sections_sports"
    CONTEXT_TRAIT_NAME_SOURCENET_LOCATION_ID = "sourcenet-Location-ID"
    CONTEXT_TRAIT_NAME_SOURCENET_NEWSPAPER_ID = "sourcenet-Newspaper-ID"
    CONTEXT_TRAIT_NAME_SOURCENET_ORGANIZATION_ID = "sourcenet-Organization-ID"
    CONTEXT_TRAIT_NAME_TITLE = "title"

    # ! --------> Relations

    # Entity_Relation_Type slugs - FROM NEWSPAPER
    CONTEXT_RELATION_TYPE_SLUG_NEWSPAPER_ARTICLE = "newspaper_article"    # FROM newspaper TO article.
    CONTEXT_RELATION_TYPE_SLUG_NEWSPAPER_REPORTER = "newspaper_reporter"  # FROM newspaper TO person (reporter) THROUGH article.
    CONTEXT_RELATION_TYPE_SLUG_NEWSPAPER_SOURCE = "newspaper_source"      # FROM newspaper TO person (source) THROUGH article.
    CONTEXT_RELATION_TYPE_SLUG_NEWSPAPER_SUBJECT = "newspaper_subject"    # FROM newspaper TO person (subject, including sources) THROUGH article.

    # Entity_Relation_Type slugs - FROM ARTICLE
    CONTEXT_RELATION_TYPE_SLUG_AUTHOR = "author"    # FROM article TO reporter.
    CONTEXT_RELATION_TYPE_SLUG_SOURCE = "source"    # FROM article TO source person.
    CONTEXT_RELATION_TYPE_SLUG_SUBJECT = "subject"  # FROM article TO subject person.

    # Entity_Relation_Type slugs - THROUGH ARTICLE
    CONTEXT_RELATION_TYPE_SLUG_MENTIONED = "mentioned"                          # FROM reporter/author TO subject THROUGH article (includes subjects and sources).
    CONTEXT_RELATION_TYPE_SLUG_QUOTED = "quoted"                                # FROM reporter TO source THROUGH article.
    CONTEXT_RELATION_TYPE_SLUG_SAME_ARTICLE_SOURCES = "same_article_sources"    # FROM source person TO source person THROUGH article.
    CONTEXT_RELATION_TYPE_SLUG_SAME_ARTICLE_SUBJECTS = "same_article_subjects"  # FROM subject person TO subject person THROUGH article (includes subjects and sources).
    CONTEXT_RELATION_TYPE_SLUG_SHARED_BYLINE = "shared_byline"                  # FROM author TO author THROUGH article.

    #-----------------------------------------------------------------------------
    # ! ==> class methods
    #-----------------------------------------------------------------------------


    #---------------------------------------------------------------------------
    # ! ==> __init__() method
    #---------------------------------------------------------------------------


    def __init__( self ):

        # call parent's __init__()
        super( ContextTextBase, self ).__init__()

        # declare variables
        self.request = None
        self.parameters = ParamContainer()

        # rate limiting
        self.is_rate_limited = False

        # define parameters - should do this in "child.__init__()".
        self.define_parameters( self.PARAM_NAME_TO_TYPE_MAP )

        # set logger name (for LoggingHelper parent class: (LoggingHelper --> BasicRateLimited --> ContextTextBase).
        self.set_logger_name( "context_text.shared.context_text_base" )

    #-- END method __init__() --#


    #---------------------------------------------------------------------------
    # ! ==> instance methods, in alphabetical order
    #---------------------------------------------------------------------------


    def get_parameters( self, *args, **kwargs ):

        '''
        Returns ParamContainer instance nested in this instance.
        Preconditions: None
        Postconditions: None

        Returns the ParamContainer stored in the instance.
        '''

        # return reference
        value_OUT = None

        # declare variables
        me = "get_parameters"

        # return the content.
        value_OUT = self.parameters

        return value_OUT

    #-- END method get_parameters() --#


    def get_parameters_dict( self, *args, **kwargs ):

        '''
        Returns parameters dictionary nested in ParamContainer instance stored
            in this instance.
        Preconditions: None
        Postconditions: None

        Returns the parameters dictionary from the ParamContainer stored in the instance.
        '''

        # return reference
        value_OUT = None

        # declare variables
        me = "get_parameters_dict"
        my_param_container = None

        # return the content.
        my_param_container = self.get_parameters()
        value_OUT = my_param_container.get_parameters()

        return value_OUT

    #-- END method get_parameters_dict() --#


#-- END class ContextTextBase --#
