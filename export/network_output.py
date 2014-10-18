from __future__ import unicode_literals

'''
Copyright 2010-2013 Jonathan Morgan

This file is part of http://github.com/jonathanmorgan/sourcenet.

sourcenet is free software: you can redistribute it and/or modify it under the terms of the GNU Lesser General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.

sourcenet is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.

You should have received a copy of the GNU Lesser General Public License along with http://github.com/jonathanmorgan/sourcenet. If not, see http://www.gnu.org/licenses/.
'''

'''
The network_output module contains objects and code to parse and output social
   network data from sourcenet in a variety of formats, and also generates
   some descriptive statistics as it builds output.
   
2014-05-16 - Jonathan Morgan - Updated so that this object now speaks in terms
   of Article_Data, not Article, so that we support multiple passes at coding
   a given article by different people, only have to store the contents of each
   article once.
   
'''

__author__="jonathanmorgan"
__date__ ="$May 1, 2010 12:49:50 PM$"

if __name__ == "__main__":
    print "Hello World"

#===============================================================================
# imports (in alphabetical order by package, then by name)
#===============================================================================

# python base imports
#from datetime import date
from datetime import datetime
import operator
import StringIO
import pickle
#from operator import __or__

# django database classes
from django.db.models import Q

# Import the classes for our SourceNet application
from sourcenet.models import Article
from sourcenet.models import Article_Data

# Import sourcenet export classes.
from sourcenet.export.csv_article_output import CsvArticleOutput
from sourcenet.export.network_data_output import NetworkDataOutput
from sourcenet.export.ndo_simple_matrix import NDO_SimpleMatrix
from sourcenet.export.ndo_csv_matrix import NDO_CSVMatrix
from sourcenet.export.ndo_tab_delimited_matrix import NDO_TabDelimitedMatrix

#===============================================================================
# classes (in alphabetical order by name)
#===============================================================================

