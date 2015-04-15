from __future__ import unicode_literals

'''
Copyright 2010-2015 Jonathan Morgan

This file is part of http://github.com/jonathanmorgan/sourcenet.

sourcenet is free software: you can redistribute it and/or modify it under the terms of the GNU Lesser General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.

sourcenet is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.

You should have received a copy of the GNU Lesser General Public License along with http://github.com/jonathanmorgan/sourcenet. If not, see http://www.gnu.org/licenses/.
'''

'''
This code file contains a class that implements functions for interacting with
   the Open Calais natural language processing API.  It includes methods for
   interacting with the Open Calais REST API and for processing the JSON response
   that the Open Calais REST API returns.
'''

#================================================================================
# Imports
#================================================================================


# python standard libraries
import json
import sys

# mess with python 3 support
import six

# python utilities
from python_utilities.django_utils.django_string_helper import DjangoStringHelper
from python_utilities.json.json_helper import JSONHelper
from python_utilities.network.http_helper import Http_Helper
from python_utilities.sequences.sequence_helper import SequenceHelper

# sourcenet classes

# models
from sourcenet.models import Article_Data
from sourcenet.models import Article_Data_Notes
from sourcenet.models import Article_Source
from sourcenet.models import Article_Source_Mention
from sourcenet.models import Article_Source_Quotation
from sourcenet.models import Article_Text
from sourcenet.models import Person

# parent abstract class.
from sourcenet.article_coding.article_coder import ArticleCoder

