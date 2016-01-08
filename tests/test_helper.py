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
from django.core.management import call_command

# import basic django configuration application.
from django_config.models import Config_Property

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
    
    
    #----------------------------------------------------------------------------
    # Class variables - overriden by __init__() per instance if same names, but
    #    if not set there, shared!
    #----------------------------------------------------------------------------


    #-----------------------------------------------------------------------------
    # class methods
    #-----------------------------------------------------------------------------


    @classmethod
    def load_fixture( cls, fixture_path_IN = "" ):
        
        # declare variables
        
        # got a fixture path?
        if ( ( fixture_path_IN is not None ) and ( fixture_path_IN != "" ) ):
        
            # got a path - try to load it.
            call_command( 'loaddata', fixture_path_IN, verbosity = 0 )
            
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