class NetworkOutput( object ):


    #---------------------------------------------------------------------------
    # CONSTANTS-ish
    #---------------------------------------------------------------------------

    # network selection parameters we expect.
    PARAM_START_DATE = 'start_date'   # publication date - articles will be included that were published on or after this date.
    PARAM_END_DATE = 'end_date'   # publication date - articles will be included that were published on or before this date.
    PARAM_DATE_RANGE = 'date_range'   # For date range fields, enter any number of paired date ranges, where dates are in the format YYYY-MM-DD, dates are separated by the string " to ", and each pair of dates is separated by two pipes ("||").  Example: 2009-12-01 to 2009-12-31||2010-02-01 to 2010-02-28
    PARAM_PUBLICATIONS = 'publications'   # list of IDs of newspapers you want included.
    PARAM_CODERS = 'coders'   # list of IDs of coders whose data you want included.
    PARAM_TOPICS = 'topics'   # list of IDs of topics whose data you want included.
    PARAM_UNIQUE_IDS = 'unique_identifiers'   # list of unique identifiers of articles whose data you want included.
    PARAM_HEADER_PREFIX = 'header_prefix'   # for output, optional prefix you want appended to front of column header names.
    PARAM_OUTPUT_TYPE = 'output_type'   # type of output you want, either CSV, tab-delimited, or old UCINet format that I should just remove.
    PARAM_ALLOW_DUPLICATE_ARTICLES = 'allow_duplicate_articles'   # allow duplicate articles...  Not sure this is relevant anymore.

    # parameters specific to network output
    PARAM_NETWORK_DOWNLOAD_AS_FILE = NetworkDataOutput.PARAM_NETWORK_DOWNLOAD_AS_FILE
    PARAM_NETWORK_LABEL = NetworkDataOutput.PARAM_NETWORK_LABEL
    PARAM_NETWORK_INCLUDE_HEADERS = NetworkDataOutput.PARAM_NETWORK_INCLUDE_HEADERS
    PARAM_NETWORK_INCLUDE_RENDER_DETAILS = NetworkDataOutput.PARAM_NETWORK_INCLUDE_RENDER_DETAILS
    PARAM_NETWORK_DATA_OUTPUT_TYPE = NetworkDataOutput.PARAM_NETWORK_DATA_OUTPUT_TYPE

    # prefix for person-selection params - same as network selection parameters
    #    above, but with this prefix appended to the front.
    PARAM_PERSON_PREFIX = 'person_'

    # constants for parsing date range string
    PARAM_DATE_RANGE_ITEM_SEPARATOR = '||'
    PARAM_DATE_RANGE_DATE_SEPARATOR = ' to '
    PARAM_DATE_RANGE_DATE_FORMAT = '%Y-%m-%d'

    # types of params.
    PARAM_TYPE_LIST = 'list'
    PARAM_TYPE_STRING = 'string'

    # Dictionary of parameters to their types, for use in debug method.
    PARAM_NAME_TO_TYPE_MAP = {
        PARAM_START_DATE : PARAM_TYPE_STRING,
        PARAM_END_DATE : PARAM_TYPE_STRING,
        PARAM_DATE_RANGE : PARAM_TYPE_STRING,
        PARAM_PUBLICATIONS : PARAM_TYPE_LIST,
        PARAM_CODERS : PARAM_TYPE_LIST,
        PARAM_TOPICS : PARAM_TYPE_LIST,
        PARAM_UNIQUE_IDS : PARAM_TYPE_STRING,
        PARAM_HEADER_PREFIX : PARAM_TYPE_STRING,
        PARAM_NETWORK_DOWNLOAD_AS_FILE : PARAM_TYPE_STRING,
        PARAM_NETWORK_INCLUDE_RENDER_DETAILS : PARAM_TYPE_STRING,
        PARAM_OUTPUT_TYPE : PARAM_TYPE_STRING,
        PARAM_NETWORK_DATA_OUTPUT_TYPE : PARAM_TYPE_STRING,
        PARAM_ALLOW_DUPLICATE_ARTICLES : PARAM_TYPE_STRING,
        PARAM_NETWORK_LABEL : PARAM_TYPE_STRING,
        PARAM_NETWORK_INCLUDE_HEADERS : PARAM_TYPE_STRING,
        PARAM_PERSON_PREFIX + PARAM_START_DATE : PARAM_TYPE_STRING,
        PARAM_PERSON_PREFIX + PARAM_END_DATE : PARAM_TYPE_STRING,
        PARAM_PERSON_PREFIX + PARAM_DATE_RANGE : PARAM_TYPE_STRING,
        PARAM_PERSON_PREFIX + PARAM_PUBLICATIONS : PARAM_TYPE_LIST,
        PARAM_PERSON_PREFIX + PARAM_CODERS : PARAM_TYPE_LIST,
        PARAM_PERSON_PREFIX + PARAM_TOPICS : PARAM_TYPE_LIST,
        PARAM_PERSON_PREFIX + PARAM_UNIQUE_IDS : PARAM_TYPE_STRING,
        PARAM_PERSON_PREFIX + PARAM_ALLOW_DUPLICATE_ARTICLES : PARAM_TYPE_STRING
    }

    OUTPUT_TYPE_CHOICES_LIST = [
        ( CsvArticleOutput.ARTICLE_OUTPUT_TYPE_ARTICLE_PER_LINE, "One article per line" ),
        ( CsvArticleOutput.ARTICLE_OUTPUT_TYPE_SOURCE_PER_LINE, "One source per line" ),
        ( CsvArticleOutput.ARTICLE_OUTPUT_TYPE_AUTHOR_PER_LINE, "One author per line" )
    ]

    # variables for choosing yes or no.
    CHOICE_YES = 'yes'
    CHOICE_NO = 'no'

    # choices for yes or no decision.
    CHOICES_YES_OR_NO_LIST = [
        ( CHOICE_NO, "No" ),
        ( CHOICE_YES, "Yes" )
    ]

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

    #---------------------------------------------------------------------------
    # __init__() method
    #---------------------------------------------------------------------------


    def __init__( self ):

        # declare variables
        self.request = None
        self.params_dictionary = {}

        # variables for outputting result as file
        self.mime_type = ""
        self.file_extension = ""
        
    #-- END method __init__() --#


    #---------------------------------------------------------------------------
    # instance methods, in alphabetical order
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
            - dictionary_IN - dictionary we want to add people to.  Returned
                with people added.
            - person_qs_IN - django query set object that contains the people we
                want to add to our dictionary.
            - store_person_IN - boolean, if False, doesn't load Person model
                instances while building the dictionary.  If True, loads Person
                models and stores them in the dictionary.

            Returns:
            - Dictionary - dictionary that contains all the people in the query
                set of Article_Person implementors passed in, either mapped to
                None or to Person model instances, depending on the
                load_person_IN flag value.
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

            #-- END check to see if there is a person (in comparison to an anonymous source, for instance, or the author just being the newspaper)

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


    def create_person_dict( self, load_person_IN = False ):

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
            - request_IN - django request object.
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
        request_IN = None
        article_data_query_set = None
        current_article_data = None
        author_qs = None
        source_qs = None

        # get request instance
        request_IN = self.request

        # got request?
        if ( request_IN ):

            # get query set to loop over Article_Data that matches our person
            #    select criteria.
            article_data_query_set = self.create_person_query_set()

            # loop over the articles
            for current_article_data in article_data_query_set:

                # retrieve authors and add them to dict
                author_qs = current_article_data.article_author_set.all()
                person_dict_OUT = self.add_people_to_dict( author_qs, person_dict_OUT, load_person_IN )

                # retrieve sources and add them to dict
                source_qs = current_article_data.article_source_set.all()
                person_dict_OUT = self.add_people_to_dict( source_qs, person_dict_OUT, load_person_IN )

            #-- END loop over articles --#

        #-- END check to make sure we have a request --#

        return person_dict_OUT

    #-- END function create_person_dict() --#


    def create_person_query_set( self ):

        # return reference
        query_set_OUT = None

        # declare variables

        # call the create query set method, use person_start_date, person_end_date
        #    as date boundaries for retrieval of all people across multiple slices.
        query_set_OUT = self.create_query_set( NetworkOutput.PARAM_PERSON_PREFIX )

        return query_set_OUT

    #-- end method output_create_person_query_set() ---------------------------#


    def create_query_set( self, param_prefix_IN = '' ):

        # return reference
        query_set_OUT = None

        # declare variables
        request_IN = None
        start_date_IN = ''
        end_date_IN = ''
        date_range_IN = ''
        publications_IN = None
        coders_IN = None
        topics_IN = None
        unique_ids_IN = ''
        allow_duplicate_articles_IN = ''
        date_range_list = None
        date_range_pair = None
        range_start_date = None
        range_end_date = None
        date_range_q = None
        date_range_q_list = None
        current_item = None
        compound_query = None
        current_query = None
        query_list = []
        unique_id_IN_list = None
        unique_id_list = None
        unique_id = ''
        unique_id_clean = ''
        #unique_id_in_string = ''

        # get the request
        request_IN = self.request

        # got a request?
        if ( request_IN ):

            # retrieve the incoming parameters
            start_date_IN = request_IN.POST.get( param_prefix_IN + NetworkOutput.PARAM_START_DATE, '' )
            end_date_IN = request_IN.POST.get( param_prefix_IN + NetworkOutput.PARAM_END_DATE, '' )
            date_range_IN = request_IN.POST.get( param_prefix_IN + NetworkOutput.PARAM_DATE_RANGE, '' )
            publications_IN = request_IN.POST.getlist( param_prefix_IN + NetworkOutput.PARAM_PUBLICATIONS )
            coders_IN = request_IN.POST.getlist( param_prefix_IN + NetworkOutput.PARAM_CODERS )
            topics_IN = request_IN.POST.getlist( param_prefix_IN + NetworkOutput.PARAM_TOPICS )
            unique_ids_IN = request_IN.POST.get( param_prefix_IN + NetworkOutput.PARAM_UNIQUE_IDS, '' )
            allow_duplicate_articles_IN = request_IN.POST.get( param_prefix_IN + NetworkOutput.PARAM_ALLOW_DUPLICATE_ARTICLES, NetworkOutput.CHOICE_NO )

            # get all articles to start
            query_set_OUT = Article_Data.objects.all()

            # now filter based on parameters passed in.
            # start date
            if ( start_date_IN != '' ):

                # set up query instance
                current_query = Q( article__pub_date__gte = start_date_IN )

                # add it to list of queries
                query_list.append( current_query )

            #-- END processing of start_date --#

            # end date
            if ( end_date_IN != '' ):

                # set up query instance
                current_query = Q( article__pub_date__lte = end_date_IN )

                # add it to list of queries
                query_list.append( current_query )

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
                    query_list.append( current_query )

                #-- END check to see if we have any valid date ranges.

            #-- END processing of date range --#

            # publications
            if ( publications_IN ):

                # loop over the publications, adding a Q object for each to the
                #    aggregated set of things we will pass to filter function.
                for current_item in publications_IN:

                    # set up query instance
                    current_query = Q( article__newspaper__id = current_item )

                    # see if we already have a query.  If not, make one.
                    if ( compound_query is None ):
                        compound_query = current_query

                    else:
                        compound_query = compound_query | current_query

                #-- end loop over newspapers for which we are building a network. --#

                # add it to the query list
                query_list.append( compound_query )
                compound_query = None

            #-- END processing of publications --#

            # coders
            if ( coders_IN ):

                # loop over the coders, adding a Q object for each to the
                #    aggregated set of things we will pass to filter function.
                for current_item in coders_IN:

                    # set up query instance
                    current_query = Q( coder__id = current_item )

                    # see if we already have a query.  If not, make one.
                    if ( compound_query is None ):
                        compound_query = current_query

                    else:
                        compound_query = compound_query | current_query

                #-- end loop over coders whose articles we are including in network. --#

                # add it to the query list
                query_list.append( compound_query )
                compound_query = None

            #-- END processing of coders --#

            # topics
            if ( topics_IN ):

                # loop over the topics, adding a Q object for each to the
                #    aggregated set of things we will pass to filter function.
                for current_item in topics_IN:

                    # set up query instance
                    current_query = Q( topics__id = current_item )

                    # see if we already have a query.  If not, make one.
                    if ( compound_query is None ):
                        compound_query = current_query

                    else:
                        compound_query = compound_query & current_query

                #-- end loop over topics we are including in network. --#

                # add it to the query list
                query_list.append( compound_query )
                compound_query = None

            #-- END processing of topics --#


            # unique identifiers IN list
            if ( unique_ids_IN ):

                # convert to an array, delimited on commas.
                unique_id_IN_list = unique_ids_IN.split( ',' )

                # loop over the IDs, strip()-ing each, enclosing it in quotes,
                #    then appending it to our unique_id_in_string.
                unique_id_list = []
                for unique_id in unique_id_IN_list:

                    # strip, then enclose in quotes
                    unique_id_clean = unique_id.strip()
                    #unique_id = '"' + unique_id_clean + '"'
                    unique_id_list.append( unique_id_clean )

                #-- END loop over unique IDs passed in --#

                # set up query instance to look for articles with
                #    unique_identifier in the list of values passed in.  Not
                #    quoting, since django should do that.
                current_query = Q( article__unique_identifier__in = unique_id_list )

                # add it to list of queries
                query_list.append( current_query )

            #-- END processing of unique_identifiers --#

            # now, add them all to the QuerySet - try a loop
            for query_item in query_list:

                # append each filter to query set.
                query_set_OUT = query_set_OUT.filter( query_item )

            #-- END loop over query set items --#

            # see if we are omitting duplicates - can only do this if no unique
            #    IDs specified.  Those take precedence (and django can't handle
            #    multiple IN statements).
            if ( ( allow_duplicate_articles_IN == NetworkOutput.CHOICE_NO ) and ( unique_ids_IN == '' ) ):

                # remove duplicate articles.
                query_set_OUT = self.remove_duplicate_article_data( query_set_OUT )

            #-- END check to see if we allow duplicates --#

        else:
        
            # no request set.  Error.
            query_set_OUT = None
        
        #-- END check to make sure we have a request. --#

        return query_set_OUT

    #-- end method create_query_set() ------------------------------------------


    def debug_parameters( self ):

        # return reference
        string_OUT = ''

        # declare variables
        request_IN = None
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

        # retrieve request
        request_IN = self.request
        
        # got a request?
        if ( request_IN ):

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
                    param_value = request_IN.POST.get( param_name, '' )

                    # append to output string list.
                    param_output_string += param_value

                elif ( param_type == NetworkOutput.PARAM_TYPE_LIST ):

                    # get param value list
                    param_value_list = request_IN.POST.getlist( param_name )

                    # output list of values
                    for param_value in param_value_list:
                        param_output_string += param_value + ", "

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
            article_output_string = "Article selection parameters:\n-----------------------------\n"
            person_output_string = "Person selection parameters:\n----------------------------\n"

            # now, join the parameters together for each, separated by "\n".
            list_separator_string = "\n"
            article_output_string += list_separator_string.join( article_output_string_list )
            person_output_string += list_separator_string.join( person_output_string_list )
            
            # And, finally, add them all together.
            string_OUT = article_output_string + "\n\n" + person_output_string

        #-- END check to see if we have a request --#

        return string_OUT

    #-- end method debug_parameters() ------------------------------------------


    def get_string_property( self, prop_name_IN, default_IN = '' ):
        
        # return reference
        value_OUT = ""
        
        # declare variables
        
        # try to retrieve value - for now, reference nested request.POST
        value_OUT = self.request.POST.get( prop_name_IN, default_IN )
        
        return value_OUT
        
    #-- END method get_string_property() --#
    

    def get_NDO_instance( self ):

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
        output_type_IN = self.get_string_property( self.PARAM_OUTPUT_TYPE )
        
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

        return NDO_instance_OUT

    #-- END get_NDO_instance() --#


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
        csv_outputter = None
        output_type_IN = ''
        header_prefix_IN = ''

        # do we have a query set?
        if ( query_set_IN ):

            # retrieve the output type and header_prefix.
            output_type_IN = self.request.POST.get( NetworkOutput.PARAM_OUTPUT_TYPE, '' )
            header_prefix_IN = self.request.POST.get( NetworkOutput.PARAM_HEADER_PREFIX, '' )

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


    def remove_duplicate_article_data( self, query_set_IN ):

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
            - QuerySet - QuerySet of Article_Data instances with only one Article_Data row per Article.
        """

        # return reference
        qs_OUT = ''

        # declare variables
        unique_article_id_to_article_data_id_dict = {}
        current_article_data = None
        current_article = None
        current_unique_id = ''
        current_id = -1
        omit_id_list = []

        # do we have a query set?
        if ( query_set_IN ):

            # loop over the article data
            for current_article_data in query_set_IN:

                # got an article?
                current_article = current_article_data.article
                if ( current_article ):

                    # yes - get unique identifier of article
                    current_unique_id = current_article.unique_identifier

                    # get ID of current Article_Data row.
                    current_id = current_article_data.id
    
                    # is the unique_id in the dict?
                    if current_unique_id in unique_article_id_to_article_data_id_dict:
    
                        # yes - so, this is a duplicate.  Add id to omit list.
                        omit_id_list.append( current_id )
    
                    else:
    
                        # not in dict, so add it and its ID.
                        unique_article_id_to_article_data_id_dict[ current_unique_id ] = current_id
    
                    #-- END check to see if duplicate. --#
                    
                #-- END check to see if we have an article. --#

            #-- END loop over article data --#

            # anything in omit list?
            if ( len( omit_id_list ) > 0 ):

                # IDs to omit.
                qs_OUT = query_set_IN.exclude( id__in = omit_id_list )

            #-- END check to see if we have to omit IDs --#

        #-- END check to make sure we have a query set. --#

        return qs_OUT

    #-- END remove_duplicate_article_data() --#


    def render_network_data( self, query_set_IN ):

        """
            Accepts query set of Article_Data.  Creates a new instance of the
               CsvArticleOutput class, places the query set in it, sets up its
               instance variables appropriately according to the request, then
               renders CSV output and returns that output as a string.
               Uses the query set to output CSV data in the format specified in
               the output_type request parameter.  If one line per article, has
               sets of columns for as many authors and sources as are present in
               the articles with the most authors and sources, respectively.  If
               one line per source, each article is given a line for each source
               with all other article information duplicated for each source. If
               one line per author, each article is given a line for each author
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
        network_OUT = ''

        # declare variables
        network_data_outputter = None
        person_dictionary = None
        output_type_IN = ''
        network_label_IN = ''
        output_headers_IN = ''

        # do we have a query set?
        if ( query_set_IN ):

            # create the person_dictionary
            person_dictionary = self.create_person_dict()

            # create instance of NetworkDataOutput.
            network_data_outputter = self.get_NDO_instance()

            # initialize it.
            network_data_outputter.set_query_set( query_set_IN )
            network_data_outputter.set_person_dictionary( person_dictionary )

            # initialize NetworkDataOutput instance from request.
            network_data_outputter.initialize_from_request( self.request )

            # render and return the result.
            network_OUT = network_data_outputter.render()

            # add some debug?
            if ( NetworkDataOutput.DEBUG_FLAG == True ):

                # yup.
                network_OUT += "\n\n" + network_data_outputter.debug + "\n\n"

            #-- END check to see if we have debug to output. --#
        #-- END check to make sure we have a query set. --#

        return network_OUT

    #-- END render_network_data() --#


    def parse_date_range( self, date_range_IN ):
        
        """
            Method: parse_date_range()
            
            Purpose: Accepts a date range string, parses it, and returns a list
               of date ranges that need to be OR-ed together.  The text in date
               range field can be parsed out into date ranges - semi-colon
               delimited, " to " between dates that bound a range.  Could add
               more complexity later.  As soon as we start doing that, need an
               object for date ranges.  For now, not so much.

            Ex.:
                2009-12-01 to 2009-12-31;2010-02-01 to 2010-02-28
                
            Params:
            - date_range_IN - date range string we need to parse.
            
            Returns:
            - List of Lists - List of pairs of date instances (two item lists) that are to be OR-ed together.
        """
        
        # return reference
        date_range_list_OUT = []
        
        # declare variables
        date_range_list = None
        date_range_string = ''
        date_range_date_list = ''
        from_string = ''
        to_string = ''
        from_date = None
        to_date = None
        date_pair_list = None
        
        # got a date range value?
        if ( date_range_IN != '' ):
        
            # got something - break it up on ";"
            date_range_list = date_range_IN.split( NetworkOutput.PARAM_DATE_RANGE_ITEM_SEPARATOR )

            # iterate over list, splitting each item on " to " and then if two
            #    things found, place them in a list and append that list to the
            #    output list.
            for date_range_string in date_range_list:

                # split on " to "
                date_range_date_list = date_range_string.split( NetworkOutput.PARAM_DATE_RANGE_DATE_SEPARATOR )

                # grab dates
                from_string = date_range_date_list[ 0 ]
                to_string = date_range_date_list[ 1 ]

                # make sure we have two values.  If not, do nothing.
                if ( ( from_string != '' ) and ( to_string != '' ) ):

                    # convert to date instances
                    from_date = datetime.strptime( from_string, NetworkOutput.PARAM_DATE_RANGE_DATE_FORMAT )
                    from_date = from_date.date()
                    to_date = datetime.strptime( to_string, NetworkOutput.PARAM_DATE_RANGE_DATE_FORMAT )
                    to_date = to_date.date()

                    # put the date()s in a list.
                    date_pair_list = [ from_date, to_date ]

                    # add list to output list.
                    date_range_list_OUT.append( date_pair_list )

                #-- END check to see if we have two values. --#

            #-- END loop over date range strings --#
        
        #-- END check to see if date range value set. --#
        
        return date_range_list_OUT

    #-- END parse_date_range() --#


    def set_request( self, request_IN ):

        """
            Method: set_request()

            Purpose: accepts a request, stores it in instance, then grabs the
                POST from the request and stores that as the params.

            Params:
            - request_IN - django HTTPRequest instance.
        """

        # declare variables
        params_IN = None

        # got a request?
        if ( request_IN ):

            # store request
            self.request = request_IN

            # get params
            params_IN = request_IN.POST

            # store params
            self.params_dictionary = params_IN

        #-- END check to see if we have a request --#

    #-- END method set_request() --#


#-- END class NetworkOutput --#