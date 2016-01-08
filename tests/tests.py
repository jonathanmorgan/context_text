"""
This file demonstrates writing tests using the unittest module. These will pass
when you run "manage.py test".

Replace this with more appropriate tests for your application.
"""

# django imports
import django.test

# python_utilities imports
from python_utilities.network.http_helper import Http_Helper

# sourcenet imports
from sourcenet.article_coding.open_calais_v2.open_calais_v2_api_response import OpenCalaisV2ApiResponse
from sourcenet.article_coding.open_calais_v2.open_calais_v2_article_coder import OpenCalaisV2ArticleCoder
from sourcenet.tests.test_helper import TestHelper

class PrereqTest( django.test.TestCase ):
    
    
    #----------------------------------------------------------------------------
    # instance methods
    #----------------------------------------------------------------------------


    def setUp(self):
        
        """
        setup tasks.  Call function that we'll re-use.
        """

        # declare variables
        current_fixture = ""
        
        # janky way to add variables to instance since you can't override init.
        self.setup_error_count = 0
        self.setup_error_list = []
        
        # Load auth data fixture
        current_fixture = TestHelper.FIXTURE_UNIT_TEST_AUTH_DATA
        try:
        
            TestHelper.load_fixture( current_fixture )

        except Exception as e:
        
            # looks like there was a problem.
            self.setup_error_count += 1
            self.setup_error_list.append( current_fixture )
            
        #-- END try/except --#
        
        # Load config property data fixture
        current_fixture = TestHelper.FIXTURE_UNIT_TEST_CONFIG_PROPERTIES
        try:
        
            TestHelper.load_fixture( current_fixture )
        

        except Exception as e:
        
            # looks like there was a problem.
            self.setup_error_count += 1
            self.setup_error_list.append( current_fixture )
            
        #-- END try/except --#
        
        # Load base unit test data fixture
        current_fixture = TestHelper.FIXTURE_UNIT_TEST_BASE_DATA
        try:
        
            TestHelper.load_fixture( current_fixture )
        

        except Exception as e:
        
            # looks like there was a problem.
            self.setup_error_count += 1
            self.setup_error_list.append( current_fixture )
            
        #-- END try/except --#
        
        # Load taggit tag data fixture
        current_fixture = TestHelper.FIXTURE_UNIT_TEST_TAGGIT_DATA
        try:
        
            TestHelper.load_fixture( current_fixture )

        except Exception as e:
        
            # looks like there was a problem.
            self.setup_error_count += 1
            self.setup_error_list.append( current_fixture )
            
        #-- END try/except --#
        
        # Load OpenCalais Access Token.
        try:
        
            TestHelper.load_open_calais_access_token()

        except Exception as e:
        
            # looks like there was a problem.
            self.setup_error_count += 1
            self.setup_error_list.append( OpenCalaisV2ArticleCoder.CONFIG_PROP_OPEN_CALAIS_ACCESS_TOKEN )
            
        #-- END try/except --#
        
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


    def test_django_config_installed( self ):

        """
        Tests whether django_config application is installed.
        """
        
        # declare variables
        is_installed = False
        
        try:
        
            # import basic django configuration application.
            from django_config.models import Config_Property
            
            # it is installed!
            is_installed = True

        except Exception as e:
        
            # looks like there was a problem.
            is_installed = False
            
        #-- END try/except --#

        # assert that it is installed.        
        self.assertEqual( is_installed, True )
        
    #-- END test method test_django_config_installed() --#


    def test_open_calais_configured( self ):

        """
        Tests whether OpenCalais configuration properties are set.
        """
        
        # declare variables
        is_configured = False
        oc_api_access_token = ""
        my_http_helper = None
        request_data = ""
        requests_response = None
        requests_raw_text = ""
        requests_response_json = None
        
        try:
        
            # import basic django configuration application.
            from django_config.models import Config_Property
            
            # get config property for OpenCalais Access token
            oc_api_access_token = Config_Property.get_property_value( OpenCalaisV2ArticleCoder.CONFIG_APPLICATION, OpenCalaisV2ArticleCoder.CONFIG_PROP_OPEN_CALAIS_ACCESS_TOKEN, None )
            
            # got a value?
            self.assertNotEqual( oc_api_access_token, "" )
            
            # OK...
            is_configured = True
            
        except Exception as e:
        
            # looks like there was a problem.
            is_configured = False
            
        #-- END try/except --#

        # assert that it is configured.        
        self.assertEqual( is_configured, True )
        
    #-- END test method test_open_calais_configured() --#


    def test_open_calais_access_token( self ):

        """
        Tests whether OpenCalais configuration properties work.
        """
        
        # declare variables
        is_configured = False
        oc_api_access_token = ""
        my_http_helper = None
        request_data = ""
        requests_response = None
        requests_raw_text = ""
        requests_response_json = None
        my_response_helper = None
        person_dict = None
        person_count = 0
        
        try:
        
            # import basic django configuration application.
            from django_config.models import Config_Property
            
            # get config property for OpenCalais Access token
            oc_api_access_token = Config_Property.get_property_value( OpenCalaisV2ArticleCoder.CONFIG_APPLICATION, OpenCalaisV2ArticleCoder.CONFIG_PROP_OPEN_CALAIS_ACCESS_TOKEN, None )
            
            # got a value?
            self.assertNotEqual( oc_api_access_token, "" )
            
            # then, try using value to create a connection to OpenCalais
            
            # setup HTTP helper
            my_http_helper = Http_Helper()
            
            # set HTTP headers
            my_http_helper.set_http_header( OpenCalaisV2ArticleCoder.HTTP_HEADER_NAME_X_AG_ACCESS_TOKEN, oc_api_access_token )
            my_http_helper.set_http_header( OpenCalaisV2ArticleCoder.HTTP_HEADER_NAME_CONTENT_TYPE, OpenCalaisV2ArticleCoder.CONTENT_TYPE_TEXT )
            my_http_helper.set_http_header( OpenCalaisV2ArticleCoder.HTTP_HEADER_NAME_OUTPUT_FORMAT, OpenCalaisV2ArticleCoder.OUTPUT_FORMAT_JSON )
            my_http_helper.set_http_header( OpenCalaisV2ArticleCoder.HTTP_HEADER_NAME_SUBMITTER, "sourcenet_unit_test" )
        
            # set request type
            my_http_helper.request_type = Http_Helper.REQUEST_TYPE_POST
                
            # place fake body text
            request_data = """
            \"We don't see this as an issue for a major sell-off in the markets,\" said Timothy M. Ghriskey, chief investment officer at the Solaris Group. \"People are responding like there is nothing new here.\"
            It has been a rocky start to the new year in global markets. The big fear is that China's economy, the world's second-largest after the United States, is slowing down and crimping growth in other countries.
            Markets \"are in a panic over what's happening in China,\" said Derek Halpenny, European head of global markets research at Bank of Tokyo-Mitsubishi UFJ in London. \"People are saying, 'Whoa, growth is way worse than we were expecting this year.'\"
            """
            
            # make Open Calais API call.
            try:
        
                # make the request.
                requests_response = my_http_helper.load_url_requests( OpenCalaisV2ArticleCoder.OPEN_CALAIS_REST_API_URL, request_type_IN = Http_Helper.REQUEST_TYPE_POST, data_IN = request_data )
                
                # raw text:
                requests_raw_text = requests_response.text
                
                # should not be empty
                self.assertNotEqual( requests_raw_text, "" )
                
                # convert to a json object, inside try since sometimes OpenCalais
                #    returns non-parsable stuff.
                try:
                
                    # convert to JSON object
                    requests_response_json = requests_response.json()
                    
                    # get response helper.
                    my_response_helper = OpenCalaisV2ApiResponse()
                    
                    # chuck the response in there.
                    my_response_helper.set_json_response_object( requests_response_json )
                    
                    # get all the people.
                    person_dict = my_response_helper.get_items_of_type( OpenCalaisV2ApiResponse.OC_ITEM_TYPE_PERSON )
                                
                    # make sure it isn't None
                    self.assertIsNotNone( person_dict )
                    if ( person_dict is not None ):
            
                        person_count = len( person_dict )
                        
                    #-- END check to see if person_dict is None --#

                    # should be at least one person.
                    self.assertNotEqual( person_count, 0 )
        
                    # if we get here, hooray!
                    is_configured = True
                    
                except ValueError as ve:
                
                    # problem parsing JSON - log body of article, response,
                    #    and exception.
                    #exception_message = "ValueError parsing OpenCalais JSON."
                    #my_logger.debug( "\n ! " + exception_message )
                    #my_logger.debug( "\n ! article text:\n" + request_data )
                    #my_logger.debug( "\n ! response text:\n" + requests_raw_text )
                    #print( "exception parsing Article " + str( article_IN.id ) + " - " + requests_raw_text )
                    #my_exception_helper.process_exception( ve, exception_message )
                    
                    # if we get here, hooray!
                    is_configured = False
                    
                except Exception as e:
                
                    # unknown problem parsing JSON - log body of article,
                    #    response, and exception.
                    #exception_message = "Exception parsing OpenCalais JSON."
                    #my_logger.debug( "\n ! " + exception_message )
                    #my_logger.debug( "\n ! article text:\n" + request_data )
                    #my_logger.debug( "\n ! response text:\n" + requests_raw_text )
                    #my_exception_helper.process_exception( e, exception_message )
                    
                    # problem with JSON - error.
                    is_configured = False

                #-- END try/except around JSON processing. --#
            
            except Exception as e:
            
                # unknown problem making API request to OpenCalais - log body of
                #    article, response, and exception.
                #exception_message = "Exception accessing OpenCalais API."
                #my_logger.debug( "\n ! " + exception_message )
                #my_logger.debug( "\n ! article text:\n" + request_data )
                #my_logger.debug( "\n ! response text:\n" + requests_raw_text )
                #my_exception_helper.process_exception( e, exception_message )
                
                # let rest of program know it is not OK to proceed.
                is_configured = False
            
            #-- END try/except around JSON processing. --#

        except Exception as e:
        
            # looks like there was a problem.
            is_configured = False
            
        #-- END try/except --#

        # assert that it is configured.        
        self.assertEqual( is_configured, True )
        
    #-- END test method test_open_calais_access_token() --#


#-- END test class PrereqTest --#