"""
This file contains tests of the context_text NetworkOutput class.

Functions tested:
- process_network_output_request()
"""

# import six
import hashlib
import json
import six

# django imports
import django.test

# python utilities
from python_utilities.strings.string_helper import StringHelper

# context_text imports
from context_text.tests.test_helper import TestHelper

# import class that actually processes requests for outputting networks.
from context_text.export.network_output import NetworkOutput
from context_text.models import NetworkDataOutputLog


class NetworkOutputTest( django.test.TestCase ):


    #----------------------------------------------------------------------------
    # ! ==> Constants-ish
    #----------------------------------------------------------------------------


    # DEBUG
    DEBUG = False

    # CLASS NAME
    CLASS_NAME = "NetworkOutputTest"

    # data spec property names
    PROP_LABEL = "label"
    PROP_DATA_SPEC = "data_spec"
    PROP_OUTPUT_HASH = "output_hash"
    PROP_OUTPUT_LEN = "output_len"
    PROP_PERSON_COUNT = "person_count"
    PROP_PERSON_INCLUDES = "person_includes"
    PROP_PERSON_EXCLUDES = "person_excludes"

    # data spec definitions
    DATA_SPEC_LABEL_TO_DETAILS_MAP = dict()

    # ==> DATA_SPEC_GRP_ALL_NAMES
    data_spec_details = dict()
    data_spec_label = "DATA_SPEC_GRP_ALL_NAMES"
    data_spec_details[ PROP_LABEL ] = data_spec_label
    data_spec_details[ PROP_DATA_SPEC ] = """{
      "coders": "7",
      "end_date": "2010-02-13",
      "tags_list": "",
      "date_range": "",
      "start_date": "2009-12-07",
      "output_type": "tab_delimited_matrix",
      "publications": "1",
      "network_label": "all_names",
      "person_coders": "7",
      "database_output": "yes",
      "person_end_date": "2010-02-13",
      "person_tag_list": "",
      "coder_types_list": "OpenCalais_REST_API_v2",
      "person_date_range": "",
      "person_query_type": "custom",
      "person_start_date": "2009-12-07",
      "unique_identifiers": "",
      "person_publications": "1",
      "coder_id_priority_list": "",
      "coder_type_filter_type": "automated",
      "network_include_headers": "no",
      "person_coder_types_list": "OpenCalais_REST_API_v2",
      "allow_duplicate_articles": "no",
      "network_data_output_type": "net_and_attr_cols",
      "network_download_as_file": "no",
      "person_unique_identifiers": "",
      "include_source_contact_types": [
        "direct",
        "event",
        "past_quotes",
        "document",
        "other"
      ],
      "person_coder_id_priority_list": "",
      "person_coder_type_filter_type": "automated",
      "network_include_render_details": "no",
      "person_allow_duplicate_articles": "no",
      "exclude_persons_with_tags_in_list": "",
      "include_persons_with_single_word_name": "yes"
    }"""
    data_spec_details[ PROP_OUTPUT_HASH ] = "f879560cab27653185bb4e42baec40b6a5d685b4143388e55041399acb921c5f"
    data_spec_details[ PROP_OUTPUT_LEN ] = 14121
    data_spec_details[ PROP_PERSON_COUNT ] = 74
    data_spec_details[ PROP_PERSON_INCLUDES ] = [ 752, 1049 ]
    data_spec_details[ PROP_PERSON_EXCLUDES ] = list()
    DATA_SPEC_LABEL_TO_DETAILS_MAP[ data_spec_label ] = data_spec_details

    # ==> DATA_SPEC_GRP_NO_SINGLE_NAMES
    data_spec_details = dict()
    data_spec_label = "DATA_SPEC_GRP_NO_SINGLE_NAMES"
    data_spec_details[ PROP_LABEL ] = data_spec_label
    data_spec_details[ PROP_DATA_SPEC ] = """{
      "coders": "7",
      "end_date": "2010-02-13",
      "tags_list": "",
      "date_range": "",
      "start_date": "2009-12-07",
      "output_type": "tab_delimited_matrix",
      "publications": "1",
      "network_label": "no_single_names",
      "person_coders": "7",
      "database_output": "yes",
      "person_end_date": "2010-02-13",
      "person_tag_list": "",
      "coder_types_list": "OpenCalais_REST_API_v2",
      "person_date_range": "",
      "person_query_type": "custom",
      "person_start_date": "2009-12-07",
      "unique_identifiers": "",
      "person_publications": "1",
      "coder_id_priority_list": "",
      "coder_type_filter_type": "automated",
      "network_include_headers": "no",
      "person_coder_types_list": "OpenCalais_REST_API_v2",
      "allow_duplicate_articles": "no",
      "network_data_output_type": "net_and_attr_cols",
      "network_download_as_file": "no",
      "person_unique_identifiers": "",
      "include_source_contact_types": "direct,event,past_quotes,document,other",
      "person_coder_id_priority_list": "",
      "person_coder_type_filter_type": "automated",
      "network_include_render_details": "no",
      "person_allow_duplicate_articles": "no",
      "exclude_persons_with_tags_in_list": "",
      "include_persons_with_single_word_name": "no"
    }"""
    data_spec_details[ PROP_OUTPUT_HASH ] = "f85a48630c029f848bbb815d003b188eff38346b8eac0da2d55b7b224b323ac5"
    data_spec_details[ PROP_OUTPUT_LEN ] = 13448
    data_spec_details[ PROP_PERSON_COUNT ] = 72
    data_spec_details[ PROP_PERSON_INCLUDES ] = list()
    data_spec_details[ PROP_PERSON_EXCLUDES ] = [ 752, 1049 ]
    DATA_SPEC_LABEL_TO_DETAILS_MAP[ data_spec_label ] = data_spec_details

    # ==> DATA_SPEC_GRP_EXCLUDE_FROM_PRESS_RELEASE
    data_spec_details = dict()
    data_spec_label = "DATA_SPEC_GRP_EXCLUDE_FROM_PRESS_RELEASE"
    data_spec_details[ PROP_LABEL ] = data_spec_label
    data_spec_details[ PROP_DATA_SPEC ] = """{
      "coders": "7",
      "end_date": "2010-02-13",
      "tags_list": "",
      "date_range": "",
      "start_date": "2009-12-07",
      "output_type": "tab_delimited_matrix",
      "publications": "1",
      "network_label": "exclude_from_press_release",
      "person_coders": "7",
      "database_output": "yes",
      "person_end_date": "2010-02-13",
      "person_tag_list": "",
      "coder_types_list": "OpenCalais_REST_API_v2",
      "person_date_range": "",
      "person_query_type": "custom",
      "person_start_date": "2009-12-07",
      "unique_identifiers": "",
      "person_publications": "1",
      "coder_id_priority_list": "",
      "coder_type_filter_type": "automated",
      "network_include_headers": "no",
      "person_coder_types_list": "OpenCalais_REST_API_v2",
      "allow_duplicate_articles": "no",
      "network_data_output_type": "net_and_attr_cols",
      "network_download_as_file": "no",
      "person_unique_identifiers": "",
      "include_source_contact_types": "direct,event,past_quotes,document,other",
      "person_coder_id_priority_list": "",
      "person_coder_type_filter_type": "automated",
      "network_include_render_details": "no",
      "person_allow_duplicate_articles": "no",
      "exclude_persons_with_tags_in_list": "from_press_release",
      "include_persons_with_single_word_name": "yes"
    }"""
    data_spec_details[ PROP_OUTPUT_HASH ] = "3529e49830a8464cc0d8a497345b56404c73b867b1046fb38df346953a9b3b72"
    data_spec_details[ PROP_OUTPUT_LEN ] = 13122
    data_spec_details[ PROP_PERSON_COUNT ] = 71
    data_spec_details[ PROP_PERSON_INCLUDES ] = list()
    data_spec_details[ PROP_PERSON_EXCLUDES ] = [ 102, 224, 261 ]
    DATA_SPEC_LABEL_TO_DETAILS_MAP[ data_spec_label ] = data_spec_details

    # ==> DATA_SPEC_GRP_EXCLUDE_GODWIN_HEIGHTS
    data_spec_details = dict()
    data_spec_label = "DATA_SPEC_GRP_EXCLUDE_GODWIN_HEIGHTS"
    data_spec_details[ PROP_LABEL ] = data_spec_label
    data_spec_details[ PROP_DATA_SPEC ] = """{
      "coders": "7",
      "end_date": "2010-02-13",
      "tags_list": "",
      "date_range": "",
      "start_date": "2009-12-07",
      "output_type": "tab_delimited_matrix",
      "publications": "1",
      "network_label": "exclude_godwin_heights",
      "person_coders": "7",
      "database_output": "yes",
      "person_end_date": "2010-02-13",
      "person_tag_list": "",
      "coder_types_list": "OpenCalais_REST_API_v2",
      "person_date_range": "",
      "person_query_type": "custom",
      "person_start_date": "2009-12-07",
      "unique_identifiers": "",
      "person_publications": "1",
      "coder_id_priority_list": "",
      "coder_type_filter_type": "automated",
      "network_include_headers": "no",
      "person_coder_types_list": "OpenCalais_REST_API_v2",
      "allow_duplicate_articles": "no",
      "network_data_output_type": "net_and_attr_cols",
      "network_download_as_file": "no",
      "person_unique_identifiers": "",
      "include_source_contact_types": "direct,event,past_quotes,document,other",
      "person_coder_id_priority_list": "",
      "person_coder_type_filter_type": "automated",
      "network_include_render_details": "no",
      "person_allow_duplicate_articles": "no",
      "exclude_persons_with_tags_in_list": "godwin_heights",
      "include_persons_with_single_word_name": "yes"
    }"""
    data_spec_details[ PROP_OUTPUT_HASH ] = "59e1b6ba6aab28cf37fcb45877d8cdd86d8593df9fa506352d0abd1b6fd3c29b"
    data_spec_details[ PROP_OUTPUT_LEN ] = 13122
    data_spec_details[ PROP_PERSON_COUNT ] = 71
    data_spec_details[ PROP_PERSON_INCLUDES ] = list()
    data_spec_details[ PROP_PERSON_EXCLUDES ] = [ 187, 188, 189 ]
    DATA_SPEC_LABEL_TO_DETAILS_MAP[ data_spec_label ] = data_spec_details

    # ==> DATA_SPEC_GRP_EXCLUDE_TWO_TAGS
    data_spec_details = dict()
    data_spec_label = "DATA_SPEC_GRP_EXCLUDE_TWO_TAGS"
    data_spec_details[ PROP_LABEL ] = data_spec_label
    data_spec_details[ PROP_DATA_SPEC ] = """{
      "coders": "7",
      "end_date": "2010-02-13",
      "tags_list": "",
      "date_range": "",
      "start_date": "2009-12-07",
      "output_type": "tab_delimited_matrix",
      "publications": "1",
      "network_label": "exclude_two_tags",
      "person_coders": "7",
      "database_output": "yes",
      "person_end_date": "2010-02-13",
      "person_tag_list": "",
      "coder_types_list": "OpenCalais_REST_API_v2",
      "person_date_range": "",
      "person_query_type": "custom",
      "person_start_date": "2009-12-07",
      "unique_identifiers": "",
      "person_publications": "1",
      "coder_id_priority_list": "",
      "coder_type_filter_type": "automated",
      "network_include_headers": "no",
      "person_coder_types_list": "OpenCalais_REST_API_v2",
      "allow_duplicate_articles": "no",
      "network_data_output_type": "net_and_attr_cols",
      "network_download_as_file": "no",
      "person_unique_identifiers": "",
      "include_source_contact_types": "direct,event,past_quotes,document,other",
      "person_coder_id_priority_list": "",
      "person_coder_type_filter_type": "automated",
      "network_include_render_details": "no",
      "person_allow_duplicate_articles": "no",
      "exclude_persons_with_tags_in_list": "from_press_release,godwin_heights",
      "include_persons_with_single_word_name": "yes"
    }"""
    data_spec_details[ PROP_OUTPUT_HASH ] = "441127876c15eda7fb6cbf64e8555e011a2f459ba64b7111ac3dd4cbcdafbb2a"
    data_spec_details[ PROP_OUTPUT_LEN ] = 12159
    data_spec_details[ PROP_PERSON_COUNT ] = 68
    data_spec_details[ PROP_PERSON_INCLUDES ] = list()
    data_spec_details[ PROP_PERSON_EXCLUDES ] = [ 102, 224, 261, 187, 188, 189 ]
    DATA_SPEC_LABEL_TO_DETAILS_MAP[ data_spec_label ] = data_spec_details

    # ==> DATA_SPEC_GRP_EXCLUDE_TWO_TAGS_AND_SINGLE_NAMES
    data_spec_details = dict()
    data_spec_label = "DATA_SPEC_GRP_EXCLUDE_TWO_TAGS_AND_SINGLE_NAMES"
    data_spec_details[ PROP_LABEL ] = data_spec_label
    data_spec_details[ PROP_DATA_SPEC ] = """{
      "coders": "7",
      "end_date": "2010-02-13",
      "tags_list": "",
      "date_range": "",
      "start_date": "2009-12-07",
      "output_type": "tab_delimited_matrix",
      "publications": "1",
      "network_label": "exclude_two_tags_and_single_names",
      "person_coders": "7",
      "database_output": "yes",
      "person_end_date": "2010-02-13",
      "person_tag_list": "",
      "coder_types_list": "OpenCalais_REST_API_v2",
      "person_date_range": "",
      "person_query_type": "custom",
      "person_start_date": "2009-12-07",
      "unique_identifiers": "",
      "person_publications": "1",
      "coder_id_priority_list": "",
      "coder_type_filter_type": "automated",
      "network_include_headers": "no",
      "person_coder_types_list": "OpenCalais_REST_API_v2",
      "allow_duplicate_articles": "no",
      "network_data_output_type": "net_and_attr_cols",
      "network_download_as_file": "no",
      "person_unique_identifiers": "",
      "include_source_contact_types": "direct,event,past_quotes,document,other",
      "person_coder_id_priority_list": "",
      "person_coder_type_filter_type": "automated",
      "network_include_render_details": "no",
      "person_allow_duplicate_articles": "no",
      "exclude_persons_with_tags_in_list": "from_press_release,godwin_heights",
      "include_persons_with_single_word_name": "no"
    }"""
    data_spec_details[ PROP_OUTPUT_HASH ] = "0f8a530f18a724b3d724d7fe9caa3082954c049abdc02b77bc480fc432d0a770"
    data_spec_details[ PROP_OUTPUT_LEN ] = 11534
    data_spec_details[ PROP_PERSON_COUNT ] = 66
    data_spec_details[ PROP_PERSON_INCLUDES ] = list()
    data_spec_details[ PROP_PERSON_EXCLUDES ] = [ 752, 1049, 102, 224, 261, 187, 188, 189 ]
    DATA_SPEC_LABEL_TO_DETAILS_MAP[ data_spec_label ] = data_spec_details


    #----------------------------------------------------------------------
    # ! ==> class methods
    #----------------------------------------------------------------------


    @classmethod
    def make_string_hash( cls, value_IN, hash_function_IN = hashlib.sha256 ):

            # return reference
            value_OUT = None

            # declare variables
            me = "make_string_hash"

            # call StringHelper method.
            value_OUT = StringHelper.make_string_hash( value_IN, hash_function_IN = hash_function_IN )

            return value_OUT

    #-- END function make_string_hash() --#


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


    def validate_process_network_output_request( self, data_spec_details_IN ):

        '''
        Render network output from different specs, verifying that the result
            matches what we expect.
        '''

        # declare variables
        me = "test_process_network_output_request"
        data_spec_label = None
        request_json = None
        network_outputter = None
        network_data = None
        network_data_hash = None
        network_data_length = None
        master_person_dict = None
        person_count = None
        find_person_id = None
        is_person_in_dict = None
        include_person_list = None
        exclude_person_list = None

        # declare variables - inputs
        data_spec_label_IN = None
        data_spec_IN = None
        data_output_hash_IN = None
        data_output_len_IN = None
        person_count_IN = None
        person_id_include_list_IN = None
        person_id_exclude_list_IN = None

        # debug
        debug_flag = self.DEBUG

        # init from details
        data_spec_label_IN = data_spec_details_IN.get( self.PROP_LABEL, None )
        data_spec_IN = data_spec_details_IN.get( self.PROP_DATA_SPEC, None )
        data_output_hash_IN = data_spec_details_IN.get( self.PROP_OUTPUT_HASH, None )
        data_output_len_IN = data_spec_details_IN.get( self.PROP_OUTPUT_LEN, None )
        person_count_IN = data_spec_details_IN.get( self.PROP_PERSON_COUNT, None )
        person_id_include_list_IN = data_spec_details_IN.get( self.PROP_PERSON_INCLUDES, None )
        person_id_exclude_list_IN = data_spec_details_IN.get( self.PROP_PERSON_EXCLUDES, None )

        # ==> label
        data_spec_label = data_spec_label_IN

        # load JSON
        request_json = json.loads( data_spec_IN )

        # make NetworkOutput instance.
        network_outputter = network_outputter = NetworkOutput()

        # create data
        network_data = network_outputter.process_network_output_request(
            params_IN = request_json,
            debug_flag_IN = False
        )

        # Create and test hash
        network_data_hash = self.make_string_hash( network_data )

        # success?
        test_value = network_data_hash
        should_be = data_output_hash_IN
        error_string = "For spec {data_spec_label}: network data hash is {test_value}, should be {should_be}".format(
            data_spec_label = data_spec_label,
            test_value = test_value,
            should_be = should_be
        )
        self.assertEqual( test_value, should_be, msg = error_string )

        # Create and test length
        network_data_length = len( network_data )

        # success?
        test_value = network_data_length
        should_be = data_output_len_IN
        error_string = "For spec {data_spec_label}: network data len() is {test_value}, should be {should_be}".format(
            data_spec_label = data_spec_label,
            test_value = test_value,
            should_be = should_be
        )
        self.assertEqual( test_value, should_be, msg = error_string )

        # evaluate master person dict
        master_person_dict = network_outputter.create_person_dict( load_person_IN = True )

        # test length
        person_count = len( master_person_dict )

        # success?
        test_value = person_count
        should_be = person_count_IN
        error_string = "For spec {data_spec_label}: network data len() is {test_value}, should be {should_be}".format(
            data_spec_label = data_spec_label,
            test_value = test_value,
            should_be = should_be
        )
        self.assertEqual( test_value, should_be, msg = error_string )

        # make sure people who should be there are in dictionary
        include_person_list = person_id_include_list_IN
        for find_person_id in include_person_list:

            # success?
            test_value = find_person_id in master_person_dict
            error_string = "For spec {data_spec_label}: person {person_id} SHOULD be in person dictionary, and they are not.".format(
                data_spec_label = data_spec_label,
                person_id = find_person_id
            )
            self.assertTrue( test_value, msg = error_string )

        #-- END loop over include persons to find. --#

        # make sure people who should not be there are not in dictionary
        exclude_person_list = person_id_exclude_list_IN
        for find_person_id in exclude_person_list:

            # success?
            test_value = find_person_id in master_person_dict
            error_string = "For spec {data_spec_label}: person {person_id} SHOULD NOT be in person dictionary, and they are present.".format(
                data_spec_label = data_spec_label,
                person_id = find_person_id
            )
            self.assertFalse( test_value, msg = error_string )

        #-- END loop over include persons to find. --#

    #-- END test method test_create_article_relations() --#


    #----------------------------------------------------------------------------
    # ! ==> instance methods - tests
    #----------------------------------------------------------------------------


    def test_process_network_output_request( self ):

        '''
        Render network output from different specs, verifying that the result
            matches what we expect.
        '''

        # declare variables
        me = "test_process_network_output_request"
        my_data_spec_dict = None
        data_spec_label = None
        data_spec_details = None
        data_spec = None
        data_spec_json = None
        new_data_spec_string = None
        my_network_label = None
        output_log_qs = None
        output_log_count = None

        # debug
        debug_flag = self.DEBUG

        print( '\n\n====> In {}.{}\n'.format( self.CLASS_NAME, me ) )

        # get map of data spec labels to data spec details
        my_data_spec_dict = self.DATA_SPEC_LABEL_TO_DETAILS_MAP

        # loop
        for data_spec_label, data_spec_details in my_data_spec_dict.items():

            # call the validate method.
            print( "Evaluating data spec {}".format( data_spec_label ) )
            self.validate_process_network_output_request( data_spec_details )

        #-- END loop over data specs --#

        # use last item in list to test not adding timestamp to label.

        # get data spec from data_spec_details.
        data_spec = data_spec_details.get( self.PROP_DATA_SPEC, None )
        data_spec_json = json.loads( data_spec )

        # set property `db_add_timestamp_to_label' to "no"
        data_spec_json[ NetworkOutput.PARAM_DB_ADD_TIMESTAMP_TO_LABEL ] = NetworkOutput.CHOICE_NO

        # retrieve network_label property.
        my_network_label = data_spec_json.get( NetworkOutput.PARAM_NETWORK_LABEL, None )

        # convert back to string, store back in details.
        new_data_spec_string = json.dumps( data_spec_json, sort_keys = True, indent = 4, separators = ( ',', ': ' ) )
        data_spec_details[ self.PROP_DATA_SPEC ] = new_data_spec_string

        # first, try to retrieve log with label = just network label.
        output_log_qs = NetworkDataOutputLog.objects.filter( label = my_network_label )
        output_log_count = output_log_qs.count()

        # success?
        test_value = output_log_count
        should_be = 0
        error_string = "For spec {data_spec_label}: with 'db_add_timestamp_to_label' to 'yes', made data, then tried to retrieve output log instance using just label ( {my_network_label} ). Should have returned {should_be}, returned {test_value}.".format(
            data_spec_label = data_spec_label,
            my_network_label = my_network_label,
            should_be = should_be,
            test_value = test_value
        )
        self.assertEqual( test_value, should_be, msg = error_string )

        # validate again (render output again with updated spec)
        self.validate_process_network_output_request( data_spec_details )

        # now, try to retrieve output log with just label.
        output_log_qs = NetworkDataOutputLog.objects.filter( label = my_network_label )
        output_log_count = output_log_qs.count()

        # success?
        test_value = output_log_count
        should_be = 1
        error_string = "For spec {data_spec_label}: set 'db_add_timestamp_to_label' to 'no', then made data, then tried to retrieve output log instance using just label ( {my_network_label} ). Should have returned {should_be} record, returned {test_value}.".format(
            data_spec_label = data_spec_label,
            my_network_label = my_network_label,
            should_be = should_be,
            test_value = test_value
        )
        self.assertEqual( test_value, should_be, msg = error_string )

    #-- END test method test_process_network_output_request() --#


#-- END test class NetworkOutputTest --#
