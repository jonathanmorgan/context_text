"""
This file contains more in-depth tests of the code for connecting to the
OpenCalais API for detecting people in articles.
"""

# django imports
from django.contrib.auth.models import User
import django.test

# python_utilities imports
from python_utilities.network.http_helper import Http_Helper

# context_text imports
from context_text.article_coding.article_coding import ArticleCoding
from context_text.article_coding.article_coding import ArticleCoder
from context_text.article_coding.open_calais_v2.open_calais_v2_api_response import OpenCalaisV2ApiResponse
from context_text.article_coding.open_calais_v2.open_calais_v2_article_coder import OpenCalaisV2ArticleCoder
from context_text.models import Article
from context_text.models import Article_Data
from context_text.models import Article_Data_Notes
from context_text.tests.test_helper import TestHelper


class OpenCalaisTest( django.test.TestCase ):


    #----------------------------------------------------------------------------
    # ! ==> CONSTANTS-ish
    #----------------------------------------------------------------------------


    TEST_ARTICLE_TOTAL_COUNT = 46

    # CLASS NAME
    CLASS_NAME = "OpenCalaisTest"


    #----------------------------------------------------------------------------
    # ! ==> instance methods
    #----------------------------------------------------------------------------


    def setUp(self):

        """
        setup tasks.  Call function that we'll re-use.
        """

        # call TestHelper.standardSetUp()
        TestHelper.standardOpenCalaisSetUp( self )

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

    #-- END test method test_django_config_installed() --#


    def test_article_coding( self ):

        # declare variables
        me = "test_article_coding"
        start_pub_date = None # should be datetime instance
        end_pub_date = None # should be datetime instance
        tag_in_list = []
        paper_id_in_list = []
        limit_to = None
        params = {}
        my_article_coding = None
        article_qs = None
        article_id_in_list = []
        article_count = -1
        coding_status = ""
        do_coding = True

        # test variables
        expected_article_count = None
        automated_user = None
        automated_username = ""
        automated_article_data_qs = None
        article_data_count = -1
        article_data_notes_qs = None
        article_data_notes_count = None
        article_data_note = None
        note_content = None
        note_content_json = None
        is_note_ok = None

        print( '\n\n--------> In {}.{}\n'.format( self.CLASS_NAME, me ) )

        # ! ==> filter articles

        # first, use filters to get a list of articles to code - set filter parameters

        # publication date range:
        #start_pub_date = "2009-12-06"
        #end_pub_date = "2009-12-12"
        #params[ ArticleCoding.PARAM_START_DATE ] = start_pub_date
        #params[ ArticleCoding.PARAM_END_DATE ] = end_pub_date

        # tags
        # NOTE - THIS DOES NOT WORK: tag_in_list = [ "prelim_reliability", "prelim_network" ]
        #tag_in_list = "prelim_reliability,prelim_network"
        #params[ ArticleCoding.PARAM_TAG_LIST ] = tag_in_list

        # newspaper ID(s)
        #paper_id_in_list = "1"
        #params[ ArticleCoding.PARAM_PUBLICATION_LIST ] = paper_id_in_list

        # paper sections
        #section_list = "Lakeshore,Front Page,City and Region,Business"
        #params[ ArticleCoding.PARAM_SECTION_LIST ] = section_list

        # set coder you want to use.

        # OpenCalais REST API, version 2
        params[ ArticleCoding.PARAM_CODER_TYPE ] = ArticleCoding.ARTICLE_CODING_IMPL_OPEN_CALAIS_API_V2

        # get instance of ArticleCoding
        my_article_coding = ArticleCoding()

        # set params
        my_article_coding.store_parameters( params )

        # create query set - ArticleCoding does the filtering for you.
        #article_qs = my_article_coding.create_article_query_set()
        article_qs = Article.objects.all()

        # filter on related article IDs?
        #article_id_in_list = [ 360962 ]
        #article_id_in_list = [ 28598 ]
        #article_id_in_list = [ 21653, 21756 ]
        #article_id_in_list = [ 90948 ]
        #article_id_in_list = [ 21627, 21609, 21579 ]
        if ( len( article_id_in_list ) > 0 ):

            # yes.
            article_qs = article_qs.filter( id__in = article_id_in_list )

        #-- END check to see if filter on specific IDs. --#

        # order by ID
        article_qs = article_qs.order_by( "id" )

        # limit to?
        limit_to = 5
        if ( ( limit_to is not None ) and ( limit_to > 0 ) ):

            # limit to
            article_qs = article_qs[ : limit_to ]
            expected_article_count = limit_to

        else:

            # no limit
            expected_article_count = self.TEST_ARTICLE_TOTAL_COUNT

        #-- END check to see if limit_to --#

        # ! ==> run test

        # make sure we have at least one article
        article_count = article_qs.count()

        # should be expected_article_count, either 46 or limit specified.
        test_value = article_count
        should_be = expected_article_count
        error_string = "In " + me + "(): Article count is " + str( test_value ) +", should be " + str( should_be )
        self.assertEqual( test_value, should_be, error_string )

        # Do coding?
        if ( do_coding == True ):

            # yes - as long as we have articles.
            if ( article_count > 0 ):

                # invoke the code_article_data( self, query_set_IN ) method.
                coding_status = my_article_coding.code_article_data( article_qs )

                # output status
                print( "\n\n==============================\n\nCoding status: \"" + coding_status + "\"" )

            #-- END check to see if article count. --#

            # tests

            # automated user created?
            automated_user = ArticleCoder.get_automated_coding_user( False )
            error_string = "In " + me + "(): Automated user not created."
            self.assertIsNotNone( automated_user, error_string )

            # make sure username is correct
            automated_username = automated_user.username
            test_value = automated_username
            should_be = "automated"
            error_string = "In " + me + "(): automated username is " + str( test_value ) +", should be " + str( should_be )
            self.assertEqual( test_value, should_be, error_string )

            # count number of articles coded by automated user
            automated_article_data_qs = Article_Data.objects.filter( coder = automated_user )
            article_data_count = automated_article_data_qs.count()

            # should also be expected_article_count, either 46 or limit specified.
            test_value = article_data_count
            should_be = expected_article_count
            error_string = "In " + me + "(): Article_Data count is " + str( test_value ) +", should be " + str( should_be )
            self.assertEqual( test_value, should_be, error_string )

            # check Article_Data_Notes
            article_data_notes_qs = Article_Data_Notes.objects.all()
            article_data_notes_qs = article_data_notes_qs.filter( content_description = "OpenCalais_REST_API_v2 response JSON" )
            article_data_notes_qs = article_data_notes_qs.filter( note_type = "OpenCalais_REST_API_v2_json" )
            article_data_notes_qs = article_data_notes_qs.filter( tags__name = "OpenCalais_REST_API_v2_json" )
            article_data_notes_qs = article_data_notes_qs.filter( content__isnull = False )
            article_data_notes_qs = article_data_notes_qs.filter( content_json__isnull = False )
            article_data_notes_count = article_data_notes_qs.count()

            # should also be expected_article_count, either 46 or limit specified.
            test_value = article_data_notes_count
            should_be = expected_article_count
            error_string = "In " + me + "(): Article_Data_Notes count is " + str( test_value ) +", should be " + str( should_be )
            self.assertEqual( test_value, should_be, error_string )

            # loop over notes
            for article_data_note in article_data_notes_qs:

                # init
                is_note_ok = True
                error_string = "Article_Data_Notes is not OK: "

                # get content and content_json
                note_content = article_data_note.content
                note_content_json = article_data_note.content_json

                # is content empty?
                if ( ( note_content is None ) or ( note_content == "" ) ):

                    # content is empty.
                    is_note_ok = False
                    error_string += "note has no content; "

                #-- END check content --#

                # is content_json populated?
                if ( note_content_json is not None ):

                    # content_json has something in it. Is it a string?
                    if ( isinstance( note_content_json, str ) == True ):

                        # it is a string. OK to try update.
                        is_note_ok = False
                        error_string += "content_json is a string, not a dict; "

                    elif ( isinstance( note_content_json, dict ) == True ):

                        # dictionary - Already parsed.
                        is_note_ok = True

                    else:

                        # not a string or a dictionary. Already parsed?
                        is_note_ok = False
                        error_string += "content_json is neither a string, nor a dict ( type: {} ); ".format( type( note_content_json ) )

                    #-- END

                else:

                    # no content or content_json. nothing to do.
                    is_note_ok = False
                    error_string += "note has no content_json; "

                #-- END check if note_content_json populated --#

                # Article_Data_Notes instance should be OK.
                test_value = is_note_ok
                error_string = "In {me}(): {error_message}".format(
                    me = me,
                    error_message = error_string
                )
                self.assertTrue( test_value, error_string )

            #-- END loop over Article_Data_Notes. --#

        else:

            # output matching article count.
            print( "do_coding == False, so dry run" )
            print( "- query params:" )
            print( params )
            print( "- matching article count: " + str( article_count ) )

        #-- END check to see if we do_coding --#

    #-- END test method test_article_coding() --#


#-- END test class OpenCalaisTest --#
