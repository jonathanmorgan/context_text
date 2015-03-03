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

# mess with python 3 support
import six

# python utilities
from python_utilities.django_utils.django_string_helper import DjangoStringHelper
from python_utilities.json.json_helper import JSONHelper
from python_utilities.network.http_helper import Http_Helper

# sourcenet classes

# models
from sourcenet.models import Article_Source
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
                        debug_string = OpenCalaisApiResponse.print_calais_json( requests_response_json )
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
        
        # quote processing variables.
        quotation_dict = None
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
        person_paper = None        

        # get logger
        my_logger = self.get_logger()
        
        # get response helper.
        my_response_helper = OpenCalaisApiResponse()

        # chuck the response in there.
        my_response_helper.set_json_response_object( json_response_IN )
        
        # once we get response JSON sorted out, then use it to interact.
        
        # get all the quotations.
        quotation_dict = my_response_helper.get_items_of_type( OpenCalaisApiResponse.OC_ITEM_TYPE_QUOTATION )
        
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
        
        # now, look at people who were quoted.
        person_counter = 0
        for person_URI in person_to_quotes_map:
        
            # increment counter
            person_counter = person_counter + 1
            
            # try to get person from URI.
            person_json = my_response_helper.get_item_from_response( person_URI )
            
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

                # !CURRENT - test new fancy lookup.
                
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
                
                # got anything?
                if ( article_source_qs.count() == 0 ):
                                             
                    # no - add - more stuff to set.  Need to see what we can get.
                    
                    # use the article_source created above.
                    #article_source = Article_Source()

                    # !TODO - set contents of Article_Source data fields.
                    article_source.article_data = article_data_IN
                    article_source.person = source_person
                    
                    # confidence level set in lookup_person() method.
                    #article_source.match_confidence_level = 1.0
    
                    article_source.source_type = Article_Source.SOURCE_TYPE_INDIVIDUAL
                    article_source.title = ""
                    article_source.more_title = ""
                    article_source.organization = None # models.ForeignKey( Organization, blank = True, null = True )
                    #article_source.document = None
                    article_source.source_contact_type = None
                    #article_source.source_capacity = None
                    #article_source.localness = None
                    article_source.notes = ""
    
                    # field to store how source was captured.
                    article_source.capture_method = self.CONFIG_APPLICATION
                
                    # !TODO - article_source.save()
                    
                    # !TODO - topics?
                    # if we want to set topics, first save article_source, then
                    #    we can parse them out of the JSON, make sure they exist
                    #    in topics table, then add relation.  Probably want to
                    #    make Person_Topic also.  So, if we do this, it will be
                    #    a separate method.
                    #article_source.topics = None # models.ManyToManyField( Topic, blank = True, null = True )

                    my_logger.debug( "In " + me + ": adding Article_Source instance for " + str( source_person ) + "." )
    
                else:
                
                    my_logger.debug( "In " + me + ": Article_Source instance already exists for " + str( source_person ) + "." )
                    
                #-- END check if need new Article_Source instance --#
                
                # !TODO - deal with quotes.
                # then, need to see if there is a quote for this quote.
                #    Filter on UUID from Quotation JSON object.
                '''
                    # fields to track locations of data this coding was based on within
                    #    article.  References are based on results of ParsedArticle.parse().
                    article_source.attribution_verb_word_index = -1
                    article_source.attribution_verb_word_number = -1
                    article_source.attribution_paragraph_number = -1
                    article_source.attribution_speaker_name_string = -1
                    article_source.is_speaker_name_pronoun = False
                    article_source.attribution_speaker_name_index_range = ""
                    article_source.attribution_speaker_name_word_range = ""
    
                '''

            else:
            
                my_logger.debug( "In " + me + ": error - no matching person found - must have been a problem looking up name \"" + author_name + "\"" )

            #-- END check to see if person found. --#
        
        #-- END loop over persons --#

        return status_OUT
    
    #-- END function process_json_api_response() --#


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