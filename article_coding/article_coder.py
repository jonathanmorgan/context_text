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

#import copy

# django config, for pulling in any configuration needed to connect to APIs, etc.

# import basic django configuration application.
from django_config.models import Config_Property

# python_utilities
from python_utilities.rate_limited.basic_rate_limited import BasicRateLimited

# Import the classes for our SourceNet application

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


    # status variables
    STATUS_OK = "OK!"
    STATUS_ERROR_PREFIX = "Error: "
    
    # debug
    DEBUG_FLAG = False


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


    #---------------------------------------------------------------------------
    # __init__() method
    #---------------------------------------------------------------------------


    def __init__( self ):

        # call parent's __init__()
        super( ArticleCoder, self ).__init__()

        # declare variables
        self.config_application = ""
        self.config_property_list = []
        self.config_properties = {}
    
        # rate-limiting
        self.do_manage_time = False
        self.rate_limit_in_seconds = -1
        self.rate_limit_daily_limit = -1
        
        # debug
        self.debug = ""
        
        # initialize configuration properties
        self.init_config_properties()
        
        # load properties
        self.load_config_properties()
        
    #-- END method __init__() --#


    #---------------------------------------------------------------------------
    # instance methods, in alphabetical order
    #---------------------------------------------------------------------------


    @abstractmethod
    def code_article( self, article_IN, *args, **kwargs ):

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

    #-- END abstract method code_article() --#
    

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
        status_OUT = self.STATUS_OK
        
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
    

    def update_config_properties( self, props_IN ):
        
        # declare variables
        properties = {}
        
        # get properties
        properties = self.get_config_properties()
        
        # update the dictionary
        properties.update( props_IN )

    #-- END method update_config_properties() --#
    

#-- END class ArticleCoder --#