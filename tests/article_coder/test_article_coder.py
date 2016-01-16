"""
This file contains tests of shared code implemented in abstract class
ArticleCoder, using child ManualArticleCoder.

Functions tested:
- process_mention
- process_quotation
- process_subject_name
- process_author_name
"""

# django imports
from django.contrib.auth.models import User
import django.test

# python_utilities imports
from python_utilities.network.http_helper import Http_Helper

# sourcenet imports
from sourcenet.article_coding.article_coding import ArticleCoding
from sourcenet.article_coding.article_coding import ArticleCoder
from sourcenet.article_coding.manual_coding.manual_article_coder import ManualArticleCoder
from sourcenet.article_coding.open_calais_v2.open_calais_v2_api_response import OpenCalaisV2ApiResponse
from sourcenet.article_coding.open_calais_v2.open_calais_v2_article_coder import OpenCalaisV2ArticleCoder
from sourcenet.models import Article
from sourcenet.models import Article_Data
from sourcenet.models import Article_Subject
from sourcenet.tests.test_helper import TestHelper


class ArticleCoderTest( django.test.TestCase ):
    
    #----------------------------------------------------------------------------
    # Constants-ish
    #----------------------------------------------------------------------------


    #----------------------------------------------------------------------------
    # instance methods
    #----------------------------------------------------------------------------


    def setUp( self ):
        
        """
        setup tasks.  Call function that we'll re-use.
        """

        # call TestHelper.standardSetUp()
        TestHelper.standardSetUp( self )

        # create test user
        TestHelper.create_test_user()

    #-- END function setUp() --#
        

    def test_setup( self ):

        """
        Tests whether there were errors in setup.
        """
        
        # declare variables
        error_count = -1
        error_message = ""
        
        # get setup error count
        setup_error_count = self.setup_error_count
        
        # should be 0
        error_message = ";".join( self.setup_error_list )
        self.assertEqual( setup_error_count, 0, msg = error_message )
        
    #-- END test method test_django_config_installed() --#


    def test_process_mention( self ):
        
        # declare variables
        me = "test_process_mention"
        debug_string = ""
        subject_name = ""
        mention_name = ""
        test_manual_article_coder = None
        test_article = None
        test_user = None
        test_article_data = None
        test_article_subject = None
        test_article_subject_mention = None
        test_mention_id = -1
        test_value_index = -1
        test_canonical_index = -1
        test_value_word_number_start = -1
        test_value_word_number_end = -1
        test_paragraph_number = -1
        test_mention_count = -1

        # set subject_name, mention_name
        subject_name = TestHelper.TEST_SUBJECT_1
        mention_name = subject_name

        # create ManualArticleCoder instance.
        test_manual_article_coder = ManualArticleCoder()

        # get an article.
        test_article = Article.objects.get( pk = 21409 )

        # get test user
        test_user = TestHelper.get_test_user()

        # create bare-bones Article_Data
        test_article_data = Article_Data()
        test_article_data.coder = test_user
        test_article_data.article = test_article
        test_article_data.save()

        # create an article_subject.
        test_article_subject = test_manual_article_coder.process_subject_name( test_article_data, subject_name )

        # test creating a new Article_Subject_Mention.
        test_article_subject_mention = test_manual_article_coder.process_mention( test_article, test_article_subject, mention_name )

        # get mention info.
        test_mention_id = test_article_subject_mention.id
        test_value_index = test_article_subject_mention.value_index
        test_canonical_index = test_article_subject_mention.canonical_index
        test_value_word_number_start = test_article_subject_mention.value_word_number_start
        test_value_word_number_end = test_article_subject_mention.value_word_number_end
        test_paragraph_number = test_article_subject_mention.paragraph_number

        debug_string = "\nMention for \"" + mention_name + "\":\nid = " + str( test_mention_id ) + ";\nvalue_index = " + str( test_value_index ) + ";\ncanonical_index = " + str( test_canonical_index ) + ";\nword_number_start = " + str( test_value_word_number_start ) + ";\nword_number_end = " + str( test_value_word_number_end ) + ";\ngraf number = " + str( test_paragraph_number )
        print( debug_string )

        # test values
        self.assertEqual( test_value_index, 451 )
        self.assertEqual( test_canonical_index, 487 )
        self.assertEqual( test_value_word_number_start, 78 )
        self.assertEqual( test_value_word_number_end, 79 )
        self.assertEqual( test_paragraph_number, 3 )

        # get count of mentions.  Should be 1.
        test_mention_count = test_article_subject.article_subject_mention_set.all().count()
        self.assertEqual( test_mention_count, 1 )

        debug_string = "\nMention count: " + str( test_mention_count )
        print( debug_string )
        
        # try adding the same mention again.
        test_article_subject_mention = test_manual_article_coder.process_mention( test_article, test_article_subject, mention_name )

        # ID should be same as before.
        self.assertEqual( test_article_subject_mention.id, test_mention_id )

        # count should be 1.
        test_mention_count = test_article_subject.article_subject_mention_set.all().count()
        self.assertEqual( test_mention_count, 1 )

        debug_string = "\nMention count: " + str( test_mention_count )
        print( debug_string )
        
        # add 2nd mention.
        mention_name = "The Rockford friends"
        test_article_subject_mention = test_manual_article_coder.process_mention( test_article, test_article_subject, mention_name )

        # get mention info.
        test_mention_id = test_article_subject_mention.id
        test_value_index = test_article_subject_mention.value_index
        test_canonical_index = test_article_subject_mention.canonical_index
        test_value_word_number_start = test_article_subject_mention.value_word_number_start
        test_value_word_number_end = test_article_subject_mention.value_word_number_end
        test_paragraph_number = test_article_subject_mention.paragraph_number

        debug_string = "\nMention for \"" + mention_name + "\":\nid = " + str( test_mention_id ) + ";\nvalue_index = " + str( test_value_index ) + ";\ncanonical_index = " + str( test_canonical_index ) + ";\nword_number_start = " + str( test_value_word_number_start ) + ";\nword_number_end = " + str( test_value_word_number_end ) + ";\ngraf number = " + str( test_paragraph_number )
        print( debug_string )

        # test values
        self.assertEqual( test_value_index, 489 )
        self.assertEqual( test_canonical_index, 538 )
        self.assertEqual( test_value_word_number_start, 82 )
        self.assertEqual( test_value_word_number_end, 84 )
        self.assertEqual( test_paragraph_number, 4 )

        # get count of mentions.  Should be 2.
        test_mention_count = test_article_subject.article_subject_mention_set.all().count()
        self.assertEqual( test_mention_count, 2 )

        debug_string = "\nMention count: " + str( test_mention_count )
        print( debug_string )
        
    #-- END test method test_process_mention() --#


    def test_process_quotation( self ):
        
        # declare variables
        me = "test_process_quotation"
        debug_string = ""
        subject_name = ""
        quotation_string = ""
        test_manual_article_coder = None
        test_article = None
        test_user = None
        test_article_data = None
        test_article_subject = None
        test_article_subject_quotation = None
        test_quotation_id = -1
        test_value_index = -1
        test_canonical_index = -1
        test_value_word_number_start = -1
        test_value_word_number_end = -1
        test_paragraph_number = -1
        test_quotation_count = -1

        # set subject_name and quotation_string
        subject_name = TestHelper.TEST_SUBJECT_1
        quotation_string = TestHelper.TEST_QUOTATION_1

        # create ManualArticleCoder instance.
        test_manual_article_coder = ManualArticleCoder()

        # get an article.
        test_article = Article.objects.get( pk = 21409 )

        # get test user
        test_user = TestHelper.get_test_user()

        # create bare-bones Article_Data
        test_article_data = Article_Data()
        test_article_data.coder = test_user
        test_article_data.article = test_article
        test_article_data.save()

        # create an article_subject.
        test_article_subject = test_manual_article_coder.process_subject_name( test_article_data, subject_name )

        # test creating a new Article_Subject_Mention.
        test_article_subject_quotation = test_manual_article_coder.process_quotation( test_article, test_article_subject, quotation_string )

        # get quotation info.
        test_quotation_id = test_article_subject_quotation.id
        test_value_index = test_article_subject_quotation.value_index
        test_canonical_index = test_article_subject_quotation.canonical_index
        test_value_word_number_start = test_article_subject_quotation.value_word_number_start
        test_value_word_number_end = test_article_subject_quotation.value_word_number_end
        test_paragraph_number = test_article_subject_quotation.paragraph_number

        debug_string = "\nQuotation for \"" + quotation_string + "\":\nid = " + str( test_quotation_id ) + ";\nvalue_index = " + str( test_value_index ) + ";\ncanonical_index = " + str( test_canonical_index ) + ";\nword_number_start = " + str( test_value_word_number_start ) + ";\nword_number_end = " + str( test_value_word_number_end ) + ";\ngraf number = " + str( test_paragraph_number )
        print( debug_string )

        # test values
        self.assertEqual( test_value_index, 391 )
        self.assertEqual( test_canonical_index, 427 )
        self.assertEqual( test_value_word_number_start, 69 )
        self.assertEqual( test_value_word_number_end, 82 )
        self.assertEqual( test_paragraph_number, 3 )

        # get count of quotes.  Should be 1.
        test_quotation_count = test_article_subject.article_subject_quotation_set.all().count()
        self.assertEqual( test_quotation_count, 1 )

        debug_string = "\nRecord count: " + str( test_quotation_count )
        print( debug_string )
        
        # try adding the same quote again.
        test_article_subject_quotation = test_manual_article_coder.process_quotation( test_article, test_article_subject, quotation_string )

        # ID should be same as before.
        self.assertEqual( test_article_subject_quotation.id, test_quotation_id )

        # count should be 1.
        test_quotation_count = test_article_subject.article_subject_quotation_set.all().count()
        self.assertEqual( test_quotation_count, 1 )

        debug_string = "\nRecord count: " + str( test_quotation_count )
        print( debug_string )
        
        # add 2nd quote.
        quotation_string = TestHelper.TEST_QUOTATION_2
        test_article_subject_quotation = test_manual_article_coder.process_quotation( test_article, test_article_subject, quotation_string )

        # get quote info.
        test_quotation_id = test_article_subject_quotation.id
        test_value_index = test_article_subject_quotation.value_index
        test_canonical_index = test_article_subject_quotation.canonical_index
        test_value_word_number_start = test_article_subject_quotation.value_word_number_start
        test_value_word_number_end = test_article_subject_quotation.value_word_number_end
        test_paragraph_number = test_article_subject_quotation.paragraph_number

        debug_string = "\nQuotation for \"" + quotation_string + "\":\nid = " + str( test_quotation_id ) + ";\nvalue_index = " + str( test_value_index ) + ";\ncanonical_index = " + str( test_canonical_index ) + ";\nword_number_start = " + str( test_value_word_number_start ) + ";\nword_number_end = " + str( test_value_word_number_end ) + ";\ngraf number = " + str( test_paragraph_number )
        print( debug_string )

        # test values
        self.assertEqual( test_value_index, 489 )
        self.assertEqual( test_canonical_index, 538 )
        self.assertEqual( test_value_word_number_start, 83 )
        self.assertEqual( test_value_word_number_end, 112 )
        self.assertEqual( test_paragraph_number, 4 )

        # get count of quotes.  Should be 2.
        test_quotation_count = test_article_subject.article_subject_quotation_set.all().count()
        self.assertEqual( test_quotation_count, 2 )

        debug_string = "\nRecord count: " + str( test_quotation_count )
        print( debug_string )
        
    #-- END test method test_process_quotation() --#


#-- END test class ArticleCoderTest --#
