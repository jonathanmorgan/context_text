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
from context.models import Entity_Relation
from context.models import Entity_Relation_Type

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


    def validate_article_article_relations( self, article_id_IN ):
        
        '''
        - pick an article
        - create entities and make author, subject, and source lists from it
        - call method.
        - build trait dictionary just like in the method.
        - check relations.
        '''
        
        # declare variables
        me = "validate_article_article_relations"
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
        trait_dict = None

        # declare variables - more in-depth testing.
        trait_dict = None
        relation_trait_filter_dict = None
        from_entity_list = None
        from_entity = None
        to_entity_list = None
        through_entity = None
        relation_type_slug = None

        # debug
        debug_flag = self.DEBUG

        print( '\n\n--------> In {}.{}\n'.format( self.CLASS_NAME, me ) )
        
        # init
        export_instance = ExportToContext()
        
        # article_id_IN should not be None
        error_string = "If you are validating article-related entities, you should pass in that article's ID, not None"
        self.assertIsNotNone( article_id_IN, msg = error_string )

        # make sure we have an article ID.
        if ( article_id_IN is not None ):
        
            article_id = article_id_IN
        
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
                                                                           
            # traits for actual relations, both article info and coder
            #     information from Article_Data.
            trait_dict = ExportToContext.make_relation_trait_dict( article_entity_IN = article_entity,
                                                                   article_data_IN = article_data_instance )            

            #------------------------------------------------------------------#
            # ! ----> Entity_Relation_Type slugs - FROM ARTICLE
            #------------------------------------------------------------------#

            # configure
            from_entity = article_entity
            through_entity = None


            # ! --------> CONTEXT_RELATION_TYPE_SLUG_AUTHOR = "author"    # FROM article TO reporter.

            # configure
            relation_type_slug = ContextTextBase.CONTEXT_RELATION_TYPE_SLUG_AUTHOR
            to_entity_list = author_entity_list
            
            # validate
            self.validate_relations( from_IN = from_entity,
                                     to_list_IN = to_entity_list,
                                     through_IN = through_entity,
                                     relation_type_slug_IN = relation_type_slug,
                                     trait_dict_IN = trait_dict )


            # ! --------> CONTEXT_RELATION_TYPE_SLUG_SOURCE = "source"    # FROM article TO source person.

            # configure
            relation_type_slug = ContextTextBase.CONTEXT_RELATION_TYPE_SLUG_SOURCE
            to_entity_list = source_entity_list
            
            # validate
            self.validate_relations( from_IN = from_entity,
                                     to_list_IN = to_entity_list,
                                     through_IN = through_entity,
                                     relation_type_slug_IN = relation_type_slug,
                                     trait_dict_IN = trait_dict )


            # ! --------> CONTEXT_RELATION_TYPE_SLUG_SUBJECT = "subject"  # FROM article TO subject person.

            # configure
            relation_type_slug = ContextTextBase.CONTEXT_RELATION_TYPE_SLUG_SUBJECT
            to_entity_list = subject_entity_list

            # validate
            self.validate_relations( from_IN = from_entity,
                                     to_list_IN = to_entity_list,
                                     through_IN = through_entity,
                                     relation_type_slug_IN = relation_type_slug,
                                     trait_dict_IN = trait_dict )

    
            #------------------------------------------------------------------#
            # ! ----> Entity_Relation_Type slugs - FROM reporter/author
            #------------------------------------------------------------------#

            # configure
            from_entity_list = author_entity_list
            through_entity = article_entity
            
            # got from entities?
            if ( ( from_entity_list is not None ) and ( len( from_entity_list ) > 0 ) ):
            
                # loop over entities for FROM
                for from_entity in from_entity_list:
                
                    # get ID
                    from_entity_id = from_entity.id
            

                    # ! --------> CONTEXT_RELATION_TYPE_SLUG_MENTIONED = "mentioned"  # FROM reporter/author TO subject THROUGH article (includes subjects and sources).
                    
                    # config
                    relation_type_slug = ContextTextBase.CONTEXT_RELATION_TYPE_SLUG_MENTIONED
                    to_entity_list = subject_entity_list
        
                    # validate
                    self.validate_relations( from_IN = from_entity,
                                             to_list_IN = to_entity_list,
                                             through_IN = through_entity,
                                             relation_type_slug_IN = relation_type_slug,
                                             trait_dict_IN = trait_dict )

    
                    # ! --------> CONTEXT_RELATION_TYPE_SLUG_QUOTED = "quoted"  # FROM reporter TO source THROUGH article.
                    
                    # config
                    relation_type_slug = ContextTextBase.CONTEXT_RELATION_TYPE_SLUG_QUOTED
                    to_entity_list = source_entity_list
        
                    # validate
                    self.validate_relations( from_IN = from_entity,
                                             to_list_IN = to_entity_list,
                                             through_IN = through_entity,
                                             relation_type_slug_IN = relation_type_slug,
                                             trait_dict_IN = trait_dict )

    
                    # ! --------> CONTEXT_RELATION_TYPE_SLUG_SHARED_BYLINE = "shared_byline"  # FROM author TO author THROUGH article.
                    
                    # config
                    relation_type_slug = ContextTextBase.CONTEXT_RELATION_TYPE_SLUG_SHARED_BYLINE
                    to_entity_list = list( author_entity_list )
                    
                    # remove the current FROM author from the TO list.
                    if ( from_entity in to_entity_list ):
                    
                        # remove it.
                        to_entity_list.remove( from_entity )
                        
                    #-- END check to make sure current FROM is in TO (it better be...) --#
        
                    # validate
                    self.validate_relations( from_IN = from_entity,
                                             to_list_IN = to_entity_list,
                                             through_IN = through_entity,
                                             relation_type_slug_IN = relation_type_slug,
                                             trait_dict_IN = trait_dict )

                #-- END loop over author list

            #-- END check to see if author list? --#

            #------------------------------------------------------------------#
            # ! ----> Entity_Relation_Type slugs - FROM source
            #------------------------------------------------------------------#

            # configure
            from_entity_list = source_entity_list
            through_entity = article_entity

            # got a FROM list?
            if ( ( from_entity_list is not None ) and ( len( from_entity_list ) > 0 ) ):
            
                # loop over entities for FROM
                for from_entity in from_entity_list:
                
                    # get id
                    from_entity_id = from_entity.id
            
                    # ! --------> CONTEXT_RELATION_TYPE_SLUG_SAME_ARTICLE_SOURCES = "same_article_sources"    # FROM source person TO source person THROUGH article.
                    
                    # config
                    relation_type_slug = ContextTextBase.CONTEXT_RELATION_TYPE_SLUG_SAME_ARTICLE_SOURCES
                    to_entity_list = list( source_entity_list )
                    
                    # remove the current FROM author from the TO list.
                    if ( from_entity in to_entity_list ):
                    
                        # remove it.
                        to_entity_list.remove( from_entity )
                        
                    #-- END check to make sure current FROM is in TO (it better be...) --#
        
                    # validate
                    self.validate_relations( from_IN = from_entity,
                                             to_list_IN = to_entity_list,
                                             through_IN = through_entity,
                                             relation_type_slug_IN = relation_type_slug,
                                             trait_dict_IN = trait_dict )

                #-- END loop over FROM list

            #-- END check to see if FROM list --#

            #------------------------------------------------------------------#
            # ! ----> Entity_Relation_Type slugs - FROM subject
            from_entity_list = subject_entity_list
            through_entity = article_entity

            # got a from list?
            if ( ( from_entity_list is not None ) and ( len( from_entity_list ) > 0 ) ):
            
                # loop over subject entities for FROM
                for from_entity in from_entity_list:
                
                    # get id
                    from_entity_id = from_entity.id
            
                    # ! --------> CONTEXT_RELATION_TYPE_SLUG_SAME_ARTICLE_SUBJECTS = "same_article_subjects"  # FROM subject person TO subject person THROUGH article (includes subjects and sources).
                    
                    # config
                    relation_type_slug = ContextTextBase.CONTEXT_RELATION_TYPE_SLUG_SAME_ARTICLE_SUBJECTS
                    to_entity_list = list( subject_entity_list )
        
                    # remove the current FROM author from the TO list.
                    if ( from_entity in to_entity_list ):
                    
                        # remove it.
                        to_entity_list.remove( from_entity )
                        
                    #-- END check to make sure current FROM is in TO (it better be...) --#
        
                    # validate
                    self.validate_relations( from_IN = from_entity,
                                             to_list_IN = to_entity_list,
                                             through_IN = through_entity,
                                             relation_type_slug_IN = relation_type_slug,
                                             trait_dict_IN = trait_dict )

                #-- END loop over FROM list

            #-- END check to see if FROM list --#

        #-- END check to make sure article ID passed in. --#
            
    #-- END test method validate_article_article_relations() --#


    def validate_article_newspaper_relations( self, article_id_IN ):
        
        '''
        - pick an article
        - create entities and make author, subject, and source lists from it
        - call method.
        - build trait dictionary just like in the method.
        - check relations.
        '''
        
        # declare variables
        me = "validate_article_newspaper_relations"
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
        
        # declare variables - more in-depth testing.
        trait_dict = None
        relation_trait_filter_dict = None
        to_entity_list = None
        relation_type_slug = None

        # debug
        debug_flag = self.DEBUG

        print( '\n\n--------> In {}.{}\n'.format( self.CLASS_NAME, me ) )
        
        # init
        export_instance = ExportToContext()
        
        # article_id_IN should not be None
        error_string = "If you are validating newspaper-related entities for an article, you should pass in that article's ID, not None"
        self.assertIsNotNone( article_id_IN, msg = error_string )

        # make sure we have an article ID.
        if ( article_id_IN is not None ):
        
            article_id = article_id_IN
        
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
            
            # Now, need to do the same work as the method to check the results.
            
            # shared traits for these relations, also used to filter.
            # - includes article's pub_date and sourcenet article ID.
            trait_dict = ExportToContext.make_relation_trait_dict( article_entity_IN = article_entity )
            relation_trait_filter_dict = trait_dict
                        

            #------------------------------------------------------------------#
            # ! ----> "newspaper_article"    # FROM newspaper TO article.
            #------------------------------------------------------------------#
            
            # configure
            relation_type_slug = ContextTextBase.CONTEXT_RELATION_TYPE_SLUG_NEWSPAPER_ARTICLE
            to_entity_list = [ article_entity ]
            
            # validate
            self.validate_relations( from_IN = newspaper_entity,
                                     to_list_IN = to_entity_list,
                                     through_IN = None,
                                     relation_type_slug_IN = relation_type_slug,
                                     trait_dict_IN = trait_dict )

            #------------------------------------------------------------------#
            # ! ----> "newspaper_reporter"  # FROM newspaper TO person (reporter) THROUGH article.
            #------------------------------------------------------------------#

            # configure
            relation_type_slug = ContextTextBase.CONTEXT_RELATION_TYPE_SLUG_NEWSPAPER_REPORTER
            to_entity_list = author_entity_list
            
            # validate
            self.validate_relations( from_IN = newspaper_entity,
                                     to_list_IN = to_entity_list,
                                     through_IN = article_entity,
                                     relation_type_slug_IN = relation_type_slug,
                                     trait_dict_IN = trait_dict )

            #------------------------------------------------------------------#
            # ! ----> "newspaper_subject"    # FROM newspaper TO person (subject, including sources) THROUGH article.
            #------------------------------------------------------------------#

            # configure
            relation_type_slug = ContextTextBase.CONTEXT_RELATION_TYPE_SLUG_NEWSPAPER_SUBJECT
            to_entity_list = subject_entity_list

            # validate
            self.validate_relations( from_IN = newspaper_entity,
                                     to_list_IN = to_entity_list,
                                     through_IN = article_entity,
                                     relation_type_slug_IN = relation_type_slug,
                                     trait_dict_IN = trait_dict )

            #------------------------------------------------------------------#
            # ! ----> "newspaper_source"      # FROM newspaper TO person (source) THROUGH article.
            #------------------------------------------------------------------#

            relation_type_slug = ContextTextBase.CONTEXT_RELATION_TYPE_SLUG_NEWSPAPER_SOURCE
            to_entity_list = source_entity_list

            # validate
            self.validate_relations( from_IN = newspaper_entity,
                                     to_list_IN = to_entity_list,
                                     through_IN = article_entity,
                                     relation_type_slug_IN = relation_type_slug,
                                     trait_dict_IN = trait_dict )
            
        #-- END loop over articles. --#
                        
    #-- END method validate_article_newspaper_relations()


    def validate_author_entity_list( self, article_id_IN ):

        # declare variables
        me = "validate_author_entity_list"
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

        print( '\n\n--------> In {}.{}\n'.format( self.CLASS_NAME, me ) )
        
        # article_id_IN should not be None
        error_string = "If you are validating an article's author entity list, you should pass in that article's ID, not None"
        self.assertIsNotNone( article_id_IN, msg = error_string )

        # make sure we have an article ID.
        if ( article_id_IN is not None ):
        
            # store ID in expected variable
            article_id = article_id_IN
        
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
        
        #-- END check to make sure we have an article ID. --#
                
    #-- END test method validate_author_entity_list() --#


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

        print( '\n\n--------> In {}.{}\n'.format( self.CLASS_NAME, me ) )

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
                
    #-- END method validate_person_entity_list() --#


    def validate_relations( self, 
                            from_IN,
                            to_list_IN,
                            through_IN,
                            relation_type_slug_IN,
                            trait_dict_IN ):
                                         
        # declare variables - more in-depth testing.
        trait_dict = None
        relation_trait_filter_dict = None
        relation_type_slug = None
        relation_type = None
        to_entity_list = None
        relation_qs = None
        test_from = None
        test_to = None
        test_through = None
        test_relation_type = None
        test_traits = None
        to_entity = None
            
        # initialize        
        relation_type_slug = relation_type_slug_IN
        relation_type = Entity_Relation_Type.objects.get( slug = relation_type_slug )
        to_entity_list = to_list_IN
        trait_dict = trait_dict_IN
            
        # first, lookup relations of appropriate type, FROM, THROUGH, with
        #     expected traits.
        test_from = from_IN
        test_to = None
        test_through = through_IN
        test_relation_type = relation_type
        test_traits = trait_dict
        relation_qs = Entity_Relation.lookup_relations( from_IN = test_from,
                                                        to_IN = test_to,
                                                        through_IN = test_through,
                                                        type_IN = test_relation_type,
                                                        match_trait_dict_IN = test_traits )
                                                        
        # should be as many as are in person_entity_list.
        test_value = relation_qs.count()
        should_be = len( to_entity_list )
        error_string = "Retrieving Entity_Relations: FROM: {}, TO: {}, THROUGH: {}, type: {}, traits: {}.  Count: {}, should be {}.".format( test_from, test_to, test_through, test_relation_type, test_traits, test_value, should_be )
        self.assertEqual( test_value, should_be, msg = error_string )
                    
        # then, loop over the TOs, and make sure each has a single
        #     matching relation.
        for current_to_entity in to_entity_list:
        
            # try to find the relation for this author.
            test_from = from_IN
            test_to = current_to_entity
            test_through = through_IN
            test_relation_type = relation_type
            test_traits = trait_dict
            relation_qs = Entity_Relation.lookup_relations( from_IN = test_from,
                                                            to_IN = test_to,
                                                            through_IN = test_through,
                                                            type_IN = test_relation_type,
                                                            match_trait_dict_IN = test_traits )
            
            # should be 1.
            test_value = relation_qs.count()
            should_be = 1
            error_string = "Retrieving Entity_Relations: FROM: {}, TO: {}, THROUGH: {}, type: {}, traits: {}.  Count: {}, should be {}.".format( test_from, test_to, test_through, test_relation_type, test_traits, test_value, should_be )
            self.assertEqual( test_value, should_be, msg = error_string )
                        
        #-- END loop over TO entities --#
        
    #-- END test method validate_newspaper_relation() --#
    

    def validate_subject_entity_list( self, article_id_IN ):

        # declare variables
        me = "validate_subject_entity_list"
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

        print( '\n\n--------> In {}.{}\n'.format( self.CLASS_NAME, me ) )

        # article_id_IN should not be None
        error_string = "If you are validating an article's subject entity lists, you should pass in that article's ID, not None"
        self.assertIsNotNone( article_id_IN, msg = error_string )

        # make sure we have an article ID.
        if ( article_id_IN is not None ):
        
            # store ID in expected variable
            article_id = article_id_IN
        
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

        #-- END check to make sure we have an article ID. --#
                
    #-- END test method validate_subject_entity_list() --#


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
                                                                           
            # ! ----> call the create_article_relations() method.
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
            
            # now, validate the relations that should have resulted from this
            #     call.
            self.validate_article_article_relations( article_id )
            
            # ! ----> call the create_article_relations() method again.
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
            
            # now, validate the relations that should have resulted from this
            #     call.
            self.validate_article_article_relations( article_id )

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
        
        # declare variables - more in-depth testing.
        trait_dict = None
        relation_trait_filter_dict = None
        to_entity_list = None
        relation_type_slug = None

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
                                                                           
            # ! ----> call the create_newspaper_relations() method.
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
            
            # now, validate the relations that should have resulted from this
            #     call.
            self.validate_article_newspaper_relations( article_id )
                        
            # ! ----> call the create_newspaper_relations() method again.
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
            
            # now, validate the relations that should have resulted from this
            #     call.
            self.validate_article_newspaper_relations( article_id )
                        
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


    def test_create_relations( self ):
        
        '''
        - pick an article
        - create entities and make author, subject, and source lists from it
        - call method.
        - build trait dictionary just like in the method.
        - check relations.
        '''
        
        # declare variables
        me = "test_create_relations"
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
        
        # declare variables - more in-depth testing.
        trait_dict = None
        relation_trait_filter_dict = None
        to_entity_list = None
        relation_type_slug = None

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
                                                                           
            # ! ----> call the create_relations() method.
            create_status = export_instance.create_relations( article_data_instance,
                                                              author_entity_list_IN = author_entity_list,
                                                              subject_entity_list_IN = subject_entity_list,
                                                              source_entity_list_IN = source_entity_list )                                                                        

            # success?
            test_value = create_status.is_success()
            should_be = True
            error_string = "Creating newspaper-related relations for newspaper entity: {}, article_entity: {}, authors: {}, subjects: {}, sources: {}, and Article_Data: {}.  Success?: {}, should be {}.".format( newspaper_entity, article_entity, author_entity_list, subject_entity_list, source_entity_list, article_data_instance, test_value, should_be )
            self.assertEqual( test_value, should_be, msg = error_string )
            
            # now, validate the relations that should have resulted from this
            #     call.
            self.validate_article_newspaper_relations( article_id )
            self.validate_article_article_relations( article_id )
                        
            # ! ----> call the create_relations method again - test duplication.
            create_status = export_instance.create_relations( article_data_instance,
                                                              author_entity_list_IN = author_entity_list,
                                                              subject_entity_list_IN = subject_entity_list,
                                                              source_entity_list_IN = source_entity_list )                                                                        

            # success?
            test_value = create_status.is_success()
            should_be = True
            error_string = "Creating newspaper-related relations for newspaper entity: {}, article_entity: {}, authors: {}, subjects: {}, sources: {}, and Article_Data: {}.  Success?: {}, should be {}.".format( newspaper_entity, article_entity, author_entity_list, subject_entity_list, source_entity_list, article_data_instance, test_value, should_be )
            self.assertEqual( test_value, should_be, msg = error_string )
            
            # now, validate the relations that should have resulted from this
            #     call.
            self.validate_article_newspaper_relations( article_id )
            self.validate_article_article_relations( article_id )

        #-- END loop over articles. --#
                        
    #-- END method test_create_relations()


    def test_make_author_entity_list( self ):

        # declare variables
        me = "test_make_author_entity_list"
        debug_flag = None
        error_string = None
        article_id = None

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


    def test_process_articles( self ):
        
        '''
        - pick an article
        - create entities and make author, subject, and source lists from it
        - call method.
        - build trait dictionary just like in the method.
        - check relations.
        '''
        
        # declare variables
        me = "test_process_articles"
        export_instance = None
        debug_flag = None
        error_string = None
        article_qs = None
        article_id = None
        create_status = None
        is_create_success = None
        
        # declare variables - more in-depth testing.
        trait_dict = None
        relation_trait_filter_dict = None
        to_entity_list = None
        relation_type_slug = None

        # debug
        debug_flag = self.DEBUG

        print( '\n\n====> In {}.{}\n'.format( self.CLASS_NAME, me ) )
        
        # init
        export_instance = ExportToContext()
        
        # create an Article QuerySet filtered to just the IDs in
        #     self.TEST_ID_LIST
        article_qs = Article.objects.filter( id__in = self.TEST_ID_LIST )
        
        # ! ----> call the process_articles() method.
        create_status = export_instance.process_articles( article_qs )
        
        # success?
        test_value = create_status.is_success()
        should_be = True
        error_string = "Calling process_articles() for Article QuerySet: {} ( from article ID list {} ).  Success?: {}, should be {}.".format( article_qs, self.TEST_ID_LIST, test_value, should_be )
        self.assertEqual( test_value, should_be, msg = error_string )

        # For each article we processed, validate relations (assuming entities
        #     are right if relations come out right).
        for article_id in self.TEST_ID_LIST:
        
            # validate the relations that should have resulted from this call.
            self.validate_article_newspaper_relations( article_id )
            self.validate_article_article_relations( article_id )
                        
        #-- END loop over articles. --#
                        
        # ! ----> call the process_articles() method again - duplicates?
        create_status = export_instance.process_articles( article_qs )
        
        # success?
        test_value = create_status.is_success()
        should_be = True
        error_string = "Calling process_articles() for Article QuerySet: {} ( from article ID list {} ).  Success?: {}, should be {}.".format( article_qs, self.TEST_ID_LIST, test_value, should_be )
        self.assertEqual( test_value, should_be, msg = error_string )

        # For each article we processed, validate relations (assuming entities
        #     are right if relations come out right).
        for article_id in self.TEST_ID_LIST:
        
            # validate the relations that should have resulted from this call.
            self.validate_article_newspaper_relations( article_id )
            self.validate_article_article_relations( article_id )
                        
        #-- END loop over articles. --#

    #-- END method test_process_articles()


#-- END test class ExportToContextTest --#
