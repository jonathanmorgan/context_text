"""
This file contains tests of shared code implemented in abstract class
ArticleCoder, using child ManualArticleCoder.

Functions tested:
- lookup_person
- process_mention
- process_quotation
- process_subject_name
- process_author_name

More info:
- https://docs.djangoproject.com/en/stable/topics/testing/
- https://docs.djangoproject.com/en/stable/topics/testing/overview/
- https://docs.djangoproject.com/en/stable/topics/testing/tools/
- https://docs.djangoproject.com/en/stable/topics/testing/advanced/
- https://docs.python.org/2.7/library/unittest.html
- https://docs.python.org/3.3/library/unittest.html
- https://docs.djangoproject.com/en/stable/intro/tutorial05/
"""

# django imports
from django.contrib.auth.models import User
import django.test

# python_utilities imports
from python_utilities.logging.logging_helper import LoggingHelper
from python_utilities.network.http_helper import Http_Helper

# sourcenet imports
from sourcenet.article_coding.article_coding import ArticleCoding
from sourcenet.article_coding.article_coding import ArticleCoder
from sourcenet.article_coding.manual_coding.manual_article_coder import ManualArticleCoder
from sourcenet.article_coding.open_calais_v2.open_calais_v2_api_response import OpenCalaisV2ApiResponse
from sourcenet.article_coding.open_calais_v2.open_calais_v2_article_coder import OpenCalaisV2ArticleCoder
from sourcenet.models import Article
from sourcenet.models import Article_Author
from sourcenet.models import Article_Data
from sourcenet.models import Article_Subject
from sourcenet.shared.person_details import PersonDetails
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
        

    def test_all_setup( self ):

        """
        Tests whether there were errors in setup.
        """
        
        # declare variables
        me = "test_all_setup"
        error_count = -1
        error_message = ""
        
        print( "\n\n==> Top of " + me + "\n" )

        # get setup error count
        setup_error_count = self.setup_error_count
        
        # should be 0
        error_message = ";".join( self.setup_error_list )
        self.assertEqual( setup_error_count, 0, msg = error_message )
        
    #-- END test method test_django_config_installed() --#


    def test_lookup_person( self ):
        
        # declare variables
        me = "test_lookup_person"
        test_manual_article_coder = None
        error_message = ""
        lookup_person_id = -1
        lookup_person_name = ""
        lookup_title = ""
        lookup_organization_string = ""
        test_person_details = None
        test_article_author = None
        test_article_subject = None
        test_person = None
        test_person_id = -1
        test_person_title = ""

        print( "\n\n==> Top of " + me + "\n" )
        
        # create ManualArticleCoder instance.
        test_manual_article_coder = ManualArticleCoder()

        #----------------------------------------------------------------------#
        # !test 1 - 149 - Coy Lynn Robinson - with person ID.       
        #----------------------------------------------------------------------#

        # test 1 person values
        lookup_person_id = 149
        lookup_person_name = "Coy Lynn Robinson"
        lookup_title = "Hancock Preparatory School principal, DPS"
        
        # set up person details
        test_person_details = PersonDetails()
        test_person_details[ ArticleCoder.PARAM_PERSON_NAME ] = lookup_person_name
        test_person_details[ ArticleCoder.PARAM_PERSON_ID ] = lookup_person_id
        test_person_details[ ArticleCoder.PARAM_TITLE ] = lookup_title
                
        # make test Article_Author
        test_article_author = Article_Author()

        # lookup person - returns person and confidence score inside
        #    Article_Author instance.
        test_article_author = test_manual_article_coder.lookup_person( test_article_author, 
                                                                       lookup_person_name,
                                                                       create_if_no_match_IN = True,
                                                                       update_person_IN = True,
                                                                       person_details_IN = test_person_details )

        # get results from Article_Author
        test_person = test_article_author.person
        test_person_match_list = test_article_author.person_match_list  # list of Person instances
                                
        # got a person?
        error_message = "In " + me + "(): No person returned for name \"" + lookup_person_name + "\", id = " + str( lookup_person_id )
        self.assertIsNotNone( test_person, msg = error_message )
        
        # retrieve the person and person ID
        test_person = test_article_author.person
        test_person_id = test_person.id
        test_person_title = test_person.title
        
        # check to make sure it is the right person.
        test_value = test_person_id
        should_be = lookup_person_id
        error_message = "In " + me + ": Person " + str( test_person ) + " has ID " + str( test_value ) + ", should be " + str( should_be ) + "."
        self.assertEqual( test_value, should_be, msg = error_message )
        
        # check to see if person title updated.
        test_value = test_person_title
        should_be = lookup_title
        error_message = "In " + me + ": Person " + str( test_person ) + " has title " + str( test_value ) + ", should be " + str( should_be ) + "."
        self.assertEqual( test_value, should_be, msg = error_message )
        
        
        #----------------------------------------------------------------------#
        # !test 2 - 1031 - Karen Irene Schwarck - use name.       
        #----------------------------------------------------------------------#

        
        # retrieve person information.
        lookup_person_name = "Karen Irene Schwarck"
        lookup_person_id = 1031
        lookup_title = "test_title"
        lookup_organization_string = "test_org"

        # set up person details
        person_details = PersonDetails()
        person_details[ ManualArticleCoder.PARAM_PERSON_NAME ] = lookup_person_name
        person_details[ ManualArticleCoder.PARAM_TITLE ] = lookup_title
        person_details[ ManualArticleCoder.PARAM_PERSON_ORGANIZATION ] = lookup_organization_string
        #person_details[ ManualArticleCoder.PARAM_PERSON_ID ] = lookup_person_id
        
        # make test Article_Author
        test_article_author = Article_Author()

        # lookup person - returns person and confidence score inside
        #    Article_Author instance.
        test_article_author = test_manual_article_coder.lookup_person( test_article_author, 
                                                                       lookup_person_name,
                                                                       create_if_no_match_IN = True,
                                                                       update_person_IN = True,
                                                                       person_details_IN = person_details )

        # get results from Article_Author
        test_person = test_article_author.person
        test_person_match_list = test_article_author.person_match_list  # list of Person instances
                                
        # got a person?
        error_message = "In " + me + "(): No person returned for name \"" + lookup_person_name + "\", id = " + str( lookup_person_id )
        self.assertIsNotNone( test_person, msg = error_message )
        
        # retrieve the person and person ID
        test_person_id = test_person.id
        test_person_title = test_person.title
        test_person_organization = test_person.organization_string
        
        # check to make sure it is the right person.
        test_value = test_person_id
        should_be = lookup_person_id
        error_message = "In " + me + ": Person " + str( test_person ) + " has ID " + str( test_value ) + ", should be " + str( should_be ) + "."
        self.assertEqual( test_value, should_be, msg = error_message )
        
        # check to see if person title updated.
        test_value = test_person_title
        should_be = lookup_title
        error_message = "In " + me + ": Person " + str( test_person ) + " has title " + str( test_value ) + ", should be " + str( should_be ) + "."
        self.assertEqual( test_value, should_be, msg = error_message )

        # check to see if organization_string updated.
        test_value = test_person_organization
        should_be = lookup_organization_string
        error_message = "In " + me + ": Person " + str( test_person ) + " has organization " + str( test_value ) + ", should be " + str( should_be ) + "."
        self.assertEqual( test_value, should_be, msg = error_message )

        #----------------------------------------------------------------------#
        # !test 3 - No match, don't create.       
        #----------------------------------------------------------------------#

        
        # retrieve person information.
        lookup_person_name = "Irving Beatrix Berlin"
        lookup_person_id = -1
        lookup_title = "test_title"
        lookup_organization_string = "test_org"

        # set up person details
        person_details = PersonDetails()
        person_details[ ManualArticleCoder.PARAM_PERSON_NAME ] = lookup_person_name
        person_details[ ManualArticleCoder.PARAM_TITLE ] = lookup_title
        person_details[ ManualArticleCoder.PARAM_PERSON_ORGANIZATION ] = lookup_organization_string
        #person_details[ ManualArticleCoder.PARAM_PERSON_ID ] = lookup_person_id
        
        # make test Article_Author
        test_article_author = Article_Author()

        # lookup person - returns person and confidence score inside
        #    Article_Author instance.
        test_article_author = test_manual_article_coder.lookup_person( test_article_author, 
                                                                       lookup_person_name,
                                                                       create_if_no_match_IN = False,
                                                                       update_person_IN = True,
                                                                       person_details_IN = person_details )

        # get results from Article_Author
        test_person = test_article_author.person
        test_person_match_list = test_article_author.person_match_list  # list of Person instances
                                
        # got a person?
        error_message = "In " + me + "(): Person returned for name \"" + lookup_person_name + "\" when I asked for none to be created: " + str( test_person )
        self.assertIsNone( test_person, msg = error_message )
        
        # try lookup again, just to make sure it didn't create.
        test_article_author = Article_Author()
        test_article_author = test_manual_article_coder.lookup_person( test_article_author, 
                                                                       lookup_person_name,
                                                                       create_if_no_match_IN = False,
                                                                       update_person_IN = True,
                                                                       person_details_IN = person_details )

        # get results from Article_Author
        test_person = test_article_author.person
        test_person_match_list = test_article_author.person_match_list  # list of Person instances
                                
        # got a person?
        error_message = "In " + me + "(): Person returned for name \"" + lookup_person_name + "\" when I asked for none to be created: " + str( test_person )
        self.assertIsNone( test_person, msg = error_message )

        
        #----------------------------------------------------------------------#
        # !test 4 - No match, do create.       
        #----------------------------------------------------------------------#

        
        # retrieve person information.
        lookup_person_name = "Irving Beatrix Berlin"
        lookup_person_id = -1
        lookup_title = "test_title"
        lookup_organization_string = "test_org"

        # set up person details
        person_details = PersonDetails()
        person_details[ ManualArticleCoder.PARAM_PERSON_NAME ] = lookup_person_name
        person_details[ ManualArticleCoder.PARAM_TITLE ] = lookup_title
        person_details[ ManualArticleCoder.PARAM_PERSON_ORGANIZATION ] = lookup_organization_string
        #person_details[ ManualArticleCoder.PARAM_PERSON_ID ] = lookup_person_id
        
        # make test Article_Author
        test_article_author = Article_Author()

        # lookup person - returns person and confidence score inside
        #    Article_Author instance.
        test_article_author = test_manual_article_coder.lookup_person( test_article_author, 
                                                                       lookup_person_name,
                                                                       create_if_no_match_IN = True,
                                                                       update_person_IN = True,
                                                                       person_details_IN = person_details )

        # get results from Article_Author
        test_person = test_article_author.person
        test_person_match_list = test_article_author.person_match_list  # list of Person instances
                                
        # got a person?
        error_message = "In " + me + "(): No person returned for name \"" + lookup_person_name + "\", id = " + str( lookup_person_id )
        self.assertIsNotNone( test_person, msg = error_message )
        
        # retrieve the person and person ID
        test_person_id = test_person.id
        test_person_title = test_person.title
        test_person_organization = test_person.organization_string
        
        # there should be an ID.
        test_value = test_person_id
        error_message = "In " + me + ": Person " + str( test_person ) + " has ID " + str( test_value ) + ", should be None."
        self.assertIsNotNone( test_value, msg = error_message )
        
        # check to see if person title updated.
        test_value = test_person_title
        should_be = lookup_title
        error_message = "In " + me + ": Person " + str( test_person ) + " has title " + str( test_value ) + ", should be " + str( should_be ) + "."
        self.assertEqual( test_value, should_be, msg = error_message )

        # check to see if organization_string updated.
        test_value = test_person_organization
        should_be = lookup_organization_string
        error_message = "In " + me + ": Person " + str( test_person ) + " has organization " + str( test_value ) + ", should be " + str( should_be ) + "."
        self.assertEqual( test_value, should_be, msg = error_message )


        #----------------------------------------------------------------------#
        # !test 5 - Single name, single match test - should not match.
        # - "Anirban" matches one person with that first name ( 526 - "Anirban Basu" )
        # - should not be counted as a match.
        # - No match, do create.
        #----------------------------------------------------------------------#

        
        # retrieve person information.
        lookup_person_name = "Anirban"
        lookup_person_id = -1
        lookup_title = "test_title"
        lookup_organization_string = "test_org"

        # set up person details
        person_details = PersonDetails()
        person_details[ ManualArticleCoder.PARAM_PERSON_NAME ] = lookup_person_name
        person_details[ ManualArticleCoder.PARAM_TITLE ] = lookup_title
        person_details[ ManualArticleCoder.PARAM_PERSON_ORGANIZATION ] = lookup_organization_string
        #person_details[ ManualArticleCoder.PARAM_PERSON_ID ] = lookup_person_id
        
        # make test Article_Author
        test_article_author = Article_Author()

        # lookup person - returns person and confidence score inside
        #    Article_Author instance.
        test_article_author = test_manual_article_coder.lookup_person( test_article_author, 
                                                                       lookup_person_name,
                                                                       create_if_no_match_IN = True,
                                                                       update_person_IN = True,
                                                                       person_details_IN = person_details )

        # get results from Article_Author
        test_person = test_article_author.person
        test_person_match_list = test_article_author.person_match_list  # list of Person instances
                                
        # got a person?
        error_message = "In " + me + "(): No person returned for name \"" + lookup_person_name + "\", id = " + str( lookup_person_id )
        self.assertIsNotNone( test_person, msg = error_message )
        
        # retrieve the person and person ID
        test_person_id = test_person.id
        test_person_title = test_person.title
        test_person_organization = test_person.organization_string
        
        # there should be an ID.
        test_value = test_person_id
        error_message = "In " + me + ": Person " + str( test_person ) + " has ID " + str( test_value ) + ", should be None."
        self.assertIsNotNone( test_value, msg = error_message )
        
        # ID should not be 526.
        test_value = test_person_id
        should_not_be = 526
        error_message = "In " + me + ": Person " + str( test_person ) + " has ID " + str( test_value ) + ", should not be " + str( should_not_be ) + "."
        self.assertNotEqual( test_value, should_not_be, msg = error_message )
        
        # check to see if person title updated.
        test_value = test_person_title
        should_be = lookup_title
        error_message = "In " + me + ": Person " + str( test_person ) + " has title " + str( test_value ) + ", should be " + str( should_be ) + "."
        self.assertEqual( test_value, should_be, msg = error_message )

        # check to see if organization_string updated.
        test_value = test_person_organization
        should_be = lookup_organization_string
        error_message = "In " + me + ": Person " + str( test_person ) + " has organization " + str( test_value ) + ", should be " + str( should_be ) + "."
        self.assertEqual( test_value, should_be, msg = error_message )


        #----------------------------------------------------------------------#
        # !test 6 - 526 - Anirban Basu - use name.       
        #----------------------------------------------------------------------#

        
        # retrieve person information.
        lookup_person_name = "Anirban Basu"
        lookup_person_id = 526
        lookup_title = "test_title"
        lookup_organization_string = "test_org"

        # set up person details
        person_details = PersonDetails()
        person_details[ ManualArticleCoder.PARAM_PERSON_NAME ] = lookup_person_name
        person_details[ ManualArticleCoder.PARAM_TITLE ] = lookup_title
        person_details[ ManualArticleCoder.PARAM_PERSON_ORGANIZATION ] = lookup_organization_string
        #person_details[ ManualArticleCoder.PARAM_PERSON_ID ] = lookup_person_id
        
        # make test Article_Author
        test_article_author = Article_Author()

        # lookup person - returns person and confidence score inside
        #    Article_Author instance.
        test_article_author = test_manual_article_coder.lookup_person( test_article_author, 
                                                                       lookup_person_name,
                                                                       create_if_no_match_IN = True,
                                                                       update_person_IN = True,
                                                                       person_details_IN = person_details )

        # get results from Article_Author
        test_person = test_article_author.person
        test_person_match_list = test_article_author.person_match_list  # list of Person instances
                                
        # got a person?
        error_message = "In " + me + "(): No person returned for name \"" + lookup_person_name + "\", id = " + str( lookup_person_id )
        self.assertIsNotNone( test_person, msg = error_message )
        
        # retrieve the person and person ID
        test_person_id = test_person.id
        test_person_title = test_person.title
        test_person_organization = test_person.organization_string
        
        # check to make sure it is the right person.
        test_value = test_person_id
        should_be = lookup_person_id
        error_message = "In " + me + ": Person " + str( test_person ) + " has ID " + str( test_value ) + ", should be " + str( should_be ) + "."
        self.assertEqual( test_value, should_be, msg = error_message )
        
        # check to see if person title updated.
        test_value = test_person_title
        should_be = lookup_title
        error_message = "In " + me + ": Person " + str( test_person ) + " has title " + str( test_value ) + ", should be " + str( should_be ) + "."
        self.assertEqual( test_value, should_be, msg = error_message )

        # check to see if organization_string updated.
        test_value = test_person_organization
        should_be = lookup_organization_string
        error_message = "In " + me + ": Person " + str( test_person ) + " has organization " + str( test_value ) + ", should be " + str( should_be ) + "."
        self.assertEqual( test_value, should_be, msg = error_message )

    #-- END test method test_lookup_person() --#

    
    def test_parse_author_string( self ):
    
        # declare variables
        me = "test_parse_author_string"
        my_logger_name = ""
        my_logger = None
        debug_string = ""
        error_message = ""
        test_author_string = ""
        test_author_info = None
        test_author_name_string = ""
        test_author_name_list = []
        test_author_affiliation = ""
        test_author_status = ""
        
        print( "\n\n==> Top of " + me + "\n" )
        my_logger_name = "TestArticleCoder." + me
        my_logger = LoggingHelper.get_a_logger( my_logger_name )

        #======================================================================#
        # ! "By Jonathan Morgan / The Detroit News"
        #======================================================================#

        test_author_string = "By Jonathan Morgan / The Detroit News"
        test_author_info = ArticleCoder.parse_author_string( test_author_string )
        test_author_name_string = test_author_info[ ArticleCoder.AUTHOR_INFO_AUTHOR_NAME_STRING ]
        test_author_name_list = test_author_info[ ArticleCoder.AUTHOR_INFO_AUTHOR_NAME_LIST ]
        test_author_affiliation = test_author_info[ ArticleCoder.AUTHOR_INFO_AUTHOR_AFFILIATION ]
        test_author_status = test_author_info[ ArticleCoder.AUTHOR_INFO_STATUS ]

        # assertions:
        
        # name string should be "Jonathan Morgan"
        test_value = test_author_name_string
        should_be = "Jonathan Morgan"
        error_message = "In " + me + ": name string should contain \"" + should_be + "\", has instead \"" + test_value + "\"."
        self.assertEqual( test_value, should_be, msg = error_message )
        
        # name list should have 1 entry.
        test_value = len( test_author_name_list )
        should_be = 1
        error_message = "In " + me + ": name list should have len() \"" + str( should_be ) + "\", has instead \"" + str( test_value ) + "\"."
        self.assertEqual( test_value, should_be, msg = error_message )
        
        # name list should just contain "Jonathan Morgan"
        test_value = " || ".join( test_author_name_list )
        should_be = "Jonathan Morgan"
        error_message = "In " + me + ": name list should contain \"" + str( should_be ) + "\", has instead \"" + str( test_value ) + "\"."
        self.assertEqual( test_value, should_be, msg = error_message )
        
        # affiliation should be "The Detroit News"
        test_value = test_author_affiliation
        should_be = "The Detroit News"
        error_message = "In " + me + ": affiliation should contain \"" + str( should_be ) + "\", has instead \"" + str( test_value ) + "\"."
        self.assertEqual( test_value, should_be, msg = error_message )
        
        #======================================================================#
        # ! "by  Jonathan Morgan  and Andrew Mellon / The Detroit News"
        #======================================================================#

        test_author_string = "by  Jonathan Morgan  and Andrew Mellon / The Detroit News"
        test_author_info = ArticleCoder.parse_author_string( test_author_string )
        test_author_name_string = test_author_info[ ArticleCoder.AUTHOR_INFO_AUTHOR_NAME_STRING ]
        test_author_name_list = test_author_info[ ArticleCoder.AUTHOR_INFO_AUTHOR_NAME_LIST ]
        test_author_affiliation = test_author_info[ ArticleCoder.AUTHOR_INFO_AUTHOR_AFFILIATION ]
        test_author_status = test_author_info[ ArticleCoder.AUTHOR_INFO_STATUS ]
        
        # assertions:
        
        # name string should be "Jonathan Morgan and Andrew Mellon"
        test_value = test_author_name_string
        should_be = "Jonathan Morgan and Andrew Mellon"
        error_message = "In " + me + ": name string should contain \"" + should_be + "\", has instead \"" + test_value + "\"."
        self.assertEqual( test_value, should_be, msg = error_message )
        
        # name list should have 2 entries.
        test_value = len( test_author_name_list )
        should_be = 2
        error_message = "In " + me + ": name list should have len() \"" + str( should_be ) + "\", has instead \"" + str( test_value ) + "\"."
        self.assertEqual( test_value, should_be, msg = error_message )
        
        # name list should contain "Jonathan Morgan || Andrew Mellon"
        test_value = " || ".join( test_author_name_list )
        should_be = "Jonathan Morgan || Andrew Mellon"
        error_message = "In " + me + ": name list should contain \"" + str( should_be ) + "\", has instead \"" + str( test_value ) + "\"."
        self.assertEqual( test_value, should_be, msg = error_message )
        
        # affiliation should be "The Detroit News"
        test_value = test_author_affiliation
        should_be = "The Detroit News"
        error_message = "In " + me + ": affiliation should contain \"" + str( should_be ) + "\", has instead \"" + str( test_value ) + "\"."
        self.assertEqual( test_value, should_be, msg = error_message )
        
        #======================================================================#
        # ! " bY Jonathan Morgan, Richard Henninger, and Andrew Mellon / The Detroit News"
        #======================================================================#

        test_author_string = " bY Jonathan Morgan, Richard Henninger, and Andrew Mellon / The Detroit News"
        test_author_info = ArticleCoder.parse_author_string( test_author_string )
        test_author_name_string = test_author_info[ ArticleCoder.AUTHOR_INFO_AUTHOR_NAME_STRING ]
        test_author_name_list = test_author_info[ ArticleCoder.AUTHOR_INFO_AUTHOR_NAME_LIST ]
        test_author_affiliation = test_author_info[ ArticleCoder.AUTHOR_INFO_AUTHOR_AFFILIATION ]
        test_author_status = test_author_info[ ArticleCoder.AUTHOR_INFO_STATUS ]

        # assertions:
        
        # name string should be "Jonathan Morgan, Richard Henninger, and Andrew Mellon"
        test_value = test_author_name_string
        should_be = "Jonathan Morgan, Richard Henninger, and Andrew Mellon"
        error_message = "In " + me + ": name string should contain \"" + should_be + "\", has instead \"" + test_value + "\"."
        self.assertEqual( test_value, should_be, msg = error_message )
        
        # name list should have 3 entries.
        test_value = len( test_author_name_list )
        should_be = 3
        error_message = "In " + me + ": name list should have len() \"" + str( should_be ) + "\", has instead \"" + str( test_value ) + "\"."
        self.assertEqual( test_value, should_be, msg = error_message )
        
        # name list should contain "Jonathan Morgan || Richard Henninger || Andrew Mellon"
        test_value = " || ".join( test_author_name_list )
        should_be = "Jonathan Morgan || Richard Henninger || Andrew Mellon"
        error_message = "In " + me + ": name list should contain \"" + str( should_be ) + "\", has instead \"" + str( test_value ) + "\"."
        self.assertEqual( test_value, should_be, msg = error_message )
        
        # affiliation should be "The Detroit News"
        test_value = test_author_affiliation
        should_be = "The Detroit News"
        error_message = "In " + me + ": affiliation should contain \"" + str( should_be ) + "\", has instead \"" + str( test_value ) + "\"."
        self.assertEqual( test_value, should_be, msg = error_message )
        
    #-- END test method test_parse_author_name() --#
    
        
    def test_process_author_name( self ):
        
        # declare variables
        me = "test_process_author_name"
        my_logger_name = ""
        debug_string = ""
        error_message = ""
        test_manual_article_coder = None
        test_article = None
        test_user = None
        test_article_data = None
        person_name = ""
        title = ""
        lookup_organization_string = ""
        person_id = -1
        person_details = None
        test_article_author = None
        test_person = None
        test_person_id = -1
        test_person_title = ""
        test_article_author_id = -1
        test_article_author_org_string = ""
        test_1_article_author_id = -1
        test_article_author_count = -1
        test_1_article_author_count = -1
        
        print( "\n\n==> Top of " + me + "\n" )
        my_logger_name = "TestArticleCoder." + me

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

        #----------------------------------------------------------------------#
        # !test 1 - with person ID.       
        #----------------------------------------------------------------------#

        # retrieve person information.
        person_name = "Karen Irene Schwarck"
        title = "test_title-1"
        lookup_organization_string = "test_org-1"
        person_id = 1031

        # set up person details
        person_details = PersonDetails()
        person_details[ ManualArticleCoder.PARAM_PERSON_NAME ] = person_name
        person_details[ ManualArticleCoder.PARAM_NEWSPAPER_INSTANCE ] = test_article.newspaper
        person_details[ ManualArticleCoder.PARAM_TITLE ] = title
        person_details[ ManualArticleCoder.PARAM_PERSON_ORGANIZATION ] = lookup_organization_string
        person_details[ ManualArticleCoder.PARAM_PERSON_ID ] = person_id

        # create an Article_Author.
        test_article_author = test_manual_article_coder.process_author_name( test_article_data, person_name, person_details_IN = person_details )
        
        # check to make sure not None
        error_message = "In " + me + ": attempt to get Article_Author for person ID " + str( person_id ) + " failed - got None back."
        self.assertIsNotNone( test_article_author, msg = error_message )
        
        # ==> Person fields

        # retrieve the person and person ID
        test_person = test_article_author.person
        test_person_id = test_person.id
        test_person_title = test_person.title
        
        # check to make sure it is the right person.
        test_value = test_person_id
        should_be = person_id
        error_message = "In " + me + ": Person " + str( test_person ) + " has ID " + str( test_value ) + ", should be " + str( should_be ) + "."
        self.assertEqual( test_value, should_be, msg = error_message )
        
        # check to see if person title updated.
        test_value = test_person_title
        should_be = title
        error_message = "In " + me + ": Person " + str( test_person ) + " has title " + str( test_value ) + ", should be " + str( should_be ) + "."
        self.assertEqual( test_value, should_be, msg = error_message )
        
        # ==> Article_Author fields

        # check to see if author organization_string updated.
        test_article_author_org_string = test_article_author.organization_string
        test_value = test_article_author_org_string
        should_be = lookup_organization_string
        error_message = "In " + me + ": Article_Author " + str( test_article_author.id ) + " has org. string " + str( test_value ) + ", should be " + str( should_be ) + "."
        self.assertEqual( test_value, should_be, msg = error_message )
        
        # capture test Article_Author ID, count of Article_Authors for next
        #    test.
        test_1_article_author_id = test_article_author.id
        test_1_article_author_count = test_article_data.article_author_set.count()
        

        #----------------------------------------------------------------------#
        # !test 2 - change title, use name to lookup, don't pass ID.
        #----------------------------------------------------------------------#

        # retrieve person information.
        person_name = "Karen Irene Schwarck"
        title = "test_title-2"
        lookup_organization_string = "test_org-2"
        person_id = 1031

        # set up person details
        person_details = PersonDetails()
        person_details[ ManualArticleCoder.PARAM_PERSON_NAME ] = person_name
        person_details[ ManualArticleCoder.PARAM_NEWSPAPER_INSTANCE ] = test_article.newspaper
        person_details[ ManualArticleCoder.PARAM_TITLE ] = title
        person_details[ ManualArticleCoder.PARAM_PERSON_ORGANIZATION ] = lookup_organization_string

        # create an article_author.
        test_article_author = test_manual_article_coder.process_author_name( test_article_data, person_name, person_details_IN = person_details )
        
        # check to make sure not None
        error_message = "In " + me + ": attempt to get Article_Author for name " + person_name + " failed - got None back."
        self.assertIsNotNone( test_article_author, msg = error_message )
        
        # ==> Person fields

        # retrieve the person and person ID
        test_person = test_article_author.person
        test_person_id = test_person.id
        test_person_title = test_person.title
        
        # check to make sure it is the right person.
        test_value = test_person_id
        should_be = person_id
        error_message = "In " + me + ": Person " + str( test_person ) + " has ID " + str( test_value ) + ", should be " + str( should_be ) + "."
        self.assertEqual( test_value, should_be, msg = error_message )
        
        # check to see if person title updated.
        test_value = test_person_title
        should_be = title
        error_message = "In " + me + ": Person " + str( test_person ) + " has title " + str( test_value ) + ", should be " + str( should_be ) + "."
        self.assertEqual( test_value, should_be, msg = error_message )
        
        # ==> Article_Author fields
        
        # same Article_Author ID as before?
        test_article_author_id = test_article_author.id
        test_value = test_article_author_id
        should_be = test_1_article_author_id
        error_message = "In " + me + ": Article_Author has ID " + str( test_value ) + ", should be " + str( should_be ) + "."
        self.assertEqual( test_value, should_be, msg = error_message )
        
        # same count of Article_Author as before?
        test_article_author_count = test_article_data.article_author_set.count()
        test_value = test_article_author_count
        should_be = test_1_article_author_count
        error_message = "In " + me + ": Article_Data.article_author_set.count() is " + str( test_value ) + ", should be " + str( should_be ) + "."
        self.assertEqual( test_value, should_be, msg = error_message )        
        
        # check to see if subject title updated (should be, since we implemented
        #    updates for existing Article_Author).
        test_article_author_org_string = test_article_author.organization_string
        test_value = test_article_author_org_string
        should_be = lookup_organization_string
        error_message = "In " + me + ": Article_Author " + str( test_person ) + " has org string " + str( test_value ) + ", should be " + str( should_be ) + "."
        self.assertEqual( test_value, should_be, msg = error_message )

        #----------------------------------------------------------------------#
        # !test 3 - delete Article_Author, try again.
        #----------------------------------------------------------------------#

        # delete Article_Author.
        test_article_author.delete()

        # try again.  Should be new Article_Author, new title in
        #    Article_Author, but old title in person.
        
        # retrieve person information.
        person_name = "Karen Irene Schwarck"
        title = "test_title-3"
        lookup_organization_string = "test_org-3"
        person_id = 1031

        # set up person details
        person_details = PersonDetails()
        person_details[ ManualArticleCoder.PARAM_PERSON_NAME ] = person_name
        person_details[ ManualArticleCoder.PARAM_NEWSPAPER_INSTANCE ] = test_article.newspaper
        person_details[ ManualArticleCoder.PARAM_TITLE ] = title
        person_details[ ManualArticleCoder.PARAM_PERSON_ORGANIZATION ] = lookup_organization_string

        # create an article_author.
        test_article_author = test_manual_article_coder.process_author_name( test_article_data, person_name, person_details_IN = person_details )
        
        # check to make sure not None
        error_message = "In " + me + ": attempt to get Article_Author for name " + person_name + " failed - got None back."
        self.assertIsNotNone( test_article_author, msg = error_message )
        
        # ==> Person fields

        # retrieve the person and person ID
        test_person = test_article_author.person
        test_person_id = test_person.id
        test_person_title = test_person.title
        
        # check to make sure it is the right person.
        test_value = test_person_id
        should_be = person_id
        error_message = "In " + me + ": Person " + str( test_person ) + " has ID " + str( test_value ) + ", should be " + str( should_be ) + "."
        self.assertEqual( test_value, should_be, msg = error_message )
        
        # check to see if person title updated.
        test_value = test_person_title
        should_be = title
        error_message = "In " + me + ": Person " + str( test_person ) + " has title " + str( test_value ) + ", should be " + str( should_be ) + "."
        self.assertEqual( test_value, should_be, msg = error_message )
        
        # ==> Article_Author fields
        
        # same Article_Author ID as before?  Should not be...
        test_article_author_id = test_article_author.id
        test_value = test_article_author_id
        should_not_be = test_1_article_author_id
        error_message = "In " + me + ": Article_Author has ID " + str( test_value ) + ", should not be " + str( should_not_be ) + "."
        self.assertNotEqual( test_value, should_not_be, msg = error_message )
        
        # same count of Article_Author as before?
        test_article_author_count = test_article_data.article_author_set.count()
        test_value = test_article_author_count
        should_be = test_1_article_author_count
        error_message = "In " + me + ": Article_Data.article_author_set.count() is " + str( test_value ) + ", should be " + str( should_be ) + "."
        self.assertEqual( test_value, should_be, msg = error_message )        
        
        # check to see if subject title updated (should be - new record).
        test_article_author_org_string = test_article_author.organization_string
        test_value = test_article_author_org_string
        should_be = lookup_organization_string
        error_message = "In " + me + ": Article_Author " + str( test_person ) + " has org. string " + str( test_value ) + ", should be " + str( should_be ) + "."
        self.assertEqual( test_value, should_be, msg = error_message )


        #----------------------------------------------------------------------#
        # !test 4 - try a name of a person not in the database, with title.
        #----------------------------------------------------------------------#

        # - new Person
        # - new Aricle_Subject
        # - check title on both Person and Article_Author.
        
        # retrieve person information.
        person_name = "Jonas Pierpont Morgan"
        title = "test_title-4"
        lookup_organization_string = "test_org-4"
        person_id = -1

        # set up person details
        person_details = PersonDetails()
        person_details[ ManualArticleCoder.PARAM_PERSON_NAME ] = person_name
        person_details[ ManualArticleCoder.PARAM_NEWSPAPER_INSTANCE ] = test_article.newspaper
        person_details[ ManualArticleCoder.PARAM_TITLE ] = title
        person_details[ ManualArticleCoder.PARAM_PERSON_ORGANIZATION ] = lookup_organization_string
    
        # create an article_author.
        test_article_author = test_manual_article_coder.process_author_name( test_article_data, person_name, person_details_IN = person_details )
        
        # check to make sure not None
        error_message = "In " + me + ": attempt to get Article_Author for name " + person_name + " failed - got None back."
        self.assertIsNotNone( test_article_author, msg = error_message )
        
        # ==> Person fields

        # retrieve the person and person ID
        test_person = test_article_author.person
        test_person_id = test_person.id
        test_person_title = test_person.title
        
        # check to see if person title updated (it should be).
        test_value = test_person_title
        should_be = title
        error_message = "In " + me + ": Person " + str( test_person ) + " has title " + str( test_value ) + ", should not be " + str( should_be ) + "."
        self.assertEqual( test_value, should_be, msg = error_message )
        
        # ==> Article_Author fields
        
        # same count of Article_Author as before?
        test_article_author_count = test_article_data.article_author_set.count()
        test_value = test_article_author_count
        should_not_be = test_1_article_author_count
        error_message = "In " + me + ": Article_Data.article_author_set.count() is " + str( test_value ) + ", should not be " + str( should_not_be ) + "."
        self.assertNotEqual( test_value, should_not_be, msg = error_message )        
        
        # should be 2 Article_Authors.
        test_value = test_article_author_count
        should_be = 2
        error_message = "In " + me + ": Article_Data.article_author_set.count() is " + str( test_value ) + ", should be " + str( should_be ) + "."
        self.assertEqual( test_value, should_be, msg = error_message )        
        
        # check to see if subject title updated (should be - new record).
        test_article_author_org_string = test_article_author.organization_string
        test_value = test_article_author_org_string
        should_be = lookup_organization_string
        error_message = "In " + me + ": Article_Author " + str( test_person ) + " has org. string " + str( test_value ) + ", should be " + str( should_be ) + "."
        self.assertEqual( test_value, should_be, msg = error_message )


    #-- END test method test_process_author_name() --#


    def test_process_mention( self ):
        
        # declare variables
        me = "test_process_mention"
        my_logger_name = ""
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

        print( "\n\n==> Top of " + me + "\n" )
        my_logger_name = "TestArticleCoder." + me

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
        TestHelper.output_debug( debug_string, me, logger_name_IN = my_logger_name )

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
        TestHelper.output_debug( debug_string, me, logger_name_IN = my_logger_name )
        
        # try adding the same mention again.
        test_article_subject_mention = test_manual_article_coder.process_mention( test_article, test_article_subject, mention_name )

        # ID should be same as before.
        self.assertEqual( test_article_subject_mention.id, test_mention_id )

        # count should be 1.
        test_mention_count = test_article_subject.article_subject_mention_set.all().count()
        self.assertEqual( test_mention_count, 1 )

        debug_string = "\nMention count: " + str( test_mention_count )
        TestHelper.output_debug( debug_string, me, logger_name_IN = my_logger_name )
        
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
        TestHelper.output_debug( debug_string, me, logger_name_IN = my_logger_name )

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
        TestHelper.output_debug( debug_string, me, logger_name_IN = my_logger_name )
        
    #-- END test method test_process_mention() --#


    def test_process_quotation( self ):
        
        # declare variables
        me = "test_process_quotation"
        my_logger_name = ""
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

        print( "\n\n==> Top of " + me + "\n" )
        my_logger_name = "TestArticleCoder." + me

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
        TestHelper.output_debug( debug_string, me, logger_name_IN = my_logger_name )

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
        TestHelper.output_debug( debug_string, me, logger_name_IN = my_logger_name )
        
        # try adding the same quote again.
        test_article_subject_quotation = test_manual_article_coder.process_quotation( test_article, test_article_subject, quotation_string )

        # ID should be same as before.
        self.assertEqual( test_article_subject_quotation.id, test_quotation_id )

        # count should be 1.
        test_quotation_count = test_article_subject.article_subject_quotation_set.all().count()
        self.assertEqual( test_quotation_count, 1 )

        debug_string = "\nRecord count: " + str( test_quotation_count )
        TestHelper.output_debug( debug_string, me, logger_name_IN = my_logger_name )
        
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
        TestHelper.output_debug( debug_string, me, logger_name_IN = my_logger_name )

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
        TestHelper.output_debug( debug_string, me, logger_name_IN = my_logger_name )
        
    #-- END test method test_process_quotation() --#


    def test_process_subject_name( self ):
        
        # declare variables
        me = "test_process_subject_name"
        my_logger_name = ""
        debug_string = ""
        error_message = ""
        test_manual_article_coder = None
        test_article = None
        test_user = None
        test_article_data = None
        person_name = ""
        title = ""
        person_id = -1
        person_details = None
        test_article_subject = None
        test_person = None
        test_person_id = -1
        test_person_title = ""
        test_article_subject_id = -1
        test_article_subject_title = ""
        test_1_article_subject_id = -1
        test_article_subject_count = -1
        test_1_article_subject_count = -1

        print( "\n\n==> Top of " + me + "\n" )
        my_logger_name = "TestArticleCoder." + me

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

        #----------------------------------------------------------------------#
        # !test 1 - with person ID.       
        #----------------------------------------------------------------------#

        # retrieve person information.
        person_name = "Karen Irene Schwarck"
        title = "test_title"
        person_id = 1031

        # set up person details
        person_details = PersonDetails()
        person_details[ ManualArticleCoder.PARAM_PERSON_NAME ] = person_name
        person_details[ ManualArticleCoder.PARAM_NEWSPAPER_INSTANCE ] = test_article.newspaper
        
        # got a title?
        if ( ( title is not None ) and ( title != "" ) ):
            
            # we do.  store it in person_details.
            person_details[ ManualArticleCoder.PARAM_TITLE ] = title
            
        #-- END check to see if title --#

        # got a person ID?
        if ( ( person_id is not None ) and ( person_id != "" ) and ( person_id > 0 ) ):
            
            # we do.  store it in person_details.
            person_details[ ManualArticleCoder.PARAM_PERSON_ID ] = person_id
            
        #-- END check to see if title --#

        # create an article_subject.
        test_article_subject = test_manual_article_coder.process_subject_name( test_article_data, person_name, person_details_IN = person_details )
        
        # check to make sure not None
        error_message = "In " + me + ": attempt to get Article_Subject for person ID " + str( person_id ) + " failed - got None back."
        self.assertIsNotNone( test_article_subject, msg = error_message )
        
        # ==> Person fields

        # retrieve the person and person ID
        test_person = test_article_subject.person
        test_person_id = test_person.id
        test_person_title = test_person.title
        
        # check to make sure it is the right person.
        test_value = test_person_id
        should_be = person_id
        error_message = "In " + me + ": Person " + str( test_person ) + " has ID " + str( test_value ) + ", should be " + str( should_be ) + "."
        self.assertEqual( test_value, should_be, msg = error_message )
        
        # check to see if person title updated.
        test_value = test_person_title
        should_be = title
        error_message = "In " + me + ": Person " + str( test_person ) + " has title " + str( test_value ) + ", should be " + str( should_be ) + "."
        self.assertEqual( test_value, should_be, msg = error_message )
        
        # ==> Article_Subject fields

        # check to see if subject title updated.
        test_article_subject_title = test_article_subject.title
        test_value = test_article_subject_title
        should_be = title
        error_message = "In " + me + ": Article_Subject " + str( test_article_subject.id ) + " has title " + str( test_value ) + ", should be " + str( should_be ) + "."
        self.assertEqual( test_value, should_be, msg = error_message )
        
        # capture test Article_Subject ID, count of Article_Subjects for next
        #    test.
        test_1_article_subject_id = test_article_subject.id
        test_1_article_subject_count = test_article_data.article_subject_set.count()
        

        #----------------------------------------------------------------------#
        # !test 2 - change title, use name to lookup, don't pass ID.
        #----------------------------------------------------------------------#

        # retrieve person information.
        person_name = "Karen Irene Schwarck"
        title = "test_title-2"
        person_id = 1031

        # set up person details
        person_details = PersonDetails()
        person_details[ ManualArticleCoder.PARAM_PERSON_NAME ] = person_name
        person_details[ ManualArticleCoder.PARAM_NEWSPAPER_INSTANCE ] = test_article.newspaper
        
        # got a title?
        if ( ( title is not None ) and ( title != "" ) ):
            
            # we do.  store it in person_details.
            person_details[ ManualArticleCoder.PARAM_TITLE ] = title
            
        #-- END check to see if title --#

        # create an article_subject.
        test_article_subject = test_manual_article_coder.process_subject_name( test_article_data, person_name, person_details_IN = person_details )
        
        # check to make sure not None
        error_message = "In " + me + ": attempt to get Article_Subject for name " + person_name + " failed - got None back."
        self.assertIsNotNone( test_article_subject, msg = error_message )
        
        # ==> Person fields

        # retrieve the person and person ID
        test_person = test_article_subject.person
        test_person_id = test_person.id
        test_person_title = test_person.title
        
        # check to make sure it is the right person.
        test_value = test_person_id
        should_be = person_id
        error_message = "In " + me + ": Person " + str( test_person ) + " has ID " + str( test_value ) + ", should be " + str( should_be ) + "."
        self.assertEqual( test_value, should_be, msg = error_message )
        
        # check to see if person title updated.
        test_value = test_person_title
        should_be = title
        error_message = "In " + me + ": Person " + str( test_person ) + " has title " + str( test_value ) + ", should be " + str( should_be ) + "."
        self.assertEqual( test_value, should_be, msg = error_message )
        
        # ==> Article_Subject fields
        
        # same Article_Subject ID as before?
        test_article_subject_id = test_article_subject.id
        test_value = test_article_subject_id
        should_be = test_1_article_subject_id
        error_message = "In " + me + ": Article_Subject has ID " + str( test_value ) + ", should be " + str( should_be ) + "."
        self.assertEqual( test_value, should_be, msg = error_message )
        
        # same count of Article_Subject as before?
        test_article_subject_count = test_article_data.article_subject_set.count()
        test_value = test_article_subject_count
        should_be = test_1_article_subject_count
        error_message = "In " + me + ": Article_Data.article_subject_set.count() is " + str( test_value ) + ", should be " + str( should_be ) + "."
        self.assertEqual( test_value, should_be, msg = error_message )        
        
        # check to see if subject title updated (should be, since we enabled
        #    updates for existing Article_Subject).
        test_article_subject_title = test_article_subject.title
        test_value = test_article_subject_title
        should_be = title
        error_message = "In " + me + ": Person " + str( test_person ) + " has title " + str( test_value ) + ", should be " + str( should_be ) + "."
        self.assertEqual( test_value, should_be, msg = error_message )

        #----------------------------------------------------------------------#
        # !test 3 - delete Article_Subject, try again.
        #----------------------------------------------------------------------#

        # delete Article_Subject.
        test_article_subject.delete()

        # try again.  Should be new Article_Subject, new title in
        #    Article_Subject, but old title in person.
        
        # retrieve person information.
        person_name = "Karen Irene Schwarck"
        title = "test_title-3"
        person_id = 1031

        # set up person details
        person_details = PersonDetails()
        person_details[ ManualArticleCoder.PARAM_PERSON_NAME ] = person_name
        person_details[ ManualArticleCoder.PARAM_NEWSPAPER_INSTANCE ] = test_article.newspaper
        
        # got a title?
        if ( ( title is not None ) and ( title != "" ) ):
            
            # we do.  store it in person_details.
            person_details[ ManualArticleCoder.PARAM_TITLE ] = title
            
        #-- END check to see if title --#

        # create an article_subject.
        test_article_subject = test_manual_article_coder.process_subject_name( test_article_data, person_name, person_details_IN = person_details )
        
        # check to make sure not None
        error_message = "In " + me + ": attempt to get Article_Subject for name " + person_name + " failed - got None back."
        self.assertIsNotNone( test_article_subject, msg = error_message )
        
        # ==> Person fields

        # retrieve the person and person ID
        test_person = test_article_subject.person
        test_person_id = test_person.id
        test_person_title = test_person.title
        
        # check to make sure it is the right person.
        test_value = test_person_id
        should_be = person_id
        error_message = "In " + me + ": Person " + str( test_person ) + " has ID " + str( test_value ) + ", should be " + str( should_be ) + "."
        self.assertEqual( test_value, should_be, msg = error_message )
        
        # check to see if person title updated.
        test_value = test_person_title
        should_be = title
        error_message = "In " + me + ": Person " + str( test_person ) + " has title " + str( test_value ) + ", should be " + str( should_be ) + "."
        self.assertEqual( test_value, should_be, msg = error_message )
        
        # ==> Article_Subject fields
        
        # same Article_Subject ID as before?  Should not be...
        test_article_subject_id = test_article_subject.id
        test_value = test_article_subject_id
        should_not_be = test_1_article_subject_id
        error_message = "In " + me + ": Article_Subject has ID " + str( test_value ) + ", should not be " + str( should_not_be ) + "."
        self.assertNotEqual( test_value, should_not_be, msg = error_message )
        
        # same count of Article_Subject as before?
        test_article_subject_count = test_article_data.article_subject_set.count()
        test_value = test_article_subject_count
        should_be = test_1_article_subject_count
        error_message = "In " + me + ": Article_Data.article_subject_set.count() is " + str( test_value ) + ", should be " + str( should_be ) + "."
        self.assertEqual( test_value, should_be, msg = error_message )        
        
        # check to see if subject title updated (should be - new record).
        test_article_subject_title = test_article_subject.title
        test_value = test_article_subject_title
        should_be = title
        error_message = "In " + me + ": Person " + str( test_person ) + " has title " + str( test_value ) + ", should be " + str( should_be ) + "."
        self.assertEqual( test_value, should_be, msg = error_message )


        #----------------------------------------------------------------------#
        # !test 4 - try a name of a person not in the database, with title.
        #----------------------------------------------------------------------#

        # - new Person
        # - new Aricle_Subject
        # - check title on both Person and Article_Subject.
        
        # retrieve person information.
        person_name = "Jonas Pierpont Morgan"
        title = "test_title-4"
        person_id = -1

        # set up person details
        person_details = PersonDetails()
        person_details[ ManualArticleCoder.PARAM_PERSON_NAME ] = person_name
        person_details[ ManualArticleCoder.PARAM_NEWSPAPER_INSTANCE ] = test_article.newspaper
        
        # got a title?
        if ( ( title is not None ) and ( title != "" ) ):
            
            # we do.  store it in person_details.
            person_details[ ManualArticleCoder.PARAM_TITLE ] = title
            
        #-- END check to see if title --#

        # create an article_subject.
        test_article_subject = test_manual_article_coder.process_subject_name( test_article_data, person_name, person_details_IN = person_details )
        
        # check to make sure not None
        error_message = "In " + me + ": attempt to get Article_Subject for name " + person_name + " failed - got None back."
        self.assertIsNotNone( test_article_subject, msg = error_message )
        
        # ==> Person fields

        # retrieve the person and person ID
        test_person = test_article_subject.person
        test_person_id = test_person.id
        test_person_title = test_person.title
        
        # check to see if person title updated (it should be).
        test_value = test_person_title
        should_be = title
        error_message = "In " + me + ": Person " + str( test_person ) + " has title " + str( test_value ) + ", should not be " + str( should_be ) + "."
        self.assertEqual( test_value, should_be, msg = error_message )
        
        # ==> Article_Subject fields
        
        # same count of Article_Subject as before?
        test_article_subject_count = test_article_data.article_subject_set.count()
        test_value = test_article_subject_count
        should_not_be = test_1_article_subject_count
        error_message = "In " + me + ": Article_Data.article_subject_set.count() is " + str( test_value ) + ", should not be " + str( should_not_be ) + "."
        self.assertNotEqual( test_value, should_not_be, msg = error_message )        
        
        # should be 2 Article_Subjects.
        test_value = test_article_subject_count
        should_be = 2
        error_message = "In " + me + ": Article_Data.article_subject_set.count() is " + str( test_value ) + ", should be " + str( should_be ) + "."
        self.assertEqual( test_value, should_be, msg = error_message )        
        
        # check to see if subject title updated (should be - new record).
        test_article_subject_title = test_article_subject.title
        test_value = test_article_subject_title
        should_be = title
        error_message = "In " + me + ": Person " + str( test_person ) + " has title " + str( test_value ) + ", should be " + str( should_be ) + "."
        self.assertEqual( test_value, should_be, msg = error_message )


    #-- END test method test_process_subject_name() --#


#-- END test class ArticleCoderTest --#
