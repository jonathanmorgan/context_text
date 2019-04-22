from __future__ import unicode_literals

'''
Copyright 2010-2014 Jonathan Morgan

This file is part of http://github.com/jonathanmorgan/context_text.

context_text is free software: you can redistribute it and/or modify it under the terms of the GNU Lesser General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.

context_text is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.

You should have received a copy of the GNU Lesser General Public License along with http://github.com/jonathanmorgan/context_text. If not, see http://www.gnu.org/licenses/.

How to add a new ArticleCoder implementation:
- make a class that extends context_text.article_coding.article_coder.ArticleCoder.
- add an import of that class to the imports section of this file, in the
   section commented as "# Import other Article coder classes".
- Add a the coder to the article coder implementation choices below (preceded
   by the comment "# Article coding implementation choices.").  This will
   include adding a variable named "ARTICLE_CODING_IMPL_<name_of_coder>" and in
   that variable, storing a string name that describes the coder that is unique
   among the ARTICLE_CODING_IMPL_* variable contents, and then adding that
   variable to the list in variable ARTICLE_CODING_IMPL_CHOICES_LIST.  If your
   new coder should become the default, you should also set
   ARTICLE_CODING_IMPL_DEFAULT to equal your new variable, as well.
- Add a conditional branch for your new coder to method get_coder_instance().
   In this branch, you'll check if the variable "coder_type_IN" equals the
   value in your ARTICLE_CODING_IMPL_<name_of_coder> variable, defined above.
   If so, you will set "coder_instance_OUT" to a new instance of your coder.
   Example:
   
          elif ( coder_type_IN == self.ARTICLE_CODING_IMPL_OPEN_CALAIS_API_V2 ):

            # Open Calais API v2.
            coder_instance_OUT = OpenCalaisV2ArticleCoder()
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
from python_utilities.rate_limited.basic_rate_limited import BasicRateLimited

# Import the classes for our context_text application
from context_text.models import Article
from context_text.models import Article_Data

# Import other Article coder classes
from context_text.article_coding.article_coder import ArticleCoder
from context_text.article_coding.open_calais_v1.open_calais_article_coder import OpenCalaisArticleCoder
from context_text.article_coding.open_calais_v2.open_calais_v2_article_coder import OpenCalaisV2ArticleCoder

# Import context_text shared classes.
from context_text.shared.context_text_base import ContextTextBase


#===============================================================================
# classes (in alphabetical order by name)
#===============================================================================

class ArticleCoding( ContextTextBase ):


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
        ContextTextBase.PARAM_START_DATE : ParamContainer.PARAM_TYPE_STRING,
        ContextTextBase.PARAM_END_DATE : ParamContainer.PARAM_TYPE_STRING,
        ContextTextBase.PARAM_DATE_RANGE : ParamContainer.PARAM_TYPE_STRING,
        ContextTextBase.PARAM_PUBLICATION_LIST : ParamContainer.PARAM_TYPE_LIST,
        ContextTextBase.PARAM_TAG_LIST : ParamContainer.PARAM_TYPE_LIST,
        ContextTextBase.PARAM_SECTION_LIST : ParamContainer.PARAM_TYPE_LIST,
        ContextTextBase.PARAM_UNIQUE_ID_LIST : ParamContainer.PARAM_TYPE_STRING,
        ContextTextBase.PARAM_ARTICLE_ID_LIST : ParamContainer.PARAM_TYPE_STRING,
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
    ARTICLE_CODING_IMPL_OPEN_CALAIS_API_V1 = ARTICLE_CODING_IMPL_OPEN_CALAIS_API
    ARTICLE_CODING_IMPL_OPEN_CALAIS_API_V2 = "open_calais_api_v2"
    ARTICLE_CODING_IMPL_CHOICES_LIST = [ ARTICLE_CODING_IMPL_OPEN_CALAIS_API_V1, ARTICLE_CODING_IMPL_OPEN_CALAIS_API_V2 ]
    ARTICLE_CODING_IMPL_DEFAULT = ARTICLE_CODING_IMPL_OPEN_CALAIS_API_V2


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
        
        # ==> moved to parent class ContextTextBase
        #self.request = None
        #self.parameters = ParamContainer()
        # define parameters
        #self.define_parameters( ArticleCoding.PARAM_NAME_TO_TYPE_MAP )
        
        # set logger name (for LoggingHelper parent class: (LoggingHelper --> BasicRateLimited --> ContextTextBase --> ArticleCoding).
        self.set_logger_name( "context_text.article_coding.article_coding" )
        
        # flag to tell whether we want a single line per article printed.
        #     Defaults to False.
        self.do_print_updates = False
        
        # tracking of success and errors.
        self.success_article_id_list = []
        self.error_article_id_to_status_map = {}
        self.last_article_coder = None
        
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
        me = "code_article_data"
        logging_message = ""
        my_logger = None
        do_i_print_updates = False
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
        error_counter = -1
        
        # grab a logger.
        my_logger = self.get_logger()
        
        # do I print some status?
        do_i_print_updates = self.do_print_updates
        
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
            error_counter = 0
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
                    logging_message = "\n\n============================================================\n==> article " + str( article_counter ) + ": " + str( current_article.id ) + " - " + current_article.headline
                    my_logger.info( logging_message )
                    
                    # print?
                    if ( do_i_print_updates == True ):
                    
                        print( logging_message )
                        
                    #-- END check to see if we print a message.
                    
                    # add per-article exception handling, so we can get an idea of how
                    #    many articles cause problems.
                    try:
                
                        # code the article.
                        current_status = article_coder.code_article( current_article )
                        
                        # record status
                        self.record_article_status( current_article.id, current_status )
                        
                        # success?
                        if ( current_status != ArticleCoder.STATUS_SUCCESS ):
                        
                            # nope.  Error.
                            error_counter += 1
                            
                            logging_message = "======> In " + me + "(): ERROR - " + current_status + "; article = " + str( current_article )
                            my_logger.debug( logging_message )
                            
                            # print?
                            if ( do_i_print_updates == True ):
                            
                                print( logging_message )
                                
                            #-- END check to see if we print a message.
                            
                        #-- END check to see if success --#
                        
                    except Exception as e:
                        
                        # increment exception_counter
                        exception_counter += 1
                        
                        # get exception helper.
                        my_exception_helper = self.get_exception_helper()
                        
                        # log exception, no email or anything.
                        exception_message = "Exception caught for article " + str( current_article.id )
                        my_exception_helper.process_exception( e, exception_message )
                        
                        logging_message = "======> " + exception_message + " - " + str( e )
                        my_logger.debug( logging_message )
                        
                        # print?
                        if ( do_i_print_updates == True ):
                        
                            print( logging_message )
                            
                        #-- END check to see if we print a message.
                        
                        # record status
                        self.record_article_status( current_article.id, logging_message )

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

        my_summary_helper.set_prop_value( "error_counter", error_counter )
        my_summary_helper.set_prop_desc( "error_counter", "Error count" )

        my_summary_helper.set_prop_value( "exception_counter", exception_counter )
        my_summary_helper.set_prop_desc( "exception_counter", "Exception count" )

        # output - set prefix if you want.
        summary_string += my_summary_helper.create_summary_string( item_prefix_IN = "==> " )
        my_logger.info( summary_string )
        
        # output summary string as status.
        status_OUT += summary_string

        return status_OUT

    #-- END code_article_data() --#


    def create_article_query_set( self, param_prefix_IN = '' ):

        # return reference
        query_set_OUT = None

        # declare variables
        me = "create_article_query_set"
        my_logger = None
        params_IN = None
        start_date_IN = ''
        end_date_IN = ''
        date_range_IN = ''
        publication_list_IN = None
        tag_list_IN = None
        section_list_IN = None
        unique_id_list_IN = ''
        article_id_list_IN = ''
        filter_articles_params = {}
        
        # grab a logger.
        my_logger = self.get_logger()

        # get the request
        params_IN = self.get_param_container()

        # got a request?
        if ( params_IN ):

            # retrieve the incoming parameters
            start_date_IN = self.get_param_as_str( param_prefix_IN + ContextTextBase.PARAM_START_DATE, None )
            end_date_IN = self.get_param_as_str( param_prefix_IN + ContextTextBase.PARAM_END_DATE, None )
            date_range_IN = self.get_param_as_str( param_prefix_IN + ContextTextBase.PARAM_DATE_RANGE, None )
            publication_list_IN = self.get_param_as_list( param_prefix_IN + ContextTextBase.PARAM_PUBLICATION_LIST, [] )
            tag_list_IN = self.get_param_as_list( param_prefix_IN + ContextTextBase.PARAM_TAG_LIST, [] )
            unique_id_list_IN = self.get_param_as_list( param_prefix_IN + ContextTextBase.PARAM_UNIQUE_ID_LIST, [] )
            article_id_list_IN = self.get_param_as_list( param_prefix_IN + ContextTextBase.PARAM_ARTICLE_ID_LIST, [] )
            section_list_IN = self.get_param_as_list( param_prefix_IN + ContextTextBase.PARAM_SECTION_LIST, [] )
            
            my_logger.info( "In " + me + ": unique_id_list_IN = " + str( unique_id_list_IN ) )            
            
            # get all articles to start
            query_set_OUT = Article.objects.all()
            
            # set up dictionary for call to Article.filter_articles()
            filter_articles_params = {}
            filter_articles_params[ Article.PARAM_START_DATE ] = start_date_IN
            filter_articles_params[ Article.PARAM_END_DATE ] = end_date_IN
            filter_articles_params[ Article.PARAM_DATE_RANGE ] = date_range_IN
            filter_articles_params[ Article.PARAM_NEWSPAPER_ID_IN_LIST ] = publication_list_IN
            filter_articles_params[ Article.PARAM_TAGS_IN_LIST ] = tag_list_IN
            filter_articles_params[ Article.PARAM_UNIQUE_ID_IN_LIST ] = unique_id_list_IN
            filter_articles_params[ Article.PARAM_ARTICLE_ID_IN_LIST ] = article_id_list_IN
            filter_articles_params[ Article.PARAM_SECTION_NAME_IN_LIST ] = section_list_IN
            
            my_logger.info( "In " + me + ": filter_articles_params = " + str( filter_articles_params ) )
            
            # call Article.filter_articles()
            query_set_OUT = Article.filter_articles( qs_IN = query_set_OUT, params_IN = filter_articles_params )
            
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
        
        elif ( coder_type_IN == self.ARTICLE_CODING_IMPL_OPEN_CALAIS_API_V2 ):

            # Open Calais API v2.
            coder_instance_OUT = OpenCalaisV2ArticleCoder()
        
        else:
        
            # no coder type, or unknown.  Use default.
            coder_instance_OUT = OpenCalaisV2ArticleCoder()
        
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
        
        # store in instance variable
        self.last_article_coder = coder_instance_OUT
        
        return coder_instance_OUT

    #-- END get_coder_instance() --#


    def get_error_count( self ):
        
        '''
        Returns count of things in self.error_article_id_to_status_map.
        '''
        
        # return reference
        value_OUT = False
        
        # declare variables
        error_map = None
        error_count = -1
        
        # get error map
        error_map = self.get_error_dictionary()
        
        # get error count
        error_count = len( error_map )
        
        return error_count
        
    #-- END method get_error_count() --#
    

    def get_error_dictionary( self ):
        
        '''
        Returns self.error_article_id_to_status_map.
        '''
        
        # return reference
        value_OUT = False
        
        # declare variables
        error_map = None
        
        # get error map
        error_map = self.error_article_id_to_status_map
        
        if ( error_map is None ):
        
            self.error_article_id_to_status_map = {}
            error_map = self.get_error_dictionary()
        
        #-- END check to see if error dictionary populated. --#
        
        value_OUT = error_map
        
        return value_OUT
        
    #-- END method get_error_dictionary() --#
    

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


    def get_success_count( self ):
        
        '''
        Returns count of articles successfully coded (count of article IDs in
            self.success_article_id_list).
        '''
        
        # return reference
        value_OUT = False
        
        # declare variables
        success_list = None
        success_count = -1
        
        # get success list
        success_list = self.get_success_list()
        
        # get success count
        success_count = len( success_list )
        
        value_OUT = success_count
        
        return value_OUT
        
    #-- END method get_success_count() --#
    

    def get_success_list( self ):
        
        '''
        Returns self.success_article_id_list.
        '''
        
        # return reference
        value_OUT = False
        
        # declare variables
        success_list = None
        
        # get success list
        success_list = self.success_article_id_list
        
        # got a value?
        if ( success_list is None ):
        
            # no - create a list, store it, then call again to retrieve it.
            self.success_article_id_list = []
            success_list = self.get_success_list()
        
        #-- END check to see if success list populated. --#
        
        value_OUT = success_list
        
        return value_OUT
        
    #-- END method get_success_list() --#
    

    def has_errors( self ):
        
        '''
        Returns True if self.error_article_id_to_status_map is not empty, False
            if empty.
        '''
        
        # return reference
        has_errors_OUT = False
        
        # declare variables
        error_count = -1
        
        # get error count
        error_count = self.get_error_count()
        
        # got errors?
        if ( error_count > 0 ):
        
            # yes.
            has_errors_OUT = True
        
        else:
        
            # no
            has_errors_OUT = False
        
        #-- END check to see if errors. --#
        
        return has_errors_OUT
        
    #-- END method has_errors() --#
    

    def record_article_status( self, article_id_IN, status_IN ):
    
        '''
        Accepts article ID and status resulting from call to
            ArticleCoder.code_article().  IF status is success, adds to list of
            articles successfully processed.  If not, adds to error structure
            that maps article IDs to a list of the error statuses for each
            article (in case a given article is run more than once).
            
        Returns status, either STATUS_SUCCESS if everything went OK, or status
            message with error description if not.
        '''
        
        # return reference
        status_OUT = self.STATUS_SUCCESS
        
        # declare variables.
        me = "record_article_status"
        my_logger = None
        success_list = None
        error_map = None
        article_status_list = None
        
        # get logger instance
        my_logger = self.get_logger()
        
        # check if there is an article ID and status.
        if ( ( article_id_IN is not None )
            and ( isinstance( article_id_IN, int ) == True )
            and ( article_id_IN > 0 ) ):
            
            # check to see if status passed in.
            if ( ( status_IN is not None )
                and ( status_IN != "" ) ):
                
                my_logger.debug( "In " + me + "(): status passed in: " + status_IN )
            
                # retrieve success list and error map.
                success_list = self.success_article_id_list
                error_map = self.error_article_id_to_status_map
            
                # got a status.  Success?
                if ( status_IN == self.STATUS_SUCCESS ):
                
                    my_logger.debug( "====> In " + me + "(): SUCCESS!" )
            
                    # success.  Add to success list.
                    success_list.append( article_id_IN )
                
                else:
                
                    my_logger.debug( "====> In " + me + "(): ERROR!" )

                    # not success.  See if article already in error map.
                    if ( article_id_IN in error_map ):
                    
                        # already there.  Get list for article ID.
                        article_status_list = error_map.get( article_id_IN, [] )
                        
                        # append the status to that list.
                        article_status_list.append( status_IN )
                        
                        # put it back in the spot for the article ID, out of an
                        #     overabundance of caution.
                        error_map[ article_id_IN ] = article_status_list
                    
                    else:
                    
                        # it is not.  Add it.
                        article_status_list = []
                        article_status_list.append( status_IN )
                        error_map[ article_id_IN ] = article_status_list
                    
                    #-- END check to see if article is already in error map --#
                
                #-- END check to see if success. --#
            
            else:
            
                # no status passed in.  No way of knowing success or failure.
                status_OUT = self.STATUS_ERROR_PREFIX + "No status passed in.  Can't record article status without a status."
            
            #-- END check to see if status passed in.
            
        else:
        
            # no article ID passed in.  Can't do anything.
            status_OUT = self.STATUS_ERROR_PREFIX + "No article ID passed in.  Can't record article status without an article."
        
        #-- END check to see if article ID. --#
        
        return status_OUT
            
    #-- END method record_article_status() --#        
    
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