from __future__ import unicode_literals

'''
Copyright 2010-present (2016) Jonathan Morgan

This file is part of http://github.com/jonathanmorgan/sourcenet.

sourcenet is free software: you can redistribute it and/or modify it under the terms of the GNU Lesser General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.

sourcenet is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.

You should have received a copy of the GNU Lesser General Public License along with http://github.com/jonathanmorgan/sourcenet. If not, see http://www.gnu.org/licenses/.
'''

__author__ = "jonathanmorgan"
__date__ = "$November 26, 2014 3:03:35 PM$"

if __name__ == "__main__":
    print( "Hello World" )

#===============================================================================
# imports (in alphabetical order by package, then by name)
#===============================================================================

# python libraries
from abc import ABCMeta, abstractmethod
import calendar
import datetime
import logging
#import copy
import re

# six - python 2 + 3
import six

# Django imports
from django.contrib.auth.models import User

# django config, for pulling in any configuration needed to connect to APIs, etc.

# import basic django configuration application.
from django_config.models import Config_Property

# django exception classes
from django.core.exceptions import MultipleObjectsReturned

# python_utilities
from python_utilities.exceptions.exception_helper import ExceptionHelper
from python_utilities.rate_limited.basic_rate_limited import BasicRateLimited
from python_utilities.sequences.sequence_helper import SequenceHelper
from python_utilities.strings.string_helper import StringHelper

# Import the classes for our SourceNet application
from sourcenet.models import Article
from sourcenet.models import Article_Author
from sourcenet.models import Article_Data
from sourcenet.models import Article_Person
from sourcenet.models import Article_Subject
from sourcenet.models import Article_Subject_Mention
from sourcenet.models import Article_Subject_Quotation
from sourcenet.models import Article_Text
from sourcenet.models import Person
from sourcenet.models import Person_External_UUID
from sourcenet.models import Person_Newspaper
from sourcenet.shared.person_details import PersonDetails
from sourcenet.shared.sourcenet_base import SourcenetBase

#================================================================================
# Shared variables and functions
#================================================================================


#===============================================================================
# classes (in alphabetical order by name)
#===============================================================================

