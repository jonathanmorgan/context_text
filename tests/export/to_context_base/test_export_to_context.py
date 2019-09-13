f"""
This file contains tests of the context_text ExportToContext class.

Functions tested:


"""

# import six
import six

# django imports
import django.test

# context imports
from context.models import Entity
from context.models import Entity_Identifier
from context.models import Entity_Identifier_Type

# context_text imports
from context_text.export.to_context_base.export_to_context import ExportToContext
from context_text.models import Article
from context_text.tests.test_helper import TestHelper


class ExportToContextTest( django.test.TestCase ):
    

    #----------------------------------------------------------------------------
    # ! ----> Constants-ish
    #----------------------------------------------------------------------------


    # CLASS NAME
    CLASS_NAME = "ExportToContextTest"

    # identifier type names
    IDENTIFIER_TYPE_NAME_ARTICLE_NEWSBANK_ID = "article_newsbank_id"
    IDENTIFIER_TYPE_NAME_ARTICLE_SOURCENET_ID = "article_sourcenet_id"
    IDENTIFIER_TYPE_NAME_PERSON_OPEN_CALAIS_UUID = "person_open_calais_uuid"    
    IDENTIFIER_TYPE_NAME_PERSON_SOURCENET_ID = "person_sourcenet_id"
    IDENTIFIER_TYPE_NAME_DOES_NOT_EXIST = "calliope_tree_frog"
    
    # map of identifier type names to test IDs
    IDENTIFIER_TYPE_NAME_TO_ID_MAP = {}
    IDENTIFIER_TYPE_NAME_TO_ID_MAP[ IDENTIFIER_TYPE_NAME_PERSON_SOURCENET_ID ] = 1
    IDENTIFIER_TYPE_NAME_TO_ID_MAP[ IDENTIFIER_TYPE_NAME_PERSON_OPEN_CALAIS_UUID ] = 2
    IDENTIFIER_TYPE_NAME_TO_ID_MAP[ IDENTIFIER_TYPE_NAME_ARTICLE_SOURCENET_ID ] = 3
    IDENTIFIER_TYPE_NAME_TO_ID_MAP[ IDENTIFIER_TYPE_NAME_ARTICLE_NEWSBANK_ID ] = 4
    
    # Entity Type slugs
    ENTITY_TYPE_SLUG_PERSON = "person"
    ENTITY_TYPE_SLUG_ARTICLE = "article"
    ENTITY_TYPE_SLUG_NEWSPAPER = "newspaper"
    
    # Entity Trait names
    TEST_ENTITY_TRAIT_NAME = "flibble_glibble_pants"
    ENTITY_TRAIT_NAME_FIRST_NAME = "first_name"
    ENTITY_TRAIT_NAME_MIDDLE_NAME = "middle_name"
    ENTITY_TRAIT_NAME_LAST_NAME = "last_name"
    
    # Identifier names
    TEST_IDENTIFIER_NAME = "nickname"
    
    # identifier type names
    ID_TYPE_NAME_SOURCENET = "person_sourcenet_id"
    ID_TYPE_NAME_OPENCALAIS = "person_open_calais_uuid"
    
    # test Article IDs
    TEST_ARTICLE_ID_1 = 21925
    TEST_ARTICLE_ID_2 = 21409

    # local fixtures
    FIXTURE_UNIT_TEST_AUTH_DATA = "context_text/fixtures/context_text_unittest_export_auth_data.json"
    FIXTURE_UNIT_TEST_CONFIG_PROPERTIES = TestHelper.FIXTURE_UNIT_TEST_CONFIG_PROPERTIES
    FIXTURE_UNIT_TEST_BASE_DATA = "context_text/fixtures/context_text_unittest_export_data.json"
    FIXTURE_UNIT_TEST_TAGGIT_DATA = "context_text/fixtures/context_text_unittest_export_taggit_data.json"
    FIXTURE_UNIT_TEST_CONTEXT_BASE = "context/fixtures/context-sourcenet_entities_and_relations.json"

    # list of fixtures, in order.
    FIXTURE_LIST = []
    FIXTURE_LIST.append( FIXTURE_UNIT_TEST_AUTH_DATA )
    FIXTURE_LIST.append( FIXTURE_UNIT_TEST_CONFIG_PROPERTIES )
    FIXTURE_LIST.append( FIXTURE_UNIT_TEST_BASE_DATA )
    FIXTURE_LIST.append( FIXTURE_UNIT_TEST_TAGGIT_DATA )
    FIXTURE_LIST.append( FIXTURE_UNIT_TEST_CONTEXT_BASE )
    
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
        TestHelper.standardSetUp( self, fixture_list_IN = self.FIXTURE_LIST )

    #-- END function setUp() --#
        

    def test_setup( self ):

        """
        Tests whether there were errors in setup.
        """
        
        # declare variables
        me = "test_setup"
        error_count = -1
        error_message = ""
        
        print( '====> In {}.{}'.format( self.CLASS_NAME, me ) )
        
        # get setup error count
        setup_error_count = self.setup_error_count
        
        # should be 0
        error_message = ";".join( self.setup_error_list )
        self.assertEqual( setup_error_count, 0, msg = error_message )
        
    #-- END test method test_django_config_installed() --#


    def test_create_article_entity( self ):
        
        # declare variables
        me = "test_create_article"
        error_string = None
        my_exporter = None
        article_1_id = None
        article_1_instance = None
        entity_1_instance = None
        entity_1_id = None
        test_entity_instance = None
        test_entity_id = None
        id_type = None
        type_slug_1 = None
        type_slug_2 = None
        type_qs = None
        type_count = None
        should_be = None

        print( '====> In {}.{}'.format( self.CLASS_NAME, me ) )
        
        my_exporter = ExportToContext()

        # initialize
        id_type = my_exporter.set_article_uuid_id_type_name( ExportToContext.ENTITY_ID_TYPE_ARTICLE_NEWSBANK_ID )
        print( "--------> ID type: {}".format( id_type ) )
        print( "All types:" )
        for current_type in Entity_Identifier_Type.objects.all():
        
            print( "- {}".format( current_type ) )
            
        #-- END loop over all types to test loading of fixture --#

        # retrieve test article 1
        article_1_id = self.TEST_ARTICLE_ID_1
        article_1_instance = Article.objects.get( id = article_1_id )
        
        # create entity for it.
        entity_1_instance = my_exporter.create_article_entity( article_1_instance )
        entity_1_id = entity_1_instance.id
        
        # do some tests.
        id_type = Entity_Identifier_Type.get_type_for_name( self.IDENTIFIER_TYPE_NAME_PERSON_SOURCENET_ID )
        test_entity_instance = Entity.get_entity_for_identifier( article_1_id, id_type_IN = id_type )
        test_entity_id = test_entity_instance.id
        
        # returned entity should have same ID as entity_1_instance.
        should_be = entity_1_id
        error_string = "article entity 1: Article id: {} --> retrieved entity ID: {}; should be ID: {}".format( article_1_id, test_entity_id, should_be )
        self.assertEqual( article_1_id, should_be, msg = error_string )
        
        # check newspaper ID
        
        # check unique_identifier
        
        # article_archive_identifier
        
        # newsbank ID
        
    #-- END test method test_create_article_entity() --#


    def test_get_article_uuid_id_type( self ):
        
        # ! TODO
        pass
        
    #-- END test method test_get_article_uuid_id_type --#
        
    
    def test_set_article_uuid_id_type_name( self ):
        
        # ! TODO
        pass
        
    #-- END test method test_set_article_uuid_id_type_name --#
        
    
#-- END test class ExportToContextTest --#
