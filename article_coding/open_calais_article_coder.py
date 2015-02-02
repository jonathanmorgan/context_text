from __future__ import unicode_literals

'''
Copyright 2010-2014 Jonathan Morgan

This file is part of http://github.com/jonathanmorgan/sourcenet.

sourcenet is free software: you can redistribute it and/or modify it under the terms of the GNU Lesser General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.

sourcenet is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.

You should have received a copy of the GNU Lesser General Public License along with http://github.com/jonathanmorgan/sourcenet. If not, see http://www.gnu.org/licenses/.
'''

'''
This code file contains a class that implements functions for interacting with
   the online database of Newsbank.  It mostly includes methods for building and
   connecting to URLs that represent issues of newspapers and articles within an
   issue, and then Beautiful Soup code for interacting with the HTML contents of
   those pages once they are retrieved.  The actual work of retrieving pages is
   outside the scope of this class.
'''

#================================================================================
# Imports
#================================================================================


# python standard libraries
import json

# python utilities
from python_utilities.django_utils.django_string_helper import DjangoStringHelper
from python_utilities.network.http_helper import Http_Helper

# parent abstract class.
from sourcenet.article_coding.article_coder import ArticleCoder


#================================================================================
# Package constants-ish
#================================================================================


#================================================================================
# OpenCalaisArticleCoder class
#================================================================================

