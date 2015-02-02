from __future__ import unicode_literals

'''
Copyright 2010-2014 Jonathan Morgan

This file is part of http://github.com/jonathanmorgan/sourcenet.

sourcenet is free software: you can redistribute it and/or modify it under the terms of the GNU Lesser General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.

sourcenet is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.

You should have received a copy of the GNU Lesser General Public License along with http://github.com/jonathanmorgan/sourcenet. If not, see http://www.gnu.org/licenses/.
'''

__author__="jonathanmorgan"
__date__ ="$November 26, 2014 3:03:35 PM$"

if __name__ == "__main__":
    print "Hello World"

#===============================================================================
# imports (in alphabetical order by package, then by name)
#===============================================================================

# python libraries
from abc import ABCMeta, abstractmethod
import logging
#import copy
import re

# Django imports
from django.contrib.auth.models import User

# django config, for pulling in any configuration needed to connect to APIs, etc.

# import basic django configuration application.
from django_config.models import Config_Property

# python_utilities
from python_utilities.exceptions.exception_helper import ExceptionHelper
from python_utilities.rate_limited.basic_rate_limited import BasicRateLimited

# Import the classes for our SourceNet application
from sourcenet.models import Article_Author
from sourcenet.models import Person

#================================================================================
# Shared variables and functions
#================================================================================


#===============================================================================
# classes (in alphabetical order by name)
#===============================================================================

