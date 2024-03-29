'''
Copyright 2010-2017 Jonathan Morgan

This file is part of http://github.com/jonathanmorgan/context_text.

context_text is free software: you can redistribute it and/or modify it under the terms of the GNU Lesser General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.

context_text is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.

You should have received a copy of the GNU Lesser General Public License along with http://github.com/jonathanmorgan/context_text. If not, see http://www.gnu.org/licenses/.
'''

'''
The network_output module contains objects and code to parse and output social
    network data from context_text in a variety of formats, and also generates
    some descriptive statistics as it builds output.

2014-05-16 - Jonathan Morgan - Updated so that this object now speaks in terms
    of Article_Data, not Article, so that we support multiple passes at coding
    a given article by different people, only have to store the contents of each
    article once.

2022-05-21 - Jonathan Morgan - Updating so `create_query_set` can both "filter"
    and "exclude".
'''

'''
If a NetworkDataOutput implementer will need to access or use variables, you
    should declare them in class NetworkDataOutput in file
    /export/network_data_output.py, then reference those variables here.
'''

__author__="jonathanmorgan"
__date__ ="$May 1, 2010 12:49:50 PM$"

if __name__ == "__main__":
    print( "Hello World" )

#===============================================================================
# imports (in alphabetical order by package, then by name)
#===============================================================================

# python base imports
import datetime
import operator

# django database classes
from django.db.models import Q

# python_utilities
from python_utilities.parameters.param_container import ParamContainer

# Import the classes for our context_text application
from context_text.models import Article
from context_text.models import Article_Data
from context_text.models import NetworkDataOutputLog

# Import context_text export classes.
from context_text.export.csv_article_output import CsvArticleOutput
from context_text.export.network_data_output import NetworkDataOutput
from context_text.export.ndo_simple_matrix import NDO_SimpleMatrix
from context_text.export.ndo_csv_matrix import NDO_CSVMatrix
from context_text.export.ndo_tab_delimited_matrix import NDO_TabDelimitedMatrix

# Import context_text shared classes.
from context_text.shared.context_text_base import ContextTextBase
from context_text.shared.context_text_error import ContextTextError

#===============================================================================
# classes (in alphabetical order by name)
#===============================================================================

