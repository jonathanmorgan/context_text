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
from context_text.models import Newspaper
from context_text.shared.context_text_base import ContextTextBase
from context_text.tests.test_helper import TestHelper


class NewspaperModelTest( django.test.TestCase ):
    

    #----------------------------------------------------------------------------
    # ! ----> Constants-ish
    #----------------------------------------------------------------------------


    # DEBUG
    DEBUG = False

    # CLASS NAME
    CLASS_NAME = "NewspaperModelTest"
    
    # Entity Trait names
    ENTITY_TRAIT_NAME_NAME = Newspaper.TRAIT_NAME_NAME
    ENTITY_TRAIT_NAME_DESCRIPTION = Newspaper.TRAIT_NAME_DESCRIPTION
    ENTITY_TRAIT_NAME_NAME = Newspaper.TRAIT_NAME_ORGANIZATION_ID
    ENTITY_TRAIT_NAME_NAME = Newspaper.TRAIT_NAME_SECTIONS_LOCAL_NEWS
    ENTITY_TRAIT_NAME_NAME = Newspaper.TRAIT_NAME_SECTIONS_SPORTS

    # Identifier names
    TEST_IDENTIFIER_NAME = TestHelper.TEST_IDENTIFIER_NAME
    
    # test Newspaper IDs
    TEST_ID_1 = 1  # Grand Rapids PRess
    TEST_ID_2 = 2  # Detroit News
    
    # ! --------> Configuration
    
    # Entity Type
    MY_ENTITY_TYPE = ContextTextBase.CONTEXT_ENTITY_TYPE_SLUG_NEWSPAPER

    # Identifier names
    MY_ENTITY_ID_TYPE_NAME = ContextTextBase.CONTEXT_ENTITY_ID_TYPE_NEWSPAPER_SOURCENET_ID
    
    # Class
    MY_CLASS = Newspaper
    
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


    def test_load_entity( self ):
        
        # declare variables
        me = "test_load_entity"
        error_string = None
        my_id_list = None
        my_id = None
        my_instance = None
        newspaper_name = None
        newspaper_description = None
        newspaper_organization = None
        newspaper_organization_id = None
        newspaper_newsbank_code = None
        newspaper_sections_local_news = None
        newspaper_sections_sports = None
        my_entity = None
        my_entity_id = None
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
        my_id_list = []
        my_id_list.append( self.TEST_ID_1 )
        my_id_list.append( self.TEST_ID_2 )        
        
        if ( debug_flag == True ):
            print( "All types:" )
            for current_type in Entity_Identifier_Type.objects.all():
            
                print( "- {}".format( current_type ) )
                
            #-- END loop over all types to test loading of fixture --#
        #-- END DEBUG --#

        # loop over test ids
        for my_id in my_id_list:
        
            # load instance information.
            my_instance = self.MY_CLASS.objects.get( id = my_id )
            newspaper_name = my_instance.name
            newspaper_description = my_instance.description
            newspaper_organization = my_instance.organization
            if ( newspaper_organization is not None ):
                newspaper_organization_id = newspaper_organization.id
            #-- END check if organization. --#
            newspaper_newsbank_code = my_instance.newsbank_code
            newspaper_sections_local_news = my_instance.sections_local_news
            newspaper_sections_sports = my_instance.sections_sports
            
            # create entity for it.
            entity_instance = my_instance.load_entity()
            entity_id = entity_instance.id
            entity_type = entity_instance.add_entity_type( self.MY_ENTITY_TYPE )
            
            # ! ----> entity in instance should now be set to new entity.

            # get nested entity's ID
            my_entity = my_instance.entity
            if ( my_entity is not None ):
            
                # entity present.  Get ID.
                my_entity_id = my_entity.id

            #-- END check to see if instance has entity. --#
            
            # nested entity ID should be same as test entity ID.
            should_be = my_entity_id
            error_string = "newspaper entity ID {} != the ID of entity returned by method {}".format( should_be, entity_id )
            self.assertEqual( entity_id, should_be, msg = error_string )

            # more tests.
            id_type = Entity_Identifier_Type.get_type_for_name( ContextTextBase.CONTEXT_ENTITY_ID_TYPE_NEWSPAPER_SOURCENET_ID )
            test_entity_instance = Entity.get_entity_for_identifier( my_id, id_type_IN = id_type )
            test_entity_id = test_entity_instance.id
            
            # returned entity should have same ID as entity_instance.
            should_be = entity_id
            error_string = "article entity 1: Article id: {} --> retrieved entity ID: {}; should be ID: {}".format( my_id, test_entity_id, should_be )
            self.assertEqual( test_entity_id, should_be, msg = error_string )
            
            # ! ----> if article.entity is emptied, should load same entity again.
            
            # reload instance
            my_instance = self.MY_CLASS.objects.get( id = my_id )
            
            # clear out entity field.
            my_instance.entity = None
            my_instance.save()
            
            # try call to load_entity
            my_instance.load_entity()
            
            # get nested entity's ID
            my_entity = my_instance.entity
            if ( my_entity is not None ):
            
                # entity present.  Get ID.
                my_entity_id = my_entity.id

            #-- END check to see if instance has entity. --#
            
            # nested entity ID should be same as test entity ID.
            should_be = my_entity_id
            error_string = "newspaper entity ID {} != the ID of entity returned by method {}".format( should_be, entity_id )
            self.assertEqual( entity_id, should_be, msg = error_string )

            # more tests.
            id_type = Entity_Identifier_Type.get_type_for_name( self.MY_ENTITY_ID_TYPE_NAME )
            test_entity_instance = Entity.get_entity_for_identifier( my_id, id_type_IN = id_type )
            test_entity_id = test_entity_instance.id
            
            # returned entity should have same ID as entity_instance.
            should_be = entity_id
            error_string = "newspaper entity 1: Newspaper id: {} --> retrieved entity ID: {}; should be ID: {}".format( my_id, test_entity_id, should_be )
            self.assertEqual( test_entity_id, should_be, msg = error_string )
                        
        #-- END loop over test instance IDs. --#
        
    #-- END test method test_load_entity() --#


    def test_update_entity( self ):
        
        # declare variables
        me = "test_update_entity"
        error_string = None
        my_id_list = None
        my_id = None
        my_instance = None
        newspaper_name = None
        newspaper_description = None
        newspaper_organization = None
        newspaper_organization_id = None
        newspaper_newsbank_code = None
        newspaper_sections_local_news = None
        newspaper_sections_sports = None
        my_entity = None
        my_entity_id = None
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
        my_id_list = []
        my_id_list.append( self.TEST_ID_1 )
        my_id_list.append( self.TEST_ID_2 )        
        
        if ( debug_flag == True ):
            print( "All types:" )
            for current_type in Entity_Identifier_Type.objects.all():
            
                print( "- {}".format( current_type ) )
                
            #-- END loop over all types to test loading of fixture --#
        #-- END DEBUG --#

        # loop over test ids
        for my_id in my_id_list:
        
            # ! ==> load instance information.
            my_instance = self.MY_CLASS.objects.get( id = my_id )
            newspaper_name = my_instance.name
            newspaper_description = my_instance.description
            newspaper_organization = my_instance.organization
            if ( newspaper_organization is not None ):
                newspaper_organization_id = newspaper_organization.id
            #-- END check if organization. --#
            newspaper_newsbank_code = my_instance.newsbank_code
            newspaper_sections_local_news = my_instance.sections_local_news
            newspaper_sections_sports = my_instance.sections_sports
                        
            # create entity for it.
            entity_instance = my_instance.update_entity()
            entity_id = entity_instance.id
            entity_type = entity_instance.add_entity_type( self.MY_ENTITY_TYPE )
            
            # entity ID in instance should now be set to this entity's ID.
            
            # reload instance
            my_instance = self.MY_CLASS.objects.get( id = my_id )
            
            # get nested entity's ID
            my_entity = my_instance.entity
            if ( my_entity is not None ):
            
                # entity present.  Get ID.
                my_entity_id = my_entity.id

            #-- END check to see if article has entity. --#
            
            # nested entity ID should be same as test entity ID.
            should_be = my_entity_id
            error_string = "instance entity ID {} != the ID of entity returned by method {}".format( should_be, entity_id )
            self.assertEqual( entity_id, should_be, msg = error_string )

            # more tests.
            id_type = Entity_Identifier_Type.get_type_for_name( self.MY_ENTITY_ID_TYPE_NAME )
            test_entity_instance = Entity.get_entity_for_identifier( my_id, id_type_IN = id_type )
            test_entity_id = test_entity_instance.id
            
            # returned entity should have same ID as entity_instance.
            should_be = entity_id
            error_string = "entity loaded by ID: instance id: {} --> retrieved entity ID: {}; should be ID: {}".format( my_id, test_entity_id, should_be )
            self.assertEqual( test_entity_id, should_be, msg = error_string )
            
           
            #----------------------------------------------------------------------#
            # ! ==> traits
            #----------------------------------------------------------------------#        
            
            # ! ----> name
            # check name trait, name = "name"
            trait_name = Newspaper.TRAIT_NAME_NAME
        
            # initialize trait from predefined entity type trait "pub_date".
            trait_definition_qs = Entity_Type_Trait.objects.filter( slug = trait_name )
            trait_definition_qs = trait_definition_qs.filter( related_type = entity_type )
            trait_definition = trait_definition_qs.get()
    
            # retrieve trait
            test_entity_trait = test_entity_instance.get_entity_trait( trait_name,
                                                                       entity_type_trait_IN = trait_definition )
            test_entity_trait_value = test_entity_trait.get_trait_value_as_str()
            
            # returned trait should have value that equals name string.
            should_be = newspaper_name
            error_string = "trait {} has value {}, should have value {}".format( trait_name, test_entity_trait_value, should_be )
            self.assertEqual( test_entity_trait_value, should_be, msg = error_string )
           
            # ! ----> description
            # ==> check description trait, name = "description"
            trait_name = Newspaper.TRAIT_NAME_DESCRIPTION
            test_entity_trait = test_entity_instance.get_entity_trait( trait_name,
                                                                       slug_IN = slugify( trait_name ) )
            test_entity_trait_value = test_entity_trait.get_trait_value_as_str()
            
            # returned trait should have value that equals newspaper description.
            should_be = newspaper_description
            error_string = "trait {} has value {}, should have value {}".format( trait_name, test_entity_trait_value, should_be )
            self.assertEqual( test_entity_trait_value, should_be, msg = error_string )
           
            # ! ----> organization ID
            # ! TODO - test behavior if None.

            # ==> check organization ID trait, name = "sourcenet-Organization-ID"
            trait_name = Newspaper.TRAIT_NAME_ORGANIZATION_ID
            test_entity_trait = test_entity_instance.get_entity_trait( trait_name,
                                                                       slug_IN = slugify( trait_name ) )
            test_entity_trait_value = test_entity_trait.get_trait_value()
                
            # is there an organization?
            if ( newspaper_organization is not None ):

                # returned trait should have value that equals newspaper organization's id.
                test_entity_trait_value = int( test_entity_trait_value )
                should_be = newspaper_organization_id
                
            else:
            
                # no organization, value should be None.
                should_be = None
                
            #-- END check to see if organization --#
            
            error_string = "trait {} has value {}, should have value {}".format( trait_name, test_entity_trait_value, should_be )
            self.assertEqual( test_entity_trait_value, should_be, msg = error_string )

            # ! ----> sections_local_news
            # ==> check sections_local_news trait, name = "sections_local_news"
            trait_name = Newspaper.TRAIT_NAME_SECTIONS_LOCAL_NEWS
            test_entity_trait = test_entity_instance.get_entity_trait( trait_name,
                                                                       slug_IN = slugify( trait_name ) )
            test_entity_trait_value = test_entity_trait.get_trait_value_as_str()
            
            # returned trait should have value that equals newspaper sections local news.
            should_be = newspaper_sections_local_news
            error_string = "trait {} has value {}, should have value {}".format( trait_name, test_entity_trait_value, should_be )
            self.assertEqual( test_entity_trait_value, should_be, msg = error_string )
           
            # ! ----> sections_sports
            # ==> check sections_sports trait, name = "sections_sports"
            trait_name = Newspaper.TRAIT_NAME_SECTIONS_SPORTS
            test_entity_trait = test_entity_instance.get_entity_trait( trait_name,
                                                                       slug_IN = slugify( trait_name ) )
            test_entity_trait_value = test_entity_trait.get_trait_value_as_str()
            
            # returned trait should have value that equals newspaper sections sports.
            should_be = newspaper_sections_sports
            error_string = "trait {} has value {}, should have value {}".format( trait_name, test_entity_trait_value, should_be )
            self.assertEqual( test_entity_trait_value, should_be, msg = error_string )            
           
            #----------------------------------------------------------------------#
            # ! ==> identifiers
            #----------------------------------------------------------------------#
            
            entity_id_qs = test_entity_instance.entity_identifier_set.all()
            entity_id_counter = 0
            for test_entity_id in entity_id_qs:
            
                # print the ID.
                entity_id_counter += 1
                print( "----> instance {} Entity ID # {}: {}".format( my_id, entity_id_counter, test_entity_id ) )
                
            #-- END loop over entity's identifiers --#
    
            # ! ----> django ID
            test_identifier_type = Entity_Identifier_Type.get_type_for_name( self.MY_ENTITY_ID_TYPE_NAME )
            test_identifier_name = test_identifier_type.name
            test_identifier = test_entity_instance.get_identifier( test_identifier_name,
                                                                   id_type_IN = test_identifier_type )
                                                                   
            # get value
            test_identifier_value = int( test_identifier.uuid )
            
            # returned identifier should have uuid that equals article's ID.
            found = test_identifier_value
            should_be = my_id
            error_string = "instance identifier {} has value {}, should have value {}".format( test_identifier_name, found, should_be )
            self.assertEqual( found, should_be, msg = error_string )
            
            # ! ----> check newsbank code (newsbank_code)
            test_identifier_type = Entity_Identifier_Type.get_type_for_name( ContextTextBase.CONTEXT_ENTITY_ID_TYPE_NEWSPAPER_NEWSBANK_CODE )
            test_identifier_name = test_identifier_type.name
            test_identifier = test_entity_instance.get_identifier( test_identifier_name,
                                                                   id_type_IN = test_identifier_type )
                                                                   
            # get value
            test_identifier_value = test_identifier.uuid
            
            # returned identifier should have uuid that equals article's ID.
            found = test_identifier_value
            should_be = newspaper_newsbank_code
            error_string = "instance identifier {} has value {}, should have value {}".format( test_identifier_name, found, should_be )
            self.assertEqual( found, should_be, msg = error_string )
                        
        #-- END loop over test isntance IDs. --#
        
    #-- END test method test_update_entity() --#


#-- END test class NewspaperModelTest --#
