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

Configuration properties for it are stored in django's admins, in the
   django_config application.  The properties are stored in Application
   "OpenCalais_REST_API_v1":
   - open_calais_api_key - API key for accessing OpenCalais version 1 API.
   - submitter - submitter you want to report to the API.
'''

#================================================================================
# Imports
#================================================================================


# python standard libraries
import json
import sys

# mess with python 3 support
import six

# django imports
from django.core.exceptions import MultipleObjectsReturned

# python utilities
from python_utilities.django_utils.django_string_helper import DjangoStringHelper
from python_utilities.json.json_helper import JSONHelper
from python_utilities.logging.logging_helper import LoggingHelper
from python_utilities.network.http_helper import Http_Helper
from python_utilities.sequences.sequence_helper import SequenceHelper

# sourcenet classes

# models
from sourcenet.models import Alternate_Subject_Match
from sourcenet.models import Article_Author
from sourcenet.models import Article_Data
from sourcenet.models import Article_Data_Notes
from sourcenet.models import Article_Subject
from sourcenet.models import Article_Subject_Mention
from sourcenet.models import Article_Subject_Quotation
from sourcenet.models import Article_Text
from sourcenet.models import Person

# person details
from sourcenet.shared.person_details import PersonDetails

# parent abstract class.
from sourcenet.article_coding.article_coder import ArticleCoder

# class to help with parsing and processing OpenCalaisApiResponse.
from sourcenet.article_coding.open_calais_v1.open_calais_api_response import OpenCalaisApiResponse

#================================================================================
# Package constants-ish
#================================================================================


#================================================================================
# OpenCalaisArticleCoder class
#================================================================================

# define OpenCalaisArticleCoder class.
class ManualArticleCoder( ArticleCoder ):

    '''
    This class is a helper for coding articles manually.
    '''

    #============================================================================
    # Constants-ish
    #============================================================================
    

    # status constants - in parent (ArticleCoder) now:
    # STATUS_SUCCESS = "Success!"
    # STATUS_ERROR_PREFIX = "Error: "
    
    # logging
    LOGGER_NAME = "sourcenet.article_coding.manual_coding.manual_article_coder"
    
    # config application
    CONFIG_APPLICATION = "Manual_Coding"

    '''
    # ==> Moved to Article_Coder class.
    # person types
    PERSON_TYPE_SUBJECT = "subject"
    PERSON_TYPE_SOURCE = "source"
    PERSON_TYPE_AUTHOR = "author"

    # subject_type to person type dictionary
    SUBJECT_TYPE_TO_PERSON_TYPE_MAP = {}
    SUBJECT_TYPE_TO_PERSON_TYPE_MAP[ Article_Subject.SUBJECT_TYPE_MENTIONED ] = PERSON_TYPE_SUBJECT
    SUBJECT_TYPE_TO_PERSON_TYPE_MAP[ Article_Subject.SUBJECT_TYPE_QUOTED ] = PERSON_TYPE_SOURCE    
    '''

    # kwarg parameter names
    KWARG_DATA_STORE_JSON_STRING = "data_store_json_string_IN"
    KWARG_ARTICLE_DATA_ID = "article_data_id_IN"
    KWARG_REQUEST = "request_IN"
    KWARG_RESPONSE_DICTIONARY = "response_dictionary_IN"

    # person store JSON property names
    DATA_STORE_PROP_PERSON_ARRAY = "person_array"
    DATA_STORE_PROP_PERSON_TYPE = ArticleCoder.PARAM_PERSON_TYPE # "person_type"
    DATA_STORE_PROP_ARTICLE_PERSON_ID = ArticleCoder.PARAM_ARTICLE_PERSON_ID # article_person_id
    DATA_STORE_PROP_PERSON_NAME = ArticleCoder.PARAM_PERSON_NAME # "person_name"
    DATA_STORE_PROP_FIXED_PERSON_NAME = ArticleCoder.PARAM_FIXED_PERSON_NAME # "fixed_person_name"
    DATA_STORE_PROP_TITLE = ArticleCoder.PARAM_TITLE             # "title"
    DATA_STORE_PROP_PERSON_ORGANIZATION = ArticleCoder.PARAM_PERSON_ORGANIZATION # "person_organization"
    DATA_STORE_PROP_QUOTE_TEXT = ArticleCoder.PARAM_QUOTE_TEXT   # "quote_text"
    DATA_STORE_PROP_PERSON_ID = ArticleCoder.PARAM_PERSON_ID     # "person_id"
    DATA_STORE_PROP_PERSON_INDEX = "person_index"
    DATA_STORE_PROP_NEXT_PERSON_INDEX = "next_person_index"
    DATA_STORE_PROP_NAME_TO_PERSON_INDEX_MAP = "name_to_person_index_map"
    DATA_STORE_PROP_ID_TO_PERSON_INDEX_MAP = "id_to_person_index_map"
    DATA_STORE_PROP_STATUS_MESSAGE_ARRAY = "status_message_array"
    DATA_STORE_PROP_LATEST_PERSON_INDEX = "latest_person_index"
    
    #--------------------------------------------------------------------------#
    # HTML element IDs
    #--------------------------------------------------------------------------#

    DIV_ID_PERSON_CODING = "person-coding"
    INPUT_ID_MATCHED_PERSON_ID = "matched-person-id"
    INPUT_ID_ARTICLE_PERSON_ID = "article-person-id"
    INPUT_ID_DATA_STORE_PERSON_INDEX = "data-store-person-index"
    INPUT_ID_PERSON_NAME = "person-name"
    INPUT_ID_FIXED_PERSON_NAME = "fixed-person-name"
    INPUT_ID_PERSON_TYPE = "person-type"
    INPUT_ID_PERSON_TITLE = "person-title"
    INPUT_ID_PERSON_ORGANIZATION = "person-organization"
    INPUT_ID_SOURCE_QUOTE_TEXT = "source-quote-text"
    DIV_ID_LOOKUP_PERSON_EXISTING_ID = "lookup-person-existing-id"
    
    # HTML elements - form submission
    INPUT_ID_SUBMIT_ARTICLE_CODING = "input-submit-article-coding";
    INPUT_ID_DATA_STORE_JSON = "id_data_store_json";
    
    # HTML elements - django-ajax-select HTML
    INPUT_ID_AJAX_ID_PERSON = "id_person";
    INPUT_ID_AJAX_ID_PERSON_TEXT = "id_person_text";
    DIV_ID_AJAX_ID_PERSON_ON_DECK = "id_person_on_deck";
    
    # HTML elements - find in text
    INPUT_ID_TEXT_TO_FIND_IN_ARTICLE = "text-to-find-in-article";


    #==========================================================================#
    # NOT Instance variables
    # Class variables - overriden by __init__() per instance if same names, but
    #    if not set there, shared!
    #==========================================================================#

    
    # declare variables
    #http_helper = None
    #content_type = ""
    #output_format = ""


    #==========================================================================#
    # Constructor
    #==========================================================================#


    def __init__( self ):

        # call parent's __init__() - I think...
        super( ManualArticleCoder, self ).__init__()
        
        # declare variables
        
        # set application string (for LoggingHelper parent class: (LoggingHelper -->
        #    BasicRateLimited --> ArticleCoder --> OpenCalaisArticleCoder).
        self.set_logger_name( self.LOGGER_NAME )
        
        # items for processing a given JSON response - should be updated with
        #    every new article coded.
        
        # coder type (defaults to self.CONFIG_APPLICATION).
        self.coder_type = self.CONFIG_APPLICATION

        # most recent Article_Data instance.
        self.latest_article_data = None
        
    #-- END method __init__() --#


    #==========================================================================#
    # Class methods
    #==========================================================================#


    @classmethod
    def convert_article_data_to_data_store_json( cls, article_data_IN, return_string_IN = False ):

        '''
        Accepts Article_Data instance we want to convert to data store JSON.
           Retrieves authors and sources and uses them to create data store
           JSON representation of Article_Data.

        Returns Article_Data in JSON format, either in dictionaries and lists
           (object format), or string JSON.
        '''

        # return reference
        json_OUT = ""

        # declare variables
        me = "convert_article_data_to_data_store_json"
        debug_message = ""
        data_store_dict = None
        article_author_qs = None
        article_subject_qs = None
        person_list = None
        current_index = -1
        next_index = -1
        name_to_person_index_dict = None
        id_to_person_index_dict = None

        # declare variables - processing Article_Data's child records.
        current_author = None
        current_subject = None
        current_article_person_id = -1
        current_person = None
        current_person_type = ""
        current_person_name = ""
        current_person_verbatim_name = ""
        current_person_lookup_name = ""
        current_organization_string = ""
        current_title = ""
        current_quote_text = ""
        current_person_id = ""
        current_person_dict = {}

        # declare variables - processing Article_Subject
        current_subject_type = ""
        current_quote_qs = None
        quote_count = -1

        # first, make sure we have something in article_data_IN.
        if ( ( article_data_IN is not None ) and ( article_data_IN != "" ) ):

            # initialize person list variables.
            person_list = []
            current_index = -1
            next_index = 0
            name_to_person_index_dict = {}
            id_to_person_index_dict = {}

            # we do.  First get list of Article_Authors.
            article_author_qs = article_data_IN.article_author_set.all()

            # ! author loop
            for current_author in article_author_qs:
            
                debug_message = "author: " + str( current_author )
                LoggingHelper.output_debug( debug_message, me, indent_with_IN = "====>", logger_name_IN = cls.LOGGER_NAME )

                # increment index values
                current_index += 1
                next_index += 1
                
                # retrieve Article_Author ID:
                current_article_person_id = current_author.id

                # get current person
                current_person = current_author.person

                debug_message = "author person: " + str( current_person )
                LoggingHelper.output_debug( debug_message, me, indent_with_IN = "========>", logger_name_IN = cls.LOGGER_NAME )

                # set values for person from instance.

                # ==> person_type
                current_person_type = cls.PERSON_TYPE_AUTHOR
                
                # ==> person_name and fixed_person_name
                current_person_name = JSONHelper.escape_json_value( current_author.name )
                current_person_verbatim_name = JSONHelper.escape_json_value( current_author.verbatim_name )
                current_person_lookup_name = JSONHelper.escape_json_value( current_author.lookup_name )
                
                # ==> organization_string
                current_organization_string = JSONHelper.escape_json_value( current_author.organization_string )
                
                # ==> title
                current_title = JSONHelper.escape_json_value( current_author.title )
                
                # ==> quote_text
                current_quote_text = ""
                
                # ==> person_id
                current_person_id = current_person.id

                # create person dictionary
                current_person_dict = {}
                current_person_dict[ cls.DATA_STORE_PROP_PERSON_TYPE ] = current_person_type
                
                # add article_person_id
                current_person_dict[ cls.DATA_STORE_PROP_ARTICLE_PERSON_ID ] = current_article_person_id
                
                # is lookup name different from verbatim name?
                if ( ( ( current_person_verbatim_name is not None ) and ( current_person_verbatim_name != "" ) )
                    and ( ( current_person_lookup_name is not None ) and ( current_person_lookup_name != "" ) )
                    and ( current_person_verbatim_name != current_person_lookup_name ) ):
                    
                    # there was a correction of the verbatim name text.
                    #     "person_name" is the "verbatim_name",
                    #     "fixed_person_name" is the "lookup_name".
                    current_person_dict[ cls.DATA_STORE_PROP_PERSON_NAME ] = current_person_verbatim_name
                    current_person_dict[ cls.DATA_STORE_PROP_FIXED_PERSON_NAME ] = current_person_lookup_name

                else:
                
                    # no fix to name.  Just pass it as we used to. 
                    current_person_dict[ cls.DATA_STORE_PROP_PERSON_NAME ] = current_person_name
                    current_person_dict[ cls.DATA_STORE_PROP_FIXED_PERSON_NAME ] = ""
                    
                #-- END check to see if fixed name. --#    
                
                current_person_dict[ cls.DATA_STORE_PROP_PERSON_ORGANIZATION ] = current_organization_string
                current_person_dict[ cls.DATA_STORE_PROP_TITLE ] = current_title
                current_person_dict[ cls.DATA_STORE_PROP_QUOTE_TEXT ] = current_quote_text
                current_person_dict[ cls.DATA_STORE_PROP_PERSON_ID ] = current_person_id
                current_person_dict[ cls.DATA_STORE_PROP_PERSON_INDEX ] = current_index                

                # add to lists and dicts.
                person_list.append( current_person_dict )
                name_to_person_index_dict[ current_person_name ] = current_index
                id_to_person_index_dict[ current_person_id ] = current_index

            #-- END loop over authors --#

            # then get list of Article_Subjects.
            article_subject_qs = article_data_IN.article_subject_set.all()

            # ! subject loop
            for current_subject in article_subject_qs:

                debug_message = "subject: " + str( current_subject )
                LoggingHelper.output_debug( debug_message, me, indent_with_IN = "====>", logger_name_IN = cls.LOGGER_NAME )

                # get current person
                current_person = current_subject.person
                
                # got a person?  Could be court records, etc.
                if ( current_person is not None ):

                    debug_message = "subject person: " + str( current_person )
                    LoggingHelper.output_debug( debug_message, me, indent_with_IN = "========>", logger_name_IN = cls.LOGGER_NAME )

                    # increment index values
                    current_index += 1
                    next_index += 1
    
                    # set values for person from instance.
    
                    # ==> article_person_id - retrieve Article_Subject ID:
                    current_article_person_id = current_subject.id

                    # ==> person_type
                    current_subject_type = current_subject.subject_type
                    current_person_type = cls.SUBJECT_TYPE_TO_PERSON_TYPE_MAP[ current_subject_type ]
                    
                    # add article_person_id
                    current_person_dict[ cls.DATA_STORE_PROP_ARTICLE_PERSON_ID ] = current_article_person_id
                    
                    # ==> person_name and fixed_person_name
                    current_person_name = JSONHelper.escape_json_value( current_subject.name )
                    current_person_verbatim_name = JSONHelper.escape_json_value( current_subject.verbatim_name )
                    current_person_lookup_name = JSONHelper.escape_json_value( current_subject.lookup_name )
                    
                    # ==> organization_string
                    current_organization_string = JSONHelper.escape_json_value( current_subject.organization_string )
                    
                    # ==> title
                    current_title = JSONHelper.escape_json_value( current_subject.title )
    
                    # ==> person ID                
                    current_person_id = current_person.id
    
                    # ==> quote text
                    current_quote_text = ""
    
                    # retrieve all quotations
                    current_quote_qs = current_subject.article_subject_quotation_set.all()
    
                    # got any?
                    quote_count = current_quote_qs.count()
                    if ( quote_count > 0 ):
    
                        # yes - get quote string from 1st.
                        first_quote = current_quote_qs[ 0 ]
                        current_quote_text = JSONHelper.escape_json_value( first_quote.value )
    
                    #-- END check to see if quotes present. --#
    
                    # create person dictionary
                    current_person_dict = {}
                    current_person_dict[ cls.DATA_STORE_PROP_PERSON_TYPE ] = current_person_type

                    # add article_person_id
                    current_person_dict[ cls.DATA_STORE_PROP_ARTICLE_PERSON_ID ] = current_article_person_id
                        
                    # is lookup name different from verbatim name?
                    if ( ( ( current_person_verbatim_name is not None ) and ( current_person_verbatim_name != "" ) )
                        and ( ( current_person_lookup_name is not None ) and ( current_person_lookup_name != "" ) )
                        and ( current_person_verbatim_name != current_person_lookup_name ) ):
                        
                        # there was a correction of the verbatim name text.
                        #     "person_name" is the "verbatim_name",
                        #     "fixed_person_name" is the "lookup_name".
                        current_person_dict[ cls.DATA_STORE_PROP_PERSON_NAME ] = current_person_verbatim_name
                        current_person_dict[ cls.DATA_STORE_PROP_FIXED_PERSON_NAME ] = current_person_lookup_name
    
                    else:
                    
                        # no fix to name.  Just pass it as we used to. 
                        current_person_dict[ cls.DATA_STORE_PROP_PERSON_NAME ] = current_person_name
                        current_person_dict[ cls.DATA_STORE_PROP_FIXED_PERSON_NAME ] = ""
                        
                    #-- END check to see if fixed name. --#    
                                    
                    current_person_dict[ cls.DATA_STORE_PROP_PERSON_ORGANIZATION ] = current_organization_string
                    current_person_dict[ cls.DATA_STORE_PROP_TITLE ] = current_title
                    current_person_dict[ cls.DATA_STORE_PROP_PERSON_ID ] = current_person_id
                    current_person_dict[ cls.DATA_STORE_PROP_QUOTE_TEXT ] = current_quote_text
                    current_person_dict[ cls.DATA_STORE_PROP_PERSON_INDEX ] = current_index                
    
                    # add to lists and dicts.
                    person_list.append( current_person_dict )
                    name_to_person_index_dict[ current_person_name ] = current_index
                    id_to_person_index_dict[ current_person_id ] = current_index

                #-- END check to see if person present. --#

            #-- END loop over subjects --#

            # put it all together.
            data_store_dict = {}
            data_store_dict[ cls.DATA_STORE_PROP_PERSON_ARRAY ] = person_list
            data_store_dict[ cls.DATA_STORE_PROP_NEXT_PERSON_INDEX ] = next_index
            data_store_dict[ cls.DATA_STORE_PROP_NAME_TO_PERSON_INDEX_MAP ] = name_to_person_index_dict
            data_store_dict[ cls.DATA_STORE_PROP_ID_TO_PERSON_INDEX_MAP ] = id_to_person_index_dict
            data_store_dict[ cls.DATA_STORE_PROP_STATUS_MESSAGE_ARRAY ] = []
            data_store_dict[ cls.DATA_STORE_PROP_LATEST_PERSON_INDEX ] = current_index
            data_store_dict[ 'article_data_id' ] = article_data_IN.id

        #-- END check to see if we have Article_Data instance. --#

        # return string or objects?
        if ( return_string_IN == True ):

            # string - use json.dumps()
            json_OUT = JSONHelper.pretty_print_json( data_store_dict )

        else:

            # objects - just return the dictionary.
            json_OUT = data_store_dict

        #-- END check to see if return string or objects. --#

        return json_OUT

    #-- END class method convert_article_data_to_json() --#


    #============================================================================
    # Instance methods
    #============================================================================


    def init_config_properties( self, *args, **kwargs ):

        '''
        purpose: Called as part of the base __init__() method, so that loading
           config properties can also be included in the parent __init__()
           method.  The application for django_config and any properties that
           need to be loaded should be set here.  To set a property use
           add_config_property( name_IN ).  To set application, use
           set_config_application( app_name_IN ).
           
        inheritance: This method overrides the abstract method of the same name in
           the ArticleCoder parent class.

        preconditions: None.

        postconditions: This instance should be ready to have
           load_config_properties() called on it after this method is invoked.
        '''

        self.set_config_application( self.CONFIG_APPLICATION )

    #-- END abstract method init_config_properties() --#
    

    def initialize_from_params( self, params_IN, *args, **kwargs ):

        '''
        purpose: Accepts a dictionary of run-time parameters, uses them to
           initialize this instance.

        inheritance: This method overrides the abstract method of the same name in
           the ArticleCoder parent class.

        preconditions: None.

        postconditions: None.
        '''

        # declare variables
        me = "initialize_from_params"
        
        # update config properties with params passed in.
        self.update_config_properties( params_IN )
        
    #-- END abstract method initialize_from_params() --#
    

    def process_article( self, article_IN, coding_user_IN = None, *args, **kwargs ):

        '''
        purpose: After the ArticleCoder is initialized, this method accepts one
           article instance and codes it for sourcing.  In regards to articles,
           this class is stateless, so you can process many articles with a
           single instance of this object without having to reconfigure each
           time.
           
        Accepts:
        - article_IN - article instance we will be coding.
        - coding_user_IN - user instance for coder who coded this article.
        - KWARG_DATA_STORE_JSON_STRING = "data_store_json_string_IN" - JSON string that contains coding for article we are processing.
        - KWARG_ARTICLE_DATA_ID = "article_data_id_IN" - ID of article data for this coder's coding on this article, if we are updating, not creating new.
        - KWARG_REQUEST = "request_IN" - if manual coding via web form, request instance of form submission.
        - KWARG_RESPONSE_DICTIONARY = "response_dictionary_IN" - if manual coding via web form, response dictionary that will be used to render response sent back to user.
        
        inheritance: This method overrides the abstract method of the same name in
           the ArticleCoder parent class.

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
        data_store_json_string = ""
        article_data_id = -1
        request = None
        response_dictionary = ""
        article_data = None
        article_data_status_messages = "" 
        
        # get logger
        my_logger = self.get_logger()
        
        # get exception_helper
        my_exception_helper = self.get_exception_helper()
        
        # get parameters for calling process_data_store_json()
        data_store_json_string = kwargs[ self.KWARG_DATA_STORE_JSON_STRING ]
        article_data_id = kwargs[ self.KWARG_ARTICLE_DATA_ID ]
        request = kwargs[ self.KWARG_REQUEST ]
        response_dictionary = kwargs[ KWARG_RESPONSE_DICTIONARY ]
        
        # call process_data_store_json()
        article_data = self.process_data_store_json( article_IN,
                                                     coding_user_IN,
                                                     data_store_json_string,
                                                     article_data_id,
                                                     request,
                                                     response_dictionary )

        # got article data?
        if ( article_data is not None ):

            # yes - store it off.
            self.latest_article_data = article_data

            # got status messages?
            article_data_status_messages = article_data.status_messages
            if ( ( article_data_status_messages is not None ) and ( article_data_status_messages != "" ) ):

                # yes.  what do you know.  Return it.
                status_OUT = article_data_status_messages

            #-- END check to see if status messages in Article_Data instance --#

        else:

            # ERROR - should have gotten Article_Data instance back.
            status_OUT = self.STATUS_ERROR_PREFIX + "In " + me + "(): ERROR - call to process_data_store_json() did not return Article_Data."

        #-- END check to see if we got anything back. --#
        
        return status_OUT

    #-- END method process_article() --#
    

    def process_data_store_json( self,
                                 article_IN,
                                 coder_user_IN,
                                 data_store_json_string_IN,
                                 article_data_id_IN = None,
                                 request_IN = None,
                                 response_dictionary_IN = None ):
    
        '''
        Accepts:
        - article_IN - article instance for which we have coding data.
        - coder_user_IN - user instance for coder.
        - data_store_json_string_IN - JSON string that contains coding for article we are processing.
        - article_data_id_IN - optional - ID of article data for this coder's coding on this article, if we are updating, not creating new.
        - request_IN - optional - if manual coding via web form, request instance of form submission.
        - response_dictionary_IN - optional - if manual coding via web form, response dictionary that will be used to render response sent back to user.

        Purpose:
           This method accepts the above parameters.  It checks to make sure
           that there is an article, a coder user, and JSON.  It tries to find
           an existing Article_Data record for the current article and coder.
           If it finds 1, it updates it.  If it finds 0, it creates one.  If it
           finds more than 1, it returns an error message.  For each person,
           this method checks the type of person (author or subject/source).
           Regardless, it checks to see if there is a person ID.  If yes, it
           creates an Article_Person child appropriate to the person type
           (Article_Subject for subjects and sources, Article_Author for
           authors) and populates the instance from information in the person's
           JSON.  If source, looks up quotation in article and stores quote
           along with detailed information on where the quotation is located.
           Returns the Article_Data for the article with all coding saved and
           referenced from witin.

        Preconditions:
           Must already have looked up and loaded the article and coder user
           into instance variables.  Should have person store JSON to process,
           as well.

        Postconditions:
           Returns Article_Data instance.  If successful, it will be a
           fully-populated Article_Data instance that contains references to
           the people stored in the JSON passed in.  If error, will be an empty
           Article_Data instance with no primary key, and error messages will
           be stored in the 'status_messages' field, with multiple messages
           separated by semi-colons.

        '''
    
        # return reference
        article_data_OUT = None
    
        # declare variables
        me = "process_data_store_json"
        
        # declare variables - coding submission.
        is_ok_to_process = True
        status_message = ""
        status_message_list = None
        coder_user = None
        data_store_json_string = ""
        data_store_json = None

        # declare variables - look for existing Article_Data
        lookup_result = None
        lookup_status = ""
        lookup_status_message = ""
        is_existing_article_data = False
        current_article_data = None

        # declare variables - make new Article_Data if needed.
        current_article = None
        current_person = None

        # declare variables - store off JSON in a note.
        json_article_data_note = None
        
        # declare variables - loop over person list in JSON.
        person_list = []
        person_count = -1
        person_counter = -1
        
        # declare variables - OLD - structures to help check for removal.
        article_author_set_qs = None
        person_id_to_article_author_map = {}
        person_name_to_article_author_map = {}
        current_author_id = -1
        article_subject_set_qs = None
        person_name_to_article_subject_map = {}
        current_subject_id = -1
        current_person_instance = None
        current_person_id = -1
        
        # declare variables - remove obsolete - NEW - lists of IDs of Article_Person children
        #     (Authors and Subjects) that we started with, and then that were
        #     looked up in processing, so we can remove any we started with that
        #     weren't referenced in the current run.
        original_article_author_id_list = []
        processed_article_author_id_list = []
        deleted_article_author_list = []
        original_article_subject_id_list = []
        processed_article_subject_id_list = []
        deleted_article_subject_list = []
        
        # declare variables - remove obsolete - OLD - maps of ids and names to
        #     their corresponding Article_Person instances.  Didn't work.
        #.    Keeping them around since they might be interesting.
        person_id_to_article_author_map = {}
        person_name_to_article_author_map = {}
        person_id_to_article_subject_map = {}
        person_name_to_article_subject_map = {}

        # declare variables - get current person's information.
        person_type = ""
        person_name = ""
        fixed_person_name = ""
        title = ""
        person_organization = ""
        quote_text = ""
        person_id = -1
        article_person_id = -1
        
        # declare variables - for processing person.
        current_article_subject = None
        current_article_subject_mention = None
        current_article_subject_quotation = None
        current_article_author = None
        current_article_person = None
        current_person_status = ""
        current_full_name = ""
        
        # start with is_ok_to_process = True and an empty status_message_list
        is_ok_to_process = True
        status_message = ""
        status_message_list = []
    
        # got an article?
        if ( article_IN is not None ):
        
            # yes, we have an article.  Got a coder user?
            coder_user = coder_user_IN
            if ( coder_user is None ):

                # got a request?
                if ( request_IN is not None ):

                    coder_user = request_IN.user

                #-- END check to see if we have a request. --#

            #-- END check to see if we have a coder user passed in. --#

            # after all that, got a coder user?
            if ( coder_user is not None ):
            
                # yes - Got a JSON string?
                data_store_json_string = data_store_json_string_IN
                if ( ( data_store_json_string is not None ) and ( data_store_json_string != "" ) ):
                
                    self.output_debug( data_store_json_string, me, "====> Person Store JSON\n\n" )

                    # got a JSON string, convert to Python objects.
                    data_store_json = json.loads( data_store_json_string )

                    # !lookup Article_Data
                    lookup_result = self.lookup_article_data( article_IN, coder_user, article_data_id_IN )
                    
                    # what have we got?
                    if ( lookup_result is not None ):
                    
                        # get Article_Data, status, status message.
                        current_article_data = lookup_result.get( self.PROP_ARTICLE_DATA, None )
                        lookup_status = lookup_result.get( self.PROP_LOOKUP_STATUS, self.PROP_LOOKUP_STATUS_VALUE_ERROR )
                        lookup_status_message = lookup_result.get( self.PROP_STATUS_MESSAGE, None )
                        
                        # set processing flags.
                        if ( lookup_status == self.PROP_LOOKUP_STATUS_VALUE_ERROR ):
                        
                            # error.  Not OK to process...
                            is_ok_to_process = False
                            
                            # ...create error message...
                            status_message_list.append( lookup_status_message )

                            # ...and log it.
                            self.output_debug( lookup_status_message, me, indent_with_IN = "====>" )
                        
                        elif ( lookup_status == self.PROP_LOOKUP_STATUS_VALUE_MULTIPLE ):
                        
                            # also error.  Not OK to process...
                            is_ok_to_process = False
                            
                            # ...create error message...
                            status_message_list.append( lookup_status_message )

                            # ...and log it.
                            self.output_debug( lookup_status_message, me, indent_with_IN = "====>" )                            
                        
                        elif ( lookup_status == self.PROP_LOOKUP_STATUS_VALUE_NEW ):

                            # OK to process...
                            is_ok_to_process = True
                            
                            # ...and not an existing Article_Data instance
                            is_existing_article_data = False
                            
                        elif ( lookup_status == self.PROP_LOOKUP_STATUS_VALUE_EXISTING ):

                            # OK to process...
                            is_ok_to_process = True
                            
                            # ...and is an existing Article_Data instance
                            is_existing_article_data = True
                            
                        else:
                        
                            # error.  Not OK to process...
                            is_ok_to_process = False
                            
                            # ...create error message...
                            status_message = "ERROR - Unknown lookup_article_data() status " + lookup_status + ", message: " + lookup_status_message
                            status_message_list.append( status_message )

                            # ...and log it.
                            self.output_debug( status_message, me, indent_with_IN = "====>" )
                        
                            # unknown status.  Error.
                            
                        #-- END conditional over statuses. --#
                            
                    else:
                    
                        # no result - error.  Not OK to process...
                        is_ok_to_process = False
                        
                        # ...create error message...
                        status_message = "ERROR - Nothing came back from lookup_article_data() status."
                        status_message_list.append( status_message )

                        # ...and log it.
                        self.output_debug( status_message, me, indent_with_IN = "====>" )
                    
                        # unknown status.  Error.
                        
                    #-- END check to make sure we have a response. --#
                    
                    # ! is it OK to process JSON?
                    if ( is_ok_to_process == True ):

                        # got article data?
                        if ( current_article_data is not None ):
                        
                            # make list of Article_Subject and Article_Author
                            #     instances associated before processing.
                            article_author_set_qs = current_article_data.article_author_set.all()
                            original_article_author_id_list = list( article_author_set_qs.values_list( "id", flat = True ).order_by( "id" ) )
                            article_subject_set_qs = current_article_data.article_subject_set.all()
                            original_article_subject_id_list = list( article_subject_set_qs.values_list( "id", flat = True ).order_by( "id" ) )
                        
                            debug_message = "original_article_author_id_list = " + str( original_article_author_id_list ) + "; original_article_subject_id_list = " + str( original_article_subject_id_list )
                            self.output_debug( debug_message, me, "@@@@@@@@>" )                                        
        
                            # yes - store JSON in an Article_Data_Note.
                            json_article_data_note = Article_Data_Notes()
                            json_article_data_note.article_data = current_article_data
                            json_article_data_note.content_type = Article_Data_Notes.CONTENT_TYPE_JSON
                            json_article_data_note.content = data_store_json_string
                            json_article_data_note.source = self.coder_type + " - user " + str( coder_user )
                            json_article_data_note.content_description = "Person Store JSON (likely from manual coding via article-code view)."
                            json_article_data_note.save()
    
                            # store current_article_data in article_data_OUT.
                            article_data_OUT = current_article_data
    
                            # get list of people.
                            person_list = data_store_json[ self.DATA_STORE_PROP_PERSON_ARRAY ]
                            
                            # get count of persons
                            person_count = len( person_list )
                            
                            # got one or more people?
                            if ( person_count > 0 ):
                                                    
                                # !loop over persons
                                person_counter = 0
                                for current_person in person_list:
    
                                    # increment counter
                                    person_counter += 1
                                
                                    # check to see if it is an empty entry (happens
                                    #    when a person is removed during coding).
                                    if ( current_person is not None ):
                                
                                        # set up person details
                                        person_details = PersonDetails()
                                        
                                        # store all fields from current_person.
                                        person_details.update( current_person )
                                        
                                        # retrieve person information.
                                        person_type = person_details.get( self.DATA_STORE_PROP_PERSON_TYPE )
                                        person_name = person_details.get( self.DATA_STORE_PROP_PERSON_NAME )
                                        fixed_person_name = person_details.get( self.DATA_STORE_PROP_FIXED_PERSON_NAME )
                                        title = person_details.get( self.DATA_STORE_PROP_TITLE )
                                        person_organization = person_details.get( self.DATA_STORE_PROP_PERSON_ORGANIZATION )
                                        quote_text = person_details.get( self.DATA_STORE_PROP_QUOTE_TEXT )
                                        person_id = person_details.get( self.DATA_STORE_PROP_PERSON_ID )
                                        article_person_id = person_details.get( self.DATA_STORE_PROP_ARTICLE_PERSON_ID )
        
                                        #debug_message = "article_person_id = " + str( article_person_id )
                                        #self.output_debug( debug_message, me, "@@@@@@@@>" )                                        
        
                                        # also add in the article's newspaper.
                                        person_details[ self.PARAM_NEWSPAPER_INSTANCE ] = article_IN.newspaper
                                        
                                        # check person type to see what type we are processing.
                                        if ( ( person_type == self.PERSON_TYPE_SUBJECT )
                                             or ( person_type == self.PERSON_TYPE_SOURCE ) ):
        
                                            # translate the person_type value into 
                                            #    subject_type, store in details.
                                            if ( person_type == self.PERSON_TYPE_SUBJECT ):
                                            
                                                # subject, so not quoted - "mentioned".
                                                person_details[ self.PARAM_SUBJECT_TYPE ] = Article_Subject.SUBJECT_TYPE_MENTIONED
                                                
                                            elif ( person_type == self.PERSON_TYPE_SOURCE ):
                                            
                                                # source - so "quoted".
                                                person_details[ self.PARAM_SUBJECT_TYPE ] = Article_Subject.SUBJECT_TYPE_QUOTED
                                                
                                            #-- END check of person_type, for translation to subject_type. --#
                                        
                                            # ! Article_Subject
                                            # - includes creating mention for name.
                                            current_article_subject = self.process_subject_name( current_article_data,
                                                                                                 person_name,
                                                                                                 person_details_IN = person_details )
        
                                            # check to see if source
                                            current_article_subject.subject_type = Article_Subject.SUBJECT_TYPE_MENTIONED
                                            if ( person_type == self.PERSON_TYPE_SOURCE ):
        
                                                # set subject_type.
                                                current_article_subject.subject_type = Article_Subject.SUBJECT_TYPE_QUOTED
        
                                                # save source updates
                                                current_article_subject.save()
        
                                                # see if there is quote text.
                                                if ( ( quote_text is not None ) and ( quote_text != "" ) ):
        
                                                    # add quote to Article_Subject.
                                                    current_article_subject_quotation = self.process_quotation( article_IN, current_article_subject, quote_text )
        
                                                    # error?
                                                    if ( current_article_subject_quotation is None ):
        
                                                        # yup - output debug message.
                                                        debug_message = "Article_Coder.process_quotation() returned None - problem processing quote \"" + quote_text + "\".  See log for more details."
                                                        status_message_list.append( debug_message )
                                                        debug_message = "ERROR: " + debug_message
                                                        self.output_debug( debug_message, me )
        
                                                    #-- END check to see if error processing quotation --#
        
                                                #-- END check to see if quote text --#
        
                                            #-- END check to see if source --#
        
                                            # save source updates - should not need save.
                                            current_article_subject.save()
                                            
                                            # ! update subject data for removal processing.
                                            current_person_instance = current_article_subject.person
                                            current_person_id = current_person_instance.id
                                            person_id_to_article_subject_map[ current_person_id ] = current_article_subject
                                            person_name_to_article_subject_map[ person_name ] = current_article_subject
        
                                            # Add ID of this Article_Subject to the processed list.
                                            processed_article_subject_id_list.append( current_article_subject.id )
                                                    
                                            # store Article_Subject instance in Article_Person reference.
                                            current_article_person = current_article_subject
                                            
                                        elif ( person_type == self.PERSON_TYPE_AUTHOR ):
                                        
                                            # ! Article_Author
                                            current_article_author = self.process_author_name( current_article_data,
                                                                                               person_name,
                                                                                               person_details_IN = person_details )
                            
                                            # ! update author data for removal processing.
                                            current_person_instance = current_article_author.person
                                            current_person_id = current_person_instance.id
                                            person_id_to_article_author_map[ current_person_id ] = current_article_author
                                            person_name_to_article_author_map[ person_name ] = current_article_author
    
                                            # Add ID of this Article_Author to the processed list.
                                            processed_article_author_id_list.append( current_article_author.id )
                                                    
                                            # store Article_Author instance in Article_Person reference.
                                            current_article_person = current_article_author
        
                                        #-- END check to see person type --#
        
                                        # set name
                                        current_article_person.name = person_name
        
                                        # check status
                                        current_person_status = current_article_person.match_status
        
                                        # got a status?
                                        if ( ( current_person_status is not None ) and ( current_person_status != "" ) ):
        
                                            # success?
                                            if ( current_person_status != self.STATUS_SUCCESS ):
        
                                                # error.  Add message to status list.
                                                status_message_list.append( current_person_status )
        
                                            #-- END check of person status --#
        
                                        #-- END check if current person has status --#
                                        
                                    else:
                                    
                                        # empty person list entry.  Make a note and
                                        #    move on.
                                        debug_message = "person_list item " + str( person_counter ) + " is None.  Moving on."
                                        # status_message_list.append( debug_message )
                                        debug_message = "WARNING: " + debug_message
                                        self.output_debug( debug_message, me )
                                    
                                    #-- END check to see if empty entry in person list --#
    
                                #-- END loop over persons --#
                                
                                # ! TODO - removal check
                                # Remove any Article_Author or Article_Subject
                                #     whose ID is in the original list but not
                                #     in the processed list.
                                
                                # ! removals - Article_Author
                                deleted_article_author_list = self.winnow_orphaned_records(
                                        original_article_author_id_list,
                                        processed_article_author_id_list,
                                        Article_Author
                                    )
                                
                                # ! removals - Article_Subject
                                deleted_article_subject_list = self.winnow_orphaned_records(
                                        original_article_subject_id_list,
                                        processed_article_subject_id_list,
                                        Article_Subject
                                    )

                                '''                                    
                                # authors
                                for current_article_author in current_article_data.article_author_set.all():
                                
                                    # get person ID and full name.
                                    current_person_id = current_article_author.person.id
                                    current_full_name = current_article_author.name
                                    
                                    # look for either ID or name to be in one of our
                                    #    dictionaries.
                                    if ( ( current_full_name not in person_name_to_article_author_map )
                                        and ( current_person_id not in person_id_to_article_author_map ) ):
                                        
                                        debug_message = "in " + me + "(): removal check - deleting article_author: " + str( current_article_author )
                                        self.output_debug( debug_message, me, "========> " )
                                        
                                        # not in either map.  Delete.
                                        current_article_author.delete()
                                        
                                    #-- END look for author in processed dictionaries --#
                                
                                #-- END loop over related Article_Author instances --#
                                
                                # subjects
                                for current_article_subject in current_article_data.article_subject_set.all():
                                
                                    # get person ID and full name.
                                    current_person_id = current_article_subject.person.id
                                    current_full_name = current_article_subject.name
                                    
                                    # look for either ID or name to be in one of our
                                    #    dictionaries.
                                    if ( ( current_full_name not in person_name_to_article_subject_map )
                                        and ( current_person_id not in person_id_to_article_subject_map ) ):
                                        
                                        debug_message = "in " + me + "(): removal check - deleting Article_Subject: " + str( current_article_subject )
                                        self.output_debug( debug_message, me, "========> " )
                                        
                                        # not in either map.  Delete.
                                        current_article_subject.delete()
                                        
                                    #-- END look for subject in processed dictionaries --#
                                
                                #-- END loop over related Article_Subject instances --#
                                '''
                                
                            #-- END check to see if there are any persons. --#
                            
                        else:
                        
                            # No article data instance.  Can't process.  Add
                            #    message to list, log it.
                            status_message = "ERROR - Even though Article_Data lookup indicated success, no Article_Data.  Don't know what to tell you."
                            status_message_list.append( status_message )
                            self.output_debug( status_message, me, "====> " )
                            article_data_OUT = None
                        
                        #-- END check to make sure we have article data --#
                                                    
                    else:

                        # Not OK to process.  Assume messages that explain why
                        #    have been placed in status_message_list.
                        pass

                    #-- END check to see if is_ok_to_process == True --#
    
                else:
                
                    # no JSON - can't process.  Add message to list, log it.
                    status_message = "ERROR - No JSON passed in - must have data in JSON to process that data."
                    status_message_list.append( status_message )
                    self.output_debug( status_message, me, "====> " )
                    article_data_OUT = None
                
                #-- END check to see if JSON string passed in.
                
            else:
            
                # no coder user?  That is an odd error.
                status_message = "ERROR - No coder user passed in - must have a coder user."
                status_message_list.append( status_message )
                self.output_debug( status_message, me, "====> " )
                article_data_OUT = None
                
            #-- END check to see if coder passed in. --#
            
        else:
        
            # no article - can't process.
            status_message = "ERROR - No article passed in - must have an article to code an article."
            status_message_list.append( status_message )
            self.output_debug( status_message, me, "====> " )
            article_data_OUT = None
        
        #-- END check to see if article ID passed in.

        # got an Article_Data instance (no likely means error)?
        if ( article_data_OUT is None ):

            # OK... create one.
            article_data_OUT = Article_Data()

        #-- END check to see if Article_Data instance. --#

        # got status messages?
        if ( ( status_message_list is not None ) and ( len( status_message_list ) > 0 ) ):

            # we do.  Convert to semi-colon-delimited list, place in
            #    Article_Data.status_messages
            # create new empty Article_Data
            status_message = ";".join( status_message_list )

            # Overwrite existing status_messages.
            article_data_OUT.status_messages = status_message

        else:

            # no status messages, so status is success!
            article_data_OUT.status_messages = self.STATUS_SUCCESS

        #-- END check to see if status messages. --#
    
        return article_data_OUT
    
    #-- END function process_data_store_json() --#
    
    def winnow_orphaned_records( self, original_ID_list_IN, updated_ID_list_IN, class_IN, *args, **kwargs ):
        
        '''
        For objects of a given class (class_IN), accepts list of IDs originally
            associated with an entity, an updated list of IDs that are currently
            associated with that entity, and the class of the object we are
            winnowing.  For each ID in the original list, checks to see if it is
            in the updated list.  If not, looks up the instance by the ID using
            class_IN, then delete()'s the instance.  Returns list of instances
            that were deleted, post-delete.
            
        Postconditions: Records whose IDs are in the original list and not in
            the updated list will be permanently deleted after this routine is
            invoked.  Returns list of instances that were deleted.
        '''

        # return reference
        deleted_instances_list_OUT = []
        
        # declare variables
        me = "winnow_orphaned_records"
        original_id_count = -1
        original_id_counter = -1
        current_ID = None
        instance_qs = None
        current_instance = None
        deleted_id_list = []
        deleted_instance_list = []
        debug_message = ""
        
        debug_message = "Winnowing class " + str( class_IN ) + "\n- original_id_list_IN = " + str( original_ID_list_IN ) + "\n- updated_ID_list_IN = " + str( updated_ID_list_IN )
        self.output_debug( debug_message, me, "~~~~" )
        
        # got an original list?
        if ( original_ID_list_IN is not None ):
            
            # is it a list?
            if ( isinstance( original_ID_list_IN, list ) == True ):
                
                # does it have anything in it?
                original_id_count = len( original_ID_list_IN )
                if ( original_id_count > 0 ):
                
                    # yes - For each item, check to see if the ID stored in the list is
                    #     in the updated_ID_list_IN.
                    original_id_counter = 0
                    for current_ID in original_ID_list_IN:
                        
                        # increment counter
                        original_id_counter += 1
        
                        debug_message = "Original ID #" + str( original_id_counter ) + " = " + str( current_ID )
                        # self.output_debug( debug_message, me, "~~~~~~~~" )
                    
                        # check to see if it is in updated list.
                        if ( current_ID not in updated_ID_list_IN ):
                        
                            debug_message += " NOT IN updated_ID_list_IN ( " + str( updated_ID_list_IN ) + " )"
                            self.output_debug( debug_message, me, "~~~~~~~~" )
                    
                            # wrap in try, in case problem with class, or record DNE.
                            try:
                            
                                # it is not in the list.  Look up the instance...
                                instance_qs = class_IN.objects.all()                    
                                current_instance = instance_qs.get( pk = current_ID )
                                
                                # ...delete it...
                                current_instance.delete()
                                
                                # ...and add it to the deleted lists.
                                deleted_id_list.append( current_ID )
                                deleted_instance_list.append( current_instance )
                                
                                debug_message = "Deleted record with ID " + str( current_ID ) + " in class " + str( class_IN )
                                self.output_debug( debug_message, me, "~~~~~~~~~~~~" )
        
                            except MultipleObjectsReturned as mor_exception:
                            
                                debug_message = "Multiple matches for ID " + str( current_ID ) + " in class " + str( class_IN )
                                self.output_debug( debug_message, me, "~~~~~~~~~~~~" )
        
                            except class_IN.DoesNotExist as dne_exception:
        
                                debug_message = "No match for ID " + str( current_ID ) + " in class " + str( class_IN )
                                self.output_debug( debug_message, me, "~~~~~~~~~~~~" )
        
                            except Exception as e:
                                
                                debug_message = "Unexpected exception caught: " + str( e ) + " processing ID " + str( current_ID ) + " and class " + str( class_IN )
                                self.output_debug( debug_message, me, "~~~~~~~~~~~~" )
                                
                            #-- END try...except around lookup of instance, and then delete() --#
                            
                        else:
                            
                            debug_message += " IN updated_ID_list_IN ( " + str( updated_ID_list_IN ) + " ) - moving on."
                            self.output_debug( debug_message, me, "~~~~~~~~" )
        
                        #-- END check to see if current original ID is in updated list --#
        
                    #-- END loop over IDs in original list. --#

                else:
                    
                    debug_message = "updated_ID_list_IN ( " + str( updated_ID_list_IN ) + " ) has nothing in it ( " + str( original_id_count ) + " )."
                    self.output_debug( debug_message, me, "~~~~" )            
                    
                #-- END check to see if there is anything in "original" list --#
                    
            else:
                
                debug_message = "updated_ID_list_IN ( " + str( updated_ID_list_IN ) + " ) is not a list ( type = " + str( type( updated_ID_list_IN ) ) + " )."
                self.output_debug( debug_message, me, "~~~~" )            
                
            #-- END check to see if the "original" list is of type list --#
            
        else:
            
            debug_message = "updated_ID_list_IN ( " + str( updated_ID_list_IN ) + " ) is None."
            self.output_debug( debug_message, me, "~~~~" )            
            
        #-- END check to see if there is an "original" list --#
        
        # return instance list
        deleted_instances_list_OUT = deleted_instance_list

        return deleted_instances_list_OUT
        
    #-- END method winnow_orphaned_records() --#
    

#-- END class ManualArticleCoder --#