class NetworkOutput( ContextTextBase ):


    #---------------------------------------------------------------------------
    # CONSTANTS-ish
    #---------------------------------------------------------------------------

    # network selection parameters we expect - moved to parent.
    #PARAM_START_DATE = 'start_date'   # publication date - articles will be included that were published on or after this date.
    #PARAM_END_DATE = 'end_date'   # publication date - articles will be included that were published on or before this date.
    #PARAM_DATE_RANGE = 'date_range'   # For date range fields, enter any number of paired date ranges, where dates are in the format YYYY-MM-DD, dates are separated by the string " to ", and each pair of dates is separated by two pipes ("||").  Example: 2009-12-01 to 2009-12-31||2010-02-01 to 2010-02-28
    #PARAM_PUBLICATION_LIST = 'publications'   # list of IDs of newspapers you want included.
    #PARAM_TOPIC_LIST = 'topics'   # list of IDs of topics whose data you want included.
    #PARAM_TAG_LIST = 'tags_list'   # comma-delimited string list of tags you want articles that are included to have one or more of assigned to them.
    #PARAM_UNIQUE_ID_LIST = 'unique_identifiers'   # list of unique identifiers of articles whose data you want included.

    # parameters for relation selection.
    PARAM_SOURCE_CAPACITY_INCLUDE_LIST = NetworkDataOutput.PARAM_SOURCE_CAPACITY_INCLUDE_LIST
    PARAM_SOURCE_CAPACITY_EXCLUDE_LIST = NetworkDataOutput.PARAM_SOURCE_CAPACITY_EXCLUDE_LIST
    PARAM_SOURCE_CONTACT_TYPE_INCLUDE_LIST = NetworkDataOutput.PARAM_SOURCE_CONTACT_TYPE_INCLUDE_LIST
    # in ContextTextBase: PARAM_EXCLUDE_PERSONS_WITH_TAGS_IN_LIST = 'exclude_persons_with_tags_in_list'   # comma-delimited string list of Article_Subject and Article_Author tag values you want excluded when creating network data.
    # in ContextTextBase: PARAM_INCLUDE_PERSONS_WITH_SINGLE_WORD_NAME = 'include_persons_with_single_word_name'   # boolean, do we include Article_Subject and Article_Author people with a single word verbatim_name.


    # network selection parameters unique to this class.
    PARAM_CODER_LIST = 'coders'   # list of IDs of coders whose data you want included.
    PARAM_CODER_ID_PRIORITY_LIST = 'coder_id_priority_list' # list of IDs of coders whose data you want included, in order of highest priority in case of a collision (two coders coding the same article) to lowest.
    PARAM_CODER_TYPE_LIST = 'coder_types_list'   # comma-delimited string list of coder_type values from Article_Data that you want articles' data to have for articles we process.
    PARAM_HEADER_PREFIX = 'header_prefix'   # for output, optional prefix you want appended to front of column header names.
    PARAM_OUTPUT_TYPE = ContextTextBase.PARAM_NAME_OUTPUT_TYPE   # 'output_type' - type of output you want, either CSV, tab-delimited, or old UCINet format that I should just remove.
    PARAM_ALLOW_DUPLICATE_ARTICLES = 'allow_duplicate_articles'   # allow duplicate articles...  Not sure this is relevant anymore.

    # parameters specific to network output
    PARAM_NETWORK_DOWNLOAD_AS_FILE = NetworkDataOutput.PARAM_NETWORK_DOWNLOAD_AS_FILE
    PARAM_NETWORK_LABEL = NetworkDataOutput.PARAM_NETWORK_LABEL
    PARAM_NETWORK_INCLUDE_HEADERS = NetworkDataOutput.PARAM_NETWORK_INCLUDE_HEADERS
    PARAM_NETWORK_INCLUDE_RENDER_DETAILS = NetworkDataOutput.PARAM_NETWORK_INCLUDE_RENDER_DETAILS
    PARAM_NETWORK_DATA_OUTPUT_TYPE = NetworkDataOutput.PARAM_NETWORK_DATA_OUTPUT_TYPE
    # in ContextTextBase: PARAM_NAME_DATABASE_OUTPUT = "database_output"
    # in ContextTextBase: PARAM_DB_ADD_TIMESTAMP_TO_LABEL = "db_add_timestamp_to_label"

    # prefix for person-selection params - same as network selection parameters
    #    above, but with this prefix appended to the front.
    PARAM_PERSON_PREFIX = 'person_'
    PARAM_PERSON_START_DATE = "{prefix}{param_name}".format(
        prefix = PARAM_PERSON_PREFIX,
        param_name = ContextTextBase.PARAM_START_DATE
    )
    PARAM_PERSON_END_DATE = "{prefix}{param_name}".format(
        prefix = PARAM_PERSON_PREFIX,
        param_name = ContextTextBase.PARAM_END_DATE
    )
    PARAM_PERSON_CODER_LIST = "{prefix}{param_name}".format(
        prefix = PARAM_PERSON_PREFIX,
        param_name = PARAM_CODER_LIST
    )
    PARAM_PERSON_CODER_ID_PRIORITY_LIST = "{prefix}{param_name}".format(
        prefix = PARAM_PERSON_PREFIX,
        param_name = PARAM_CODER_ID_PRIORITY_LIST
    )

    # parameters for person selection.
    PARAM_PERSON_QUERY_TYPE = NetworkDataOutput.PARAM_PERSON_QUERY_TYPE

    # parameters for filtering Article_Data based on coder type
    PARAM_CODER_TYPE_FILTER_TYPE =  NetworkDataOutput.PARAM_CODER_TYPE_FILTER_TYPE # "coder_type_filter_type"
    PARAM_PERSON_CODER_TYPE_FILTER_TYPE = NetworkDataOutput.PARAM_PERSON_CODER_TYPE_FILTER_TYPE # "person_coder_type_filter_type"

    # Dictionary of parameters to their types, for use in debug method.
    PARAM_NAME_TO_TYPE_MAP = {
        ContextTextBase.PARAM_START_DATE : ParamContainer.PARAM_TYPE_STRING,
        ContextTextBase.PARAM_END_DATE : ParamContainer.PARAM_TYPE_STRING,
        ContextTextBase.PARAM_DATE_RANGE : ParamContainer.PARAM_TYPE_STRING,
        ContextTextBase.PARAM_PUBLICATION_LIST : ParamContainer.PARAM_TYPE_LIST,
        PARAM_CODER_LIST : ParamContainer.PARAM_TYPE_LIST,
        PARAM_CODER_ID_PRIORITY_LIST : ParamContainer.PARAM_TYPE_LIST,
        PARAM_CODER_TYPE_FILTER_TYPE : ParamContainer.PARAM_TYPE_STRING,
        PARAM_CODER_TYPE_LIST : ParamContainer.PARAM_TYPE_LIST,
        ContextTextBase.PARAM_TOPIC_LIST : ParamContainer.PARAM_TYPE_LIST,
        ContextTextBase.PARAM_TAG_LIST : ParamContainer.PARAM_TYPE_LIST,
        ContextTextBase.PARAM_UNIQUE_ID_LIST : ParamContainer.PARAM_TYPE_LIST,
        PARAM_ALLOW_DUPLICATE_ARTICLES : ParamContainer.PARAM_TYPE_STRING,
        PARAM_SOURCE_CONTACT_TYPE_INCLUDE_LIST : ParamContainer.PARAM_TYPE_LIST,
        PARAM_SOURCE_CAPACITY_INCLUDE_LIST : ParamContainer.PARAM_TYPE_LIST,
        PARAM_SOURCE_CAPACITY_EXCLUDE_LIST : ParamContainer.PARAM_TYPE_LIST,
        ContextTextBase.PARAM_EXCLUDE_PERSONS_WITH_TAGS_IN_LIST : ParamContainer.PARAM_TYPE_LIST,
        ContextTextBase.PARAM_INCLUDE_PERSONS_WITH_SINGLE_WORD_NAME : ParamContainer.PARAM_TYPE_STRING,
        PARAM_HEADER_PREFIX : ParamContainer.PARAM_TYPE_STRING,
        PARAM_NETWORK_DOWNLOAD_AS_FILE : ParamContainer.PARAM_TYPE_STRING,
        PARAM_NETWORK_INCLUDE_RENDER_DETAILS : ParamContainer.PARAM_TYPE_STRING,
        PARAM_OUTPUT_TYPE : ParamContainer.PARAM_TYPE_STRING,
        PARAM_NETWORK_DATA_OUTPUT_TYPE : ParamContainer.PARAM_TYPE_STRING,
        PARAM_NETWORK_LABEL : ParamContainer.PARAM_TYPE_STRING,
        PARAM_NETWORK_INCLUDE_HEADERS : ParamContainer.PARAM_TYPE_STRING,
        ContextTextBase.PARAM_NAME_DATABASE_OUTPUT : ParamContainer.PARAM_TYPE_STRING,
        ContextTextBase.PARAM_DB_ADD_TIMESTAMP_TO_LABEL : ParamContainer.PARAM_TYPE_STRING,
        ContextTextBase.PARAM_NAME_DB_SAVE_DATA_IN_DATABASE : ParamContainer.PARAM_TYPE_STRING,
        ContextTextBase.PARAM_NAME_SAVE_DATA_IN_FOLDER : ParamContainer.PARAM_TYPE_STRING,
        PARAM_PERSON_QUERY_TYPE : ParamContainer.PARAM_TYPE_STRING,
        PARAM_PERSON_START_DATE : ParamContainer.PARAM_TYPE_STRING,
        PARAM_PERSON_END_DATE : ParamContainer.PARAM_TYPE_STRING,
        PARAM_PERSON_PREFIX + ContextTextBase.PARAM_DATE_RANGE : ParamContainer.PARAM_TYPE_STRING,
        PARAM_PERSON_PREFIX + ContextTextBase.PARAM_PUBLICATION_LIST : ParamContainer.PARAM_TYPE_LIST,
        PARAM_PERSON_PREFIX + PARAM_CODER_TYPE_FILTER_TYPE : ParamContainer.PARAM_TYPE_STRING,
        PARAM_PERSON_PREFIX + PARAM_CODER_LIST : ParamContainer.PARAM_TYPE_LIST,
        PARAM_PERSON_PREFIX + PARAM_CODER_ID_PRIORITY_LIST : ParamContainer.PARAM_TYPE_LIST,
        PARAM_PERSON_PREFIX + ContextTextBase.PARAM_TOPIC_LIST : ParamContainer.PARAM_TYPE_LIST,
        PARAM_PERSON_PREFIX + ContextTextBase.PARAM_TAG_LIST : ParamContainer.PARAM_TYPE_LIST,
        PARAM_PERSON_PREFIX + ContextTextBase.PARAM_UNIQUE_ID_LIST : ParamContainer.PARAM_TYPE_LIST,
        PARAM_PERSON_PREFIX + PARAM_ALLOW_DUPLICATE_ARTICLES : ParamContainer.PARAM_TYPE_STRING
    }

    OUTPUT_TYPE_CHOICES_LIST = [
        ( CsvArticleOutput.ARTICLE_OUTPUT_TYPE_ARTICLE_PER_LINE, "One article per line" ),
        ( CsvArticleOutput.ARTICLE_OUTPUT_TYPE_SOURCE_PER_LINE, "One source per line" ),
        ( CsvArticleOutput.ARTICLE_OUTPUT_TYPE_AUTHOR_PER_LINE, "One author per line" )
    ]

    # variables for choosing yes or no. - moved to parent.
    #CHOICE_YES = 'yes'
    #CHOICE_NO = 'no'

    # choices for yes or no decision.
    #CHOICES_YES_OR_NO_LIST = [
    #    ( CHOICE_NO, "No" ),
    #    ( CHOICE_YES, "Yes" )
    #]

    # Network data format output types
    NETWORK_OUTPUT_TYPE_SIMPLE_MATRIX = NetworkDataOutput.NETWORK_DATA_FORMAT_SIMPLE_MATRIX
    NETWORK_OUTPUT_TYPE_CSV_MATRIX = NetworkDataOutput.NETWORK_DATA_FORMAT_CSV_MATRIX
    NETWORK_OUTPUT_TYPE_TAB_DELIMITED_MATRIX = NetworkDataOutput.NETWORK_DATA_FORMAT_TAB_DELIMITED_MATRIX
    NETWORK_OUTPUT_TYPE_DEFAULT = NetworkDataOutput.NETWORK_DATA_FORMAT_DEFAULT

    NETWORK_OUTPUT_TYPE_CHOICES_LIST = NetworkDataOutput.NETWORK_DATA_FORMAT_CHOICES_LIST

    # Network data output types
    NETWORK_DATA_OUTPUT_TYPE_NETWORK = NetworkDataOutput.NETWORK_DATA_OUTPUT_TYPE_NETWORK
    NETWORK_DATA_OUTPUT_TYPE_ATTRIBUTES = NetworkDataOutput.NETWORK_DATA_OUTPUT_TYPE_ATTRIBUTES
    NETWORK_DATA_OUTPUT_TYPE_NET_AND_ATTR_COLS = NetworkDataOutput.NETWORK_DATA_OUTPUT_TYPE_NET_AND_ATTR_COLS
    NETWORK_DATA_OUTPUT_TYPE_NET_AND_ATTR_ROWS = NetworkDataOutput.NETWORK_DATA_OUTPUT_TYPE_NET_AND_ATTR_ROWS
    NETWORK_DATA_OUTPUT_TYPE_DEFAULT = NetworkDataOutput.NETWORK_DATA_OUTPUT_TYPE_DEFAULT

    NETWORK_DATA_OUTPUT_TYPE_CHOICES_LIST = NetworkDataOutput.NETWORK_DATA_OUTPUT_TYPE_CHOICES_LIST

    # Person Query Types
    PERSON_QUERY_TYPE_ALL = NetworkDataOutput.PERSON_QUERY_TYPE_ALL
    PERSON_QUERY_TYPE_ARTICLES = NetworkDataOutput.PERSON_QUERY_TYPE_ARTICLES
    PERSON_QUERY_TYPE_CUSTOM = NetworkDataOutput.PERSON_QUERY_TYPE_CUSTOM
    PERSON_QUERY_TYPE_DEFAULT = NetworkDataOutput.PERSON_QUERY_TYPE_DEFAULT

    PERSON_QUERY_TYPE_CHOICES_LIST = NetworkDataOutput.PERSON_QUERY_TYPE_CHOICES_LIST

    # Filtering Article_Data on coder_type.
    CODER_TYPE_FILTER_TYPE_NONE = NetworkDataOutput.CODER_TYPE_FILTER_TYPE_NONE
    CODER_TYPE_FILTER_TYPE_AUTOMATED = NetworkDataOutput.CODER_TYPE_FILTER_TYPE_AUTOMATED
    CODER_TYPE_FILTER_TYPE_ALL = NetworkDataOutput.CODER_TYPE_FILTER_TYPE_ALL
    CODER_TYPE_FILTER_TYPE_DEFAULT = NetworkDataOutput.CODER_TYPE_FILTER_TYPE_DEFAULT

    CODER_TYPE_FILTER_TYPE_CHOICES_LIST = NetworkDataOutput.CODER_TYPE_FILTER_TYPE_CHOICES_LIST


    #---------------------------------------------------------------------------
    # ! class methods
    #---------------------------------------------------------------------------


    #---------------------------------------------------------------------------
    # ! __init__() method
    #---------------------------------------------------------------------------


    def __init__( self ):

        # call parent's __init__()
        super().__init__()

        # declare variables - moved to parent
        #self.request = None
        #self.parameters = ParamContainer()

        # define parameters - moved to parent
        #self.define_parameters( NetworkOutput.PARAM_NAME_TO_TYPE_MAP )

        # variables for outputting result as file
        self.mime_type = ""
        self.file_extension = ""

        # variable to hold combined master article and person coder ID list.
        self.m_article_coder_id_list = None
        self.m_person_coder_id_list = None

        # auditing
        self.last_label = None

        # ability to store NetworkDataOutput instance
        self.ndo_instance = None

        # set logger name (for LoggingHelper parent class: (LoggingHelper --> BasicRateLimited --> ContextTextBase --> ArticleCoding).
        self.set_logger_name( "context_text.export.network_output" )

    #-- END method __init__() --#


    #---------------------------------------------------------------------------
    # ! instance methods, in alphabetical order
    #---------------------------------------------------------------------------


    def add_people_to_dict( self, person_qs_IN, dictionary_IN, store_person_IN = False ):

        """
            Accepts a dictionary, a list of Article_Person instances, and a flag
                that indicates if model instances should be stored in the
                dictionary. Adds the people in the Article_Person query set to
                the dictionary, making the Person ID the key and either None or
                the Person model instance the value, depending on the value in
                the store_person_IN flag.

            Preconditions: request must have contained required parameters, and
                so contained at least a start and end date and a publication.
                Should we have a flag that says to use the same criteria as the
                selection criteria?

            Postconditions: uses a lot of memory if you choose a large date
                range. Returns the same dictionary passed in, but with the
                people in store_person_IN added.

            Parameters:
            - self - self instance variable.
            - person_qs_IN - django query set object that contains the people we
                want to add to our dictionary.
            - dictionary_IN - dictionary we want to add people to.  Returned
                with people added.
            - store_person_IN - boolean, if False, doesn't load Person model
                instances while building the dictionary.  If True, loads Person
                models and stores them in the dictionary.

            Returns:
            - Dictionary - dictionary that contains all the people in the query
                set of Article_Person implementors passed in, either mapped to
                None or to Person model instances, depending on the
                store_person_IN flag value.
        """

        # return reference
        person_dict_OUT = {}

        # declare variables
        current_relation = None
        current_person = None
        current_person_id = ''
        current_value = None

        # set the output dictionary
        if ( dictionary_IN ):

            # yes, store in output parameter
            person_dict_OUT = dictionary_IN

        #-- END check to see if dictionary passed in --#

        # loop over the articles
        for current_relation in person_qs_IN:

            # add author's person ID to list.  If no person ID, don't add (what
            #    to do about anonymous sources?).
            current_person = current_relation.person

            # see if there is a person
            if ( current_person is not None ):

                # are we also loading the person?
                current_person_id = current_person.id

                if ( store_person_IN == True ):

                    # yes, use Person model as value.
                    current_value = current_person

                else:

                    # no, use None as value.
                    current_value = None

                #-- END conditional to check if we are storing actual model instances --#

                # store the person in the output dict.
                person_dict_OUT[ current_person_id ] = current_value

            #-- END check to see if there is a person (in comparison to an anonymous source, for instance, or the author just being the newspaper) --#

        #-- END loop over people --#

        return person_dict_OUT

    #-- END function add_people_to_dict() --#


    def create_network_query_set( self ):

        # return reference
        query_set_OUT = None

        # declare variables

        # call the create query set method, use start_date and end_date as date
        #    boundaries for a given network slice.
        query_set_OUT = self.create_query_set()

        return query_set_OUT

    #-- end method output_create_network_query_set() -------------------------------------------------------


    def create_person_dict( self, load_person_IN = False, debug_flag_IN = None ):

        """
            Accepts flag that dictates whether we load the actual person
                record or not.  Uses person start and end dates from nested
                request to retrieve all the article data in the range specified,
                and then builds a dictionary of all the IDs of those people
                mapped to their Person instance.

            Preconditions: request must have contained required parameters, and
                so contained at least a start and end date and a publication.
                Should we have a flag that says to use the same criteria as the
                selection criteria?

            Postconditions: uses a lot of memory if you choose a large date
                range.

            Parameters:
            - load_person_IN - boolean, if False, doesn't load Person model
                instances while building the dictionary.  If True, loads Person
                models and stores them in the dictionary.

            Returns:
            - Dictionary - dictionary that maps person IDs to Person model
                instances for all people associated with all the articles in the
                desired date range.
        """

        # return reference
        person_dict_OUT = {}

        # declare variables
        me = "create_person_dict"
        my_debug_flag = None
        debug_message = None
        my_logger = None
        article_data_query_set = None
        current_article_data = None
        author_qs = None
        source_qs = None
        exclude_persons_with_tags_list = None
        include_persons_with_single_name = None

        # init debug
        my_debug_flag = NetworkDataOutput.DEBUG_FLAG
        if ( debug_flag_IN is not None ):
            my_debug_flag = debug_flag_IN
        #-- END check if debug flag passed in. --#

        # initialize logger
        my_logger = self.get_logger()

        # init person filter criteria
        exclude_persons_with_tags_list = self.get_param_as_list( ContextTextBase.PARAM_EXCLUDE_PERSONS_WITH_TAGS_IN_LIST )
        include_persons_with_single_name = self.get_param_as_str( ContextTextBase.PARAM_INCLUDE_PERSONS_WITH_SINGLE_WORD_NAME, ContextTextBase.CHOICE_NO )

        # get query set to loop over Article_Data that matches our person
        #    select criteria.
        article_data_query_set = self.create_person_query_set()

        debug_message = "In {me}: article_data_query_set.count() = {qs_count}".format(
            me = me,
            qs_count = article_data_query_set.count()
        )
        self.output_debug( debug_message, do_print_IN = my_debug_flag )

        # loop over the articles
        for current_article_data in article_data_query_set:

            #------------------------------------------------------------------#
            # retrieve authors and add them to dict
            author_qs = current_article_data.get_article_authors_qs(
                exclude_persons_with_tags_list_IN = exclude_persons_with_tags_list,
                include_persons_with_single_name_IN = include_persons_with_single_name
            )

            person_dict_OUT = self.add_people_to_dict( author_qs, person_dict_OUT, load_person_IN )

            #------------------------------------------------------------------#
            # retrieve sources and add them to dict
            source_qs = current_article_data.get_quoted_article_sources_qs(
                exclude_persons_with_tags_list_IN = exclude_persons_with_tags_list,
                include_persons_with_single_name_IN = include_persons_with_single_name
            )

            person_dict_OUT = self.add_people_to_dict( source_qs, person_dict_OUT, load_person_IN )

        #-- END loop over articles --#

        debug_message = "In {me}: len( person_dict_OUT ) = {dict_count}".format(
            me = me,
            dict_count = len( person_dict_OUT )
        )
        self.output_debug( debug_message, do_print_IN = my_debug_flag )

        return person_dict_OUT

    #-- END function create_person_dict() --#


    def create_person_query_set( self, person_query_type_IN = None ):

        # return reference
        query_set_OUT = None

        # declare variables
        me = "create_person_query_set"
        my_logger = None
        selected_person_query_type = ""

        # initialize logger.
        my_logger = self.get_logger()

        # got a value passed in?
        if ( ( person_query_type_IN is not None ) and ( person_query_type_IN != "" ) ):

            # value passed in - use it.
            selected_person_query_type = person_query_type_IN

        else:

            # nothing passed in - retrieve person query type from request.
            selected_person_query_type = self.get_param_as_str( NetworkOutput.PARAM_PERSON_QUERY_TYPE, NetworkOutput.PERSON_QUERY_TYPE_DEFAULT )

        #-- END check to see if query type passed in --#

        my_logger.debug( "In " + me + ": selected_person_query_type = " + selected_person_query_type )

        # Figure out what to call to generate QuerySet based on selected person
        #    query type.

        # "all"
        if ( selected_person_query_type == NetworkOutput.PERSON_QUERY_TYPE_ALL ):

            # want all people referenced in any coded article - return all
            #    Article_Data instances.
            query_set_OUT = Article_Data.objects.all()
            my_logger.debug( "In " + me + ": returning all Article_Data instances." )

        # "articles"
        elif ( selected_person_query_type == NetworkOutput.PERSON_QUERY_TYPE_ARTICLES ):

            # just want people associated with selected articles.
            query_set_OUT = self.create_network_query_set()
            my_logger.debug( "In " + me + ": returning same Article_Data instances used for network." )

        # "custom"
        elif ( selected_person_query_type == NetworkOutput.PERSON_QUERY_TYPE_CUSTOM ):

            # custom - call the create_query_set() method with "PERSON_" prefix,
            #    so it uses the custom person selection filter fields.  This
            #    will be used for things like retrieving all people across
            #    multiple time slices to be included in each time slice's
            #    network.
            query_set_OUT = self.create_query_set( NetworkOutput.PARAM_PERSON_PREFIX )
            my_logger.debug( "In " + me + ": returning Article_Data instances that match custom person query filters." )

        else:

            # unknown person query type - just use those for selected articles.
            query_set_OUT = self.create_network_query_set()

        #-- END check to see what we do based on person query type. --#

        return query_set_OUT

    #-- end method create_person_query_set() ---------------------------#


    def create_query_set( self, param_prefix_IN = '' ):

        # return reference
        query_set_OUT = None

        # declare variables
        me = "create_query_set"
        status_message = None
        my_logger = None
        start_date_IN = ''
        end_date_IN = ''
        date_range_IN = ''
        publication_list_IN = None
        coder_list_IN = None
        coder_id_list = None
        coder_id_priority_list_IN = None
        coder_id_string = ""
        coder_id_int = -1
        coder_int_list = None
        coder_type_filter_type_IN = None
        coder_type_list_IN = None
        tag_list_IN = None
        topic_list_IN = None
        unique_id_list_IN = ''
        allow_duplicate_articles_IN = ''
        date_range_list = None
        date_range_pair = None
        range_start_date = None
        range_end_date = None
        date_range_q = None
        date_range_q_list = None
        current_item = None
        current_query = None

        # declare variables - build actual QuerySet.
        filter_list = []
        filter_item = None
        filter_item_count = None
        exclude_list = []
        exclude_item = None
        exclude_item_count = None
        query_item_count = None
        has_unique_id_list = False

        # filtering Article_Data coder_type
        automated_coder_user = None
        automated_coder_pk = -1

        # get logger
        my_logger = self.get_logger()

        #=====================================================================#
        # ! retrieve the incoming parameters
        #=====================================================================#

        start_date_IN = self.get_param_as_str( param_prefix_IN + ContextTextBase.PARAM_START_DATE, '' )
        end_date_IN = self.get_param_as_str( param_prefix_IN + ContextTextBase.PARAM_END_DATE, '' )
        date_range_IN = self.get_param_as_str( param_prefix_IN + ContextTextBase.PARAM_DATE_RANGE, '' )
        publication_list_IN = self.get_param_as_list( param_prefix_IN + ContextTextBase.PARAM_PUBLICATION_LIST )

        # use method to get coder ID list now that there are two fields.
        coder_id_list = self.get_coder_id_list( param_prefix_IN )

        coder_type_filter_type_IN = self.get_param_as_str( param_prefix_IN + NetworkOutput.PARAM_CODER_TYPE_FILTER_TYPE, '' )
        coder_type_list_IN = self.get_param_as_list( param_prefix_IN + NetworkOutput.PARAM_CODER_TYPE_LIST )
        topic_list_IN = self.get_param_as_list( param_prefix_IN + ContextTextBase.PARAM_TOPIC_LIST )
        tag_list_IN = self.get_param_as_list( param_prefix_IN + ContextTextBase.PARAM_TAG_LIST )
        unique_id_list_IN = self.get_param_as_list( param_prefix_IN + ContextTextBase.PARAM_UNIQUE_ID_LIST )
        allow_duplicate_articles_IN = self.get_param_as_str( param_prefix_IN + NetworkOutput.PARAM_ALLOW_DUPLICATE_ARTICLES, ContextTextBase.CHOICE_NO )

        # get all articles to start
        query_set_OUT = Article_Data.objects.all()

        #=====================================================================#
        # ! now filter based on parameters passed in.
        #=====================================================================#

        # start date
        if ( start_date_IN != '' ):

            # set up query instance
            current_query = Q( article__pub_date__gte = start_date_IN )

            # add it to list of queries
            filter_list.append( current_query )

        #-- END processing of start_date --#

        # end date
        if ( end_date_IN != '' ):

            # set up query instance
            current_query = Q( article__pub_date__lte = end_date_IN )

            # add it to list of queries
            filter_list.append( current_query )

        #-- END processing of end_date --#

        # date range?
        if ( date_range_IN != '' ):

            # first, break up the string into a list of start and end dates.
            date_range_list = self.parse_date_range( date_range_IN )
            date_range_q_list = []

            # loop over the date ranges, create a Q for each, and then store
            #    that Q in our Q list.
            for date_range_pair in date_range_list:

                # get start and end datetime.date instances.
                range_start_date = date_range_pair[ 0 ]
                range_end_date = date_range_pair[ 1 ]

                # make Q
                date_range_q = Q( article__pub_date__gte = range_start_date ) & Q( article__pub_date__lte = range_end_date )

                # add Q to Q list.
                date_range_q_list.append( date_range_q )

            #-- END loop over date range items. --#

            # see if there is anything in date_range_q_list.
            if ( len( date_range_q_list ) > 0 ):

                # There is something.  Convert it to one big ORed together
                #    Q and add that to the list.
                current_query = reduce( operator.__or__, date_range_q_list )

                # add this to the query list.
                filter_list.append( current_query )

            #-- END check to see if we have any valid date ranges.

        #-- END processing of date range --#

        # publications
        #if ( publication_list_IN ):
        if ( ( publication_list_IN is not None ) and ( len( publication_list_IN ) > 0 ) ):

            # set up query instance
            current_query = Q( article__newspaper__id__in = publication_list_IN )

            # add it to the query list
            filter_list.append( current_query )

        #-- END processing of publications --#

        # coders
        #if ( coder_list_IN ):
        if ( ( coder_id_list is not None ) and ( len( coder_id_list ) > 0 ) ):

            # try converting items in list to int.
            coder_int_list = []
            for coder_id_string in coder_id_list:

                # convert to int, then append to list.
                coder_id_int = int( coder_id_string )
                coder_int_list.append( coder_id_int )

            #-- END loop over string coder IDs. --#

            my_logger.debug( "In " + me + ": coder_int_list = " + str( coder_id_list ) )

            # set up query instance
            current_query = Q( coder__pk__in = coder_int_list )

            # add it to the query list
            filter_list.append( current_query )

        #-- END processing of coders --#

        my_logger.debug( "In " + me + ": coder_type_filter_type = " + str( coder_type_filter_type_IN ) )

        # Article_Data coder_type values - check if we are filtering.
        if ( ( coder_type_filter_type_IN is not None )
            and ( coder_type_filter_type_IN != "" )
            and ( coder_type_filter_type_IN != self.CODER_TYPE_FILTER_TYPE_NONE ) ):

            # yes, but still need to make sure there is something in the list.
            #if ( coder_type_list_IN ):
            if ( ( coder_type_list_IN is not None ) and ( len( coder_type_list_IN ) > 0 ) ):

                # we have a list.  See what our filter type is.
                if ( coder_type_filter_type_IN == self.CODER_TYPE_FILTER_TYPE_ALL ):

                    # "all" - plain old filter - set up query instance
                    current_query = Q( coder_type__in = coder_type_list_IN )

                    # add it to the query list
                    filter_list.append( current_query )

                elif ( coder_type_filter_type_IN == self.CODER_TYPE_FILTER_TYPE_AUTOMATED ):

                    # only want to filter records coded by automated user.
                    current_query = Article_Data.create_q_filter_automated_by_coder_type( coder_type_list_IN )

                    # add it to the query list
                    filter_list.append( current_query )

                else:

                    # not a valid type.  No filter.
                    my_logger.debug( "In " + me + ": unknown coder_type_filter_type = " + str( coder_type_filter_type_IN ) )

                #-- END check to see what the coder_type_filter_type is --#

            else:

                # nothing in coder type list, so no filtering to do.
                my_logger.debug( "In " + me + ": coder_type filtering requested ( " + coder_type_filter_type_IN + " ), but no coder_type values passed in.  Moving on." )

            #-- END processing of coder types --#

        #-- END check to see if we filter on coder_type --#

        # topics
        #if ( topic_list_IN ):
        if ( ( topic_list_IN is not None ) and ( len( topic_list_IN ) > 0 ) ):

            # set up query instance
            current_query = Q( topics__id__in = topic_list_IN )

            # add it to the query list
            filter_list.append( current_query )

        #-- END processing of topics --#

        # tags IN list.
        if ( ( tag_list_IN is not None ) and ( len( tag_list_IN ) > 0 ) ):

            # we have a tag list.  Set up Q() instance.
            current_query = Q( article__tags__name__in = tag_list_IN )

            # add it to the query list
            filter_list.append( current_query )

        #-- END check to see if we need to match tags. --#

        # unique identifiers IN list
        # if ( unique_id_list_IN ):
        has_unique_id_list = False
        if ( ( unique_id_list_IN is not None ) and ( len( unique_id_list_IN ) > 0 ) ):

            # set up query instance to look for articles with
            #    unique_identifier in the list of values passed in.  Not
            #    quoting, since django should do that.
            current_query = Q( article__unique_identifier__in = unique_id_list_IN )

            # add it to list of queries
            filter_list.append( current_query )

            # set flag so we know there were indeed unique IDs. --#
            has_unique_id_list = True

        #-- END processing of unique_identifiers --#

        my_logger.debug( "In " + me + ": before adding Q() instances - type of query_set_OUT = " + str( type( query_set_OUT ) ) )

        #=====================================================================#
        # ! combine filters and excludes into QuerySet.
        #=====================================================================#

        # init auditing counters
        query_item_count = 0
        filter_item_count = 0
        exclude_item_count = 0

        # filters - add them all to the QuerySet - try a loop
        for filter_item in filter_list:

            # increment query_item_count
            query_item_count += 1
            filter_item_count += 1

            # append each filter to query set.
            query_set_OUT = query_set_OUT.filter( filter_item )

            # debug
            status_message = "In {me}(): Q() #{query_item_count} ( filter #{filter_item_count} ) - type of query_set_OUT = {qs_type}".format(
                me = me,
                query_item_count = query_item_count,
                filter_item_count = filter_item_count,
                qs_type = str( type( query_set_OUT ) )
            )
            my_logger.debug( status_message )

        #-- END loop over query set filter items --#

        # excludes - add them all to the QuerySet - try a loop
        for exclude_item in exclude_list:

            # increment query_item_count
            query_item_count += 1
            exclude_item_count += 1

            # append each filter to query set.
            query_set_OUT = query_set_OUT.exclude( exclude_item )

            # debug
            status_message = "In {me}(): Q() #{query_item_count} ( exclude #{exclude_item_count} ) - type of query_set_OUT = {qs_type}".format(
                me = me,
                query_item_count = query_item_count,
                exclude_item_count = exclude_item_count,
                qs_type = str( type( query_set_OUT ) )
            )
            my_logger.debug( status_message )

        #-- END loop over query set exclude items --#

        # see if we are omitting duplicates - can only do this if no unique
        #    IDs specified.  Those take precedence (and django can't handle
        #    multiple IN statements).
        #if ( ( allow_duplicate_articles_IN == NetworkOutput.CHOICE_NO ) and ( unique_ids_IN == '' ) ):
        if ( ( allow_duplicate_articles_IN == NetworkOutput.CHOICE_NO ) and ( has_unique_id_list == False ) ):

            # remove duplicate articles.
            query_set_OUT = self.remove_duplicate_article_data( query_set_OUT, param_prefix_IN )

            my_logger.debug( "In " + me + ": after remove_duplicate_article_data() - type of query_set_OUT = " + str( type( query_set_OUT ) ) )

        #-- END check to see if we allow duplicates --#

        my_logger.debug( "In " + me + ": end of method - type of query_set_OUT = " + str( type( query_set_OUT ) ) )

        return query_set_OUT

    #-- end method create_query_set() ------------------------------------------


    def debug_parameters( self ):

        # return reference
        string_OUT = ''

        # declare variables
        expected_params = None
        param_name = ''
        param_type = ''
        param_value = ''
        param_value_list = None
        param_output_string = ''
        article_output_string_list = []
        article_output_string = ""
        person_output_string_list = []
        person_output_string = ""
        list_separator_string = ""

        # get list of expected params
        expected_params = NetworkOutput.PARAM_NAME_TO_TYPE_MAP

        # loop over expected parameters, grabbing each and adding it to the
        #    output string.
        for param_name, param_type in expected_params.items():

            # initialize this param's output string.
            param_output_string = param_name + " = \""

            # see if we have a string or a list.
            if ( param_type == NetworkOutput.PARAM_TYPE_STRING ):

                # get param value
                param_value = self.get_param_as_str( param_name, '' )

                # append to output string list.
                param_output_string += param_value

            elif ( param_type == NetworkOutput.PARAM_TYPE_LIST ):

                # get param value list
                param_value_list = self.get_param_as_list( param_name )

                # output list of values
                param_output_string += str( param_value_list )
                #for param_value in param_value_list:
                #    param_output_string += param_value + ", "

            #-- END handle different types of parameters appropriately --#

            # append closing double quote and newline.
            param_output_string += "\";"

            # then append output string to appropriate output string list,
            #    depending on type.  To check, see if param name starts with
            #    "person_" (stored in self.PARAM_PERSON_PREFIX).
            if ( param_name.startswith( self.PARAM_PERSON_PREFIX ) == True ):

                # person param.
                person_output_string_list.append( param_output_string )

            else:

                # article param.
                article_output_string_list.append( param_output_string )

            #-- END Check to see which list we append to. --#

        #-- END loop over expected parameters --#

        # initialize article and person parameter output strings.
        article_output_string = "Article_Data selection and network creation parameters:\n-----------------------------\n"
        person_output_string = "Person selection parameters:\n----------------------------\n"

        # now, join the parameters together for each, separated by "\n".
        list_separator_string = "\n"
        article_output_string += list_separator_string.join( article_output_string_list )
        person_output_string += list_separator_string.join( person_output_string_list )

        # And, finally, add them all together.
        string_OUT = article_output_string + "\n\n" + person_output_string

        return string_OUT

    #-- end method debug_parameters() ------------------------------------------


    def get_article_coder_id_list( self ):

        '''
        Checks to see if article coder list already populated.  If so, returns
            it.  If not, builds article coder ID list, stores it, then returns
            it.
        '''

        # return reference
        list_OUT = None

        # declare variables
        coder_id_list = None

        # try to set from instance variable.
        coder_id_list = self.m_article_coder_id_list

        # is it None?
        if ( coder_id_list is None ):

            # it is None.  Render list.
            coder_id_list = self.get_coder_id_list()

            # store it.
            self.m_article_coder_id_list = coder_id_list

            # and return it.
            list_OUT = self.m_article_coder_id_list

        else:

            # not None - return it.
            list_OUT = self.m_article_coder_id_list

        #-- END check to see if list populated. --#

        return list_OUT

    #-- END method get_article_coder_id_list --#


    def get_coder_id_list( self, param_prefix_IN = '' ):

        '''
        Builds coder ID list, then returns it.  To do this:
        - checks to see if prioritized list of coder IDs was in request.
        - If not, returns the unordered person ID list.
        - If so:

            - starts with prioritized list as a base.  Loops over IDs that
                are in the unordered list.  If any are not in prioritized
                list, appends them to the end.
            - return the merged list.

        Returns None if error.
        '''

        # return reference
        list_OUT = None

        # declare variables
        me = "get_coder_id_list"
        my_logger = None
        debug_message = None
        coder_list_IN = None
        coder_id_priority_list_IN = None
        coder_id_list = None
        coder_id_string = None
        coder_id = None

        # get logger
        my_logger = self.get_logger()

        # get the two places where coder IDs are stored.
        coder_list_IN = self.get_param_as_list( param_prefix_IN + NetworkOutput.PARAM_CODER_LIST )
        coder_id_priority_list_IN = self.get_string_param_as_list( param_prefix_IN + NetworkOutput.PARAM_CODER_ID_PRIORITY_LIST )

        debug_message = "In " + me + ": coder_list_IN = " + str( coder_list_IN ) + "; coder_id_priority_list_IN = " + str( coder_id_priority_list_IN )
        my_logger.debug( debug_message )

        # got a priority list?
        if ( ( coder_id_priority_list_IN is not None )
            and ( coder_id_priority_list_IN != "" )
            and ( len( coder_id_priority_list_IN ) > 0 ) ):

            # yes - use it.
            coder_id_list = coder_id_priority_list_IN

            # now, see if unordered list has anything in it.
            if ( ( coder_list_IN is not None )
                and ( coder_list_IN != "" )
                and ( len( coder_list_IN ) > 0 ) ):

                # loop
                for coder_id in coder_list_IN:

                    # see if it is in the output list.
                    if ( coder_id not in coder_id_list ):

                        # not in ther already - append().
                        coder_id_list.append( coder_id )

                    #-- END check to see if coder ID is in coder_id_list. --#

                #-- END loop over coder IDs in unordered list.

            #-- END check to see if unordered list. --#

        else:

            # no - use the normal list
            coder_id_list = coder_list_IN

        #-- END coder ID processing. --#

        # convert them all to integers and store in list_OUT
        list_OUT = []
        for coder_id_string in coder_id_list:

            # convert to int
            coder_id = int( coder_id_string )

            # add to output list.
            list_OUT.append( coder_id )

        #-- END loop over string coder IDs. --#

        debug_message = "In " + me + ": list_OUT = " + str( list_OUT )
        my_logger.debug( debug_message )

        return list_OUT

    #-- END method get_coder_id_list --#


    def get_file_extension( self ):

        # return reference
        value_OUT = None

        value_OUT = self.file_extension

        return value_OUT

    #-- END method get_file_extension() --#


    def get_mime_type( self ):

        # return reference
        value_OUT = None

        value_OUT = self.mime_type

        return value_OUT

    #-- END method get_mime_type() --#


    def get_NDO_instance( self, store_ndo_instance_IN = False ):

        '''
        Assumes there is an output type property specified in the POST parameters
            passed in as part of the current request.  Retrieves this output type,
            creates a NetworkDataOutput implementer instance to match the type,
            then returns the instance.  If no type or unknown type, returns None.
        '''

        # return reference
        NDO_instance_OUT = None

        # declare variables
        output_type_IN = ""

        # get output type.
        output_type_IN = self.get_param_as_str( self.PARAM_OUTPUT_TYPE )

        # make instance for output type.
        if ( output_type_IN == self.NETWORK_OUTPUT_TYPE_SIMPLE_MATRIX ):

            # simple matrix.
            NDO_instance_OUT = NDO_SimpleMatrix()

        elif ( output_type_IN == self.NETWORK_OUTPUT_TYPE_CSV_MATRIX ):

            # CSV matrix.
            NDO_instance_OUT = NDO_CSVMatrix()

        elif ( output_type_IN == self.NETWORK_OUTPUT_TYPE_TAB_DELIMITED_MATRIX ):

            # Tab-delimited matrix.
            NDO_instance_OUT = NDO_TabDelimitedMatrix()

        else:

            # no output type, or unknown.  Make simple output matrix.
            NDO_instance_OUT = NDO_SimpleMatrix()

        #-- END check to see what type we have. --#

        # set mime type and file extension from instance
        self.mime_type = NDO_instance_OUT.mime_type
        self.file_extension = NDO_instance_OUT.file_extension

        # store instance, as well?
        if ( store_ndo_instance_IN == True ):

            self.ndo_instance = NDO_instance_OUT

        #-- END check if we want to store the instance, as well. --#

        return NDO_instance_OUT

    #-- END get_NDO_instance() --#


    def get_person_coder_id_list( self ):

        '''
        Checks to see if person coder list already populated.  If so, returns
            it.  If not, builds article coder ID list, stores it, then returns
            it.
        '''

        # return reference
        list_OUT = None

        # declare variables
        coder_id_list = None

        # try to set from instance variable.
        coder_id_list = self.m_person_coder_id_list

        # is it None?
        if ( coder_id_list is None ):

            # it is None.  Render list.
            coder_id_list = self.get_coder_id_list( param_prefix_IN = self.PARAM_PERSON_PREFIX )

            # store it.
            self.m_person_coder_id_list = coder_id_list

            # and return it.
            list_OUT = self.m_person_coder_id_list

        else:

            # not None - return it.
            list_OUT = self.m_person_coder_id_list

        #-- END check to see if list populated. --#

        return list_OUT

    #-- END method get_person_coder_id_list --#


    def has_prioritized_coder_list( self, param_prefix_IN = "" ):

        '''
        Accepts param prefix.  Checks to see if there is a
            coder_id_priority_list set.  If so, return True.  If not, returns
            False.
        '''

        # return reference
        has_list_OUT = False

        # declare variables
        coder_id_priority_list_IN = None

        # try to get coder ID priority list.
        coder_id_priority_list_IN = self.get_param_as_list ( param_prefix_IN + NetworkOutput.PARAM_CODER_ID_PRIORITY_LIST )

        # anything in the list?
        if ( ( coder_id_priority_list_IN is not None )
            and ( isinstance( coder_id_priority_list_IN, list ) == True )
            and ( len( coder_id_priority_list_IN ) > 0 ) ):

            # yes.  Return True.
            has_list_OUT = True

        else:

            # no prioritized list.
            has_list_OUT = False

        #-- END check to see if prioritized list. --#

        return has_list_OUT

    #-- END method has_prioritized_coder_list() --#


    def process_network_output_request(
        self,
        request_IN = None,
        params_IN = None,
        debug_flag_IN = None,
        do_log_output_IN = False,
        output_log_label_IN = None
    ):

        # return reference
        data_OUT = None

        # declare variables
        me = "process_network_output_request"
        status_message = None
        debug_message = None
        my_debug_flag = None
        include_render_details_IN = ''
        include_render_details = False
        output_string = ''
        current_item = None
        network_query_set = None
        network_query_set_count = None
        article_data_count = ''
        query_counter = ''

        # declare variables - output logging
        data_spec_json = None
        data_output_request_type = None
        do_log_output = None
        do_save_data_to_db = None
        output_logger = None
        dataspec_json = None
        my_param_container = None
        add_timestamp_to_label = None
        output_log_label = None
        network_label_IN = None
        label_value = None
        output_type_IN = None

        # declare variables - save data to file system.
        file_extension = None
        save_data_in_folder_path_IN = None
        do_save_data_to_file = None
        file_extension = None
        data_file_name = None
        data_file_path = None
        data_file = None
        my_data_hash_hexdigest = None

        # declare variables - DEBUG
        coder_list_IN = None
        coder_id_priority_list_IN = None
        person_coder_list_IN = None
        person_coder_id_priority_list_IN = None

        # init debug
        my_debug_flag = NetworkDataOutput.DEBUG_FLAG
        if ( debug_flag_IN is not None ):
            my_debug_flag = debug_flag_IN
        #-- END check if debug flag passed in. --#

        # retrieve articles specified by the input parameters, then create
        #   string output, then pass it and form on to the output form.

        # initialize parameters
        if ( request_IN is not None ):

            # store request, and it will pull POST out of it.
            self.set_request( request_IN )

            # store some metadata, in case we are logging output.
            data_spec_json = self.get_parameters_dict()
            data_output_request_type = NetworkDataOutputLog.REQUEST_TYPE_HTTP_REQUEST

        elif ( params_IN is not None ):

            # no request, but parameters passed in. Just use those.
            self.store_parameters( params_IN )

            # store some metadata, in case we are logging output.
            data_spec_json = params_IN
            data_output_request_type = NetworkDataOutputLog.REQUEST_TYPE_JSON

        else:

            # no request or params. Error.
            status_message = "In {me}(): No request or params passed in. Nothing to be done.".format( me = me )
            raise ContextTextError( status_message )

        #-- END check to see

        #----------------------------------------
        # save to resulting data to file system?
        do_save_data_to_file = False
        save_data_in_folder_path_IN = self.get_param(
            NetworkOutput.PARAM_NAME_SAVE_DATA_IN_FOLDER,
            None
        )
        if ( ( save_data_in_folder_path_IN is not None ) and ( save_data_in_folder_path_IN != "" ) ):

            # looks like we have a file output folder path...
            do_save_data_to_file = True

        #-- END check if we save data to file --#

        #----------------------------------------
        # logging output?

        # retrieve database_output parameters.
        do_log_output = self.get_param_yes_no_as_boolean(
            NetworkOutput.PARAM_NAME_DATABASE_OUTPUT,
            default_IN = do_log_output_IN
        )

        # retrieve database_output parameters.
        do_save_data_to_db = self.get_param_yes_no_as_boolean(
            NetworkOutput.PARAM_NAME_DB_SAVE_DATA_IN_DATABASE,
            default_IN = True
        )

        # retrieve label information so it can be reused for file output.

        #----------------------------------------------------------------------#
        # ==> label

        # start with date-time string (standard value)
        current_date_time = datetime.datetime.now().strftime( '%Y%m%d-%H%M%S' )

        # retrieve network_label parameter.
        network_label_IN = self.get_param(
            NetworkOutput.PARAM_NETWORK_LABEL,
            None
        )

        # first, parameter passed in data spec takes precedence.
        if (
            ( network_label_IN is not None )
            and ( network_label_IN != "" )
        ):

            # network_label param - use it.
            label_value = network_label_IN

        else:

            # no data spec param, try parameter passed to method.
            label_value = output_log_label_IN

        #-- END check if label passed in. --#

        if ( do_log_output == True ):

            # yes. Create instance.
            output_logger = NetworkDataOutputLog()

            # and store request type and data spec JSON.
            output_logger.set_request_type( data_output_request_type )
            output_logger.set_data_spec_json( data_spec_json )

            #------------------------------------------------------------------#
            # label

            # start with request type and timestamp.
            output_log_label = "{request_type}-{timestamp_now}".format(
                request_type = output_logger.get_request_type(),
                timestamp_now = current_date_time
            )

            # do we want timestamp added to label?
            add_timestamp_to_label = self.get_param_yes_no_as_boolean(
                NetworkOutput.PARAM_DB_ADD_TIMESTAMP_TO_LABEL,
                default_IN = True
            )

            # got a label_value?
            if (
                ( label_value is not None )
                and ( label_value != "" )
            ):

                # yes - do we add_timestamp_to_label?
                if ( add_timestamp_to_label == True ):

                    # prepend it to label...
                    output_log_label = "{label_value}-{rest_of_label}".format(
                        label_value = label_value,
                        rest_of_label = output_log_label
                    )

                else:

                    # just the label, no time stamp.
                    output_log_label = label_value

                #-- END check if, when there is a label passed in, we want to add a timestamp --#

            #-- END check if label value --#

            # store label
            output_logger.set_label( output_log_label )
            self.last_label = output_log_label

            #------------------------------------------------------------------#
            # output_type --> network_data_format
            output_type_IN = self.get_param(
                NetworkOutput.PARAM_OUTPUT_TYPE,
                None
            )
            output_logger.set_network_data_format( output_type_IN )

            #------------------------------------------------------------------#
            # save()
            output_logger.save()

            #------------------------------------------------------------------#
            # tags - got a label_value?
            if ( label_value is not None ):

                # yes - add it and the label as tags.
                output_logger.tags.add( label_value )
                output_logger.tags.add( output_log_label )

            #-- END check if label value --#

        #-- END init logging output. --#

        # do we include details?
        include_render_details_IN = self.get_param(
            NetworkOutput.PARAM_NETWORK_INCLUDE_RENDER_DETAILS,
            NetworkOutput.CHOICE_NO
        )

        # convert include_render_details_IN to boolean
        if ( include_render_details_IN == NetworkOutput.CHOICE_YES ):

            # yes - True
            include_render_details = True

        else:

            # not yes, so False.
            include_render_details = False

        #-- END check to see whether we include render details --#

        debug_message = "In " + me + ": parameter debug - " + self.debug_parameters()
        self.output_debug( debug_message, do_print_IN = my_debug_flag )

        # get the two places where coder IDs are stored.
        coder_list_IN = self.get_param_as_list( NetworkOutput.PARAM_CODER_LIST )
        coder_id_priority_list_IN = self.get_string_param_as_list( NetworkOutput.PARAM_CODER_ID_PRIORITY_LIST )

        debug_message = "In " + me + ": coder_list_IN = " + str( coder_list_IN ) + "; coder_id_priority_list_IN = " + str( coder_id_priority_list_IN )
        self.output_debug( debug_message, do_print_IN = my_debug_flag )

        # get the two places where person coder IDs are stored.
        person_coder_list_IN = self.get_param_as_list( NetworkOutput.PARAM_PERSON_CODER_LIST )
        person_coder_id_priority_list_IN = self.get_string_param_as_list( NetworkOutput.PARAM_PERSON_CODER_ID_PRIORITY_LIST )

        debug_message = "In " + me + ": person_coder_list_IN = " + str( person_coder_list_IN ) + "; person_coder_id_priority_list_IN = " + str( person_coder_id_priority_list_IN )
        self.output_debug( debug_message, do_print_IN = my_debug_flag )

        # prepare data

        # retrieve Article_Data QuerySet based on parameters passed in.
        network_query_set = self.create_network_query_set()

        debug_message = "In {me}: type of network_query_set = {qs_type}".format(
            me = me,
            qs_type = str( type( network_query_set ) )
        )
        self.output_debug( debug_message, do_print_IN = my_debug_flag )

        # get count of queryset return items
        if ( network_query_set is not None ):

            article_data_count = network_query_set.count()

        else:

            article_data_count = -1

        #-- END check to see if None --#

        debug_message = "In {me}: before parameter and article details, Article_Data count: {article_data_count}.".format(
            me = me,
            article_data_count = article_data_count
        )
        self.output_debug( debug_message, do_print_IN = my_debug_flag )

        # include render details?
        if ( include_render_details == True ):

            # For now, output plain string
            output_string += "=======================\n"
            output_string += "parameter overview:\n"
            output_string += "=======================\n"
            output_string += "\n"
            output_string += self.debug_parameters()
            output_string += "\n"
            output_string += "\n"
            my_param_container = self.get_param_container()
            output_string += my_param_container.debug_parameters()

            #-------------------------------------------------------------------
            # summary info.
            #-------------------------------------------------------------------

            output_string += "\n\n\n"
            output_string += "=======================\n"
            output_string += "article overview:\n"
            output_string += "=======================\n"
            output_string += "\nTotal article data rows returned: " + str( article_data_count ) + "\n\n"

            # loop over the query set.
            query_counter = 0

            if ( network_query_set is not None ):

                for current_item in network_query_set:

                    query_counter += 1
                    output_string += "- " + str( query_counter ) + " ( id: " + str( current_item.article.id ) + " ) - " + current_item.article.headline + "\n"

                #-- END loop over articles to list out headlines. --#

            #-- END check to see if network_query_set is None --#

            # render and output networkd data.
            output_string += "\n\n"
            output_string += "=======================\n"
            output_string += "network data output:\n"
            output_string += "=======================\n"

        #-- END check to see if we include render details. --#

        self.output_debug( "In " + me + ": after parameter and article details, before rendering network." )

        # render the actual network data.
        output_string += self.render_network_data( network_query_set, debug_flag_IN = my_debug_flag )

        # include render details?
        if ( include_render_details == True ):

            output_string += "=======================\n"
            output_string += "END network data output\n"
            output_string += "=======================\n"

        #-- END check to see if we output render details --#

        data_OUT = output_string

        # write file to file system?

        # logging output?
        if ( do_log_output == True ):

            # only store to data base if told to do so.
            if ( do_save_data_to_db == True ):

                # store output and save.

                #------------------------------------------------------------------#
                # ==> network_data
                output_logger.set_network_data( data_OUT )

                #------------------------------------------------------------------#
                # save()
                output_logger.save()

            #-- END check

        #-- END check if output_logger instance present. --#

        # write data to file system?
        if ( do_save_data_to_file == True ):

            # we have been asked to save data file to file system.
            file_extension = self.get_file_extension()
            data_file_name = "{current_date_time}.{file_extension}".format(
                current_date_time = current_date_time,
                file_extension = file_extension
            )

            # got a label_value?
            if (
                ( label_value is not None )
                and ( label_value != "" )
            ):

                # yes - add to beginning of file name.
                data_file_name = "{label_value}-{rest_of_name}".format(
                    label_value = label_value,
                    rest_of_name = data_file_name
                )

            else:

                # no - create generic name.
                data_file_name = "{generic_label}-{rest_of_name}".format(
                    generic_label = "network_output_data",
                    rest_of_name = data_file_name
                )

            #-- END check if label value --#

            # create data file path from save folder path and name
            data_file_path = "{folder_path}/{data_file_name}".format(
                folder_path = save_data_in_folder_path_IN,
                data_file_name = data_file_name
            )

            # write data to specified file.
            with open( data_file_path, 'w' ) as data_file:

                # write!
                data_file.write( data_OUT )

                # logging?
                if ( do_log_output == True ):

                    #------------------------------------------------------------------#
                    # ==> network_data_file_path
                    output_logger.set_network_data_file_path( data_file_path )

                    # calculate and store hash
                    my_data_hash_hexdigest = output_logger.get_network_data_hash()
                    if ( ( my_data_hash_hexdigest is None ) or ( my_data_hash_hexdigest == "" ) ):

                        # no hash yet - make and store one.
                        my_data_hash_hexdigest = output_logger.make_string_hash( data_OUT )
                        output_logger.set_network_data_hash( my_data_hash_hexdigest )

                    #-- END check to see if hash set yet. --#

                    #------------------------------------------------------------------#
                    # save()
                    output_logger.save()

                #-- END check if logging --#

            #-- END with open( data_file_path, 'w') as data_file --#

        #-- END check if save data file to file system --#

        return data_OUT

    #-- END method process_network_output_request() --#


    def render_csv_article_data( self, query_set_IN ):

        """
            Accepts query set of articles.  Creates a new instance of the
                CsvArticleOutput class, places the query set in it, sets up its
                instance variables approrpiately according to the request, then
                renders CSV output and returns that output as a string.
                Uses the query set to output CSV data in the format specified in
                the output_type request parameter.  If one line per article, has
                sets of columns for as many authors and sources as are present in
                the articles with the most authors and sources, respectively.  If
                one line per source, each article is given a line for each source
                with all other article information duplicated for each source. If
                one line per author, each article is given a line for each author
                with all other article information duplicated for each author.

            Preconditions: assumes that we have a query set of articles passed
                in that we can store in the instance.  If not, does nothing,
                returns empty string.

            Postconditions: returns the CSV network data, in a string.

            Parameters:
            - query_set_IN - django HTTP request instance that contains parameters we use to generate network data.

            Returns:
            - String - CSV output for the network described by the articles selected based on the parameters passed in.
        """

        # return reference
        csv_OUT = ''

        # declare variables
        my_params = None
        csv_outputter = None
        output_type_IN = ''
        header_prefix_IN = ''

        # do we have a query set?
        if ( query_set_IN ):

            # retrieve the output type and header_prefix.
            my_params = self.get_param_container()
            output_type_IN = my_params.get_param_as_str( NetworkOutput.PARAM_OUTPUT_TYPE, '' )
            header_prefix_IN = my_params.get_param_as_str( NetworkOutput.PARAM_HEADER_PREFIX, '' )

            # create instance of CsvArticleOutput.
            csv_outputter = CsvArticleOutput()

            # initialize it.
            csv_outputter.set_output_type( output_type_IN )
            csv_outputter.set_query_set( query_set_IN )
            csv_outputter.header_prefix = header_prefix_IN

            # render and return the result.
            csv_OUT = csv_outputter.render()

        #-- END check to make sure we have a query set. --#

        return csv_OUT

    #-- END render_csv_article_data() --#


    def remove_duplicate_article_data( self, query_set_IN, param_prefix_IN ):

        """
            Accepts query set of Article_Data.  Designed to make sure we only
            have one data record per article.  This could be a good idea in
            some cases, and could be a bad idea in others...

            Preconditions: assumes that we have a query set of Article_Data
                instances passed in that we can interact with to look for
                duplicates.  If not, does nothing.

            Postconditions: returns a query set with a not IN filter that omits
                Article_Data instances past the first it encounters for a given
                article.

            Parameters:
            - query_set_IN - django QuerySet instance that contains Article_Data instances.

            Returns:
            - QuerySet - QuerySet of Article_Data instances with only one Article_Data row per Article.  If nothing to remove, just returns QuerySet passed in.  If something other than a QuerySet passed in, just returns it.
        """

        # ! TODO - test!

        # return reference
        qs_OUT = ''

        # declare variables
        me = "remove_duplicate_article_data"
        my_logger = None
        unique_article_id_to_article_data_id_dict = {}
        unique_article_id_to_article_data_map = {}
        has_prioritized_coders = False
        prioritized_coder_id_list = None
        current_article_data = None
        current_article = None
        current_unique_id = ''
        current_id = -1
        current_coder = None
        current_coder_id = -1
        current_coder_index = -1
        current_article_data_id = -1
        selected_article_data = None
        selected_article_data_id = -1
        selected_coder = None
        selected_coder_id = -1
        selected_coder_index = -1
        omit_id_list = []

        # get logger
        my_logger = self.get_logger()

        my_logger.debug( "In " + me + ": beginning of method: count of query_set_IN = " + str( query_set_IN.count() ) )

        # to start, set return QuerySet to QuerySet passed in.
        qs_OUT = query_set_IN

        # do we have a query set?
        if query_set_IN is not None:

            # get prioritized coder list?
            has_prioritized_coders = self.has_prioritized_coder_list( param_prefix_IN )
            if ( has_prioritized_coders == True ):

                # yes - retrieve.
                prioritized_coder_id_list = self.get_coder_id_list( param_prefix_IN )

            #-- END check to see if prioritized coders? --#

            # loop over the article data
            for current_article_data in query_set_IN:

                # got an article?
                current_article = current_article_data.article
                if ( current_article ):

                    # yes - get unique identifier of article
                    current_unique_id = current_article.unique_identifier
                    current_id = current_article.id

                    # get ID of current Article_Data row.
                    current_article_data_id = current_article_data.id

                    #my_logger.debug( "In " + me + ": current_article = id: " + str( current_id ) + "; current_unique_id = " + str( current_unique_id ) )

                    # is the unique_id in the dict?
                    if current_unique_id in unique_article_id_to_article_data_id_dict:

                        # yes - so, this is a duplicate.  Do we have prioritized
                        #     coders?
                        if ( has_prioritized_coders == True ):

                            # prioritized coders.  Get instance for current
                            #     selected article, then get ID of coder.
                            selected_article_data = unique_article_id_to_article_data_map[ current_unique_id ]
                            selected_article_data_id = selected_article_data.id
                            selected_coder = selected_article_data.coder
                            selected_coder_id = selected_coder.id

                            # get selected index from prioritized list.
                            selected_coder_index = prioritized_coder_id_list.index( selected_coder_id )

                            # get coder ID and index from current.
                            current_coder = current_article_data.coder
                            current_coder_id = current_coder.id
                            current_coder_index = prioritized_coder_id_list.index( current_coder_id )

                            # if current index less than selected_value...
                            if ( current_coder_index < selected_coder_index ):

                                # this is highest priority yet. store current
                                #     rather than selected.
                                unique_article_id_to_article_data_id_dict[ current_unique_id ] = current_article_data_id
                                unique_article_id_to_article_data_map[ current_unique_id ] = current_article_data

                                # add selected to the omit list.
                                omit_id_list.append( selected_article_data_id )

                            else:

                                # not a higher priority - add to omit list.
                                omit_id_list.append( current_article_data_id )

                            #-- END check to see if higher priority. --#

                        else:

                            # No prioritization - first come, first served.
                            #     Add id to omit list.
                            omit_id_list.append( current_article_data_id )

                        #-- END check to see if prioritized coder list. --#

                    else:

                        # not in dict, so add it and its ID and instance.
                        unique_article_id_to_article_data_id_dict[ current_unique_id ] = current_article_data_id
                        unique_article_id_to_article_data_map[ current_unique_id ] = current_article_data

                    #-- END check to see if duplicate. --#

                #-- END check to see if we have an article. --#

            #-- END loop over article data --#

            # anything in omit list?
            if ( len( omit_id_list ) > 0 ):

                # IDs to omit.
                qs_OUT = qs_OUT.exclude( id__in = omit_id_list )

            #-- END check to see if we have to omit IDs --#

        #-- END check to make sure we have a query set. --#

        my_logger.debug( "In " + me + ": end of method: count of qs_OUT = " + str( qs_OUT.count() ) )

        return qs_OUT

    #-- END remove_duplicate_article_data() --#


    def render_network_data( self, query_set_IN, debug_flag_IN = None, save_ndo_IN = False ):

        """
            Accepts query set of Article_Data.  Creates a new instance of the
                requested output class, places the query set in it, sets up its
                instance variables appropriately according to the request, then
                renders output and returns that output as a string.

            Preconditions: assumes that we have a query set of articles passed
                in that we can store in the instance.  If not, does nothing,
                returns empty string.

            Postconditions: returns the CSV network data, in a string.

            Parameters:
            - query_set_IN - django HTTP request instance that contains parameters we use to generate network data.

            Returns:
            - String - output for the network described by the articles selected based on the parameters passed in.
        """

        # return reference
        network_OUT = ''

        # declare variables
        me = "render_network_data"
        my_debug_flag = None
        debug_message = None
        network_data_outputter = None
        person_dictionary = None
        my_params = None

        # init debug
        my_debug_flag = NetworkDataOutput.DEBUG_FLAG
        if ( debug_flag_IN is not None ):
            my_debug_flag = debug_flag_IN
        #-- END check if debug flag passed in. --#

        # do we have a query set?
        if ( query_set_IN ):

            debug_message = "in {me}: Article_Data QuerySet size = {qs_count}".format(
                me = me,
                qs_count = query_set_IN.count()
            )
            self.output_debug( debug_message, do_print_IN = my_debug_flag )

            # create the person_dictionary
            person_dictionary = self.create_person_dict( debug_flag_IN = my_debug_flag )

            debug_message = "in {me}: person dictionary size = {person_count}".format(
                me = me,
                person_count = len( person_dictionary )
            )
            self.output_debug( debug_message, do_print_IN = my_debug_flag )

            # create instance of NetworkDataOutput.
            network_data_outputter = self.get_NDO_instance( store_ndo_instance_IN = save_ndo_IN )

            debug_message = "in {me}: retrieved NDO instance of type = {ndo_type}".format(
                me = me,
                ndo_type = type( network_data_outputter )
            )
            self.output_debug( debug_message, do_print_IN = my_debug_flag )

            # initialize it.
            network_data_outputter.set_query_set( query_set_IN )
            network_data_outputter.set_person_dictionary( person_dictionary )

            # initialize NetworkDataOutput instance from params.
            my_params = self.get_param_container()
            network_data_outputter.initialize_from_params( my_params )

            debug_message = "in {me}: After NDO init, before render()".format( me = me )
            self.output_debug( debug_message, do_print_IN = my_debug_flag )

            # render and return the result.
            network_OUT = network_data_outputter.render()

            debug_message = "in {me}: After render() - NDO debug = {ndo_debug}".format(
                me = me,
                ndo_debug = network_data_outputter.debug
            )
            self.output_debug( debug_message, do_print_IN = my_debug_flag )

            # add some debug?
            if ( my_debug_flag == True ):

                # yup.
                network_OUT += "\n\n" + network_data_outputter.debug + "\n\n"

            #-- END check to see if we have debug to output. --#

        #-- END check to make sure we have a query set. --#

        return network_OUT

    #-- END render_network_data() --#


    def set_file_extension( self, value_IN ):

        # return reference
        value_OUT = None

        self.file_extension = value_IN

        value_OUT = self.get_file_extension()

        return value_OUT

    #-- END method get_file_extension() --#


    def set_mime_type( self, value_IN ):

        # return reference
        value_OUT = None

        self.mime_type = value_IN

        value_OUT = self.get_mime_type()

        return value_OUT

    #-- END method get_mime_type() --#


#-- END class NetworkOutput --#
