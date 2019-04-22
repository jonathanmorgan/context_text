'''
Copyright 2014 Jonathan Morgan

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

#import copy

# Django DB classes, just to play with...
#from django.db.models import Count # for aggregating counts of authors, sources.
#from django.db.models import Max   # for getting max value of author, source counts.

# Import the classes for our context_text application
#from context_text.models import Article
#from context_text.models import Article_Author
from context_text.models import Article_Subject
#from context_text.models import Person
#from context_text.models import Topic

# parent abstract class.
from context_text.export.network_data_output import NetworkDataOutput

#===============================================================================
# classes (in alphabetical order by name)
#===============================================================================

class NDO_SimpleMatrix( NetworkDataOutput ):

    
    #---------------------------------------------------------------------------
    # CONSTANTS-ish
    #---------------------------------------------------------------------------

    # output constants
    OUTPUT_END_OF_LINE = "\n"
    OUTPUT_DEFAULT_COLUMN_SEPARATOR = "  "
    
    # output type
    MY_OUTPUT_TYPE = "simple_matrix"


    #---------------------------------------------------------------------------
    # instance variables
    #---------------------------------------------------------------------------

    
    column_separator = OUTPUT_DEFAULT_COLUMN_SEPARATOR


    #---------------------------------------------------------------------------
    # __init__() method
    #---------------------------------------------------------------------------


    def __init__( self ):

        # call parent's __init__() - I think...
        super( NDO_SimpleMatrix, self ).__init__()

        # declare variables
        self.column_separator = self.OUTPUT_DEFAULT_COLUMN_SEPARATOR

        # override things set in parent.
        self.output_type = self.MY_OUTPUT_TYPE
        self.debug = "NDO_SimpleMatrix debug:\n\n"
        
        # variables for outputting result as file
        self.mime_type = "text/plain"
        self.file_extension = "txt"

    #-- END method __init__() --#


    #---------------------------------------------------------------------------
    # instance methods, in alphabetical order
    #---------------------------------------------------------------------------


    def create_label_string( self, delimiter_IN = OUTPUT_END_OF_LINE, quote_character_IN = '' ):

        """
            Method: create_label_string()

            Purpose: retrieves the master person list from the instance, uses it
               to output a list of the person IDS and their source types, one to
               a line, that could be pasted into a column next to the attributes
               or data to make it more readily understandable for someone
               eye-balling it.  Each person's label consists of:
               "<person_counter>__<person_id>__<person_type>"
               WHERE:
               - <person_counter> is the simple integer count of people in list, incremented as each person is added.
               - <person_id> is the ID of the person's Person record in the system.
               - <person_type> is the string person type of the person, then a hyphen, then the person type ID of that type.

            Returns:
            - string representation of labels for each row in network and attributes.
        """

        # return reference
        string_OUT = ""

        # declare variables
        master_list = None
        my_label = ''
        current_person_id = -1
        person_count = -1
        current_type = ''
        current_type_id = -1
        current_label = ""
        current_value = ''
        delimiter = delimiter_IN
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
                string_OUT += current_value + delimiter

            #-- END loop over persons.

            # append counts
            string_OUT += "\n\ntotals: unknown=" + str( unknown_count ) + "; author=" + str( author_count ) + "; source=" + str( source_count ) + "; both=" + str( both_count ) + "\n\n"

        #-- END check to make sure we have a person list. --#

        return string_OUT

    #-- END method create_label_string --#


    def create_network_string( self ):

        """
            Method: create_network_string()

            Purpose: retrieves the master person list from the instance, uses it
               to output a square matrix where rows and columns are people, by
               person ID, and the value at the intersection between two people
               is the number of time they were linked in articles during the
               time period that the network was drawn from.

            Returns:
            - string representation of network.
        """

        # return reference
        network_string_OUT = ""

        # declare variables
        master_list = None
        my_label = ''
        current_person_id = -1
        end_of_line = self.OUTPUT_END_OF_LINE

        # get master list
        master_list = self.get_master_person_list()

        # got something?
        if ( master_list ):

            # got one.  Do we have a label to append?
            my_label = self.network_label

            if ( my_label != '' ):

                # we have a label.  Add it as the first line of the output.
                network_string_OUT += my_label + end_of_line

            #-- END check for label. --#

            # loop over sorted person list, calling method to output network
            #    row for each person.
            for current_person_id in sorted( master_list ):

                # append the person's row to the output string.
                network_string_OUT += self.create_person_row_string( current_person_id ) + end_of_line

            #-- END loop over persons.

        #-- END check to make sure we have a person list. --#

        return network_string_OUT

    #-- END method create_network_string --#


    def create_person_row_string( self, person_id_IN ):

        """
            Method: create_person_row_string()

            Purpose: retrieves the master person list from the instance, uses it
               to output a square matrix where rows and columns are people, by
               person ID, and the value at the intersection between two people
               is the number of time they were linked in articles during the
               time period that the network was drawn from.

            Returns:
            - string representation of network.
        """

        # return reference
        string_OUT = ""

        # declare variables
        master_list = None
        current_person_relations = None
        current_other_id = -1
        current_other_count = -1
        delimiter = self.column_separator

        # get person ID?
        if ( person_id_IN ):

            # get master list
            master_list = self.get_master_person_list()

            # get relations for this person.
            current_person_relations = self.get_relations_for_person( person_id_IN )

            # loop over master list, checking for relations with each person.
            for current_other_id in sorted( master_list ):

                # try to retrieve relation count from relations
                if current_other_id in current_person_relations:

                    # they are related.  Get count.
                    current_other_count = current_person_relations[ current_other_id ]

                else:

                    # no relation.  Set current count to 0
                    current_other_count = 0

                #-- END check to see if related.

                # output the count for the current person.
                string_OUT += delimiter + str( current_other_count )

            #-- END loop over master list --#

        #-- END check to make sure we have a person --#

        return string_OUT

    #-- END method create_person_row_string --#


    def create_person_type_attribute_string( self ):

        '''
            Method: create_person_type_attribute_string()

            Purpose: Create a string list of person type IDs for the people in
               master list, for use in assigning person type attributes to the
               corresponding people/nodes.

            Preconditions: Master person list must be present.

            Params: none

            Returns:
            - string_OUT - list of person IDs, in sorted master person list order, one to a line.
        '''

        # return reference
        string_OUT = ""

        # declare variables
        person_type_id_list = None

        # get person type ID list
        person_type_id_list = self.create_person_type_id_list( True )

        # got it?
        if ( person_type_id_list ):

            # output the name of this attribute
            string_OUT += "person_type\n"

            # join the list into a string, separated by newlines.
            string_OUT += "\n".join( person_type_id_list )
            
            # add a newline to the end.
            string_OUT += "\n"
            
        #-- END check to make sure we have list.

        return string_OUT

    #-- END method create_person_type_attribute_string --#


    def render_network_data( self ):

        """
            Assumes render method has already created network data by calling
               process_author_relations() and updated source person types by
               calling update_source_person_types().  Outputs a simple text
               matrix of ties.  For a given cell in the matrix, the value is an
               integer: 0 if no tie, 1 or greater if tie.  Each column value is
               separated by two spaces.
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
        data_output_type = ""

        #--------------------------------------------------------------------
        # render network data based on people and ties.
        #--------------------------------------------------------------------
        
        # get data output type
        my_data_output_type = self.data_output_type
        
        # then, need to output.  For each network, output the network, then also
        #    output an attribute file that says, for all people whether each
        #    person was a reporter or a source.
        
        # include network?
        if ( ( my_data_output_type == NetworkDataOutput.NETWORK_DATA_OUTPUT_TYPE_NETWORK )
            or ( my_data_output_type == NetworkDataOutput.NETWORK_DATA_OUTPUT_TYPE_NET_AND_ATTR_COLS )
            or ( my_data_output_type == NetworkDataOutput.NETWORK_DATA_OUTPUT_TYPE_NET_AND_ATTR_ROWS ) ):

            # output the N of the network.
            network_data_OUT += "\nN = " + str( len( self.master_person_list ) ) + "\n"
    
            # output network.
            network_data_OUT += self.create_network_string()
    
            # Add a couple of new lines
            network_data_OUT += "\n\n"
    
        #-- END check to see if include network matrix --#

        # include person type attributes?
        if ( ( my_data_output_type == NetworkDataOutput.NETWORK_DATA_OUTPUT_TYPE_ATTRIBUTES )
            or ( my_data_output_type == NetworkDataOutput.NETWORK_DATA_OUTPUT_TYPE_NET_AND_ATTR_COLS )
            or ( my_data_output_type == NetworkDataOutput.NETWORK_DATA_OUTPUT_TYPE_NET_AND_ATTR_ROWS ) ):

            # yes - append the attribute string.
            network_data_OUT += self.create_person_type_attribute_string()
            
        #-- END check to see if include attributes. --#

        # Add a divider, then row headers and column headers for matrix,
        #    attribute list.
        network_data_OUT += "\n-------------------------------\nColumn and row labels (in the order the rows appear from top to bottom in the network matrix and attribute vector above, and in the order the columns appear from left to right) \n\n"

        # create column of headers
        network_data_OUT += self.create_label_string( "\n" )
        network_data_OUT += "\n\nLabel array, for use in analysis:\n"
        network_data_OUT += self.create_label_string( ",", '"' ) + "\n"

        return network_data_OUT

    #-- END render_network_data() --#


#-- END class NDO_SimpleMatrix --#