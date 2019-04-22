from __future__ import unicode_literals
from __future__ import division

'''
Copyright 2010-2014 Jonathan Morgan

This file is part of http://github.com/jonathanmorgan/context_text.

context_text is free software: you can redistribute it and/or modify it under the terms of the GNU Lesser General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.

context_text is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.

You should have received a copy of the GNU Lesser General Public License along with http://github.com/jonathanmorgan/context_text. If not, see http://www.gnu.org/licenses/.
'''

__author__="jonathanmorgan"
__date__ ="$May 1, 2010 6:26:35 PM$"

if __name__ == "__main__":
    print( "Hello World" )

#===============================================================================
# imports (in alphabetical order by package, then by name)
#===============================================================================

# python libraries
from abc import ABCMeta, abstractmethod

#import copy

# import six for Python 2 and 3 compatibility.
import six

# Django DB classes, just to play with...
#from django.db.models import Count # for aggregating counts of authors, sources.
#from django.db.models import Max   # for getting max value of author, source counts.

# python_utilities
from python_utilities.parameters.param_container import ParamContainer

# Import the classes for our context_text application
#from context_text.models import Article
#from context_text.models import Article_Author
from context_text.models import Article_Subject
#from context_text.models import Person
#from context_text.models import Topic

# Import context_text shared classes.
from context_text.shared.context_text_base import ContextTextBase


#===============================================================================
# classes (in alphabetical order by name)
#===============================================================================

