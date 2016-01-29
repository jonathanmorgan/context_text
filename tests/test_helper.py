from __future__ import unicode_literals

'''
Copyright 2010-2016 Jonathan Morgan

This file is part of http://github.com/jonathanmorgan/sourcenet.

sourcenet is free software: you can redistribute it and/or modify it under the terms of the GNU Lesser General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.

sourcenet is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.

You should have received a copy of the GNU Lesser General Public License along with http://github.com/jonathanmorgan/sourcenet. If not, see http://www.gnu.org/licenses/.
'''

__author__="jonathanmorgan"
__date__ ="$January 07, 2016 4:03:35 PM$"

if __name__ == "__main__":
    print "Hello World"

#===============================================================================
# imports (in alphabetical order by package, then by name)
#===============================================================================

# python libraries

# Django imports
from django.contrib.auth.models import User
from django.core.management import call_command

# import basic django configuration application.
from django_config.models import Config_Property

# python_utilities - logging
from python_utilities.logging.logging_helper import LoggingHelper

# sourcenet imports
from sourcenet.article_coding.open_calais_v2.open_calais_v2_article_coder import OpenCalaisV2ArticleCoder


#================================================================================
# Shared variables and functions
#================================================================================


#===============================================================================
# classes (in alphabetical order by name)
#===============================================================================

