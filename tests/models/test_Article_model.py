f"""
This file contains tests of the context_text Article model class.

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
from context_text.models import Article
from context_text.shared.context_text_base import ContextTextBase
from context_text.tests.test_helper import TestHelper


class ArticleModelTest( django.test.TestCase ):
    

    #----------------------------------------------------------------------------
    # ! ----> Constants-ish
    #----------------------------------------------------------------------------


    # DEBUG
    DEBUG = False

    # CLASS NAME
    CLASS_NAME = "ArticleModelTest"

    # identifier type names
    IDENTIFIER_TYPE_NAME_ARTICLE_NEWSBANK_ID = Article.ENTITY_ID_TYPE_ARTICLE_NEWSBANK_ID
    IDENTIFIER_TYPE_NAME_ARTICLE_SOURCENET_ID = Article.ENTITY_ID_TYPE_ARTICLE_SOURCENET_ID
    IDENTIFIER_TYPE_NAME_ARTICLE_ARCHIVE_IDENTIFIER = Article.ENTITY_ID_TYPE_ARTICLE_ARCHIVE_IDENTIFIER
    IDENTIFIER_TYPE_NAME_PERMALINK = Article.ENTITY_ID_TYPE_PERMALINK
    IDENTIFIER_TYPE_NAME_PERSON_OPEN_CALAIS_UUID = ContextTextBase.CONTEXT_ENTITY_ID_TYPE_NAME_PERSON_OPEN_CALAIS_UUID
    IDENTIFIER_TYPE_NAME_PERSON_SOURCENET_ID = ContextTextBase.CONTEXT_ENTITY_ID_TYPE_NAME_PERSON_SOURCENET_ID
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
    ENTITY_TYPE_SLUG_ARTICLE = ContextTextBase.CONTEXT_ENTITY_TYPE_SLUG_ARTICLE
    ENTITY_TYPE_SLUG_NEWSPAPER = ContextTextBase.CONTEXT_ENTITY_TYPE_SLUG_NEWSPAPER
    ENTITY_TYPE_SLUG_PERSON = ContextTextBase.CONTEXT_ENTITY_TYPE_SLUG_PERSON
    
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


    def test_load_entity( self ):
        
        # declare variables
        me = "test_load_entity"
        error_string = None
        article_id_list = None
        article_id = None
        article_instance = None
        article_newspaper = None
        article_newspaper_id = None
        article_pub_date = None
        article_unique_identifier = None
        article_archive_source = None
        article_archive_id = None
        article_entity = None
        article_entity_id = None
        entity_instance = None
        entity_id = None
        entity_type = None
        test_entity_instance = None
        entity_id_qs = None
        test_entity_id = None
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
        
        # initialize
        article_id_list = []
        article_id_list.append( self.TEST_ARTICLE_ID_1 )
        article_id_list.append( self.TEST_ARTICLE_ID_2 )        
        
        if ( debug_flag == True ):
            print( "All types:" )
            for current_type in Entity_Identifier_Type.objects.all():
            
                print( "- {}".format( current_type ) )
                
            #-- END loop over all types to test loading of fixture --#
        #-- END DEBUG --#

        # loop over test articles
        for article_id in article_id_list:
        
            # load article information.
            article_instance = Article.objects.get( id = article_id )
            article_newspaper = article_instance.newspaper
            article_newspaper_id = article_newspaper.id
            article_pub_date = article_instance.pub_date
            article_pub_date = article_pub_date.strftime( "%Y-%m-%d" )
            article_unique_identifier = article_instance.unique_identifier
            article_archive_source = article_instance.archive_source
            article_archive_id = article_instance.archive_id
            article_archive_permalink = article_instance.permalink
            
            # create entity for it.
            entity_instance = article_instance.load_entity()
            entity_id = entity_instance.id
            entity_type = entity_instance.add_entity_type( Article.ENTITY_TYPE_SLUG_ARTICLE )
            
            # ! ----> entity in article should now be set to new entity.

            # get nested entity's ID
            article_entity = article_instance.entity
            if ( article_entity is not None ):
            
                # entity present.  Get ID.
                article_entity_id = article_entity.id

            #-- END check to see if article has entity. --#
            
            # nested entity ID should be same as test entity ID.
            should_be = article_entity_id
            error_string = "article entity ID {} != the ID of entity returned by method {}".format( should_be, entity_id )
            self.assertEqual( entity_id, should_be, msg = error_string )

            # more tests.
            id_type = Entity_Identifier_Type.get_type_for_name( self.IDENTIFIER_TYPE_NAME_ARTICLE_SOURCENET_ID )
            test_entity_instance = Entity.get_entity_for_identifier( article_id, id_type_IN = id_type )
            test_entity_id = test_entity_instance.id
            
            # returned entity should have same ID as entity_instance.
            should_be = entity_id
            error_string = "article entity 1: Article id: {} --> retrieved entity ID: {}; should be ID: {}".format( article_id, test_entity_id, should_be )
            self.assertEqual( test_entity_id, should_be, msg = error_string )
            
            # ! ----> if article.entity is emptied, should load same entity again.
            
            # reload article
            article_instance = Article.objects.get( id = article_id )
            
            # clear out entity field.
            article_instance.entity = None
            article_instance.save()
            
            # try call to load_entity
            article_instance.load_entity()
            
            # get nested entity's ID
            article_entity = article_instance.entity
            if ( article_entity is not None ):
            
                # entity present.  Get ID.
                article_entity_id = article_entity.id

            #-- END check to see if article has entity. --#
            
            # nested entity ID should be same as test entity ID.
            should_be = article_entity_id
            error_string = "article entity ID {} != the ID of entity returned by method {}".format( should_be, entity_id )
            self.assertEqual( entity_id, should_be, msg = error_string )

            # more tests.
            id_type = Entity_Identifier_Type.get_type_for_name( self.IDENTIFIER_TYPE_NAME_ARTICLE_SOURCENET_ID )
            test_entity_instance = Entity.get_entity_for_identifier( article_id, id_type_IN = id_type )
            test_entity_id = test_entity_instance.id
            
            # returned entity should have same ID as entity_instance.
            should_be = entity_id
            error_string = "article entity 1: Article id: {} --> retrieved entity ID: {}; should be ID: {}".format( article_id, test_entity_id, should_be )
            self.assertEqual( test_entity_id, should_be, msg = error_string )
                        
        #-- END loop over test article IDs. --#
        
    #-- END test method test_load_entity() --#


    def test_update_entity( self ):
        
        # declare variables
        me = "test_update_entity"
        error_string = None
        article_id_list = None
        article_id = None
        article_instance = None
        article_newspaper = None
        article_newspaper_id = None
        article_pub_date = None
        article_unique_identifier = None
        article_archive_source = None
        article_archive_id = None
        article_entity = None
        article_entity_id = None
        entity_instance = None
        entity_id = None
        entity_type = None
        test_entity_instance = None
        entity_id_qs = None
        test_entity_id = None
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
        
        # initialize
        article_id_list = []
        article_id_list.append( self.TEST_ARTICLE_ID_1 )
        article_id_list.append( self.TEST_ARTICLE_ID_2 )        
        
        if ( debug_flag == True ):
            print( "All types:" )
            for current_type in Entity_Identifier_Type.objects.all():
            
                print( "- {}".format( current_type ) )
                
            #-- END loop over all types to test loading of fixture --#
        #-- END DEBUG --#

        # loop over test articles
        for article_id in article_id_list:
        
            # load article information.
            article_instance = Article.objects.get( id = article_id )
            article_newspaper = article_instance.newspaper
            article_newspaper_id = article_newspaper.id
            article_pub_date = article_instance.pub_date
            article_pub_date = article_pub_date.strftime( "%Y-%m-%d" )
            article_unique_identifier = article_instance.unique_identifier
            article_archive_source = article_instance.archive_source
            article_archive_id = article_instance.archive_id
            article_archive_permalink = article_instance.permalink
            
            # create entity for it.
            entity_instance = article_instance.update_entity()
            entity_id = entity_instance.id
            entity_type = entity_instance.add_entity_type( Article.ENTITY_TYPE_SLUG_ARTICLE )
            
            # entity ID in article should now be set to this entity's ID.
            
            # reload article
            article_instance = Article.objects.get( id = article_id )
            
            # get nested entity's ID
            article_entity = article_instance.entity
            if ( article_entity is not None ):
            
                # entity present.  Get ID.
                article_entity_id = article_entity.id

            #-- END check to see if article has entity. --#
            
            # nested entity ID should be same as test entity ID.
            should_be = article_entity_id
            error_string = "article entity ID {} != the ID of entity returned by method {}".format( should_be, entity_id )
            self.assertEqual( entity_id, should_be, msg = error_string )

            # more tests.
            id_type = Entity_Identifier_Type.get_type_for_name( self.IDENTIFIER_TYPE_NAME_ARTICLE_SOURCENET_ID )
            test_entity_instance = Entity.get_entity_for_identifier( article_id, id_type_IN = id_type )
            test_entity_id = test_entity_instance.id
            
            # returned entity should have same ID as entity_instance.
            should_be = entity_id
            error_string = "article entity 1: Article id: {} --> retrieved entity ID: {}; should be ID: {}".format( article_id, test_entity_id, should_be )
            self.assertEqual( test_entity_id, should_be, msg = error_string )
            
           
            #----------------------------------------------------------------------#
            # traits
            #----------------------------------------------------------------------#        
            
            # ==> check pub_date trait, name = "pub_date"
            trait_name = ContextTextBase.CONTEXT_TRAIT_NAME_PUB_DATE
        
            # initialize trait from predefined entity type trait "pub_date".
            trait_definition_qs = Entity_Type_Trait.objects.filter( slug = trait_name )
            trait_definition_qs = trait_definition_qs.filter( related_type = entity_type )
            trait_definition = trait_definition_qs.get()
    
            # retrieve trait
            test_entity_trait = test_entity_instance.get_entity_trait( trait_name,
                                                                       entity_type_trait_IN = trait_definition )
            test_entity_trait_value = test_entity_trait.value
            
            # returned trait should have value that equals article pub_date string.
            should_be = article_pub_date
            error_string = "article trait {} has value {}, should have value {}".format( trait_name, test_entity_trait_value, should_be )
            self.assertEqual( test_entity_trait_value, should_be, msg = error_string )
           
            # ==> check newspaper ID - trait, name = "sourcenet-Newspaper-ID"
            trait_name = ContextTextBase.CONTEXT_TRAIT_NAME_SOURCENET_NEWSPAPER_ID
            test_entity_trait = test_entity_instance.get_entity_trait( trait_name,
                                                                       slug_IN = slugify( trait_name ) )
            test_entity_trait_value = int( test_entity_trait.value )
            
            # returned trait should have value that equals newspaper ID.
            should_be = article_newspaper_id
            error_string = "article trait {} has value {}, should have value {}".format( trait_name, test_entity_trait_value, should_be )
            self.assertEqual( test_entity_trait_value, should_be, msg = error_string )
           
            #----------------------------------------------------------------------#
            # identifiers
            #----------------------------------------------------------------------#
            
            entity_id_qs = test_entity_instance.entity_identifier_set.all()
            entity_id_counter = 0
            for test_entity_id in entity_id_qs:
            
                # print the ID.
                entity_id_counter += 1
                print( "----> Article {} Entity ID # {}: {}".format( article_id, entity_id_counter, test_entity_id ) )
                
            #-- END loop over entity's identifiers --#
    
            # ==> django ID
            test_identifier_type = Entity_Identifier_Type.get_type_for_name( self.IDENTIFIER_TYPE_NAME_ARTICLE_SOURCENET_ID )
            test_identifier_name = test_identifier_type.name
            test_identifier = test_entity_instance.get_identifier( test_identifier_name,
                                                                   id_type_IN = test_identifier_type )
                                                                   
            # get value
            test_identifier_value = int( test_identifier.uuid )
            
            # returned identifier should have uuid that equals article's ID.
            found = test_identifier_value
            should_be = article_id
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
            should_be = article_unique_identifier
            error_string = "article identifier {} has value {}, should have value {}".format( test_identifier_name, found, should_be )
            self.assertEqual( found, should_be, msg = error_string )
            
            # ==> article_archive_identifier
            test_identifier_type = Entity_Identifier_Type.get_type_for_name( self.IDENTIFIER_TYPE_NAME_ARTICLE_ARCHIVE_IDENTIFIER )
            test_identifier_name = test_identifier_type.name
            test_identifier_source = article_archive_source
            print( "Trying to retrieve identifier with name = {}; source = {}; and type = {}".format( test_identifier_name, test_identifier_source, test_identifier_type ) )
            test_identifier = test_entity_instance.get_identifier( test_identifier_name,
                                                                   id_source_IN = test_identifier_source,
                                                                   id_type_IN = test_identifier_type )
    
            # are article archive identifier and source set?
            if (
                (
                    ( article_archive_id is not None )
                    and ( article_archive_id != "" )
                )
                and
                (
                    ( article_archive_source is not None )
                    and ( article_archive_source != "" )
                )
            ):
                    
                # get value
                test_identifier_value = test_identifier.uuid
                
                # returned identifier should have uuid that equals article's ID.
                found = test_identifier_value
                should_be = article_archive_id
                error_string = "article identifier {} has value {}, should have value {}".format( test_identifier_name, found, should_be )
                self.assertEqual( found, should_be, msg = error_string )
                
            else:
            
                # no archive identifier set, so should return None.
                error_string = "article identifier {} should not be set, instead, is present: {}".format( test_identifier_name, test_identifier )
                self.assertIsNone( test_identifier, msg = error_string )
                
            #-- END check to see if archive identifier is set. --#
                            
            # ==> permalink
            test_identifier_type = Entity_Identifier_Type.get_type_for_name( self.IDENTIFIER_TYPE_NAME_PERMALINK )
            test_identifier_name = test_identifier_type.name
            test_identifier = test_entity_instance.get_identifier( test_identifier_name,
                                                                   id_type_IN = test_identifier_type )
                                                                   
            # get value
            test_identifier_value = test_identifier.uuid
            
            # returned identifier should have uuid that equals article's ID.
            found = test_identifier_value
            should_be = article_archive_permalink
            error_string = "article identifier {} has value {}, should have value {}".format( test_identifier_name, found, should_be )
            self.assertEqual( found, should_be, msg = error_string )
            
        #-- END loop over test article IDs. --#
        
    #-- END test method test_update_entity() --#


#-- END test class ArticleModelTest --#