# class to help with parsing and processing OpenCalaisApiResponse.
from sourcenet.article_coding.open_calais_api_response import OpenCalaisApiResponse

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
    
    # variables to hold strings related to OpenCalais.
    OPEN_CALAIS_UUID_NAME = "OpenCalais API URI (URL)"
    

    #============================================================================
    # NOT Instance variables
    # Class variables - overriden by __init__() per instance if same names, but
    #    if not set there, shared!
    #============================================================================

    
    # declare variables
    #http_helper = None
    #content_type = ""
    #output_format = ""


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
        me = "process_article"
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
        my_json_note = None
        
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
                
                    self.output_debug( "\n\nIn " + me + ": Article_Data instance id = " + str( article_data.id ) )
                
                    # wrap in try/except to aim to catch unexpected exceptions,
                    #    so we can set a status in the Article_Data instance.
                    try:
                
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
                            debug_string = OpenCalaisApiResponse.print_calais_json( requests_response_json )
                            self.output_debug( debug_string )
            
                        #-- END debug --#
            
                        self.output_debug( "In " + me + ": after parsing JSON, before processing it." )
            
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

                            # if we make it here, we're done processing.
                            #    Complete!                            
                            article_data.status = Article_Data.STATUS_COMPLETE

                        #-- END check to see if OK to process information returned from OpenCalais. --#
                            
                        # regardless, Save Article_Data instance if flag indicates
                        #    we are to save.
                        if ( do_save_data == True ):
                            
                            article_data.save()
                            
                            # store the JSON in an Article_Data_Note.
                            my_json_note = Article_Data_Notes()
                            
                            # set values
                            my_json_note.article_data = article_data
                            my_json_note.content_type = Article_Data_Notes.CONTENT_TYPE_JSON
                            my_json_note.content = JSONHelper.pretty_print_json( requests_response_json )
                            #my_json_note.status = ""
                            my_json_note.source = self.CONFIG_APPLICATION
                            my_json_note.content_description = "OpenCalais REST API response JSON"
                            
                            # save note.
                            my_json_note.save()
    
                        #-- END check to see if we save article data --#
                        
                        # not saving article at this point - shouldn't be changing anything there.
                        # save the article, as well?
                        #if ( do_save_article == True ):
                            
                            # We do also save the article itself.
                        #    article_IN.save()
                            
                        #-- END check to see if we save article. --#

                    except Exception as e:
                    
                        # set status on article data to unknown_error and save().
                        exception_message = "In OpenCalaisArticleCoder." + me + "(): Unknown exception caught while processing article.  Exception: " + str( e )
                        article_data.set_status( Article_Data.STATUS_UNKNOWN_ERROR, exception_message )
                        article_data.save()
                        
                        # unknown problem processing article
                        my_logger.debug( "\n ! " + exception_message )
                        my_logger.debug( "\n ! Article_Data:\n" + str( article_data ) )
                        my_exception_helper.process_exception( e, exception_message )
                        
                        # return status.  Article_Data is already saved.  Might
                        #    as well let this end gracefully.
                        status_OUT = self.STATUS_ERROR_PREFIX + exception_message
                        
                        # OR, re-raise excpetion:
                        # exception_type, exception_value, exception_traceback = sys.exc_info()
                        # raise exception_type, exception_value, exception_traceback
                    
                    #-- END try/except around all article processing after retrieving article_data. --#
                        
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
        my_reponse_helper = None
        my_capture_method = ""
        
        # quote processing variables.
        quotation_dict = None
        quote_count = -1
        current_oc_URI = None
        current_quotation_json = None
        quote_counter = -1
        quote_person_URI = ""
        quote_person = None
        person_to_quotes_map = {}
        person_quote_dict = {}
        
        # person processing variables.
        person_counter = -1
        person_URI = ""
        person_json = None
        person_name = ""
        person_details_dict = {}
        source_person = None
        article_source_qs = None
        article_source_count = -1
        person_paper = None
        
        # mention processing variables.
        mention_list = []
        mention_counter = -1
        current_mention = None
        
        # quotation processing variables.
        uri_to_quotation_dictionary = {}
        person_quote_list = None
        quote_counter = -1
        current_quotation_URI = ""
        quotation_JSON = None
        quotation_qs = None
        current_quotation = None
        status_string = ""

        # get logger
        my_logger = self.get_logger()
        
        # initialize variables from article_data_IN
        my_capture_method = article_data_IN.coder_type
        
        # get response helper.
        my_response_helper = OpenCalaisApiResponse()
        
        #temp_dict_1 = my_response_helper.type_group_to_items_dict
        #my_logger.debug( "In " + me + ": type_group_to_items_dict = " + str( temp_dict_1 ) )
        #temp_dict_2 = my_response_helper.type_to_items_dict
        #my_logger.debug( "In " + me + ": type_to_items_dict = " + str( temp_dict_2 ) )
        
        # chuck the response in there.
        my_response_helper.set_json_response_object( json_response_IN )
        
        # once we get response JSON sorted out, then use it to interact.
        
        # get all the quotations.
        quotation_dict = my_response_helper.get_items_of_type( OpenCalaisApiResponse.OC_ITEM_TYPE_QUOTATION )

        # make sure it isn't None
        if ( quotation_dict is not None ):

            quote_count = len( quotation_dict )
            my_logger.debug( "In " + me + ": quote count = " + str( quote_count ) )
            
            # make sure we have one or more quotes
            if ( quote_count > 0 ):
            
                # loop over them
                quote_counter = 0
                for current_oc_URI, current_quotation_json in six.iteritems( quotation_dict ):
                
                    # increment counter
                    quote_counter = quote_counter + 1
                    
                    # log the URI
                    my_logger.debug( "In " + me + ": quote #" + str( quote_counter ) + " = " + current_oc_URI )
                    
                    # get the URI of the person who was quoted.
                    quote_person_URI = JSONHelper.get_json_object_property( current_quotation_json, OpenCalaisApiResponse.JSON_NAME_QUOTE_PERSON_URI )
                    
                    # is person already in person-to-quote map?
                    if quote_person_URI in person_to_quotes_map:
                    
                        # yes - get quote dictionary...
                        person_quote_dict = person_to_quotes_map[ quote_person_URI ]
        
                        # then add current quote to dictionary.
                        person_quote_dict[ current_oc_URI ] = current_quotation_json
                    
                    else:
                    
                        # person not in map.  Make dict of quotes...
                        person_quote_dict = {}
        
                        # add current quote...
                        person_quote_dict[ current_oc_URI ] = current_quotation_json
        
                        # then associate quotes with person URI.
                        person_to_quotes_map[ quote_person_URI ] = person_quote_dict
                    
                    #-- END check to see if person in person-to-quotes map. --#
                    
                #-- END loop over quotation items --#
                
                my_logger.debug( "In " + me + ": done with quote loop, on to person loop, over person-to-quote map." )
                
                # now, look at people who were quoted.
                person_counter = 0
                for person_URI in person_to_quotes_map:
                
                    # increment counter
                    person_counter = person_counter + 1
                    
                    # try to get person from URI.
                    person_json = my_response_helper.get_item_from_response( person_URI )
                    person_json_string = JSONHelper.pretty_print_json( person_json )
                    
                    self.output_debug( "+++++ Person JSON for URI: \"" + person_URI + "\"\n\n\n" + person_json_string )
                    
                    # Do we have JSON for this URI?
                    if ( ( person_json is not None ) and ( person_json_string.strip() != "null" ) ):
                    
                        # get and output name.
                        person_name = JSONHelper.get_json_object_property( person_json, OpenCalaisApiResponse.JSON_NAME_PERSON_NAME )
                        
                        my_logger.debug( "In " + me + ": person #" + str( person_counter ) + " = " + person_name )
                        
                        # try looking up source just like we look up authors.
            
                        # make empty article source to work with, for now.
                        article_source = Article_Source()
                        
                        # prepare person details.
                        person_details_dict = {}
                        person_details_dict[ self.PARAM_NEWSPAPER_INSTANCE ] = article_IN.newspaper
                        person_details_dict[ self.PARAM_EXTERNAL_UUID_NAME ] = self.OPEN_CALAIS_UUID_NAME
                        person_details_dict[ self.PARAM_EXTERNAL_UUID ] = person_URI
                        person_details_dict[ self.PARAM_EXTERNAL_UUID_SOURCE ] = self.config_application
                        person_details_dict[ self.PARAM_CAPTURE_METHOD ] = my_capture_method                        
            
                        # lookup person - returns person and confidence score inside
                        #    Article_Source instance.
                        article_source = self.lookup_person( article_source, 
                                                             person_name,
                                                             create_if_no_match_IN = True,
                                                             update_person_IN = True,
                                                             person_details_IN = person_details_dict )
                        source_person = article_source.person
                                    
                        # got a person?
                        if ( source_person is not None ):
            
                            # One Article_Source per person, and then have a new thing to
                            #    hold quotations that hangs off that.
                            # At any rate, make method to process person/quote that you pass:
                            # - source_person
                            # - article_data_IN
                            # - my_response_helper (including JSON, etc.)
                            # - quote JSON?  OR quotes list for person, from person_to_quotes_map...?
                            # - ...?
                            
                            # Now, we need to deal with Article_Source instance.  First, see
                            #    if there already is one for this name.  If so, do nothing.
                            #    If not, make one.
                            article_source_qs = article_data_IN.article_source_set.filter( person = source_person )
                            article_source_count = article_source_qs.count()
                            
                            # got anything?
                            if ( article_source_count == 0 ):
                                                         
                                # no - add - more stuff to set.  Need to see what we can get.
                                
                                # use the article_source created above.
                                #article_source = Article_Source()
                            
                                article_source.article_data = article_data_IN
                                article_source.person = source_person
                                
                                # confidence level set in lookup_person() method.
                                #article_source.match_confidence_level = 1.0
                
                                article_source.source_type = Article_Source.SOURCE_TYPE_INDIVIDUAL
                                article_source.title = ""
                                article_source.more_title = ""
                                article_source.organization = None # models.ForeignKey( Organization, blank = True, null = True )
                                #article_source.document = None
                                article_source.source_contact_type = Article_Source.SOURCE_CONTACT_TYPE_OTHER
                                #article_source.source_capacity = None
                                #article_source.localness = None
                                article_source.notes = ""
                
                                # field to store how source was captured.
                                article_source.capture_method = self.CONFIG_APPLICATION
                            
                                article_source.save()
                                
                                # !TODO - topics?
                                # if we want to set topics, first save article_source, then
                                #    we can parse them out of the JSON, make sure they exist
                                #    in topics table, then add relation.  Probably want to
                                #    make Person_Topic also.  So, if we do this, it will be
                                #    a separate method.
                                #article_source.topics = None # models.ManyToManyField( Topic, blank = True, null = True )
            
                                my_logger.debug( "In " + me + ": adding Article_Source instance for " + str( source_person ) + "." )
                
                            elif ( article_source_count == 1 ):
                            
                                my_logger.debug( "In " + me + ": Article_Source instance already exists for " + str( source_person ) + "." )
                                
                                # retrieve article source from query set.
                                article_source = article_source_qs.get()
                                
                                # !TODO - want to do any updates?
                                
                            else:
                            
                                # neither 0 or 1 sources - either invalid or multiple,
                                #    either is not right.
                                my_logger.debug( "In " + me + ": Article_Source count for " + str( source_person ) + " = " + str( article_source_count ) + ".  What to do?" )
                                                    
                            #-- END check if need new Article_Source instance --#
                            
                            # make sure we have an article_source
                            if ( ( article_source is not None ) and ( article_source.id ) ):
            
                                # !deal with mentions.
                                
                                # get list of mentions from Person's "instances"
                                mention_list = JSONHelper.get_json_object_property( person_json, OpenCalaisApiResponse.JSON_NAME_INSTANCES )
                
                                # loop
                                mention_counter = 0
                                for current_mention in mention_list:
                                
                                    # incremenet counter
                                    mention_counter = mention_counter + 1
                                
                                    self.output_debug( "Mention " + str( mention_counter ) )
                                    
                                    # call method to process mention.
                                    self.process_json_mention( article_IN, article_source, current_mention )
                
                                #-- END loop over mentions --#
                
                                # !deal with quotes.
                                # to start, loop over the quotes associated with the current
                                #    person and see what is in them.
                                
                                # get map of URIs to JSON for "Quotation" item type.
                                uri_to_quotation_dictionary = my_response_helper.get_items_of_type( OpenCalaisApiResponse.OC_ITEM_TYPE_QUOTATION )
                                
                                # get quote list for current person.
                                person_quote_list = person_to_quotes_map.get( person_URI, [] )
                                
                                # loop
                                quote_counter = 0
                                for current_quotation_URI in person_quote_list:
                
                                    # increment counter
                                    quote_counter = quote_counter + 1
                
                                    self.output_debug( "Quotation " + str( quote_counter ) + " URI: " + current_quotation_URI )
                                    
                                    # get JSON from URI_to_quotation_dictionary.
                                    quotation_JSON = uri_to_quotation_dictionary.get( current_quotation_URI, None )
                
                                    # got one?
                                    if ( quotation_JSON is not None ):
                
                                        self.process_json_quotation( article_IN, article_source, current_quotation_URI, quotation_JSON )
                                        
                                    #-- END check to see if Quotation JSON --#
                                    
                                #-- END loop over quotations --#
                                
                            #-- END check to make sure we have an Article_Source --#
            
                        else:
                        
                            my_logger.debug( "In " + me + ": ERROR - no matching person found - must have been a problem looking up name \"" + author_name + "\"" )
            
                        #-- END check to see if person found. --#
                        
                    else:
                    
                        # !TODO - need to set something on article_data_IN here, so we
                        #    can track when this odd error occurs - was a problem with
                        #    OpenCalais.
                        status_string = "In OpenCalaisArticleCoder." + me + ": ERROR - No Person JSON for URI: \"" + person_URI + "\".  When OpenCalais includes URIs that don't have matches in the JSON, that usually means an error occurred.  Probably should reprocess this article.  JSON contents: " + person_json_string.strip()
                        article_data_IN.set_status( Article_Data.STATUS_SERVICE_ERROR, status_string  )
                    
                        # log it.
                        my_logger.debug( status_string )
                        
                    #-- END check to see if JSON present for URI --#
                
                #-- END loop over persons --#
                
            else:
    
                my_logger.debug( "In OpenCalaisArticleCoder." + me + ": No quotations in article, so nothing else to do." )
    
            #-- END check to see if any quotes in article.  If not, no attribution. --#

        else:

            my_logger.debug( "In OpenCalaisArticleCoder." + me + ": No quotations in article (None returned), so nothing else to do." )

        #-- END check to see if any quotes in article.  If not, no attribution. --#

        return status_OUT
    
    #-- END function process_json_api_response() --#


    def process_json_mention( self, article_IN, article_source_IN, mention_JSON_IN ):
    
        '''
        Accepts Article, Article_Source, and JSON of a mention of the source.
           Retrieves data from JSON.  Looks for mention that has same length,
           offset, and value.  If present, does nothing.  If not, makes an
           Article_Source_Mention instance for the mention, populates it, saves
           it, then returns it.  If error, returns None.
           
        Preconditions:  Assumes all input variables will be populated
           appropriately.  If any are missing or set to None, will break,
           throwing exceptions.
           
        Postconditions:  If mention wasn't already stored, it will be after
           this call.
           
        Example JSON:
        {
            "detection": "[ Fiat (SpA) that we have and we need to examine,\" ]Fred Diaz[, head of the Ram brand, said in an interview]",
            "exact": "Fred Diaz",
            "length": 9,
            "offset": 382,
            "prefix": " Fiat (SpA) that we have and we need to examine,\" ",
            "suffix": ", head of the Ram brand, said in an interview"
        }

        '''
        
        # return reference
        instance_OUT = None
        
        # declare variables
        me = "process_json_mention"
        mention_qs = None
        mention_count = -1
        current_mention = None
        
        # declare variables - Information from OpenCalais JSON
        mention_instances_list = None
        mention_detection = ""
        mention_exact = ""
        mention_length = ""
        mention_offset = ""
        mention_prefix = ""
        mention_suffix = ""
        
        # declare variables - get values from article text.
        article_text = None
        find_string = ""
        mention_FIT_values = {}
        FIT_status_list = []
        FIT_status_count = -1
        canonical_index_list = []
        plain_text_index_list = []
        paragraph_list = []
        first_word_list = []
        last_word_list = []
        
        # declare variables - values we'll place in instance at the end.
        canonical_index = -1
        plain_text_index = -1
        paragraph_number = -1
        first_word_number = -1
        last_word_number = -1
        is_ok_to_update = False
        current_value = None
        notes_list = []
        notes_count = -1
        notes_string = ""
        found_list = []
        found_list_count = -1
        sanity_check_index = -1
        found_dict = {}
        mention_prefix_length = -1
        mention_prefix_word_list = []
        mention_prefix_word_count = -1
        
        # declare variables - troubleshooting
        current_match = -1
        full_string_index = -1
        mention_prefix_length = -1
        calculated_match_index = -1
        
        # output JSON.
        self.output_debug( "++++++++ In " + me + " - Mention JSON:\n\n\n" + JSONHelper.pretty_print_json( mention_JSON_IN )  )

        # first, retrieve values from JSON, so we can use them to see if already
        #    added.
        
        # "detection" is the "exact" (mention), with "prefix" and "suffix"
        #    before and after, each enclosed in square brackets.
        #    - Example: [<"prefix">]<"exact">[<"suffix">]
        mention_detection = mention_JSON_IN.get( OpenCalaisApiResponse.JSON_NAME_DETECTION, None )
        
        # "exact" is the mention itself.
        #    - Examples: "he" or "Jim Morrison"
        mention_exact = mention_JSON_IN.get( OpenCalaisApiResponse.JSON_NAME_EXACT, None )
        
        # "length" is the length of the mention string.
        mention_length = mention_JSON_IN.get( OpenCalaisApiResponse.JSON_NAME_LENGTH, None )
        
        # "offset" is the index of the start of the mention string in the
        #    article text passed to OpenCalais (plain text).
        mention_offset = mention_JSON_IN.get( OpenCalaisApiResponse.JSON_NAME_OFFSET, None )
        
        # "prefix" is the text directly before the mention, for context.
        mention_prefix = mention_JSON_IN.get( OpenCalaisApiResponse.JSON_NAME_PREFIX, None )

        # "suffix" is the text directly after the mention, for context.
        mention_suffix = mention_JSON_IN.get( OpenCalaisApiResponse.JSON_NAME_SUFFIX, None )

        # is this mention already stored?
        
        # Filter on exact, offset, length, prefix, and suffix.
        mention_qs = article_source_IN.article_source_mention_set.filter( value = mention_exact )
        mention_qs = mention_qs.filter( value_index = mention_offset )
        mention_qs = mention_qs.filter( value_length = mention_length )
        mention_qs = mention_qs.filter( context_before = mention_prefix )
        mention_qs = mention_qs.filter( context_after = mention_suffix )
                        
        # got one?
        mention_count = mention_qs.count()
        if ( mention_count == 0 ):
                        
            # no.  Create one.
            current_mention = Article_Source_Mention()
            
            # store the Article_Source in it.
            current_mention.article_source = article_source_IN
            
            # store information from OpenCalais
            current_mention.value = mention_exact
            current_mention.value_in_context = mention_detection
            current_mention.value_index = mention_offset
            current_mention.value_length = mention_length
            current_mention.context_before = mention_prefix
            current_mention.context_after = mention_suffix
            
            # derive a few more details based on finding the mention in the text
            #    of the article.
            
            # get article text for article.
            article_text = article_IN.article_text_set.get()
            
            # then, call find_in_text (FIT) method on mention plus suffix (to
            #    make sure we get the right "he", for example).
            find_string = mention_exact + mention_suffix
            mention_FIT_values = article_text.find_in_text( find_string )
            
            # Validate results.
            FIT_status_list = self.validate_FIT_results( mention_FIT_values )
            
            # any error statuses passed back?
            FIT_status_count = len( FIT_status_list )
            if ( FIT_status_count == 0 ):
            
                # None - success!  Load items into variables.
                
                # get result lists.
                canonical_index_list = mention_FIT_values.get( Article_Text.FIT_CANONICAL_INDEX_LIST, [] )
                plain_text_index_list = mention_FIT_values.get( Article_Text.FIT_TEXT_INDEX_LIST, [] )
                paragraph_list = mention_FIT_values.get( Article_Text.FIT_PARAGRAPH_NUMBER_LIST, [] )
                first_word_list = mention_FIT_values.get( Article_Text.FIT_FIRST_WORD_NUMBER_LIST, [] )
                last_word_list = mention_FIT_values.get( Article_Text.FIT_LAST_WORD_NUMBER_LIST, [] )

                # load values from lists.
                plain_text_index = plain_text_index_list[ 0 ]
                
                if ( mention_offset != plain_text_index ):
                
                    # not the same.  output debug.
                    notes_string = "In " + me + ": ERROR - mention index from OpenCalais ( " + str( mention_offset ) + " ) doesn't match what we found ( " + str( plain_text_index ) + " ). Using local match index instead."
                    notes_list.append( notes_string )
                    self.output_debug( notes_string )
                    
                    # AND use what we calculated, not what OpenCalais returned.
                    plain_text_index = current_value

                #-- END check to see if index from OpenCalais matches --#

                canonical_index = canonical_index_list[ 0 ]
                paragraph_number = paragraph_list[ 0 ]
                first_word_number = first_word_list[ 0 ]

                # add the count of words in the actual mention minus
                #    1 (to account for the first word already being
                #    counted) to the first word value to get the last
                #    word number.
                mention_word_list = mention_exact.split()
                mention_word_count = len( mention_word_list )
                last_word_number = first_word_number + mention_word_count - 1

                # flag that it is OK to update.
                is_ok_to_update = True

            else:
            
                # add FIT_status_list to notes_list.
                notes_list = notes_list + FIT_status_list

                # try one-by-one.  Start with is_ok_to_update = True, then set
                #    to False if anything goes wrong.
                is_ok_to_update = True

                # to start, make sure the text is in the article.
                find_full_string = mention_prefix + mention_exact + mention_suffix
                found_list = article_text.find_in_plain_text( find_full_string )
                found_list_count = len( found_list )
                if ( found_list_count == 1 ):
                
                    # we know we have one match, so we can dig in and try to get
                    #    all the things.
                    sanity_check_index = found_list[ 0 ]
                    full_string_index = sanity_check_index
                    
                    #-----------------------------------------------------------
                    # plain text index
                    #-----------------------------------------------------------

                    # get actual plain text index (no prefix)
                    find_string = mention_exact + mention_suffix
                    found_list = article_text.find_in_plain_text( find_string )
                    found_list_count = len( found_list )
                    if ( found_list_count == 1 ):
                    
                        # load value.
                        plain_text_index = found_list[ 0 ]
                        
                        # see if it agrees with OpenCalais
                        if ( mention_offset != plain_text_index ):
                        
                            # not the same.  output debug.
                            notes_string = "In " + me + ": ERROR - mention index from OpenCalais ( " + str( mention_offset ) + " ) doesn't match what we found ( " + str( plain_text_index ) + " ). Using local match index instead."
                            notes_list.append( notes_string )
                            self.output_debug( notes_string )
                            
                            # AND use what we calculated, not what OpenCalais returned.
                            plain_text_index = current_value
        
                        #-- END check to see if index from OpenCalais matches --#
                        
                    elif ( found_list_count > 1 ):
                    
                        # multiple matches.  If at end of entire article, could
                        #    be because suffix is one or two words, there are
                        #    other matches in the article.
                        # Match = full_string_index + mention_prefix_length
                        mention_prefix_length = len( mention_prefix )
                        calculated_match_index = full_string_index + mention_prefix_length
                        if calculated_match_index in found_list:
                        
                            # the calculated match index is in list.  That is
                            #    the match.  Use it.
                            plain_text_index = calculated_match_index
                            
                        #-- END check to see which match is the right one.
                    
                    else:
                    
                        # ERROR.
                        notes_string = "In " + me + ": ERROR - plain text index - `mention + suffix` match count = " + str( found_list_count ) + ", `prefix + mention + suffix` was at index " + str( sanity_check_index )
                        notes_list.append( notes_string )
                        self.output_debug( notes_string )
                        
                        #is_ok_to_update = False
                        # might as well update, so we can see what else for
                        #    debugging. just set the plain text index to -1.
                        plain_text_index = -1
                    
                    #-- END check to see if found mention + suffix
                    
                    #-----------------------------------------------------------
                    # canonical index
                    #-----------------------------------------------------------

                    # canonical text seems to be a troublesome one.  Start out
                    #    looking for the full string.
                    found_list = article_text.find_in_canonical_text( find_full_string )
                    found_list_count = len( found_list )
                    if ( found_list_count == 1 ):
                    
                        # found it.  load value from list.
                        canonical_index = found_list[ 0 ]
                        
                        # then, add the length of the prefix to the value, to
                        #    get to the actual value.
                        mention_prefix_length = len( mention_prefix )
                        canonical_index = canonical_index + mention_prefix_length
                        
                    else:
                    
                        # ERROR.
                        notes_string = "In " + me + ": ERROR - canonical index - prefix + mention + suffix ( \"" + find_full_string + "\" ) either returned 0 or multiple matches: " + str( found_list )
                        notes_list.append( notes_string )
                        self.output_debug( notes_string )

                        # OK to update...  Just broken.
                        # is_ok_to_update = False
                    
                    #-- END check to see if found mention + suffix
                    
                    #-----------------------------------------------------------
                    # word first and last numbers
                    #-----------------------------------------------------------

                    # Start out looking for the full string.
                    found_dict = article_text.find_in_word_list( find_full_string )
                    first_word_list = found_dict.get( Article_Text.FIT_FIRST_WORD_NUMBER_LIST, [] )
                    last_word_list = found_dict.get( Article_Text.FIT_LAST_WORD_NUMBER_LIST, [] )
                    found_list_count = len( first_word_list )
                    if ( found_list_count == 1 ):
                    
                        # found it.  load values from lists.
                        first_word_number = first_word_list[ 0 ]
                        last_word_number = last_word_list[ 0 ]
                        
                        # then, add the number of words of the prefix to the
                        #    first word value, to get to the actual value.
                        mention_prefix_word_list = mention_prefix.split()
                        mention_prefix_word_count = len( mention_prefix_word_list )
                        first_word_number = first_word_number + mention_prefix_word_count
                        
                        # and add the count of words in the actual mention minus
                        #    1 (to account for the first word already being
                        #    counted) to the first word value to get the last
                        #    word number.
                        mention_word_list = mention_exact.split()
                        mention_word_count = len( mention_word_list )
                        last_word_number = first_word_number + mention_word_count - 1
                        
                    else:
                    
                        # ERROR.
                        notes_string = "In " + me + ": ERROR - word first and last numbers - prefix + mention + suffix ( \"" + find_full_string + "\" ) either returned 0 or multiple matches: " + str( found_list )
                        notes_list.append( notes_string )
                        self.output_debug( notes_string )

                        # OK to update...  Just broken.
                        # is_ok_to_update = False
                    
                    #-- END check to see if found mention + suffix
                    
                    #-----------------------------------------------------------
                    # paragraph number
                    #-----------------------------------------------------------

                    # Start out looking for the full string.
                    found_list = article_text.find_in_paragraph_list( find_full_string )
                    found_list_count = len( found_list )
                    if ( found_list_count == 1 ):
                    
                        # found it.  load value from list.
                        paragraph_number = found_list[ 0 ]
                        
                    else:
                    
                        # ERROR.
                        notes_string = "In " + me + ": ERROR - paragraph number - prefix + mention + suffix ( \"" + find_full_string + "\" ) either returned 0 or multiple matches: " + str( found_list )
                        notes_list.append( notes_string )
                        self.output_debug( notes_string )

                        # OK to update...  Just broken.
                        # is_ok_to_update = False
                    
                    #-- END check to see if found mention + suffix
                                        
                else:
                
                    # Either no match or multiple.
                    notes_string = "In " + me + ": ERROR - plain text index - prefix + mention + suffix ( \"" + find_full_string + "\" ) either returned 0 or multiple matches: " + str( found_list )
                    notes_list.append( notes_string )
                    self.output_debug( notes_string )
                    is_ok_to_update = False
                
                #-- END check to see if match for prefix + mention + suffix --#
                
            #-- END check to make sure all searches returned same count of matches. --#
            
            # OK to update the stuff from FIT?
            if ( is_ok_to_update == True ):

                # Yes.  Update them.
                current_mention.value_index = plain_text_index
                current_mention.canonical_index = canonical_index
                current_mention.value_word_number_start = first_word_number
                current_mention.value_word_number_end = last_word_number
                current_mention.paragraph_number = paragraph_number
            
            #-- END check to see if OK to update with info from FIT. --#

            # and store a few more details.
            current_mention.capture_method = self.CONFIG_APPLICATION

            # no UUID for a mention.
            #current_mention.uuid = quotation_URI_IN
            #current_mention.uuid_name = self.OPEN_CALAIS_UUID_NAME
            
            # notes?
            notes_count = len( notes_list )
            if ( notes_count > 0 ):
            
                # yes - join with newline, add to notes.
                notes_string = "\n".join( notes_list )
                current_mention.notes = notes_string
                
            #-- END check to see if notes. --#
                        
            # save the quotation instance.
            current_mention.save()
            
            # and return it.
            instance_OUT = current_mention
            
        elif ( mention_count == 1 ):
        
            # already got one.  Return it.
            instance_OUT = mention_qs.get()
        
        elif ( mention_count > 1 ):
        
            # trouble - more than one quotation for the UUID.
            self.output_debug( "++++++++ In " + me + " - ERROR - more than one mention matches.  Something is off..." )
            instance_OUT = None

        else:
        
            # trouble - count is invalid.
            self.output_debug( "++++++++ In " + me + " - ERROR - count of mention matches is neither 0, 1, or greater than 1.  Something is off..." )
            instance_OUT = None

        #-- END check to see if mention already stored. --#
        
        return instance_OUT
        
    #-- END method process_json_mention() --#

        
    def process_json_quotation( self, article_IN, article_source_IN, quotation_URI_IN, quotation_JSON_IN ):
    
        '''
        Accepts Article, Article_Source, OpenCalais URI of a quotation, and JSON
           of a quotation attributed to the source.  Uses URI to check if the
           quotation has already been attributed to the source.  If so, returns
           the instance.  If not, creates an instance and saves it, then returns
           it.  If error, returns None.
           
        Preconditions:  Assumes all input variables will be populated
           appropriately.  If any are missing or set to None, will break,
           throwing exceptions.
           
        Postconditions:  If quotation wasn't already stored, it will be after
           this call.
           
        Example JSON (bonus - can you find the OpenCalais parsing error?):
        {
            "_type": "Quotation",
            "_typeGroup": "relations",
            "_typeReference": "http://s.opencalais.com/1/type/em/r/Quotation",
            "instances": [
                {
                    "detection": "[went on sale in 2005 to limited success. ]Sales through November are less than 15,000, down 54 percent, according to Autodata Corp. Toyota Motor Corp. showed the A-BAT concept, a small hybrid unibody pickup, at the 2008 Detroit auto show but has no immediate plans to put it into production, said spokesman John McCandless.[ \"A lot of people have tried the idea of creating]",
                    "exact": "Sales through November are less than 15,000, down 54 percent, according to Autodata Corp. Toyota Motor Corp. showed the A-BAT concept, a small hybrid unibody pickup, at the 2008 Detroit auto show but has no immediate plans to put it into production, said spokesman John McCandless.",
                    "length": 281,
                    "offset": 2110,
                    "prefix": "went on sale in 2005 to limited success. ",
                    "suffix": " \"A lot of people have tried the idea of creating"
                }
            ],
            "person": "http://d.opencalais.com/pershash-1/52f81716-30d1-3b2b-bc98-16e50eb06782",
            "persondescription": "spokesman",
            "quote": "Sales through November are less than 15,000, down 54 percent, according to Autodata Corp. Toyota Motor Corp. showed the A-BAT concept, a small hybrid unibody pickup, at the 2008 Detroit auto show but has no immediate plans to put it into production"
        }
        '''
        
        # return reference
        instance_OUT = None
        
        # declare variables
        me = "process_json_quotation"
        quotation_qs = None
        quotation_count = -1
        
        # declare variables - Information from OpenCalais JSON
        quotation_string = ""
        quotation_person_title = ""
        quotation_instances_list = None
        current_quotation = None
        quotation_detection = ""
        quotation_exact = ""
        quotation_length = ""
        quotation_offset = ""
        quotation_prefix = ""
        quotation_suffix = ""
        
        # declare variables - get values from article text.
        article_text = None
        quotation_FIT_values = {}
        FIT_status_list = []
        FIT_status_count = -1
        canonical_index_list = []
        plain_text_index_list = []
        paragraph_list = []
        first_word_list = []
        last_word_list = []
        
        # declare variables - values we'll place in instance at the end.
        canonical_index = -1
        plain_text_index = -1
        paragraph_number = -1
        first_word_number = -1
        last_word_number = -1
        is_ok_to_update = False
        current_value = None
        notes_list = []
        notes_count = -1
        notes_string = ""
        
        # output JSON.
        self.output_debug( "++++++++ In " + me + " - Quotation JSON:\n\n\n" + JSONHelper.pretty_print_json( quotation_JSON_IN )  )

        # need to see if this quotation has already been stored.

        # Filter on UUID from Quotation JSON object.
        quotation_qs = article_source_IN.article_source_quotation_set.filter( uuid = quotation_URI_IN )
                        
        # got one?
        quotation_count = quotation_qs.count()
        if ( quotation_count == 0 ):
                        
            # no.  Create one.
            current_quotation = Article_Source_Quotation()
            
            # store the Article_Source in it.
            current_quotation.article_source = article_source_IN
            
            # get actual quotation information from JSON
            
            # "quote" is the quotation without an attribution string.
            quotation_string = quotation_JSON_IN.get( OpenCalaisApiResponse.JSON_NAME_QUOTE, None )
            
            self.output_debug( "In " + me + ": quotation_string = \"" + quotation_string + "\"" )

            # "persondescription" is the description of the person that
            #    accompanied attribution for the quote.
            #    - Example: would be "spokesman" for atttribution string
            #       ", said spokesman John McCandless."
            quotation_person_title = quotation_JSON_IN.get( OpenCalaisApiResponse.JSON_NAME_PERSON_DESCRIPTION, None )

            # more details are stored in JSON object referred to as "instances".
            quotation_instances_list = quotation_JSON_IN.get( OpenCalaisApiResponse.JSON_NAME_INSTANCES, None )
            current_instance = quotation_instances_list[ 0 ]
            
            # get values from OpenCalais instance
            
            # "detection" is the "exact" (quote plus attribution), with "prefix"
            #    and "suffix" before and after, each enclosed in square
            #    brackets.
            #    - Example: [<"prefix">]<"exact">[<"suffix">]
            quotation_detection = current_instance.get( OpenCalaisApiResponse.JSON_NAME_DETECTION, None )
            
            # "exact" is the quotation plus the attribution string.
            #    - Example: "quote", said Jim.
            quotation_exact = current_instance.get( OpenCalaisApiResponse.JSON_NAME_EXACT, None )
            
            # "length" is the length of the quotation string.
            quotation_length = current_instance.get( OpenCalaisApiResponse.JSON_NAME_LENGTH, None )
            
            # "offset" is the index of the start of the quotation string in the
            #    article text passed to OpenCalais (plain text).
            quotation_offset = current_instance.get( OpenCalaisApiResponse.JSON_NAME_OFFSET, None )
            
            # "prefix" is the text directly before the quotation, included for
            #    context.
            quotation_prefix = current_instance.get( OpenCalaisApiResponse.JSON_NAME_PREFIX, None )

            # "suffix" is the text directly after the quotation, included for
            #    context.
            quotation_suffix = current_instance.get( OpenCalaisApiResponse.JSON_NAME_SUFFIX, None )

            # store information from OpenCalais
            current_quotation.value = quotation_string
            current_quotation.value_with_attribution = quotation_exact
            current_quotation.value_in_context = quotation_detection
            current_quotation.value_index = quotation_offset
            current_quotation.value_length = quotation_length
            current_quotation.context_before = quotation_prefix
            current_quotation.context_after = quotation_suffix
            
            # derive a few more details based on finding the quote in the text
            #    of the article.
            
            # get article text for article.
            article_text = article_IN.article_text_set.get()
            
            # then, call find_in_text (FIT) method.  When we deal with words, we
            #    split on spaces.  Because of this, "words" must include the
            #    punctuation around them for them to match.  The quotation_string
            #    doesn't include punctuation, so we can't use it.  Instead, we
            #    need to use the "exact" string, since it includes punctuation.
            quotation_FIT_values = article_text.find_in_text( quotation_exact )
            
            # Validate results.
            FIT_status_list = self.validate_FIT_results( quotation_FIT_values )

            # any error statuses passed back?
            FIT_status_count = len( FIT_status_list )
            if ( FIT_status_count == 0 ):
            
                # None - success!
                
                self.output_debug( "In " + me + ": FIT status was good - single match for each element we are looking for." )

                # get result lists.
                canonical_index_list = quotation_FIT_values.get( Article_Text.FIT_CANONICAL_INDEX_LIST, [] )
                plain_text_index_list = quotation_FIT_values.get( Article_Text.FIT_TEXT_INDEX_LIST, [] )
                paragraph_list = quotation_FIT_values.get( Article_Text.FIT_PARAGRAPH_NUMBER_LIST, [] )
                first_word_list = quotation_FIT_values.get( Article_Text.FIT_FIRST_WORD_NUMBER_LIST, [] )
                last_word_list = quotation_FIT_values.get( Article_Text.FIT_LAST_WORD_NUMBER_LIST, [] )

                # this is the normal case.  Save the values into our current
                #    quotation instance.
                
                # make sure that the plain text index matches the one from
                #    OpenCalais.
                plain_text_index = plain_text_index_list[ 0 ]
                if ( quotation_offset != plain_text_index ):
                
                    # not the same.  output debug.
                    notes_string = "In " + me + ": ERROR - quotation index from OpenCalais ( " + str( quotation_offset ) + " ) doesn't match what we found ( " + str( plain_text_index ) + " ).  Using local match index instead."
                    notes_list.append( notes_string )
                    self.output_debug( notes_string )
                    
                    # AND use what we calculated, not what OpenCalais returned.
                    current_quotation.value_index = plain_text_index

                #-- END check to see if index from OpenCalais matches --#
                
                # canonical index
                canonical_index = canonical_index_list[ 0 ]
                
                # value_word_number_start
                first_word_number = first_word_list[ 0 ]
                
                # value_word_number_end
                last_word_number = last_word_list[ 0 ]

                # paragraph_number
                paragraph_number = paragraph_list[ 0 ]
                
                # flag that it is OK to update.
                is_ok_to_update = True

            else:

                # add FIT_status_list to notes_list.
                notes_list = notes_list + FIT_status_list

                self.output_debug( "In " + me + ": FIT status was bad - see if the string is actually in the article." )

                # try one-by-one.  Start with is_ok_to_update = True, then set
                #    to False if anything goes wrong.
                is_ok_to_update = True

                # to start, make sure the text is in the article.
                found_list = article_text.find_in_plain_text( quotation_exact )
                found_list_count = len( found_list )
                if ( found_list_count == 1 ):
                
                    # we know we have one match, so we can dig in and try to get
                    #    all the things.
                    
                    #-----------------------------------------------------------
                    # plain text index
                    #-----------------------------------------------------------

                    # store the plain text index from check above.
                    plain_text_index = found_list[ 0 ]
                    
                    # see if it agrees with OpenCalais
                    if ( quotation_offset != plain_text_index ):
                    
                        # not the same.  output debug.
                        notes_string = "In " + me + ": ERROR - quotation index from OpenCalais ( " + str( quotation_offset ) + " ) doesn't match what we found ( " + str( plain_text_index ) + " ).  Using local match index instead."
                        notes_list.append( notes_string )
                        self.output_debug( notes_string )
                        
                        # AND use what we calculated, not what OpenCalais returned.
                        plain_text_index = plain_text_index
    
                    #-- END check to see if index from OpenCalais matches --#
                        
                    #-----------------------------------------------------------
                    # canonical index
                    #-----------------------------------------------------------

                    # canonical text seems to be a troublesome one.  Start out
                    #    looking for the full string.
                    found_list = article_text.find_in_canonical_text( quotation_exact )
                    found_list_count = len( found_list )
                    if ( found_list_count == 1 ):
                    
                        # found it.  load value from list.
                        canonical_index = found_list[ 0 ]
                        
                    else:
                    
                        # ERROR.
                        notes_string = "In " + me + ": ERROR - canonical index - search for quotation ( \"" + quotation_string + "\" ) either returned 0 or multiple matches: " + str( found_list )
                        notes_list.append( notes_string )
                        self.output_debug( notes_string )
                        
                        # set canonical_index to -1.
                        canonical_index = -1

                        # OK to update...  Just broken.
                        # is_ok_to_update = False
                    
                    #-- END check to see if found mention + suffix
                    
                    #-----------------------------------------------------------
                    # word first and last numbers
                    #-----------------------------------------------------------

                    # Start out looking for the full string.
                    found_dict = article_text.find_in_word_list( quotation_exact )
                    
                    self.output_debug( "In " + me + ": results of looking for string in word list: " + str( found_dict ) )
                    
                    first_word_list = found_dict.get( Article_Text.FIT_FIRST_WORD_NUMBER_LIST, [] )
                    last_word_list = found_dict.get( Article_Text.FIT_LAST_WORD_NUMBER_LIST, [] )
                    found_list_count = len( first_word_list )
                    if ( found_list_count == 1 ):
                    
                        # found it.  load values from lists.
                        first_word_number = first_word_list[ 0 ]
                        last_word_number = last_word_list[ 0 ]
                        
                    else:
                    
                        # ERROR.
                        notes_string = "In " + me + ": ERROR - word first and last numbers - search for quotation ( \"" + quotation_string + "\" ) either returned 0 or multiple matches: " + str( first_word_list )
                        notes_list.append( notes_string )
                        self.output_debug( notes_string )

                        # OK to update...  Just broken.
                        # is_ok_to_update = False
                    
                    #-- END check to see if found mention + suffix
                    
                    #-----------------------------------------------------------
                    # paragraph number
                    #-----------------------------------------------------------

                    # Start out looking for the full string.
                    found_list = article_text.find_in_paragraph_list( quotation_exact )
                    found_list_count = len( found_list )
                    if ( found_list_count == 1 ):
                    
                        # found it.  load value from list.
                        paragraph_number = found_list[ 0 ]
                        
                    else:
                    
                        # ERROR.
                        notes_string = "In " + me + ": ERROR - paragraph number - search for quotation ( \"" + quotation_string + "\" ) either returned 0 or multiple matches: " + str( found_list )
                        notes_list.append( notes_string )
                        self.output_debug( notes_string )

                        # OK to update...  Just broken.
                        # is_ok_to_update = False
                    
                    #-- END check to see if found mention + suffix
                    
                #-- END check to see if quotation is in plain text string --#
                                        
            #-- END check to make sure all searches returned same count of matches. --#

            # OK to update the stuff from FIT?
            if ( is_ok_to_update == True ):

                # Yes.  Update them.
                current_quotation.value_index = plain_text_index
                current_quotation.canonical_index = canonical_index
                current_quotation.value_word_number_start = first_word_number
                current_quotation.value_word_number_end = last_word_number
                current_quotation.paragraph_number = paragraph_number
            
            #-- END check to see if OK to update with info from FIT. --#

            # and store a few more details.
            current_quotation.capture_method = self.CONFIG_APPLICATION
            current_quotation.uuid = quotation_URI_IN
            current_quotation.uuid_name = self.OPEN_CALAIS_UUID_NAME
            
            # notes?
            if ( len( notes_list ) > 0 ):
            
                # yes - join with newline, add to notes.
                notes_string = "\n".join( notes_list )
                current_quotation.notes = notes_string
                
            #-- END check to see if notes. --#
                        
            # Deferring handling of attribution information for now.
            # fields to track locations of data this coding was based on within
            #    article.  References are based on results of ParsedArticle.parse().
            #article_source.attribution_verb_word_index = -1
            #article_source.attribution_verb_word_number = -1
            #article_source.attribution_paragraph_number = -1
            #article_source.attribution_speaker_name_string = -1
            #article_source.is_speaker_name_pronoun = False
            #article_source.attribution_speaker_name_index_range = ""
            #article_source.attribution_speaker_name_word_range = ""
            
            # save the quotation instance.
            current_quotation.save()
            
            # and return it.
            instance_OUT = current_quotation
            
        elif ( quotation_count == 1 ):
        
            # already got one.  Return it.
            instance_OUT = quotation_qs.get()
        
        elif ( quotation_count > 1 ):
        
            # trouble more than one quotation for the UUID.
            self.output_debug( "++++++++ In " + me + " - ERROR - more than one quotation matches URI \"" + quotation_URI_IN + "\".  Something is off..." )
            instance_OUT = None

        else:
        
            # trouble - count is invalid.
            self.output_debug( "++++++++ In " + me + " - ERROR - count of matches to URI \"" + quotation_URI_IN + "\" is neither 0, 1, or greater than 1.  Something is off..." )
            instance_OUT = None

        #-- END check to see if quote already stored. --#
        
        return instance_OUT
        
    #-- END method process_json_quotation() --#

        
    def set_http_helper( self, instance_IN ):
        
        # return reference
        instance_OUT = ""
        
        # set instance
        self.http_helper = instance_IN
        
        # return instance
        instance_OUT = self.get_http_helper()
        
        return instance_OUT
        
    #-- END method set_http_helper() --#
    

    def validate_FIT_results( self, FIT_values_IN ):

        '''
        Accepts a dictionary of results from a Article_Text.find_in_text() call.
           Looks for problems (counts of nested lists not being 1, not being all
           the same).  If it finds problems, returns list of string messages 
           describing problems.  If no problems, returns empty list.
        '''
        
        # return reference
        status_list_OUT = []
        
        # declare variables
        me = "validate_FIT_results"
        status_OUT = ""
        canonical_index_list = []
        plain_text_index_list = []
        paragraph_list = []
        first_word_list = []
        last_word_list = []
        canonical_index_count = -1
        plain_text_index_count = -1
        paragraph_count = -1
        first_word_count = -1
        last_word_count = -1
        count_list = []
        unique_count_list = []
        unique_count = -1
        match_count = -1

        # Unpack results - for each value, could be 0, 1, or more.
        # - If 0, no match - ERROR.
        # - If 1, use value.
        # - If more than one, multiple matches - ERROR.
        # - All lists should have same count.  If any are different - ERROR.

        # get result lists.
        canonical_index_list = FIT_values_IN.get( Article_Text.FIT_CANONICAL_INDEX_LIST, [] )
        plain_text_index_list = FIT_values_IN.get( Article_Text.FIT_TEXT_INDEX_LIST, [] )
        paragraph_list = FIT_values_IN.get( Article_Text.FIT_PARAGRAPH_NUMBER_LIST, [] )
        first_word_list = FIT_values_IN.get( Article_Text.FIT_FIRST_WORD_NUMBER_LIST, [] )
        last_word_list = FIT_values_IN.get( Article_Text.FIT_LAST_WORD_NUMBER_LIST, [] )

        # get counts and add them to list.
        canonical_index_count = len( canonical_index_list )
        count_list.append( canonical_index_count )

        plain_text_index_count = len( plain_text_index_list )
        count_list.append( plain_text_index_count )

        paragraph_count = len( paragraph_list )
        count_list.append( paragraph_count )

        first_word_count = len( first_word_list )
        count_list.append( first_word_count )

        last_word_count = len( last_word_list )
        count_list.append( last_word_count )

        # counts all the same?
        unique_count_list = SequenceHelper.list_unique_values( count_list )
        
        # first, see how many unique values (should be 1).
        unique_count = len( unique_count_list )
        if ( unique_count == 1 ):
        
            # all have same count.  What is it?
            match_count = unique_count_list[ 0 ]
            if ( match_count == 1 ):
            
                # this is the normal case.  Return empty list.
                status_list_OUT = []

            elif ( match_count == 0 ):
            
                # error - no matches returned for quotation.  What to do?
                status_OUT = "In " + me + ": ERROR - search for string in text yielded no matches."
                status_list_OUT.append( status_OUT )
                self.output_debug( status_OUT )
                
            elif ( match_count > 1 ):
            
                # error - multiple matches returned for quotation.  What to do?
                status_OUT = "In " + me + ": ERROR - search for string in text yielded " + str( match_count ) + " matches."
                status_list_OUT.append( status_OUT )
                self.output_debug( status_OUT )
                
            else:
            
                # error - matches returned something other than 0, 1, or
                #    > 1.  What to do?
                status_OUT = "In " + me + ": ERROR - search for string in text yielded invalid count: " + str( match_count )
                status_list_OUT.append( status_OUT )
                self.output_debug( status_OUT )
                
            #-- END check to see how many matches were found. --#
            
        else:

            # error - unique_count_list does not have only one thing in it.
            status_OUT = "In " + me + ": ERROR - search for string in text yielded different numbers of results for different ways of searching: " + str( unique_count_list )
            status_list_OUT.append( status_OUT )
            self.output_debug( status_OUT )
            
        #-- END check to make sure all searches returned same count of matches. --#
        
        return status_list_OUT        
        
    #-- END method validate_FIT_results() --#


#-- END class OpenCalaisArticleCoder --#