class NetworkDataOutput( ContextTextBase ):

    
    #---------------------------------------------------------------------------
    # META!!!
    #---------------------------------------------------------------------------

    
    __metaclass__ = ABCMeta


    #---------------------------------------------------------------------------
    # CONSTANTS-ish
    #---------------------------------------------------------------------------


    # network output type constants
    
    # Network data format output types
    NETWORK_DATA_FORMAT_SIMPLE_MATRIX = "simple_matrix"
    NETWORK_DATA_FORMAT_CSV_MATRIX = "csv_matrix"
    NETWORK_DATA_FORMAT_TAB_DELIMITED_MATRIX = "tab_delimited_matrix"
    NETWORK_DATA_FORMAT_DEFAULT = NETWORK_DATA_FORMAT_TAB_DELIMITED_MATRIX
    
    NETWORK_DATA_FORMAT_CHOICES_LIST = [
        ( NETWORK_DATA_FORMAT_SIMPLE_MATRIX, "Simple Matrix" ),
        ( NETWORK_DATA_FORMAT_CSV_MATRIX, "CSV Matrix" ),
        ( NETWORK_DATA_FORMAT_TAB_DELIMITED_MATRIX, "Tab-Delimited Matrix" ),
    ]

    # Network data output types
    NETWORK_DATA_OUTPUT_TYPE_NETWORK = "network"
    NETWORK_DATA_OUTPUT_TYPE_ATTRIBUTES = "attributes"
    NETWORK_DATA_OUTPUT_TYPE_NET_AND_ATTR_COLS = "net_and_attr_cols"
    NETWORK_DATA_OUTPUT_TYPE_NET_AND_ATTR_ROWS = "net_and_attr_rows"
    NETWORK_DATA_OUTPUT_TYPE_DEFAULT = NETWORK_DATA_OUTPUT_TYPE_NET_AND_ATTR_COLS
    
    NETWORK_DATA_OUTPUT_TYPE_CHOICES_LIST = [
        ( NETWORK_DATA_OUTPUT_TYPE_NETWORK, "Just Network" ),
        ( NETWORK_DATA_OUTPUT_TYPE_ATTRIBUTES, "Just Attributes" ),
        ( NETWORK_DATA_OUTPUT_TYPE_NET_AND_ATTR_COLS, "Network + Attribute Columns" ),
        ( NETWORK_DATA_OUTPUT_TYPE_NET_AND_ATTR_ROWS, "Network + Attribute Rows" ),
    ]

    # Person Query Types
    PERSON_QUERY_TYPE_ALL = "all"
    PERSON_QUERY_TYPE_ARTICLES = "articles"
    PERSON_QUERY_TYPE_CUSTOM = "custom"
    PERSON_QUERY_TYPE_DEFAULT = PERSON_QUERY_TYPE_ARTICLES

    PERSON_QUERY_TYPE_CHOICES_LIST = [ 
        ( PERSON_QUERY_TYPE_ALL, "All persons" ),
        ( PERSON_QUERY_TYPE_ARTICLES, "From selected articles" ),
        ( PERSON_QUERY_TYPE_CUSTOM, "Custom, defined below" ),
    ]

    # Filtering Article_Data on coder_type.
    CODER_TYPE_FILTER_TYPE_NONE = ContextTextBase.CODER_TYPE_FILTER_TYPE_NONE
    CODER_TYPE_FILTER_TYPE_AUTOMATED = ContextTextBase.CODER_TYPE_FILTER_TYPE_AUTOMATED
    CODER_TYPE_FILTER_TYPE_ALL = ContextTextBase.CODER_TYPE_FILTER_TYPE_ALL
    CODER_TYPE_FILTER_TYPE_DEFAULT = ContextTextBase.CODER_TYPE_FILTER_TYPE_DEFAULT
    
    CODER_TYPE_FILTER_TYPE_CHOICES_LIST = [ 
        ( CODER_TYPE_FILTER_TYPE_NONE, "Do not filter" ),
        ( CODER_TYPE_FILTER_TYPE_AUTOMATED, "Just automated" ),
        ( CODER_TYPE_FILTER_TYPE_ALL, "All users" ),
    ]

    # person types
    PERSON_TYPE_UNKNOWN = 'unknown'
    PERSON_TYPE_AUTHOR = 'author'
    PERSON_TYPE_SOURCE = 'source'
    PERSON_TYPE_BOTH = 'both'
    PERSON_TYPE_TO_ID = {
        PERSON_TYPE_UNKNOWN : 1,
        PERSON_TYPE_AUTHOR : 2,
        PERSON_TYPE_SOURCE : 3,
        PERSON_TYPE_BOTH : 4
    }

    # status variables
    STATUS_OK = "OK!"
    STATUS_ERROR_PREFIX = "Error: "

    # variables for choosing yes or no.
    CHOICE_YES = 'yes'
    CHOICE_NO = 'no'

    # source types
    SOURCE_TYPE_INDIVIDUAL = 'individual'

    # source contact types
    SOURCE_CONTACT_TYPE_DIRECT = 'direct'
    SOURCE_CONTACT_TYPE_EVENT = 'event'

    # DEBUG constant
    DEBUG_FLAG = False

    # parameter constants
    PARAM_OUTPUT_TYPE = 'output_type'
    PARAM_NETWORK_DOWNLOAD_AS_FILE = 'network_download_as_file'
    PARAM_NETWORK_LABEL = 'network_label'
    PARAM_NETWORK_DATA_OUTPUT_TYPE = 'network_data_output_type'   # type of data you want to output - either just the network, just node attributes, or network with attributes in same table, either with attributes as additional rows or additional columns.
    PARAM_NETWORK_INCLUDE_HEADERS = 'network_include_headers'
    PARAM_NETWORK_INCLUDE_RENDER_DETAILS = 'network_include_render_details'
    PARAM_SOURCE_CAPACITY_INCLUDE_LIST = Article_Subject.PARAM_SOURCE_CAPACITY_INCLUDE_LIST
    PARAM_SOURCE_CAPACITY_EXCLUDE_LIST = Article_Subject.PARAM_SOURCE_CAPACITY_EXCLUDE_LIST
    PARAM_SOURCE_CONTACT_TYPE_INCLUDE_LIST = Article_Subject.PARAM_SOURCE_CONTACT_TYPE_INCLUDE_LIST
    PARAM_PERSON_QUERY_TYPE = "person_query_type"
    PARAM_CODER_TYPE_FILTER_TYPE = "coder_type_filter_type"
    PARAM_PERSON_CODER_TYPE_FILTER_TYPE = "person_" + PARAM_CODER_TYPE_FILTER_TYPE
    
    # node attributes
    NODE_ATTRIBUTE_PERSON_ID = "person_id"
    NODE_ATTRIBUTE_PERSON_TYPE = "person_type"
    NODE_ATTRIBUTE_LIST = [
        NODE_ATTRIBUTE_PERSON_ID,
        NODE_ATTRIBUTE_PERSON_TYPE,
    ]


    #---------------------------------------------------------------------------
    # __init__() method
    #---------------------------------------------------------------------------


    def __init__( self ):

        # call parent's __init__()
        super( NetworkDataOutput, self ).__init__()

        # declare variables
        self.query_set = None
        self.output_type = NetworkDataOutput.NETWORK_DATA_FORMAT_DEFAULT
        self.data_format = NetworkDataOutput.NETWORK_DATA_FORMAT_DEFAULT
        self.data_output_type = NetworkDataOutput.NETWORK_DATA_OUTPUT_TYPE_DEFAULT
        self.include_render_details = False
        self.person_dictionary = {}
        self.network_label = '' # heading to put in first line of network data.
        self.relation_map = {}
        self.include_row_and_column_headers = False
        
        # variables for outputting result as file
        self.mime_type = ""
        self.file_extension = ""
        
        # need a way to keep track of who is a reporter and who is a source.
        # person ID to person type map
        self.person_type_dict = {}

        # variable to hold master person list.
        self.master_person_list = []

        # internal debug string
        self.debug = "NetworkDataOutput debug:\n\n"

        # inclusion parameter holder
        self.inclusion_params = {}

        # set logger name (for LoggingHelper parent class: (LoggingHelper --> BasicRateLimited --> ContextTextBase --> ArticleCoding).
        self.set_logger_name( "context_text.export.network_data_output" )
        
    #-- END method __init__() --#


    #---------------------------------------------------------------------------
    # instance methods, in alphabetical order
    #---------------------------------------------------------------------------


    def add_directed_relation( self, person_from_id_IN, person_to_id_IN ):

        """
            Method: add_directed_relation()

            Purpose: Accepts two person IDs.  For the from person, goes into the
               nested connection map, grabs that person's connection dictionary,
               and checks if the to person is in the map.  If so, grabs the
               counter for number of contacts and increments it by one.  If not,
               adds the person and sets counter to 1.

            Preconditions: connection_map must be initialized to a dictionary.

            Params:
            - person_from_id_IN - person ID of 1st person to connect.
            - person_to_id_IN - person ID of 2nd person to connect.

            Returns:
            - string status message, either STATUS_OK if success, or
               STATUS_ERROR_PREFIX followed by descriptive error message.
        """

        # return reference
        status_OUT = NetworkDataOutput.STATUS_OK

        # declare variables
        my_relation_map = None
        person_relations = None
        current_person_count = -1
        updated_person_count = -1

        # got two IDs?
        if ( person_from_id_IN and person_to_id_IN ):

            # got IDs.  retrieve relation_map.
            my_relation_map = self.get_relation_map()

            # got a map?
            if ( my_relation_map is not None ):

                # look for from person in map.
                if person_from_id_IN in my_relation_map:

                    # already there - grab their relations map.
                    person_relations = my_relation_map[ person_from_id_IN ]

                else:

                    # not yet in connection map.  Create a dictionary to hold
                    #    their relations.
                    person_relations = {}

                    # store it in the relation map
                    my_relation_map[ person_from_id_IN ] = person_relations

                #- END check to see if person has relations. --#

                # is to person in relations map?
                if person_to_id_IN in person_relations:

                    # yes.  Retrieve that person's value, add one, and place
                    #    incremented value back in hash.
                    current_person_count = person_relations[ person_to_id_IN ]
                    updated_person_count = current_person_count + 1

                else: # not already connected.

                    # not in person relations.  Set count to 1
                    updated_person_count = 1

                #-- END check to see if already are connected. --#

                # update the count.
                person_relations[ person_to_id_IN ] = updated_person_count

            #-- END sanity check to make sure we have a map.

        #-- END check to make sure we have IDs. --#

        if ( self.DEBUG_FLAG == True ):
            # output the author map
            self.debug += "\n\n*** in add_directional_relation, after adding relations, my_relation_map:\n" + str( my_relation_map ) + "\n\n"
        #-- END DEBUG --#

        return status_OUT

    #-- END method add_directed_relation --#


    def add_reciprocal_relation( self, person_1_id_IN, person_2_id_IN ):

        """
            Method: add_reciprocal_relation()

            Purpose: Accepts two person IDs.  For each, goes into the nested
               connection map, grabs that person's connection dictionary, and
               checks if the other person is in the map.  If so, grabs the
               counter for number of contacts and increments it by one.  If not,
               adds the person and sets counter to 1.

            Preconditions: connection_map must be initialized to a dictionary.

            Params:
            - person_1_id_IN - person ID of 1st person to connect.
            - person_2_id_IN - person ID of 2nd person to connect.

            Returns:
            - string status message, either STATUS_OK if success, or
               STATUS_ERROR_PREFIX followed by descriptive error message.
        """

        # return reference
        status_OUT = NetworkDataOutput.STATUS_OK
        
        # declare variables
        me = "add_reciprocal_relation"
        my_logger = None
        debug_string = ""
        
        # initialize logger
        my_logger = self.get_logger()

        # make sure we have two values.
        if ( person_1_id_IN and person_2_id_IN ):

            if ( self.DEBUG_FLAG == True ):

                # output message about having two values.
                debug_string = "In " + me + ": got two IDs: " + str( person_1_id_IN ) + "; " + str( person_2_id_IN ) + "."
                
                # add to debug string?
                self.debug += "\n\n" + debug_string + "\n\n"
                
                my_logger.debug( debug_string )
                            
            #-- END DEBUG --#

            # add directed relations from 1 to 2 and from 2 to 1.
            self.add_directed_relation( person_1_id_IN, person_2_id_IN )
            self.add_directed_relation( person_2_id_IN, person_1_id_IN )

            if ( self.DEBUG_FLAG == True ):
                # output the author map
                self.debug += "\n\n*** in add_reciprocal_relation, after adding relations, relation_map:\n" + str( self.relation_map ) + "\n\n"
            #-- END DEBUG --#

        else:

            # error, something is missing.
            status_OUT = NetworkDataOutput.STATUS_ERROR_PREFIX + "in add_reciprocal relationship, one or more IDs is missing, so can't create relationship."

            if ( self.DEBUG_FLAG == True ):
                # output the author map
                self.debug += "\n\n" + status_OUT + "\n\n"
            #-- END DEBUG --#

        #-- END check to make sure we have values. --#

        return status_OUT

    #-- END method add_reciprocal_relation --#


    def create_header_list( self ):

        """
            Method: create_header_list()

            Purpose: checks data_output_type, renders header list based on what
               data we are outputting.  Returns list of headers.

            Returns:
            - List of headers for our CSV document.
        """

        # return reference
        header_list_OUT = None

        # declare variables
        my_data_output_type = ""
        node_attribute_list = []
        current_attr_name = ""

        # get the data output type.
        my_data_output_type = self.data_output_type
        
        # only need to get list of labels if we are outputting network as well as attributes.

        # include network?
        if ( ( my_data_output_type == NetworkDataOutput.NETWORK_DATA_OUTPUT_TYPE_NETWORK )
            or ( my_data_output_type == NetworkDataOutput.NETWORK_DATA_OUTPUT_TYPE_NET_AND_ATTR_COLS )
            or ( my_data_output_type == NetworkDataOutput.NETWORK_DATA_OUTPUT_TYPE_NET_AND_ATTR_ROWS ) ):

            # yes.  Start with list of labels.
            header_list_OUT = self.create_label_list()
            
        else:
        
            # not outputting whole network.  Start with empty list.
            header_list_OUT = []
            
        #-- END check to see if outputting network. --#
        
        # add "id" to the beginning of list (header for column of labels that
        #    starts each row).
        header_list_OUT.insert( 0, "id" )
        
        # Are we outputting attributes in columns, either just attributes, or network plus attributes as columns?
        if ( ( my_data_output_type == NetworkDataOutput.NETWORK_DATA_OUTPUT_TYPE_ATTRIBUTES )
            or ( my_data_output_type == NetworkDataOutput.NETWORK_DATA_OUTPUT_TYPE_NET_AND_ATTR_COLS ) ):

            # we are - add column headers for attributes - loop over NODE_ATTRIBUTE_LIST.
            node_attribute_list = NetworkDataOutput.NODE_ATTRIBUTE_LIST
            for current_attr_name in node_attribute_list:
            
                # add the attribute name to the list.
                header_list_OUT.append( current_attr_name )
            
            #-- END loop over attributes
            
        #-- END check to see if output attributes as columns --#

        return header_list_OUT

    #-- END method create_header_list --#


    def create_label_list( self, quote_character_IN = '' ):

        """
            Method: create_label_list()

            Purpose: retrieves the master person list from the instance, uses it
               to output a list of the person IDS and their source types.  Each
               person's label consists of:
               "<person_counter>__<person_id>__<person_type>"
               WHERE:
               - <person_counter> is the simple integer count of people in list, incremented as each person is added.
               - <person_id> is the ID of the person's Person record in the system.
               - <person_type> is the string person type of the person, then a hyphen, then the person type ID of that type.

            Returns:
            - list of string representation of labels for each row in network.
        """

        # return reference
        list_OUT = []

        # declare variables
        master_list = None
        my_label = ''
        current_person_id = -1
        person_count = -1
        current_type = ''
        current_type_id = -1
        current_label = ""
        current_value = ''
        unknown_count = 0
        author_count = 0
        source_count = 0
        both_count = 0

        # get master list
        master_list = self.get_master_person_list()

        # got something?
        if ( master_list ):

            # loop over sorted person list, building label line for each person.
            person_count = 0
            for current_person_id in sorted( master_list ):

                person_count += 1
                
                # get current person type and type ID
                current_type = self.get_person_type( current_person_id )
                current_type_id = self.get_person_type_id( current_person_id )

                # increment count
                if ( current_type == NetworkDataOutput.PERSON_TYPE_UNKNOWN ):
                    unknown_count += 1
                elif ( current_type == NetworkDataOutput.PERSON_TYPE_AUTHOR ):
                    author_count += 1
                elif ( current_type == NetworkDataOutput.PERSON_TYPE_SOURCE ):
                    source_count += 1
                elif ( current_type == NetworkDataOutput.PERSON_TYPE_BOTH ):
                    both_count += 1

                # get label
                current_label = self.get_person_label( current_person_id )

                # append the person's row to the output string.
                current_value = str( person_count ) + "__" + current_label

                # do we want quotes?
                if ( quote_character_IN != '' ):

                    # yes.  Add quotes around the value.
                    current_value = quote_character_IN + current_value + quote_character_IN

                #-- END quote values check --#

                # append to output
                list_OUT.append( current_value )

            #-- END loop over persons. --#

            # append counts
            #string_OUT += "\n\ntotals: unknown=" + str( unknown_count ) + "; author=" + str( author_count ) + "; source=" + str( source_count ) + "; both=" + str( both_count ) + "\n\n"

        #-- END check to make sure we have a person list. --#

        return list_OUT

    #-- END method create_label_list --#


    def create_person_id_list( self, as_string_IN = True ):

        """
            Method: create_person_id_list()

            Purpose: Create a list of person IDs for the people in master
               list.

            Preconditions: Master person list must be present.

            Params: none

            Returns:
            - list_OUT - list of person IDs, in sorted master person list order.
        """

        # return reference
        list_OUT = []

        # declare variables
        person_list = None
        current_person_id = -1
        output_person_id = -1

        # get master list
        person_list = self.get_master_person_list()

        # got it?
        if ( person_list ):

            # loop over the master list.
            for current_person_id in sorted( person_list ):
            
                # store in output variable
                output_person_id = current_person_id

                # append as a string?
                if ( as_string_IN == True ):

                    output_person_id = str( output_person_id )

                #-- END check to see if append as string --#

                # append to output list.
                list_OUT.append( output_person_id )

            #-- END loop over people --#

        #-- END check to make sure we have list.

        return list_OUT

    #-- END method create_person_id_list --#


    def create_person_type_id_list( self, as_string_IN = True ):

        """
            Method: create_person_type_id_list()

            Purpose: Create a list of person type IDs for the people in master
               list, for use in assigning person type attributes to the
               corresponding people/nodes.

            Preconditions: Master person list must be present.

            Params: none

            Returns:
            - list_OUT - list of person IDs, in sorted master person list order.
        """

        # return reference
        list_OUT = []

        # declare variables
        person_list = None
        current_person_id = -1
        current_person_type_id = -1

        # get master list
        person_list = self.get_master_person_list()

        # got it?
        if ( person_list ):

            # loop over the master list, look for each in the map of person to
            #    type.  If found, append type.  If not found, append "unknown".
            for current_person_id in sorted( person_list ):

                # get person's type
                current_person_type_id = self.get_person_type_id( current_person_id )

                # append as a string?
                if ( as_string_IN == True ):

                    current_person_type_id = str( current_person_type_id )

                #-- END check to see if append as string --#

                # append to output list.
                list_OUT.append( current_person_type_id )

            #-- END loop over people --#

        #-- END check to make sure we have list.

        return list_OUT

    #-- END method create_person_type_id_list --#


    def do_output_attribute_columns( self ):

        """
            Method: do_output_attribute_columns()

            Purpose: Examines self.data_output_type to see if we are to output
               node attribute rows.  If so, returns True, if not, returns False.
               Values that mean we output attribute columns:
               - NetworkDataOutput.NETWORK_DATA_OUTPUT_TYPE_ATTRIBUTES
               - NetworkDataOutput.NETWORK_DATA_OUTPUT_TYPE_NET_AND_ATTR_COLS

            Returns:
            - boolean - If we are to output attribute columns, returns True.  If not, returns False.
        """

        # return reference
        do_it_OUT = False

        # declare variables
        my_data_output_type = ""

        # get data output type
        my_data_output_type = self.data_output_type
        
        # do the output?
        if ( ( my_data_output_type == NetworkDataOutput.NETWORK_DATA_OUTPUT_TYPE_ATTRIBUTES )
            or ( my_data_output_type == NetworkDataOutput.NETWORK_DATA_OUTPUT_TYPE_NET_AND_ATTR_COLS ) ):

            # yes.
            do_it_OUT = True

        else:
        
            # no.
            do_it_OUT = False
    
        #-- END check to see if include network matrix --#

        return do_it_OUT

    #-- END method do_output_attribute_columns() --#


    def do_output_attribute_rows( self ):

        """
            Method: do_output_attribute_rows()

            Purpose: Examines self.data_output_type to see if we are to output
               node attribute rows.  If so, returns True, if not, returns False.
               Values that mean we output attribute rows:
               - NetworkDataOutput.NETWORK_DATA_OUTPUT_TYPE_NET_AND_ATTR_ROWS

            Returns:
            - boolean - If we are to output attribute rows, returns True.  If not, returns False.
        """

        # return reference
        do_it_OUT = False

        # declare variables
        my_data_output_type = ""

        # get data output type
        my_data_output_type = self.data_output_type
        
        # do the output?
        if ( my_data_output_type == NetworkDataOutput.NETWORK_DATA_OUTPUT_TYPE_NET_AND_ATTR_ROWS ):

            # yes.
            do_it_OUT = True

        else:
        
            # no.
            do_it_OUT = False
    
        #-- END check to see if include network matrix --#

        return do_it_OUT

    #-- END method do_output_attribute_rows() --#


    def do_output_network( self ):

        """
            Method: do_output_network()

            Purpose: Examines self.data_output_type to see if we are to output
               network data.  If so, returns True, if not, returns False.
               Values that mean we output network data:
               - NetworkDataOutput.NETWORK_DATA_OUTPUT_TYPE_NETWORK
               - NetworkDataOutput.NETWORK_DATA_OUTPUT_TYPE_NET_AND_ATTR_COLS
               - NetworkDataOutput.NETWORK_DATA_OUTPUT_TYPE_NET_AND_ATTR_ROWS

            Returns:
            - boolean - If we are to output network data, returns True.  If not, returns False.
        """

        # return reference
        do_it_OUT = False

        # declare variables
        my_data_output_type = ""

        # get data output type
        my_data_output_type = self.data_output_type
        
        # include network?
        if ( ( my_data_output_type == NetworkDataOutput.NETWORK_DATA_OUTPUT_TYPE_NETWORK )
            or ( my_data_output_type == NetworkDataOutput.NETWORK_DATA_OUTPUT_TYPE_NET_AND_ATTR_COLS )
            or ( my_data_output_type == NetworkDataOutput.NETWORK_DATA_OUTPUT_TYPE_NET_AND_ATTR_ROWS ) ):

            # yes, we output network.
            do_it_OUT = True

        else:
        
            # no, not outputting network.
            do_it_OUT = False
    
        #-- END check to see if include network matrix --#

        return do_it_OUT

    #-- END method do_output_network() --#


    def generate_master_person_list( self, is_sorted_IN = True ):

        """
            Method: generate_master_person_list()

            Purpose: Uses nested person_dict and map of person IDs to person
               types to make a big list of all the people we need to include
               in the network we output.

            Preconditions: person_dictionary must be initialized and populated.

            Returns:
            - List - reference to the generated master person list.
        """

        # return reference
        list_OUT = []

        # declare variables
        me = "generate_master_person_list"
        my_logger = None
        debug_string = ""
        person_dict = None
        person_ids_list = None
        current_person_id = None
        person_id_to_type_dict = None
        merged_person_id_list = None

        # initialize logger
        my_logger = self.get_logger()

        # retrieve the person dictionary
        person_dict = self.person_dictionary

        my_logger.debug( "In " + me + ": len( person_dict ) = " + str( len( person_dict ) ) )

        # grab list of keys from person_dictionary.
        person_ids_list = person_dict.keys()

        # ABSOLUTELY BROKEN FIRST ATTEMPT FROM 2010, FOR POSTERITY:
        #
        #person_ids_count = len( person_ids_list )
        # ==> person_ids_count = 738
        #merge_values_list[ 0 : person_ids_count - 1 ] = NetworkDataOutput.PERSON_TYPE_UNKNOWN
        # ==> len( merge_values_list ) = 7
        #zipped_tuples_list = zip( person_ids_list, merge_values_list )
        # ==> len( zipped_tuples_list ) = 7
        #merged_person_types = dict( zipped_tuples_list )
        # ==> len( merged_person_types ) = 7
        #merged_person_types.update( self.person_type_dict )
        # ==> len( merged_person_types ) = 314
        #
        # Resulted in person dictionary count dropping from 738 to 7, then
        #    increasing up to the number of people referenced by the selected
        #    articles, as stored in self.person_type_dict.

        # make a dictionary that maps persons from person dictionary to type...
        person_id_to_type_dict = {}
        for current_person_id in person_ids_list:
        
            # to start, add all persons to dictionary with type of "unknown".
            person_id_to_type_dict[ current_person_id ] = NetworkDataOutput.PERSON_TYPE_UNKNOWN
            
        #-- END loop over IDs from dictionary. --#

        # update or add people and corresponding types from the nested
        #    self.person_type_dict.
        person_id_to_type_dict.update( self.person_type_dict )

        my_logger.debug( "In " + me + ": after person_id_to_type_dict.update( self.person_type_dict ), len( person_id_to_type_dict ) = " + str( len( person_id_to_type_dict ) ) )

        # store this in the person_type_dict?

        # grab the ID list from this merged dictionary, sort it, and use it
        #    as your list of people to iterate over as you create actual
        #    output.
        merged_person_id_list = person_id_to_type_dict.keys()
        
        # do we want it sorted?
        if ( is_sorted_IN == True ):
        
            # we want it sorted.
            merged_person_id_list = sorted( merged_person_id_list )
        
        #-- END check to see if we want the list sorted. --#

        # save this as the master person list.
        self.master_person_list = merged_person_id_list

        list_OUT = self.master_person_list
        
        my_logger.debug( "In " + me + ": len( self.master_person_list ) = " + str( len( self.master_person_list ) ) )

        return list_OUT

    #-- END method generate_master_person_list() --#


    def get_master_person_list( self, is_sorted_IN = True ):

        """
            Method: get_master_person_list()

            Purpose: Checks if list is set and has something in it.  If yes,
               returns list nested in instance.  If no, calls the generate
               method and returns the result.

            Preconditions: person_dictionary must be initialized and populated.

            Returns:
            - List - reference to the generated master person list.
        """

        # return reference
        list_OUT = []

        # declare variables
        is_ok = True

        # retrieve master person list
        list_OUT = self.master_person_list

        if ( list_OUT ):

            if ( len( list_OUT ) < 1 ):

                # nothing in list.  Not OK.
                is_ok = False

            #-- END check to see if anything in list.

        else:

            # no list.  not OK.
            is_ok = False

        #-- END check to see if stored list is OK --#

        # is stored list OK?
        if ( is_ok == False ):

            # not OK.  Try generating list.
            list_OUT = self.generate_master_person_list( is_sorted_IN )

        #-- END check if list is OK. --#
        
        return list_OUT

    #-- END method get_master_person_list() --#


    def get_person_label( self, person_id_IN ):

        """
            Method: get_person_label()

            Purpose: accepts a person ID, retrieves that person's type and type
               ID, combines the three pieces of information to create label for
               that user.

            Params:
            - person_id_IN - ID of person whose type we want to check.

            Returns:
            - String - label for the current person that combines person ID, person type, and person type ID.
        """

        # return reference
        value_OUT = ""

        # declare variables
        person_type = ""
        person_type_id = ""

        # got a value?
        if ( person_id_IN ):

            # get current person type and type ID
            person_type = self.get_person_type( person_id_IN )
            person_type_id = self.get_person_type_id( person_id_IN )

            # append the person's row to the output string.
            value_OUT = str( person_id_IN ) + "__" + person_type + "-" + str( person_type_id )

        #-- END check to see if we have a person ID --#

        return value_OUT

    #-- END method get_person_label() --#


    def get_person_type( self, person_id_IN ):

        """
            Method: get_person_type()

            Purpose: accepts a person ID, retrieves that person's type from the
               person-to-type dict stored in this instance.

            Params:
            - person_id_IN - ID of person whose type we want to check.

            Returns:
            - String - type for the current person.
        """

        # return reference
        value_OUT = NetworkDataOutput.PERSON_TYPE_UNKNOWN

        # declare variables
        person_to_type_map = None

        # got a value?
        if ( person_id_IN ):

            # get dict.
            person_to_type_map = self.person_type_dict

            # see if person is in the dict.
            if person_id_IN in person_to_type_map:

                # they exist! get their type
                value_OUT = person_to_type_map[ person_id_IN ]

            #-- END check to see if person has a type --#

        #-- END check to see if we have a person ID --#

        return value_OUT

    #-- END method get_person_type() --#


    def get_person_type_id( self, person_id_IN ):

        """
            Method: get_person_type_id()

            Purpose: accepts a person ID, retrieves that person's type from the
               person-to-type dict stored in this instance, then maps that
               string to a type ID.

            Params:
            - person_id_IN - ID of person whose type we want to check.

            Returns:
            - String - type for the current person.
        """

        # return reference
        value_OUT = NetworkDataOutput.PERSON_TYPE_UNKNOWN

        # declare variables
        person_type = ''
        type_to_id_map = None

        # got a value?
        if ( person_id_IN ):

            # get person type
            person_type = self.get_person_type( person_id_IN )

            # look up the ID for that type.
            type_to_id_map = NetworkDataOutput.PERSON_TYPE_TO_ID

            # known type?
            if person_type in type_to_id_map:

                # yes, return id
                value_OUT = type_to_id_map[ person_type ]

            else:

                # no, return unknown's ID.
                value_OUT = type_to_id_map[ NetworkDataOutput.PERSON_TYPE_UNKNOWN ]

            #-- END check to see if type is known type. --#

        #-- END check to see if we have a person ID --#

        return value_OUT

    #-- END method get_person_type_id() --#


    def get_relation_map( self ):

        """
            Method: get_relation_map()

            Purpose: retrieves nested relation map.  Eventually could be
               used to manage access to multiple types of relations.

            Returns:
            - dictionary - dictionary that maps person IDs to their connections
               to other people.
        """

        # return reference
        value_OUT = ''

        # grab map
        value_OUT = self.relation_map

        return value_OUT

    #-- END method get_relation_map() --#


    def get_relations_for_person( self, person_id_IN ):

        """
            Method: get_relations_for_person()

            Purpose: retrieves nested relation map.  Eventually could be
               used to manage access to multiple types of relations.

            Returns:
            - dictionary - dictionary that maps person IDs to their connections
               to other people.
        """

        # return reference
        value_OUT = {}

        # declare variables
        relation_dict = None

        # got an ID?
        if ( person_id_IN != '' ):

            # grab map
            relation_dict = self.get_relation_map()

            # anything there?
            if ( relation_dict ):

                # yes.  Check if ID is a key.
                if person_id_IN in relation_dict:

                    # it is.  Return what is there.
                    value_OUT = relation_dict[ person_id_IN ]

                else:

                    # no relations.  Return empty dictionary.
                    value_OUT = {}

                #-- END check to see if person has any relations.

            #-- END check to make sure dict is populated. --#

        #-- END check to see if ID passed in. --#

        return value_OUT

    #-- END method get_relations_for_person() --#


    def initialize_from_params( self, param_container_IN ):

        # declare variables
        output_type_IN = ''
        data_output_type_IN = ''
        include_render_details_IN = ''
        network_label_IN = ''
        source_capacity_include_list_IN = None
        source_capacity_exclude_list_IN = None
        source_contact_type_include_list_IN = None

        # retrieve info.
        output_type_IN = param_container_IN.get_param_as_str( NetworkDataOutput.PARAM_OUTPUT_TYPE, NetworkDataOutput.NETWORK_DATA_FORMAT_DEFAULT )
        data_output_type_IN = param_container_IN.get_param_as_str( NetworkDataOutput.PARAM_NETWORK_DATA_OUTPUT_TYPE, NetworkDataOutput.NETWORK_DATA_OUTPUT_TYPE_DEFAULT )
        include_render_details_IN = param_container_IN.get_param_as_str( NetworkDataOutput.PARAM_NETWORK_INCLUDE_RENDER_DETAILS, NetworkDataOutput.CHOICE_NO )
        network_label_IN = param_container_IN.get_param_as_str( NetworkDataOutput.PARAM_NETWORK_LABEL, '' )
        source_capacity_include_list_IN = param_container_IN.get_param_as_list( NetworkDataOutput.PARAM_SOURCE_CAPACITY_INCLUDE_LIST )
        source_capacity_exclude_list_IN = param_container_IN.get_param_as_list( NetworkDataOutput.PARAM_SOURCE_CAPACITY_EXCLUDE_LIST )
        source_contact_type_include_list_IN = param_container_IN.get_param_as_list( NetworkDataOutput.PARAM_SOURCE_CONTACT_TYPE_INCLUDE_LIST )

        # store
        self.set_output_type( output_type_IN )
        self.data_output_type = data_output_type_IN
        self.network_label = network_label_IN

        # convert include_render_details_IN to boolean
        if ( include_render_details_IN == NetworkDataOutput.CHOICE_YES ):
        
            # yes - True
            self.include_render_details = True

        else:
        
            # not yes, so False.
            self.include_render_details = False
        
        #-- END check to see whether we include render details --#
        
        # got source contact type include list?
        if ( ( source_contact_type_include_list_IN is not None ) and ( len( source_contact_type_include_list_IN ) > 0 ) ):
        
            # store in internal inclusion parameters
            self.inclusion_params[ NetworkDataOutput.PARAM_SOURCE_CONTACT_TYPE_INCLUDE_LIST ] = source_contact_type_include_list_IN
        
        #-- END check to see if source contact type list --#

        # got include list?
        if ( source_capacity_include_list_IN ):

            # store in internal inclusion parameters
            self.inclusion_params[ NetworkDataOutput.PARAM_SOURCE_CAPACITY_INCLUDE_LIST ] = source_capacity_include_list_IN

        #-- END check to see if anything in list. --#

        # got exclude list?
        if ( source_capacity_exclude_list_IN ):

            # store in internal inclusion parameters
            self.inclusion_params[ NetworkDataOutput.PARAM_SOURCE_CAPACITY_EXCLUDE_LIST ] = source_capacity_exclude_list_IN

        #-- END check to see if anything in list. --#

    #-- END method initialize_from_params() --#


    def is_source_connected( self, source_IN ):

        """
            Method: is_source_connected()

            Purpose: accepts a source, examines its categorization to determine
               if the source is eligible to be classified as "connected" to the
               authors of the story.  If "connected", returns True.  If not,
               returns False.  By default, "Connected" = source of type
               "individual" with contact type of "direct" or "event".
               Eventually we can make this more nuanced, allow filtering here
               based on input parameters, and allow different types of
               connections to be requested.  For now, just need it to work.

            Params:
            - source_IN - source whose connectedness we need to check.

            Returns:
            - boolean - If "connected", returns True.  If not, returns False.
        """

        # return reference
        is_connected_OUT = True

        # this functionality has been moved over to the model, so it can be used
        #    in more places.  So, just call the method.
        is_connected_OUT = source_IN.is_connected( self.inclusion_params )

        return is_connected_OUT

    #-- END method is_source_connected() --#


    def process_author_relations( self, author_qs_IN, source_qs_IN ):

        """
            Method: process_author_relations()

            Purpose: Accepts a QuerySet of authors and one of sources from a
               given Article_Data instance (so, the authors of and sources
               quoted in a given article).  First, checks to see if multiple
               authors.  If so, loops and creates a dictionary that maps author
               ID to author instance.  Then, iterates over keys of this dict.
               For each author:
                  - removes that author from the local author dictionary
                  - registers them as an author in the master person_type_dict
                  - loops over all remaining authors in the map, creating a
                     reciprocal co-author/shared byline relation with each.
                  - calls the process_source_relations() method to tie the
                     author to the sources passed in.
               If only one author, just registers them as an author and calls
               process_source_relations().

            Preconditions: connection_map must be initialized to a dictionary.
               Also must pass in something for author query set and source query
               set (each should be pulled from the same single Article_Data
               instance).

            Params:
            - author_qs_IN - QuerySet of authors to relate to each other.
            - source_qs_IN - QuerySet of sources that are in the current
               article.

            Returns:
            - string status message, either STATUS_OK if success, or
               STATUS_ERROR_PREFIX followed by descriptive error message.
        """

        # return reference
        status_OUT = NetworkDataOutput.STATUS_OK

        # declare variables
        me = "process_author_relations"
        my_logger = None
        #multiple_authors = False
        author_map = None
        current_author = None
        current_person_id = -1
        author_id_list = None
        remaining_author_id_list = None
        remaining_person_id = -1

        # initialize logger
        my_logger = self.get_logger()

        # make sure we have a QuerySet.
        if ( author_qs_IN is not None ):

            # do we have more than one author?
            #if ( author_qs_IN.count() > 1 ):

            #    multiple_authors = True
                
            #-- END setting up for multiple authors. --#

            # Create map of authors in to their model instances.
            author_map = {}

            # loop over authors
            for current_author in author_qs_IN:

                # get ID.
                current_person_id = current_author.get_person_id()

                # is there an associated person?
                if ( current_person_id ):

                    # tie instance to ID in map.
                    author_map[ current_person_id ] = current_author

                #-- END check to make sure the author has an associated person --#

            #-- END loop over authors to build map. --#

            if ( self.DEBUG_FLAG == True ):

                # output message about connectedness of source.
                debug_string = "\n\nIn " + me + ": author map = \n" + str( author_map ) + "\n\n"
                
                # add to debug string?
                self.debug += debug_string
                
                my_logger.debug( debug_string )
                
            #-- END DEBUG --#

            # Now, make a copy of the keys of the map, for us to loop over.
            author_id_list = list( six.viewkeys( author_map ) )

            # loop over keys.
            for current_person_id in author_id_list:

                if ( self.DEBUG_FLAG == True ):

                    # output message about connectedness of source.
                    debug_string = "\n\nIn " + me + ": author person ID:\n" + str( current_person_id ) + "\n\n"
                    
                    # add to debug string?
                    self.debug += debug_string
                    
                    my_logger.debug( debug_string )
                
                #-- END DEBUG --#

                # remove author from author_map.  pop()-ing it, for now, just
                #    in case.  Eventually, probably should del:
                # del author_map[ current_person_id ]
                #
                # - NOTE: bi-directional tie, so OK to remove from map as we go.
                #    If the ties were potentially asymmetrical, would need to do
                #    something substantially different.
                current_author = author_map.pop( current_person_id )

                if ( self.DEBUG_FLAG == True ):

                    # output message about connectedness of source.
                    debug_string = "\n\nIn " + me + ": author map = \n" + str( author_map ) + "\n\n"
                    
                    # add to debug string?
                    self.debug += debug_string
                    
                    my_logger.debug( debug_string )
                    
                #-- END DEBUG --#
                
                # get IDs of remaining authors
                remaining_author_id_list = author_map.keys()

                # loop over remaining authors and connect.
                for remaining_person_id in remaining_author_id_list:

                    # make a reciprocal relation between the current author and
                    #    this remaining author.
                    self.add_reciprocal_relation( current_person_id, remaining_person_id )

                #-- END loop over remaining authors to make relations between them --#

                # set the person's type to author
                self.update_person_type( current_person_id, NetworkDataOutput.PERSON_TYPE_AUTHOR )

                # update the person's relations to sources.
                self.process_source_relations( current_person_id, source_qs_IN )

            #-- END processing loop over author keys --#

        #-- END check to make sure we have a QuerySet --#

        return status_OUT

    #-- END method process_author_relations --#


    def process_source_relations( self, author_id_IN, source_qs_IN ):

        """
            Method: process_source_relations()

            Purpose: Accepts an author ID and a QuerySet of sources.  For each
               source, checks to see if eligible to be included in the network.
               If eligible, ties source to author.  If not, moves on.

            Preconditions: connection_map must be initialized to a dictionary.

            Params:
            - author_id_IN - ID of author we are tying sources to.
            - source_qs_IN - QuerySet of sources to relate to the author.

            Returns:
            - string status message, either STATUS_OK if success, or
               STATUS_ERROR_PREFIX followed by descriptive error message.
        """

        # return reference
        status_OUT = NetworkDataOutput.STATUS_OK

        # declare variables
        me = "process_source_relations"
        my_logger = None
        debug_string = ""
        author_map = None
        current_source = None
        is_connected = False
        current_person_id = -1
        source_counter = -1

        # initialize logger
        my_logger = self.get_logger()

        # make sure we have an author ID.
        if ( author_id_IN != '' ):

            # make sure we have a QuerySet, and it has more than one thing in it.
            if ( ( source_qs_IN is not None ) and ( source_qs_IN.count() > 0 ) ):

                # we have sources to join.  Loop!
                source_counter = 0
                for current_source in source_qs_IN:

                    source_counter += 1

                    # see if source has the right attributes to be considered
                    #    connected.
                    is_connected = self.is_source_connected( current_source )

                    # connected?
                    if ( is_connected == True ):

                        # yes! get source's person ID
                        current_person_id = current_source.get_person_id()

                        if ( self.DEBUG_FLAG == True ):

                            # output message about connectedness of source.
                            debug_string = "In " + me + ": connected source " + str( source_counter ) + " has ID: " + str( current_person_id )
                            
                            # add to debug string?
                            self.debug += "\n\n" + debug_string + "\n\n"
                            
                            my_logger.debug( debug_string )
                            
                        #-- END DEBUG --#

                        if ( current_person_id ):

                            # relate the author and this source.
                            self.add_reciprocal_relation( author_id_IN, current_person_id )

                        #-- END check to make sure that the source has an associated person --#

                    else:

                        if ( self.DEBUG_FLAG == True ):

                            # output message about connectedness of source.
                            debug_string = "In " + me + ": source " + str( source_counter ) + " is not connected."
                            
                            # add to debug string?
                            self.debug += "\n\n" + debug_string + "\n\n"
                            
                            my_logger.debug( debug_string )
                            
                        #-- END DEBUG --#

                    #-- END check to see if connected. --#

                #-- END loop over sources --#

            #-- END check to make sure we have at least one source. --#

        #-- END check to make sure we have an author ID --#

        return status_OUT

    #-- END method process_source_relations --#


    def render( self ):

        """
            Assumes query set of articles has been placed in this instance.
               Uses the query set to output delimited data in the format specified in
               the output_type instance variable.  If one line per article, has
               sets of columns for as many authors and sources as are present in
               the articles with the most authors and sources, respectively.

            Preconditions: assumes that we have a query set of articles stored
               in the instance.  If not, does nothing, returns empty string.

            Postconditions: returns the delimited network data, each column separated by two spaces, in a string.

            Parameters - all inputs are stored in instance variables:
            - self.query_set - Query set of articles for which we want to create network data.
            - self.person_dictionary - QuerySet of people we want included in our network (can include people not mentioned in an article, in case we want to include all people from two different time periods, for example).
            - self.inclusion_params

            Returns:
            - String - delimited output (two spaces separate each column value in a row) for the network described by the articles selected based on the parameters passed in.
        """

        # return reference
        network_data_OUT = ''

        # declare variables
        me = "render"
        my_logger = None
        debug_string = ""
        article_data_query_set = None
        person_dict = None
        network_dict = {}
        article_data_counter = 0
        current_article_data = None
        article_author_count = -1
        author_qs = None
        source_qs = None

        # initialize logger
        my_logger = self.get_logger()

        # start by grabbing person dict, query set.
        article_data_query_set = self.query_set
        person_dict = self.person_dictionary

        # make sure each of these has something in it.
        if ( ( article_data_query_set ) and ( person_dict ) ):

            #--------------------------------------------------------------------
            # create ties
            #--------------------------------------------------------------------
            
            # loop over the article data for each article to be processed.
            for current_article_data in article_data_query_set:

                article_data_counter += 1

                if ( self.DEBUG_FLAG == True ):

                    # output message about connectedness of source.
                    debug_string = "In " + me + ": +++ Current article data = " + str( current_article_data.id ) + " +++"
                    
                    # add to debug string?
                    self.debug += "\n\n" + debug_string + "\n\n"
                    
                    my_logger.debug( debug_string )

                #-- END DEBUG --#

                # first, see how many authors this article has.
                article_author_count = current_article_data.article_author_set.count()

                # if no authors, move on.
                if ( article_author_count > 0 ):

                    # get authors
                    author_qs = current_article_data.article_author_set.all()
                    source_qs = current_article_data.get_quoted_article_sources_qs()

                    # call method to loop over authors and tie them to other
                    #    authors (if present) and eligible sources.
                    self.process_author_relations( author_qs, source_qs )

                    # update the person types for sources
                    self.update_source_person_types( source_qs )

                    if ( self.DEBUG_FLAG == True ):

                        # output message about connectedness of source.
                        debug_string = "In " + me + ": Relation Map after article " + str( article_data_counter ) + ":\n" + str( self.relation_map )
                        
                        # add to debug string?
                        self.debug += "\n\n" + debug_string + "\n\n"
                        
                        #my_logger.debug( debug_string )
    
                    #-- END DEBUG --#

                #-- END check to make sure there are authors.

            #-- END loop over article data for each article to be processed.

            #--------------------------------------------------------------------
            # build person list (list of network matrix rows/columns)
            #--------------------------------------------------------------------
            
            # now that all relations are mapped, need to build our master person
            #    list, so we can loop to build out the network.  All people who
            #    need to be included should be in the person_dictionary passed
            #    in.  To be sure, we can make a copy that places source type
            #    of unknown as value for all, then update with the
            #    people_to_type map, so we make sure all sources that were
            #    included in the network are in the dict.
            self.generate_master_person_list()

            if ( self.DEBUG_FLAG == True ):
                self.debug += "\n\nPerson Dictionary:\n" + str( self.person_dictionary ) + "\n\n"
                self.debug += "\n\nMaster person list:\n" + str( self.master_person_list ) + "\n\n"
                self.debug += "\n\nParam list:\n" + str( self.inclusion_params ) + "\n\n"
            #-- END DEBUG --#

            #--------------------------------------------------------------------
            # render network data based on people and ties.
            #--------------------------------------------------------------------
            
            network_data_OUT += self.render_network_data()
            
        #-- END check to make sure we have the data we need. --#

        return network_data_OUT

    #-- END render() --#


    @abstractmethod
    def render_network_data( self ):

        '''
        Invoked from render(), after ties have been generated based on articles
           and people passed in.  Returns a string.  This string can contain the
           rendered data (CSV file, etc.), or it can just contain a status
           message if the data is rendered to a file or a database.
        '''

        pass

    #-- END abstract method render_network_data() --#
    

    def set_output_type( self, value_IN ):

        """
            Method: set_output_type()

            Purpose: accepts an output type, stores it in instance.

            Params:
            - value_IN - String output type value.
        """

        # got a value?
        if ( value_IN ):

            # store value
            self.output_type = value_IN
            self.data_format = value_IN

        #-- END check to see if we have a value --#

    #-- END method set_output_type() --#


    def set_query_set( self, value_IN ):

        """
            Method: set_request()

            Purpose: accepts a query set, stores it in instance, then grabs the
               POST from the request and stores that as the params.

            Params:
            - value_IN - django QuerySet instance that contains the articles
               from which we are to build our network data.
        """

        # got a value?
        if ( value_IN ):

            # store value
            self.query_set = value_IN

        #-- END check to see if we have a value --#

    #-- END method set_query_set() --#


    def set_person_dictionary( self, value_IN ):

        """
            Method: set_person_dictionary()

            Purpose: accepts a dictionary, with person ID as key, values...
               undetermined at this time, stores it in the instance.

            Params:
            - value_IN - Python dictionary with person IDs as keys.
        """

        # got a value?
        if ( value_IN ):

            # store value
            self.person_dictionary = value_IN

        #-- END check to see if we have a value --#

    #-- END method set_person_dictionary() --#


    def update_person_type( self, person_id_IN, value_IN ):

        """
            Method: update_person_type()

            Purpose: accepts a person ID and the type of that person.  Checks to
               see if person is in dict already. If not, adds them, assigns type
               passed in to them.  If yes, checks type.  If it matches type
               passed in, does nothing.  If types are different, stores the
               "both" type.

            Params:
            - person_id_IN - ID of person whose type we are updating.
            - value_IN - type we want t assign to person.
        """

        # declare variables
        person_to_type_map = ''
        current_person_type = ''

        # got person ID?
        if ( person_id_IN ):

            # got a value?
            if ( value_IN ):

                # see if person is already in dict.
                person_to_type_map = self.person_type_dict

                # present in dict?
                if person_id_IN in person_to_type_map:

                    # yes.  Get current value.
                    current_person_type = person_to_type_map[ person_id_IN ]

                    # got a value?
                    if ( current_person_type ):

                        # yes.  Different from value passed in?  If so, set to
                        #    both.  If same, do nothing - already set!
                        if ( current_person_type != value_IN ):

                            # not same as existing, so set to both.
                            person_to_type_map[ person_id_IN ] = NetworkDataOutput.PERSON_TYPE_BOTH

                        #-- END check to see if value is different. --#

                    else:

                        # no value present, so store value
                        person_to_type_map[ person_id_IN ] = value_IN

                    #-- END check to see if value present --#

                else: # person not in dict.

                    # person not in dict.  Add them and their type.
                    person_to_type_map[ person_id_IN ] = value_IN

                #-- END check to see if person is in dict --#

            #-- END check to see if we have a value --#

        #-- END check to see if we have a person ID --#

    #-- END method update_person_type() --#


    def update_source_person_types( self, source_qs_IN ):

        """
            Method: update_source_person_types()

            Purpose: Accepts a QuerySet of sources.  For each source, updates
               its person type to source.

            Preconditions: connection_map must be initialized to a dictionary.

            Params:
            - source_qs_IN - QuerySet of sources to relate to the author.

            Returns:
            - string status message, either STATUS_OK if success, or
               STATUS_ERROR_PREFIX followed by descriptive error message.
        """

        # return reference
        status_OUT = NetworkDataOutput.STATUS_OK

        # declare variables
        current_source = None
        current_person_id = -1

        # make sure we have a QuerySet, and it has more than one thing in it.
        if ( ( source_qs_IN is not None ) and ( source_qs_IN.count() > 0 ) ):

            # we have sources to join.  Loop!
            for current_source in source_qs_IN:

                # get current person.
                current_person_id = current_source.get_person_id()

                # see if there is a person
                if ( current_person_id ):

                    # update this source's type.
                    self.update_person_type( current_person_id, NetworkDataOutput.PERSON_TYPE_SOURCE )

                #-- END check to make sure source has a person.

            #-- END loop over sources --#

        #-- END check to make sure we have at least one source. --#

        return status_OUT

    #-- END method update_source_person_types --#


#-- END class NetworkDataOutput --#