class ArticleCoder( BasicRateLimited ):

    
    #---------------------------------------------------------------------------
    # META!!!
    #---------------------------------------------------------------------------

    
    __metaclass__ = ABCMeta


    #---------------------------------------------------------------------------
    # CONSTANTS-ish
    #---------------------------------------------------------------------------


    # status constants
    STATUS_SUCCESS = "Success!"    
    STATUS_ERROR_PREFIX = "Error: "

    # DEPRECATED STATUSES - DO NOT USE IN NEW CODE
    STATUS_OK = "OK!"

    # debug
    DEBUG_FLAG = False
    
    # coder user
    CODER_USERNAME_AUTOMATED = "automated"
    CODER_USER_AUTOMATED = None
    
    # config parameters
    PARAM_AUTOPROC_ALL = "autoproc_all"
    PARAM_AUTOPROC_AUTHORS = "autoproc_authors"
    
    # author string processing
    REGEX_BEGINS_WITH_BY = re.compile( r'^BY ', re.IGNORECASE )


    #---------------------------------------------------------------------------
    # instance variables
    #---------------------------------------------------------------------------


    # cofiguration parameters
    config_application = ""
    config_property_list = []
    config_properties = {}
    
    # rate-limiting - in BasicRateLimited
    #do_manage_time = False
    #rate_limit_in_seconds = -1
    #rate_limit_daily_limit = -1
    
    # debug
    debug = ""

    # exception helper.
    exception_helper = None
    
    
    #----------------------------------------------------------------------------
    # class methods
    #----------------------------------------------------------------------------


    @classmethod
    def get_automated_coding_user( cls, *args, **kwargs ):
    
        '''
        Can't reference django models in class context anymore in models files:
            http://stackoverflow.com/questions/25537905/django-1-7-throws-django-core-exceptions-appregistrynotready-models-arent-load
        So, this method gets User instance for automated user username instead.
        '''
        
        # return reference
        user_OUT = None

        # declare variables
        temp_user = None
        
        # User already retrieved?
        if ( cls.CODER_USER_AUTOMATED == None ):
        
            # get user
            temp_user = User.objects.get( username = cls.CODER_USERNAME_AUTOMATED )
            
            # store it
            cls.CODER_USER_AUTOMATED = temp_user
            
        #-- END check to see if user already stored in class. --#

        # return it.
        user_OUT = cls.CODER_USER_AUTOMATED

        return user_OUT
        
    #-- END class method get_automated_coding_user() --#
    
    
    #---------------------------------------------------------------------------
    # __init__() method
    #---------------------------------------------------------------------------


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
        my_exception_helper = ExceptionHelper()
        #my_exception_helper.set_logging_level( logging.DEBUG )
        self.set_exception_helper( my_exception_helper )

        # initialize configuration properties
        self.init_config_properties()
        
        # load properties
        self.load_config_properties()
        
        # set logger name (for LoggingHelper parent class: (LoggingHelper -->
        #    BasicRateLimited --> ArticleCoder).
        self.set_logger_name( "sourcenet.article_coding.article_coder" )

    #-- END method __init__() --#


    #---------------------------------------------------------------------------
    # instance methods, in alphabetical order
    #---------------------------------------------------------------------------


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
        debug_string = ""
        
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
    
    
    def output_debug( self, message_IN ):
    
        '''
        Accepts message string.  If debug is on, passes it to print().  If not,
           does nothing for now.
        '''
        
        # declare variables
        my_logger = None
    
        # got a message?
        if ( message_IN ):
        
            # get logger
            my_logger = self.get_logger()
            
            # only print if debug is on.
            if ( self.DEBUG_FLAG == True ):
            
                # debug is on.  log it.
                my_logger.debug( message_IN )
            
            #-- END check to see if debug is on --#
        
        #-- END check to see if message. --#
    
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
        my_logger = None
        author_string = ""
        author_parts = None
        author_parts_length = -1
        author_organization = ""
        author_name_list = []
        author_and_part = ""
        author_comma_part = ""
        author_name = ""
        author_person = None
        article_author = None
        article_author_qs = None
        
        # get logger
        my_logger = self.get_logger()
        
        # get author_string
        author_string = author_string_IN
        
        # got Article_Data instance?
        if ( article_data_IN is not None ):
        
            # got an author string?
            if ( ( author_string is not None ) and ( author_string != "" ) ):
            
                my_logger.debug( "--- In " + me + ": Processing author string: \"" + author_string + "\"" )
                
                # got an author string.  Parse it.  First, break out organization.
                # split author string on "/"
                author_parts = author_string.split( '/' )
                
                # got two parts?
                author_parts_length = len( author_parts )
                if ( author_parts_length == 2 ):
                
                    # we do.  2nd part = organization
                    author_organization = author_parts[ 1 ]
                    author_organization = author_organization.strip()
                    
                    # first part is author string we look at going forward.
                    author_string = author_parts[ 0 ]
                    author_string = author_string.strip()
                    
                    # also, if string starts with "By ", remove it.
                    author_string = re.sub( self.REGEX_BEGINS_WITH_BY, "", author_string )
                    
                elif ( ( author_parts_length == 0 ) or ( author_parts_length > 2 ) ):
                
                    # error.  what to do?
                    status_OUT = self.STATUS_ERROR_PREFIX + " in " + me + ": splitting on '/' resulted in either an empty array or more than two things.  This isn't right ( " + my_article.author_string + " )."
                    
                #-- END check results of splitting on "/"
                
                # Got something in author_string?
                if ( ( author_string is not None ) and ( author_string != "" ) ):
    
                    # after splitting, we have a string.  Now need to split on
                    #    "," and " and ".  First, split on " and ".
                    for author_and_part in author_string.split( " and " ):
                    
                        # try splitting on comma.
                        author_parts = author_and_part.split( "," )
                        
                        # got any?
                        if ( len( author_parts ) > 0 ):
                        
                            # yes.  Add each as a name.
                            for author_comma_part in author_parts:
                            
                                # add name to list of names.
                                author_name_list.append( author_comma_part )
                                
                            #-- END loop over authors separated by commas. --#
                            
                        else:
                        
                            # no comma-delimited names.  Add current string to
                            #    name list.
                            author_name_list.append( author_and_part )
                            
                        #-- END check to see if comma-delimited names --#
                        
                    #-- END loop over and-delimited split of authors --#
                    
                    # time to start testing.  Print out the array.
                    my_logger.debug( "In " + me + ": Author list: " + str( author_name_list ) )
    
                    # For each name in array, see if we already have a matching
                    #    person.
                    for author_name in author_name_list:
                    
                        # first, call Person method to find matching person for
                        #    name.
                        author_person = Person.get_person_for_name( author_name, True )
                        
                        # got a person?
                        if ( author_person ):
    
                            # if no ID, is new.  Save to database.
                            if ( not( author_person.id ) ):
                            
                                # no ID.  Save the record.
                                author_person.save()
                                my_logger.debug( "In " + me + ": saving new person - " + str( author_person ) )
                                
                            #-- END check to see if new Person. --#
                            
                            # Now, we need to deal with Article_Author instance.
                            #    First, see if there already is one for this
                            #    name.  If so, do nothing.  If not, make one.
                            article_author_qs = article_data_IN.article_author_set.filter( person = author_person )
                            
                            # got anything?
                            if ( article_author_qs.count() == 0 ):
                                                         
                                # no - add - including organization string.
                                article_author = Article_Author()
                                article_author.article_data = article_data_IN
                                article_author.person = author_person
                                article_author.organization_string = author_organization
                                article_author.save()
                                
                                my_logger.debug( "In " + me + ": adding Article_Author instance for " + str( author_person ) + "." )
    
                            else:
                            
                                my_logger.debug( "In " + me + ": Article_Author instance already exists for " + str( author_person ) + "." )
                                
                            #-- END check if need new Article_Author instance --#
    
                        else:
                        
                            my_logger.debug( "In " + me + ": error - no matching person found - must have been a problem looking up name \"" + author_name + "\"" )
    
                        #-- END check to see if person found. --#
                    
                    #-- END loop over author names. --#
    
                else:                
                    
                    # error.  what to do?
                    status_OUT = self.STATUS_ERROR_PREFIX + "in " + me + ": after splitting on '/', no author string left.  Not a standard byline ( " + author_string + " )."
    
                #-- END check to see if anything in author string.
            
            else:
            
                # No author string - error.
                status_OUT = self.STATUS_ERROR_PREFIX + "in " + me + ": no author string, so nothing to do."
            
            #-- END check to see if author string. --#
            
        else:
        
            # No Article_Data instance.
            status_OUT = self.STATUS_ERROR_PREFIX + "in " + me + ": no Article_Data instance, so no place to store author data."            
        
        #-- END check to see if article data instance. --#
        
        return status_OUT
    
    #-- END method process_author_string() --#


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
    

#-- END class ArticleCoder --#