class ArticleCoder( BasicRateLimited ):

    
    #----------------------------------------------------------------------------
    # META!!!
    #----------------------------------------------------------------------------

    
    __metaclass__ = ABCMeta


    #----------------------------------------------------------------------------
    # CONSTANTS-ish
    #----------------------------------------------------------------------------


    # status constants
    STATUS_SUCCESS = "Success!"    
    STATUS_ERROR_PREFIX = "Error: "
    STATUS_LIST_DELIMITER = " || "

    # DEPRECATED STATUSES - DO NOT USE IN NEW CODE
    STATUS_OK = "OK!"

    # debug
    DEBUG_FLAG = True
    
    # logging
    LOGGER_NAME = "sourcenet.article_coding.article_coder"
    
    # config parameters
    PARAM_AUTOPROC_ALL = "autoproc_all"
    PARAM_AUTOPROC_AUTHORS = "autoproc_authors"
    
    # author string processing
    REGEX_BEGINS_WITH_BY = re.compile( r'^\s*BY\s+', re.IGNORECASE )
    REGEX_CONTAINS_AND = re.compile( r'\s+AND\s+', re.IGNORECASE )
    
    # PARAMS for update_person()
    PARAM_PERSON_ID = PersonDetails.PROP_NAME_PERSON_ID
    PARAM_PERSON_NAME = PersonDetails.PROP_NAME_PERSON_NAME
    PARAM_FIXED_PERSON_NAME = PersonDetails.PROP_NAME_FIXED_PERSON_NAME
    PARAM_PERSON_TYPE = PersonDetails.PROP_NAME_PERSON_TYPE
    PARAM_ORIGINAL_PERSON_TYPE = PersonDetails.PROP_NAME_ORIGINAL_PERSON_TYPE
    PARAM_ARTICLE_PERSON_ID = PersonDetails.PROP_NAME_ARTICLE_PERSON_ID
    PARAM_TITLE = PersonDetails.PROP_NAME_TITLE
    PARAM_PERSON_ORGANIZATION = PersonDetails.PROP_NAME_PERSON_ORGANIZATION
    PARAM_QUOTE_TEXT = PersonDetails.PROP_NAME_QUOTE_TEXT
    PARAM_NEWSPAPER_INSTANCE = PersonDetails.PROP_NAME_NEWSPAPER_INSTANCE
    PARAM_NEWSPAPER_NOTES = PersonDetails.PROP_NAME_NEWSPAPER_NOTES
    PARAM_EXTERNAL_UUID_NAME = PersonDetails.PROP_NAME_EXTERNAL_UUID_NAME
    PARAM_EXTERNAL_UUID = PersonDetails.PROP_NAME_EXTERNAL_UUID
    PARAM_EXTERNAL_UUID_SOURCE = PersonDetails.PROP_NAME_EXTERNAL_UUID_SOURCE
    PARAM_EXTERNAL_UUID_NOTES = PersonDetails.PROP_NAME_EXTERNAL_UUID_NOTES
    PARAM_CAPTURE_METHOD = PersonDetails.PROP_NAME_CAPTURE_METHOD
    PARAM_SUBJECT_TYPE = PersonDetails.PROP_NAME_SUBJECT_TYPE
    PARAM_CODER_TYPE = PersonDetails.PROP_NAME_CODER_TYPE

    # author info properties
    AUTHOR_INFO_AUTHOR_NAME_STRING = "author_name_string"
    AUTHOR_INFO_AUTHOR_NAME_LIST = "author_name_list"
    AUTHOR_INFO_AUTHOR_AFFILIATION = "author_affiliation"
    AUTHOR_INFO_STATUS = "status"
    
    # for lookup, match statuses
    MATCH_STATUS_SINGLE = "single"
    MATCH_STATUS_MULTIPLE = "multiple"
    MATCH_STATUS_NONE = "none"
    
    # props for dictionary returned when getting Article_Data for article/user
    #    pair
    PROP_ARTICLE_DATA = "article_data"
    PROP_STATUS_MESSAGE = "status_message"
    PROP_LOOKUP_STATUS = "lookup_status"
    PROP_LOOKUP_STATUS_VALUE_NEW = "new"
    PROP_LOOKUP_STATUS_VALUE_EXISTING = "existing"
    PROP_LOOKUP_STATUS_VALUE_MULTIPLE = "multiple"
    PROP_LOOKUP_STATUS_VALUE_ERROR = "error"
    PROP_EXCEPTION = "exception"
    
    PROP_LOOKUP_ERROR_STATUS_LIST = []
    PROP_LOOKUP_ERROR_STATUS_LIST.append( PROP_LOOKUP_STATUS_VALUE_MULTIPLE )
    PROP_LOOKUP_ERROR_STATUS_LIST.append( PROP_LOOKUP_STATUS_VALUE_ERROR )
    
    PROP_LOOKUP_FOUND_STATUS_LIST = []
    PROP_LOOKUP_FOUND_STATUS_LIST.append( PROP_LOOKUP_STATUS_VALUE_NEW )    
    PROP_LOOKUP_FOUND_STATUS_LIST.append( PROP_LOOKUP_STATUS_VALUE_EXISTING )
    
    # person types
    PERSON_TYPE_SUBJECT = PersonDetails.PERSON_TYPE_SUBJECT
    PERSON_TYPE_SOURCE = PersonDetails.PERSON_TYPE_SOURCE
    PERSON_TYPE_AUTHOR = PersonDetails.PERSON_TYPE_AUTHOR

    # subject_type to person type dictionary
    SUBJECT_TYPE_TO_PERSON_TYPE_MAP = PersonDetails.SUBJECT_TYPE_TO_PERSON_TYPE_MAP


    #----------------------------------------------------------------------------
    # NOT instance variables
    # Class variables - overriden by __init__() per instance if same names, but
    #    if not set there, shared!
    #----------------------------------------------------------------------------


    # cofiguration parameters
    #config_application = ""
    #config_property_list = []
    #config_properties = {}
    
    # rate-limiting - in BasicRateLimited
    #do_manage_time = False
    #rate_limit_in_seconds = -1
    #rate_limit_daily_limit = -1
    
    # debug
    #debug = ""

    # exception helper.
    #exception_helper = None
    
    
    #-----------------------------------------------------------------------------
    # ! ==> class methods
    #-----------------------------------------------------------------------------


    @classmethod
    def get_automated_coding_user( cls, create_if_no_match_IN = True, *args, **kwargs ):
    
        '''
        Can't reference django models in class context anymore in models files:
            http://stackoverflow.com/questions/25537905/django-1-7-throws-django-core-exceptions-appregistrynotready-models-arent-load
        So, this method gets User instance for automated user username instead.
        '''
        
        # return reference
        user_OUT = None

        # logic moved to SourcenetBase - call method there.
        user_OUT = SourcenetBase.get_automated_coding_user( create_if_no_match_IN )

        return user_OUT
        
    #-- END class method get_automated_coding_user() --#
    
    
    @classmethod
    def parse_author_string( cls, author_string_IN, capitalize_each_word_IN = False, delimiter_IN = Article.AUTHOR_STRING_DIVIDER, *args, **kwargs ):
        
        '''
        Accepts an author string.  Parses into author name string, author name
            list, and author affiliation string as follows:
            - strip off "BY" and any number of spaces from beginning if present.
            - split string on "/" to separate name(s) from affiliation
            - split name string on "and", and then ",", to find multiple names.
            - all names go in name list.
        '''
        
        # return reference
        author_info_OUT = {}
        
        # declare variables
        me = "parse_author_string"
        my_logger = None
        status_message = ""
        status_message_list = []
        status_OUT = ""
        author_parts = None
        author_parts_length = -1
        author_affiliation = ""
        author_name_string = ""
        author_name_list = []
        author_split_on_and_list = []
        author_and_part = ""
        current_author_name = ""
        author_split_on_comma_list = []
        author_comma_part = ""
        
        # get logger
        my_logger = cls.get_a_logger( cls.LOGGER_NAME )
        
        # get author_string
        author_string = author_string_IN
        
        # got a string?
        if ( ( author_string is not None ) and ( author_string != "" ) ):
        
            my_logger.debug( "--- In " + me + ": Processing author string: \"" + author_string + "\"" )
            
            # got an author string.  Parse it.  First, break out organization.
            # split author string on "/"
            author_parts = author_string.split( delimiter_IN )
            
            # got two parts?
            author_parts_length = len( author_parts )
            if ( author_parts_length == 2 ):
                
                # we do.  2nd part = organization
                author_affiliation = author_parts[ 1 ]
                author_affiliation = author_affiliation.strip()
                
                # first part is author string we look at going forward.
                author_name_string = author_parts[ 0 ]
                author_name_string = author_name_string.strip()
                
                # also, if string starts with "By " and any number of spaces,
                #     remove it.
                author_name_string = re.sub( cls.REGEX_BEGINS_WITH_BY, "", author_name_string )
                
            # one part? (just call it the name string)
            elif ( author_parts_length == 1 ):
            
                # consider the one item in list to be author string.
                author_name_string = author_parts[ 0 ]
                author_name_string = author_name_string.strip()
                
                # also, if string starts with "By " and any number of spaces,
                #     remove it.
                author_name_string = re.sub( cls.REGEX_BEGINS_WITH_BY, "", author_name_string )
            
            elif ( ( author_parts_length == 0 ) or ( author_parts_length > 2 ) ):
            
                # error.  what to do?
                status_message = cls.STATUS_ERROR_PREFIX + " in " + me + ": splitting on '/' resulted in either an empty array or more than two things.  This isn't right ( " + author_string + " )."
                status_message_list.append( status_message )
                
                # do not process.
                author_name_string = None
                
            #-- END check results of splitting on "/"
            
            # Got something in author_name_string?
            if ( ( author_name_string is not None ) and ( author_name_string != "" ) ):

                # after splitting, we have a string.  Now need to split on
                #    "," and " and ".  First, split on " and ".
                
                # make sure any " and " is all lower case...
                author_name_string = re.sub( cls.REGEX_CONTAINS_AND, " and ", author_name_string )
                
                # ...then, split on " and "...
                author_split_on_and_list = author_name_string.split( " and " )

                # ...and then loop over parts.
                for author_and_part in author_split_on_and_list:
                
                    # strip out white space
                    current_author_name = author_and_part.strip()
                
                    # try splitting on comma.
                    author_split_on_comma_list = current_author_name.split( "," )
                    
                    # got any?
                    if ( len( author_split_on_comma_list ) > 0 ):
                    
                        # yes.  Add each as a name.
                        for author_comma_part in author_split_on_comma_list:
                        
                            # strip out white space
                            current_author_name = author_comma_part.strip()
                            
                            # still got something?
                            if ( ( current_author_name is not None ) and ( current_author_name != "" ) ):

                                # capitalize each word?
                                if ( capitalize_each_word_IN == True ):
                                
                                    # yes - capitalize each word.
                                    current_author_name = StringHelper.capitalize_each_word( current_author_name )
                                    
                                #-- END check to see if we are to capitalize each word --#

                                # add name to list of names.
                                author_name_list.append( current_author_name )
                                
                            #-- END check to make sure there was a name. --#
                            
                        #-- END loop over authors separated by commas. --#
                        
                    else:
                    
                        # no comma-delimited names.
                        
                        # capitalize each word?
                        if ( capitalize_each_word_IN == True ):
                        
                            # yes - capitalize each word.
                            current_author_name = StringHelper.capitalize_each_word( current_author_name )
                            
                        #-- END check to see if we are to capitalize each word --#

                        # Add current string to name list.
                        author_name_list.append( current_author_name )
                        
                    #-- END check to see if comma-delimited names --#
                    
                #-- END loop over and-delimited split of authors --#
                
                # time to start testing.  Print out the array.
                my_logger.debug( "In " + me + ": Author list: " + str( author_name_list ) )
                
            else:                
                
                # error.  what to do?
                status_message = cls.STATUS_ERROR_PREFIX + "in " + me + ": after splitting on '/', no author string left.  Not a standard byline ( " + author_string + " )."
                status_message_list.append( status_message )

            #-- END check to see if anything in author string. --#
        
        else:
        
            # No author string - error.
            status_message = cls.STATUS_ERROR_PREFIX + "in " + me + ": no author string, so nothing to do."
            status_message_list.append( status_message )
        
        #-- END check to see if author string. --#

        # place values in author info dictionary.
        author_info_OUT = {}
        author_info_OUT[ cls.AUTHOR_INFO_AUTHOR_NAME_STRING ] = author_name_string
        author_info_OUT[ cls.AUTHOR_INFO_AUTHOR_NAME_LIST ] = author_name_list
        author_info_OUT[ cls.AUTHOR_INFO_AUTHOR_AFFILIATION ] = author_affiliation
        author_info_OUT[ cls.AUTHOR_INFO_STATUS ] = " || ".join( status_message_list )
        my_logger.debug( "In " + me + ": Author info: " + str( author_info_OUT ) )
    
        return author_info_OUT
    
    #-- END class method parse_author_string() --#


    #----------------------------------------------------------------------------
    # ! ==> __init__() method
    #----------------------------------------------------------------------------


    def __init__( self ):

        # call parent's __init__()
        super( ArticleCoder, self ).__init__()

        # declare variables
        my_exception_helper = None
        self.config_application = ""
        self.config_property_list = []
        self.config_properties = {}
    
        # rate-limiting
        self.do_manage_time = False
        self.rate_limit_in_seconds = -1
        self.rate_limit_daily_limit = -1
        
        # debug
        self.debug = ""
        
        # exception helper
        self.exception_helper = None
        my_exception_helper = ExceptionHelper()
        #my_exception_helper.set_logging_level( logging.DEBUG )
        self.set_exception_helper( my_exception_helper )

        # initialize configuration properties
        self.init_config_properties()
        
        # load properties
        self.load_config_properties()
        
        # LoggingHelper parent class: (LoggingHelper --> BasicRateLimited -->
        #     ArticleCoder
        # - set logger name
        self.set_logger_name( self.LOGGER_NAME )
        
        # - set logger_debug_flag
        self.logger_debug_flag = self.DEBUG_FLAG

    #-- END method __init__() --#


    #----------------------------------------------------------------------------
    # ! ==> instance methods, in alphabetical order
    #----------------------------------------------------------------------------


    def add_config_property( self, prop_name_IN ):
        
        # return reference
        prop_name_OUT = ''
        
        # declare variables
        prop_name_list = []
        
        # get property name list.
        prop_name_list = self.get_config_property_list()
        
        # add the property name to the list.
        prop_name_list.append( prop_name_IN )
        
        return prop_name_OUT
        
    #-- END method add_config_property() --#
    
    
    def code_article( self, article_IN, *args, **kwargs ):

        '''
        purpose: After the ArticleCoder is initialized, this method accepts one
           article instance and codes it for sourcing.  Processing that is the
           same for all articles lives here, then abstract method
           process_article() is called for coder-specific article processing.
           In regards to articles, this class is stateless, so you can process
           many articles with a single instance of this object without having to
           reconfigure each time.
        preconditions: load_config_properties() should have been invoked before
           running this method.
        postconditions: article passed in is coded, which means an Article_Data
           instance is created for it and populated to the extent the child
           class is capable of coding the article.
        '''

        # return reference
        status_OUT = self.STATUS_SUCCESS
        
        # declare variables
        my_logger = None
        automated_coding_user = None
        article_text = None
        article_body_html = ""
        request_data = ""
        my_http_helper = None
        requests_response = None
        requests_raw_text = ""
        requests_response_json = None
        debug_message = ""
        
        # get logger
        my_logger = self.get_logger()
        
        # get automated_coding_user
        automated_coding_user = self.get_automated_coding_user()
        
        # got a user?
        if ( automated_coding_user is not None ):

            # got an article?
            if ( article_IN is not None ):
    
                # call process_article()
                status_OUT = self.process_article( article_IN, automated_coding_user )
    
                # see if status other than success
                if ( status_OUT != self.STATUS_SUCCESS ):
                    
                    # error - output
                    my_logger.debug( "ERROR with article \"" + str( article_IN ) + "\": " + status_OUT + "\n" )
                    
                else:
                    
                    # Success move on.
                    my_logger.debug( "SUCCESS - Processed article \"" + str( article_IN ) + "\"\n" )
                
                #-- END status processing. --#

            #-- END check to see if article. --#
            
        else:
        
            status_OUT = self.STATUS_ERROR_PREFIX + "Could not find user with name \"automated\".  Can't code articles without a user."
            
        #-- END check to make sure we have an automated coding user. --#
        
        return status_OUT

    #-- END method code_article() --#
    

    def get_config_application( self ):

        '''
        Returns this instance's config_application value.  If no value, returns None.
        '''
        
        # return reference
        value_OUT = None

        # declare variables

        # get value.
        value_OUT = self.config_application
        
        # got anything?
        if ( ( value_OUT is None ) or ( value_OUT == "" ) ):
        
            # no - return None.
            value_OUT = None
            
        #-- END check to see if we have a value. --#

        return value_OUT

    #-- END get_config_application() --#


    def get_config_properties( self ):

        '''
        Retrieves dict that maps property names to property values.
        '''
        
        # return reference
        dict_OUT = None

        # get properties.
        dict_OUT = self.config_properties

        return dict_OUT

    #-- END get_config_properties() --#


    def get_config_property( self, name_IN, default_IN = None ):

        '''
        Retrieves property value for the name passed in.  If no value, returns None.
        '''
        
        # return reference
        value_OUT = None

        # declare variables
        my_props = None

        # got a name?
        if ( ( name_IN is not None ) and ( name_IN != "" ) ):

            # get properties.
            my_props = self.get_config_properties()
            
            # get value
            value_OUT = my_props.get( name_IN, default_IN )
                        
        else:
        
            # no name - return None
            value_OUT = default_IN
        
        #-- END check to see if name passed in. --#

        return value_OUT

    #-- END get_config_property() --#


    def get_config_property_list( self ):

        '''
        Returns this instance's config_property_list.  If no value, returns [].
        '''
        
        # return reference
        list_OUT = None

        # declare variables

        # get list.
        list_OUT = self.config_property_list
        
        # got anything?
        if list_OUT is None:
        
            # no - return None.
            list_OUT = []
            
        #-- END check to see if we have a value. --#

        return list_OUT

    #-- END get_config_property_list() --#


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


    @abstractmethod
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

        pass

    #-- END abstract method init_config_properties() --#
    

    @abstractmethod
    def initialize_from_params( self, params_IN, *args, **kwargs ):

        '''
        purpose: Accepts a dictionary of run-time parameters, uses them to
           initialize this instance.
        preconditions: None.
        postconditions: None.
        '''

        pass

    #-- END abstract method init_config_properties() --#
    

    def load_config_properties( self, *args, **kwargs ):

        '''
        Invoked from render(), after ties have been generated based on articles
           and people passed in.  Returns a string.  This string can contain the
           rendered data (CSV file, etc.), or it can just contain a status
           message if the data is rendered to a file or a database.
           
        Example of getting properties from django_config:
        
        # get settings from django_config.
        email_smtp_server_host = Config_Property.get_property_value( Issue.CONFIG_APPLICATION, Issue.CONFIG_PROP_SMTP_HOST )
        email_smtp_server_port = Config_Property.get_property_int_value( Issue.CONFIG_APPLICATION, Issue.CONFIG_PROP_SMTP_PORT, -1 )
        email_smtp_server_username = Config_Property.get_property_value( Issue.CONFIG_APPLICATION, Issue.CONFIG_PROP_SMTP_USERNAME, "" )
        email_smtp_server_password = Config_Property.get_property_value( Issue.CONFIG_APPLICATION, Issue.CONFIG_PROP_SMTP_PASSWORD, "" )
        use_SSL = Config_Property.get_property_boolean_value( Issue.CONFIG_APPLICATION, Issue.CONFIG_PROP_SMTP_USE_SSL, False )
        email_from_address = Config_Property.get_property_value( Issue.CONFIG_APPLICATION, Issue.CONFIG_PROP_FROM_EMAIL )

        '''

        # return reference
        status_OUT = self.STATUS_SUCCESS
        
        # declare variables.
        config_application = ""
        config_prop_list = []
        property_name = ""
        property_value = ""
        
        # retrieve application and property list.
        config_application = self.get_config_application()
        config_prop_list = self.get_config_property_list()
        
        # loop over property list.
        for property_name in config_prop_list:
        
            # retrieve property
            property_value = Config_Property.get_property_value( config_application, property_name, None )
            
            # store it.
            self.set_config_property( property_name, property_value ) 
        
        #-- END loop over property names. ---#

        return status_OUT

    #-- END abstract method load_config_properties() --#
    

    def lookup_article_data( self, article_IN, user_IN, article_data_id_IN = None ):
        
        '''
        Accepts article, user and optional Article_Data ID.  Tries to retrieve
            Article_Data for article-user pair.  If multiple found and ID passed
            in, then tried to filter on that ID to get a single match.
           
        Returns a dictionary that contains:
        - PROP_ARTICLE_DATA = "article_data" - either matching Article_Data
            instance or None.
        - PROP_LOOKUP_STATUS = "lookup_status" - status code with one of the 
            following statuses:
            - PROP_LOOKUP_STATUS_VALUE_NEW = "new"
            - PROP_LOOKUP_STATUS_VALUE_EXISTING = "existing"
            - PROP_LOOKUP_STATUS_VALUE_MULTIPLE = "multiple"
            - PROP_LOOKUP_STATUS_VALUE_ERROR = "error"
        - PROP_STATUS_MESSAGE = "status_message" - if "multiple" or "error",
            explains what happened.  If "new" or "existing", empty.
        - PROP_EXCEPTION = "exception"
           
        Postconditions - Returns:
        - if single match found, returns it with status of "existing"
            (self.PROP_LOOKUP_STATUS_PROP_EXISTING) and no status message or
            exception.
        - if no match found, creates new instance, returns it with status of
            "new" (self.PROP_LOOKUP_STATUS_PROP_NEW) and no status message
            or exception.
        - if multiple matches found, returns None with status of "multiple"
            (self.PROP_LOOKUP_STATUS_PROP_MULTIPLE), status_message explaining,
            and no exception.
        - if other error, returns None, status of "error"
            (self.PROP_LOOKUP_STATUS_PROP_ERROR), status message that contains
            the exception cast as a string, and the exception itself.
        '''
        
        # return references
        result_OUT = {}
        article_data_OUT = None
        status_OUT = ""
        status_message_OUT = ""
        exception_OUT = None
        
        # declare variables.
        me = "lookup_article_data"
        article_data_id_list = None
        article_data_qs = None
        mor_exception = None
        dne_exception = None
        article_data_count = -1
        article_data_instance = None
        
        # make sure we have an article...
        if ( article_IN is not None ):
        
            # ...and a user.
            if ( user_IN is not None ):
            
                # got article and user.  By default, get for article and user,
                #    even if we have an ID specified.
                
                # !check for existing Article_Data
                # see if there is an existing Article_Data instance for this
                #    user and article.
                article_data_qs = Article_Data.objects.filter( coder = user_IN )
                article_data_qs = article_data_qs.filter( article = article_IN )

                # How many matches?
                try:

                    # use .get() to retrieve single instance from QuerySet.
                    article_data_OUT = article_data_qs.get()

                    # set status to "existing"
                    status_OUT = self.PROP_LOOKUP_STATUS_VALUE_EXISTING

                except MultipleObjectsReturned as mor_exception:

                    # more than one - get count and ID list.
                    article_data_count = article_data_qs.count()
                    
                    # build string Article_Data ID list.
                    article_data_id_list = []
                    for article_data_instance in article_data_qs:
                    
                        # convert ID to string, add to list.
                        article_data_id_list.append( str( article_data_instance.id ) )
                        
                    #-- END loop to get article IDs. --#

                    # See if we have an Article_Data ID.
                    if ( ( article_data_id_IN is not None ) and ( article_data_id_IN != "" ) and ( article_data_id_IN > 0 ) ):
                    
                        # we have an Article_Data ID.  filter.
                        try:
    
                            # use exception handling to see if record already exists.
                            
                            # filter on ID
                            article_data_qs = article_data_qs.filter( pk = article_data_id_IN )
                            
                            # use get() to see if there is a single match.
                            article_data_OUT = article_data_qs.get()

                            # yes - set status to "existing"
                            status_OUT = self.PROP_LOOKUP_STATUS_VALUE_EXISTING
        
                        except Exception as e:
                        
                            # no single match.  article data to None...
                            article_data_OUT = None

                            # set status to "multiple"
                            status_OUT = self.PROP_LOOKUP_STATUS_VALUE_MULTIPLE
        
                            # ...create status message...
                            status_message_OUT = "Multiple Article_Data found ( ids = " + ", ".join( article_data_id_list ) + " ) for user: " + str( user_IN ) + " and article ID: " + str( article_IN.id ) + ", none of which has Article_Data ID passed in ( " + str( article_data_id_IN ) + " )."

                            # ...and log it.
                            self.output_debug( status_message, me, indent_with_IN = "====>" )
                    
                        #-- END check to see if we can find existing article data. --#
                        
                    else:

                        # Too many Article_Data instances for user, and
                        #    no way to choose among them.

                        # no single match.  article data to None...
                        article_data_OUT = None

                        # ...set status to "multiple"...
                        status_OUT = self.PROP_LOOKUP_STATUS_VALUE_MULTIPLE
    
                        # ...create status message...
                        status_message_OUT = "Multiple Article_Data found ( ids = " + ", ".join( article_data_id_list ) + " ) for user: " + str( user_IN ) + " and article ID: " + str( article_IN.id ) + "."

                        # ...and log it.
                        self.output_debug( status_message, me, indent_with_IN = "====>" )
                    
                    #-- END check to see if article data already exists. --#

                except Article_Data.DoesNotExist as dne_exception:
                
                    # no Article_Data.  Create a new record.
                    article_data_OUT = Article_Data()
                    
                    # get article for ID, store in Article_Data.
                    article_data_OUT.article = article_IN
                    article_data_OUT.coder = user_IN
                
                    # Save off Aricle_Data instance - current_article_data.save()
                    article_data_OUT.save()

                    # set status to "new"
                    status_OUT = self.PROP_LOOKUP_STATUS_VALUE_NEW

                except Exception as e:

                    # hmmm.  Not sure what is going on here.  set status to
                    #    "error", put str( e ) in message, and store exception.
                    article_data_OUT = None
                    status_OUT = self.PROP_LOOKUP_STATUS_VALUE_ERROR
                    status_message_OUT = "Article_Data lookup for user: " + str( user_IN ) + " and article ID: " + str( article_IN.id ) + " resulted in unexpected Exception: " + str( e )
                    exception_OUT = e

                #-- END try...except around initial attempt to pull in Article_Data for current user. --#

            else:
            
                # No user - error.
                article_data_OUT = None
                status_OUT = self.PROP_LOOKUP_STATUS_VALUE_ERROR
                status_message_OUT = "No user passed in.  Can't lookup Article_Data for article ID: " + str( article_IN.id ) + "."
                        
            #-- END check to see if user.
            
        else:
        
            # No article - error.
            article_data_OUT = None
            status_OUT = self.PROP_LOOKUP_STATUS_VALUE_ERROR
            status_message_OUT = "No article passed in.  Can't lookup Article_Data if no article specified."
                    
        #-- END check to see if article.

        # pack up result dictionary.
        result_OUT[ self.PROP_ARTICLE_DATA ] = article_data_OUT
        result_OUT[ self.PROP_LOOKUP_STATUS ] = status_OUT
        result_OUT[ self.PROP_STATUS_MESSAGE ] = status_message_OUT
        result_OUT[ self.PROP_EXCEPTION ] = exception_OUT
        
        return result_OUT
        
    #-- END method lookup_article_data() --#
    

    def lookup_calc_confidence( self, person_IN, person_details_IN = {}, *args, **kwargs ):

        '''
        Invoked by lookup_person(), calculates confidence score for person
           passed in, returns decimal confidence score between 0 (no confidence)
           and 1 (high confidence).
        
        Accepts:
           - person_IN - Article_Person child instance (Article_Author or Article_Subject)
           - person_details_IN - optional dictionary of person details for the current person.  Includes:
              - PARAM_NEWSPAPER_INSTANCE = "newspaper_instance"
              - PARAM_NEWSPAPER_NOTES = "newspaper_notes"
              - PARAM_EXTERNAL_UUID_NAME = "external_uuid_name"
              - PARAM_EXTERNAL_UUID = "external_uuid"
              - PARAM_EXTERNAL_UUID_SOURCE = "external_uuid_source"
              - PARAM_EXTERNAL_UUID_NOTES = "external_uuid_notes"
           
        Current confidence checks (subtracts 0.1 each if not present):
        - If UUID present in person_details_IN, checks to see if person has that UIID related.  If not, -0.1.
        - If UUID present in person_details_IN, checks to see if any other person has that UIID related.  If yes...  Uh Oh. -2.0
        - If newspaper present, checks to see if person is related to that newspaper.  If not, -0.1.
        - Tries a full-name search.  If others with full-name, -0.1 (though likely a parsing issue...)
        '''

        # return reference
        value_OUT = 0.0
        
        # declare variables.
        me = "lookup_calc_confidence"
        my_person_details = None
        newspaper_IN = None
        uuid_IN = ""
        person_id = -1
        confidence_level = 0.0
        confidence_qs = None
        confidence_count = -1
        current_person = None
        
        # sanity full-name lookup.
        standardized_full_name = ""
        full_name_qs = None
        full_name_match_count = -1
        
        # got a person?
        if ( person_IN is not None ):
        
            # make sure we have PersonDetails instance.
            my_person_details = PersonDetails.get_instance( person_details_IN )
        
            # load up incoming things we care about here.
            newspaper_IN = my_person_details.get( self.PARAM_NEWSPAPER_INSTANCE, None )
            uuid_IN = my_person_details.get( self.PARAM_EXTERNAL_UUID, None )
            person_id = person_IN.id
        
            # start confidence at 1
            confidence_level = 1.0
            
            # got a UUID?
            if ( ( uuid_IN is not None ) and ( uuid_IN != "" ) ):

                # yes.  See if we have one that matches.
                confidence_qs = person_IN.person_external_uuid_set.filter( uuid = uuid_IN )
                
                # got any?
                confidence_count = confidence_qs.count()
                if ( confidence_count == 0 ):
                
                    # no match for UUID.
                    confidence_level = confidence_level - 0.1
                
                elif ( confidence_count > 1 ):
                
                    # multiple matches!  Error.
                    self.output_debug( "In " + me + ": ERROR - While calculating confidence, multiple matches for UUID \"" + uuid_IN + "\"" )
                
                #-- END check to see if match. --#
                
                # see if anyone else has this UUID.
                confidence_qs = Person.objects.filter( person_external_uuid__uuid = uuid_IN )
                confidence_qs = confidence_qs.exclude( pk = person_id )
                
                # got any?
                confidence_count = confidence_qs.count()
                if ( confidence_count > 0 ):
                
                    # found match for UUID other than this person.
                    confidence_level = confidence_level - 2.0
                    
                    self.output_debug( "In " + me + ": ERROR - found people other than the one passed in with UUID." )
                    self.output_debug( "In " + me + ": Person passed in: " + str( person_IN ) )
                    self.output_debug( "In " + me + ": Others:" )

                    # output other people, for debugging.
                    for current_person in confidence_qs:
                    
                        self.output_debug( "In " + me + ": - " + str( current_person ) )
                    
                    #-- END loop over corrupted UUID persons. --#
                
                #-- END check to see if single match. --#                            
            
            #-- END check to see if UUID --#
            
            # got a newspaper?
            if ( newspaper_IN is not None ):
            
                # see if any have same paper as that passed in.
                confidence_qs = person_IN.person_newspaper_set.filter( newspaper = newspaper_IN )
                
                # got any?
                confidence_count = confidence_qs.count()
                if ( confidence_count == 0 ):
                
                    # no match for paper.
                    confidence_level = confidence_level - 0.1
                    
                elif ( confidence_count > 1 ):
                
                    # multiple matches!  Error.
                    self.output_debug( "In " + me + ": ERROR - While calculating confidence, multiple matches for newspaper: " + str( newspaper_IN ) )
                
                #-- END check to see if single match. --#                            
                
            #-- END check to see if newspaper passed in. --#
            
            # full name check (just out of curiosity...)
            standardized_full_name = person_IN.full_name_string
            
            # look for matches based on full name string.
            full_name_qs = Person.objects.filter( full_name_string__iexact = standardized_full_name )
  
            # got more than one?
            if ( full_name_match_count > 1 ):
            
                # there are more than one match.  My confidence just decreased.
                confidence_level = confidence_level - 0.5

            #-- END check to see if duplicates. --#

        #-- END check to see if person. --#
        
        value_OUT = confidence_level

        self.output_debug( "In " + me + ": confidence = " + str( value_OUT ) )

        return value_OUT

    #-- END abstract method load_config_properties() --#
    
    
    def lookup_person( self,
                       article_person_IN,
                       full_name_IN,
                       lookup_id_if_present_IN = True,
                       create_if_no_match_IN = True,
                       update_person_IN = True,
                       person_details_IN = PersonDetails(),
                       on_multiple_match_try_exact_lookup_IN = False,
                       on_multiple_create_new_person_IN = True,
                       *args,
                       **kwargs ):
    
        '''
        Accepts:
           - article_person_IN - Article_Person child instance (Article_Author or Article_Subject)
           - full_name_IN - full name of person we're looking up.
           - use_id_before_name_IN - optional boolean that indicates whether an ID being present in the details should override names in the details.  Defaults to True.
           - create_if_no_match_IN - optional boolean that indicates whether we want to create a new person if not found
           - update_person_IN - optional boolean that indicates whether we want to update the person based on stuff in person_details_IN if person found.
           - person_details_IN - optional dictionary of person details for the current person.  Includes:
              - PARAM_NEWSPAPER_INSTANCE = "newspaper_instance"
              - PARAM_NEWSPAPER_NOTES = "newspaper_notes"
              - PARAM_EXTERNAL_UUID_NAME = "external_uuid_name"
              - PARAM_EXTERNAL_UUID = "external_uuid"
              - PARAM_EXTERNAL_UUID_SOURCE = "external_uuid_source"
              - PARAM_EXTERNAL_UUID_NOTES = "external_uuid_notes"
              - PARAM_CAPTURE_METHOD = "capture_method"
              - PARAM_TITLE = "title" - title text - if new person created, uses up to first 255 characters of this, if present, as the sourcenet_person "title" column value.
              - PARAM_PERSON_ORGANIZATION = "person_organization"
              - PARAM_PERSON_ID = "person_id"
           - on_multiple_match_try_exact_lookup_IN - optional boolean, defaults 
              to False.  If True, tries an exact match - exactly what is in the
              name passed in, including making sure that fields that are not
              present in the name are also empty in match.  This is a slippery
              slope - this increases the probability of false positives.  Use
              at your own risk.
           - on_multiple_create_new_person_IN - optional boolean, defaults to
              True.  If True, when multiples are detected and disambiguation
              fails, creates a new person, stores the potential matches as well.
           
        Starting with the methods on Person object:

           - Person.get_person_for_name( full_name_IN, create_if_no_match_IN ).
           - Person.look_up_person_from_name( full_name_IN ).

        Tries to get person based on full name.  Then, if multiple matches, we
           attempt to disambiguate.  If new Person created, save the person.
           Then, if update_person_IN is true, update the person with information
           from person_details_IN.
           
        Returns Article_Person child passed in, with person nested inside it and
           match_confidence_level set.  If error or none found, person in
           Article_Person child will be set to None.
        '''
        
        # return reference
        instance_OUT = None
        
        # declare variables
        me = "lookup_person"
        newspaper_IN = None
        uuid_IN = ""
        person_id_IN = -1
        person_instance = None
        my_person_details = None
        lookup_status = ""
        standardized_full_name = ""
        full_name_qs = None
        full_name_count = -1
        current_person = None
        multiple_qs = None
        multiple_count = -1
        confidence_level = 1.0
        
        # declare variables - match status
        match_status = ""
        is_single_name_part = False
        temp_person = None
        temp_lookup_status = None
        test_person_qs = None
        test_person_count = -1
        test_person = None
        multiple_list = []
        
        # declare variables - match status - remove periods from name.
        my_human_name = None
        temp_full_name = None
        
        # declare variables - disambiguation
        person_id_list = []
        person_qs = None
        person_count = -1
        found_person = False
        person_filter_qs = None
        person_filter_count = -1
        
        # saving/updating person
        capture_method = ""
        title_IN = ""
        title_cleaned = ""
        title_length = -1
        organization_string_IN = ""
        organization_cleaned = ""
        organization_length = -1
        
        # declare variables - debug logging
        debug_string = ""
        
        # got a return reference?
        if ( article_person_IN is not None ):

            # prepare person details.  Got a dictionary passed in?
            if ( ( person_details_IN is not None )
                 and ( isinstance( person_details_IN, dict ) == True )
                 and ( len( person_details_IN ) > 0 ) ):
                 
                # details passed in - use them.
                
                # make sure we have PersonDetails instance, not just a dict(ionary).
                my_person_details = PersonDetails.get_instance( person_details_IN )

                debug_message = "--- In " + me + ": processing \"" + full_name_IN + "\", FOUND person_details_IN: " + str( my_person_details )
                self.output_debug( debug_message )
    
            else:
            
                # nothing passed in - create new dictionary.
                my_person_details = PersonDetails()
            
                debug_message = "--- In " + me + ": processing \"" + full_name_IN + "\", NO person_details_IN."
                self.output_debug( debug_message )
    
            #-- END check to see if dictionary passed in. --#

            # load up incoming things we care about here.
            newspaper_IN = my_person_details.get( self.PARAM_NEWSPAPER_INSTANCE, None )
            uuid_IN = my_person_details.get( self.PARAM_EXTERNAL_UUID, None )
            person_id_IN = my_person_details.get( self.PARAM_PERSON_ID, -1 )
        
            # and we'll use the instance passed in as the return reference.
            instance_OUT = article_person_IN
            
            # Was there a person ID in the details instance?
            if ( ( person_id_IN is not None ) and ( person_id_IN != "" ) and ( person_id_IN > 0 ) ):
            
                # Do we privilege ID over name?
                if ( lookup_id_if_present_IN == True ):
            
                    # yes.  Try to just get that person.
                    try:
                    
                        person_instance = Person.objects.get( pk = person_id_IN )
                    
                    except Person.DoesNotExist as dne:
                    
                        # Not found.
                        self.output_debug( "ERROR - In " + me + ": person_id_IN passed in ( " + str( person_id_IN ) + " ), but DoesNotExist." )
                        person_instance = None
                        
                    except Person.MultipleObjectsReturned as more:
                    
                        # multiple found.  Big error.
                        self.output_debug( "ERROR - In " + me + ": person_id_IN passed in ( " + str( person_id_IN ) + " ), but MultipleObjectsReturned." )
                        person_instance = None
                        
                    except Exception as e:
                    
                        # Unexpected exception.
                        self.output_debug( "In " + me + ": person_id_IN passed in ( " + str( person_id_IN ) + " ), unexpected Exception caught trying to look up in database: " + str( e ) )
                        person_instance = None
                        
                    #-- END try-except to look up person based on ID. --#
                    
                #-- END check to see if we should just get the person. --#
            
            #-- END check to see if person ID present. --#
        
            # if no person from ID, got a name?
            if ( ( person_instance is None ) and ( ( full_name_IN is not None ) and ( full_name_IN != "" ) ) ):
            
        #------------------------------------------------------------------------
        # !Search/Lookup phase
        #
        # Postconditions:
        # After this phase of lookup, the following variables will be set:
        # - match_status - set to either self.MATCH_STATUS_NONE, self.MATCH_STATUS_SINGLE, or self.MATCH_STATUS_MULTIPLE.
        # - person_instance
        #    - if match_status = self.MATCH_STATUS_SINGLE, set to the single match found.
        #    - if match_status = self.MATCH_STATUS_NONE, contains Person instance created from name passed in, not yet saved to database.
        #    - if match_status = self.MATCH_STATUS_MULTIPLE, should be ignored (should be None).
        # - multiple_list
        #    - if match_status = self.MATCH_STATUS_MULTIPLE - contains a list of Person instances of potential matches.
        #    - if match_status is self.MATCH_STATUS_SINGLE or self.MATCH_STATUS_NONE, should be ignored (should be empty List).
        #------------------------------------------------------------------------
            
                # lookup Person
                person_instance = Person.get_person_for_name( full_name_IN, create_if_no_match_IN = create_if_no_match_IN )
                lookup_status = Person.get_person_lookup_status( person_instance )
                
                # Decide what to do based on status.
                
                # Person.LOOKUP_STATUS_FOUND - found exactly one match.
                if ( lookup_status == Person.LOOKUP_STATUS_FOUND ):
                
                    # found one match.
                    match_status = self.MATCH_STATUS_SINGLE
                    
                    # check to see if the name passed in is a single name.
                    is_single_name_part = Person.is_single_name_part( full_name_IN )
                    if ( is_single_name_part == True ):

                        # yes.  Do strict lookup with no partial match to see if
                        #     this is an exact match.
                        temp_person = Person.get_person_for_name( full_name_IN,
                                                                  create_if_no_match_IN = False,
                                                                  do_strict_match_IN = True,
                                                                  do_partial_match_IN = False )
                        temp_lookup_status = Person.get_person_lookup_status( temp_person )
                        
                        # exact match?
                        if ( ( temp_person is None ) or ( person_instance.id != temp_person.id ) ):
                        
                            # we have a single word name, lookup and strict
                            #     lookup result in different matches.
                                                        
                            # further verify by checking if just one match for
                            #     the name passed in and first_name, ignoring
                            #     other name fields.
                            test_person_qs = Person.objects.filter( first_name__iexact = full_name_IN )
                            test_person_count = test_person_qs.count()
                            if ( test_person_count == 1 ):

                                # This is a relatively rare scenario - a single
                                #     name part matches to the only person in
                                #     the database that contains that name part
                                #     in their first name.  For our purposes,
                                #     this is not a match.  Make a new person
                                #     for the single name part, set match status
                                #     to None.
                                match_status = self.MATCH_STATUS_NONE
                                person_instance = Person.create_person_for_name( full_name_IN )
                                self.output_debug( "In " + me + ": name " + str( full_name_IN ) + " is first name of one person ( " + str( person_instance ) + " ) who has more name information.  This is not a reliable match, so creating new Person with just name passed in." )
                                
                            elif ( test_person_count > 1 ):
                            
                                # make list of IDs of multiple matches.
                                multiple_list = []
                                for test_person in test_person_qs:
                                    
                                    # add ID of each person to list.
                                    multiple_list.append( test_person )
                                    
                                #-- END loop over multiple matches. --#
                                
                                self.output_debug( "In " + me + ": name " + str( full_name_IN ) + " is first name of more than one person ( " + str( multiple_list ) + " ) who just has that first name.  But we found an exact match.  This makes no sense." )
                                
                            else:
                            
                                self.output_debug( "In " + me + ": name " + str( full_name_IN ) + " is not first name of any person, and yet it was matched to person: " + str( person_instance ) + ".  This makes no sense." )                                

                            #-- END check to see if one person with same first name --#
                                
                        #-- END check to see if our match is an exact match --#
                    
                    #-- END check to see if single name part --#
                
                # Person.LOOKUP_STATUS_NEW - no match, new record created.
                elif ( lookup_status == Person.LOOKUP_STATUS_NEW ):
                
                    # no match.
                    match_status = self.MATCH_STATUS_NONE

                # Person.LOOKUP_STATUS_NONE - either multiple found or none.
                elif ( lookup_status == Person.LOOKUP_STATUS_NONE ):
                
                    # could either be multiple matches for name or no matches
                    #    depending on whether create_if_no_match_IN is True or
                    #    False.  Use lookup method to get QuerySet of matches,
                    #    then based on the results, set match_status and if
                    #    multiple, add all to multiple_list.
                    multiple_qs = Person.look_up_person_from_name( full_name_IN )
                    
                    # get count
                    multiple_count = multiple_qs.count()
                    
                    # 0 or many?
                    if ( multiple_count == 0 ):
                    
                        # no matches.
                        match_status = self.MATCH_STATUS_NONE
                        
                        # make new person instance for name (not saved)
                        person_instance = Person.get_person_for_name( full_name_IN, create_if_no_match_IN = True )
                    
                        self.output_debug( "In " + me + ": multiple_qs.count() returned " + str( multiple_count ) + " ( match_status = \"" + match_status + "\" )." )
                    
                    elif ( multiple_count == 1 ):
                    
                        # one match. What?
                        match_status = self.MATCH_STATUS_SINGLE
                        person_instance = multiple_qs.get()
                        
                        self.output_debug( "In " + me + ": multiple_qs.count() returned " + str( multiple_count ) + " ( match_status = \"" + match_status + "\" ), in a part of code where result should have been either 0 or > 1.  Error." )
                    
                    elif ( multiple_count > 1 ):
                    
                        # more than one.
                        match_status = self.MATCH_STATUS_MULTIPLE
                    
                        # store persons in list.
                        #multiple_list = list( multiple_qs )
                        multiple_list = []
                        for current_person in multiple_qs:
                        
                            # add person to list.
                            multiple_list.append( current_person )
                            
                        #-- END loop over QuerySet. --#

                        self.output_debug( "In " + me + ": multiple_qs.count() returned " + str( multiple_count ) + " ( match_status = \"" + match_status + "\" ). List of matches: " + str( multiple_list ) )
                    
                    else:
                    
                        self.output_debug( "In " + me + ": multiple_qs.count() returned " + str( multiple_count ) + " ( match_status = \"" + str( match_status ) + "\" ), which is neither 0, 1, or > 1.  Error." )
                    
                    #-- END check to see how many matches --W
                
                else:
                
                    self.output_debug( "In " + me + ": Person.get_person_lookup_status() returned \"" + str( lookup_status ) + "\", which is non-standard.  Error." )

                #-- END check to see what we do based on status of lookup. --#
                
                # !full name string match
                # If no match for parsed name, try looking up using string
                #    full name (could in some cases be because of nameparser
                #    parsing error).
                if ( match_status == self.MATCH_STATUS_NONE ):

                    # no match for parsed name.  Try looking up using string
                    #    full name (could in some cases be because of nameparser
                    #    parsing error).
                    
                    # get standardized full name.
                    
                    # if no person instance, use Person.get_person_for_name() to
                    #    make one.
                    if ( person_instance is None ):
                    
                        # make instance, but it isn't saved to database.
                        person_instance = Person.get_person_for_name( full_name_IN, create_if_no_match_IN = True )
                        
                    #-- END check to see if person_instance --#
                    
                    # get full name string.
                    standardized_full_name = StringHelper.object_to_unicode_string( person_instance.full_name_string )
                    
                    # log the type of the variable here.
                    #debug_string = "standardized full name = \"" + str( standardized_full_name ) + "\"; type = " + str( type( standardized_full_name ) )
                    #self.output_debug( debug_string, me )
                        
                    # look for matches based on full name string.
                    full_name_qs = Person.objects.filter( full_name_string__iexact = standardized_full_name )

                    # got anything back?
                    full_name_count = full_name_qs.count()
                    if ( full_name_count == 0 ):

                        # !remove periods, look again.

                        # If no match, try removing periods ( "." ) from name
                        #     parts, then looking up using string full name (in
                        #     case middle initials are inconsistently entered 
                        #     with or without periods).
                        
                        # Use temp person to clean up punctuation
                        my_human_name = person_instance.to_HumanName()
                        temp_person = Person.create_person_for_name( full_name_IN,
                                                                     human_name_IN = my_human_name,
                                                                     remove_periods_IN = True )
                        temp_full_name = temp_person.full_name_string
                        
                        # look for matches based on no-periods full name string.
                        full_name_qs = Person.objects.filter( full_name_string__iexact = temp_full_name )

                    #-- END try to lookup person, periods removed from name strings. --#
                    
                    # !TODO - just first name, last name...?

                    # got anything back?
                    full_name_count = full_name_qs.count()
                    if ( full_name_count == 0 ):
                    
                        # nothing returned from looking for full name, either.
                        match_status = self.MATCH_STATUS_NONE
                    
                    elif ( full_name_count == 1 ):
                    
                        # found one based on full name.  Parse error?
                        match_status = self.MATCH_STATUS_SINGLE
                        
                        # store person as person_instance.
                        person_instance = full_name_qs.get()
                        
                        # verification will handle assessing confidence.
                    
                    elif ( full_name_count > 1 ):

                        # found more than one based on full name.  What to do?
                        match_status = self.MATCH_STATUS_MULTIPLE
                        
                        # store persons in list.
                        #multiple_list = list( full_name_qs )
                        for current_person in full_name_qs:
                        
                            # add person to list.
                            multiple_list.append( current_person )
                            
                        #-- END loop over QuerySet. --#
                        
                    else:
                    
                        self.output_debug( "In " + me + ": full_name_qs.count() returned " + str( full_name_count ) + ", which is neither 0, 1, or > 1. Error." )
                    
                    #-- END check to see if any matches. --#
                
                #-- END check to see if we need to try full-name lookup. --#

                    
        #-----------------------------------------------------------------------
        # !Disambiguation Phase
        # - try exact match on each?
        # - create an entirely new person?
        # - UUID?
        # - newspaper?
        #-----------------------------------------------------------------------

                
                # multiple matches...        
                if ( match_status == self.MATCH_STATUS_MULTIPLE ):

                    # found_person initialize to False
                    found_person = False
                    
                    #== filter criteria on Person QuerySet ====================#

                    # convert multiple list into a QuerySet of those Persons.
                    person_id_list = []
                    
                    # get IDs for each of the multiple Persons.
                    for current_person in multiple_list:
                    
                        # put ID in list.
                        person_id_list.append( current_person.id )
                        
                    #-- END loop over multiple persons. --#
                    
                    self.output_debug( "In " + me + ": Multiple person matches: " + str( person_id_list ) )

                    # filter on IDs.
                    person_qs = Person.objects.filter( id__in = person_id_list )

                    #-- got a UUID? -------------------------------------------#
                    if ( ( uuid_IN is not None ) and ( uuid_IN != "" ) ):

                        # yes.  See if we have one that matches.
                        person_filter_qs = person_qs.filter( person_external_uuid__uuid = uuid_IN )
                        
                        # got any?
                        person_filter_count = person_filter_qs.count()
                        if ( person_filter_count == 1 ):
                        
                            # found match for UUID.
                            person_instance = person_filter_qs.get()
                            found_person = True
                            confidence_level = 1.0
                            
                            self.output_debug( "In " + me + ": MATCH FOUND for UUID " + str( uuid_IN ) + ": " + str( person_instance ) )
                        
                        #-- END check to see if single match. --#                            

                    #-- END check to see if UUID --#
                    
                    # got a newspaper (and UUID didn't match)?
                    if ( ( found_person == False ) and ( newspaper_IN is not None ) ):
                    
                        # see if any have same paper as that passed in.
                        person_filter_qs = person_qs.filter( person_newspaper__newspaper = newspaper_IN )
                        
                        # got any?
                        person_filter_count = person_filter_qs.count()
                        if ( person_filter_count == 1 ):
                        
                            # found match for newspaper.
                            person_instance = person_filter_qs.get()
                            found_person = True
                            confidence_level = 0.5
                        
                            self.output_debug( "In " + me + ": MATCH FOUND for Newspaper " + str( newspaper_IN ) + ": " + str( person_instance ) )

                        #-- END check to see if single match. --#                            
                        
                    #-- END check to see if newspaper passed in. --#
                    
                    #== last resort - exact match? ============================#

                    # if still no match, try an exact search using the name?
                    if ( ( found_person == False ) and ( on_multiple_match_try_exact_lookup_IN == True ) ):
                    
                        # try a strict match lookup.
                        person_qs = Person.look_up_person_from_name( full_name_IN, do_strict_match_IN = True )
                    
                        # how many results?  And, if only one, is this really better?
                        if ( person_qs.count() == 1 ):
                        
                            # Well, caller asked for it.  OK!
                            person_instance = person_filter_qs.get()
                            found_person = True
                            confidence_level = 0.7  # not sure of level of confidence here - if small sample, might be right...                           
                        
                            self.output_debug( "In " + me + ": MATCH FOUND for Exact Name Match: " + str( person_instance ) )

                        #-- END check to see if only 1 returned from exact. --#
                        
                    #-- END check to see if we want to do a strict match. --#
                    
                    #== finally, if all has failed, create new? ===============#
                    if ( ( found_person == False ) and ( on_multiple_create_new_person_IN == True ) ):
                    
                        # well, we've been asked to create a new person...
                        person_instance = Person.create_person_for_name( full_name_IN )
                        found_person = True
                        confidence_level = 0.0  # not sure what to do when you just give up and make a new person.
                    
                        self.output_debug( "In " + me + ": NO MATCH, created new person: " + str( person_instance ) )

                    #-- END check to see if we make a new person --#
                
                #-- END check to see if multiple. --#

        #------------------------------------------------------------------------
        # !Verification/Confidence phase
        #
        # Uses contents of match_status, person_instance, and multiple_list to
        #    figure out what to return from method call.
        # - If single person match found, calculates confidence, then places
        #    person_instance and confidence score into return reference.
        # - If no match, creates new Person by saving person_instance, then sets
        #    confidence to 1, stores person_instance in return reference.
        # - If multiple matches, places list of Person instances for potential
        #    matches in instance variable
        #    person_match_list inside return reference.
        #------------------------------------------------------------------------
            
                # so, based on match status, what do we do?
                # - set confidence level.
                # - if multiple, store list in return reference.

                # MATCH_STATUS_NONE - no match, new record created.
                if ( match_status == self.MATCH_STATUS_NONE ):
                
                    # should already be a new person instance created above.
                    
                    # confidence:
                    confidence_level = 1.0
                
                # MATCH_STATUS_MULTIPLE - multiple matches.  Store multiple list.
                elif ( match_status == self.MATCH_STATUS_MULTIPLE ):
                
                    # should already be a new person instance created above.
                    
                    # store multiple list in return reference.
                    instance_OUT.person_match_list = multiple_list

                    # confidence:
                    confidence_level = 0.0
                
                # MATCH_STATUS_SINGLE - one match.  Calculate confidence.
                elif ( match_status == self.MATCH_STATUS_SINGLE ):
                
                    #  use method to calculate confidence
                    confidence_level = self.lookup_calc_confidence( person_instance, my_person_details )
                
                else:
                
                    self.output_debug( "In " + me + ": match_status is \"" + str( match_status ) + "\", which is non-standard.  Error." )

                #-- END check to see what to do based on match status --#
                
            #-- END check to see if person not found by ID, and full name present.--#
                
            # should always be a Person to return at this point, but being
            #    cautious, just in case.
                
        #------------------------------------------------------------------------
        # !save/update person
        #------------------------------------------------------------------------
            
            # got a person (sanity check)?
            if ( person_instance is not None ):
            
                # if no ID, is new.
                if ( not( person_instance.id ) ):
                
                    # Set values and save to database?
                    if ( create_if_no_match_IN == True ):
                
                        # ! INSERT new person
                        self.output_debug( "INSERT PERSON - person_details_IN: " + str( my_person_details ), me, "========>" )
    
                        # no ID.  See if there is a capture_method.
                        capture_method = my_person_details.get( self.PARAM_CAPTURE_METHOD, None )
                        if ( ( capture_method is not None ) and ( capture_method != "" ) ):
                        
                            # got a capture method.  Add it to person instance.
                            person_instance.set_capture_method( capture_method )
                        
                        #-- END check to see if capture_method --#
                        
                        # Save the record.
                        person_instance.save()

                        # call update_person() to set title, organization,
                        #     related records.
                        person_instance = self.update_person( person_instance, my_person_details, allow_empty_IN = True )
                                                
                        self.output_debug( "saved new person - " + str( person_instance ), me, "========>" )
                        
                    else:
                    
                        person_instance = None
                    
                    #-- END check to see if we set values and save to database. --#
                    
                else:
                
                    # not new - are we to update?
                    if ( ( update_person_IN is not None ) and ( update_person_IN == True ) ):
                    
                        # ! UPDATE existing person
                        self.output_debug( "UPDATE PERSON - my_person_details: " + str( my_person_details ), me, "========>" )
    
                        # yes.
                        person_instance = self.update_person( person_instance, my_person_details )
    
                    #-- END check to see if we update person --#
                    
                #-- END check to see if INSERT or UPDATE --#
                
                # place person inside Article_Person instance.
                instance_OUT.person = person_instance
                instance_OUT.match_confidence_level = confidence_level
                instance_OUT.name = full_name_IN
                
            #-- END check to see if person found or created --#

            # only print if debug is on.
            if ( self.DEBUG_FLAG == True ):
            
                # debug is on.  log it.
                self.output_debug( "In " + me + " person match = " + str( person_instance ) )
            
            #-- END check to see if debug is on --#
                        
        #-- END check to see if Article_Person child instance present --#
            
        return instance_OUT
    
    #-- END method lookup_person() --#


    def output_debug( self, message_IN, method_IN = "", indent_with_IN = "", logger_name_IN = "", do_print_IN = False, resource_string_IN = None  ):
        
        '''
        Accepts message string.  If debug is on, logs it.  If not,
           does nothing for now.
        '''
        
        # just call LoggingHelper.output_debug_message() method.
        self.output_debug_message( message_IN, method_IN, indent_with_IN, logger_name_IN, do_print_IN, resource_string_IN )

    #-- END method output_debug() --#


    @abstractmethod
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

        pass

    #-- END abstract method process_article() --#
    

    def process_author_name( self,
                             article_data_IN,
                             author_name_IN,
                             person_details_IN = None ):
    
        '''
        Calls process_person_name() for logic.  See that method's doc for
            processing details.
        Accepts Article_Data container, string author name, optional string
            author organization, optional author person ID, and optional person
            details dictionary.  If ID present, tries to look up person based on
            ID.  If not, looks up person based name.  If person found, only adds
            to Article_Data if that person does not already have an
            Article_Author row.  If person not found, and if person details
            present, uses details passed in when populating person (see
            ArticleCoder.lookup_person() doc for values that can be passed in
            person details).
           
        preconditions: Assumes that there is an associated article.  If not,
            there will be an exception.
           
        postconditions: If all goes well, results in Article_Author for author
            passed in associated with Article_Data passed in, and returns status
            self.STATUS_SUCCESS.  If error, no Article_Author created, and
            status message describing the problem returned.  If person lookup
            works, but person already has an Article_Author row, updates that
            record with any changes present in PersonDetails.
        '''
        
        # return reference
        article_author_OUT = None
        
        # declare variables.
        me = "process_author_name"
        my_logger = None
        debug_message = ""
        
        # do any author-specific post-processing updates here.
                
        # ! call process_person_name()
        article_author_OUT = self.process_person_name( article_data_IN,
                                                       author_name_IN,
                                                       person_details_IN = person_details_IN,
                                                       article_person_class_IN = Article_Author )
                                                       
        # do any author-specific post-processing updates here.
                
        return article_author_OUT
    
    #-- END method process_author_name() --#


    def process_author_string( self, article_data_IN = None, author_string_IN = "" ):
        
        '''
        Eventually, this will be a real, generalized author string processor.
           For now, it just calls the method that knows how newsbank stores
           Grand Rapids Press bylines.
        '''
        
        # return reference
        status_OUT = self.STATUS_SUCCESS
        
        status_OUT = self.process_newsbank_grpress_author_string( article_data_IN, author_string_IN )
        
        return status_OUT
        
    #-- END method process_author_string() --#
        
    
    def process_mention( self, article_IN, article_subject_IN, mention_string_IN, mention_prefix_IN = "", mention_suffix_IN = "" ):
    
        '''
        Accepts Article, Article_Subject instance, and string text of a
           mention of the subject.  Looks for mention that has same string
           value.  If present, returns Article_Subject_Mention.
           If not, makes an Article_Subject_Mention instance for the mention,
           populates it, saves it, then returns it.  If error, returns None.
           
        Preconditions:  Assumes article_IN, article_subject_IN ,and
           mention_string_IN will be populated appropriately.  If any are
           missing or set to None, will break, throwing exceptions.  You should
           have already created and saved your Article_Subject before passing it
           to this method.
           
        Postconditions:  If mention wasn't already stored, it will be after
           this call.
        '''
        
        # return reference
        instance_OUT = None
        
        # declare variables
        me = "process_mention"
        debug_message = ""
        
        # declare variables - mention details and lookup
        mention_string = ""
        mention_length = ""
        mention_qs = None
        mention_count = -1
        current_mention = None
        
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
        
        # initialize notes list.
        notes_list = []
        
        # got a quotation string?
        if ( ( mention_string_IN is not None ) and ( mention_string_IN != "" ) ):
        
            # strip white space
            mention_string = mention_string_IN.strip()
            mention_length = len( mention_string )

            # also prep prefix and suffix if present.

            # prefix
            mention_prefix = None
            if ( ( mention_prefix_IN is not None ) and ( mention_prefix_IN != "" ) ):
                
                # strip prefix.
                mention_prefix = mention_prefix_IN.strip()

            #-- END check to see if prefix passed in. --#

            # add suffix if present.
            mention_suffix = None
            if ( ( mention_suffix_IN is not None ) and ( mention_suffix_IN != "" ) ):
                
                # strip suffix.
                mention_suffix = mention_suffix_IN.strip()

            #-- END check to see if suffix passed in. --#

            # output string.
            debug_message = "Mention: " + mention_string
            self.output_debug( debug_message, me )

            # got Article_Subject?
            if ( article_subject_IN is not None ):

                # got Article?
                if ( article_IN is not None ):

                    # is this mention already stored?
                    
                    # Filter on value.
                    mention_qs = article_subject_IN.article_subject_mention_set.filter( value = mention_string )
                                    
                    # got one?
                    mention_count = mention_qs.count()
                    if ( mention_count == 0 ):
                                    
                        # no.  Create one.
                        current_mention = Article_Subject_Mention()
                        
                        # store the Article_Subject in it.
                        current_mention.article_subject = article_subject_IN
                        
                        # store information from OpenCalais
                        current_mention.value = mention_string
                        current_mention.value_length = mention_length
                        
                        # derive a few more details based on finding the mention in the text
                        #    of the article.
                        
                        # get article text for article.
                        article_text = article_IN.article_text_set.get()
                        
                        # then, call find_in_text (FIT) method on mention plus suffix (to
                        #    make sure we get the right "he", for example).
                        find_string = mention_string

                        # add suffix if present.
                        if ( ( mention_suffix is not None ) and ( mention_suffix != "" ) ):
                            
                            # strip suffix, then add space between it and string
                            #    just to make sure there is only one space.
                            find_string += " " + mention_suffix.strip()

                        #-- END check to see if suffix passed in. --#

                        # find in text!
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

                            # ==> plain_text_index
                            plain_text_index = plain_text_index_list[ 0 ]

                            # ==> canonical_index
                            canonical_index = canonical_index_list[ 0 ]

                            # ==> paragraph_number
                            paragraph_number = paragraph_list[ 0 ]

                            # ==> first_word_number
                            first_word_number = first_word_list[ 0 ]

                            # ==> last_word_number
                            # add the count of words in the actual mention minus
                            #    1 (to account for the first word already being
                            #    counted) to the first word value to get the last
                            #    word number.
                            mention_word_list = mention_string.split()
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
                            find_full_string = mention_string

                            # add prefix if present.
                            if ( ( mention_prefix is not None ) and ( mention_prefix != "" ) ):
                                
                                # strip prefix, add space between it and string
                                #    just to make sure there is only one space.
                                find_full_string = mention_prefix.strip() + " " + find_full_string

                            #-- END check to see if prefix passed in. --#

                            # add suffix if present.
                            if ( ( mention_suffix is not None ) and ( mention_suffix != "" ) ):
                                
                                # strip suffix, add space between it and string
                                #    just to make sure there is only one space.
                                find_full_string += " " + mention_suffix.strip()

                            #-- END check to see if suffix passed in. --#

                            # ! Find in Text (FIT) inconsistent - look for string in plain text
                            found_list = article_text.find_in_plain_text( find_full_string )
                            found_list_count = len( found_list )
                            if ( found_list_count >= 1 ):
                            
                                # we know we have at least one match, so we can
                                #    dig in and try to get all the things.  For
                                #    simplicity's sake, for now, retrieve
                                #    information on first occurrence.

                                # If more than one, make a note, move on.
                                if ( found_list_count > 1 ):

                                    debug_message = "Found " + str( found_list_count ) + " matches for mention_string \"" + mention_string + "\" at indices: " + str( found_list )
                                    notes_list.append( debug_message )
                                    debug_message = "WARNING: " + debug_message
                                    self.output_debug( debug_message, me )

                                #-- END check to see if multiple matches found. --#

                                # use first match.
                                sanity_check_index = found_list[ 0 ]
                                full_string_index = sanity_check_index
                                
                                #-----------------------------------------------------------
                                # ! ==> plain text index
                                #-----------------------------------------------------------

                                # get actual plain text index (no prefix)
                                # eventually, here you'd do string + suffix.
                                #    For now, we just have string.
                                find_string = mention_string

                                # add suffix if present.
                                if ( ( mention_suffix is not None ) and ( mention_suffix != "" ) ):
                                    
                                    # strip suffix, add space between it and string
                                    #    just to make sure there is only one space.
                                    find_string += " " + mention_suffix.strip()

                                #-- END check to see if suffix passed in. --#

                                found_list = article_text.find_in_plain_text( find_string )
                                found_list_count = len( found_list )
                                if ( found_list_count == 1 ):
                                
                                    # if more than one, just use 1st.
                                    plain_text_index = found_list[ 0 ]
                                                                        
                                elif ( found_list_count > 1 ):
                                
                                    # do we have a prefix?
                                    if ( ( mention_prefix is not None ) and ( mention_prefix != "" ) ):

                                        # multiple matches.  If at end of entire
                                        #    article, could be because suffix is
                                        #    one or two words, there are other
                                        #    matches in the article.
                                        # Check to see if any of the matches are
                                        #    in a position that corresponds to
                                        #    the start of the actual mention in
                                        #    the full-string match.  The full-
                                        #    string match includes prefix, so
                                        #    shift that index to the right the
                                        #    length of the prefix to get to the
                                        #    start of the actual string.
                                        # Match = full_string_index + mention_prefix_length
                                        mention_prefix_length = len( mention_prefix )
                                        calculated_match_index = full_string_index + mention_prefix_length
                                        if calculated_match_index in found_list:
                                        
                                            # the calculated match index is in list.  That is
                                            #    the match.  Use it.
                                            plain_text_index = calculated_match_index
                                            
                                        else:

                                            # Not there.  Just use the 1st.
                                            plain_text_index = found_list[ 0 ]

                                        #-- END check to see which match is the right one.

                                    else:

                                        # nope.  Just use first match.
                                        plain_text_index = found_list[ 0 ]
                                                                        
                                    #-- END check to see if we have a prefix. --#
                                
                                else:
                                
                                    # ERROR.
                                    notes_string = "ERROR: Plain text index - `mention + suffix` (" + find_string + ") match count = " + str( found_list_count ) + ", `prefix + mention + suffix` (" + find_full_string + ") was at index " + str( sanity_check_index )
                                    notes_list.append( "In " + me + " " + notes_string )
                                    self.output_debug( notes_string, me )
                                    
                                    #is_ok_to_update = False
                                    # might as well update, so we can see what else for
                                    #    debugging. just set the plain text index to -1.
                                    plain_text_index = -1
                                
                                #-- END check to see if found mention + suffix
                                
                                #-----------------------------------------------------------
                                # ! ==> canonical index
                                #-----------------------------------------------------------

                                # canonical text seems to be a troublesome one.  Start out
                                #    looking for the full string.
                                found_list = article_text.find_in_canonical_text( find_full_string )
                                found_list_count = len( found_list )
                                
                                # one or more matches?
                                if ( found_list_count >= 1 ):
    
                                    # more than one?
                                    if ( found_list_count > 1 ):

                                        # WARNING.
                                        notes_string = "In " + me + ": WARNING - canonical index - prefix + mention + suffix ( \"" + find_full_string + "\" ) returned multiple matches: " + str( found_list ) + ".  Using 1st match."
                                        notes_list.append( notes_string )
                                        self.output_debug( notes_string )

                                        # OK to update...  Just broken.
                                        # is_ok_to_update = False

                                    #-- END check to see if more than one match --#

                                    # found it.  load value from list.
                                    canonical_index = found_list[ 0 ]
                                    
                                    # got prefix?
                                    if ( ( mention_prefix is not None ) and ( mention_prefix != "" ) ):
                                    
                                        # yes - add the length of the prefix to the
                                        #    value, to get to the actual start of
                                        #    the mention.
                                        mention_prefix_length = len( mention_prefix )
                                        canonical_index = canonical_index + mention_prefix_length

                                    #-- END check to see if prefix. --#
                                    
                                else:
                                
                                    # ERROR.
                                    notes_string = "In " + me + ": ERROR - canonical index - prefix + mention + suffix ( \"" + find_full_string + "\" ) returned 0 matches: " + str( found_list )
                                    notes_list.append( notes_string )
                                    self.output_debug( notes_string )

                                    # OK to update...  Just broken.
                                    # is_ok_to_update = False
                                
                                #-- END check to see if found in canonical text --#
                                
                                #-----------------------------------------------------------
                                # ! ==> word first and last numbers
                                #-----------------------------------------------------------

                                # Start out looking for the full string.
                                found_dict = article_text.find_in_word_list( find_full_string )
                                first_word_list = found_dict.get( Article_Text.FIT_FIRST_WORD_NUMBER_LIST, [] )
                                last_word_list = found_dict.get( Article_Text.FIT_LAST_WORD_NUMBER_LIST, [] )
                                found_list_count = len( first_word_list )

                                # one or more matches?
                                if ( found_list_count >= 1 ):
                                
                                    # more than one?
                                    if ( found_list_count > 1 ):

                                        # WARNING.
                                        notes_string = "WARNING - word first and last numbers - prefix + mention + suffix ( \"" + find_full_string + "\" ) either returned 0 or multiple matches: " + str( found_list ) + ".  Using 1st match."
                                        notes_list.append( "In " + me + ": " + notes_string )
                                        self.output_debug( notes_string, me )

                                        # OK to update...  Just broken.
                                        # is_ok_to_update = False
                                    
                                    #-- END check to see if found mention + suffix
                                
                                    # use first match.  load values from lists.
                                    first_word_number = first_word_list[ 0 ]
                                    last_word_number = last_word_list[ 0 ]
                                    
                                    # got a prefix?
                                    if ( ( mention_prefix is not None ) and ( mention_prefix != "" ) ):

                                        # yes - add prefix word count to the
                                        #    first word value, to get to the
                                        #    actual value.
                                        mention_prefix_word_list = mention_prefix.split()
                                        mention_prefix_word_count = len( mention_prefix_word_list )
                                        first_word_number = first_word_number + mention_prefix_word_count

                                    #-- END check to see if we have a prefix. --#
                                    
                                    # and add the count of words in the actual mention minus
                                    #    1 (to account for the first word already being
                                    #    counted) to the first word value to get the last
                                    #    word number.
                                    mention_word_list = mention_string.split()
                                    mention_word_count = len( mention_word_list )
                                    last_word_number = first_word_number + mention_word_count - 1

                                #-- END check to see if 1 or more matches in word list. --#
                                    
                                #-----------------------------------------------------------
                                # ! ==> paragraph number
                                #-----------------------------------------------------------

                                # Start out looking for the full string.
                                found_list = article_text.find_in_paragraph_list( find_full_string )
                                found_list_count = len( found_list )
                                
                                # one or more matches?
                                if ( found_list_count >= 1 ):
    
                                    # more than one?
                                    if ( found_list_count > 1 ):

                                        # WARNING.
                                        notes_string = "In " + me + ": WARNING - paragraph number - prefix + mention + suffix ( \"" + find_full_string + "\" ) either returned 0 or multiple matches: " + str( found_list ) + ".  Using 1st match."
                                        notes_list.append( notes_string )
                                        self.output_debug( notes_string )

                                        # OK to update...  Just broken.
                                        # is_ok_to_update = False

                                    #-- END check to see if more than one match --#

                                    # use first
                                    paragraph_number = found_list[ 0 ]
                                
                                #-- END check to see if found paragraph --#
                                                    
                            else:
                            
                                # No match.
                                notes_string = "ERROR - plain text index - prefix + mention + suffix ( \"" + find_full_string + "\" ) either returned 0 or multiple matches: " + str( found_list )
                                notes_list.append( "In " + me + ": " + notes_string )
                                self.output_debug( notes_string, me )
                                is_ok_to_update = False
                            
                            #-- END check to see if match for prefix + mention + suffix --#
                            
                        #-- END FIT check to make sure all searches returned same count of matches, else look more closely. --#
                        
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
                        current_mention.capture_method = self.coder_type

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
                    
                        # trouble - more than one mention matches.  Output message, return the first.
                        debug_message = "WARNING - more than one mention matches \"" + mention_string + "\".  Returning the first match."
                        self.output_debug( debug_message, me )

                        # grab first match.
                        mention_qs = mention_qs.order_by( "value_index" )
                        instance_OUT = mention_qs[ 0 ]

                        # if prefix or suffix, see if they narrow to 1.  If not,
                        #    move on.

                        # got prefix?
                        if ( ( mention_prefix is not None ) and ( mention_prefix != "" ) ):

                            # filter.
                            mention_qs = mention_qs.filter( context_before = mention_prefix )

                        #-- END check to see if prefix. --#

                        # got suffix?
                        if ( ( mention_suffix is not None ) and ( mention_suffix != "" ) ):

                            # filter.
                            mention_qs = mention_qs.filter( context_after = mention_suffix )

                        #-- END check to see if suffix. --#

                        # down to 1?
                        if ( mention_qs.count() == 1 ):

                            # yes.  I'll be darned.  Use it.
                            instance_OUT = mention_qs.get()

                        #-- END check to see if we've narrowed it to 1.

                    else:
                    
                        # trouble - count is invalid.
                        debug_message = "ERROR - count of mention matches for string \"" + mention_string + "\" is neither 0, 1, or greater than 1.  Falling out."
                        self.output_debug( debug_message, me, "++++++++" )
                        instance_OUT = None

                    #-- END check to see if mention already stored. --#
                    
                else:

                    # ERROR - no Article passed in.
                    debug_message = "ERROR - no Article instance passed in, no text in which we'd locate mention, so falling out."
                    self.output_debug( debug_message, me )
                    instance_OUT = None

                #-- END check to see if Article (article_IN) passed in.

            else:

                # ERROR - no Article_Subject passed in.
                debug_message = "ERROR - no Article_Subject instance passed in, can't attach Article_Subject_Quotation, so falling out."
                self.output_debug( debug_message, me )
                instance_OUT = None

            #-- END check to see if Article_Subject (article_subject_IN) passed in.

        else:

            # ERROR - no quotation string.
            debug_message = "ERROR - no quotation string passed in, nothing to process, falling out."
            self.output_debug( debug_message, me )
            instance_OUT = None

        #-- END check to see if quotation string (quotation_string_IN) passed in.
        
        return instance_OUT
        
    #-- END method process_mention() --#

        
    def process_newsbank_grpress_author_string( self, article_data_IN = None, author_string_IN = "" ):
    
        '''
        This method parses the contents of the parent article's author_string
           variable.  Breaks out the organizational affiliation portion of the
           author string (the part after the "/", then splits on commas and
           ampersands to detect multiple authors.  For each author, uses the
           NameParse object to parse their name into prefix/title, first name,
           middle name(s), last name, and suffix.  Looks first for an exact
           person match.  If one found, creates an Article_Author instance to
           link that person to this instance.  If none found, creates a new
           Person, associates it with this instance, then searches for
           potential duplicates, associating any found with the newly created
           Person record.  Should work for Detroit News articles from Newsbank
           as well, but their organizational affiliation is in body of article,
           so incomplete data...
        preconditions: Assumes that there is an associated article.  If not,
           there will be an exception.
        '''
        
        # return reference
        status_OUT = self.STATUS_SUCCESS
        
        # declare variables.
        me = "process_newsbank_grpress_author_string"
        status_message = ""
        status_message_list = []
        my_logger = None
        author_string = ""
        author_info = {}
        author_name_string = ""
        author_organization = ""
        author_name_list = []
        author_and_part = ""
        author_comma_part = ""
        author_name = ""
        article_author_instance = None
        process_author_name_status = ""
        my_capture_method = ""
        person_details = {}
        
        # get logger
        my_logger = self.get_logger()
        
        # get author_string
        author_string = author_string_IN
        
        # got Article_Data instance?
        if ( article_data_IN is not None ):
        
            # got an author string?
            if ( ( author_string is not None ) and ( author_string != "" ) ):
            
                # get capture method
                my_capture_method = article_data_IN.coder_type
                
                debug_message = "author string - \"" + author_string + "\""
                self.output_debug( debug_message, me )

                # parse author string.
                author_info = self.parse_author_string( author_string )
                
                debug_message = "parsed author_info = " + str( author_info )
                self.output_debug( debug_message, me )

                # retrieve information    
                author_name_string = author_info[ self.AUTHOR_INFO_AUTHOR_NAME_STRING ]
                author_organization = author_info[ self.AUTHOR_INFO_AUTHOR_AFFILIATION ]
                author_name_list = author_info[ self.AUTHOR_INFO_AUTHOR_NAME_LIST ]
                status_message = author_info[ self.AUTHOR_INFO_STATUS ]
                if ( ( status_message is not None ) and ( status_message != "" ) ):
                
                    # append to list.
                    status_message_list.append( status_message )
                    
                #-- END check to see if status message. --#

                # anything in the list?
                if ( ( author_name_list is not None ) and ( len( author_name_list ) > 0 ) ):

                    # For each name in array, see if we already have a matching
                    #    person.
                    for author_name in author_name_list:
                        
                        # call process_author_name() to deal with author.
                        person_details = PersonDetails()
                        person_details[ self.PARAM_PERSON_NAME ] = author_name
                        person_details[ self.PARAM_PERSON_ORGANIZATION ] = author_organization
                        person_details[ self.PARAM_TITLE ] = author_organization
                        article_author_instance = self.process_author_name( article_data_IN, author_name, person_details_IN = person_details )
                        process_author_name_status = article_author_instance.match_status
                        
                        # do anything with status?
                        if ( process_author_name_status != self.STATUS_SUCCESS ):

                            # append to status message list.
                            status_message_list.append( process_author_name_status )
                            
                        #-- END check to see if error status. --#
                    
                    #-- END loop over author names. --#
                
                #-- END check to see if list has anything in it. --#

            else:
            
                # No author string - error.
                status_message = self.STATUS_ERROR_PREFIX + "in " + me + ": no author string, so nothing to do."
                status_message_list.append( status_message )
            
            #-- END check to see if author string. --#
            
        else:
        
            # No Article_Data instance.
            status_message = self.STATUS_ERROR_PREFIX + "in " + me + ": no Article_Data instance, so no place to store author data."    
            status_message_list.append( status_message )        
        
        #-- END check to see if article data instance. --#
        
        # got status message(s)?
        if ( ( status_message_list is not None ) and ( len( status_message_list ) > 0 ) ):
        
            # yes.  Join into status_OUT.
            status_OUT = self.STATUS_LIST_DELIMITER.join( status_message_list )
            
        else:
        
            # no - return success.
            status_OUT = self.STATUS_SUCCESS
            
        #-- END check to see if anything in status_message_list --#
        
        return status_OUT
    
    #-- END method process_newsbank_grpress_author_string() --#


    def process_person_name( self,
                             article_data_IN,
                             person_name_IN,
                             person_details_IN = None,
                             article_person_class_IN = None ):

        '''
        Accepts Article_Data container, string person name, class of the
            child class of Article_Person to store the results in (defaults to
            None, which will cause an exception if not changed), and an optional
            (but effectively required) PersonDetails instance with more details
            on the person we are processing.
            
        If ID is present, tries to look up person based on ID.  If not, looks up
            person based on name.  If person found, only adds to Article_Data if
            that person does not already have an Article_Person child row 
            (Article_Subject or Article_Author, depending on the class passed in
            article_person_class_IN) already.  If person details present, uses
            details passed in when populating or updating person (see
            ArticleCoder.lookup_person() doc for values that can be passed in
            person details) and Article_Person child instance.
           
        preconditions: Assumes that there is an associated article in
            article_data_IN.  If not, there will be an exception.
           
        postconditions: If all goes well, results in Article_Person child
            instance for person passed in associated with Article_Data passed
            in, and returns the Article_Person child instance with status stored
            in "match_status" field.  If error, empty Article_Person child is
            created and returned with no ID, and match_status message describing
            the problem.  If person lookup works, but person already has an
            Article_Person child row, updates row to reflect any changes in
            person details since the row was originally created.
        '''
        
        # return reference
        article_person_OUT = None
        status_OUT = self.STATUS_SUCCESS
        
        # declare variables - input parameters, from person_details
        person_name_IN = ""
        fixed_person_name_IN = ""
        title_IN = ""
        organization_string_IN = ""
        coder_type_IN = ""
        person_id_IN = None
        article_person_id_IN = None
        capture_method_IN = ""
        
        # declare variables.
        me = "process_person_name"
        my_logger = None
        debug_message = ""
        
        # declare variables - person information
        article_person_instance = None
        person_name = ""
        person_verbatim_name = ""
        person_lookup_name = ""
        person_organization = None
        my_person_details = None
        my_capture_method = ""
        current_key = ""
        current_value = ""
        
        # declare variables - person lookup
        person_instance = None
        person_match_list = []
        article_person_qs = None
        article_person_count = -1
        article_person_instance = None
        
        # declare variables - update processing.
        article_person_id = -1
        do_save_updates = False
        existing_name = ""
        existing_lookup_name = ""
        existing_person = None
        existing_person_id = -1
        new_person_id = -1
        existing_title = ""
        existing_org_string = ""
        update_status = None

        # get logger
        my_logger = self.get_logger()
        
        # got an Article_Person descendent in article_person_class_IN?
        if ( article_person_class_IN is not None ):
        
            # make empty Article_Person descendent instance to work with, using
            #     class passed in.
            article_person_instance = article_person_class_IN()
                
            # is it an Article_Person decendent?
            if ( isinstance( article_person_instance, Article_Person ) == True ):
        
                debug_message = "--- In " + me + ": Article_Person class: \"" + str( article_person_class_IN ) + "\""
                my_logger.debug( debug_message )
        
                # initialize person_name variables.
                person_name = person_name_IN
                person_verbatim_name = person_name
                person_lookup_name = person_name
        
                # ! got PersonDetails?
                if ( ( person_details_IN is not None )
                     and ( isinstance( person_details_IN, dict ) == True )
                     and ( len( person_details_IN ) > 0 ) ):
                     
                    # details passed in - use them.
                    
                    # make sure we have PersonDetails instance, not just a dict(ionary).
                    my_person_details = PersonDetails.get_instance( person_details_IN )
                    
                    debug_message = "--- In " + me + ": processing \"" + person_name_IN + "\", FOUND person_details_IN: " + str( my_person_details )
                    my_logger.debug( debug_message )
                        
                else:
                
                    # nothing passed in - create new PersonDetails instance.
                    my_person_details = PersonDetails()
                
                    debug_message = "--- In " + me + ": processing \"" + person_name_IN + "\", NO person_details_IN."
                    my_logger.debug( debug_message )
        
                #-- END check to see if dictionary passed in. --#
                
                # got or made person details.  Retrieve input values.
                person_name_IN = my_person_details.get( self.PARAM_PERSON_NAME, "" )
                fixed_person_name_IN = my_person_details.get( self.PARAM_FIXED_PERSON_NAME, "" )
                title_IN = my_person_details.get( self.PARAM_TITLE, None )
                organization_string_IN = my_person_details.get( self.PARAM_PERSON_ORGANIZATION, None )
                coder_type_IN = my_person_details.get( self.PARAM_CAPTURE_METHOD, None )
                person_id_IN = my_person_details.get( self.PARAM_PERSON_ID, None )
                article_person_id_IN = my_person_details.get( self.PARAM_ARTICLE_PERSON_ID, None )
                capture_method_IN = my_person_details.get( self.PARAM_CAPTURE_METHOD, None )
                
                # if person name is populated in person details, it and fixed person
                #     name take precedence over any name passed in.  If not, just
                #     use the name passed in.
                if ( ( person_name_IN is not None ) and ( person_name_IN != "" ) ):
    
                    # we have a person name.  Set person_name, person_verbatim_name
                    #     to this value (person_name should always be the actual
                    #     verbatim mention of the person).
                    person_name = person_name_IN
                    person_verbatim_name = person_name
    
                    # what do we use to lookup?  If fixed_person_name, uses that, if
                    #     not, uses person_name.
                    person_lookup_name = my_person_details.get_lookup_name()
    
                #-- END check to see if person name passed in details --#

                debug_message = "--- In " + me + ": processing \"" + str( person_name_IN ) + "\", LOOKUP NAME = \"" + str( person_lookup_name)  + "\" (from person_details_IN)"
                my_logger.debug( debug_message )
        
                # got Article_Data instance?
                if ( article_data_IN is not None ):
                
                    # place Article_Data instance in article_person_instance.
                    article_person_instance.article_data = article_data_IN
                    
                    # got an person name or person ID?
                    if ( ( ( person_lookup_name is not None ) and ( person_lookup_name != "" ) )
                        or ( ( person_id_IN is not None ) and ( person_id_IN != "" ) and ( person_id_IN > 0 ) ) ):
                    
                        # get capture method - one in person details?
                        if ( ( capture_method_IN is not None ) and ( capture_method_IN != "" ) ):
                        
                            # use it.
                            my_capture_method = capture_method_IN
                        
                        # if no specific capture method passed in, see if coder
                        #     type present in the person details passed in.
                        elif ( ( coder_type_IN is not None ) and ( coder_type_IN != "" ) ):
                        
                            my_capture_method = coder_type_IN
                            
                        else:
                        
                            # no capture method or coder type passed in, use 
                            #     coder_type from Article_Data.
                            my_capture_method = article_data_IN.coder_type
                            
                        #-- END check for coder_type_IN --#
                
                        debug_message = "--- In " + me + ": Processing person name: \"" + person_lookup_name + "\" ( id: " + str( person_id_IN ) + " )"
                        my_logger.debug( debug_message )
                        
                        #--------------------------------------------------------------#
                        # ! update person details
                        #--------------------------------------------------------------#
                        
                        # prepare person details.
                        
                        # newspaper instance - only add if key not already in dictionary.
                        if self.PARAM_NEWSPAPER_INSTANCE not in my_person_details:
                        
                            # not there - add it.
                            my_person_details[ self.PARAM_NEWSPAPER_INSTANCE ] = article_data_IN.article.newspaper
                            
                        #-- END check to see if newspaper instance already in dict --#
        
                        # capture method - only add if key not already in dictionary.
                        current_key = self.PARAM_CAPTURE_METHOD
                        current_value = my_capture_method
                        if current_key not in my_person_details:
                        
                            # not there - got a value?
                            if ( ( current_value is not None ) and ( current_value != "" ) ):
                        
                                # got a value - add it.
                                my_person_details[ current_key ] = current_value
                                
                            #-- END check to see if we have a value --#
                            
                        #-- END check to see if capture method already in dict --#
                        
                        #--------------------------------------------------------------#
                        #-- Set person_organization. --#
                        #--------------------------------------------------------------#
        
                        # got one passed in?
                        if ( organization_string_IN is not None ):
                        
                            # got one passed in.  Use it.
                            person_organization = organization_string_IN
                            
                        #-- END setting person_organization --#
            
                        #--------------------------------------------------------------#
                        # ! do lookup
                        #--------------------------------------------------------------#
        
                        # lookup person - returns person and confidence score inside
                        #    Article_Person descendent instance.
                        article_person_instance = self.lookup_person( article_person_instance, 
                                                                      person_lookup_name,
                                                                      create_if_no_match_IN = True,
                                                                      update_person_IN = True,
                                                                      person_details_IN = my_person_details )
        
                        # retrieve information from Article_Person
                        person_instance = article_person_instance.person
                        person_match_list = article_person_instance.person_match_list  # list of Person instances
        
                        # got a person?
                        if ( person_instance is not None ):
                        
                            # Now, we need to deal with Article_Person descendent
                            #     instance.  Try to see if there is an existing
                            #     record we should update.
                            
                            # start with all records for class passed in...
                            article_person_qs = article_person_class_IN.objects.all()

                            # ...limit to those associated with the current
                            #     Article_Data...
                            article_person_qs = article_person_qs.filter( article_data = article_data_IN )

                            # See if there was the ID of an Article_Person child
                            #     record stored in the PersonDetails passed in.
                            
                            # got an article_person_id?
                            if ( ( article_person_id_IN is not None )
                                and ( article_person_id_IN != "" )
                                and ( int( article_person_id_IN ) > 0 ) ):
                            
                                # there is an ID.  Try to retrieve the specified
                                #     record.
                                article_person_id = int( article_person_id_IN )
                                article_person_qs = article_person_qs.filter( pk = article_person_id )
                                
                            else:
                            
                                # no ID - see if there is already an instance for 
                                #     the person we looked up.

                                # ...limit to the person we've looked up.
                                article_person_qs = article_person_qs.filter( person = person_instance )
                                
                            #-- END attempt to retrieve existing Article_Person instance --#
                            
                            # got anything?
                            article_person_count = article_person_qs.count()
                            if ( article_person_count == 1 ):

                                # ! UPDATE existing Article_Person child
                                do_save_updates = False

                                my_logger.debug( "In " + me + ": " + str( article_person_class_IN ) + " instance already exists for " + str( person_instance ) + "." )
                                
                                # retrieve article person from query set.
                                article_person_instance = article_person_qs.get()

                                # add a few things to person_details.
                                
                                # person instance
                                my_person_details[ PersonDetails.PROP_NAME_PERSON_INSTANCE ] = person_instance
                                
                                # update values in instance, don't save (happens
                                #    at the end).
                                article_person_instance.update_from_person_details( my_person_details, do_save_IN = False )
                                
                                #------------------------------------------------------#
                                # UPDATE alternate matches
        
                                # Were there alternate matches?
                                if ( len( person_match_list ) > 0 ):
                                
                                    # yes - store the list of alternate matches in the
                                    #    Article_Person child instance variable
                                    #    "person_match_list".
                                    article_person_instance.person_match_list = person_match_list
                                    
                                    # save calls process_alternate_matches().
                                    do_save_updates = True
                                    
                                    # call method to process alternate matches.
                                    my_logger.debug( "In " + me + ": @@@@@@@@ Existing " + str( article_person_class_IN ) + " found for person, calling process_alternate_matches as part of save()." )
                                    # article_person_instance.process_alternate_matches()
                                    
                                #-- END check to see if there were alternate matches --#
                                
                                #------------------------------------------------------#
                                # do we need to save?
        
                                if ( do_save_updates == True ):
                                
                                    # we do.
                                    # always saves at the end - article_person_instance.save()
                                    pass
                                
                                #-- END check to see if we need to save --#
                                
                            # ! either no match, or multiple (!)
                            elif ( ( article_person_count == 0 ) or ( article_person_count > 1 ) ):
                                                         
                                # ! INSERT new Article_Person child instance.
                                # no - add - including organization string.
        
                                # use instance already created above for call to
                                #     lookup_person().
                                #article_person_instance = article_person_class_IN()
                                
                                # add some things to my_person_details
                                
                                # Article_Data instance
                                my_person_details[ PersonDetails.PROP_NAME_ARTICLE_DATA_INSTANCE ] = article_data_IN
                                
                                # capture method
                                my_person_details[ PersonDetails.PROP_NAME_CAPTURE_METHOD ] = my_capture_method

                                # set notes to empty string.
                                my_person_details[ PersonDetails.PROP_NAME_NOTES ] = ""
     
                                # person instance
                                my_person_details[ PersonDetails.PROP_NAME_PERSON_INSTANCE ] = person_instance
        
                                # populate the instance, don't save (happens
                                #    at the end).
                                article_person_instance.update_from_person_details( my_person_details, do_save_IN = False )
        
                                # confidence level set in lookup_person() method.
                                #article_subject.match_confidence_level = 1.0
                                        
                                # save, and as part of save, record alternate matches.
                                # always saves at the end - article_person_instance.save()
                                
                                my_logger.debug( "In " + me + ": adding " + str( article_person_class_IN ) + " instance for " + str( person_instance ) + "." )
        
                                # greater then 1 match?
                                if ( article_person_count > 1 ):
                                
                                    # neither 0 or 1 person records - either invalid
                                    #     or multiple, and either ain't right.
                                    debug_message = "In " + me + ": " + str( article_person_class_IN ) + " count ( person instance = " + str( person_instance ) + "; article_person_id_IN = " + str( article_person_id_IN ) + " ) is " + str( article_person_count ) + ".  What to do?"
                                    my_logger.debug( debug_message )
                                    
                                    # update new instance from process_person_name
                                    status_OUT = self.STATUS_ERROR_PREFIX + " " + debug_message
                                    
                                #-- END check to see if more than 1 --#
            
                            #-- END check if need new Article_Person child instance --#
        
                        else:
                        
                            # No Person Found.
                            status_OUT = self.STATUS_ERROR_PREFIX + " in " + me + ": no matching person found - must have been a problem looking up name \"" + person_name + "\""            
                        
                            my_logger.debug( status_OUT )
        
                        #-- END check to see if person found. --#
                            
                    else:
                    
                        # No person string - error.
                        status_OUT = self.STATUS_ERROR_PREFIX + " in " + me + ": no person string, so nothing to do."
                    
                    #-- END check to see if person name. --#
                    
                    # since we have an article data, store status and save.
                    article_person_instance.match_status = status_OUT
                    article_person_instance.save()

                else:
                
                    # No Article_Data instance.
                    status_OUT = self.STATUS_ERROR_PREFIX + " in " + me + ": no Article_Data instance, so no place to store author data."            
                
                    # no article data, store status but don't save.
                    article_person_instance.match_status = status_OUT
                    #article_person_instance.save()
                
                #-- END check to see if article data instance. --#
                                
            else:
            
                debug_message = "--- In " + me + ": Class " + str( article_person_class_IN ) + " does not inherit from Article_Person class."
                my_logger.debug( debug_message )
                    
            #-- END check to see if instance of class passed in is an instance of Article_Person --#
            
        else:
        
            debug_message = "--- In " + me + ": No Article_Person class found."
            my_logger.debug( debug_message )
        
        #-- END check to see if class passed in is an Article_Person descendent --#
        
        # store article_person_instance in return reference.
        article_person_OUT = article_person_instance
        
        return article_person_OUT
    
    #-- END method process_person_name() --#


    def process_quotation( self,
                           article_IN,
                           article_subject_IN,
                           quotation_string_IN,
                           quotation_uuid_IN = "",
                           quotation_uuid_type_IN = "",
                           do_try_compact_IN = False ):
    
        '''
        Accepts Article, Article_Subject of a source, string quotation
           attributed to the source, and an optional uuid value and type.
           Checks to see if quotation string is already attributed to the
           source.  If so, returns Article_Subject_Quotation instance.
           If not, creates an Article_Subject_Quotation instance, populates
           it appropriately, then returns it.  If error, returns None.
           
        Preconditions:  Assumes article_IN, article_subject_IN ,and
           quotation_string_IN will be populated appropriately.  If any are
           missing or set to None, will break, throwing exceptions.  You should
           have already created and saved your Article_Subject before passing it
           to this method.
           
        Postconditions:  If quotation wasn't already stored, it will be after
           this call.
        '''
        
        # return reference
        instance_OUT = None
        
        # declare variables
        me = "process_quotation"
        debug_message = ""

        # declare variables - quotation details and lookup.
        quotation_string = ""
        quotation_length = ""
        quotation_qs = None
        quotation_count = -1
        current_quotation = None
        original_quotation_string = ""

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

        # initialize notes list.
        notes_list = []
        
        # got a quotation string?
        if ( ( quotation_string_IN is not None ) and ( quotation_string_IN != "" ) ):
        
            # strip white space
            quotation_string = quotation_string_IN.strip()

            # output string.
            debug_message = "Quotation: " + quotation_string
            self.output_debug( debug_message, me )

            # got Article_Subject?
            if ( article_subject_IN is not None ):

                # got Article?
                if ( article_IN is not None ):

                    # need to see if this quotation has already been stored.

                    # Filter on value in related Article_Subject_Quotation instances.
                    quotation_qs = article_subject_IN.article_subject_quotation_set.filter( value = quotation_string )
                                    
                    # got one?
                    quotation_count = quotation_qs.count()
                    if ( quotation_count == 0 ):
                                    
                        # no.  Create one.
                        current_quotation = Article_Subject_Quotation()
                        
                        # store the Article_Subject in it.
                        current_quotation.article_subject = article_subject_IN
                        
                        # length of the quotation string.
                        quotation_length = len( quotation_string )
                        
                        # store information we have so far
                        current_quotation.value = quotation_string
                        current_quotation.value_length = quotation_length
                        
                        # derive a few more details based on finding the quote in the text
                        #    of the article.
                        
                        # get article text for article.
                        article_text = article_IN.article_text_set.get()
                        
                        # then, call find_in_text (FIT) method.  When we deal with words, we
                        #    split on spaces.  Because of this, "words" must include the
                        #    punctuation around them for them to match.
                        quotation_FIT_values = article_text.find_in_text( quotation_string )
                        
                        # Validate results.
                        FIT_status_list = self.validate_FIT_results( quotation_FIT_values )

                        # any error statuses passed back?
                        FIT_status_count = len( FIT_status_list )
                        if ( FIT_status_count == 0 ):
                        
                            # None - success!
                            
                            debug_message = "FIT status was good - single match for each element we are looking for (string: " + quotation_string + ")."
                            self.output_debug( debug_message, me )

                            # get result lists.
                            canonical_index_list = quotation_FIT_values.get( Article_Text.FIT_CANONICAL_INDEX_LIST, [] )
                            plain_text_index_list = quotation_FIT_values.get( Article_Text.FIT_TEXT_INDEX_LIST, [] )
                            paragraph_list = quotation_FIT_values.get( Article_Text.FIT_PARAGRAPH_NUMBER_LIST, [] )
                            first_word_list = quotation_FIT_values.get( Article_Text.FIT_FIRST_WORD_NUMBER_LIST, [] )
                            last_word_list = quotation_FIT_values.get( Article_Text.FIT_LAST_WORD_NUMBER_LIST, [] )

                            # this is the normal case.  Save the values into our current
                            #    quotation instance.
                            
                            # ==> value_index
                            plain_text_index = plain_text_index_list[ 0 ]
                            
                            # ==> canonical index
                            canonical_index = canonical_index_list[ 0 ]
                            
                            # ==> value_word_number_start
                            first_word_number = first_word_list[ 0 ]
                            
                            # ==> value_word_number_end
                            last_word_number = last_word_list[ 0 ]

                            # ==> paragraph_number
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
                            found_list = article_text.find_in_plain_text( quotation_string )
                            found_list_count = len( found_list )
                            
                            # ! ==> do_try_compact_IN?
                            # got anything?  If no, do we try compacting white
                            #     space inside string?
                            if ( ( found_list_count == 0 ) and ( do_try_compact_IN == True ) ):
                            
                                # last ditch effort - compact white space inside
                                #    the string.
                                original_quotation_string = quotation_string
                                quotation_string = StringHelper.replace_white_space( string_IN = original_quotation_string,
                                                                                     replace_with_IN = " ",
                                                                                     use_regex_IN = True )
                                                                                     
                                # and try again - make sure the text is in the article.
                                found_list = article_text.find_in_plain_text( quotation_string )
                                found_list_count = len( found_list )
                            
                                # make note of compaction.
                                notes_string = "In " + me + ": searched in plain text for compacted quote ( original: \"" + original_quotation_string + "\"; compacted: \"" + quotation_string + "\" ): " + str( found_list )
                                notes_list.append( notes_string )
                                self.output_debug( notes_string )

                            #-- END check to see if match in plain text. --#
                            
                            # got anything now?
                            if ( found_list_count == 1 ):
                            
                                # we know we have one match, so we can dig in and try to get
                                #    all the things.
                                
                                #-----------------------------------------------------------
                                # plain text index
                                #-----------------------------------------------------------

                                # store the plain text index from check above.
                                plain_text_index = found_list[ 0 ]
                                
                                #-----------------------------------------------------------
                                # canonical index
                                #-----------------------------------------------------------

                                # canonical text seems to be a troublesome one.  Start out
                                #    looking for the full string.
                                found_list = article_text.find_in_canonical_text( quotation_string )
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
                                found_dict = article_text.find_in_word_list( quotation_string )
                                
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
                                found_list = article_text.find_in_paragraph_list( quotation_string )
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
                                

                            else:

                                # ERROR.
                                notes_string = "In " + me + ": ERROR - canonical index - search for quotation ( \"" + quotation_string + "\" ) either returned 0 or multiple matches: " + str( found_list )
                                notes_list.append( notes_string )
                                self.output_debug( notes_string )

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

                        # ==> capture method
                        current_quotation.capture_method = self.coder_type

                        # ==> uuid
                        if ( ( quotation_uuid_IN is not None ) and ( quotation_uuid_IN != "" ) ):
                            current_quotation.uuid = quotation_uuid_IN
                        #-- END check to see if we have a uuid. --#

                        # ==> uuid_name
                        if ( ( quotation_uuid_type_IN is not None ) and ( quotation_uuid_type_IN != "" ) ):
                            current_quotation.uuid_name = quotation_uuid_type_IN
                        #-- END check to see if we have uuid name (type) --#
                        
                        # notes?
                        if ( len( notes_list ) > 0 ):
                        
                            # yes - join with newline, add to notes.
                            notes_string = "\n".join( notes_list )
                            current_quotation.notes = notes_string
                            
                        #-- END check to see if notes. --#
                                    
                        # Deferring handling of attribution information for now.
                        # fields to track locations of data this coding was based on within
                        #    article.  References are based on results of ParsedArticle.parse().
                        #article_subject.attribution_verb_word_index = -1
                        #article_subject.attribution_verb_word_number = -1
                        #article_subject.attribution_paragraph_number = -1
                        #article_subject.attribution_speaker_name_string = -1
                        #article_subject.is_speaker_name_pronoun = False
                        #article_subject.attribution_speaker_name_index_range = ""
                        #article_subject.attribution_speaker_name_word_range = ""
                        
                        # save the quotation instance.
                        current_quotation.save()
                        
                        # and return it.
                        instance_OUT = current_quotation
                        
                    elif ( quotation_count == 1 ):
                    
                        # already got one.  Return it.
                        instance_OUT = quotation_qs.get()
                    
                    elif ( quotation_count > 1 ):
                    
                        # trouble more than one quotation for the quotation_string.
                        debug_message = "ERROR - more than one quotation matches string: \"" + quotation_string + "\".  Something is off..."
                        self.output_debug( debug_message, me, "++++++++" )
                        instance_OUT = None

                    else:
                    
                        # trouble - count is invalid.
                        debug_message = "ERROR - count of matches to string: \"" + quotation_string + "\" is neither 0, 1, or greater than 1.  Something is off..."
                        self.output_debug( debug_message, me, "++++++++" )
                        instance_OUT = None

                    #-- END check to see if quote already stored. --#

                else:

                    # ERROR - no Article passed in.
                    debug_message = "ERROR - no Article instance passed in, can't find position of quotation in text, so falling out."
                    self.output_debug( debug_message, me )
                    instance_OUT = None

                #-- END check to see if Article (article_IN) passed in.

            else:

                # ERROR - no Article_Subject passed in.
                debug_message = "ERROR - no Article_Subject instance passed in, can't attach Article_Subject_Quotation, so falling out."
                self.output_debug( debug_message, me )
                instance_OUT = None

            #-- END check to see if Article_Subject (article_subject_IN) passed in.

        else:

            # ERROR - no quotation string.
            debug_message = "ERROR - no quotation string passed in, nothing to process, falling out."
            self.output_debug( debug_message, me )
            instance_OUT = None

        #-- END check to see if quotation string (quotation_string_IN) passed in.
        
        return instance_OUT
        
    #-- END method process_quotation() --#

    
    def process_subject_name( self,
                              article_data_IN,
                              subject_name_IN = None,
                              person_details_IN = None,
                              do_create_name_mention_IN = True ):
    
        '''
        Accepts:
            - article_data_IN - Article_Data container for this set of coding.
            - subject_name_IN - name of subject we are processing.
            - person_details_IN - optional dictionary of pre-populated person information.  Defaults to None.  If None, just uses an empty one.
            - do_create_name_mention_IN - optional boolean, if True, tries to find name in article and capture its location in an Article_Mention, if False, does not.
        
        From person_details_IN, retrieves:
            - subject_UUID_IN - optional external Universal Unique IDentifier for subject.
            - subject_UUID_name_IN - optional name of the type of UUID passed in.
            - subject_UUID_source_IN - optional description of source of UUID.
            - coder_type_IN - optional coder type of coder who detected this subject.  If empty, uses coder type of article_data_IN.
            - subject_person_id_IN - optional ID of person to use for this subject, rather than looking up based on name.
        
        If ID is present, tries to look up person based on ID.  If not, looks up
            person based name.  If person found, only adds to Article_Data if
            that person does not already have an Article_Subject row.  If person
            not found, and if person details present, uses details passed in when
            populating person (see ArticleCoder.lookup_person() doc for values
            that can be passed in person details).
           
        preconditions: Assumes that there is an associated article in
            article_data_IN.  If not, there will be an exception.
           
        postconditions: If all goes well, results in Article_Subject for subject
            passed in associated with Article_Data passed in, and returns the
            Article_Subject instance with status stored in
            Article_Subject.match_status.  If error, empty Article_Subject is
            created and returned with no ID, and match_status message describing
            the problem.  If person lookup works, but person already has an
            Article_Subject row, does nothing.
        '''
        
        # return reference
        article_subject_OUT = None
        status_OUT = self.STATUS_SUCCESS
        
        # input variables from PersonDetails
        person_name_IN = ""
        fixed_person_name_IN = ""
        title_IN = ""
        organization_string_IN = ""
        subject_UUID_IN = ""
        subject_UUID_name_IN = ""
        subject_UUID_source_IN = ""
        coder_type_IN = ""
        subject_person_id_IN = None    # ID of Person previously associated with this name.
        subject_type_IN = ""
        article_person_id_IN = None    # ID of Article_Person descendent associated with this person, if one already created.

        # declare variables.
        me = "process_subject_name"
        my_logger = None
        debug_message = ""
        article_subject = None
        my_capture_method = ""

        # declare variable - set up person details
        my_person_details = None

        # declare variables - update existing Article_Subject
        existing_subject_type = ""
        my_article = None
        
        # declare variables - post-processing.
        person_verbatim_name = ""
        person_lookup_name = ""
        
        # get logger
        my_logger = self.get_logger()
        
        # ! got PersonDetails?
        if ( ( person_details_IN is not None )
            and ( isinstance( person_details_IN, dict ) == True )
            and ( len( person_details_IN ) > 0 ) ):
             
            # details passed in - use them.
            
            # Make sure we have PersonDetails instance, not just a dict(ionary).
            my_person_details = PersonDetails.get_instance( person_details_IN )
            
            debug_message = "--- In " + me + ": processing \"" + subject_name_IN + "\", FOUND person_details_IN: " + str( my_person_details )
            my_logger.debug( debug_message )
            
        else:
        
            # nothing passed in - create new PersonDetails.
            my_person_details = PersonDetails()
            
            debug_message = "--- In " + me + ": processing \"" + subject_name_IN + "\", NO person_details_IN."
            my_logger.debug( debug_message )

        #-- END check to see if dictionary passed in. --#

        # got or made person details.  Retrieve input values.
        person_name_IN = my_person_details.get( self.PARAM_PERSON_NAME, "" )
        fixed_person_name_IN = my_person_details.get( self.PARAM_FIXED_PERSON_NAME, "" )
        title_IN = my_person_details.get( self.PARAM_TITLE, "" )
        organization_string_IN = my_person_details.get( self.PARAM_PERSON_ORGANIZATION, "" )
        subject_UUID_IN = my_person_details.get( self.PARAM_EXTERNAL_UUID, "" )
        subject_UUID_name_IN = my_person_details.get( self.PARAM_EXTERNAL_UUID_NAME, "" )
        subject_UUID_source_IN = my_person_details.get( self.PARAM_EXTERNAL_UUID_SOURCE, "" )
        coder_type_IN = my_person_details.get( self.PARAM_CAPTURE_METHOD, "" )
        subject_person_id_IN = my_person_details.get( self.PARAM_PERSON_ID, None )
        subject_type_IN = my_person_details.get( self.PARAM_SUBJECT_TYPE, Article_Subject.SUBJECT_TYPE_MENTIONED )  # default to mentioned.
        article_person_id_IN = my_person_details.get( self.PARAM_ARTICLE_PERSON_ID, None )

        # got Article_Data instance?
        if ( article_data_IN is not None ):
        
            # ! call process_person_name()
            article_subject_OUT = self.process_person_name( article_data_IN,
                                                            person_name_IN,
                                                            person_details_IN = my_person_details,
                                                            article_person_class_IN = Article_Subject )
                                                           
            
                    
            # make sure we got an Article_Subject back.
            if ( article_subject_OUT is not None ):
            
                # initialize subject to "mentioned".
                article_subject_OUT.subject_type = Article_Subject.SUBJECT_TYPE_MENTIONED
            
                # get information from Article_Subject instance.
                my_article = article_data_IN.article
                person_lookup_name = article_subject_OUT.lookup_name
                person_verbatim_name = article_subject_OUT.verbatim_name
                
                # name mention?  Same for INSERT or UPDATE
                if ( do_create_name_mention_IN == True ):
                    
                    # add name mention to Article_Subject.  Use verbatim
                    #     name.
                    current_article_subject_mention = self.process_mention( my_article, article_subject_OUT, person_verbatim_name )
                    
                    # error?
                    if ( current_article_subject_mention is None ):

                        # yup - output debug message.
                        debug_message = "ERROR: Article_Coder.process_mention() returned None - problem processing name mention \"" + str( person_verbatim_name ) + "\" ( lookup name = \"" + str( person_lookup_name ) + "\" ).  See log for more details."
                        self.output_debug( debug_message, me )

                    #-- END check to see if error processing quotation --#

                #-- END check to see if we create name mention. --#

                # NEW - set to source type of individual.
                article_subject_OUT.source_type = Article_Subject.SOURCE_TYPE_INDIVIDUAL

                #article_subject_OUT.document = None
                article_subject_OUT.source_contact_type = Article_Subject.SOURCE_CONTACT_TYPE_OTHER
                #article_subject_OUT.source_capacity = None
                #article_subject_OUT.localness = None

                #------------------------------------------------------#
                # ==> subject_type
                
                # has subject type changed?
                existing_subject_type = article_subject_OUT.subject_type
                if ( subject_type_IN != existing_subject_type ):
                
                    # replace, and save.
                    article_subject_OUT.subject_type = subject_type_IN

                    # we need to save.
                    do_save_updates = True

                #-- END check to see if subject_type string changed --#

                # save, and as part of save, record alternate matches.
                article_subject_OUT.save()

            #-- END check to see if process_person_name() was a success --#
            
        else:
        
            # No Article_Data instance.
            status_OUT = self.STATUS_ERROR_PREFIX + " in " + me + ": no Article_Data instance, so no place to store subject data."            
        
            article_subject_OUT.match_status = status_OUT
            
            # can't save() without Article_Data.
            # article_subject_OUT.save()

        #-- END check to see if Article_Data instance. --#
                
        return article_subject_OUT
    
    #-- END method process_subject_name() --#

    
    def set_config_application( self, value_IN ):

        '''
        Accepts an application string name, stores value passed in, returns the
           value.
        '''
        
        # return reference
        value_OUT = None

        # declare variables

        # store value.
        self.config_application = value_IN
        
        # get return value
        value_OUT = self.get_config_application()

        return value_OUT

    #-- END set_config_application() --#


    def set_config_property( self, name_IN, value_IN ):
        
        # return reference
        value_OUT = ""
        
        # declare variables
        properties = {}
        
        # get properties
        properties = self.get_config_properties()
        
        # set property
        properties[ name_IN ] = value_IN
        
        # return new property value
        value_OUT = value_IN
        
        return value_OUT
        
    #-- END method set_config_property() --#
    

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


    def update_config_properties( self, props_IN ):
        
        # declare variables
        properties = {}
        
        # get properties
        properties = self.get_config_properties()
        
        # update the dictionary
        properties.update( props_IN )

    #-- END method update_config_properties() --#
    

    def update_person( self, person_IN, person_details_IN = PersonDetails(), allow_empty_IN = False, *args, **kwargs ):
        
        '''
        Accepts person instance, and then accepts dictionary of all the stuff you
           could place as additional detail to help disambiguate a person in
           person_details_IN.  Looks to see if this stuff has been associated
           with person.  If yes, does nothing.  If no, creates associations.
           Returns person.
           
        Person column values supported:
        
        - title (in parameter PARAM_TITLE) - if no title set for person passed in, places the title passed in into the title field and saves the Person instance.
        - organization (in parameter PARAM_PERSON_ORGANIZATION) - if no title set for person passed in, places the organization passed in into the title field and saves the Person instance.
        - capture_method (in parameter PARAM_CAPTURE_METHOD) - if no capture method for person passed in, places capture method from person_details there, then saves.
        
        Associations supported:
           
        - Person_Newspaper - columns:        
            - newspaper = models.ForeignKey( Newspaper, blank = True, null = True )
            - notes = models.TextField( blank = True, null = True )

        - Person_External_UUID - columns:
            - name = models.CharField( max_length = 255, null = True, blank = True )
            - UUID = models.TextField( blank = True, null = True )
            - source = models.CharField( max_length = 255, null = True, blank = True )
            - notes = models.TextField( blank = True, null = True )
            
        - Alternate_Name - columns:
            - same as Person, but with addition that these are child records of
               a person, to hold alternate names, so you can search against this 
               as well as Person.
            - pending...
        '''
        
        # return reference
        person_OUT = None
        
        # declare variables.
        me = "update_person"
        my_person_details = None
        do_save = False
        newspaper_IN = None
        newspaper_notes_IN = ""
        external_uuid_name_IN = ""
        external_uuid_IN = ""
        external_uuid_source_IN = ""
        external_uuid_notes_IN = ""
        title_IN = ""
        existing_title = ""
        organization_string_IN = ""
        existing_organization_string = ""
        capture_method_IN = ""
        existing_capture_method = ""
        
        self.output_debug( "Top of " + me + "(): person_IN: " + str( person_IN ) + "; person_details_IN: " + str( person_details_IN ), me, "========>" )
                
        # got a person?
        if ( person_IN is not None ):
        
            # place person into output reference
            person_OUT = person_IN
        
            # initialize do_save flag to False.
            do_save = False
        
            # make sure we have PersonDetails instance.
            my_person_details = PersonDetails.get_instance( person_details_IN )
        
            # get values from my_person_details
            newspaper_IN = my_person_details.get( self.PARAM_NEWSPAPER_INSTANCE, None )
            newspaper_notes_IN = my_person_details.get( self.PARAM_NEWSPAPER_NOTES, None )
            external_uuid_name_IN = my_person_details.get( self.PARAM_EXTERNAL_UUID_NAME, None )
            external_uuid_IN = my_person_details.get( self.PARAM_EXTERNAL_UUID, None )
            external_uuid_source_IN = my_person_details.get( self.PARAM_EXTERNAL_UUID_SOURCE, None )
            external_uuid_notes_IN = my_person_details.get( self.PARAM_EXTERNAL_UUID_NOTES, None )
            title_IN = my_person_details.get( self.PARAM_TITLE, "" )
            organization_string_IN = my_person_details.get( self.PARAM_PERSON_ORGANIZATION, "" )
            capture_method_IN = my_person_details.get( self.PARAM_CAPTURE_METHOD, "" )
            
            #------------------------------------------------------#
            # ==> newspaper

            # got a newspaper instance?
            if ( newspaper_IN is not None ):
            
                # Call Person.associate_newspaper - it handles checking to see if
                #    association is already present.
                person_OUT.associate_newspaper( newspaper_IN, newspaper_notes_IN )
            
            #-- END check to see if newspaper_IN present --#
            
            #------------------------------------------------------#
            # ==> UUID

            # got a UUID value?
            if ( ( external_uuid_IN is not None ) and ( external_uuid_IN != "" ) ):
            
                # we do.  Call Person.associate_external_uuid() - it handles
                #    checking if association is already present.
                person_OUT.associate_external_uuid( external_uuid_IN, external_uuid_source_IN, external_uuid_name_IN, external_uuid_notes_IN )
            
            #-- END check to see if external UUID --#

            #------------------------------------------------------#
            # ==> title

            # has title changed?
            existing_title = person_OUT.title
            if ( title_IN != existing_title ):
                
                # got a value, OR is empty OK?
                if ( ( ( title_IN is not None ) and ( title_IN != "" ) )
                    or ( allow_empty_IN == True ) ):

                    # yes.  Update title.
                    self.output_debug( "Updating title from: \"" + str( existing_title ) + "\" to: \"" + str( title_IN ) + "\"", me, "========>" )
                    person_OUT.set_title( title_IN, do_save_IN = False, do_append_IN = True )
                    self.output_debug( "Updated title: " + str( person_OUT.title ), me, "========>" )
    
                    # we need to save.
                    do_save = True
                    
                else:
                
                    self.output_debug( "NOT updating title from: \"" + str( existing_title ) + "\" to: \"" + str( title_IN ) + "\"", me, "========>" )
                
                #-- END check to see if we are OK to update --#

            else:
            
                # title unchanged
                self.output_debug( "No need to update title - existing: \"" + str( existing_title ) + "\"; new: \"" + str( title_IN ) + "\"", me, "========>" )
            
            #-- END check to see if title changed --#

            #------------------------------------------------------#
            # ==> organization_string

            # has organization string changed?
            existing_organization_string = person_OUT.organization_string
            if ( organization_string_IN != existing_organization_string ):

                # got a value, OR is empty OK?
                if ( ( ( organization_string_IN is not None ) and ( organization_string_IN != "" ) )
                    or ( allow_empty_IN == True ) ):

                    # yes.  Update organization string.
                    self.output_debug( "Updating organization string from: \"" + str( existing_organization_string ) + "\" to: \"" + str( organization_string_IN ) + "\"", me, "========>" )
                    person_OUT.set_organization_string( organization_string_IN, do_save_IN = False, do_append_IN = True )
                    self.output_debug( "Updated organization string: " + str( person_OUT.organization_string ), me, "========>" )
    
                    # we need to save.
                    do_save = True

                else:
                
                    self.output_debug( "NOT updating organization string from: \"" + str( existing_organization_string ) + "\" to: \"" + str( organization_string_IN ) + "\"", me, "========>" )
                
                #-- END check to see if we are OK to update --#

            else:
            
                # organization string unchanged.
                self.output_debug( "No need to update organization string - existing: \"" + str( existing_organization_string ) + "\"; new: \"" + str( organization_string_IN ) + "\"", me, "========>" )

            #-- END check to see if organization_string changed --#
            
            #------------------------------------------------------#
            # ==> capture_method

            # has capture method changed?
            existing_capture_method = person_OUT.capture_method
            if ( capture_method_IN != existing_capture_method ):

                # got a value, OR is empty OK?
                if ( ( ( capture_method_IN is not None ) and ( capture_method_IN != "" ) )
                    or ( allow_empty_IN == True ) ):

                    # yes.  Update capture_method.
                    self.output_debug( "Updating capture_method from: \"" + str( existing_capture_method ) + "\" to: \"" + str( capture_method_IN ) + "\"", me, "========>" )
                    person_OUT.set_capture_method( capture_method_IN )
                    self.output_debug( "Updated capture_method string: " + str( person_OUT.capture_method ), me, "========>" )
    
                    # we need to save.
                    do_save = True

                else:
                
                    self.output_debug( "NOT updating capture_method string from: \"" + str( existing_capture_method ) + "\" to: \"" + str( capture_method_IN ) + "\"", me, "========>" )
                
                #-- END check to see if we are OK to update --#

            else:
            
                # capture_method string unchanged.
                self.output_debug( "No need to update capture_method string - existing: \"" + str( existing_capture_method ) + "\"; new: \"" + str( capture_method_IN ) + "\"", me, "========>" )

            #-- END check to see if capture_method changed --#

            # do we need to save the person itself?
            if ( do_save == True ):
                
                # yes.  Save.
                #self.output_debug( "Saving updated person " + str( person_OUT ), me, "========>" )
                person_OUT.save()
                
            #-- END check to see if we need to save person instance --#

        #-- END check to see if person passed in --#

        return person_OUT
        
    #-- END method update_person() --#
    

    def validate_FIT_results( self, FIT_values_IN ):

        '''
        Accepts a dictionary of results from a Article_Text.find_in_text() call.
           Looks for problems (counts of nested lists not being 1, not being all
           the same).  If it finds problems, returns list of string messages 
           describing problems.  If no problems, returns empty list.
        '''
        
        # return reference
        status_list_OUT = []
        
        # call class method on Article_Text.
        status_list_OUT = Article_Text.validate_FIT_results( FIT_values_IN )
        
        return status_list_OUT        
        
    #-- END method validate_FIT_results() --#


#-- END class ArticleCoder --#