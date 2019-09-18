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
from context_text.tests.test_helper import TestHelper


class ExportToContextTest( django.test.TestCase ):
    

    #----------------------------------------------------------------------------
    # ! ----> Constants-ish
    #----------------------------------------------------------------------------


    # DEBUG
    DEBUG = False

    # CLASS NAME
    CLASS_NAME = "ExportToContextTest"

    # identifier type names
    IDENTIFIER_TYPE_NAME_ARTICLE_NEWSBANK_ID = "article_newsbank_id"
    IDENTIFIER_TYPE_NAME_ARTICLE_SOURCENET_ID = "article_sourcenet_id"
    IDENTIFIER_TYPE_NAME_ARTICLE_ARCHIVE_IDENTIFIER = "article_archive_identifier"
    IDENTIFIER_TYPE_NAME_PERMALINK = "permalink"
    IDENTIFIER_TYPE_NAME_PERSON_OPEN_CALAIS_UUID = "person_open_calais_uuid"    
    IDENTIFIER_TYPE_NAME_PERSON_SOURCENET_ID = "person_sourcenet_id"
    IDENTIFIER_TYPE_NAME_DOES_NOT_EXIST = "calliope_tree_frog"
    
    # map of identifier type names to test IDs
    IDENTIFIER_TYPE_NAME_TO_ID_MAP = {}
    IDENTIFIER_TYPE_NAME_TO_ID_MAP[ IDENTIFIER_TYPE_NAME_PERSON_SOURCENET_ID ] = 1
    IDENTIFIER_TYPE_NAME_TO_ID_MAP[ IDENTIFIER_TYPE_NAME_PERSON_OPEN_CALAIS_UUID ] = 2
    IDENTIFIER_TYPE_NAME_TO_ID_MAP[ IDENTIFIER_TYPE_NAME_ARTICLE_SOURCENET_ID ] = 3
    IDENTIFIER_TYPE_NAME_TO_ID_MAP[ IDENTIFIER_TYPE_NAME_ARTICLE_NEWSBANK_ID ] = 4
    IDENTIFIER_TYPE_NAME_TO_ID_MAP[ IDENTIFIER_TYPE_NAME_PERMALINK ] = 5
    IDENTIFIER_TYPE_NAME_TO_ID_MAP[ IDENTIFIER_TYPE_NAME_ARTICLE_ARCHIVE_IDENTIFIER ] = 6
    
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
        
        print( '\n====> In {}.{}'.format( self.CLASS_NAME, me ) )
        
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
        article_1_newspaper = None
        article_1_newspaper_id = None
        article_1_pub_date = None
        article_1_unique_identifier = None
        article_1_archive_source = None
        article_1_archive_id = None
        entity_1_instance = None
        entity_1_id = None
        entity_1_type = None
        test_entity_instance = None
        test_entity_id = None
        id_type = None
        type_slug_1 = None
        type_slug_2 = None
        type_qs = None
        type_count = None
        should_be = None

        # declare variables - loading traits
        trait_name = None
        trait_definition_qs = None
        trait_definition = None
        test_entity_trait = None
        test_entity_trait_value = None
        test_identifier_name = None
        test_identifier_type = None
        test_identifier = None
        test_identifier_uuid = None
        test_identifier_source = None

        # debug
        debug_flag = self.DEBUG

        print( '\n====> In {}.{}'.format( self.CLASS_NAME, me ) )
        
        my_exporter = ExportToContext()

        # initialize
        id_type = my_exporter.set_article_uuid_id_type_name( ExportToContext.ENTITY_ID_TYPE_ARTICLE_NEWSBANK_ID )
        
        if ( debug_flag == True ):
            print( "--------> ID type: {}".format( id_type ) )
            print( "All types:" )
            for current_type in Entity_Identifier_Type.objects.all():
            
                print( "- {}".format( current_type ) )
                
            #-- END loop over all types to test loading of fixture --#
        #-- END DEBUG --#

        # retrieve test article 1
        article_1_id = self.TEST_ARTICLE_ID_1
        article_1_instance = Article.objects.get( id = article_1_id )
        article_1_newspaper = article_1_instance.newspaper
        article_1_newspaper_id = article_1_newspaper.id
        article_1_pub_date = article_1_instance.pub_date
        article_1_pub_date = article_1_pub_date.strftime( "%Y-%m-%d" )
        article_1_unique_identifier = article_1_instance.unique_identifier
        article_1_archive_source = article_1_instance.archive_source
        article_1_archive_id = article_1_instance.archive_id
        article_1_archive_permalink = article_1_instance.permalink
        
        # create entity for it.
        entity_1_instance = my_exporter.create_article_entity( article_1_instance )
        entity_1_id = entity_1_instance.id
        entity_1_type = entity_1_instance.my_entity_types.get()
        
        # do some tests.
        id_type = Entity_Identifier_Type.get_type_for_name( self.IDENTIFIER_TYPE_NAME_ARTICLE_SOURCENET_ID )
        test_entity_instance = Entity.get_entity_for_identifier( article_1_id, id_type_IN = id_type )
        test_entity_id = test_entity_instance.id
        
        # returned entity should have same ID as entity_1_instance.
        should_be = entity_1_id
        error_string = "article entity 1: Article id: {} --> retrieved entity ID: {}; should be ID: {}".format( article_1_id, test_entity_id, should_be )
        self.assertEqual( test_entity_id, should_be, msg = error_string )
        
        #----------------------------------------------------------------------#
        # traits
        #----------------------------------------------------------------------#        
        
        # ==> check pub_date trait, name = "pub_date"
        trait_name = ExportToContext.TRAIT_NAME_PUB_DATE
    
        # initialize trait from predefined entity type trait "pub_date".
        trait_definition_qs = Entity_Type_Trait.objects.filter( slug = trait_name )
        trait_definition_qs = trait_definition_qs.filter( related_type = entity_1_type )
        trait_definition = trait_definition_qs.get()

        # retrieve trait
        test_entity_trait = test_entity_instance.get_entity_trait( trait_name,
                                                                   entity_type_trait_IN = trait_definition )
        test_entity_trait_value = test_entity_trait.value
        
        # returned trait should have value that equals article pub_date string.
        should_be = article_1_pub_date
        error_string = "article trait {} has value {}, should have value {}".format( trait_name, test_entity_trait_value, should_be )
        self.assertEqual( test_entity_trait_value, should_be, msg = error_string )
       
        # ==> check newspaper ID - trait, name = "sourcenet-Newspaper-ID"
        trait_name = ExportToContext.TRAIT_NAME_SOURCENET_NEWSPAPER_ID
        test_entity_trait = test_entity_instance.get_entity_trait( trait_name,
                                                                   slug_IN = slugify( trait_name ) )
        test_entity_trait_value = int( test_entity_trait.value )
        
        # returned trait should have value that equals newspaper ID.
        should_be = article_1_newspaper_id
        error_string = "article trait {} has value {}, should have value {}".format( trait_name, test_entity_trait_value, should_be )
        self.assertEqual( test_entity_trait_value, should_be, msg = error_string )
       
        #----------------------------------------------------------------------#
        # identifiers
        #----------------------------------------------------------------------#

        # ==> django ID
        test_identifier_type = Entity_Identifier_Type.get_type_for_name( self.IDENTIFIER_TYPE_NAME_ARTICLE_SOURCENET_ID )
        test_identifier_name = test_identifier_type.name
        test_identifier = test_entity_instance.get_identifier( test_identifier_name,
                                                               id_type_IN = test_identifier_type )
                                                               
        # get value
        test_identifier_value = int( test_identifier.uuid )
        
        # returned identifier should have uuid that equals article's ID.
        found = test_identifier_value
        should_be = article_1_id
        error_string = "article identifier {} has value {}, should have value {}".format( test_identifier_name, found, should_be )
        self.assertEqual( found, should_be, msg = error_string )
        
        # ==> check unique_identifier (newsbank ID)
        test_identifier_type = Entity_Identifier_Type.get_type_for_name( self.IDENTIFIER_TYPE_NAME_ARTICLE_NEWSBANK_ID )
        test_identifier_name = test_identifier_type.name
        test_identifier = test_entity_instance.get_identifier( test_identifier_name,
                                                               id_type_IN = test_identifier_type )
                                                               
        # get value
        test_identifier_value = test_identifier.uuid
        
        # returned identifier should have uuid that equals article's ID.
        found = test_identifier_value
        should_be = article_1_unique_identifier
        error_string = "article identifier {} has value {}, should have value {}".format( test_identifier_name, found, should_be )
        self.assertEqual( found, should_be, msg = error_string )
        
        # ==> article_archive_identifier
        test_identifier_type = Entity_Identifier_Type.get_type_for_name( self.IDENTIFIER_TYPE_NAME_ARTICLE_ARCHIVE_IDENTIFIER )
        test_identifier_name = test_identifier_type.name
        test_identifier_source = article_1_archive_source
        test_identifier = test_entity_instance.get_identifier( test_identifier_name,
                                                               id_source_IN = test_identifier_source,
                                                               id_type_IN = test_identifier_type )
                                                               
        # get value
        #test_identifier_value = test_identifier.uuid
        
        # returned identifier should have uuid that equals article's ID.
        #found = test_identifier_value
        #should_be = article_1_archive_id
        #error_string = "article identifier {} has value {}, should have value {}".format( test_identifier_name, found, should_be )
        #self.assertEqual( found, should_be, msg = error_string )

        # retrieve identifier should result in None.
        error_string = "article identifier {} should not be set, instead, is present: {}".format( test_identifier_name, test_identifier )
        self.assertIsNone( test_identifier, msg = error_string )
                        
        # ==> permalink
        test_identifier_type = Entity_Identifier_Type.get_type_for_name( self.IDENTIFIER_TYPE_NAME_PERMALINK )
        test_identifier_name = test_identifier_type.name
        test_identifier = test_entity_instance.get_identifier( test_identifier_name,
                                                               id_type_IN = test_identifier_type )
                                                               
        # get value
        test_identifier_value = test_identifier.uuid
        
        # returned identifier should have uuid that equals article's ID.
        found = test_identifier_value
        should_be = article_1_archive_permalink
        error_string = "article identifier {} has value {}, should have value {}".format( test_identifier_name, found, should_be )
        self.assertEqual( found, should_be, msg = error_string )
        
        # ! TODO - article that has archive information (add it, then do a create).
        
    #-- END test method test_create_article_entity() --#


    def test_get_article_uuid_id_type( self ):
        
        # declare variables
        me = "test_get_article_uuid_id_type"
        error_string = None
        my_exporter = None
        silly_type_name = None
        my_type_name = None
        my_type_instance = None
        my_type_instance_id = None
        returned_type_instance = None
        returned_type_instance_id = None
        stored_type_name = None
        stored_type_instance = None
        stored_type_instance_id = None
        
        print( '\n====> In {}.{}'.format( self.CLASS_NAME, me ) )
                
        # initialize - make exporter instance
        my_exporter = ExportToContext()
        
        # initialize - set up type reference.
        silly_type_name = self.IDENTIFIER_TYPE_NAME_DOES_NOT_EXIST
        my_type_name = self.IDENTIFIER_TYPE_NAME_PERSON_SOURCENET_ID
        my_type_instance = Entity_Identifier_Type.get_type_for_name( my_type_name )
        my_type_instance_id = my_type_instance.id
        
        #----------------------------------------------------------------------#
        # ----> first, try to retrieve instance with bad name, no default.
        #----------------------------------------------------------------------#
        print( "----> first, try to retrieve instance with bad name, no default." )

        my_exporter.set_article_uuid_id_type_name( silly_type_name, do_get_instance_IN = False )
        returned_type_instance = my_exporter.get_article_uuid_id_type( default_name_IN = None )
        
        # return should be None.
        error_string = "Return of call to my_exporter.get_article_uuid_id_type() with default_name_IN set to None should have returned None, returned instead: {}".format( returned_type_instance )
        self.assertIsNone( returned_type_instance, msg = error_string )
        
        # retrieve type instance from exporter should result in None.
        stored_type_instance = my_exporter.article_uuid_id_type
        error_string = "Reference to my_exporter.article_uuid_id_type should have returned None, returned instead: {}".format( stored_type_instance )
        self.assertIsNone( stored_type_instance, msg = error_string )
        
        # retrieve type name from exporter should yield the name passed in.
        stored_type_name = my_exporter.article_uuid_id_type_name
        should_be = silly_type_name
        error_string = "Reference to my_exporter.article_uuid_id_type_name should have returned {}, returned instead: {}".format( should_be, stored_type_name )
        self.assertEqual( stored_type_name, should_be, msg = error_string )
        
        #----------------------------------------------------------------------#
        # ----> try to retrieve instance with bad name, good default, no update if default used.
        #----------------------------------------------------------------------#
        print( "----> try to retrieve instance with bad name, good default, no update if default used." )

        returned_type_instance = my_exporter.get_article_uuid_id_type( default_name_IN = my_type_name, update_on_default_IN = False )
        
        # return should NOT be None.
        error_string = "Return of call to my_exporter.get_article_uuid_id_type() with good default ( {} ) and update_on_default_IN = False  should have returned an instance, returned None instead: {}".format( my_type_name, returned_type_instance )
        self.assertIsNotNone( returned_type_instance, msg = error_string )
        
        # returned instance ID should be same as my instance ID.
        returned_type_instance_id = returned_type_instance.id
        should_be = my_type_instance_id
        error_string = "Returned id type instance ID ( {} ) should be the same as my_type_instance_id ( {} )".format( returned_type_instance_id, should_be )
        self.assertEqual( returned_type_instance_id, should_be, msg = error_string )

        # retrieve type instance from exporter should result in None.
        stored_type_instance = my_exporter.article_uuid_id_type
        error_string = "Reference to my_exporter.article_uuid_id_type should have returned None, returned instead: {}".format( stored_type_instance )
        self.assertIsNone( stored_type_instance, msg = error_string )
        
        # retrieve type name from exporter should yield the silly name passed in.
        stored_type_name = my_exporter.article_uuid_id_type_name
        should_be = silly_type_name
        error_string = "Reference to my_exporter.article_uuid_id_type_name should have returned {}, returned instead: {}".format( should_be, stored_type_name )
        self.assertEqual( stored_type_name, should_be, msg = error_string )
        returned_type_instance = my_exporter.set_article_uuid_id_type_name( silly_type_name, do_get_instance_IN = True )
                
        #----------------------------------------------------------------------#
        # ----> try to retrieve instance with bad name, good default, update if default used.
        #----------------------------------------------------------------------#
        print( "----> try to retrieve instance with bad name, good default, update if default used." )

        returned_type_instance = my_exporter.get_article_uuid_id_type( default_name_IN = my_type_name, update_on_default_IN = True )
        
        # return should NOT be None.
        error_string = "Return of call to my_exporter.get_article_uuid_id_type() with good default ( {} ) and update_on_default_IN = True should have returned an instance, returned None instead: {}".format( my_type_name, returned_type_instance )
        self.assertIsNotNone( returned_type_instance, msg = error_string )
        
        # returned instance ID should be same as my instance ID.
        returned_type_instance_id = returned_type_instance.id
        should_be = my_type_instance_id
        error_string = "Returned id type instance ID ( {} ) should be the same as my_type_instance_id ( {} )".format( returned_type_instance_id, should_be )
        self.assertEqual( returned_type_instance_id, should_be, msg = error_string )

        # retrieve type instance from exporter should also not result in None.
        stored_type_instance = my_exporter.article_uuid_id_type
        error_string = "Reference to my_exporter.article_uuid_id_type should have returned an instance, not None: {}".format( stored_type_instance )
        self.assertIsNotNone( stored_type_instance, msg = error_string )
        
        # stored instance ID should also be same as my instance ID.
        stored_type_instance_id = stored_type_instance.id
        should_be = my_type_instance_id
        error_string = "Stored id type instance ID ( {} ) should be the same as my_type_instance_id ( {} )".format( stored_type_instance_id, should_be )
        self.assertEqual( stored_type_instance_id, should_be, msg = error_string )

        # retrieve type name from exporter should yield the default name passed in.
        stored_type_name = my_exporter.article_uuid_id_type_name
        should_be = my_type_name
        error_string = "Reference to my_exporter.article_uuid_id_type_name should have returned {}, returned instead: {}".format( my_type_name, stored_type_name )
        self.assertEqual( stored_type_name, should_be, msg = error_string )
        
        #----------------------------------------------------------------------#
        # ----> set to a valid name, don't get instance, try to get.
        #----------------------------------------------------------------------#
        print( "----> set to a valid name, don't get instance, try to get." )

        # ==> store type name, don't retrieve instance.
        my_exporter.article_uuid_id_type_name = None
        my_exporter.article_uuid_id_type = None
        my_exporter.set_article_uuid_id_type_name( my_type_name, do_get_instance_IN = False )

        # retrieve type instance from exporter should result in None.
        stored_type_instance = my_exporter.article_uuid_id_type
        error_string = "Reference to my_exporter.article_uuid_id_type should have returned None, returned instead: {}".format( stored_type_instance )
        self.assertIsNone( stored_type_instance, msg = error_string )
        
        # ==> get type instance, no default, so will fail if problem with stored name.
        returned_type_instance = my_exporter.get_article_uuid_id_type( default_name_IN = None )

        # return should NOT be None.
        error_string = "Return of call to my_exporter.get_article_uuid_id_type() where no instance set, with no default and update_on_default_IN = True should have returned an instance, returned None instead: {}".format( returned_type_instance )
        self.assertIsNotNone( returned_type_instance, msg = error_string )
        
        # returned instance ID should be same as my instance ID.
        returned_type_instance_id = returned_type_instance.id
        should_be = my_type_instance_id
        error_string = "Returned id type instance ID ( {} ) should be the same as my_type_instance_id ( {} )".format( returned_type_instance_id, should_be )
        self.assertEqual( returned_type_instance_id, should_be, msg = error_string )

        # retrieve type instance from exporter should also not result in None.
        stored_type_instance = my_exporter.article_uuid_id_type
        error_string = "Reference to my_exporter.article_uuid_id_type should have returned an instance, not None: {}".format( stored_type_instance )
        self.assertIsNotNone( stored_type_instance, msg = error_string )
        
        # stored instance ID should also be same as my instance ID.
        stored_type_instance_id = stored_type_instance.id
        should_be = my_type_instance_id
        error_string = "Stored id type instance ID ( {} ) should be the same as my_type_instance_id ( {} )".format( stored_type_instance_id, should_be )
        self.assertEqual( stored_type_instance_id, should_be, msg = error_string )

        # retrieve type name from exporter should yield the stored name.
        stored_type_name = my_exporter.article_uuid_id_type_name
        should_be = my_type_name
        error_string = "Reference to my_exporter.article_uuid_id_type_name should have returned {}, returned instead: {}".format( my_type_name, stored_type_name )
        self.assertEqual( stored_type_name, should_be, msg = error_string )

        #----------------------------------------------------------------------#
        # ----> set to a valid name, get instance, try to get.
        #----------------------------------------------------------------------#
        print( "----> set to a valid name, get instance, try to get." )

        # ==> store type name, retrieve instance.
        my_exporter.article_uuid_id_type_name = None
        my_exporter.article_uuid_id_type = None
        my_exporter.set_article_uuid_id_type_name( my_type_name, do_get_instance_IN = True )

        # retrieve type instance from exporter should not result in None.
        stored_type_instance = my_exporter.article_uuid_id_type
        error_string = "Reference to my_exporter.article_uuid_id_type should have returned an instance, not None: {}".format( stored_type_instance )
        self.assertIsNotNone( stored_type_instance, msg = error_string )
        
        # ==> get type instance, no default, so will fail if problem with stored name.
        returned_type_instance = my_exporter.get_article_uuid_id_type( default_name_IN = None )

        # return should NOT be None.
        error_string = "Return of call to my_exporter.get_article_uuid_id_type() with no default and update_on_default_IN = True should have returned an instance, returned None instead: {}".format( returned_type_instance )
        self.assertIsNotNone( returned_type_instance, msg = error_string )
        
        # returned instance ID should be same as my instance ID.
        returned_type_instance_id = returned_type_instance.id
        should_be = my_type_instance_id
        error_string = "Returned id type instance ID ( {} ) should be the same as my_type_instance_id ( {} )".format( returned_type_instance_id, should_be )
        self.assertEqual( returned_type_instance_id, should_be, msg = error_string )

        # retrieve type instance from exporter should also not result in None.
        stored_type_instance = my_exporter.article_uuid_id_type
        error_string = "Reference to my_exporter.article_uuid_id_type should have returned an instance, not None: {}".format( stored_type_instance )
        self.assertIsNotNone( stored_type_instance, msg = error_string )
        
        # stored instance ID should also be same as my instance ID.
        stored_type_instance_id = stored_type_instance.id
        should_be = my_type_instance_id
        error_string = "Stored id type instance ID ( {} ) should be the same as my_type_instance_id ( {} )".format( stored_type_instance_id, should_be )
        self.assertEqual( stored_type_instance_id, should_be, msg = error_string )

        # retrieve type name from exporter should yield the stored name.
        stored_type_name = my_exporter.article_uuid_id_type_name
        should_be = my_type_name
        error_string = "Reference to my_exporter.article_uuid_id_type_name should have returned {}, returned instead: {}".format( my_type_name, stored_type_name )
        self.assertEqual( stored_type_name, should_be, msg = error_string )

    #-- END test method test_get_article_uuid_id_type --#
        
    
    def test_set_article_uuid_id_type_name( self ):
        
        # declare variables
        me = "test_set_article_uuid_id_type_name"
        error_string = None
        my_exporter = None
        silly_type_name = None
        my_type_name = None
        my_type_instance = None
        my_type_instance_id = None
        returned_type_instance = None
        returned_type_instance_id = None
        stored_type_name = None
        stored_type_instance = None
        stored_type_instance_id = None
        
        print( '\n====> In {}.{}'.format( self.CLASS_NAME, me ) )
                
        # initialize - make exporter instance
        my_exporter = ExportToContext()
        
        # initialize - set up type reference.
        silly_type_name = self.IDENTIFIER_TYPE_NAME_DOES_NOT_EXIST
        my_type_name = self.IDENTIFIER_TYPE_NAME_PERSON_SOURCENET_ID
        my_type_instance = Entity_Identifier_Type.get_type_for_name( my_type_name )
        my_type_instance_id = my_type_instance.id

        #----------------------------------------------------------------------#
        # ----> first, set id type name, but don't create instance.
        #----------------------------------------------------------------------#

        returned_type_instance = my_exporter.set_article_uuid_id_type_name( silly_type_name, do_get_instance_IN = False )
        
        # return should be None.
        error_string = "Return of call to my_exporter.set_article_uuid_id_type_name() for name_string {} with do_get_instance_IN set to False should have returned None, returned instead: {}".format( silly_type_name, returned_type_instance )
        self.assertIsNone( returned_type_instance, msg = error_string )
        
        # retrieve type instance from exporter should result in None.
        stored_type_instance = my_exporter.article_uuid_id_type
        error_string = "Reference to my_exporter.article_uuid_id_type should have returned None, returned instead: {}".format( stored_type_instance )
        self.assertIsNone( stored_type_instance, msg = error_string )
        
        # retrieve type name from exporter should yield the name passed in.
        stored_type_name = my_exporter.article_uuid_id_type_name
        should_be = silly_type_name
        error_string = "Reference to my_exporter.article_uuid_id_type_name should have returned {}, returned instead: {}".format( should_be, stored_type_name )
        self.assertEqual( stored_type_name, should_be, msg = error_string )
        
        #----------------------------------------------------------------------#
        # ----> Then, set id type name, DO create instance.
        #----------------------------------------------------------------------#

        returned_type_instance = my_exporter.set_article_uuid_id_type_name( my_type_name, do_get_instance_IN = True )
        
        # return should not be None.
        error_string = "Return of call to my_exporter.set_article_uuid_id_type_name() for valid name_string {} with do_get_instance_IN set to True should have returned an instance, returned None instead: {}".format( my_type_name, returned_type_instance )
        self.assertIsNotNone( returned_type_instance, msg = error_string )
        
        # returned instance ID should be same as my instance ID.
        returned_type_instance_id = returned_type_instance.id
        should_be = my_type_instance_id
        error_string = "Returned id type instance ID ( {} ) should be the same as my_type_instance_id ( {} )".format( returned_type_instance_id, should_be )
        self.assertEqual( returned_type_instance_id, should_be, msg = error_string )

        # retrieve type instance from exporter should also not result in None.
        stored_type_instance = my_exporter.article_uuid_id_type
        error_string = "Reference to my_exporter.article_uuid_id_type should have returned an instance, not None: {}".format( stored_type_instance )
        self.assertIsNotNone( stored_type_instance, msg = error_string )
        
        # stored instance ID should also be same as my instance ID.
        stored_type_instance_id = stored_type_instance.id
        should_be = my_type_instance_id
        error_string = "Stored id type instance ID ( {} ) should be the same as my_type_instance_id ( {} )".format( stored_type_instance_id, should_be )
        self.assertEqual( stored_type_instance_id, should_be, msg = error_string )

        # retrieve type name from exporter should yield the name passed in.
        stored_type_name = my_exporter.article_uuid_id_type_name
        should_be = my_type_name
        error_string = "Reference to my_exporter.article_uuid_id_type_name should have returned {}, returned instead: {}".format( my_type_name, stored_type_name )
        self.assertEqual( stored_type_name, should_be, msg = error_string )

    #-- END test method test_set_article_uuid_id_type_name --#
        
    
#-- END test class ExportToContextTest --#
