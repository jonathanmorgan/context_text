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

# python libraries
import csv
# documentation: https://docs.python.org/2/library/csv.html

# six imports - support Pythons 2 and 3
import six
# import StringIO
from six import StringIO

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

class NDO_CSVMatrix( NetworkDataOutput ):

    
    #---------------------------------------------------------------------------
    # CONSTANTS-ish
    #---------------------------------------------------------------------------

    # output type
    MY_OUTPUT_TYPE = "csv_matrix"

    # LOCAL_DEBUG_FLAG
    LOCAL_DEBUG_FLAG = False


    #---------------------------------------------------------------------------
    # instance variables
    #---------------------------------------------------------------------------


    csv_string_buffer = None
    csv_writer = None
    delimiter = ","

    
    #---------------------------------------------------------------------------
    # __init__() method
    #---------------------------------------------------------------------------


    def __init__( self ):

        # call parent's __init__() - I think...
        super( NDO_CSVMatrix, self ).__init__()

        # override things set in parent.
        self.output_type = self.MY_OUTPUT_TYPE
        self.debug = "NDO_CSVMatrix debug:\n\n"

        # initialize variables.
        self.csv_string_buffer = None
        self.csv_writer = None
        self.delimiter = ","

        # variables for outputting result as file
        self.mime_type = "text/csv"
        self.file_extension = "csv"

    #-- END method __init__() --#


    #---------------------------------------------------------------------------
    # instance methods, in alphabetical order
    #---------------------------------------------------------------------------


    def append_person_row( self, person_id_IN, row_count_IN = "" ):

        """
            Method: append_person_row()

            Purpose: retrieves the master person list from the instance, uses it
               and the person ID passed in to output the row for the current
               person in a square matrix where rows and columns are people,
               sorted by person ID, and the value at the intersection between
               two people is the number of time they were linked in articles
               during the time period that the network was drawn from.

            Postconditions: Doesn't return anything, but appends row for current
               user to the nested CSV writer.

            Returns:
            - nothing.
        """

        # return reference

        # declare variables
        current_person_label = ""
        person_list = None
        do_output_network = False
        current_person_relations = None
        current_other_id = -1
        current_other_count = -1
        column_value_list = []
        csv_writer = None
        do_output_attrs = False
        person_type_id = -1

        # get person ID?
        if ( person_id_IN ):
        
            if ( ( self.LOCAL_DEBUG_FLAG == True ) or ( self.DEBUG_FLAG == True ) ):
                self.debug += "person " + str( person_id_IN ) + "; "
            #-- END DEBUG --#
                
            # get label for current user
            current_person_label = str( row_count_IN ) + "__" + self.get_person_label( person_id_IN )
            
            # make it first column in row.
            column_value_list.append( current_person_label )
            
            # are we outputting network?
            do_output_network = self.do_output_network()
            if ( do_output_network == True ):

                # get person list
                person_list = self.get_master_person_list()
    
                # get relations for this person.
                current_person_relations = self.get_relations_for_person( person_id_IN )
    
                # loop over master list, checking for relations with each person.
                for current_other_id in sorted( person_list ):
    
                    # try to retrieve relation count from relations
                    if current_other_id in current_person_relations:
    
                        # they are related.  Get count.
                        current_other_count = current_person_relations[ current_other_id ]
    
                    else:
    
                        # no relation.  Set current count to 0
                        current_other_count = 0
    
                    #-- END check to see if related.
    
                    # output the count for the current person.
                    column_value_list.append( str( current_other_count ) )
    
                #-- END loop over master list --#
                
            #-- END check to see if we output network data. --#
            
            # do we append node attributes to the end of each row?
            do_output_attrs = self.do_output_attribute_columns()
            if ( do_output_attrs == True ):

                # yes - append attributes.
                
                # append person's ID.
                column_value_list.append( str( person_id_IN ) )

                # get current person's person type and append it.
                person_type_id = self.get_person_type_id( person_id_IN )
                column_value_list.append( str( person_type_id ) )
                            
            #-- END check to see if we append attributes to the end of rows. --#
            
            # append row to CSV
            self.append_row_to_csv( column_value_list )

        #-- END check to make sure we have a person --#

    #-- END method append_person_row --#


    def append_person_id_row( self ):

        '''
            Method: append_person_id_row()

            Purpose: Create a list of person IDs for the people in
               master list, then append the list to the end of the
               CSV document.

            Preconditions: Master person list must be present.

            Params: none
            
            Postconditions: Row is appended to the end of the nested CSV document, but nothing is returned.
        '''

        # return reference

        # declare variables
        person_id_list = None

        # get person type ID list
        person_id_list = self.create_person_id_list( True )

        if ( ( self.LOCAL_DEBUG_FLAG == True ) or ( self.DEBUG_FLAG == True ) ):
            self.debug += "\n\nperson id list:\n" + "; ".join( person_id_list )
        #-- END DEBUG --#

        # got it?
        if ( ( person_id_list != None ) and ( len( person_id_list ) > 0 ) ):

            # add label to front
            person_id_list.insert( 0, "person_id" )

            # write the row
            self.append_row_to_csv( person_id_list )
            
        #-- END check to make sure we have list.

    #-- END method append_person_id_row --#


    def append_person_type_id_row( self ):

        '''
            Method: append_person_type_id_row()

            Purpose: Create a list of person type IDs for the people in
               master list, for use in assigning person type attributes to the
               corresponding people/nodes.  Append the list to the end of the
               CSV document.

            Preconditions: Master person list must be present.

            Params: none
            
            Postconditions: Row is appended to the end of the nested CSV document, but nothing is returned.
        '''

        # return reference

        # declare variables
        person_type_id_list = None

        # get person type ID list
        person_type_id_list = self.create_person_type_id_list( True )

        if ( ( self.LOCAL_DEBUG_FLAG == True ) or ( self.DEBUG_FLAG == True ) ):
            self.debug += "\n\nperson type id list:\n" + "; ".join( person_type_id_list )
        #-- END DEBUG --#

        # got it?
        if ( ( person_type_id_list != None ) and ( len( person_type_id_list ) > 0 ) ):

            # add label to front
            person_type_id_list.insert( 0, "person_type" )

            # write the row
            self.append_row_to_csv( person_type_id_list )
            
        #-- END check to make sure we have list.

    #-- END method append_person_type_id_row --#


    def append_row_to_csv( self, column_value_list_IN ):
        
        '''
        Accepts list of column values that make up a row in a CSV document.
           Retrieves nested CSV writer, writes the row to the document.
        '''
        
        # declare variables.
        my_csv_writer = None
        
        # got a list?
        if ( ( column_value_list_IN != None ) and ( len( column_value_list_IN ) > 0 ) ):

            # yes - get writer.
            my_csv_writer = self.get_csv_writer()
            
            # write the list to the CSV writer
            my_csv_writer.writerow( column_value_list_IN ) 
        
        #-- END check to see if got list. --#
        
    #-- END method append_row_to_csv() --#


    def cleanup( self ):
        
        # declare variables
        my_csv_string_buffer = None
        
        # get string buffer.
        my_csv_string_buffer = self.get_csv_string_buffer()
        
        # close string buffer
        my_csv_string_buffer.close()
        
        # None out string buffer and writer
        self.csv_writer = None
        self.csv_string_buffer = None
        
    #-- END method cleanup() --#


    def create_csv_document( self ):

        """
            Method: create_csv_document()

            Purpose: retrieves the master person list from the instance, uses it
               to output a CSV square matrix where rows and columns are people,
               by person ID, and the value at the intersection between two people
               is the number of time they were linked in articles during the
               time period that the network was drawn from.

            Preconditions: Assumes that csv output is already initialized.
            
            Returns:
            - nothing - CSV is stored in internal CSV Writer and String buffer.
        """

        # return reference

        # declare variables
        header_label_list = None
        master_list = None
        current_person_id = -1
        person_counter = -1
        my_csv_buffer = None
        do_output_attr_rows = False

        # get list of column headers.
        header_label_list = self.create_header_list()
        
        # add header label row to csv document.
        self.append_row_to_csv( header_label_list )

        # get sorted master list (returns it sorted by default)
        master_list = self.get_master_person_list()

        # got something?
        if ( ( master_list != None ) and ( len( master_list ) > 0 ) ):

            # loop over sorted person list, calling method to output network
            #    row for each person.  Leaving in sorted() since it copies
            #    the array, and we are looping twice - not sure if it will
            #    maintain two separate positions in nested loops.
            person_counter = 0
            for current_person_id in sorted( master_list ):

                # increment counter
                person_counter += 1

                # add the person's row to the CSV writer.
                self.append_person_row( current_person_id, person_counter )

            #-- END loop over persons.

        #-- END check to make sure we have a person list. --#
        
        # add attributes as rows?
        do_output_attr_rows = self.do_output_attribute_rows()
        if ( do_output_attr_rows == True ):

            # yes - append the "person_id" attribute string...
            self.append_person_id_row()
            
            # ...and append the "person_type" attribute string.
            self.append_person_type_id_row()
            
        #-- END check to see if include attributes. --#

    #-- END method create_csv_document --#


    def create_csv_string( self ):

        """
            Method: create_csv_string()

            Purpose: retrieves the master person list from the instance, uses it
               to output a CSV square matrix where rows and columns are people,
               by person ID, and the value at the intersection between two people
               is the number of time they were linked in articles during the
               time period that the network was drawn from.

            Returns:
            - string CSV representation of network.
        """

        # return reference
        network_string_OUT = ""

        # declare variables
        master_list = None
        current_person_id = -1
        person_counter = -1
        my_csv_buffer = None

        # initialize CSV output.
        self.init_csv_output()

        # create the CSV document.
        self.create_csv_document()

        # get underlying string buffer.
        my_csv_buffer = self.csv_string_buffer
        
        # convert contents to string
        network_string_OUT = my_csv_buffer.getvalue()

        # cleanup.
        self.cleanup()

        return network_string_OUT

    #-- END method create_csv_string --#


    def get_csv_string_buffer( self ):
        
        # return reference
        buffer_OUT = None
        
        # got an instance nested already?
        if ( self.csv_string_buffer != None ):
        
            # yes.  Return it.
            buffer_OUT = self.csv_string_buffer
            
        else:
        
            # no - init, then return self.csv_writer.
            self.init_csv_output()
            buffer_OUT = self.csv_string_buffer
            
        #-- END check to see if we already have a CSV writer. --#
        
        return buffer_OUT
        
    #-- END method get_csv_string_buffer() --#
    

    def get_csv_writer( self ):
        
        # return reference
        writer_OUT = None
        
        # got an instance nested already?
        if ( self.csv_writer != None ):
        
            # yes.  Return it.
            writer_OUT = self.csv_writer
            
        else:
        
            # no - init, then return self.csv_writer.
            self.init_csv_output()
            writer_OUT = self.csv_writer
            
        #-- END check to see if we already have a CSV writer. --#
        
        return writer_OUT
        
    #-- END method get_csv_writer() --#
    

    def init_csv_output( self ):
        
        '''
        Creates a string buffer, then uses that to create a CSV writer.  The
           writer is used to create the CSV file.  You pass lists of column
           values to the method writerow() and the CSV writer creates a row
           where each value in the list is a column value.
           Stores both the string buffer and writer in instance variables.
        '''

        # declare variables
        output_string_buffer = None
        output_writer = None
        
        # Make string buffer.
        output_string_buffer = StringIO()
        
        # Use it to create writer.
        output_writer = csv.writer( output_string_buffer, delimiter=self.delimiter )

        # store off these instances.
        self.csv_string_buffer = output_string_buffer
        self.csv_writer = output_writer

    #-- END method init_csv_output() --#


    def render_network_data( self ):

        """
            Assumes render method has already created network data by calling
               process_author_relations() and updated source person types by
               calling update_source_person_types().  Outputs a simple text
               matrix of ties.  For a given cell in the matrix, the value is an
               integer: 0 if no tie, 1 or greater if tie.  Each column value is
               separated by two spaces.

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
        include_render_details = False
        
        # include render details?
        include_render_details = self.include_render_details

        #--------------------------------------------------------------------
        # render network data based on people and ties.
        #--------------------------------------------------------------------
        
        # then, need to output.  For each network, output the network, then also
        #    output an attribute file that says, for all people whether each
        #    person was a reporter or a source.

        if ( include_render_details == True ):

            # output the N of the network.
            network_data_OUT += "\nN = " + str( len( self.master_person_list ) ) + "\n"
            
        #-- END check to see if include render details. --#
    
        # output network.
        network_data_OUT += self.create_csv_string()
        
        # if local debug is on but global debug isn't, output debug.
        if ( ( self.LOCAL_DEBUG_FLAG == True ) and ( self.DEBUG_FLAG == False ) ):
            network_data_OUT += "\n\n\n====================\nDEBUG\n====================\n\n" + self.debug
        #-- END DEBUG --#

        return network_data_OUT

    #-- END render_network_data() --#


#-- END class NDO_CSVMatrix --#