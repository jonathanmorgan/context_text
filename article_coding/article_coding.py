from __future__ import unicode_literals

'''
Copyright 2010-2014 Jonathan Morgan

This file is part of http://github.com/jonathanmorgan/sourcenet.

sourcenet is free software: you can redistribute it and/or modify it under the terms of the GNU Lesser General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.

sourcenet is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.

You should have received a copy of the GNU Lesser General Public License along with http://github.com/jonathanmorgan/sourcenet. If not, see http://www.gnu.org/licenses/.
'''

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

# Import other Article coder classes
from sourcenet.article_coding.open_calais_article_coder import OpenCalaisArticleCoder


#===============================================================================
# classes (in alphabetical order by name)
#===============================================================================

class ArticleCoding( object ):


    #---------------------------------------------------------------------------
    # CONSTANTS-ish
    #---------------------------------------------------------------------------

    # network selection parameters we expect.
    PARAM_START_DATE = 'start_date'   # publication date - articles will be included that were published on or after this date.
    PARAM_END_DATE = 'end_date'   # publication date - articles will be included that were published on or before this date.
    PARAM_DATE_RANGE = 'date_range'   # For date range fields, enter any number of paired date ranges, where dates are in the format YYYY-MM-DD, dates are separated by the string " to ", and each pair of dates is separated by two pipes ("||").  Example: 2009-12-01 to 2009-12-31||2010-02-01 to 2010-02-28
    PARAM_PUBLICATION_LIST = 'publications'   # list of IDs of newspapers you want included.
    PARAM_TAG_LIST = 'tags_list'   # list of tag values that you want included.
    PARAM_UNIQUE_ID_LIST = 'unique_identifiers'   # list of unique identifiers of articles whose data you want included.
    PARAM_ARTICLE_ID_LIST = 'article_id_list'   # list of ids of articles whose data you want included.
    PARAM_CODER_TYPE = 'coder_type'   # list of ids of articles whose data you want included.

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
        PARAM_PUBLICATION_LIST : PARAM_TYPE_LIST,
        PARAM_TAG_LIST : PARAM_TYPE_LIST,
        PARAM_UNIQUE_ID_LIST : PARAM_TYPE_STRING,
        PARAM_ARTICLE_ID_LIST : PARAM_TYPE_STRING,
        PARAM_CODER_TYPE : PARAM_TYPE_STRING,
    }

    # variables for choosing yes or no.
    CHOICE_YES = 'yes'
    CHOICE_NO = 'no'

    # choices for yes or no decision.
    CHOICES_YES_OR_NO_LIST = [
        ( CHOICE_NO, "No" ),
        ( CHOICE_YES, "Yes" )
    ]

    # Article coding implementation choices.
    ARTICLE_CODING_IMPL_OPEN_CALAIS_API = "open_calais_api"
    ARTICLE_CODING_IMPL_CHOICES_LIST = [ ARTICLE_CODING_IMPL_OPEN_CALAIS_API, ]
    ARTICLE_CODING_IMPL_DEFAULT = ARTICLE_CODING_IMPL_OPEN_CALAIS_API


    #---------------------------------------------------------------------------
    # __init__() method
    #---------------------------------------------------------------------------


    def __init__( self ):

        # declare variables
        self.request = None
        self.params_dictionary = {}
        
    #-- END method __init__() --#


    #---------------------------------------------------------------------------
    # instance methods, in alphabetical order
    #---------------------------------------------------------------------------


    def code_article_data( self, query_set_IN ):

        """
            Accepts query set of Articles.  Creates a new instance of the
               ArticleCoder class for coder_type passed in, places the query set
               in it, sets up its instance variables appropriately according to
               the request, then codes the attribution in the articles using the
               coder class.  Returns status message.  Results in Article_Data for
               each attribution detected by the coder in each article.  Checks
               for the attribution to already have been detected using article,
               paragraph number, etc.  If so, does not create an additional
               Article_Data instance (could add a flag for this later if
               needed...).
            Preconditions: assumes that we have a query set of Articles passed
               in that we can store in the instance.  If not, does nothing,
               returns empty string.
            Postconditions: Returns status message.  Results in Article_Data for
               each attribution detected by the coder in each article.  Checks
               for the attribution to already have been detected using article,
               paragraph number, etc.  If so, does not create an additional
               Article_Data instance (could add a flag for this later if
               needed...).

            Parameters:
            - query_set_IN - django HTTP request instance that contains parameters we use to generate network data.

            Returns:
            - String - Status message.
        """

        # return reference
        status_OUT = ''

        # declare variables
        article_coder = None

        # do we have a query set?
        if ( query_set_IN ):

            # create instance of ArticleCoder.
            article_coder = self.get_coder_instance()

            # initialize it.
            article_coder.set_query_set( query_set_IN )
            article_coder.set_person_dictionary( person_dictionary )

            # initialize NetworkDataOutput instance from request.
            article_coder.initialize_from_request( self.request )

            # render and return the result.
            status_OUT = article_coder.code_articles()

            # add some debug?
            if ( ArticleCoder.DEBUG_FLAG == True ):

                # yup.
                status_OUT += "\n\n" + network_data_outputter.debug + "\n\n"

            #-- END check to see if we have debug to output. --#
        #-- END check to make sure we have a query set. --#

        return status_OUT

    #-- END code_article_data() --#


    def create_article_query_set( self, param_prefix_IN = '' ):

        # return reference
        query_set_OUT = None

        # declare variables
        params_IN = None
        start_date_IN = ''
        end_date_IN = ''
        date_range_IN = ''
        publication_list_IN = None
        tag_list_IN = None
        unique_id_list_IN = ''
        article_id_list_IN = ''
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

        # get the request
        params_IN = self.get_parameters()

        # got a request?
        if ( params_IN ):

            # retrieve the incoming parameters
            start_date_IN = self.get_string_param( param_prefix_IN + ArticleCoding.PARAM_START_DATE, '' )
            end_date_IN = self.get_string_param( param_prefix_IN + ArticleCoding.PARAM_END_DATE, '' )
            date_range_IN = self.get_string_param( param_prefix_IN + ArticleCoding.PARAM_DATE_RANGE, '' )
            publication_list_IN = self.get_list_param( param_prefix_IN + ArticleCoding.PARAM_PUBLICATION_LIST, None )
            tag_list_IN = self.get_list_param( param_prefix_IN + ArticleCoding.PARAM_TAG_LIST, None )
            unique_id_list_IN = self.get_list_param( param_prefix_IN + ArticleCoding.PARAM_UNIQUE_ID_LIST, None )
            article_id_list_IN = self.get_list_param( param_prefix_IN + ArticleCoding.PARAM_ARTICLE_ID_LIST, None )

            # get all articles to start
            query_set_OUT = Article.objects.all()

            # now filter based on parameters passed in.
            # start date
            if ( start_date_IN != '' ):

                # set up query instance
                current_query = Q( pub_date__gte = start_date_IN )

                # add it to list of queries
                query_list.append( current_query )

            #-- END processing of start_date --#

            # end date
            if ( end_date_IN != '' ):

                # set up query instance
                current_query = Q( pub_date__lte = end_date_IN )

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
                    date_range_q = Q( pub_date__gte = range_start_date ) & Q( pub_date__lte = range_end_date )

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
            if ( ( publication_list_IN is not None ) and ( len( publication_list_IN ) > 0 ) ):

                # loop over the publications, adding a Q object for each to the
                #    aggregated set of things we will pass to filter function.
                for current_item in publication_list_IN:

                    # set up query instance
                    current_query = Q( newspaper__id = int( current_item ) )

                    # see if we already have a query.  If not, make one.
                    if ( compound_query is None ):

                        # no.  Use the current query.
                        compound_query = current_query

                    else:

                        # yes.  Add to it.
                        compound_query = compound_query | current_query

                    #-- END check to see if we already have a query. --#

                #-- END loop over newspapers for which we are building a network. --#

                # add it to the query list
                query_list.append( compound_query )
                compound_query = None

            #-- END processing of publications --#

            # tags
            if ( ( tag_list_IN is not None ) and ( len( tag_list_IN ) > 0 ) ):

                # set up query instance
                current_query = Q( tags__name__in = tag_list_IN )

                # add it to the query list
                query_list.append( current_query )
                compound_query = None

            #-- END processing of tags --#

            # unique identifiers IN list
            if ( ( unique_id_list_IN is not None ) and ( len( unique_id_list_IN ) > 0 ) ):

                # set up query instance to look for articles with
                #    unique_identifier in the list of values passed in.  Not
                #    quoting, since django should do that.
                current_query = Q( unique_identifier__in = unique_id_list_IN )

                # add it to list of queries
                query_list.append( current_query )

            #-- END processing of unique_identifiers --#

            # article ID IN list
            if ( ( article_id_list_IN is not None ) and ( len( article_id_list_IN ) > 0 ) ):

                # set up query instance to look for articles with
                #    ID in the list of values passed in.  Not
                #    quoting, since django should do that.
                current_query = Q( id__in = article_id_list_IN )

                # add it to list of queries
                query_list.append( current_query )

            #-- END processing of article IDs --#

            # now, add them all to the QuerySet - try a loop
            for query_item in query_list:

                # append each filter to query set.
                query_set_OUT = query_set_OUT.filter( query_item )

            #-- END loop over query set items --#

        else:
        
            # no param container present.  Error.
            query_set_OUT = None
        
        #-- END check to make sure we have a param container. --#

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
                    param_value = self.get_string_param( param_name, '' )

                    # append to output string list.
                    param_output_string += param_value

                elif ( param_type == NetworkOutput.PARAM_TYPE_LIST ):

                    # get param value list
                    param_value_list = self.get_param( param_name )

                    # output list of values
                    for param_value in param_value_list:
                    
                        param_output_string += param_value + ", "
                        
                    #-- END loop over values in list. --#

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


    def get_coder_instance( self ):

        '''
        Assumes there is an output type property specified in the POST parameters
           passed in as part of the current request.  Retrieves this output type,
           creates a NetworkDataOutput implementer instance to match the type,
           then returns the instance.  If no type or unknown type, returns None.
        '''
        
        # return reference
        coder_instance_OUT = None

        # declare variables
        coder_type_IN = ""

        # get output type.
        coder_type_IN = self.get_string_param( self.PARAM_CODER_TYPE, self.ARTICLE_CODING_IMPL_DEFAULT )
        
        # make instance for coder type.
        if ( coder_type_IN == self.ARTICLE_CODING_IMPL_OPEN_CALAIS_API ):
        
            # Open Calais API.
            coder_instance_OUT = OpenCalaisArticleCoder()
        
        else:
        
            # no output type, or unknown.  Make simple output matrix.
            coder_instance_OUT = OpenCalaisArticleCoder()
        
        #-- END check to see what type we have. --#
        
        return coder_instance_OUT

    #-- END get_coder_instance() --#


    def get_parameters( self ):
        
        # return reference
        dict_OUT = ""
        
        # declare variables
        
        # try to retrieve value - for now, reference nested request.POST
        dict_OUT = self.params_dictionary
        
        return dict_OUT
        
    #-- END method get_parameters() --#
    
    
    def get_list_param( self, param_name_IN, default_IN = [], delimiter_IN = ',' ):
        
        # return reference
        list_OUT = []
        
        # declare variables
        list_param_value = ""
        param_type = ""
        working_list = []
        current_value = ""
        current_value_clean = ""
        missing_string = "get_list_param-missing"
        
        # first, try getting raw param, see if it is already a list.
        
        # get raw value
        list_param_value = self.get_param( param_name_IN, None )
        
        # get type string
        param_type = type( list_param_value )
        
        # check if list
        if param_type == list:
        
            # already a list - return it.
            list_OUT = list_param_value
            
        else:
        
            # not a list.  assume string.
        
            # get list param's original value
            list_param_value = self.get_string_param( param_name_IN, missing_string )
            
            # print( "====> list param value: " + list_param_value )
            
            # got a value?
            if ( ( list_param_value != "" ) and ( list_param_value != missing_string ) ):
            
                # yes - split on delimiter into a list
                working_list = list_param_value.split( delimiter_IN )
                
                # loop over the IDs, strip()-ing each then appending it to list_OUT.
                list_OUT = []
                for current_value in working_list:
             
                    # strip
                    current_value_clean = current_value.strip()
                    list_OUT.append( current_value_clean )
        
                #-- END loop over unique IDs passed in --#
            
            elif list_param_value == "":
            
                # return empty list.
                list_OUT = []
                
            elif list_param_value == missing_string:
            
                # return default
                list_OUT = default_IN
                
            else:
            
                # not sure how we got here - return default.
                list_OUT = default_IN
            
            #-- END check to see what was in value. --#
            
        #-- END check to see if already a list --#
        
        return list_OUT
        
    #-- END method get_list_param() --#
    

    def get_param( self, param_name_IN, default_IN = None ):
        
        # return reference
        value_OUT = ""
        
        # declare variables
        my_params = None
        
        # try to retrieve value - for now, reference nested parameters.
        my_params = self.get_parameters()
        value_OUT = my_params.get( param_name_IN, default_IN )
        
        return value_OUT
        
    #-- END method get_param() --#
    

    def get_string_param( self, param_name_IN, default_IN = '' ):
        
        # return reference
        value_OUT = ""
        
        # call get_param()
        value_OUT = self.get_param( param_name_IN, default_IN )
        
        # force conversion to string.
        value_OUT = str( value_OUT )
        
        return value_OUT
        
    #-- END method get_string_param() --#
    

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


    def set_parameters( self, dict_IN ):

        """
            Method: set_parameters()

            Purpose: accepts a dict of parameters, stores it in instance.
            
            Params:
            - dict_IN - dict of parameter names mapped to values.
        """

        # declare variables

        # got a request?
        if ( dict_IN ):

            # store params
            self.params_dictionary = dict_IN

        #-- END check to see if we have a dictionary --#

    #-- END method set_parameters() --#


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
            self.set_parameters( params_IN )

        #-- END check to see if we have a request --#

    #-- END method set_request() --#


#-- END class ArticleCoding --#