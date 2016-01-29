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

# python utilities
from python_utilities.django_utils.django_string_helper import DjangoStringHelper
from python_utilities.json.json_helper import JSONHelper
from python_utilities.network.http_helper import Http_Helper
from python_utilities.sequences.sequence_helper import SequenceHelper

# sourcenet classes

# models
from sourcenet.models import Alternate_Subject_Match
from sourcenet.models import Article_Data
from sourcenet.models import Article_Data_Notes
from sourcenet.models import Article_Subject
from sourcenet.models import Article_Subject_Mention
from sourcenet.models import Article_Subject_Quotation
from sourcenet.models import Article_Text
from sourcenet.models import Person

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
    
    # config application
    CONFIG_APPLICATION = "Manual_Coding"

    # person types
    PERSON_TYPE_SUBJECT = "subject"
    PERSON_TYPE_SOURCE = "source"
    PERSON_TYPE_AUTHOR = "author"

    # subject_type to person type dictionary
    SUBJECT_TYPE_TO_PERSON_TYPE_MAP = {}
    SUBJECT_TYPE_TO_PERSON_TYPE_MAP[ Article_Subject.SUBJECT_TYPE_MENTIONED ] = PERSON_TYPE_SUBJECT
    SUBJECT_TYPE_TO_PERSON_TYPE_MAP[ Article_Subject.SUBJECT_TYPE_QUOTED ] = PERSON_TYPE_SOURCE    

    # kwarg parameter names
    KWARG_DATA_STORE_JSON_STRING = "data_store_json_string_IN"
    KWARG_ARTICLE_DATA_ID = "article_data_id_IN"
    KWARG_REQUEST = "request_IN"
    KWARG_RESPONSE_DICTIONARY = "response_dictionary_IN"

    # person store JSON property names
    DATA_STORE_PROP_PERSON_ARRAY = "person_array"
    DATA_STORE_PROP_PERSON_TYPE = "person_type"
    DATA_STORE_PROP_PERSON_NAME = "person_name"
    DATA_STORE_PROP_TITLE = "title"
    DATA_STORE_PROP_QUOTE_TEXT = "quote_text"
    DATA_STORE_PROP_PERSON_ID = "person_id"
    DATA_STORE_PROP_NEXT_PERSON_INDEX = "next_person_index"
    DATA_STORE_PROP_NAME_TO_PERSON_INDEX_MAP = "name_to_person_index_map"
    DATA_STORE_PROP_ID_TO_PERSON_INDEX_MAP = "id_to_person_index_map"
    DATA_STORE_PROP_STATUS_MESSAGE_ARRAY = "status_message_array"
    DATA_STORE_PROP_LATEST_PERSON_INDEX = "latest_person_index"


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
    # Constructor
    #============================================================================


    def __init__( self ):

        # call parent's __init__() - I think...
        super( ManualArticleCoder, self ).__init__()
        
        # declare variables
        
        # set application string (for LoggingHelper parent class: (LoggingHelper -->
        #    BasicRateLimited --> ArticleCoder --> OpenCalaisArticleCoder).
        self.set_logger_name( "sourcenet.article_coding.manual_coding.manual_article_coder" )
        
        # items for processing a given JSON response - should be updated with
        #    every new article coded.
        
        # coder type (defaults to self.CONFIG_APPLICATION).
        self.coder_type = self.CONFIG_APPLICATION

        # most recent Article_Data instance.
        self.latest_article_data = None
        
    #-- END method __init__() --#


    #============================================================================
    # Class methods
    #============================================================================


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
        current_person = None
        current_person_type = ""
        current_person_name = ""
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

            # loop
            for current_author in article_author_qs:

                # get current person
                current_person = current_author.person

                # set values for person from instance.

                # ==> person_type
                current_person_type = cls.PERSON_TYPE_AUTHOR
                
                # ==> person_name
                current_person_name = JSONHelper.escape_json_value( current_person.get_name_string() )
                
                # ==> title
                current_title = JSONHelper.escape_json_value( current_author.organization_string )
                
                # ==> quote_text
                current_quote_text = ""
                
                # ==> person_id
                current_person_id = current_person.id

                # create person dictionary
                current_person_dict = {}
                current_person_dict[ cls.DATA_STORE_PROP_PERSON_TYPE ] = current_person_type
                current_person_dict[ cls.DATA_STORE_PROP_PERSON_NAME ] = current_person_name
                current_person_dict[ cls.DATA_STORE_PROP_TITLE ] = current_title
                current_person_dict[ cls.DATA_STORE_PROP_QUOTE_TEXT ] = current_quote_text
                current_person_dict[ cls.DATA_STORE_PROP_PERSON_ID ] = current_person_id

                # add to lists and dicts.
                person_list.append( current_person_dict )
                current_index += 1
                next_index += 1
                name_to_person_index_dict[ current_person_name ] = current_index
                id_to_person_index_dict[ current_person_id ] = current_index

            #-- END loop over authors --#

            # then get list of Article_Subjects.
            article_subject_qs = article_data_IN.article_subject_set.all()

            # loop
            for current_subject in article_subject_qs:

                # get current person
                current_person = current_subject.person
                
                # got a person?  Could be court records, etc.
                if ( current_person is not None ):

                    # set values for person from instance.
    
                    # ==> person_type
                    current_subject_type = current_subject.subject_type
                    current_person_type = cls.SUBJECT_TYPE_TO_PERSON_TYPE_MAP[ current_subject_type ]
                    
                    # ==> name
                    current_person_name = JSONHelper.escape_json_value( current_person.get_name_string() )
                    
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
                    current_person_dict[ cls.DATA_STORE_PROP_PERSON_NAME ] = current_person_name
                    current_person_dict[ cls.DATA_STORE_PROP_TITLE ] = current_title
                    current_person_dict[ cls.DATA_STORE_PROP_PERSON_ID ] = current_person_id
                    current_person_dict[ cls.DATA_STORE_PROP_QUOTE_TEXT ] = current_quote_text
    
                    # add to lists and dicts.
                    person_list.append( current_person_dict )
                    current_index += 1
                    next_index += 1
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
        article_data_id = -1
        person_list = []
        person_count = -1
        person_counter = -1
        coder_user = None
        person_type = ""
        person_name = ""
        title = ""
        quote_text = ""
        person_id = -1
        is_existing_article_data = False
        article_data_qs = None
        article_data_count = -1
        current_article_data = None
        json_article_data_note = None
        current_article = None
        current_person = None
        person_type = ""
        person_name = ""
        title = ""
        quote_text = ""
        person_id = ""
        current_article_subject = None
        current_article_subject_mention = None
        current_article_subject_quotation = None
        current_article_author = None
        current_article_person = None
        current_person_status = ""

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

                    # see if there is an existing Article_Data instance for this
                    #    user and article.
                    is_existing_article_data = False
                    article_data_qs = Article_Data.objects.filter( coder = coder_user )
                    article_data_qs = article_data_qs.filter( article = article_IN )

                    # How many matches?
                    try:

                        # use .get() to retrieve single instance from QuerySet.
                        current_article_data = article_data_qs.get()

                        # set is_existing_article_data to True
                        is_existing_article_data = True

                    except Exception as e:

                        # hmmm.  Either no matches, or more than one.
                        article_data_count = article_data_qs.count()
                        if ( article_data_count > 1 ):

                            # more than one.  See if we have an ID.
                            if ( ( article_data_id_IN is not None ) and ( article_data_id_IN != "" ) and ( article_data_id_IN > 0 ) ):
                            
                                # we have an Article_Data ID.  look up.
                                try:
            
                                    # use exception handling to see if record already exists.
                                    
                                    # filter on ID
                                    article_data_qs = Article_Data.objects.filter( pk = article_data_id_IN )
                                    
                                    # then use get() to make sure this ID belongs to the current user.
                                    current_article_data = article_data_qs.get( coder = coder_user )

                                    # set is_existing_article_data to True
                                    is_existing_article_data = True
                            
                                except Exception as e:
                                
                                    # not found.  Set current_article_data to None...
                                    current_article_data = None

                                    # ...tell logic it isn't OK to process...
                                    is_ok_to_process = False

                                    # ...create error message...
                                    status_message = "Article_Data record for ID passed in ( " + str( article_data_id_IN ) + " ) either does not exist or does not belong to the current user: " + str( coder_user )
                                    status_message_list.append( status_message )

                                    # ...and log it.
                                    self.output_debug( status_message, me, indent_with_IN = "====>" )
                            
                                #-- END check to see if we can find existing article data. --#
                                
                            else:

                                # Too many Article_Data instances for user, and
                                #    no way to choose among them.

                                # not OK to process.
                                is_ok_to_process = False

                                # log and store status message.
                                status_message = "Found " + str( article_data_qs.count() ) + " Article_Data records for user ( " + str( coder_user ) + " ) and article ( " + str( article_IN ) + " )"
                                status_message_list.append( status_message )
                                self.output_debug( status_message, me, "====> " )
                                current_article_data = None

                            #-- END check to see if article data already exists. --#

                        else:

                            # No Article_Data found.  OK to process, set variable to None.
                            current_article_data = None

                            # set is_existing_article_data to False.
                            is_existing_article_data = False

                        #-- END check to see if 0 or > 1 Article_Data found for current user. --#

                    #-- END try...except around initial attempt to pull in Article_Data for current user. --#

                    # is it OK to process?
                    if ( is_ok_to_process == True ):

                        # got article data?
                        if ( current_article_data is None ):
                        
                            # no Article_Data.  Create a new record.
                            current_article_data = Article_Data()
                            
                            # get article for ID, store in Article_Data.
                            current_article = article_IN
                            current_article_data.article = current_article
                            current_article_data.coder = coder_user
                        
                            # Save off Aricle_Data instance - current_article_data.save()
                            current_article_data.save()

                        #-- END check to see if Article_Data instance. --#

                        # add Article_Data_Notes with JSON.
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
                            
                                    # retrieve person information.
                                    person_type = current_person.get( self.DATA_STORE_PROP_PERSON_TYPE )
                                    person_name = current_person.get( self.DATA_STORE_PROP_PERSON_NAME )
                                    title = current_person.get( self.DATA_STORE_PROP_TITLE )
                                    quote_text = current_person.get( self.DATA_STORE_PROP_QUOTE_TEXT )
                                    person_id = current_person.get( self.DATA_STORE_PROP_PERSON_ID )
    
                                    # set up person details
                                    person_details = {}
                                    person_details[ self.PARAM_NEWSPAPER_INSTANCE ] = article_IN.newspaper
                                    
                                    # got a title?
                                    if ( ( title is not None ) and ( title != "" ) ):
                                        
                                        # we do.  store it in person_details.
                                        person_details[ self.PARAM_TITLE ] = title
                                        
                                    #-- END check to see if title --#
                                    
                                    # check person type to see what type we are processing.
                                    if ( ( person_type == self.PERSON_TYPE_SUBJECT )
                                         or ( person_type == self.PERSON_TYPE_SOURCE ) ):
    
                                        # Article_Subject
                                        current_article_subject = self.process_subject_name( current_article_data,
                                                                                             person_name,
                                                                                             person_details_IN = person_details,
                                                                                             subject_person_id_IN = person_id )
    
                                        # check to see if source
                                        current_article_subject.subject_type = Article_Subject.SUBJECT_TYPE_MENTIONED
                                        if ( person_type == self.PERSON_TYPE_SOURCE ):
    
                                            # set subject_type.
                                            current_article_subject.subject_type = Article_Subject.SUBJECT_TYPE_QUOTED
    
                                            # save source updates
                                            current_article_subject.save()
    
                                            # add name mention to Article_Subject.
                                            current_article_subject_mention = self.process_mention( article_IN, current_article_subject, person_name )
    
                                            # error?
                                            if ( current_article_subject_mention is None ):
    
                                                # yup - output debug message.
                                                debug_message = "Article_Coder.process_mention() returned None - problem processing name mention \"" + person_name + "\".  See log for more details."
                                                status_message_list.append( debug_message )
                                                debug_message = "ERROR: " + debug_message
                                                self.output_debug( debug_message, me )
    
                                            #-- END check to see if error processing quotation --#
    
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
    
                                        # store Article_Subject instance in Article_Person reference.
                                        current_article_person = current_article_subject
    
                                    elif ( person_type == self.PERSON_TYPE_AUTHOR ):
                                    
                                        # Add organization string to person_details
                                        #    for author, this is in the "title"
                                        #    field.
                                        person_details[ self.PARAM_AUTHOR_ORGANIZATION_STRING ] = title
                                    
                                        # Article_Author
                                        current_article_author = self.process_author_name( current_article_data,
                                                                                           person_name,
                                                                                           author_organization_IN = title,
                                                                                           author_person_id_IN = person_id,
                                                                                           person_details_IN = person_details )
                        
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
                            
                        #-- END check to see if there are any persons. --#
                        
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


#-- END class ManualArticleCoder --#