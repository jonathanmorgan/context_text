"""
This file contains tests of the context_text Person model (and by extension
   Abstract_Person).

Functions tested:
- Person.look_up_person_from_name()
"""

# django imports
import django.test
from django.utils.text import slugify

# context imports
from context.models import Entity
from context.models import Entity_Identifier
from context.models import Entity_Identifier_Type
from context.models import Entity_Type
from context.models import Entity_Type_Trait

# context_text imports
from context_text.models import Person
from context_text.shared.context_text_base import ContextTextBase
from context_text.tests.test_helper import TestHelper


class PersonModelTest( django.test.TestCase ):
    
    #----------------------------------------------------------------------------
    # ! ==> Constants-ish
    #----------------------------------------------------------------------------


    # DEBUG
    DEBUG = False

    # CLASS NAME
    CLASS_NAME = "PersonModelTest"
    
    # Entity Trait names
    ENTITY_TRAIT_NAME_FIRST_NAME = Person.TRAIT_NAME_FIRST_NAME
    ENTITY_TRAIT_NAME_FULL_NAME = Person.TRAIT_NAME_FULL_NAME
    ENTITY_TRAIT_NAME_GENDER = Person.TRAIT_NAME_GENDER
    ENTITY_TRAIT_NAME_LAST_NAME = Person.TRAIT_NAME_LAST_NAME
    ENTITY_TRAIT_NAME_MIDDLE_NAME = Person.TRAIT_NAME_MIDDLE_NAME
    ENTITY_TRAIT_NAME_NAME_PREFIX = Person.TRAIT_NAME_NAME_PREFIX
    ENTITY_TRAIT_NAME_NAME_SUFFIX = Person.TRAIT_NAME_NAME_SUFFIX
    ENTITY_TRAIT_NAME_ORGANIZATION_ID = Person.TRAIT_NAME_ORGANIZATION_ID
    ENTITY_TRAIT_NAME_TITLE = Person.TRAIT_NAME_TITLE

    # Identifier names
    TEST_IDENTIFIER_NAME = TestHelper.TEST_IDENTIFIER_NAME
    
    # test IDs
    TEST_ID_1 = 24  # Godfrey, Shawn Michael - has gender, middle name, v1
    TEST_ID_2 = 25  # Benison, James ( Assistant Kent County Prosecutor ) - has gender, title, v1
    TEST_ID_3 = 1047  #  High, Calvin Christian - has middle name, v2
    
    TEST_ID_LIST = []
    TEST_ID_LIST.append( TEST_ID_1 )
    TEST_ID_LIST.append( TEST_ID_2 )
    TEST_ID_LIST.append( TEST_ID_3 )
    
    # ! ====> Configuration
    
    # Entity Type
    MY_ENTITY_TYPE = ContextTextBase.CONTEXT_ENTITY_TYPE_SLUG_PERSON

    # Identifier names
    MY_ENTITY_ID_TYPE_NAME = Person.ENTITY_ID_TYPE_PERSON_SOURCENET_ID
    
    # Class
    MY_CLASS = Person


    #----------------------------------------------------------------------
    # ! ==> class methods
    #----------------------------------------------------------------------


    #----------------------------------------------------------------------------
    # ! ==> instance methods - setup
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
        
        print( '\n\n====> In {}.{}\n'.format( self.CLASS_NAME, me ) )
        
        # get setup error count
        setup_error_count = self.setup_error_count
        
        # should be 0
        error_message = ";".join( self.setup_error_list )
        self.assertEqual( setup_error_count, 0, msg = error_message )
        
    #-- END test method test_setup() --#


    #----------------------------------------------------------------------------
    # ! ==> instance methods - shared methods
    #----------------------------------------------------------------------------


    def validate_entity( self, id_IN ):
        
        # declare variables
        me = "validate_entity"
        error_string = None
        my_id_list = None
        my_id = None
        my_instance = None
        my_entity = None
        my_entity_id = None
        my_entity_type_slug = None
        my_entity_type_qs = None
        my_entity_type = None
        entity_instance = None
        entity_id = None
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
        test_identifier_instance = None

        # declare variables - class-specific trait variables.
        person_first_name = None
        person_full_name = None
        person_gender = None
        person_last_name = None
        person_middle_name = None
        person_name_prefix = None
        person_name_suffix = None
        person_organization = None
        person_organization_id = None
        person_title = None
        person_id_qs = None
        identifier_instance = None
        my_id_name = None
        my_id_uuid = None
        my_id_id_type = None
        my_id_source = None
        my_id_notes = None
        my_id_type_name = None

        # debug
        debug_flag = self.DEBUG

        print( '\n\n--------> In {}.{}\n'.format( self.CLASS_NAME, me ) )
        
        if ( debug_flag == True ):
            print( "All types:" )
            for current_type in Entity_Identifier_Type.objects.all():
            
                print( "- {}".format( current_type ) )
                
            #-- END loop over all types to test loading of fixture --#
        #-- END DEBUG --#

        # article_id_IN should not be None
        error_string = "If you are validating entities, you should pass in the parent instance's ID, not None"
        self.assertIsNotNone( id_IN, msg = error_string )

        # make sure we have an ID.
        if ( id_IN is not None ):
        
            my_id = id_IN
        
            # ! ----> load instance information.
            my_instance = self.MY_CLASS.objects.get( id = my_id )
            my_entity_type_slug = my_instance.my_entity_type_slug
            my_entity_type_qs = Entity_Type.objects.filter( slug = my_entity_type_slug )
            my_entity_type = my_entity_type_qs.get()
            person_first_name = my_instance.first_name
            person_full_name = my_instance.full_name_string
            person_gender = my_instance.gender
            person_last_name = my_instance.last_name
            person_middle_name = my_instance.middle_name
            person_name_prefix = my_instance.name_prefix
            person_name_suffix = my_instance.name_suffix
            person_organization = my_instance.organization
            if ( person_organization is not None ):
                person_organization_id = person_organization.id
            #-- END check if organization. --#
            person_title = my_instance.title
            person_id_qs = my_instance.person_external_uuid_set.all()
                        
            # get nested entity's ID
            my_entity = my_instance.entity

            # my_entity should not be None
            error_string = "Instance should contain an Entity, not have None"
            self.assertIsNotNone( my_entity, msg = error_string )

            if ( my_entity is not None ):
            
                # entity present.  Get ID.
                my_entity_id = my_entity.id

            #-- END check to see if article has entity. --#
            
            # !----> check ID and type

            # does django ID identifier match instance ID?
            id_type = Entity_Identifier_Type.get_type_for_name( self.MY_ENTITY_ID_TYPE_NAME )
            test_entity_instance = Entity.get_entity_for_identifier( my_id, id_entity_id_type_IN = id_type )
            test_entity_id = test_entity_instance.id
            
            # returned entity should have same ID as entity_instance.
            should_be = my_entity_id
            error_string = "entity loaded by ID: instance id: {} --> retrieved entity ID: {}; should be ID: {}".format( my_id, test_entity_id, should_be )
            self.assertEqual( test_entity_id, should_be, msg = error_string )
            
            # does entity type match slug in our class?
            test_entity_type = test_entity_instance.get_my_entity_type()
            test_entity_type_slug = test_entity_type.slug
            test_value = test_entity_type_slug
            
            # returned entity should have same type slug as instance.
            should_be = my_entity_type_slug
            error_string = "entity type has slug: {} --> should be: {}".format( test_value, should_be )
            self.assertEqual( test_value, should_be, msg = error_string )
                        
           
            #------------------------------------------------------------------#
            # ! ----> predefined entity traits
            #------------------------------------------------------------------#        
            
            # ! --------> first_name
            # check first name trait, name = "first_name"
            trait_name = Person.TRAIT_NAME_FIRST_NAME
            should_be = person_first_name
        
            # initialize trait from predefined entity type trait for trait_name.
            trait_definition = my_entity_type.get_trait_spec( trait_name )
    
            # retrieve trait
            test_entity_trait = test_entity_instance.get_entity_trait( trait_name,
                                                                       entity_type_trait_IN = trait_definition )

            # Just get trait value, so None stays as None, not "None".
            test_entity_trait_value = test_entity_trait.get_trait_value()
            
            # returned trait should have value that equals name string.
            error_string = "trait {} has value {}, should have value {}".format( trait_name, test_entity_trait_value, should_be )
            self.assertEqual( test_entity_trait_value, should_be, msg = error_string )
           
            # ! --------> middle_name
            # check middle name trait, name = "middle_name"
            trait_name = Person.TRAIT_NAME_MIDDLE_NAME
            should_be = person_middle_name
        
            # initialize trait from predefined entity type trait for trait_name.
            trait_definition = my_entity_type.get_trait_spec( trait_name )
    
            # retrieve trait
            test_entity_trait = test_entity_instance.get_entity_trait( trait_name,
                                                                       entity_type_trait_IN = trait_definition )

            # Just get trait value, so None stays as None, not "None".
            test_entity_trait_value = test_entity_trait.get_trait_value()
            
            # returned trait should have value that equals name string.
            error_string = "trait {} has value {}, should have value {}".format( trait_name, test_entity_trait_value, should_be )
            self.assertEqual( test_entity_trait_value, should_be, msg = error_string )
           
            # ! --------> last_name
            # check last name trait, name = "last_name"
            trait_name = Person.TRAIT_NAME_LAST_NAME
            should_be = person_last_name
        
            # initialize trait from predefined entity type trait for trait_name.
            trait_definition = my_entity_type.get_trait_spec( trait_name )
    
            # retrieve trait
            test_entity_trait = test_entity_instance.get_entity_trait( trait_name,
                                                                       entity_type_trait_IN = trait_definition )

            # Just get trait value, so None stays as None, not "None".
            test_entity_trait_value = test_entity_trait.get_trait_value()
            
            # returned trait should have value that equals name string.
            error_string = "trait {} has value {}, should have value {}".format( trait_name, test_entity_trait_value, should_be )
            self.assertEqual( test_entity_trait_value, should_be, msg = error_string )
           
            #------------------------------------------------------------------#
            # ! ----> free-form entity traits
            #------------------------------------------------------------------#

            # ! --------> full_name

            # ==> check full name string trait, name = "full_name"
            trait_name = Person.TRAIT_NAME_FULL_NAME
            should_be = person_full_name
            
            # get value
            test_entity_trait = test_entity_instance.get_entity_trait( trait_name,
                                                                       slug_IN = slugify( trait_name ) )

            # Just get trait value, so None stays as None, not "None".
            test_entity_trait_value = test_entity_trait.get_trait_value()
            
            # returned trait should have value that equals newspaper description.
            error_string = "trait {} has value {}, should have value {}".format( trait_name, test_entity_trait_value, should_be )
            self.assertEqual( test_entity_trait_value, should_be, msg = error_string )
           
            # ! --------> gender

            # ==> check gender trait, name = "gender"
            trait_name = Person.TRAIT_NAME_GENDER
            should_be = person_gender
            
            # get value
            test_entity_trait = test_entity_instance.get_entity_trait( trait_name,
                                                                       slug_IN = slugify( trait_name ) )

            # Just get trait value, so None stays as None, not "None".
            test_entity_trait_value = test_entity_trait.get_trait_value()
            
            # returned trait should have value that equals newspaper description.
            error_string = "trait {} has value {}, should have value {}".format( trait_name, test_entity_trait_value, should_be )
            self.assertEqual( test_entity_trait_value, should_be, msg = error_string )
           
            # ! --------> name_prefix

            # ==> check name prefix trait, name = "name_prefix"
            trait_name = Person.TRAIT_NAME_NAME_PREFIX
            should_be = person_name_prefix
            
            # get value
            test_entity_trait = test_entity_instance.get_entity_trait( trait_name,
                                                                       slug_IN = slugify( trait_name ) )

            # Just get trait value, so None stays as None, not "None".
            test_entity_trait_value = test_entity_trait.get_trait_value()
            
            # returned trait should have value that equals newspaper description.
            error_string = "trait {} has value {}, should have value {}".format( trait_name, test_entity_trait_value, should_be )
            self.assertEqual( test_entity_trait_value, should_be, msg = error_string )
           
            # ! --------> name_suffix

            # ==> check name suffix trait, name = "name_suffix"
            trait_name = Person.TRAIT_NAME_NAME_SUFFIX
            should_be = person_name_suffix
            
            # get value
            test_entity_trait = test_entity_instance.get_entity_trait( trait_name,
                                                                       slug_IN = slugify( trait_name ) )

            # Just get trait value, so None stays as None, not "None".
            test_entity_trait_value = test_entity_trait.get_trait_value()
            
            # returned trait should have value that equals newspaper description.
            error_string = "trait {} has value {}, should have value {}".format( trait_name, test_entity_trait_value, should_be )
            self.assertEqual( test_entity_trait_value, should_be, msg = error_string )
           
            # ! --------> title

            # ==> check title trait, name = "title"
            trait_name = Person.TRAIT_NAME_TITLE
            should_be = person_title
            
            # get value
            test_entity_trait = test_entity_instance.get_entity_trait( trait_name,
                                                                       slug_IN = slugify( trait_name ) )

            # Just get trait value, so None stays as None, not "None".
            test_entity_trait_value = test_entity_trait.get_trait_value()
            
            # returned trait should have value that equals newspaper description.
            error_string = "trait {} has value {}, should have value {}".format( trait_name, test_entity_trait_value, should_be )
            self.assertEqual( test_entity_trait_value, should_be, msg = error_string )
           
            # ! --------> organization.id

            # ==> check organization ID trait, name = "sourcenet-Organization-ID"
            trait_name = Person.TRAIT_NAME_ORGANIZATION_ID

            # get value
            test_entity_trait = test_entity_instance.get_entity_trait( trait_name,
                                                                       slug_IN = slugify( trait_name ) )
            test_entity_trait_value = test_entity_trait.get_trait_value()
                
            # set should_be - is there an organization?
            if ( person_organization is not None ):

                # returned trait should have value that equals person organization's id.
                test_entity_trait_value = int( test_entity_trait_value )
                should_be = person_organization_id
                
            else:
            
                # no organization, value should be None.
                should_be = None
                
            #-- END check to see if organization --#
            
            error_string = "trait {} has value {}, should have value {}".format( trait_name, test_entity_trait_value, should_be )
            self.assertEqual( test_entity_trait_value, should_be, msg = error_string )

            # make sure that the organization has an entity, also.
            if ( person_organization is not None ):

                related_has_entity = person_organization.has_entity()
                should_be = True
                error_string = "instance related organization ( {} ) does not have an associated entity, update_entity() should have created one.".format( newspaper_organization )
                self.assertEqual( related_has_entity, should_be, msg = error_string )
                
            #-- END check to see if organization --#


            #----------------------------------------------------------------------#
            # ! ----> identifiers
            #----------------------------------------------------------------------#
            
            entity_id_qs = test_entity_instance.entity_identifier_set.all()
            entity_id_counter = 0
            for test_entity_id in entity_id_qs:
            
                # print the ID.
                entity_id_counter += 1
                print( "----> instance {} Entity ID # {}: {}".format( my_id, entity_id_counter, test_entity_id ) )
                
            #-- END loop over entity's identifiers --#
    
            # ! --------> django ID
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
            
            # ! --------> External UUIDs

            # loop over identifiers.
            for identifier_instance in person_id_qs:
            
                # output the identifier
                print( "----> Current identifier: {}".format( identifier_instance ) )
            
                # retrieve identifier information
                my_id_name = identifier_instance.name
                my_id_uuid = identifier_instance.uuid
                my_id_id_type = identifier_instance.id_type
                my_id_source = identifier_instance.source
                my_id_notes = identifier_instance.notes
                my_id_type_name = None
                
                # see if it is an OpenCalais ID.
                if ( my_id_name in Person.EXTERNAL_UUID_NAME_OPEN_CALAIS_LIST ):
                
                    # it is.  retrieve pre-defined OpenCalais identifier type.
                    my_id_type_name = Person.ENTITY_ID_TYPE_PERSON_OPEN_CALAIS_UUID

                else:
                
                    # it is not - try to retrieve type for value in id_type.
                    my_id_type_name = my_id_id_type
                    
                #-- END check to see if known type. --#
                
                # try to load type, then set identifier.
                identifier_type = Entity_Identifier_Type.get_type_for_name( my_id_type_name )
                identifier_uuid = my_id_uuid
                
                # did we find an identifier_type?
                if ( identifier_type is not None ):
                
                    # also need to set name - when there is an ID type, the
                    #     type name overrides any name passed in.
                    my_id_name = identifier_type.name
                
                #-- END check to see if we found a type --#
                
                # is identifier with matching identity already present?
                #identifier_instance = test_entity_instance.get_identifier( my_id_name,
                #                                                      id_source_IN = my_id_source,
                #                                                      id_id_type_IN = my_id_id_type,
                #                                                      id_type_IN = None )
                    
                # does identifier already exist?
                test_identifier_instance = test_entity_instance.get_identifier( my_id_name,
                                                                                id_source_IN = my_id_source,
                                                                                id_id_type_IN = my_id_id_type,
                                                                                id_type_IN = identifier_type,
                                                                                id_uuid_IN = identifier_uuid )
                
                # should not be None.
                error_string = "instance identifier {} did not match Entity_Identifier for Entity {}".format( identifier_instance, entity_instance )
                self.assertIsNotNone( test_identifier_instance, msg = error_string )
                        
            #-- END loop over identifiers. --#
                                                
        #-- END loop over test isntance IDs. --#
        
    #-- END test method validate_entity() --#


    #----------------------------------------------------------------------------
    # ! ==> instance methods - tests
    #----------------------------------------------------------------------------


    def test_find_person_from_name( self ):
        
        # declare variables
        me = "test_find_person_from_name"
        name_string = ""
        should_be = -1
        do_strict = False
        do_partial = False
        error_string = ""
        test_qs = None
        match_count = -1
        
        print( '\n\n====> In {}.{}\n'.format( self.CLASS_NAME, me ) )

        #----------------------------------------------------------------------#
        # "A Smith"
        #----------------------------------------------------------------------#

        name_string = "A Smith"
        should_be = 3
        test_qs = Person.find_person_from_name( name_string )
        match_count = test_qs.count()
        error_string = name_string + " --> " + str( match_count ) + " should = " + str( should_be )
        self.assertEqual( match_count, should_be, msg = error_string )

        #----------------------------------------------------------------------#
        # "Smith"
        #----------------------------------------------------------------------#

        name_string = "Smith"
        should_be = 3
        test_qs = Person.find_person_from_name( name_string )
        match_count = test_qs.count()
        error_string = name_string + " --> " + str( match_count ) + " should = " + str( should_be )
        self.assertEqual( match_count, should_be, msg = error_string )

        #----------------------------------------------------------------------#
        # "A W Smith"
        #----------------------------------------------------------------------#

        name_string = "A W Smith"
        should_be = 1
        test_qs = Person.find_person_from_name( name_string )
        match_count = test_qs.count()
        error_string = name_string + " --> " + str( match_count ) + " should = " + str( should_be )
        self.assertEqual( match_count, should_be, msg = error_string )

        #----------------------------------------------------------------------#
        # "Alma Smith"
        #----------------------------------------------------------------------#

        name_string = "Alma Smith"
        should_be = 1
        test_qs = Person.find_person_from_name( name_string )
        match_count = test_qs.count()
        error_string = name_string + " --> " + str( match_count ) + " should = " + str( should_be )
        self.assertEqual( match_count, should_be, msg = error_string )

        #----------------------------------------------------------------------#
        # "W Smith"
        #----------------------------------------------------------------------#

        name_string = "W Smith"
        should_be = 0
        test_qs = Person.find_person_from_name( name_string )
        match_count = test_qs.count()
        error_string = name_string + " --> " + str( match_count ) + " should = " + str( should_be )
        self.assertEqual( match_count, should_be, msg = error_string )

        #----------------------------------------------------------------------#
        # "Alma W Smith"
        #----------------------------------------------------------------------#

        name_string = "Alma W Smith"
        should_be = 1
        test_qs = Person.find_person_from_name( name_string )
        match_count = test_qs.count()
        error_string = name_string + " --> " + str( match_count ) + " should = " + str( should_be )
        self.assertEqual( match_count, should_be, msg = error_string )

        #----------------------------------------------------------------------#
        # "Alma Wheeler Smith"
        #----------------------------------------------------------------------#

        name_string = "Alma Wheeler Smith"
        should_be = 1
        test_qs = Person.find_person_from_name( name_string )
        match_count = test_qs.count()
        error_string = name_string + " --> " + str( match_count ) + " should = " + str( should_be )
        self.assertEqual( match_count, should_be, msg = error_string )

        #----------------------------------------------------------------------#
        # "a smith"
        #----------------------------------------------------------------------#

        name_string = "A Smith".lower()
        should_be = 3
        test_qs = Person.find_person_from_name( name_string )
        match_count = test_qs.count()
        error_string = name_string + " --> " + str( match_count ) + " should = " + str( should_be )
        self.assertEqual( match_count, should_be, msg = error_string )

        #----------------------------------------------------------------------#
        # "smith"
        #----------------------------------------------------------------------#

        name_string = "Smith".lower()
        should_be = 3
        test_qs = Person.find_person_from_name( name_string )
        match_count = test_qs.count()
        error_string = name_string + " --> " + str( match_count ) + " should = " + str( should_be )
        self.assertEqual( match_count, should_be, msg = error_string )

        #----------------------------------------------------------------------#
        # "a w smith"
        #----------------------------------------------------------------------#

        name_string = "A W Smith".lower()
        should_be = 1
        test_qs = Person.find_person_from_name( name_string )
        match_count = test_qs.count()
        error_string = name_string + " --> " + str( match_count ) + " should = " + str( should_be )
        self.assertEqual( match_count, should_be, msg = error_string )

        #----------------------------------------------------------------------#
        # "alma smith"
        #----------------------------------------------------------------------#

        name_string = "Alma Smith".lower()
        should_be = 1
        test_qs = Person.find_person_from_name( name_string )
        match_count = test_qs.count()
        error_string = name_string + " --> " + str( match_count ) + " should = " + str( should_be )
        self.assertEqual( match_count, should_be, msg = error_string )

        #----------------------------------------------------------------------#
        # "w smith"
        #----------------------------------------------------------------------#

        name_string = "W Smith".lower()
        should_be = 0
        test_qs = Person.find_person_from_name( name_string )
        match_count = test_qs.count()
        error_string = name_string + " --> " + str( match_count ) + " should = " + str( should_be )
        self.assertEqual( match_count, should_be, msg = error_string )

        #----------------------------------------------------------------------#
        # "alma w smith"
        #----------------------------------------------------------------------#

        name_string = "Alma W Smith".lower()
        should_be = 1
        test_qs = Person.find_person_from_name( name_string )
        match_count = test_qs.count()
        error_string = name_string + " --> " + str( match_count ) + " should = " + str( should_be )
        self.assertEqual( match_count, should_be, msg = error_string )

        #----------------------------------------------------------------------#
        # "alma wheeler smith"
        #----------------------------------------------------------------------#

        name_string = "Alma Wheeler Smith".lower()
        should_be = 1
        test_qs = Person.find_person_from_name( name_string )
        match_count = test_qs.count()
        error_string = name_string + " --> " + str( match_count ) + " should = " + str( should_be )
        self.assertEqual( match_count, should_be, msg = error_string )

    #-- END test method test_find_person_from_name() --#


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
        person_first_name = None
        person_full_name = None
        person_gender = None
        person_last_name = None
        person_middle_name = None
        person_name_prefix = None
        person_name_suffix = None
        person_organization = None
        person_organization_id = None
        person_title = None
        person_id_qs = None

        # debug
        debug_flag = self.DEBUG

        print( '\n\n====> In {}.{}\n'.format( self.CLASS_NAME, me ) )
        
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
            person_first_name = my_instance.first_name
            person_full_name = my_instance.full_name_string
            person_gender = my_instance.gender
            person_last_name = my_instance.last_name
            person_middle_name = my_instance.middle_name
            person_name_prefix = my_instance.name_prefix
            person_name_suffix = my_instance.name_suffix
            person_organization = my_instance.organization
            if ( person_organization is not None ):
                person_organization_id = person_organization.id
            #-- END check if organization. --#
            person_title = my_instance.title
            person_id_qs = my_instance.person_external_uuid_set.all()

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
            test_entity_instance = Entity.get_entity_for_identifier( my_id, id_entity_id_type_IN = id_type )
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
            test_entity_instance = Entity.get_entity_for_identifier( my_id, id_entity_id_type_IN = id_type )
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
        person_first_name = None
        person_full_name = None
        person_gender = None
        person_last_name = None
        person_middle_name = None
        person_name_prefix = None
        person_name_suffix = None
        person_organization = None
        person_organization_id = None
        person_title = None
        person_id_qs = None

        # debug
        debug_flag = self.DEBUG

        print( '\n\n====> In {}.{}\n'.format( self.CLASS_NAME, me ) )
        
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
            person_first_name = my_instance.first_name
            person_full_name = my_instance.full_name_string
            person_gender = my_instance.gender
            person_last_name = my_instance.last_name
            person_middle_name = my_instance.middle_name
            person_name_prefix = my_instance.name_prefix
            person_name_suffix = my_instance.name_suffix
            person_organization = my_instance.organization
            if ( person_organization is not None ):
                person_organization_id = person_organization.id
            #-- END check if organization. --#
            person_title = my_instance.title
            person_id_qs = my_instance.person_external_uuid_set.all()

            
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
            test_entity_instance = Entity.get_entity_for_identifier( my_id, id_entity_id_type_IN = id_type )
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
            test_entity_instance = Entity.get_entity_for_identifier( my_id, id_entity_id_type_IN = id_type )
            test_entity_id = test_entity_instance.id
            
            # returned entity should have same ID as entity_instance.
            should_be = entity_id
            error_string = "newspaper entity 1: Newspaper id: {} --> retrieved entity ID: {}; should be ID: {}".format( my_id, test_entity_id, should_be )
            self.assertEqual( test_entity_id, should_be, msg = error_string )
                        
        #-- END loop over test instance IDs. --#
        
    #-- END test method test_load_entity() --#


    def test_look_up_person_from_name( self ):
        
        # declare variables
        me = "test_look_up_person_from_name"
        name_string = ""
        should_be = -1
        do_strict = False
        do_partial = False
        error_string = ""
        test_qs = None
        match_count = -1

        print( '\n\n====> In {}.{}\n'.format( self.CLASS_NAME, me ) )
        
        #----------------------------------------------------------------------#
        # "A Smith"
        #----------------------------------------------------------------------#

        name_string = "A Smith"

        # strict, no partial - 0
        should_be = 0
        do_strict = True
        do_partial = False
        test_qs = Person.look_up_person_from_name( name_string, do_strict_match_IN = do_strict, do_partial_match_IN = do_partial )
        match_count = test_qs.count()
        error_string = name_string + ": strict = " + str( do_strict ) + "; partial = " + str( do_partial ) + " --> " + str( match_count ) + " should = " + str( should_be )
        self.assertEqual( match_count, should_be, msg = error_string )
        
        # strict, partial - 2
        should_be = 2
        do_strict = True
        do_partial = True
        test_qs = Person.look_up_person_from_name( name_string, do_strict_match_IN = do_strict, do_partial_match_IN = do_partial )
        match_count = test_qs.count()
        error_string = name_string + ": strict = " + str( do_strict ) + "; partial = " + str( do_partial ) + " --> " + str( match_count ) + " should = " + str( should_be )
        self.assertEqual( match_count, should_be, msg = error_string )
        
        # not strict, no partial - 0
        should_be = 0
        do_strict = False
        do_partial = False
        test_qs = Person.look_up_person_from_name( name_string, do_strict_match_IN = do_strict, do_partial_match_IN = do_partial )
        match_count = test_qs.count()
        error_string = name_string + ": strict = " + str( do_strict ) + "; partial = " + str( do_partial ) + " --> " + str( match_count ) + " should = " + str( should_be )
        self.assertEqual( match_count, should_be, msg = error_string )

        # not strict, partial - 3
        should_be = 3
        do_strict = False
        do_partial = True
        test_qs = Person.look_up_person_from_name( name_string, do_strict_match_IN = do_strict, do_partial_match_IN = do_partial )
        match_count = test_qs.count()
        error_string = name_string + ": strict = " + str( do_strict ) + "; partial = " + str( do_partial ) + " --> " + str( match_count ) + " should = " + str( should_be )
        self.assertEqual( match_count, should_be, msg = error_string )

        #----------------------------------------------------------------------#
        # "Smith"
        #----------------------------------------------------------------------#

        name_string = "Smith"

        # strict, no partial - 0
        should_be = 0
        do_strict = True
        do_partial = False
        test_qs = Person.look_up_person_from_name( name_string, do_strict_match_IN = do_strict, do_partial_match_IN = do_partial )
        match_count = test_qs.count()
        error_string = name_string + ": strict = " + str( do_strict ) + "; partial = " + str( do_partial ) + " --> " + str( match_count ) + " should = " + str( should_be )
        self.assertEqual( match_count, should_be, msg = error_string )
        
        # strict, partial - 0
        should_be = 0
        do_strict = True
        do_partial = True
        test_qs = Person.look_up_person_from_name( name_string, do_strict_match_IN = do_strict, do_partial_match_IN = do_partial )
        match_count = test_qs.count()
        error_string = name_string + ": strict = " + str( do_strict ) + "; partial = " + str( do_partial ) + " --> " + str( match_count ) + " should = " + str( should_be )
        self.assertEqual( match_count, should_be, msg = error_string )
        
        # not strict, no partial - 0 (parses single name as first, not last)
        should_be = 0
        do_strict = False
        do_partial = False
        test_qs = Person.look_up_person_from_name( name_string, do_strict_match_IN = do_strict, do_partial_match_IN = do_partial )
        match_count = test_qs.count()
        error_string = name_string + ": strict = " + str( do_strict ) + "; partial = " + str( do_partial ) + " --> " + str( match_count ) + " should = " + str( should_be )
        self.assertEqual( match_count, should_be, msg = error_string )

        # not strict, partial - 0 (parses single name as first, not last)
        should_be = 0
        do_strict = False
        do_partial = True
        test_qs = Person.look_up_person_from_name( name_string, do_strict_match_IN = do_strict, do_partial_match_IN = do_partial )
        match_count = test_qs.count()
        error_string = name_string + ": strict = " + str( do_strict ) + "; partial = " + str( do_partial ) + " --> " + str( match_count ) + " should = " + str( should_be )
        self.assertEqual( match_count, should_be, msg = error_string )

        #----------------------------------------------------------------------#
        # "A W Smith"
        #----------------------------------------------------------------------#

        name_string = "A W Smith"

        # strict, no partial - 0
        should_be = 0
        do_strict = True
        do_partial = False
        test_qs = Person.look_up_person_from_name( name_string, do_strict_match_IN = do_strict, do_partial_match_IN = do_partial )
        match_count = test_qs.count()
        error_string = name_string + ": strict = " + str( do_strict ) + "; partial = " + str( do_partial ) + " --> " + str( match_count ) + " should = " + str( should_be )
        self.assertEqual( match_count, should_be, msg = error_string )
        
        # strict, partial - 1
        should_be = 1
        do_strict = True
        do_partial = True
        test_qs = Person.look_up_person_from_name( name_string, do_strict_match_IN = do_strict, do_partial_match_IN = do_partial )
        match_count = test_qs.count()
        error_string = name_string + ": strict = " + str( do_strict ) + "; partial = " + str( do_partial ) + " --> " + str( match_count ) + " should = " + str( should_be )
        self.assertEqual( match_count, should_be, msg = error_string )
        
        # not strict, no partial - 0
        should_be = 0
        do_strict = False
        do_partial = False
        test_qs = Person.look_up_person_from_name( name_string, do_strict_match_IN = do_strict, do_partial_match_IN = do_partial )
        match_count = test_qs.count()
        error_string = name_string + ": strict = " + str( do_strict ) + "; partial = " + str( do_partial ) + " --> " + str( match_count ) + " should = " + str( should_be )
        self.assertEqual( match_count, should_be, msg = error_string )

        # not strict, partial - 1
        should_be = 1
        do_strict = False
        do_partial = True
        test_qs = Person.look_up_person_from_name( name_string, do_strict_match_IN = do_strict, do_partial_match_IN = do_partial )
        match_count = test_qs.count()
        error_string = name_string + ": strict = " + str( do_strict ) + "; partial = " + str( do_partial ) + " --> " + str( match_count ) + " should = " + str( should_be )
        self.assertEqual( match_count, should_be, msg = error_string )

        #----------------------------------------------------------------------#
        # "Alma Smith"
        #----------------------------------------------------------------------#

        name_string = "Alma Smith"

        # strict, no partial - 0
        should_be = 0
        do_strict = True
        do_partial = False
        test_qs = Person.look_up_person_from_name( name_string, do_strict_match_IN = do_strict, do_partial_match_IN = do_partial )
        match_count = test_qs.count()
        error_string = name_string + ": strict = " + str( do_strict ) + "; partial = " + str( do_partial ) + " --> " + str( match_count ) + " should = " + str( should_be )
        self.assertEqual( match_count, should_be, msg = error_string )
        
        # strict, partial - 0
        should_be = 0
        do_strict = True
        do_partial = True
        test_qs = Person.look_up_person_from_name( name_string, do_strict_match_IN = do_strict, do_partial_match_IN = do_partial )
        match_count = test_qs.count()
        error_string = name_string + ": strict = " + str( do_strict ) + "; partial = " + str( do_partial ) + " --> " + str( match_count ) + " should = " + str( should_be )
        self.assertEqual( match_count, should_be, msg = error_string )
        
        # not strict, no partial - 1
        should_be = 1
        do_strict = False
        do_partial = False
        test_qs = Person.look_up_person_from_name( name_string, do_strict_match_IN = do_strict, do_partial_match_IN = do_partial )
        match_count = test_qs.count()
        error_string = name_string + ": strict = " + str( do_strict ) + "; partial = " + str( do_partial ) + " --> " + str( match_count ) + " should = " + str( should_be )
        self.assertEqual( match_count, should_be, msg = error_string )

        # not strict, partial - 1
        should_be = 1
        do_strict = False
        do_partial = True
        test_qs = Person.look_up_person_from_name( name_string, do_strict_match_IN = do_strict, do_partial_match_IN = do_partial )
        match_count = test_qs.count()
        error_string = name_string + ": strict = " + str( do_strict ) + "; partial = " + str( do_partial ) + " --> " + str( match_count ) + " should = " + str( should_be )
        self.assertEqual( match_count, should_be, msg = error_string )

        #----------------------------------------------------------------------#
        # "W Smith"
        #----------------------------------------------------------------------#

        name_string = "W Smith"

        # strict, no partial - 0
        should_be = 0
        do_strict = True
        do_partial = False
        test_qs = Person.look_up_person_from_name( name_string, do_strict_match_IN = do_strict, do_partial_match_IN = do_partial )
        match_count = test_qs.count()
        error_string = name_string + ": strict = " + str( do_strict ) + "; partial = " + str( do_partial ) + " --> " + str( match_count ) + " should = " + str( should_be )
        self.assertEqual( match_count, should_be, msg = error_string )
        
        # strict, partial - 0
        should_be = 0
        do_strict = True
        do_partial = True
        test_qs = Person.look_up_person_from_name( name_string, do_strict_match_IN = do_strict, do_partial_match_IN = do_partial )
        match_count = test_qs.count()
        error_string = name_string + ": strict = " + str( do_strict ) + "; partial = " + str( do_partial ) + " --> " + str( match_count ) + " should = " + str( should_be )
        self.assertEqual( match_count, should_be, msg = error_string )
        
        # not strict, no partial - 0
        should_be = 0
        do_strict = False
        do_partial = False
        test_qs = Person.look_up_person_from_name( name_string, do_strict_match_IN = do_strict, do_partial_match_IN = do_partial )
        match_count = test_qs.count()
        error_string = name_string + ": strict = " + str( do_strict ) + "; partial = " + str( do_partial ) + " --> " + str( match_count ) + " should = " + str( should_be )
        self.assertEqual( match_count, should_be, msg = error_string )

        # not strict, partial - 0
        should_be = 0
        do_strict = False
        do_partial = True
        test_qs = Person.look_up_person_from_name( name_string, do_strict_match_IN = do_strict, do_partial_match_IN = do_partial )
        match_count = test_qs.count()
        error_string = name_string + ": strict = " + str( do_strict ) + "; partial = " + str( do_partial ) + " --> " + str( match_count ) + " should = " + str( should_be )
        self.assertEqual( match_count, should_be, msg = error_string )

        #----------------------------------------------------------------------#
        # "Alma Wheeler Smith"
        #----------------------------------------------------------------------#

        name_string = "Alma Wheeler Smith"

        # strict, no partial - 1
        should_be = 1
        do_strict = True
        do_partial = False
        test_qs = Person.look_up_person_from_name( name_string, do_strict_match_IN = do_strict, do_partial_match_IN = do_partial )
        match_count = test_qs.count()
        error_string = name_string + ": strict = " + str( do_strict ) + "; partial = " + str( do_partial ) + " --> " + str( match_count ) + " should = " + str( should_be )
        self.assertEqual( match_count, should_be, msg = error_string )
        
        # strict, partial - 1
        should_be = 1
        do_strict = True
        do_partial = True
        test_qs = Person.look_up_person_from_name( name_string, do_strict_match_IN = do_strict, do_partial_match_IN = do_partial )
        match_count = test_qs.count()
        error_string = name_string + ": strict = " + str( do_strict ) + "; partial = " + str( do_partial ) + " --> " + str( match_count ) + " should = " + str( should_be )
        self.assertEqual( match_count, should_be, msg = error_string )
        
        # not strict, no partial - 1
        should_be = 1
        do_strict = False
        do_partial = False
        test_qs = Person.look_up_person_from_name( name_string, do_strict_match_IN = do_strict, do_partial_match_IN = do_partial )
        match_count = test_qs.count()
        error_string = name_string + ": strict = " + str( do_strict ) + "; partial = " + str( do_partial ) + " --> " + str( match_count ) + " should = " + str( should_be )
        self.assertEqual( match_count, should_be, msg = error_string )

        # not strict, partial - 1
        should_be = 1
        do_strict = False
        do_partial = True
        test_qs = Person.look_up_person_from_name( name_string, do_strict_match_IN = do_strict, do_partial_match_IN = do_partial )
        match_count = test_qs.count()
        error_string = name_string + ": strict = " + str( do_strict ) + "; partial = " + str( do_partial ) + " --> " + str( match_count ) + " should = " + str( should_be )
        self.assertEqual( match_count, should_be, msg = error_string )

        #----------------------------------------------------------------------#
        # "a smith"
        #----------------------------------------------------------------------#

        name_string = "A Smith".lower()

        # strict, no partial - 0
        should_be = 0
        do_strict = True
        do_partial = False
        test_qs = Person.look_up_person_from_name( name_string, do_strict_match_IN = do_strict, do_partial_match_IN = do_partial )
        match_count = test_qs.count()
        error_string = name_string + ": strict = " + str( do_strict ) + "; partial = " + str( do_partial ) + " --> " + str( match_count ) + " should = " + str( should_be )
        self.assertEqual( match_count, should_be, msg = error_string )
        
        # strict, partial - 2
        should_be = 2
        do_strict = True
        do_partial = True
        test_qs = Person.look_up_person_from_name( name_string, do_strict_match_IN = do_strict, do_partial_match_IN = do_partial )
        match_count = test_qs.count()
        error_string = name_string + ": strict = " + str( do_strict ) + "; partial = " + str( do_partial ) + " --> " + str( match_count ) + " should = " + str( should_be )
        self.assertEqual( match_count, should_be, msg = error_string )
        
        # not strict, no partial - 0
        should_be = 0
        do_strict = False
        do_partial = False
        test_qs = Person.look_up_person_from_name( name_string, do_strict_match_IN = do_strict, do_partial_match_IN = do_partial )
        match_count = test_qs.count()
        error_string = name_string + ": strict = " + str( do_strict ) + "; partial = " + str( do_partial ) + " --> " + str( match_count ) + " should = " + str( should_be )
        self.assertEqual( match_count, should_be, msg = error_string )

        # not strict, partial - 3
        should_be = 3
        do_strict = False
        do_partial = True
        test_qs = Person.look_up_person_from_name( name_string, do_strict_match_IN = do_strict, do_partial_match_IN = do_partial )
        match_count = test_qs.count()
        error_string = name_string + ": strict = " + str( do_strict ) + "; partial = " + str( do_partial ) + " --> " + str( match_count ) + " should = " + str( should_be )
        self.assertEqual( match_count, should_be, msg = error_string )

        #----------------------------------------------------------------------#
        # "smith"
        #----------------------------------------------------------------------#

        name_string = "Smith".lower()

        # strict, no partial - 0
        should_be = 0
        do_strict = True
        do_partial = False
        test_qs = Person.look_up_person_from_name( name_string, do_strict_match_IN = do_strict, do_partial_match_IN = do_partial )
        match_count = test_qs.count()
        error_string = name_string + ": strict = " + str( do_strict ) + "; partial = " + str( do_partial ) + " --> " + str( match_count ) + " should = " + str( should_be )
        self.assertEqual( match_count, should_be, msg = error_string )
        
        # strict, partial - 0
        should_be = 0
        do_strict = True
        do_partial = True
        test_qs = Person.look_up_person_from_name( name_string, do_strict_match_IN = do_strict, do_partial_match_IN = do_partial )
        match_count = test_qs.count()
        error_string = name_string + ": strict = " + str( do_strict ) + "; partial = " + str( do_partial ) + " --> " + str( match_count ) + " should = " + str( should_be )
        self.assertEqual( match_count, should_be, msg = error_string )
        
        # not strict, no partial - 0 (parses single name as first, not last)
        should_be = 0
        do_strict = False
        do_partial = False
        test_qs = Person.look_up_person_from_name( name_string, do_strict_match_IN = do_strict, do_partial_match_IN = do_partial )
        match_count = test_qs.count()
        error_string = name_string + ": strict = " + str( do_strict ) + "; partial = " + str( do_partial ) + " --> " + str( match_count ) + " should = " + str( should_be )
        self.assertEqual( match_count, should_be, msg = error_string )

        # not strict, partial - 0 (parses single name as first, not last)
        should_be = 0
        do_strict = False
        do_partial = True
        test_qs = Person.look_up_person_from_name( name_string, do_strict_match_IN = do_strict, do_partial_match_IN = do_partial )
        match_count = test_qs.count()
        error_string = name_string + ": strict = " + str( do_strict ) + "; partial = " + str( do_partial ) + " --> " + str( match_count ) + " should = " + str( should_be )
        self.assertEqual( match_count, should_be, msg = error_string )

        #----------------------------------------------------------------------#
        # "a w smith"
        #----------------------------------------------------------------------#

        name_string = "A W Smith".lower()

        # strict, no partial - 0
        should_be = 0
        do_strict = True
        do_partial = False
        test_qs = Person.look_up_person_from_name( name_string, do_strict_match_IN = do_strict, do_partial_match_IN = do_partial )
        match_count = test_qs.count()
        error_string = name_string + ": strict = " + str( do_strict ) + "; partial = " + str( do_partial ) + " --> " + str( match_count ) + " should = " + str( should_be )
        self.assertEqual( match_count, should_be, msg = error_string )
        
        # strict, partial - 1
        should_be = 1
        do_strict = True
        do_partial = True
        test_qs = Person.look_up_person_from_name( name_string, do_strict_match_IN = do_strict, do_partial_match_IN = do_partial )
        match_count = test_qs.count()
        error_string = name_string + ": strict = " + str( do_strict ) + "; partial = " + str( do_partial ) + " --> " + str( match_count ) + " should = " + str( should_be )
        self.assertEqual( match_count, should_be, msg = error_string )
        
        # not strict, no partial - 0
        should_be = 0
        do_strict = False
        do_partial = False
        test_qs = Person.look_up_person_from_name( name_string, do_strict_match_IN = do_strict, do_partial_match_IN = do_partial )
        match_count = test_qs.count()
        error_string = name_string + ": strict = " + str( do_strict ) + "; partial = " + str( do_partial ) + " --> " + str( match_count ) + " should = " + str( should_be )
        self.assertEqual( match_count, should_be, msg = error_string )

        # not strict, partial - 1
        should_be = 1
        do_strict = False
        do_partial = True
        test_qs = Person.look_up_person_from_name( name_string, do_strict_match_IN = do_strict, do_partial_match_IN = do_partial )
        match_count = test_qs.count()
        error_string = name_string + ": strict = " + str( do_strict ) + "; partial = " + str( do_partial ) + " --> " + str( match_count ) + " should = " + str( should_be )
        self.assertEqual( match_count, should_be, msg = error_string )

        #----------------------------------------------------------------------#
        # "alma smith"
        #----------------------------------------------------------------------#

        name_string = "Alma Smith".lower()

        # strict, no partial - 0
        should_be = 0
        do_strict = True
        do_partial = False
        test_qs = Person.look_up_person_from_name( name_string, do_strict_match_IN = do_strict, do_partial_match_IN = do_partial )
        match_count = test_qs.count()
        error_string = name_string + ": strict = " + str( do_strict ) + "; partial = " + str( do_partial ) + " --> " + str( match_count ) + " should = " + str( should_be )
        self.assertEqual( match_count, should_be, msg = error_string )
        
        # strict, partial - 0
        should_be = 0
        do_strict = True
        do_partial = True
        test_qs = Person.look_up_person_from_name( name_string, do_strict_match_IN = do_strict, do_partial_match_IN = do_partial )
        match_count = test_qs.count()
        error_string = name_string + ": strict = " + str( do_strict ) + "; partial = " + str( do_partial ) + " --> " + str( match_count ) + " should = " + str( should_be )
        self.assertEqual( match_count, should_be, msg = error_string )
        
        # not strict, no partial - 1
        should_be = 1
        do_strict = False
        do_partial = False
        test_qs = Person.look_up_person_from_name( name_string, do_strict_match_IN = do_strict, do_partial_match_IN = do_partial )
        match_count = test_qs.count()
        error_string = name_string + ": strict = " + str( do_strict ) + "; partial = " + str( do_partial ) + " --> " + str( match_count ) + " should = " + str( should_be )
        self.assertEqual( match_count, should_be, msg = error_string )

        # not strict, partial - 1
        should_be = 1
        do_strict = False
        do_partial = True
        test_qs = Person.look_up_person_from_name( name_string, do_strict_match_IN = do_strict, do_partial_match_IN = do_partial )
        match_count = test_qs.count()
        error_string = name_string + ": strict = " + str( do_strict ) + "; partial = " + str( do_partial ) + " --> " + str( match_count ) + " should = " + str( should_be )
        self.assertEqual( match_count, should_be, msg = error_string )

        #----------------------------------------------------------------------#
        # "w smith"
        #----------------------------------------------------------------------#

        name_string = "W Smith".lower()

        # strict, no partial - 0
        should_be = 0
        do_strict = True
        do_partial = False
        test_qs = Person.look_up_person_from_name( name_string, do_strict_match_IN = do_strict, do_partial_match_IN = do_partial )
        match_count = test_qs.count()
        error_string = name_string + ": strict = " + str( do_strict ) + "; partial = " + str( do_partial ) + " --> " + str( match_count ) + " should = " + str( should_be )
        self.assertEqual( match_count, should_be, msg = error_string )
        
        # strict, partial - 0
        should_be = 0
        do_strict = True
        do_partial = True
        test_qs = Person.look_up_person_from_name( name_string, do_strict_match_IN = do_strict, do_partial_match_IN = do_partial )
        match_count = test_qs.count()
        error_string = name_string + ": strict = " + str( do_strict ) + "; partial = " + str( do_partial ) + " --> " + str( match_count ) + " should = " + str( should_be )
        self.assertEqual( match_count, should_be, msg = error_string )
        
        # not strict, no partial - 0
        should_be = 0
        do_strict = False
        do_partial = False
        test_qs = Person.look_up_person_from_name( name_string, do_strict_match_IN = do_strict, do_partial_match_IN = do_partial )
        match_count = test_qs.count()
        error_string = name_string + ": strict = " + str( do_strict ) + "; partial = " + str( do_partial ) + " --> " + str( match_count ) + " should = " + str( should_be )
        self.assertEqual( match_count, should_be, msg = error_string )

        # not strict, partial - 0
        should_be = 0
        do_strict = False
        do_partial = True
        test_qs = Person.look_up_person_from_name( name_string, do_strict_match_IN = do_strict, do_partial_match_IN = do_partial )
        match_count = test_qs.count()
        error_string = name_string + ": strict = " + str( do_strict ) + "; partial = " + str( do_partial ) + " --> " + str( match_count ) + " should = " + str( should_be )
        self.assertEqual( match_count, should_be, msg = error_string )

        #----------------------------------------------------------------------#
        # "alma wheeler smith"
        #----------------------------------------------------------------------#

        name_string = "Alma Wheeler Smith".lower()

        # strict, no partial - 1
        should_be = 1
        do_strict = True
        do_partial = False
        test_qs = Person.look_up_person_from_name( name_string, do_strict_match_IN = do_strict, do_partial_match_IN = do_partial )
        match_count = test_qs.count()
        error_string = name_string + ": strict = " + str( do_strict ) + "; partial = " + str( do_partial ) + " --> " + str( match_count ) + " should = " + str( should_be )
        self.assertEqual( match_count, should_be, msg = error_string )
        
        # strict, partial - 1
        should_be = 1
        do_strict = True
        do_partial = True
        test_qs = Person.look_up_person_from_name( name_string, do_strict_match_IN = do_strict, do_partial_match_IN = do_partial )
        match_count = test_qs.count()
        error_string = name_string + ": strict = " + str( do_strict ) + "; partial = " + str( do_partial ) + " --> " + str( match_count ) + " should = " + str( should_be )
        self.assertEqual( match_count, should_be, msg = error_string )
        
        # not strict, no partial - 1
        should_be = 1
        do_strict = False
        do_partial = False
        test_qs = Person.look_up_person_from_name( name_string, do_strict_match_IN = do_strict, do_partial_match_IN = do_partial )
        match_count = test_qs.count()
        error_string = name_string + ": strict = " + str( do_strict ) + "; partial = " + str( do_partial ) + " --> " + str( match_count ) + " should = " + str( should_be )
        self.assertEqual( match_count, should_be, msg = error_string )

        # not strict, partial - 1
        should_be = 1
        do_strict = False
        do_partial = True
        test_qs = Person.look_up_person_from_name( name_string, do_strict_match_IN = do_strict, do_partial_match_IN = do_partial )
        match_count = test_qs.count()
        error_string = name_string + ": strict = " + str( do_strict ) + "; partial = " + str( do_partial ) + " --> " + str( match_count ) + " should = " + str( should_be )
        self.assertEqual( match_count, should_be, msg = error_string )

    #-- END test method test_look_up_person_from_name() --#


    def test_update_entity( self ):
        
        # declare variables
        me = "test_update_entity"
        debug_flag = None
        error_string = None
        current_type = None
        my_id_list = None
        my_id = None
        my_instance = None
        entity_instance = None
        entity_instance_id = None
        original_entity_id = None
        test_value = None
        should_be = None

        # debug
        debug_flag = self.DEBUG

        print( '\n\n====> In {}.{}\n'.format( self.CLASS_NAME, me ) )
        
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
        
            # get instance
            my_instance = self.MY_CLASS.objects.get( id = my_id )
            
            # create entity for it.
            entity_instance = my_instance.update_entity()
            original_entity_id = entity_instance.id
            my_instance.save()
            
            # validate
            self.validate_entity( my_id )
            
            # call the update method again.
            entity_instance = my_instance.update_entity()
            entity_instance_id = entity_instance.id
            my_instance.save()
            
            # validate again.
            self.validate_entity( my_id )
            
            # make sure the two entitie share ID (same entity).
            test_value = entity_instance_id
            should_be = original_entity_id
            error_string = "Entity after 2nd call to update_entity() has ID: {}, should be ID: {}".format( test_value, should_be )
            self.assertEqual( test_value, should_be, msg = error_string )            
            
        #-- END loop over test IDs. --#
        
    #-- END test method test_update_entity() --#


#-- END test class PersonModelTest --#
