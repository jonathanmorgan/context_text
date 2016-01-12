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

    # kwarg parameter names
    KWARG_PERSON_STORE_JSON_STRING = "person_store_json_string_IN"
    KWARG_ARTICLE_DATA_ID = "article_data_id_IN"
    KWARG_REQUEST = "request_IN"
    KWARG_RESPONSE_DICTIONARY = "response_dictionary_IN"

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
        - KWARG_PERSON_STORE_JSON_STRING = "person_store_json_string_IN" - JSON string that contains coding for article we are processing.
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
        person_store_json_string = ""
        article_data_id = -1
        request = None
        response_dictionary = ""
        article_data = None
        article_data_status_messages = "" 
        
        # get logger
        my_logger = self.get_logger()
        
        # get exception_helper
        my_exception_helper = self.get_exception_helper()
        
        # get parameters for calling process_person_store_json()
        person_store_json_string = kwargs[ self.KWARG_PERSON_STORE_JSON_STRING ]
        article_data_id = kwargs[ self.KWARG_ARTICLE_DATA_ID ]
        request = kwargs[ self.KWARG_REQUEST ]
        response_dictionary = kwargs[ KWARG_RESPONSE_DICTIONARY ]
        
        # call process_person_store_json()
        article_data = self.process_person_store_json( article_IN,
                                                       coding_user_IN,
                                                       person_store_json_string,
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
            status_OUT = self.STATUS_ERROR_PREFIX + "In " + me + "(): ERROR - call to process_person_store_json() did not return Article_Data."

        #-- END check to see if we got anything back. --#
        
        return status_OUT

    #-- END method process_article() --#
    

    def process_person_store_json( self,
                                   article_IN,
                                   coder_user_IN,
                                   person_store_json_string_IN,
                                   article_data_id_IN,
                                   request_IN,
                                   response_dictionary_IN ):
    
        '''
        Accepts:
        - article_IN - article instance for which we have coding data.
        - coder_user_IN - user instance for coder.
        - person_store_json_string_IN - JSON string that contains coding for article we are processing.
        - article_data_id_IN - ID of article data for this coder's coding on this article, if we are updating, not creating new.
        - request_IN - if manual coding via web form, request instance of form submission.
        - response_dictionary_IN - if manual coding via web form, response dictionary that will be used to render response sent back to user.        
        '''
    
        # return reference
        article_data_OUT = None
    
        # declare variables
        me = "process_person_store_json"
        
        # declare variables - coding submission.
        coder_user = None
        person_store_json_string = ""
        person_store_json = None
        article_data_id = -1
        person_list = []
        person_count = -1
        coder_user = None
        person_type = ""
        person_name = ""
        name_and_title = ""
        quote_text = ""
        person_id = -1
        current_article_data = None
        current_article = None
        current_person = None
        person_type = ""
        person_name = ""
        name_and_title = ""
        quote_text = ""
        person_id = ""
        current_article_subject = None
        current_article_author = None
        current_article_person = None
        current_person_status = ""
    
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
                person_store_json_string = person_store_json_string_IN
                if ( ( person_store_json_string is not None ) and ( person_store_json_string != "" ) ):
                
                    # got a JSON string, convert to Python objects.
                    person_store_json = json.loads( person_store_json_string )
                    
                    # get list of people.
                    person_list = person_store_json[ "person_array" ]
                    
                    # get count of persons
                    person_count = len( person_list )
                    
                    # got one or more people?
                    if ( person_count > 0 ):
                    
                        # yes - Got an Article_Data ID?
                        if ( ( article_data_id_IN is not None ) and ( article_data_id_IN != "" ) and ( article_data_id_IN > 0 ) ):
                        
                            # we have an Article_Data ID.  look up.
                            try:
        
                                # use exception handling to see if record already exists.
                                
                                # filter on ID
                                current_article_data = Article_Data.objects.filter( pk = article_data_id_IN )
                                
                                # then use get() to make sure this ID belongs to the current user.
                                current_article_data = current_article_data.get( coder = coder_user )
                        
                            except Exception as e:
                            
                                # not found.  Set current_article_data tp None.
                                current_article_data = None
                        
                            #-- END check to see if we can find existing article data. --#
                            
                        #-- END check to see if article data already exists. --#
                        
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
                    
                        # !TODO - loop over persons
                        # loop over persons
                        for current_person in person_list:
                        
                            # retrieve person information.
                            person_type = current_person.get( "person_type" )
                            person_name = current_person.get( "person_name" )
                            name_and_title = current_person.get( "name_and_title" )
                            quote_text = current_person.get( "quote_text" )
                            person_id = current_person.get( "person_id" )

                            # set up person details
                            person_details = {}
                            person_details[ self.PARAM_NEWSPAPER_INSTANCE ] = current_article.newspaper
                            
                            # check person type to see what type we are processing.
                            if ( ( person_type == self.PERSON_TYPE_SUBJECT )
                                 or ( person_type == self.PERSON_TYPE_SOURCE ) ):

                                # Article_Subject
                                person_details = {}
                                person_details[ self.PARAM_NEWSPAPER_INSTANCE ] = current_article.newspaper
                                current_article_subject = self.process_subject_name( current_article_data,
                                                                                     person_name,
                                                                                     person_details_IN = person_details,
                                                                                     subject_person_id_IN = person_id )

                                # check to see if source
                                if ( person_type == self.PERSON_TYPE_SOURCE ):

                                    # set subject_type.
                                    current_article_subject.subject_type = Article_Subject.SUBJECT_TYPE_QUOTED

                                    # see if there is quote text.
                                    if ( ( quote_text is not None ) and ( quote_text != "" ) ):

                                        # !TODO - add quote to Article_Subject.
                                        pass

                                    #-- END check to see if quote text --#

                                    # save source updates
                                    current_article_subject.save()

                                #-- END check to see if source --#

                                # store Article_Subject instance in Article_Person reference.
                                current_article_person = current_article_subject

                            elif ( person_type == self.PERSON_TYPE_AUTHOR ):
                            
                                # Article_Author
                                current_article_author = self.process_author_name( current_article_data,
                                                                                   person_name,
                                                                                   author_organization_IN = name_and_title,
                                                                                   author_person_id_IN = person_id,
                                                                                   person_details_IN = person_details )
                
                                # store Article_Author instance in Article_Person reference.
                                current_article_person = current_article_author

                            #-- END check to see person type --#
                            
                            # check status
                            current_person_status = current_article_person.match_status

                            # got a status?
                            if ( ( current_person_status is not None ) and ( current_person_status != "" ) ):

                                # success?
                                if ( current_person_status != self.STATUS_SUCCESS ):

                                    # error.  What to do?
                                    pass

                                #-- END check of person status --#

                            #-- END check if current person has status --#

                        #-- END loop over persons --#
                        
                    #-- END check to see if there are any persons. --#
                    
                    # store JSON string in response dictionary
                    response_dictionary_IN[ 'person_store_json' ] = person_store_json_string    
    
                else:
                
                    # no JSON - can't process.
                    self.output_debug( "ERROR - No JSON passed in - must have data in JSON to process that data...", me, "====> " )
                    article_data_OUT = None
                
                #-- END check to see if JSON string passed in.
                
            else:
            
                # no coder user?  That is an odd error.
                self.output_debug( "ERROR - No coder user passed in - must have a coder user...", me, "====> " )
                article_data_OUT = None
                
            #-- END check to see if coder passed in. --#
            
        else:
        
            # no article ID - can't process.
            self.output_debug( "ERROR - No article ID passed in - must have an article ID to code an article...", me, "====> " )
            article_data_OUT = None
        
        #-- END check to see if article ID passed in.
    
        return article_data_OUT
    
    #-- END function process_person_store_json() --#


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