# define OpenCalaisArticleCoder class.
class OpenCalaisArticleCoder( ArticleCoder ):

    '''
    This class is a helper for Collecting articles out of NewsBank.  It implements
       functions for interacting with the online database of Newsbank.  It mostly
       includes methods for building and connecting to URLs that represent issues
       of newspapers and articles within an issue, and then Beautiful Soup code
       for interacting with the HTML contents of those pages once they are
       retrieved.  The actual work of retrieving pages is outside the scope of
       this class.
    Preconditions: It depends on cookielib, datetime, os, re, sys, urllib2 and
       BeautifulSoup 3.
    '''

    #============================================================================
    # Constants-ish
    #============================================================================
    

    # status constants - in parent (ArticleCoder) now:
    # STATUS_SUCCESS = "Success!"
    # STATUS_ERROR_PREFIX = "Error: "
    
    # config application
    CONFIG_APPLICATION = "OpenCalais_REST_API"
    
    # config property names.
    CONFIG_PROP_OPEN_CALAIS_API_KEY = "open_calais_api_key"
    CONFIG_PROP_SUBMITTER = "submitter"
    
    # HTTP header names
    HTTP_HEADER_NAME_X_CALAIS_LICENSE_ID = "x-calais-licenseID"
    HTTP_HEADER_NAME_CONTENT_TYPE = "Content-Type"
    HTTP_HEADER_NAME_OUTPUT_FORMAT = "outputformat"
    HTTP_HEADER_NAME_SUBMITTER = "submitter"
    
    # content types
    CONTENT_TYPE_TEXT = "TEXT/RAW"
    CONTENT_TYPE_HTML = "TEXT/HTML"
    CONTENT_TYPE_DEFAULT = CONTENT_TYPE_TEXT
    
    # output formats
    OUTPUT_FORMAT_JSON = "Application/JSON"
    OUTPUT_FORMAT_DEFAULT = OUTPUT_FORMAT_JSON
    
    # Open Calais API URL
    OPEN_CALAIS_REST_API_URL = "http://api.opencalais.com/tag/rs/enrich"
    

    #============================================================================
    # Instance variables
    #============================================================================

    
    # declare variables
    http_helper = None
    content_type = ""
    output_format = ""


    #============================================================================
    # Instance methods
    #============================================================================


    def __init__( self ):

        # call parent's __init__() - I think...
        super( OpenCalaisArticleCoder, self ).__init__()
        
        # declare variables
        
        # initialize variables
        self.http_helper = None
        self.content_type = ""
        self.output_format = ""
        
        # rate-limiting
        self.do_manage_time = True
        self.rate_limit_in_seconds = 0.25
        self.rate_limit_daily_limit = 10000
    
        # set application string (for LoggingHelper parent class: (LoggingHelper -->
        #    BasicRateLimited --> ArticleCoder --> OpenCalaisArticleCoder).
        self.set_logger_name( "sourcenet.article_coding.open_calais_article_coder" )

    #-- END method __init__() --#


    def process_article( self, article_IN, coding_user_IN = None, *args, **kwargs ):

        '''
        purpose: After the ArticleCoder is initialized, this method accepts one
           article instance and codes it for sourcing.  In regards to articles,
           this class is stateless, so you can process many articles with a
           single instance of this object without having to reconfigure each
           time.
        preconditions: load_config_properties() should have been invoked before
           running this method.
        postconditions: article passed in is coded, which means an Article_Data
           instance is created for it and populated to the extent the child
           class is capable of coding the article.
        '''

        # return reference
        status_OUT = self.STATUS_SUCCESS
        
        # declare variables
        me = "classmethod process_articles"
        my_logger = None
        my_exception_helper = None
        exception_message = ""
        debug_string = ""
        process_all_IN = False
        process_authors_IN = False
        automated_coding_user = None
        article_text = None
        article_body_html = ""
        request_data = ""
        my_http_helper = None
        my_content_type = ""
        requests_response = None
        requests_raw_text = ""
        requests_response_json = None
        is_response_OK = True
        article_data = None
        my_author_string = ""
        latest_status = ""
        do_save_article = True
        do_save_data = False
        
        # get logger
        my_logger = self.get_logger()
        
        # get exception_helper
        my_exception_helper = self.get_exception_helper()
        
        # parse params
        process_all_IN = self.get_config_property( self.PARAM_AUTOPROC_ALL, True )
        
        # if not process all, do we process any?
        if ( process_all_IN == False ):

            # how about authors?
            process_authors_IN = self.get_config_property( self.PARAM_AUTOPROC_AUTHORS, True )
            
        #-- END check to see if we set processing flags by item --#
        
        my_logger.debug( "Input flags: process_all = \"" + str( process_all_IN ) + "\"; process_authors = \"" + str( process_authors_IN ) + "\"" )
        
        # get automated_coding_user
        automated_coding_user = coding_user_IN
        
        # got a user?
        if ( automated_coding_user is not None ):

            # got an article?
            if ( article_IN is not None ):
    
                # get Article_Data instance for user and coder_type.  Grab it
                #    first so we can store error information in it if problem
                #    on OpenCalais side.
                article_data = article_IN.get_article_data_for_coder( automated_coding_user, self.CONFIG_APPLICATION )
                
                # got article data?
                if ( article_data is not None ):
                
                    # then, get text.
                    article_text = article_IN.article_text_set.get()
                    
                    # retrieve article body with HTML
                    article_body_html = article_text.get_content()
                    
                    # AND get without HTML - OpenCalais API does not deal well
                    #    with HTML - just pass plain text.
                    article_body_text = article_text.get_content_sans_html()
                    
                    # store whatever we are passing in the request_data variable.
                    request_data = article_body_text
                    
                    if ( self.DEBUG_FLAG == True ):
                    
                        my_logger.debug( "In " + me + ": Article " + str( article_IN.id ) + " - " + article_IN.headline )
                        my_logger.debug( "In " + me + ": current article body:" )
                        my_logger.debug( request_data )
                    
                    #-- END debug --#
                    
                    # encode the data, so (hopefully) HTTPHelper doesn't have to.
                    #request_data = DjangoStringHelper.encode_string( request_data, DjangoStringHelper.ENCODING_UTF8 )
                    # - moved this into load_url_requests().
                    
                    # get Http_Helper instance
                    my_http_helper = self.get_http_helper()
                    
                    # what is the content type?
                    my_content_type = my_http_helper.get_http_header( self.HTTP_HEADER_NAME_CONTENT_TYPE )
                    
                    if ( self.DEBUG_FLAG == True ):
                    
                        my_logger.debug( "In " + me + ": content type = " + my_content_type )
                        
                    #-- END debug --#
                    
                    # make the request.
                    requests_response = my_http_helper.load_url_requests( self.OPEN_CALAIS_REST_API_URL, request_type_IN = Http_Helper.REQUEST_TYPE_POST, data_IN = request_data )
                    
                    # raw text:
                    requests_raw_text = requests_response.text
                    
                    # convert to a json object, inside try since sometimes OpenCalais
                    #    returns non-parsable stuff.
                    try:
                    
                        # convert to JSON object
                        requests_response_json = requests_response.json()
                        is_response_OK = True
                        
                    except ValueError as ve:
                    
                        # problem parsing JSON - log body of article, response,
                        #    and exception.
                        exception_message = "ValueError parsing OpenCalais JSON."
                        my_logger.debug( "\n ! " + exception_message )
                        my_logger.debug( "\n ! article text:\n" + request_data )
                        my_logger.debug( "\n ! response text:\n" + requests_raw_text )
                        my_exception_helper.process_exception( ve, exception_message )
                        
                        # set status on article data to service_error
                        article_data.status = Article_Data.STATUS_SERVICE_ERROR
                        
                        # let rest of program know it is not OK to proceed.
                        is_response_OK = False
                    
                    except Exception as e:
                    
                        # unknown problem parsing JSON - log body of article,
                        #    response, and exception.
                        exception_message = "Exception parsing OpenCalais JSON."
                        my_logger.debug( "\n ! " + exception_message )
                        my_logger.debug( "\n ! article text:\n" + request_data )
                        my_logger.debug( "\n ! response text:\n" + requests_raw_text )
                        my_exception_helper.process_exception( e, exception_message )
                        
                        # set status on article data to service_error
                        article_data.status = Article_Data.STATUS_SERVICE_ERROR
                        
                        # let rest of program know it is not OK to proceed.
                        is_response_OK = False
                    
                    #-- END try/except around JSON processing. --#
                    
                    # render some of it as a string, for debug.
                    if ( self.DEBUG_FLAG == True ):
                    
                        # render and output debug string.
                        debug_string = self.print_calais_json( requests_response_json )
                        self.output_debug( debug_string )
        
                    #-- END debug --#
        
                    # all parsed - OK to continue?
                    if ( is_response_OK == True ):
        
                        # process contents of response.
                    
                        # Process authors?
                        if ( ( process_all_IN == True ) or ( process_authors_IN == True ) ):
                        
                            # process authors.  Get author string
                            my_author_string = article_IN.author_string
                            
                            my_logger.info( "Article author string: " + my_author_string )
                            
                            # process author string.
                            latest_status = self.process_author_string( article_data, my_author_string )
                            
                            do_save_data = True
                            
                            my_logger.debug( "After calling process_author_string() - " + latest_status )
                            
                        #-- End check to see if we process authors --#
                        
                        # call the process_json_api_response() method to parse
                        #    the request JSON, find all quotations, people they
                        #    are tied to, then make attribution relations.
                        latest_status = self.process_json_api_response( article_IN, article_data, requests_response_json )
                        
                    #-- END check to see if OK to process information returned from OpenCalais. --#
                        
                    # regardless, Save Article_Data instance if flag indicates
                    #    we are to save.
                    if ( do_save_data == True ):
                        
                        article_data.save()
                        
                    #-- END check to see if we save article data --#
                    
                    # not saving article at this point - shouldn't be changing anything there.
                    # save the article, as well?
                    #if ( do_save_article == True ):
                        
                        # We do also save the article itself.
                    #    article_IN.save()
                        
                    #-- END check to see if we save article. --#

                else:
                
                    status_OUT = self.STATUS_ERROR_PREFIX + "Could not retrieve Article_Data instance.  Very odd.  Might mean we have multiple data records for coder \"" + automated_coding_user + "\" and coder_type \"" + self.CONFIG_APPLICATION + "\""
                    
                #-- END check to see if we found article data into which we'll code.
    
            #-- END check to see if article. --#
            
        else:
        
            status_OUT = self.STATUS_ERROR_PREFIX + "Could not find user with name \"automated\".  Can't code articles without a user."
            
        #-- END check to make sure we have an automated coding user. --#
        
        return status_OUT

    #-- END method process_article() --#
    

    def get_content_type( self ):

        '''
        Retrieves content type of content to be passed to OpenCalais.
        '''
        
        # return reference
        value_OUT = None

        # get Http_Helper instance.
        value_OUT = self.content_type
        
        # got anything?
        if ( ( value_OUT is None ) or ( value_OUT == "" ) ):
        
            # no - return default.
            value_OUT = self.CONTENT_TYPE_DEFAULT
        
        #-- END check to see if value --#

        return value_OUT

    #-- END get_content_type() --#


    def get_http_helper( self ):

        '''
        Retrieves Http_Helper instance.
        '''
        
        # return reference
        instance_OUT = None

        # get Http_Helper instance.
        instance_OUT = self.http_helper

        return instance_OUT

    #-- END get_http_helper() --#


    def get_output_format( self ):

        '''
        Retrieves output format for OpenCalais request.
        '''
        
        # return reference
        value_OUT = None

        # get Http_Helper instance.
        value_OUT = self.output_format
        
        # got anything?
        if ( ( value_OUT is None ) or ( value_OUT == "" ) ):
        
            # no - return default.
            value_OUT = self.OUTPUT_FORMAT_DEFAULT
        
        #-- END check to see if value --#

        return value_OUT

    #-- END get_output_format() --#


    def init_config_properties( self, *args, **kwargs ):

        '''
        purpose: Called as part of the base __init__() method, so that loading
           config properties can also be included in the parent __init__()
           method.  The application for django_config and any properties that
           need to be loaded should be set here.  To set a property use
           add_config_property( name_IN ).  To set application, use
           set_config_application( app_name_IN ).
        preconditions: None.
        postconditions: This instance should be ready to have
           load_config_properties() called on it after this method is invoked.
        '''

        self.set_config_application( self.CONFIG_APPLICATION )
        self.add_config_property( self.CONFIG_PROP_OPEN_CALAIS_API_KEY )
        self.add_config_property( self.CONFIG_PROP_SUBMITTER )

    #-- END abstract method init_config_properties() --#
    

    def initialize_from_params( self, params_IN, *args, **kwargs ):

        '''
        purpose: Accepts a dictionary of run-time parameters, uses them to
           initialize this instance.
        preconditions: None.
        postconditions: None.
        '''

        # declare variables
        me = "initialize_from_params"
        my_http_helper = None
        my_open_calais_api_key = ""
        my_content_type = ""
        my_output_format = ""
        my_submitter = "sourcenet"
        
        # update config properties with params passed in.
        self.update_config_properties( params_IN )
        
        # create Http_Helper
        my_http_helper = Http_Helper()
        
        # retrieve API key.
        my_open_calais_api_key = self.get_config_property( self.CONFIG_PROP_OPEN_CALAIS_API_KEY )
        
        # content type
        my_content_type = self.get_content_type()

        # output format
        my_output_format = self.get_output_format()

        # retrieve submitter
        my_submitter = self.get_config_property( self.CONFIG_PROP_SUBMITTER, "sourcenet" )
        
        # set http headers
        my_http_helper.set_http_header( self.HTTP_HEADER_NAME_X_CALAIS_LICENSE_ID, my_open_calais_api_key )
        my_http_helper.set_http_header( self.HTTP_HEADER_NAME_CONTENT_TYPE, my_content_type )
        my_http_helper.set_http_header( self.HTTP_HEADER_NAME_OUTPUT_FORMAT, my_output_format )
        my_http_helper.set_http_header( self.HTTP_HEADER_NAME_SUBMITTER, my_submitter )
        
        # request type
        my_http_helper.request_type = Http_Helper.REQUEST_TYPE_POST
        
        # store the http_helper
        self.set_http_helper( my_http_helper )

    #-- END abstract method initialize_from_params() --#
    

    def print_calais_json( self, json_IN ):
    
        '''
        Accepts OpenCalais API JSON object, prints selected parts of it to a
           string variable.  Returns that string.
        '''
    
        # return reference
        string_OUT = ""
        
        # declare variables
        properties_to_output_list = []
        current_property = ""
        
        # set properties we want to output
        properties_to_output_list = [ "_type", "_typeGroup", "commonname", "name", "person" ]
        
        # loop over the stuff in the response:
        item_counter = 0
        current_container = json_IN
        for item in current_container.keys():
        
            item_counter += 1
            string_OUT += "==> " + str( item_counter ) + ": " + item + "\n"
            
            # loop over properties that we care about.
            for current_property in properties_to_output_list:
                        
                # is property in the current JSON item we are looking at?
                if ( current_property in current_container[ item ] ):

                    # yes - output.
                    current_property_value = current_container[ item ][ current_property ]
                    string_OUT += "----> " + current_property + ": " + current_property_value  + "\n"

                    # is it a Quotation or a Person?
                    if ( ( current_property_value == "Quotation" ) or ( current_property_value == "Person" ) ):

                        string_OUT += str( current_container[ item ] ) + "\n"

                    #-- END check to see if type is "Quotation" --#

                #-- END current_property --#

            #-- END loop over list of properties we want to output. --#
            
        #-- END loop over items --#
        
        return string_OUT
        
    #-- END function print_calais_json --#


    def process_json_api_response( self, article_IN, article_data_IN, json_response_IN ):
    
        '''
        Accepts Article, Article_Data instance of article we are processing, and
           the JSON response from passing that article's text to the OpenCalais
           API.  Parses response, finds all quotations and the people they are
           tied to.  Then, for each quotation:
           - look up the people who are quoted by name.
              - If ambiguity, make a new person, but also keep track of other
                 potential matches (will need to add this to the database).
              - will probably need to refine the person lookup, too.  Right now, 
           - add sources to Article_Data.
           - save the article data.
        '''
        
        # return reference
        status_OUT = self.STATUS_SUCCESS
        
        # declare variables
        me = "process_json_api_response"
        my_logger = None
        json_string = ""
        
        # get logger
        my_logger = self.get_logger()
        
        # first, remind myself what the JSON looks like.
        json_string = json.dumps( json_response_IN, sort_keys = True, indent = 4, separators = ( ',', ': ' ) )
        my_logger.debug( "In " + me + ": outputting whole JSON document:" )
        my_logger.debug( json_string )
        
        return status_OUT
    
    #-- END function process_json_response() --#


    def set_http_helper( self, instance_IN ):
        
        # return reference
        instance_OUT = ""
        
        # set instance
        self.http_helper = instance_IN
        
        # return instance
        instance_OUT = self.get_http_helper()
        
        return instance_OUT
        
    #-- END method set_http_helper() --#
    

#-- END class OpenCalaisArticleCoder --#