class TestHelper( object ):

    
    #----------------------------------------------------------------------------
    # CONSTANTS-ish
    #----------------------------------------------------------------------------


    # fixtures paths, in order they should be loaded.
    FIXTURE_UNIT_TEST_AUTH_DATA = "sourcenet/fixtures/sourcenet_unittest_auth_data.json"
    FIXTURE_UNIT_TEST_CONFIG_PROPERTIES = "sourcenet/fixtures/sourcenet_unittest_django_config_data.json"
    FIXTURE_UNIT_TEST_BASE_DATA = "sourcenet/fixtures/sourcenet_unittest_data.json"
    FIXTURE_UNIT_TEST_TAGGIT_DATA = "sourcenet/fixtures/sourcenet_unittest_taggit_data.json"
    
    # OpenCalais
    OPEN_CALAIS_ACCESS_TOKEN_FILE_NAME = "open_calais_access_token.txt"

    # Test user
    TEST_USER_NAME = "test_user"
    TEST_USER_EMAIL = "test@email.com"
    TEST_USER_PASSWORD = "calliope"

    # test authors
    TEST_AUTHOR_1 = "Nate Reems"
    TEST_AUTHOR_2 = "Nardy Baeza Bickel"
    TEST_AUTHOR_LIST = [ TEST_AUTHOR_1, TEST_AUTHOR_2 ]

    # test subjects
    TEST_SUBJECT_1 = "Alex McNamara"
    TEST_SUBJECT_2 = "Justin VanderVelde"
    TEST_SUBJECT_3 = "Pete Goodell"
    TEST_SUBJECT_4 = "Bob Dukesherer"
    TEST_SUBJECT_5 = "Steve Brown"
    TEST_SUBJECT_6 = "Rick DeGraaf"
    TEST_SUBJECT_LIST = [ TEST_SUBJECT_1, TEST_SUBJECT_2, TEST_SUBJECT_3, TEST_SUBJECT_4, TEST_SUBJECT_5, TEST_SUBJECT_6 ]

    # test quotations
    TEST_QUOTATION_1 = "The snow-covered runs are a beautiful sight to snowboarders Alex McNamara and Justin VanderVelde."
    TEST_QUOTATION_2 = "The Rockford friends, who have been practicing jumping and twirling tricks at Cannonsburg for a decade, said a \"long\" summer and fall left them eager to bust out their boards."


    #----------------------------------------------------------------------------
    # Class variables - overriden by __init__() per instance if same names, but
    #    if not set there, shared!
    #----------------------------------------------------------------------------

    
    DEBUG = True


    #-----------------------------------------------------------------------------
    # class methods
    #-----------------------------------------------------------------------------


    @classmethod
    def create_test_user( cls, username_IN = "" ):

        # return reference
        user_OUT = None

        # declare variables
        test_user = None
        test_username = ""

        # do we want non-standard username?
        if ( ( username_IN is not None ) and ( username_IN != "" ) ):

            test_username = username_IN

        else:

            test_username = cls.TEST_USER_NAME

        #-- END check to see if special user name. --#

        # create new test user
        test_user = User.objects.create_user( username = test_username,
                                              email = cls.TEST_USER_EMAIL,
                                              password = cls.TEST_USER_PASSWORD )
        test_user.save()

        user_OUT = test_user

        return user_OUT

    #-- END class method create_test_user() --#


    @classmethod
    def get_test_user( cls, username_IN = "" ):

        # return reference
        user_OUT = None

        # declare variables
        test_user = None
        test_username = ""

        # do we want non-standard username?
        if ( ( username_IN is not None ) and ( username_IN != "" ) ):

            test_username = username_IN

        else:

            test_username = cls.TEST_USER_NAME

        #-- END check to see if special user name. --#

        # try a lookup
        try:

            # by username
            user_OUT = User.objects.get( username = test_username )
        
        except Exception as e:
        
            # create new test user
            user_OUT = cls.create_test_user()

        #-- END try to get existing test user. --#

        return user_OUT

    #-- END class method get_test_user() --#


    @classmethod
    def load_fixture( cls, fixture_path_IN = "", verbosity_IN = 0 ):
        
        # declare variables
        
        # got a fixture path?
        if ( ( fixture_path_IN is not None ) and ( fixture_path_IN != "" ) ):
        
            # got a path - try to load it.
            call_command( 'loaddata', fixture_path_IN, verbosity = verbosity_IN )
            
        #-- END check to make sure we have a path --#
        
    #-- END function load_fixture() --#
    
    
    @classmethod
    def load_open_calais_access_token( cls, directory_path_IN = "" ):
        
        # return references
        value_OUT = ""
        
        # declare variables
        file_path = ""
        file_pointer = None
        file_contents = ""
        config_property_qs = None
        config_property_count = -1
        config_property = None
        
        # loading file with API key in it.  Start with standard file name.
        file_path = cls.OPEN_CALAIS_ACCESS_TOKEN_FILE_NAME
        
        # got a directory path?
        if ( ( directory_path_IN is not None ) and ( directory_path_IN != "" ) ):
        
            # got a path - add file name to the end of it.
            file_path = directory_path_IN + "/" + file_path
            
        #-- END check for path passed in. --#

        # open the file and read the contents.
        with open( file_path, "rU" ) as file_pointer:
        
            # read contents into a variable
            file_contents = file_pointer.read()
            file_contents = file_contents.strip()
        
        #-- END file processing --#
        
        # got anything?
        if ( ( file_contents is not None ) and ( file_contents != "" ) ):
        
            # yes - there are contents.  place in configuration property.
            
            # first, try to retrieve the config property.
            config_property_qs = Config_Property.objects.filter( application = OpenCalaisV2ArticleCoder.CONFIG_APPLICATION )
            config_property_qs = config_property_qs.filter( property_name = OpenCalaisV2ArticleCoder.CONFIG_PROP_OPEN_CALAIS_ACCESS_TOKEN )
            
            # got anything?
            config_property_count = config_property_qs.count()
            if ( config_property_count == 0 ):
            
                # no match.  Create the property...
                config_property = Config_Property()
                config_property.application = OpenCalaisV2ArticleCoder.CONFIG_APPLICATION
                config_property.property_name = OpenCalaisV2ArticleCoder.CONFIG_PROP_OPEN_CALAIS_ACCESS_TOKEN
                config_property.save()
                
                # ...and retrieve it into a QuerySet
                config_property_qs = Config_Property.objects.filter( pk = config_property.id )
                
            #-- END check to see if we have right number of things. --#
            
            # get() the property instance - Will throw exception if > 1.
            config_property = config_property_qs.get()
            
            # set value
            config_property.property_value = file_contents
            
            # save
            config_property.save()
        
        #-- END check to see if anything in the file --#
        
        value_OUT = file_contents
        
        return value_OUT
        
    #-- END function load_open_calais_access_token() --#
    
    
    @classmethod
    def output_debug( cls, message_IN, method_IN = "", indent_with_IN = "", logger_name_IN = "" ):
        
        '''
        Accepts message string.  If debug is on, logs it.  If not,
           does nothing for now.
        '''
        
        # declare variables
    
        # got a message?
        if ( message_IN ):
        
            # only print if debug is on.
            if ( cls.DEBUG == True ):
            
                # use Logging Helper to log messages.
                LoggingHelper.output_debug( message_IN, method_IN, indent_with_IN, logger_name_IN )
            
            #-- END check to see if debug is on --#
        
        #-- END check to see if message. --#
    
    #-- END method output_debug() --#
    
    
    @classmethod
    def standardOpenCalaisSetUp( cls, test_case_IN = None ):
        
        """
        setup tasks.  Call function that we'll re-use.
        """

        # declare variables
        me = "standardOpenCalaisSetUp"
        status_instance = None
        current_fixture = ""
        
        print( "\nIn TestHelper." + me + "(): starting standardOpenCalaisSetUp." )
        
        # see if test case passed in.  If so, set status variables on it.
        if ( test_case_IN is not None ):
        
            # not None, set status variables on it.
            status_instance = test_case_IN
            
        else:
        
            # no test case passed in.  Just set on self.
            status_instance = self
        
        #-- END check to see if test case --#

        # call standardSetup.
        cls.standardSetUp( status_instance )
        
        # Load OpenCalais Access Token.
        try:
        
            cls.load_open_calais_access_token()

        except Exception as e:
        
            # looks like there was a problem.
            status_instance.setup_error_count += 1
            status_instance.setup_error_list.append( OpenCalaisV2ArticleCoder.CONFIG_PROP_OPEN_CALAIS_ACCESS_TOKEN )
            
        #-- END try/except --#
        
        print( "In TestHelper." + me + "(): standardOpenCalaisSetUp complete." )

    #-- END function standardOpenCalaisSetUp() --#
        

    @classmethod
    def standardSetUp( cls, test_case_IN = None ):
        
        """
        setup tasks.  Call function that we'll re-use.
        """

        # declare variables
        me = "standardSetUp"
        status_instance = None
        current_fixture = ""
        
        print( "\nIn TestHelper." + me + "(): starting standardSetUp." )
        
        # see if test case passed in.  If so, set status variables on it.
        if ( test_case_IN is not None ):
        
            # not None, set status variables on it.
            status_instance = test_case_IN
            
        else:
        
            # no test case passed in.  Just set on self.
            status_instance = self
        
        #-- END check to see if test case --#
        
        # janky way to add variables to instance since you can't override init.
        status_instance.setup_error_count = 0
        status_instance.setup_error_list = []
        
        # Load auth data fixture
        current_fixture = cls.FIXTURE_UNIT_TEST_AUTH_DATA
        try:
        
            cls.load_fixture( current_fixture )

        except Exception as e:
        
            # looks like there was a problem.
            status_instance.setup_error_count += 1
            status_instance.setup_error_list.append( current_fixture )
            
        #-- END try/except --#
        
        # Load config property data fixture
        current_fixture = cls.FIXTURE_UNIT_TEST_CONFIG_PROPERTIES
        try:
        
            cls.load_fixture( current_fixture )

        except Exception as e:
        
            # looks like there was a problem.
            status_instance.setup_error_count += 1
            status_instance.setup_error_list.append( current_fixture )
            
        #-- END try/except --#
        
        # Load base unit test data fixture
        current_fixture = cls.FIXTURE_UNIT_TEST_BASE_DATA
        try:
        
            cls.load_fixture( current_fixture )
        

        except Exception as e:
        
            # looks like there was a problem.
            status_instance.setup_error_count += 1
            status_instance.setup_error_list.append( current_fixture )
            
        #-- END try/except --#
        
        # Load taggit tag data fixture
        current_fixture = cls.FIXTURE_UNIT_TEST_TAGGIT_DATA
        try:
        
            cls.load_fixture( current_fixture )

        except Exception as e:
        
            # looks like there was a problem.
            status_instance.setup_error_count += 1
            status_instance.setup_error_list.append( current_fixture )
            
        #-- END try/except --#
        
        print( "In TestHelper." + me + "(): standardSetUp complete." )

    #-- END function standardSetUp() --#
        

    #----------------------------------------------------------------------------
    # __init__() method
    #----------------------------------------------------------------------------


    def __init__( self ):

        # call parent's __init__()
        super( TestHelper, self ).__init__()

    #-- END method __init__() --#


    #----------------------------------------------------------------------------
    # instance methods, in alphabetical order
    #----------------------------------------------------------------------------


#-- END class TestHelper --#