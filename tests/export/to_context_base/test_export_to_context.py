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
from context_text.article_coding.open_calais_v2.open_calais_v2_article_coder import OpenCalaisV2ArticleCoder
from context_text.export.to_context_base.export_to_context import ExportToContext
from context_text.models import Article
from context_text.models import Article_Subject
from context_text.models import Person
from context_text.shared.context_text_base import ContextTextBase
from context_text.tests.test_helper import TestHelper


class ExportToContextTest( django.test.TestCase ):
    

    #----------------------------------------------------------------------------
    # ! ==> Constants-ish
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
    # ! ==> class methods
    #----------------------------------------------------------------------


    #---------------------------------------------------------------------------
    # ! ==> overridden built-in methods
    #---------------------------------------------------------------------------


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
        
        print( '\n====> In {}.{}'.format( self.CLASS_NAME, me ) )
        
        # get setup error count
        setup_error_count = self.setup_error_count
        
        # should be 0
        error_message = ";".join( self.setup_error_list )
        self.assertEqual( setup_error_count, 0, msg = error_message )
        
    #-- END test method test_django_config_installed() --#


    #----------------------------------------------------------------------------
    # ! ==> instance methods - shared methods
    #----------------------------------------------------------------------------


    def validate_person_entity_list( self, person_entity_list_IN, article_person_qs_IN ):

        # declare variables
        me = "validate_person_entity_list"
        debug_flag = None
        error_string = None
        test_value = None
        should_be = None
        should_not_be = None
        person_entity_list = None
        article_person_qs = None
        person_entity_count = None
        article_person_count = None
        person_entity = None
        trait_instance = None
        person_first_name = None
        person_middle_name = None
        person_last_name = None
        person_full_name = None
        id_instance = None
        person_django_id = None
        test_qs = None
        test_count = None

        # debug
        debug_flag = self.DEBUG

        print( '\n\n========> In {}.{}\n'.format( self.CLASS_NAME, me ) )

        # make sure we have an entity list
        if ( person_entity_list_IN is not None ):
        
            # store in internal variable.
            person_entity_list = person_entity_list_IN
        
            # make sure we have a QuerySet.
            if ( article_person_qs_IN is not None ):
            
                # store in internal variable
                article_person_qs = article_person_qs_IN
            
                # compare counts
                person_entity_count = len( person_entity_list )
                article_person_count = article_person_qs.count()

                # counts should be equal.                
                test_value = person_entity_count
                should_be = article_person_count
                error_string = "Getting person list: entity count {} should be {}".format( test_value, should_be )
                self.assertEqual( test_value, should_be, msg = error_string )
                
                # loop over the entities
                for person_entity in person_entity_list:
                
                    # retrieve some values we can use to filter the author_qs to
                    #     make sure each author entity has an accompanying
                    #     Article_Author instance.
                    
                    # first name
                    trait_instance = person_entity.get_trait( Person.TRAIT_NAME_FIRST_NAME )
                    person_first_name = trait_instance.get_trait_value()
                    
                    # middle name
                    trait_instance = person_entity.get_trait( Person.TRAIT_NAME_MIDDLE_NAME )
                    person_middle_name = trait_instance.get_trait_value()
                    
                    # last name
                    trait_instance = person_entity.get_trait( Person.TRAIT_NAME_LAST_NAME )
                    person_last_name = trait_instance.get_trait_value()
                    
                    # full name
                    trait_instance = person_entity.get_trait( Person.TRAIT_NAME_FULL_NAME )
                    person_full_name = trait_instance.get_trait_value()
                    
                    # get identifier for django ID
                    id_instance = person_entity.get_identifier( Person.ENTITY_ID_TYPE_PERSON_SOURCENET_ID )
                    person_django_id = id_instance.uuid
                    
                    # filter
                    test_qs = article_person_qs.filter( person__first_name = person_first_name )
                    test_qs = test_qs.filter( person__middle_name = person_middle_name )
                    test_qs = test_qs.filter( person__last_name = person_last_name )
                    test_qs = test_qs.filter( person__full_name_string = person_full_name )
                    test_qs = test_qs.filter( person__pk = person_django_id )
                    
                    # get count
                    test_count = test_qs.count()
                    
                    # should be 1
                    test_value = test_count
                    should_be = 1
                    error_string = "Getting Article_Person for first name: {}, middle name: {}, last name: {}, full name string: {}, django ID: {}; found {}, should be {}".format( person_first_name, person_middle_name, person_last_name, person_full_name, person_django_id, test_value, should_be )
                    self.assertEqual( test_value, should_be, msg = error_string )
                
                #-- END loop over person entities. --#
            
            #-- END loop over Article_Data QuerySet --#
        
        #-- END loop over article IDs. --#
                
    #-- END test method test_make_author_entity_list() --#


    #----------------------------------------------------------------------------
    # ! ==> instance methods - tests
    #----------------------------------------------------------------------------


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


    def test_create_article_relations( self ):
        
        '''
        - pick an article
        - create entities and make author, subject, and source lists from it
        - call method.
        - build trait dictionary just like in the method.
        - check relations.
        '''
        
        # declare variables
        me = "test_create_article_relations"
        export_instance = None
        debug_flag = None
        error_string = None
        article_id = None
        article_instance = None
        article_data_qs = None
        article_data_instance = None
        article_entity = None
        author_entity_list = None
        subject_entity_list = None
        source_entity_list = None
        create_status = None
        is_create_success = None
        trait_dict = None

        # debug
        debug_flag = self.DEBUG

        print( '\n\n====> In {}.{}\n'.format( self.CLASS_NAME, me ) )
        
        # init
        export_instance = ExportToContext()
        
        # first, get a few Articles to test with.  For each, get Article_Data,
        #     pass it to method, then make sure that what comes back matches what
        #     is in the Article_Data.
        for article_id in self.TEST_ID_LIST:
        
            # load article.
            article_instance = Article.objects.get( pk = article_id )
            
            # retrieve related Article_Data QuerySet.
            article_data_qs = article_instance.article_data_set.all()
            article_data_qs = TestHelper.filter_article_data_open_calais_v2( article_data_qs )
            article_data_instance = article_data_qs.get()
            
            # article entity
            article_entity = article_instance.update_entity()
            
            # get list of author entities...
            author_entity_list = ExportToContext.make_author_entity_list( article_data_instance )

            # ...subject entities (including sources)...
            subject_entity_list = ExportToContext.make_subject_entity_list( article_data_instance,
                                                                            limit_to_sources_IN = False,
                                                                            include_sources_in_subjects_IN = True )

            # ...and source entities.
            source_entity_list = ExportToContext.make_subject_entity_list( article_data_instance,
                                                                           limit_to_sources_IN = True,
                                                                           include_sources_in_subjects_IN = False )
                                                                           
            # call the create newspaper relations method.
            create_status = export_instance.create_article_relations( article_entity,
                                                                      author_entity_list_IN = author_entity_list,
                                                                      subject_entity_list_IN = subject_entity_list,
                                                                      source_entity_list_IN = source_entity_list,
                                                                      article_data_IN = article_data_instance )
                                                                        
            # success?
            test_value = create_status.is_success()
            should_be = True
            error_string = "Creating article-related relations for article_entity: {}, authors: {}, subjects: {}, sources: {}, and Article_Data: {}.  Success?: {}, should be {}.".format( article_entity, author_entity_list, subject_entity_list, source_entity_list, article_data_instance, test_value, should_be )
            self.assertEqual( test_value, should_be, msg = error_string )
            
        #-- END loop over articles --#
            
    #-- END test method test_create_article_relations() --#


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
        
        '''
        - pick an article
        - create entities and make author, subject, and source lists from it
        - call method.
        - build trait dictionary just like in the method.
        - check relations.
        '''
        
        # declare variables
        me = "test_create_newspaper_relations"
        export_instance = None
        debug_flag = None
        error_string = None
        article_id = None
        article_instance = None
        article_data_qs = None
        article_data_instance = None
        article_entity = None
        newspaper_instance = None
        newspaper_entity = None
        author_entity_list = None
        subject_entity_list = None
        source_entity_list = None
        create_status = None
        is_create_success = None
        trait_dict = None

        # debug
        debug_flag = self.DEBUG

        print( '\n\n====> In {}.{}\n'.format( self.CLASS_NAME, me ) )
        
        # init
        export_instance = ExportToContext()
        
        # first, get a few Articles to test with.  For each, get Article_Data,
        #     pass it to method, then make sure that what comes back matches what
        #     is in the Article_Data.
        for article_id in self.TEST_ID_LIST:
        
            # load article.
            article_instance = Article.objects.get( pk = article_id )
            
            # retrieve related Article_Data QuerySet.
            article_data_qs = article_instance.article_data_set.all()
            article_data_qs = TestHelper.filter_article_data_open_calais_v2( article_data_qs )
            article_data_instance = article_data_qs.get()
            
            # article entity
            article_entity = article_instance.update_entity()
            
            # newspaper entity
            newspaper_instance = article_instance.newspaper
            newspaper_entity = newspaper_instance.update_entity()
            
            # get list of author entities...
            author_entity_list = ExportToContext.make_author_entity_list( article_data_instance )

            # ...subject entities (including sources)...
            subject_entity_list = ExportToContext.make_subject_entity_list( article_data_instance,
                                                                            limit_to_sources_IN = False,
                                                                            include_sources_in_subjects_IN = True )

            # ...and source entities.
            source_entity_list = ExportToContext.make_subject_entity_list( article_data_instance,
                                                                           limit_to_sources_IN = True,
                                                                           include_sources_in_subjects_IN = False )
                                                                           
            # call the create newspaper relations method.
            create_status = export_instance.create_newspaper_relations( newspaper_entity,
                                                                        article_entity,
                                                                        author_entity_list_IN = author_entity_list,
                                                                        subject_entity_list_IN = subject_entity_list,
                                                                        source_entity_list_IN = source_entity_list,
                                                                        article_data_IN = article_data_instance )
                                                                        
            # success?
            test_value = create_status.is_success()
            should_be = True
            error_string = "Creating newspaper-related relations for newspaper entity: {}, article_entity: {}, authors: {}, subjects: {}, sources: {}, and Article_Data: {}.  Success?: {}, should be {}.".format( newspaper_entity, article_entity, author_entity_list, subject_entity_list, source_entity_list, article_data_instance, test_value, should_be )
            self.assertEqual( test_value, should_be, msg = error_string )
            
            '''
            # Now, need to do the same work as the method to check the results.
            
            # shared traits for these relations, also used to filter.
            # - includes article's pub_date and sourcenet article ID.
            trait_dict = self.make_relation_trait_dict( article_entity_IN = article_entity_IN )
            relation_trait_filter_dict = trait_dict
                        
            # ! ----> "newspaper_article"    # FROM newspaper TO article.
        
            # got article entity?
            if ( article_entity_IN is not None ):

                # get type
                relation_type = Entity_Relation_Type.objects.get( slug = ContextTextBase.CONTEXT_RELATION_TYPE_SLUG_NEWSPAPER_ARTICLE )
                
                # create relation if no match of FROM, TO, type, pub_date, and article ID.
                relation = Entity_Relation.create_entity_relation( from_IN = newspaper_entity_IN,
                                                                   to_IN = article_entity_IN,
                                                                   type_IN = relation_type,
                                                                   trait_name_to_value_map_IN = trait_dict,
                                                                   match_trait_dict_IN = relation_trait_filter_dict )                
            
            #-- END check to see if article entity. --#
            
            # ! ----> "newspaper_reporter"  # FROM newspaper TO person (reporter) THROUGH article.
            relation_type_slug = ContextTextBase.CONTEXT_RELATION_TYPE_SLUG_NEWSPAPER_REPORTER
            relation_type = Entity_Relation_Type.objects.get( slug = relation_type_slug )
            person_entity_list = author_entity_list_IN

            # got people in list?
            if ( ( person_entity_list is not None ) and ( len( person_entity_list ) > 0 ) ):
            
                # yes, there are people.  Loop.
                for person_entity in person_entity_list:
                
                    # create relation if no match of FROM, TO, type, and pub_date.
                    relation = Entity_Relation.create_entity_relation( from_IN = newspaper_entity_IN,
                                                                       to_IN = person_entity,
                                                                       through_IN = article_entity_IN,
                                                                       type_IN = relation_type,
                                                                       trait_name_to_value_map_IN = trait_dict,
                                                                       match_trait_dict_IN = relation_trait_filter_dict )
                
                #-- END loop over people --#
            
            #-- END check to see if person entities in list. --#
                
            # ! ----> "newspaper_subject"    # FROM newspaper TO person (subject, including sources) THROUGH article.
            relation_type_slug = ContextTextBase.CONTEXT_RELATION_TYPE_SLUG_NEWSPAPER_SUBJECT
            relation_type = Entity_Relation_Type.objects.get( slug = relation_type_slug )
            person_entity_list = subject_entity_list_IN

            # got people in list?
            if ( ( person_entity_list is not None ) and ( len( person_entity_list ) > 0 ) ):
            
                # yes, there are people.  Loop.
                for person_entity in person_entity_list:
                
                    # create relation if no match of FROM, TO, type, and pub_date.
                    relation = Entity_Relation.create_entity_relation( from_IN = newspaper_entity_IN,
                                                                       to_IN = person_entity,
                                                                       through_IN = article_entity_IN,
                                                                       type_IN = relation_type,
                                                                       trait_name_to_value_map_IN = trait_dict,
                                                                       match_trait_dict_IN = relation_trait_filter_dict )
                
                #-- END loop over people --#
            
            #-- END check to see if person entities in list. --#
                
            # ! ----> "newspaper_source"      # FROM newspaper TO person (source) THROUGH article.
            relation_type_slug = ContextTextBase.CONTEXT_RELATION_TYPE_SLUG_NEWSPAPER_SOURCE
            relation_type = Entity_Relation_Type.objects.get( slug = relation_type_slug )
            person_entity_list = source_entity_list_IN

            # got people in list?
            if ( ( person_entity_list is not None ) and ( len( person_entity_list ) > 0 ) ):
            
                # yes, there are people.  Loop.
                for person_entity in person_entity_list:
                
                    # create relation if no match of FROM, TO, type, and pub_date.
                    relation = Entity_Relation.create_entity_relation( from_IN = newspaper_entity_IN,
                                                                       to_IN = person_entity,
                                                                       through_IN = article_entity_IN,
                                                                       type_IN = relation_type,
                                                                       trait_name_to_value_map_IN = trait_dict,
                                                                       match_trait_dict_IN = relation_trait_filter_dict )
                
                #-- END loop over people --#
            
            #-- END check to see if person entities in list. --#
            '''
            
        #-- END loop over articles. --#
                        
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


    def test_make_author_entity_list( self ):

        # declare variables
        me = "test_make_author_entity_list"
        debug_flag = None
        error_string = None
        automated_coder_user = None
        test_value = None
        should_be = None
        should_not_be = None
        article_id = None
        article_instance = None
        article_data_qs = None
        article_data_instance = None
        person_entity_list = None
        article_person_qs = None

        # debug
        debug_flag = self.DEBUG

        print( '\n\n====> In {}.{}\n'.format( self.CLASS_NAME, me ) )
        
        # first, get a few Articles to test with.  For each, get Article_Data,
        #     pass it to method, then make sure that what comes back matches what
        #     is in the Article_Data.
        for article_id in self.TEST_ID_LIST:
        
            # load article.
            article_instance = Article.objects.get( pk = article_id )
            
            # retrieve related Article_Data QuerySet.
            article_data_qs = article_instance.article_data_set.all()
            article_data_qs = TestHelper.filter_article_data_open_calais_v2( article_data_qs )
            
            # loop.
            for article_data_instance in article_data_qs:
            
                # retrieve author list.
                person_entity_list = ExportToContext.make_author_entity_list( article_data_instance )
                
                # get Article_Author QuerySet
                article_person_qs = article_data_instance.article_author_set.all()

                # validate
                self.validate_person_entity_list( person_entity_list, article_person_qs )
            
            #-- END loop over Article_Data QuerySet --#
        
        #-- END loop over article IDs. --#
                
    #-- END test method test_make_author_entity_list() --#


    def test_make_relation_trait_dict( self ):

        # declare variables
        me = "test_make_relation_trait_dict"
        debug_flag = None
        error_string = None
        test_value = None
        should_be = None
        should_not_be = None
        article_id = None
        article_instance = None
        article_data_qs = None
        article_data_instance = None
        article_entity = None
        trait_dict = None
        coder_user = None

        # debug
        debug_flag = self.DEBUG

        print( '\n\n====> In {}.{}\n'.format( self.CLASS_NAME, me ) )
        
        # first, get a few Articles to test with.  For each, get Article_Data,
        #     pass it to method, then make sure that what comes back matches what
        #     is in the Article_Data.
        for article_id in self.TEST_ID_LIST:
        
            # load article.
            article_instance = Article.objects.get( pk = article_id )
            
            # retrieve related Article_Data QuerySet.
            article_data_qs = article_instance.article_data_set.all()
            article_data_qs = TestHelper.filter_article_data_open_calais_v2( article_data_qs )
            
            # get entity for Article
            article_entity = article_instance.update_entity()
            
            # loop over Article_Data
            for article_data_instance in article_data_qs:
            
                # create trait dict.
                trait_dict = ExportToContext.make_relation_trait_dict( article_entity_IN = article_entity, article_data_IN = article_data_instance )
                
                # tests
                
                # ! ----> pub_date
                trait_name = ContextTextBase.CONTEXT_TRAIT_NAME_PUB_DATE
                test_value = trait_dict.get( trait_name, None )
                should_be = article_instance.pub_date
                should_be = should_be.strftime( "%Y-%m-%d" )
                error_string = "Retrieving value for name \"{}\" from trait_dict - found value {}, should be {}.".format( trait_name, test_value, should_be )
                self.assertEqual( test_value, should_be, msg = error_string )
                
                # ! ----> Article ID
                trait_name = Article.ENTITY_ID_TYPE_ARTICLE_SOURCENET_ID
                test_value = trait_dict.get( trait_name, None )
                test_value = int( test_value )
                should_be = article_instance.id
                error_string = "Retrieving value for name \"{}\" from trait_dict - found value {}, should be {}.".format( trait_name, test_value, should_be )
                self.assertEqual( test_value, should_be, msg = error_string )
                
                # now get coder user.
                coder_user = article_data_instance.coder
                
                # ! ----> coder ID
                trait_name = ContextTextBase.CONTEXT_TRAIT_NAME_CODER_ID
                test_value = trait_dict.get( trait_name, None )
                test_value = int( test_value )
                should_be = coder_user.id
                error_string = "Retrieving value for name \"{}\" from trait_dict - found value {}, should be {}.".format( trait_name, test_value, should_be )
                self.assertEqual( test_value, should_be, msg = error_string )

                # ! ----> coder username
                trait_name = ContextTextBase.CONTEXT_TRAIT_NAME_CODER_USERNAME
                test_value = trait_dict.get( trait_name, None )
                should_be = coder_user.username
                error_string = "Retrieving value for name \"{}\" from trait_dict - found value {}, should be {}.".format( trait_name, test_value, should_be )
                self.assertEqual( test_value, should_be, msg = error_string )

                # ! ----> coder type
                trait_name = ContextTextBase.CONTEXT_TRAIT_NAME_CODER_TYPE
                test_value = trait_dict.get( trait_name, None )
                should_be = article_data_instance.coder_type
                error_string = "Retrieving value for name \"{}\" from trait_dict - found value {}, should be {}.".format( trait_name, test_value, should_be )
                self.assertEqual( test_value, should_be, msg = error_string )
                
            #-- END loop over Article_Data. --#
        
        #-- END loop over article IDs. --#
                
    #-- END test method test_make_relation_trait_dict() --#


    def test_make_subject_entity_list( self ):

        # declare variables
        me = "test_make_subject_entity_list"
        debug_flag = None
        error_string = None
        test_value = None
        should_be = None
        should_not_be = None
        article_id = None
        article_instance = None
        article_data_qs = None
        article_data_instance = None
        person_entity_list = None
        article_person_qs = None

        # debug
        debug_flag = self.DEBUG

        # init
        
        # get automated coder
        automated_coder_user = ContextTextBase.get_automated_coding_user()

        print( '\n\n====> In {}.{}\n'.format( self.CLASS_NAME, me ) )

        # first, get a few Articles to test with.  For each, get Article_Data,
        #     pass it to method, then make sure that what comes back matches what
        #     is in the Article_Data.
        for article_id in self.TEST_ID_LIST:
        
            # load article.
            article_instance = Article.objects.get( pk = article_id )
            
            # retrieve related Article_Data QuerySet.
            article_data_qs = article_instance.article_data_set.all()
            article_data_qs = TestHelper.filter_article_data_open_calais_v2( article_data_qs )
            
            # loop.
            for article_data_instance in article_data_qs:
            
                print( "---------> Article_Data instance: {}".format( article_data_instance ) )
            
                # ! ----> retrieve all subject list, including sources.
                person_entity_list = ExportToContext.make_subject_entity_list( article_data_instance )
                
                # get Article_Person QuerySet
                article_person_qs = article_data_instance.article_subject_set.all()

                # validate
                self.validate_person_entity_list( person_entity_list, article_person_qs )
            
                # ! ----> retrieve all subject list, including sources (same as default).
                person_entity_list = ExportToContext.make_subject_entity_list( article_data_instance,
                                                                               limit_to_sources_IN = False,
                                                                               include_sources_in_subjects_IN = True )
                
                # get Article_Person QuerySet
                article_person_qs = article_data_instance.article_subject_set.all()

                # validate
                self.validate_person_entity_list( person_entity_list, article_person_qs )
            
                # ! ----> retrieve subject list, excluding sources.
                person_entity_list = ExportToContext.make_subject_entity_list( article_data_instance,
                                                                               limit_to_sources_IN = False,
                                                                               include_sources_in_subjects_IN = False )
                # get Article_Person QuerySet, excluding sources
                article_person_qs = article_data_instance.article_subject_set.filter( subject_type = Article_Subject.SUBJECT_TYPE_MENTIONED )

                # validate
                self.validate_person_entity_list( person_entity_list, article_person_qs )
            
                # ! ----> retrieve just source list.
                person_entity_list = ExportToContext.make_subject_entity_list( article_data_instance,
                                                                               limit_to_sources_IN = True,
                                                                               include_sources_in_subjects_IN = False )
                
                # get Article_Person QuerySet
                article_person_qs = article_data_instance.article_subject_set.filter( subject_type = Article_Subject.SUBJECT_TYPE_QUOTED )

                # validate
                self.validate_person_entity_list( person_entity_list, article_person_qs )
            
                # retrieve just source list (include_sources_in_subjects_IN
                #     should not matter).
                person_entity_list = ExportToContext.make_subject_entity_list( article_data_instance,
                                                                               limit_to_sources_IN = True,
                                                                               include_sources_in_subjects_IN = True )
                
                # get Article_Person QuerySet
                article_person_qs = article_data_instance.article_subject_set.filter( subject_type = Article_Subject.SUBJECT_TYPE_QUOTED )

                # validate
                self.validate_person_entity_list( person_entity_list, article_person_qs )
            
            #-- END loop over Article_Data QuerySet --#
        
        #-- END loop over article IDs. --#
                
    #-- END test method test_make_subject_entity_list() --#


#-- END test class ExportToContextTest --#
