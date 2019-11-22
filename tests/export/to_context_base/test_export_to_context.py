f"""
This file contains tests of the context_text ExportToContext class.

Functions tested:


"""

# import six
import six

# django imports
import django.test
from django.utils.text import slugify

# context imports
from context.models import Entity
from context.models import Entity_Identifier
from context.models import Entity_Identifier_Type
from context.models import Entity_Type_Trait

# context_text imports
from context_text.export.to_context_base.export_to_context import ExportToContext
from context_text.models import Article
from context_text.shared.context_text_base import ContextTextBase
from context_text.tests.test_helper import TestHelper


class ExportToContextTest( django.test.TestCase ):
    

    #----------------------------------------------------------------------------
    # ! ----> Constants-ish
    #----------------------------------------------------------------------------


    # DEBUG
    DEBUG = False

    # CLASS NAME
    CLASS_NAME = "ExportToContextTest"
    
    # Entity Trait names
    TEST_ENTITY_TRAIT_NAME = "flibble_glibble_pants"
    ENTITY_TRAIT_NAME_FIRST_NAME = "first_name"
    ENTITY_TRAIT_NAME_MIDDLE_NAME = "middle_name"
    ENTITY_TRAIT_NAME_LAST_NAME = "last_name"
    
    # Identifier names
    TEST_IDENTIFIER_NAME = "nickname"
    
    # test IDs
    TEST_ID_1 = 21925
    TEST_ID_2 = 21409
    
    TEST_ID_LIST = []
    TEST_ID_LIST.append( TEST_ID_1 )
    TEST_ID_LIST.append( TEST_ID_2 )

    
    #----------------------------------------------------------------------
    # ! ----> class methods
    #----------------------------------------------------------------------


    #----------------------------------------------------------------------------
    # ! ----> instance methods
    #----------------------------------------------------------------------------


    def setUp( self ):
        
        """
        setup tasks.  Call function that we'll re-use.
        """

        # call TestHelper.standardSetUp()
        TestHelper.standardSetUp( self, fixture_list_IN = TestHelper.EXPORT_FIXTURE_LIST )

    #-- END function setUp() --#
        

    def test_setup( self ):

        """
        Tests whether there were errors in setup.
        """
        
        # declare variables
        me = "test_setup"
        error_count = -1
        error_message = ""
        
        print( '\n====> In {}.{}'.format( self.CLASS_NAME, me ) )
        
        # get setup error count
        setup_error_count = self.setup_error_count
        
        # should be 0
        error_message = ";".join( self.setup_error_list )
        self.assertEqual( setup_error_count, 0, msg = error_message )
        
    #-- END test method test_django_config_installed() --#


    def test_create_article_entity( self ):
        
        # declare variables
        me = "test_create_article_entity"
        debug_flag = None
        error_string = None

        # debug
        debug_flag = self.DEBUG

        print( '\n\n====> In {}.{}\n'.format( self.CLASS_NAME, me ) )
        print( "Testing of creating an article entity is implemented in: context_text/tests/models/test_Article_model.py --> test_update_entity" )
        print( "This method will be updated to include any functionality not handled by that method." )
                
    #-- END test method test_create_article_entity() --#


    def test_create_entity_container_entity( self ):
        
        # declare variables
        me = "test_create_entity_container_entity"
        debug_flag = None
        error_string = None

        # debug
        debug_flag = self.DEBUG

        print( '\n\n====> In {}.{}\n'.format( self.CLASS_NAME, me ) )
        print( "The create_entity_container_entity() method simply calls update_entity() on whatever instance is passed in.  Each class handles its own testing." )
        print( "This test method will be updated to include any functionality not handled by the update_entity() method." )
                
    #-- END test method test_create_entity_container_entity() --#


    def test_create_newspaper_relations( self ):
        
        # pick an article
        # create entities and make author, subject, and source lists from it
        # call method.
        # build trait dictionary just like in the method.
        # check relations.
        
    #-- END method test_create_newspaper_relations()


    def test_create_person_entity( self ):
        
        # declare variables
        me = "test_create_person_entity"
        debug_flag = None
        error_string = None

        # debug
        debug_flag = self.DEBUG

        print( '\n\n====> In {}.{}\n'.format( self.CLASS_NAME, me ) )
        print( "Testing of creating a person entity is implemented in: context_text/tests/models/test_Person_model.py --> test_update_entity" )
        print( "This method will be updated to include any functionality not handled by that method." )
                
    #-- END test method test_create_person_entity() --#


#-- END test class ExportToContextTest --#
