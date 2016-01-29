"""
This file contains more in-depth tests of the code for connecting to the
OpenCalais API for detecting people in articles.
"""

# django imports
from django.contrib.auth.models import User
import django.test

# python_utilities imports
from python_utilities.network.http_helper import Http_Helper

# sourcenet imports
from sourcenet.article_coding.article_coding import ArticleCoding
from sourcenet.article_coding.article_coding import ArticleCoder
from sourcenet.article_coding.open_calais_v2.open_calais_v2_api_response import OpenCalaisV2ApiResponse
from sourcenet.article_coding.open_calais_v2.open_calais_v2_article_coder import OpenCalaisV2ArticleCoder
from sourcenet.models import Article
from sourcenet.models import Article_Data
from sourcenet.tests.test_helper import TestHelper


class OpenCalaisTest( django.test.TestCase ):
    
    
    #----------------------------------------------------------------------------
    # instance methods
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
        error_count = -1
        error_message = ""
        
        # get setup error count
        setup_error_count = self.setup_error_count
        
        # should be 0
        error_message = ";".join( self.setup_error_list )
        self.assertEqual( setup_error_count, 0, msg = error_message )
        
    #-- END test method test_django_config_installed() --#


    def test_article_coding( self ):
        
        # declare variables
        start_pub_date = None # should be datetime instance
        end_pub_date = None # should be datetime instance
        tag_in_list = []
        paper_id_in_list = []
        params = {}
        my_article_coding = None
        article_qs = None
        article_id_in_list = []
        article_count = -1
        coding_status = ""
        do_coding = True
        
        # test variables
        automated_user = None
        automated_username = ""
        automated_article_data_qs = None
        article_data_count = -1
        
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
        
        # limit to one for an initial test?
        #article_qs = article_qs[ : 1 ]
        
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
        
        # make sure we have at least one article
        article_count = article_qs.count()
        
        # should be 46
        self.assertEqual( article_count, 46 )
        
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
            self.assertIsNotNone( automated_user )
            
            # make sure username is correct
            automated_username = automated_user.username
            self.assertEqual( automated_username, "automated" )
            
            # count number of articles coded by automated user
            automated_article_data_qs = Article_Data.objects.filter( coder = automated_user )
            article_data_count = automated_article_data_qs.count()
            
            # should also be 46
            self.assertEqual( article_data_count, 46 )
            
        else:
            
            # output matching article count.
            print( "do_coding == False, so dry run" )
            print( "- query params:" )
            print( params )
            print( "- matching article count: " + str( article_count ) )
            
        #-- END check to see if we do_coding --#
                             
    #-- END test method test_article_coding() --#


#-- END test class OpenCalaisTest --#