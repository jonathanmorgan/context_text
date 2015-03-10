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
import logging
import operator

# django database classes
from django.db.models import Q

# python_utilities
from python_utilities.exceptions.exception_helper import ExceptionHelper
from python_utilities.logging.summary_helper import SummaryHelper
from python_utilities.parameters.param_container import ParamContainer

# Import the classes for our SourceNet application
from sourcenet.models import Article
from sourcenet.models import Article_Data

# Import other Article coder classes
from sourcenet.article_coding.article_coder import ArticleCoder
from sourcenet.article_coding.open_calais_article_coder import OpenCalaisArticleCoder
from python_utilities.logging.summary_helper import SummaryHelper
from python_utilities.rate_limited.basic_rate_limited import BasicRateLimited

# Import sourcenet shared classes.
from sourcenet.shared.sourcenet_base import SourcenetBase


#===============================================================================
# classes (in alphabetical order by name)
#===============================================================================

class ArticleCoding( SourcenetBase ):


    #---------------------------------------------------------------------------
    # CONSTANTS-ish
    #---------------------------------------------------------------------------

    # network selection parameters we expect. - moved to parent
    #PARAM_START_DATE = 'start_date'   # publication date - articles will be included that were published on or after this date.
    #PARAM_END_DATE = 'end_date'   # publication date - articles will be included that were published on or before this date.
    #PARAM_DATE_RANGE = 'date_range'   # For date range fields, enter any number of paired date ranges, where dates are in the format YYYY-MM-DD, dates are separated by the string " to ", and each pair of dates is separated by two pipes ("||").  Example: 2009-12-01 to 2009-12-31||2010-02-01 to 2010-02-28
    #PARAM_PUBLICATION_LIST = 'publications'   # list of IDs of newspapers you want included.
    #PARAM_TAG_LIST = 'tags_list'   # list of tag values that you want included.
    #PARAM_SECTION_LIST = 'section_list'   # list of tag values that you want included.
    #PARAM_UNIQUE_ID_LIST = 'unique_identifiers'   # list of unique identifiers of articles whose data you want included.
    #PARAM_ARTICLE_ID_LIST = 'article_id_list'   # list of ids of articles whose data you want included.

    # parameters that are unique to this class.
    PARAM_CODER_TYPE = 'coder_type'   # type of coder we want to use, in case there are multiple implementations.

    # constants for parsing date range string - moved to parent
    #PARAM_DATE_RANGE_ITEM_SEPARATOR = '||'
    #PARAM_DATE_RANGE_DATE_SEPARATOR = ' to '
    #PARAM_DATE_RANGE_DATE_FORMAT = '%Y-%m-%d'

    # types of params.
    #PARAM_TYPE_LIST = 'list'
    #PARAM_TYPE_STRING = 'string'

    # Dictionary of parameters to their types, for use in debug method.
    PARAM_NAME_TO_TYPE_MAP = {
        SourcenetBase.PARAM_START_DATE : ParamContainer.PARAM_TYPE_STRING,
        SourcenetBase.PARAM_END_DATE : ParamContainer.PARAM_TYPE_STRING,
        SourcenetBase.PARAM_DATE_RANGE : ParamContainer.PARAM_TYPE_STRING,
        SourcenetBase.PARAM_PUBLICATION_LIST : ParamContainer.PARAM_TYPE_LIST,
        SourcenetBase.PARAM_TAG_LIST : ParamContainer.PARAM_TYPE_LIST,
        SourcenetBase.PARAM_SECTION_LIST : ParamContainer.PARAM_TYPE_LIST,
        SourcenetBase.PARAM_UNIQUE_ID_LIST : ParamContainer.PARAM_TYPE_STRING,
        SourcenetBase.PARAM_ARTICLE_ID_LIST : ParamContainer.PARAM_TYPE_STRING,
        PARAM_CODER_TYPE : ParamContainer.PARAM_TYPE_STRING,
    }

    # variables for choosing yes or no.
    #CHOICE_YES = 'yes'
    #CHOICE_NO = 'no'

    # choices for yes or no decision.
    #CHOICES_YES_OR_NO_LIST = [
    #    ( CHOICE_NO, "No" ),
    #    ( CHOICE_YES, "Yes" )
    #]

    # Article coding implementation choices.
    ARTICLE_CODING_IMPL_OPEN_CALAIS_API = "open_calais_api"
    ARTICLE_CODING_IMPL_CHOICES_LIST = [ ARTICLE_CODING_IMPL_OPEN_CALAIS_API, ]
    ARTICLE_CODING_IMPL_DEFAULT = ARTICLE_CODING_IMPL_OPEN_CALAIS_API


    #---------------------------------------------------------------------------
    # NOT Instance variables
    # Class variables - overriden by __init__() per instance if same names, but
    #    if not set there, shared!
    #---------------------------------------------------------------------------
    
    # exception helper.
    #exception_helper = None
    
    #---------------------------------------------------------------------------
    # __init__() method
    #---------------------------------------------------------------------------


    def __init__( self ):

        # call parent's __init__()
        super( ArticleCoding, self ).__init__()

        # declare variables
        my_exception_helper = None
        
        # exception helper
        self.exception_helper = None
        my_exception_helper = ExceptionHelper()
        #my_exception_helper.set_logging_level( logging.DEBUG )
        self.set_exception_helper( my_exception_helper )
        
        # ==> moved to parent class SourcenetBase
        #self.request = None
        #self.parameters = ParamContainer()
        # define parameters
        #self.define_parameters( ArticleCoding.PARAM_NAME_TO_TYPE_MAP )
        
        # set logger name (for LoggingHelper parent class: (LoggingHelper --> BasicRateLimited --> SourcenetBase --> ArticleCoding).
        self.set_logger_name( "sourcenet.article_coding.article_coding" )
        
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
        my_logger = None
        my_summary_helper = None
        summary_string = ""
        article_coder = None
        param_dict = {}
        current_status = ""
        my_exception_helper = None
        exception_message = ""
        
        # rate-limiting variables
        am_i_rate_limited = False
        continue_work = True
        
        # auditing variables
        article_counter = -1
        exception_counter = -1
        
        # grab a logger.
        my_logger = self.get_logger()
        
        # initialize summary helper
        my_summary_helper = SummaryHelper()
        
        # init rate-limiting
        am_i_rate_limited = self.do_manage_time

        # do we have a query set?
        if ( query_set_IN ):

            # create instance of ArticleCoder.
            article_coder = self.get_coder_instance()

            # initialize ArticleCoder instance from params.
            
            # Get parent parameter container.
            my_params = self.get_param_container()
            
            # retrieve the inner dictionary.
            param_dict = my_params.get_parameters()
            
            # use the dictionary from the param container to initialize.
            article_coder.initialize_from_params( param_dict )

            # loop on the article list, passing each to the ArticleCoder for
            #    processing.
            article_counter = 0
            exception_counter = 0
            continue_work = True
            for current_article in query_set_IN:
            
                # OK to continue work?
                if ( continue_work == True ):

                    # increment article counter
                    article_counter += 1
                    
                    # rate-limited?
                    if ( am_i_rate_limited == True ):
                    
                        # yes - start timer.
                        self.start_request()
                    
                    #-- END pre-request check for rate-limiting --#
                    
                    # a little debugging to start
                    my_logger.info( "\n\n============================================================\n==> article " + str( article_counter ) + ": " + str( current_article.id ) + " - " + current_article.headline )
                    
                    # add per-article exception handling, so we can get an idea of how
                    #    many articles cause problems.
                    try:
                
                        # code the article.
                        current_status = article_coder.code_article( current_article )
                        
                    except Exception as e:
                        
                        # increment exception_counter
                        exception_counter += 1
                        
                        # get exception helper.
                        my_exception_helper = self.get_exception_helper()
                        
                        # log exception, no email or anything.
                        exception_message = "Exception caught for article " + str( current_article.id )
                        my_exception_helper.process_exception( e, exception_message )
                        
                        my_logger.debug( "======> " + exception_message )
                        
                    #-- END exception handling around individual article processing. --#
                
                    # rate-limited?
                    if ( am_i_rate_limited == True ):
                    
                        # yes - check if we may continue.
                        continue_work = self.may_i_continue()
                    
                    #-- END post-request check for rate-limiting --#
                    
                else:
                
                    # not OK to continue work.  Break?
                    #break
                    pass
                
                #-- END check to see if OK to continue.  If not... --#
                
            #-- END loop over articles --#

            # add some debug?
            if ( ArticleCoder.DEBUG_FLAG == True ):

                # yup.
                status_OUT += "\n\n" + article_coder.debug + "\n\n"

            #-- END check to see if we have debug to output. --#

        #-- END check to make sure we have a query set. --#
        
        # add stuff to summary and print the results.

        # set stop time
        my_summary_helper.set_stop_time()

        # add stuff to summary
        my_summary_helper.set_prop_value( "article_counter", article_counter )
        my_summary_helper.set_prop_desc( "article_counter", "Articles processed" )

        my_summary_helper.set_prop_value( "exception_counter", exception_counter )
        my_summary_helper.set_prop_desc( "exception_counter", "Exception count" )

        # output - set prefix if you want.
        summary_string += my_summary_helper.create_summary_string( item_prefix_IN = "==> " )
        my_logger.info( summary_string )
        
        # output summary string as status.
        status_OUT += "\n\n" + summary_string

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
        section_list_IN = None
        unique_id_list_IN = ''
        article_id_list_IN = ''
        date_range_list = None
        date_range_pair = None
        range_start_date = None
        range_end_date = None
        date_range_q = None
        date_range_q_list = None
        current_item = None
        current_query = None
        query_list = []

        # get the request
        params_IN = self.get_param_container()

        # got a request?
        if ( params_IN ):

            # retrieve the incoming parameters
            start_date_IN = self.get_param_as_str( param_prefix_IN + SourcenetBase.PARAM_START_DATE, '' )
            end_date_IN = self.get_param_as_str( param_prefix_IN + SourcenetBase.PARAM_END_DATE, '' )
            date_range_IN = self.get_param_as_str( param_prefix_IN + SourcenetBase.PARAM_DATE_RANGE, '' )
            publication_list_IN = self.get_param_as_list( param_prefix_IN + SourcenetBase.PARAM_PUBLICATION_LIST, None )
            tag_list_IN = self.get_param_as_list( param_prefix_IN + SourcenetBase.PARAM_TAG_LIST, None )
            unique_id_list_IN = self.get_param_as_list( param_prefix_IN + SourcenetBase.PARAM_UNIQUE_ID_LIST, None )
            article_id_list_IN = self.get_param_as_list( param_prefix_IN + SourcenetBase.PARAM_ARTICLE_ID_LIST, None )
            section_list_IN = self.get_param_as_list( param_prefix_IN + SourcenetBase.PARAM_SECTION_LIST, None )

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

                # set up query instance
                current_query = Q( newspaper__id__in = publication_list_IN )

                # add it to the query list
                query_list.append( current_query )

            #-- END processing of publications --#

            # tags
            if ( ( tag_list_IN is not None ) and ( len( tag_list_IN ) > 0 ) ):

                # set up query instance
                current_query = Q( tags__name__in = tag_list_IN )

                # add it to the query list
                query_list.append( current_query )

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

            # section string list
            if ( ( section_list_IN is not None ) and ( len( section_list_IN ) > 0 ) ):

                # set up query instance to look for articles with
                #    ID in the list of values passed in.  Not
                #    quoting, since django should do that.
                current_query = Q( section__in = section_list_IN )

                # add it to list of queries
                query_list.append( current_query )

            #-- END processing of section names --#

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
        my_logger = None
        coder_type_IN = ""
        is_coder_rate_limited = False

        # get logger
        my_logger = self.get_logger()

        # get output type.
        coder_type_IN = self.get_param_as_str( self.PARAM_CODER_TYPE, self.ARTICLE_CODING_IMPL_DEFAULT )
        
        my_logger.debug( "Coder Type: " + coder_type_IN )
        
        # make instance for coder type.
        if ( coder_type_IN == self.ARTICLE_CODING_IMPL_OPEN_CALAIS_API ):
        
            # Open Calais API.
            coder_instance_OUT = OpenCalaisArticleCoder()
        
        else:
        
            # no output type, or unknown.  Make simple output matrix.
            coder_instance_OUT = OpenCalaisArticleCoder()
        
        #-- END check to see what type we have. --#
        
        # set up rate limiting
        is_coder_rate_limited = coder_instance_OUT.do_manage_time
        if ( is_coder_rate_limited == True ):
        
            # yes.  initialize variables.
            self.do_manage_time = True
            self.rate_limit_in_seconds = coder_instance_OUT.rate_limit_in_seconds
        
        else:
        
            # no.  initialize variables.
            self.do_manage_time = False
            self.rate_limit_in_seconds = -1
        
        #-- END check to see if rate-limited. --#
        
        return coder_instance_OUT

    #-- END get_coder_instance() --#


    def get_exception_helper( self ):

        '''
        Returns this instance's ExceptionHelper instance.  If no value, returns None.
        '''
        
        # return reference
        value_OUT = None

        # declare variables

        # get value.
        value_OUT = self.exception_helper
        
        # got anything?
        if ( ( value_OUT is None ) or ( value_OUT == "" ) ):
        
            # no - return None.
            value_OUT = None
            
        #-- END check to see if we have a value. --#

        return value_OUT

    #-- END get_exception_helper() --#


    def set_exception_helper( self, value_IN ):

        '''
        Accepts an ExceptionHelper instance, stores value passed in, returns the
           value.
        '''
        
        # return reference
        value_OUT = None

        # declare variables

        # store value.
        self.exception_helper = value_IN
        
        # get return value
        value_OUT = self.get_exception_helper()

        return value_OUT

    #-- END set_exception_helper() --#


#-- END class ArticleCoding --#