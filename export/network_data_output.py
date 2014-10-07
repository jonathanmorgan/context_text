'''
Copyright 2010-2014 Jonathan Morgan

This file is part of http://github.com/jonathanmorgan/sourcenet.

sourcenet is free software: you can redistribute it and/or modify it under the terms of the GNU Lesser General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.

sourcenet is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.

You should have received a copy of the GNU Lesser General Public License along with http://github.com/jonathanmorgan/sourcenet. If not, see http://www.gnu.org/licenses/.
'''

__author__="jonathanmorgan"
__date__ ="$May 1, 2010 6:26:35 PM$"

if __name__ == "__main__":
    print "Hello World"

#===============================================================================
# imports (in alphabetical order by package, then by name)
#===============================================================================

# python libraries
from abc import ABCMeta, abstractmethod

#import copy

# Django DB classes, just to play with...
#from django.db.models import Count # for aggregating counts of authors, sources.
#from django.db.models import Max   # for getting max value of author, source counts.

# Import the classes for our SourceNet application
#from sourcenet.models import Article
#from sourcenet.models import Article_Author
from sourcenet.models import Article_Source
#from sourcenet.models import Person
#from sourcenet.models import Topic

#===============================================================================
# classes (in alphabetical order by name)
#===============================================================================

class NetworkDataOutput( object ):

    
    #---------------------------------------------------------------------------
    # META!!!
    #---------------------------------------------------------------------------

    
    __metaclass__ = ABCMeta


    #---------------------------------------------------------------------------
    # CONSTANTS-ish
    #---------------------------------------------------------------------------


    # article output type constants
    NETWORK_OUTPUT_TYPE_SIMPLE_MATRIX = 'simple_matrix'

    OUTPUT_TYPE_CHOICES_LIST = [
        ( NETWORK_OUTPUT_TYPE_SIMPLE_MATRIX, "Simple Matrix" ),
    ]

    DEFAULT_NETWORK_OUTPUT_TYPE = NETWORK_OUTPUT_TYPE_SIMPLE_MATRIX

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
    DEBUG = False

    # parameter constants
    PARAM_OUTPUT_TYPE = 'output_type'
    PARAM_NETWORK_LABEL = 'network_label'
    PARAM_NETWORK_INCLUDE_HEADERS = 'network_include_headers'
    PARAM_SOURCE_CAPACITY_INCLUDE_LIST = Article_Source.PARAM_SOURCE_CAPACITY_INCLUDE_LIST
    PARAM_SOURCE_CAPACITY_EXCLUDE_LIST = Article_Source.PARAM_SOURCE_CAPACITY_EXCLUDE_LIST


    #---------------------------------------------------------------------------
    # __init__() method
    #---------------------------------------------------------------------------


    def __init__( self ):

        # declare variables
        self.query_set = None
        self.output_type = NetworkDataOutput.DEFAULT_NETWORK_OUTPUT_TYPE
        self.person_dictionary = {}
        self.network_label = '' # heading to put in first line of network data.
        self.relation_map = {}
        self.include_row_and_column_headers = False

        # need a way to keep track of who is a reporter and who is a source.
        # person ID to person type map
        self.person_type_dict = {}

        # variable to hold master person list.
        self.master_person_list = []

        # internal debug string
        self.debug = "NetworkDataOutput debug:\n\n"

        # inclusion parameter holder
        self.inclusion_params = {}

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

        if ( NetworkDataOutput.DEBUG == True ):
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

        # make sure we have two values.
        if ( person_1_id_IN and person_2_id_IN ):

            if ( NetworkDataOutput.DEBUG == True ):
                # output the author map
                self.debug += "\n\nin add_reciprocal_relation, got two IDs: " + str( person_1_id_IN ) + "; " + str( person_2_id_IN ) + ".\n\n"
            #-- END DEBUG --#

            # add directed relations from 1 to 2 and from 2 to 1.
            self.add_directed_relation( person_1_id_IN, person_2_id_IN )
            self.add_directed_relation( person_2_id_IN, person_1_id_IN )

            if ( NetworkDataOutput.DEBUG == True ):
                # output the author map
                self.debug += "\n\n*** in add_reciprocal_relation, after adding relations, relation_map:\n" + str( self.relation_map ) + "\n\n"
            #-- END DEBUG --#

        else:

            # error, something is missing.
            status_OUT = NetworkDataOutput.STATUS_ERROR_PREFIX + "in add_reciprocal relationship, one or more IDs is missing, so can't create relationship."

            if ( NetworkDataOutput.DEBUG == True ):
                # output the author map
                self.debug += "\n\n" + status_OUT + "\n\n"
            #-- END DEBUG --#

        #-- END check to make sure we have values. --#

        return status_OUT

    #-- END method add_reciprocal_relation --#


    def generate_master_person_list( self ):

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
        person_ids_list = None
        person_ids_count = None
        merged_person_types = None
        merged_person_id_list = None

        # retrieve the person dictionary
        person_dict = self.person_dictionary

        # grab list of keys from person_dictionary.
        person_ids_list = person_dict.keys()

        # make a dict from it.
        person_ids_count = len( person_ids_list )
        merge_values = []
        merge_values[ 0 : person_ids_count - 1 ] = NetworkDataOutput.PERSON_TYPE_UNKNOWN
        merged_person_types = dict( zip( person_ids_list, merge_values ) )

        # add in the people from the person_type_dict.
        merged_person_types.update( self.person_type_dict )

        # store this in the person_type_dict?

        # grab the ID list from this merged dictionary, sort it, and use it
        #    as your list of people to iterate over as you create actual
        #    output.
        merged_person_id_list = merged_person_types.keys()

        # save this as the master person list.
        self.master_person_list = merged_person_id_list

        list_OUT = merged_person_id_list

        return list_OUT

    #-- END method add_reciprocal_relation --#


    def get_master_person_list( self ):

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
            list_OUT = self.generate_master_person_list()

        #-- END check if list is OK. --#

        return list_OUT

    #-- END method add_reciprocal_relation --#


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


    def initialize_from_request( self, request_IN ):

        # declare variables
        output_type_IN = ''
        network_label_IN = ''
        source_capacity_include_list_IN = None
        source_capacity_exclude_list_IN = None

        # retrieve info.
        output_type_IN = request_IN.POST.get( NetworkDataOutput.PARAM_OUTPUT_TYPE, NetworkDataOutput.DEFAULT_NETWORK_OUTPUT_TYPE )
        network_label_IN = request_IN.POST.get( NetworkDataOutput.PARAM_NETWORK_LABEL, '' )
        source_capacity_include_list_IN = request_IN.POST.getlist( NetworkDataOutput.PARAM_SOURCE_CAPACITY_INCLUDE_LIST )
        source_capacity_exclude_list_IN = request_IN.POST.getlist( NetworkDataOutput.PARAM_SOURCE_CAPACITY_EXCLUDE_LIST )

        # store
        self.output_type = output_type_IN
        self.network_label = network_label_IN

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

    #-- END method initialize_from_request() --#


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

            Purpose: Accepts a QuerySet of authors and one of sources.  First,
               checks to see if multiple authors.  If so, loops and creates a
               dictionary that maps author ID to author instance.  Then,
               iterates over keys of this map.  For each author:
                  - removes that author from the local author dictionary
                  - registers them as an author in the person_type_dict
                  - loops over all remaining authors in the map, creating a
                     reciprocal relation with each.
                  - calls the process_source_relations() method to tie the
                     author to the sources passed in.
               If only one author, just registers them as an author and calls
               process_source_relations().

            Preconditions: connection_map must be initialized to a dictionary.
               Also must pass in something for author query set and source query
               set.

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
        #multiple_authors = False
        author_map = None
        current_author = None
        current_person_id = -1
        author_id_list = None
        remaining_author_id_list = None
        remaining_person_id = -1

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

            if ( NetworkDataOutput.DEBUG == True ):
                # output the author map
                self.debug += "\n\nauthor map:\n" + str( author_map ) + "\n\n"
            #-- END DEBUG --#


            # Now, make a copy of the keys of the map, for us to loop over.
            author_id_list = author_map.keys()

            # loop over keys.
            for current_person_id in author_id_list:

                if ( NetworkDataOutput.DEBUG == True ):
                    # output the author map
                    self.debug += "\n\nauthor person ID:\n" + str( current_person_id ) + "\n\n"
                #-- END DEBUG --#

                # remove author from author_map.  pop()-ing it, for now, just
                #    in case.  Eventually, probably should del:
                # del author_map[ current_author_id ]
                current_author = author_map.pop( current_person_id )

                if ( NetworkDataOutput.DEBUG == True ):
                    # output the author map
                    self.debug += "\n\nauthor map:\n" + str( author_map ) + "\n\n"
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
        author_map = None
        current_source = None
        is_connected = False
        current_person_id = -1
        source_counter = -1

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

                        if ( NetworkDataOutput.DEBUG == True ):
                            # output the author map
                            self.debug += "\n\nin process_source_relations, source " + str( source_counter ) + " has ID: " + str( current_person_id ) + ".\n\n"
                        #-- END DEBUG --#

                        if ( current_person_id ):

                            # relate the author and this source.
                            self.add_reciprocal_relation( author_id_IN, current_person_id )

                        #-- END check to make sure that the source has an associated person --#

                    else:

                        if ( NetworkDataOutput.DEBUG == True ):
                            # output the author map
                            self.debug += "\n\nin process_source_relations, source " + str( source_counter ) + " is not connected.\n\n"
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
        article_data_query_set = None
        person_dict = None
        network_dict = {}
        article_data_counter = 0
        current_article_data = None
        article_author_count = -1
        author_qs = None
        source_qs = None

        # start by grabbing person dict, query set.
        article_data_query_set = self.query_set
        person_dict = self.person_dictionary

        # make sure each of these has something in it.
        if ( ( article_data_query_set ) and ( person_dict ) ):

            #--------------------------------------------------------------------
            # create ties
            #--------------------------------------------------------------------
            
            # loop over the articles.
            for current_article_data in article_data_query_set:

                article_data_counter += 1

                if ( NetworkDataOutput.DEBUG == True ):
                    self.debug += "\n\n+++ Current article data = " + str( current_article_data.id ) + " +++\n\n"
                #-- END DEBUG --#

                # first, see how many authors this article has.
                article_author_count = current_article_data.article_author_set.count()

                # if no authors, move on.
                if ( article_author_count > 0 ):

                    # get authors
                    author_qs = current_article_data.article_author_set.all()
                    source_qs = current_article_data.article_source_set.all()

                    # call method to loop over authors and tie them to other
                    #    authors (if present) and eligible sources.
                    self.process_author_relations( author_qs, source_qs )

                    # update the person types for sources
                    self.update_source_person_types( source_qs )

                    if ( NetworkDataOutput.DEBUG == True ):
                        # output the relation thinger
                        self.debug += "\n\nRelation Map after article " + str( article_counter ) + ":\n" + str( self.relation_map ) + "\n\n"
                    #-- END DEBUG --#

                #-- END check to make sure there are authors.

            #-- END loop over articles.

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

            if ( NetworkDataOutput.DEBUG == True ):
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

        #-- END check to see if we have a value --#

    #-- END method set_output_type() --#


    def set_query_set( self, value_IN ):

        """
            Method: set_request()

            Purpose: accepts a query set, stores it in instance, then grabs the
               POST from the request and stores that as the params.

            Params:
            - request_IN - django QuerySet instance that contains the articles
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