f"""
This file contains tests of the context_text Organization model class.

Functions tested:

- has_entity()
- load_entity() - inherited from Abstract_Entity_Container.
- update_entity()

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
from context_text.models import Organization
from context_text.shared.context_text_base import ContextTextBase
from context_text.tests.test_helper import TestHelper


class OrganizationModelTest( django.test.TestCase ):
    

    #----------------------------------------------------------------------------
    # ! ----> Constants-ish
    #----------------------------------------------------------------------------


    # DEBUG
    DEBUG = False

    # CLASS NAME
    CLASS_NAME = "OrganizationModelTest"
    
    # Entity Trait names
    ENTITY_TRAIT_NAME_NAME = Organization.TRAIT_NAME_NAME
    ENTITY_TRAIT_NAME_DESCRIPTION = Organization.TRAIT_NAME_DESCRIPTION
    ENTITY_TRAIT_NAME_LOCATION_ID = Organization.TRAIT_NAME_LOCATION_ID

    # Identifier names
    TEST_IDENTIFIER_NAME = TestHelper.TEST_IDENTIFIER_NAME
    
    # test Newspaper IDs
    TEST_ID_1 = 55  # Grand Action
    TEST_ID_2 = 59  # Wolverine World Wide
    
    TEST_ID_LIST = []
    TEST_ID_LIST.append( TEST_ID_1 )
    TEST_ID_LIST.append( TEST_ID_2 )
    
    # ! --------> Configuration
    
    # Entity Type
    MY_ENTITY_TYPE = ContextTextBase.CONTEXT_ENTITY_TYPE_SLUG_ORGANIZATION

    # Identifier names
    MY_ENTITY_ID_TYPE_NAME = ContextTextBase.CONTEXT_ENTITY_ID_TYPE_ORGANIZATION_SOURCENET_ID
    
    # Class
    MY_CLASS = Organization
    
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
        
    #-- END test method test_setup() --#


    def test_has_entity( self ):
        
        # declare variables
        me = "test_has_entity"
        error_string = None
        my_id_list = None
        my_id = None
        my_instance = None
        my_has_entity = None
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

        # declare variables - class-specific trait variables.
        organization_name = None
        organization_description = None
        organization_location = None
        organization_location_id = None

        # debug
        debug_flag = self.DEBUG

        print( '\n====> In {}.{}'.format( self.CLASS_NAME, me ) )
        
        # initialize
        my_id_list = self.TEST_ID_LIST
        
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
            organization_name = my_instance.name
            organization_description = my_instance.description
            organization_location = my_instance.location
            if ( organization_location is not None ):
                organization_location_id = organization_location.id
            #-- END check if location. --#
            
            # check if entity. Should not be.
            my_has_entity = my_instance.has_entity()
            should_be = False
            error_string = "instance already has entity ( {} - {} ), should not yet.".format( my_has_entity, my_instance.get_entity() )
            self.assertEqual( my_has_entity, should_be, msg = error_string )            
            
            # create entity for it.
            entity_instance = my_instance.load_entity()
            entity_id = entity_instance.id
            entity_type = entity_instance.add_entity_type( self.MY_ENTITY_TYPE )
            
            # ! ----> entity in instance should now be set to new entity.

            # check if entity. Now, should be one.
            my_has_entity = my_instance.has_entity()
            should_be = True
            error_string = "instance does not have entity instance, but it should ( {} ).".format( my_has_entity )
            self.assertEqual( my_has_entity, should_be, msg = error_string )            
            
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
        
    #-- END test method test_has_entity() --#


    def test_load_entity( self ):
        
        # declare variables
        me = "test_load_entity"
        error_string = None
        my_id_list = None
        my_id = None
        my_instance = None
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

        # declare variables - class-specific trait variables.
        organization_name = None
        organization_description = None
        organization_location = None
        organization_location_id = None

        # debug
        debug_flag = self.DEBUG

        print( '\n====> In {}.{}'.format( self.CLASS_NAME, me ) )
        
        # initialize
        my_id_list = self.TEST_ID_LIST
        
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
            organization_name = my_instance.name
            organization_description = my_instance.description
            organization_location = my_instance.location
            if ( organization_location is not None ):
                organization_location_id = organization_location.id
            #-- END check if location. --#
            
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
            id_type = Entity_Identifier_Type.get_type_for_name( self.MY_ENTITY_ID_TYPE_NAME )
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

        # declare variables - class-specific trait variables.
        organization_name = None
        organization_description = None
        organization_location = None
        organization_location_id = None

        # debug
        debug_flag = self.DEBUG

        print( '\n====> In {}.{}'.format( self.CLASS_NAME, me ) )
        
        # initialize
        my_id_list = self.TEST_ID_LIST
        
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
            organization_name = my_instance.name
            organization_description = my_instance.description
            organization_location = my_instance.location
            if ( organization_location is not None ):
                organization_location_id = organization_location.id
            else:
                organization_location_id = None
            #-- END check if location. --#
                        
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

            # check pre-defined name trait.
            trait_name = Organization.TRAIT_NAME_NAME
            should_be = organization_name
        
            # initialize trait from predefined entity type for trait_name.
            #trait_definition_qs = Entity_Type_Trait.objects.filter( slug = trait_name )
            #trait_definition_qs = trait_definition_qs.filter( related_type = entity_type )
            #trait_definition = trait_definition_qs.get()
            trait_definition = entity_type.get_trait_spec( trait_name )
    
            # retrieve value
            test_entity_trait = test_entity_instance.get_entity_trait( trait_name,
                                                                       entity_type_trait_IN = trait_definition )
            test_entity_trait_value = test_entity_trait.get_trait_value_as_str()
            
            # returned trait should have value that equals name string.
            error_string = "trait {} has value {}, should have value {}".format( trait_name, test_entity_trait_value, should_be )
            self.assertEqual( test_entity_trait_value, should_be, msg = error_string )
           
            # ! ----> description

            # ==> check description trait, name = "description"
            trait_name = Organization.TRAIT_NAME_DESCRIPTION
            should_be = organization_description

            # retrieve value
            test_entity_trait = test_entity_instance.get_entity_trait( trait_name,
                                                                       slug_IN = slugify( trait_name ) )
            test_entity_trait_value = test_entity_trait.get_trait_value_as_str()
            
            # returned trait should have value that equals newspaper description.
            error_string = "trait {} has value {}, should have value {}".format( trait_name, test_entity_trait_value, should_be )
            self.assertEqual( test_entity_trait_value, should_be, msg = error_string )
           
            # ! ----> location ID

            # ==> check location ID trait, name = "sourcenet-Location-ID"
            trait_name = Organization.TRAIT_NAME_LOCATION_ID

            # retrieve value
            test_entity_trait = test_entity_instance.get_entity_trait( trait_name,
                                                                       slug_IN = slugify( trait_name ) )
            test_entity_trait_value = test_entity_trait.get_trait_value()
            
            # set should_be - is there an organization?
            if ( organization_location is not None ):

                # returned trait should have value that equals organization's location id.
                test_entity_trait_value = int( test_entity_trait_value )
                should_be = organization_location_id
                
            else:
            
                # no location, value should be None.
                should_be = None
                
            #-- END check to see if location --#
            
            # test
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
            should_be = my_id
            test_identifier_type = Entity_Identifier_Type.get_type_for_name( self.MY_ENTITY_ID_TYPE_NAME )
            test_identifier_name = test_identifier_type.name
            test_identifier = test_entity_instance.get_identifier( test_identifier_name,
                                                                   id_type_IN = test_identifier_type )
                                                                   
            # get value
            test_identifier_value = int( test_identifier.uuid )
            
            # returned identifier should have uuid that equals instance's ID.
            found = test_identifier_value
            error_string = "instance identifier {} has value {}, should have value {}".format( test_identifier_name, found, should_be )
            self.assertEqual( found, should_be, msg = error_string )
            
        #-- END loop over test isntance IDs. --#
        
    #-- END test method test_update_entity() --#


#-- END test class OrganizationModelTest --#
