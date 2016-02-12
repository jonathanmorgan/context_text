"""
This file contains tests of code specific to ManualArticleCoder.

Functions tested:
- convert_article_data_to_data_store_json()
- process_data_store_json()
"""

# django imports
from django.contrib.auth.models import User
import django.test

# python utilities
from python_utilities.json.json_helper import JSONHelper

# sourcenet imports
from sourcenet.article_coding.manual_coding.manual_article_coder import ManualArticleCoder
from sourcenet.models import Article
from sourcenet.models import Article_Data
from sourcenet.models import Article_Subject
from sourcenet.models import Person
from sourcenet.tests.test_helper import TestHelper


class ManualArticleCoderTest( django.test.TestCase ):
    
    #----------------------------------------------------------------------------
    # Constants-ish
    #----------------------------------------------------------------------------


    data_store_json_insert = '''{
  "person_array": [
    {
      "person_type": "author",
      "person_name": "Nardy Baeza Bickel",
      "person_organization": "The Grand Rapids Press",
      "title": "The Grand Rapids Press",
      "quote_text": "",
      "person_id": 161
    },
    {
      "person_type": "author",
      "person_name": "Nate Reens",
      "person_organization": "The Grand Rapids Press",
      "title": "The Grand Rapids Press",
      "quote_text": "",
      "person_id": null
    },
    {
      "person_type": "source",
      "person_name": "Alex McNamara",
      "person_organization": "",
      "title": "snowboarder",
      "quote_text": "The Rockford friends, who have been practicing jumping and twirling tricks at Cannonsburg for a decade, said a \\\"long\\\" summer and fall left them eager to bust out their boards.",
      "person_id": null
    },
    {
      "person_type": "source",
      "person_name": "Justin VanderVelde",
      "person_organization": "",
      "title": "22-year-old snowboarder",
      "quote_text": "\\\"You have to wait all summer for it to start snowing, so you might as well (hit the hill) as soon as the snow falls,\\\" the 22-year-old VanderVelde said Sunday.",
      "person_id": 162
    },
    {
      "person_type": "source",
      "person_name": "Pete Goodell",
      "person_organization": "Pando Winter Sports Park",
      "title": "manager at Pando Winter Sports Park",
      "quote_text": "\\\"We went from green grass to a lot of snow,\\\" said Pete Goodell, a manager at Pando. \\\"We still had to make a lot with the machines, but it was a great start.",
      "person_id": 163
    },
    {
      "person_type": "source",
      "person_name": "Bob Dukesherer",
      "person_organization": "National Weather Service",
      "title": "National Weather Service meteorologist",
      "quote_text": "Bob Dukesherer, a National Weather Service meteorologist, says it's a near certainty that will happen by Tuesday, when a storm will settle in and hang over the region through Saturday.",
      "person_id": null
    },
    {
      "person_type": "source",
      "person_name": "Steve Brown",
      "person_organization": "Cannonsburg Ski Area",
      "title": "manager at Cannonsburg Ski Area",
      "quote_text": "The forecast should make for good business at Cannonsburg, which drew several hundred customers on its first day of business Sunday, manager Steve Brown said.",
      "person_id": 165
    },
    {
      "person_type": "source",
      "person_name": "Rick DeGraaf",
      "person_organization": "",
      "title": "Skier",
      "quote_text": "Skier Rick DeGraaf, who was headed for his second ride on the lift at Cannonsburg on Sunday, said the day's moderate temperatures made for a nice day on the hill.",
      "person_id": 166
    },
    {
      "person_type": "source",
      "person_name": "West Michigan",
      "person_organization": "",
      "title": "nice day on the hill",
      "quote_text": "this week",
      "person_id": null
    }
  ],
  "next_person_index": 9,
  "name_to_person_index_map": {
    "Nardy Baeza Bickel": 0,
    "Nate Reens": 1,
    "Alex McNamara": 2,
    "Justin VanderVelde": 3,
    "Pete Goodell": 4,
    "Bob Dukesherer": 5,
    "Steve Brown": 6,
    "Rick DeGraaf": 7,
    "West Michigan": 8
  },
  "id_to_person_index_map": {
    "161": 0,
    "162": 3,
    "163": 4,
    "165": 6,
    "166": 7
  },
  "status_message_array": [],
  "latest_person_index": 8
}'''


    data_store_json_insert_with_nulls = '''{
  "person_array": [
    null,
    {
      "person_type": "author",
      "person_name": "Nardy Baeza Bickel",
      "person_organization": "The Grand Rapids Press",
      "title": "The Grand Rapids Press",
      "quote_text": "",
      "person_id": 161
    },
    {
      "person_type": "author",
      "person_name": "Nate Reens",
      "person_organization": "The Grand Rapids Press",
      "title": "The Grand Rapids Press",
      "quote_text": "",
      "person_id": null
    },
    null,
    {
      "person_type": "source",
      "person_name": "Alex McNamara",
      "person_organization": "",
      "title": "snowboarder",
      "quote_text": "The Rockford friends, who have been practicing jumping and twirling tricks at Cannonsburg for a decade, said a \\\"long\\\" summer and fall left them eager to bust out their boards.",
      "person_id": null
    },
    {
      "person_type": "source",
      "person_name": "Justin VanderVelde",
      "person_organization": "",
      "title": "22-year-old snowboarder",
      "quote_text": "\\\"You have to wait all summer for it to start snowing, so you might as well (hit the hill) as soon as the snow falls,\\\" the 22-year-old VanderVelde said Sunday.",
      "person_id": 162
    },
    {
      "person_type": "source",
      "person_name": "Pete Goodell",
      "person_organization": "Pando Winter Sports Park",
      "title": "manager at Pando Winter Sports Park",
      "quote_text": "\\\"We went from green grass to a lot of snow,\\\" said Pete Goodell, a manager at Pando. \\\"We still had to make a lot with the machines, but it was a great start.",
      "person_id": 163
    },
    {
      "person_type": "source",
      "person_name": "Bob Dukesherer",
      "person_organization": "National Weather Service",
      "title": "National Weather Service meteorologist",
      "quote_text": "Bob Dukesherer, a National Weather Service meteorologist, says it's a near certainty that will happen by Tuesday, when a storm will settle in and hang over the region through Saturday.",
      "person_id": null
    },
    {
      "person_type": "source",
      "person_name": "Steve Brown",
      "person_organization": "Cannonsburg Ski Area",
      "title": "manager at Cannonsburg Ski Area",
      "quote_text": "The forecast should make for good business at Cannonsburg, which drew several hundred customers on its first day of business Sunday, manager Steve Brown said.",
      "person_id": 165
    },
    {
      "person_type": "source",
      "person_name": "Rick DeGraaf",
      "person_organization": "",
      "title": "Skier",
      "quote_text": "Skier Rick DeGraaf, who was headed for his second ride on the lift at Cannonsburg on Sunday, said the day's moderate temperatures made for a nice day on the hill.",
      "person_id": 166
    },
    {
      "person_type": "source",
      "person_name": "West Michigan",
      "person_organization": "",
      "title": "nice day on the hill",
      "quote_text": "this week",
      "person_id": null
    },
    null
  ],
  "next_person_index": 12,
  "name_to_person_index_map": {
    "Nardy Baeza Bickel": 1,
    "Nate Reens": 2,
    "Alex McNamara": 4,
    "Justin VanderVelde": 5,
    "Pete Goodell": 6,
    "Bob Dukesherer": 7,
    "Steve Brown": 8,
    "Rick DeGraaf": 9
  },
  "id_to_person_index_map": {
    "161": 1,
    "162": 5,
    "163": 6,
    "165": 8,
    "166": 9
  },
  "status_message_array": [],
  "latest_person_index": 11
}'''


    data_store_json_update = '''{
  "person_array": [
    {
      "person_type": "author",
      "person_name": "Hardy Baeza Bickel",
      "person_organization": "The Grand Rapids Press",
      "title": "Grand Rapids Press",
      "quote_text": "",
      "person_id": 161
    },
    {
      "person_type": "author",
      "person_name": "James Cabalum",
      "person_organization": "The Grand Rapids Press",
      "title": "Special to The Grand Rapids Press",
      "quote_text": "",
      "person_id": null
    },
    {
      "person_type": "source",
      "person_name": "Alex McNamara",
      "person_organization": "",
      "title": "snowboarder",
      "quote_text": "The Rockford friends, who have been practicing jumping and twirling tricks at Cannonsburg for a decade, said a \\\"long\\\" summer and fall left them eager to bust out their boards.",
      "person_id": null
    },
    {
      "person_type": "source",
      "person_name": "Barren hills",
      "person_organization": "",
      "title": "visible only four days",
      "quote_text": "The snow-covered runs are a beautiful sight to snowboarders Alex McNamara and Justin VanderVelde.",
      "person_id": null
    },
    {
      "person_type": "source",
      "person_name": "Pete Goodell",
      "person_organization": "Pando Winter Sports Park",
      "title": "manager at Pando Winter Sports Park",
      "quote_text": "\\\"We went from green grass to a lot of snow,\\\" said Pete Goodell, a manager at Pando. \\\"We still had to make a lot with the machines, but it was a great start.",
      "person_id": 163
    },
    {
      "person_type": "source",
      "person_name": "Bob Dukesherer",
      "person_organization": "National Weather Service",
      "title": "meteorologist",
      "quote_text": "Bob Dukesherer, a National Weather Service meteorologist, says it's a near certainty that will happen by Tuesday, when a storm will settle in and hang over the region through Saturday.",
      "person_id": null
    },
    {
      "person_type": "source",
      "person_name": "Steven Brown",
      "person_organization": "Cannonsburg Ski Area",
      "title": "manager at Cannonsburg Ski Area",
      "quote_text": "The forecast should make for good business at Cannonsburg, which drew several hundred customers on its first day of business Sunday, manager Steve Brown said.",
      "person_id": 165
    },
    {
      "person_type": "subject",
      "person_name": "Richard DeGraaf",
      "person_organization": "",
      "title": "good business",
      "quote_text": "Skier Rick DeGraaf, who was headed for his second ride on the lift at Cannonsburg on Sunday, said the day's moderate temperatures made for a nice day on the hill.",
      "person_id": 166
    }
  ],
  "next_person_index": 8,
  "name_to_person_index_map": {
    "Nardy Baeza Bickel": 0,
    "James Cabalum": 1,
    "Alex McNamara": 2,
    "Barren hills": 3,
    "Pete Goodell": 4,
    "Bob Dukesherer": 5,
    "Steve Brown": 6,
    "Rick DeGraaf": 7
  },
  "id_to_person_index_map": {
    "161": 0,
    "163": 4,
    "165": 6,
    "166": 7
  },
  "status_message_array": [],
  "latest_person_index": 7
}'''


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


    def test_convert_article_data_to_data_store_json( self ):
        
        # ! TODO - check if organization coming out correct
        # declare variables
        me = "test_convert_article_data_to_data_store_json"
        debug_string = ""
        error_string = ""
        test_manual_article_coder = None
        test_article_data_id = None
        test_article_data = None
        test_json_generated_dict = None
        test_json_dict_string = ""
        test_json_generated_string = ""
        
        # declare variables - interact with JSON output.
        test_value = -1
        lastest_person_index = -1
        next_person_index = -1
        person_array_list = None
        person_array_list_count = -1
        name_to_index_dict = None
        name_to_index_dict_count = -1
        person_id_to_index_dict = None
        person_id_to_index_dict_count = -1
        author_name = ""
        source_name = ""
        test_lookup_name = ""
        test_index = -1
        test_person_dict = None
        test_person_type = None
        test_person_name = ""
        test_person_id = -1
        test_title = ""
        test_quote_text = ""
        test_index_from_id = -1

        print( "\n\n==> Top of " + me + "\n" )

        # create ManualArticleCoder instance.
        test_manual_article_coder = ManualArticleCoder()

        # get an Article_Data instance.
        test_article_data_id = 82
        test_article_data = Article_Data.objects.get( pk = test_article_data_id )

        # convert Article_Data to JSON dictionary.
        test_json_generated_dict = test_manual_article_coder.convert_article_data_to_data_store_json( test_article_data, return_string_IN = False )
        
        # convert to string
        test_json_dict_string = JSONHelper.pretty_print_json( test_json_generated_dict )
        dict_json_length = len( test_json_dict_string )
        
        # convert Article_Data to JSON string.
        test_json_generated_string = test_manual_article_coder.convert_article_data_to_data_store_json( test_article_data, return_string_IN = True )
        string_json_length = len( test_json_dict_string )

        # should be the same
        error_string = "In " + me + "(): JSON from dict len() = " + str( dict_json_length ) + "; JSON string len() = " + str( string_json_length )
        self.assertEqual( dict_json_length, string_json_length, msg = error_string )

        # and, see if the dict has what we'd expect.

        #----------------------------------------------------------------------#
        # ! ==> lastest_person_index
        #----------------------------------------------------------------------#

        test_name =  ManualArticleCoder.DATA_STORE_PROP_LATEST_PERSON_INDEX
        should_be = 7
        lastest_person_index = test_json_generated_dict.get( test_name, -1 )
        test_value = lastest_person_index
        error_string = "In " + me + "(): " + test_name + " is " + str( test_value ) + "; should be " + str( should_be )+ "."
        self.assertEqual( test_value, should_be, msg = error_string )

        #----------------------------------------------------------------------#
        # ! ==> next_person_index
        #----------------------------------------------------------------------#

        test_name =  ManualArticleCoder.DATA_STORE_PROP_NEXT_PERSON_INDEX
        should_be = 8
        next_person_index = test_json_generated_dict.get( test_name, -1 )
        test_value = next_person_index
        error_string = "In " + me + "(): " + test_name + " is " + str( test_value ) + "; should be " + str( should_be )+ "."
        self.assertEqual( test_value, should_be, msg = error_string )
        
        #----------------------------------------------------------------------#
        # ! ==> person_array
        #----------------------------------------------------------------------#

        test_name =  ManualArticleCoder.DATA_STORE_PROP_PERSON_ARRAY
        person_array_list = test_json_generated_dict.get( test_name, None )

        error_string = "In " + me + "(): " + test_name + " in generated JSON is None."
        self.assertIsNotNone( person_array_list, msg = error_string )        

        # anything there at all?
        if ( person_array_list is not None ):
        
            # how many items?
            person_array_list_count = len( person_array_list )
            
            # should be 8
            test_value = person_array_list_count
            should_be = 8
            error_string = "In " + me + "(): " + test_name + " length = " + str( test_value ) + ", should be " + str( should_be ) + "."
            self.assertEqual( test_value, should_be, msg = error_string )
            
        #-- END check to see if we have person array list. --#

        #----------------------------------------------------------------------#
        # ! ==> name_to_person_index_map
        #----------------------------------------------------------------------#

        test_name =  ManualArticleCoder.DATA_STORE_PROP_NAME_TO_PERSON_INDEX_MAP
        name_to_index_dict = test_json_generated_dict.get( test_name, None )

        error_string = "In " + me + "(): " + test_name + " in generated JSON is None."
        self.assertIsNotNone( name_to_index_dict, msg = error_string )        

        # anything there at all?
        if ( name_to_index_dict is not None ):
        
            # how many items?
            name_to_index_dict_count = len( name_to_index_dict )
            
            # should be 8
            test_value = name_to_index_dict_count
            should_be = 8
            error_string = "In " + me + "(): " + test_name + " length = " + str( test_value ) + ", should be " + str( should_be ) + "."
            self.assertEqual( test_value, should_be, msg = error_string )
            
        #-- END check to see if we have name_to_person_index_map. --#

        #----------------------------------------------------------------------#
        # ! ==> id_to_person_index_map
        #----------------------------------------------------------------------#

        person_id_to_index_dict = None

        test_name =  ManualArticleCoder.DATA_STORE_PROP_ID_TO_PERSON_INDEX_MAP
        person_id_to_index_dict = test_json_generated_dict.get( test_name, None )

        error_string = "In " + me + "(): " + test_name + " in generated JSON is None."
        self.assertIsNotNone( person_id_to_index_dict, msg = error_string )        

        # anything there at all?
        if ( person_id_to_index_dict is not None ):
        
            # how many items?
            person_id_to_index_dict_count = len( person_id_to_index_dict )
            
            # should be 8
            test_value = person_id_to_index_dict_count
            should_be = 8
            error_string = "In " + me + "(): " + test_name + " length = " + str( test_value ) + ", should be " + str( should_be ) + "."
            self.assertEqual( test_value, should_be, msg = error_string )
            
        #-- END check to see if we have name_to_person_index_map. --#
        
        # spot check one author name and one source name.
        
        #----------------------------------------------------------------------#
        # ! Author "Nate Reens"
        #----------------------------------------------------------------------#
        
        # set author name
        author_name = "Nate Reens"
        test_lookup_name = author_name
        
        # get index from name_to_person_index_map
        test_index = name_to_index_dict.get( test_lookup_name, -1 )
        
        # should not be -1
        error_string = "In " + me + "(): name " + test_lookup_name + " index is " + str( test_index ) + ", should not be -1."
        self.assertNotEqual( test_index, -1, msg = error_string )
        
        # get person dict for that index.
        test_person_dict = person_array_list[ test_index ]
        
        error_string = "In " + me + "(): person dict for index " + str( test_index ) + " in name_to_person_index_map is None."
        self.assertIsNotNone( test_person_dict, msg = error_string )        

        # got one?
        if ( test_person_dict is not None ):

            # get values and test values
            
            # ==> person_type
            test_name = ManualArticleCoder.DATA_STORE_PROP_PERSON_TYPE
            test_person_type = test_person_dict.get( test_name, None )
            test_value = test_person_type
            should_be = ManualArticleCoder.PERSON_TYPE_AUTHOR
            error_string = "In " + me + "(): " + test_name + " = \"" + test_value + "\", should be \"" + should_be + "\""
            self.assertEqual( test_value, should_be, error_string )
            
            # ==> person_name
            test_name = ManualArticleCoder.DATA_STORE_PROP_PERSON_NAME
            test_person_name = test_person_dict.get( test_name, None )
            test_value = test_person_name
            should_be = test_lookup_name
            error_string = "In " + me + "(): " + test_name + " = \"" + test_value + "\", should be \"" + should_be + "\""
            self.assertEqual( test_value, should_be, error_string )
            
            # ==> title
            test_name = ManualArticleCoder.DATA_STORE_PROP_TITLE
            test_title = test_person_dict.get( test_name, None )
            test_value = test_title
            should_be = "The Grand Rapids Press"
            error_string = "In " + me + "(): " + test_name + " = \"" + test_value + "\", should be \"" + should_be + "\""
            self.assertEqual( test_value, should_be, error_string )
            
            # ==> quote_text
            test_name = ManualArticleCoder.DATA_STORE_PROP_QUOTE_TEXT
            test_quote_text = test_person_dict.get( test_name, None )
            test_value = test_quote_text
            should_be = ""
            error_string = "In " + me + "(): " + test_name + " = \"" + test_value + "\", should be \"" + should_be + "\""
            self.assertEqual( test_value, should_be, error_string )
            
            # ==> person_id
            test_name = ManualArticleCoder.DATA_STORE_PROP_PERSON_ID
            test_person_id = test_person_dict.get( test_name, None )
            test_value = test_person_id
            should_be = 46
            error_string = "In " + me + "(): " + test_name + " = \"" + str( test_value ) + "\", should be \"" + str( should_be ) + "\""
            self.assertEqual( test_value, should_be, error_string )

            # try to use ID to get index.
            test_index_from_id = person_id_to_index_dict.get( test_person_id, -1 )
            test_value = test_index_from_id
            should_be = test_index
            error_string = "In " + me + "(): index for id " + str( test_person_id ) + " = \"" + str( test_value ) + "\", should be \"" + str( should_be ) + "\""
            self.assertEqual( test_value, should_be, error_string )            

        #-- END check to see if author's person dict is None. --#
        
        #----------------------------------------------------------------------#
        # ! Source "Rick DeGraaf"
        #----------------------------------------------------------------------#
        
        # set source name
        source_name = "Rick DeGraaf"
        test_lookup_name = source_name
        
        # get index from name_to_person_index_map
        test_index = name_to_index_dict.get( test_lookup_name, -1 )
        
        # should not be -1
        error_string = "In " + me + "(): name " + test_lookup_name + " index is " + str( test_index ) + ", should not be -1."
        self.assertNotEqual( test_index, -1, msg = error_string )
        
        # get person dict for that index.
        test_person_dict = person_array_list[ test_index ]
        
        error_string = "In " + me + "(): person dict for index " + str( test_index ) + " in name_to_person_index_map is None."
        self.assertIsNotNone( test_person_dict, msg = error_string )        

        # got one?
        if ( test_person_dict is not None ):

            # get values and test values
            
            # ==> person_type
            test_name = ManualArticleCoder.DATA_STORE_PROP_PERSON_TYPE
            test_person_type = test_person_dict.get( test_name, None )
            test_value = test_person_type
            should_be = ManualArticleCoder.PERSON_TYPE_SOURCE
            error_string = "In " + me + "(): " + test_name + " = \"" + test_value + "\", should be \"" + should_be + "\""
            self.assertEqual( test_value, should_be, error_string )
            
            # ==> person_name
            test_name = ManualArticleCoder.DATA_STORE_PROP_PERSON_NAME
            test_person_name = test_person_dict.get( test_name, None )
            test_value = test_person_name
            should_be = test_lookup_name
            error_string = "In " + me + "(): " + test_name + " = \"" + test_value + "\", should be \"" + should_be + "\""
            self.assertEqual( test_value, should_be, error_string )
            
            # ==> title
            test_name = ManualArticleCoder.DATA_STORE_PROP_TITLE
            test_title = test_person_dict.get( test_name, None )
            test_value = test_title
            should_be = "skier"
            error_string = "In " + me + "(): " + test_name + " = \"" + test_value + "\", should be \"" + should_be + "\""
            self.assertEqual( test_value, should_be, error_string )
            
            # ==> quote_text
            test_name = ManualArticleCoder.DATA_STORE_PROP_QUOTE_TEXT
            test_quote_text = test_person_dict.get( test_name, None )
            test_value = test_quote_text
            should_be = ""
            error_string = "In " + me + "(): " + test_name + " = \"" + test_value + "\", should be \"" + should_be + "\""
            self.assertEqual( test_value, should_be, error_string )
            
            # ==> person_id
            test_name = ManualArticleCoder.DATA_STORE_PROP_PERSON_ID
            test_person_id = test_person_dict.get( test_name, None )
            test_value = test_person_id
            should_be = 166
            error_string = "In " + me + "(): " + test_name + " = \"" + str( test_value ) + "\", should be \"" + str( should_be ) + "\""
            self.assertEqual( test_value, should_be, error_string )

            # try to use ID to get index.
            test_index_from_id = person_id_to_index_dict.get( test_person_id, -1 )
            test_value = test_index_from_id
            should_be = test_index
            error_string = "In " + me + "(): index for id " + str( test_person_id ) + " = \"" + str( test_value ) + "\", should be \"" + str( should_be ) + "\""
            self.assertEqual( test_value, should_be, error_string )            

        #-- END check to see if source's person dict is None. --#

    #-- END test method test_convert_article_data_to_data_store_json() --#


    def test_process_data_store_json( self ):
        
        # declare variables
        me = "test_process_data_store_json"
        error_string = ""
        loop_counter = -1
        test_article = None
        test_json_string_list = []
        test_json_string = ""
        test_user = None
        test_article_data = None
        test_article_data_id = -1
        test_response_dict = None
        
        # declare variables - test results
        test_author_qs = None
        test_author_count = -1
        test_subject_qs = None
        test_subject_count = -1
        test_source_qs = None
        test_source_count = -1
        
        # declare variables - test individual people
        test_lookup_name = ""
        test_person_qs = None
        test_person = None
        test_person_title = None
        test_article_author = None
        test_article_subject_qs = None
        test_article_subject = None
        test_quote_qs = None
        test_mention_qs = None
        
        # declare variables - test update
        work_qs = None
        test_name = ""

        print( "\n\n==> Top of " + me + "\n" )

        # initialize JSON string list        
        test_json_string_list = [ self.data_store_json_insert, self.data_store_json_insert_with_nulls ]
        
        # ! ==> loop over JSON strings - each should be identical in terms of output,
        #    one has nulls interspersed, one does not.
        loop_counter = 0
        for test_json_string in test_json_string_list:
        
            # increment loop counter
            loop_counter += 1
        
            # setup - wipe the title from Rick DeGraaf.
            test_person_qs = Person.look_up_person_from_name( "Rick DeGraaf" )
            test_person = test_person_qs.get()
            test_person.title = ""
            test_person.save()
            
            # create ManualArticleCoder instance.
            test_manual_article_coder = ManualArticleCoder()
    
            # get article whose data this is.                
            test_article = Article.objects.get( pk = 21409 )
    
            # get test user.
            test_user = TestHelper.get_test_user()
    
            # create bare-bones Article_Data, get ID
            #test_article_data = Article_Data()
            #test_article_data.coder = test_user
            #test_article_data.article = test_article
            #test_article_data.save()
            #test_article_data_id = test_article_data.id
            
            # initialize empty response dictionary
            test_response_dict = {}
    
            # call process_data_store_json method.
            test_article_data = test_manual_article_coder.process_data_store_json( test_article, test_user, test_json_string )
    
            #----------------------------------------------------------------------#
            # ! test resulting article data.
            #----------------------------------------------------------------------#
    
            # author count
            test_author_qs = test_article_data.article_author_set.all()
            test_author_count = test_author_qs.count()
            
            # should be 2
            test_value = test_author_count
            should_be = 2
            error_string = "In " + me + "(): counter = " + str( loop_counter ) + "; author count is " + str( test_author_count ) +", should be " + str( should_be )
            self.assertEqual( test_value, should_be, error_string )            
    
            # subject count
            test_subject_qs = test_article_data.article_subject_set.all()
            test_subject_count = test_subject_qs.count()
    
            # should be 7
            test_value = test_subject_count
            should_be = 7
            error_string = "In " + me + "(): counter = " + str( loop_counter ) + "; subject count is " + str( test_value ) +", should be " + str( should_be )
            self.assertEqual( test_value, should_be, error_string )            
    
            # source count
            test_source_qs = test_article_data.article_subject_set.filter( subject_type = Article_Subject.SUBJECT_TYPE_QUOTED )
            test_source_count = test_source_qs.count()
    
            # should be 7
            test_value = test_source_count
            should_be = 7
            error_string = "In " + me + "(): counter = " + str( loop_counter ) + "; source count is " + str( test_value ) +", should be " + str( should_be )
            self.assertEqual( test_value, should_be, error_string )            
    
            # spot check one author name, an existing source, and a new source.
            
            #----------------------------------------------------------------------#
            # ! Author "Nate Reens"
            #----------------------------------------------------------------------#
            
            # set author name
            author_name = "Nate Reens"
            test_lookup_name = author_name
            
            # retrieve person
            test_person_qs = Person.look_up_person_from_name( test_lookup_name )
            test_person = test_person_qs.get()
            
            # should be ID 46
            test_value = test_person.id
            should_be = 46
            error_string = "In " + me + "(): counter = " + str( loop_counter ) + "; test person ID is \"" + str( test_value ) + "\", should be \"" + str( should_be ) + "\""
            self.assertEqual( test_value, should_be, error_string )            
            
            # check title (it gets updated now!)
            test_value = test_person.title
            should_be = "The Grand Rapids Press"
            error_string = "In " + me + "(): counter = " + str( loop_counter ) + "; test title is \"" + str( test_value ) + "\", should be \"" + str( should_be ) + "\""
            self.assertEqual( test_value, should_be, error_string )            
            
            # get Article_Author
            test_article_author = test_article_data.article_author_set.get( person = test_person )
            
            # test organization affiliation
            test_value = test_article_author.organization_string
            should_be = "The Grand Rapids Press"
            error_string = "In " + me + "(): counter = " + str( loop_counter ) + "; test organization_string is \"" + str( test_value ) + "\", should be " + str( should_be ) + "\""
            self.assertEqual( test_value, should_be, error_string )
            
            # test Article_Author title
            test_value = test_article_author.title
            error_string = "In " + me + "(): counter = " + str( loop_counter ) + "; test Article_Author title is \"" + str( test_value ) + "\", should be None"
            self.assertIsNone( test_value, error_string )
    
            #----------------------------------------------------------------------#
            # ! Source "Rick DeGraaf"
            #----------------------------------------------------------------------#
            
            # set source name
            source_name = "Rick DeGraaf"
            test_lookup_name = source_name
            
            # retrieve person
            test_person_qs = Person.look_up_person_from_name( test_lookup_name )
            test_person = test_person_qs.get()
            
            # should be ID 166
            test_value = test_person.id
            should_be = 166
            error_string = "In " + me + "(): counter = " + str( loop_counter ) + "; test person ID is " + str( test_value ) + ", should be " + str( should_be )
            self.assertEqual( test_value, should_be, error_string )            
            
            # check title
            test_value = test_person.title
            should_be = "Skier"
            error_string = "In " + me + "(): counter = " + str( loop_counter ) + "; test title is " + str( test_value ) + ", should be " + str( should_be )
            self.assertEqual( test_value, should_be, error_string )            
            
            # get Article_Subject
            test_article_subject_qs = test_article_data.article_subject_set.filter( subject_type = Article_Subject.SUBJECT_TYPE_QUOTED )
            test_article_subject = test_article_subject_qs.get( person = test_person )
            
            # test Article_Subject title
            test_value = test_article_subject.title
            should_be = "Skier"
            error_string = "In " + me + "(): counter = " + str( loop_counter ) + "; test Article_Subject title is \"" + str( test_value ) + "\", should be \"" + str( should_be ) + "\""
            self.assertEqual( test_value, should_be, error_string )
            
            # check for quote and mention.
            
            # ==> quotation
            test_quote_qs = test_article_subject.article_subject_quotation_set.all()
            
            # should be 1
            test_value = test_quote_qs.count()
            should_be = 1
            error_string = "In " + me + "(): counter = " + str( loop_counter ) + "; quotation count is " + str( test_value ) +", should be " + str( should_be )
            self.assertEqual( test_value, should_be, error_string )
            
            # make sure quote text is right.
            test_quote = test_quote_qs.get()
            test_value = test_quote.value
            should_be = "Skier Rick DeGraaf, who was headed for his second ride on the lift at Cannonsburg on Sunday, said the day's moderate temperatures made for a nice day on the hill."
            error_string = "In " + me + "(): counter = " + str( loop_counter ) + "; quotation value is " + str( test_value ) +", should be " + str( should_be )
            self.assertEqual( test_value, should_be, error_string )
            
            # ! - TODO - test position of quotation.
    
            # ==> mention
            test_mention_qs = test_article_subject.article_subject_mention_set.all()
    
            # should be 1
            test_value = test_mention_qs.count()
            should_be = 1
            error_string = "In " + me + "(): counter = " + str( loop_counter ) + "; mention count is " + str( test_value ) +", should be " + str( should_be )
            self.assertEqual( test_value, should_be, error_string )
            
            # make sure quote text is right.
            test_mention = test_mention_qs.get()
            test_value = test_mention.value
            should_be = test_lookup_name
            error_string = "In " + me + "(): counter = " + str( loop_counter ) + "; mention value is " + str( test_value ) +", should be " + str( should_be )
            self.assertEqual( test_value, should_be, error_string )
            
            # ! - TODO - test position of mention.
           
            #----------------------------------------------------------------------#
            # ! Source "Western Michigan"
            #----------------------------------------------------------------------#
            
            # set source name
            source_name = "West Michigan"
            test_lookup_name = source_name
            
            # retrieve person
            test_person_qs = Person.look_up_person_from_name( test_lookup_name )
            test_person = test_person_qs.get()
            
            # check title
            test_value = test_person.title
            should_be = "nice day on the hill"
            error_string = "In " + me + "(): counter = " + str( loop_counter ) + "; test title is " + str( test_value ) + ", should be " + str( should_be )
            self.assertEqual( test_value, should_be, error_string )            
            
            # get Article_Subject
            test_article_subject_qs = test_article_data.article_subject_set.filter( subject_type = Article_Subject.SUBJECT_TYPE_QUOTED )
            test_article_subject = test_article_subject_qs.get( person = test_person )
            
            # test Article_Subject title
            test_value = test_article_subject.title
            should_be = "nice day on the hill"
            error_string = "In " + me + "(): counter = " + str( loop_counter ) + "; test Article_Subject title is \"" + str( test_value ) + "\", should be \"" + str( should_be ) + "\""
            self.assertEqual( test_value, should_be, error_string )
            
            # check for quote and mention.
            
            # ==> quotation
            test_quote_qs = test_article_subject.article_subject_quotation_set.all()
            
            # should be 1
            test_value = test_quote_qs.count()
            should_be = 1
            error_string = "In " + me + "(): counter = " + str( loop_counter ) + "; quotation count is " + str( test_value ) +", should be " + str( should_be )
            self.assertEqual( test_value, should_be, error_string )
            
            # make sure quote text is right.
            test_quote = test_quote_qs.get()
            test_value = test_quote.value
            should_be = "this week"
            error_string = "In " + me + "(): counter = " + str( loop_counter ) + "; quotation value is " + str( test_value ) +", should be " + str( should_be )
            self.assertEqual( test_value, should_be, error_string )
            
            # ! - TODO - test position of quotation.
    
            # ==> mention
            test_mention_qs = test_article_subject.article_subject_mention_set.all()
    
            # should be 1
            test_value = test_mention_qs.count()
            should_be = 1
            error_string = "In " + me + "(): counter = " + str( loop_counter ) + "; mention count is " + str( test_value ) +", should be " + str( should_be )
            self.assertEqual( test_value, should_be, error_string )
            
            # make sure quote text is right.
            test_mention = test_mention_qs.get()
            test_value = test_mention.value
            should_be = test_lookup_name
            error_string = "In " + me + "(): counter = " + str( loop_counter ) + "; mention value is " + str( test_value ) +", should be " + str( should_be )
            self.assertEqual( test_value, should_be, error_string )
            
            # ! - TODO - test position of mention.
            
        #-- END loop over list of JSON documents. --#

        #----------------------------------------------------------------------#
        # ! ==> update test
        
        print( "\n\nUpdate test\n\n" )
        
        # get JSON string
        test_json_string = self.data_store_json_update
        
        # setup - wipe the title from Rick DeGraaf.
        test_person_qs = Person.look_up_person_from_name( "Rick DeGraaf" )
        test_person = test_person_qs.get()
        test_person.title = ""
        test_person.save()
        
        # create ManualArticleCoder instance.
        test_manual_article_coder = ManualArticleCoder()

        # get article whose data this is.                
        test_article = Article.objects.get( pk = 21409 )

        # get test user.
        test_user = TestHelper.get_test_user()

        # create bare-bones Article_Data, get ID
        #test_article_data = Article_Data()
        #test_article_data.coder = test_user
        #test_article_data.article = test_article
        #test_article_data.save()
        #test_article_data_id = test_article_data.id
        
        # initialize empty response dictionary
        test_response_dict = {}

        # call process_data_store_json method.
        test_article_data = test_manual_article_coder.process_data_store_json( test_article, test_user, test_json_string )

        #----------------------------------------------------------------------#
        # test resulting article data.
        #----------------------------------------------------------------------#

        #----------------------------------------------------------------------#
        # ! authors
        
        # author count
        test_author_qs = test_article_data.article_author_set.all()
        test_author_count = test_author_qs.count()
        
        for test_author in test_author_qs:
            
            print( "post-update - author: " + str( test_author ) + "; Article_Author name = " + test_author.name )
            
        #-- END loop over authors. --#
        
        # should be 2
        test_value = test_author_count
        should_be = 2
        error_string = "In " + me + "(): author count is " + str( test_value ) +", should be " + str( should_be )
        self.assertEqual( test_value, should_be, error_string )
        
        # make sure that Nate Reens (person ID 46) is not an author.
        work_qs = test_author_qs.filter( person__id = 46 )
        test_value = work_qs.count()
        should_be = 0
        error_string = "In " + me + "(): checking if Nate Reens (46) has been removed - authors who are Nate Reens = " + str( test_value ) +", should be " + str( should_be )
        self.assertEqual( test_value, should_be, error_string )
        
        # and that James Cabalum was added as an author.
        test_name = "James Cabalum"
        test_person_qs = Person.look_up_person_from_name( test_name )
        test_person = test_person_qs.get()
        work_qs = test_author_qs.filter( person = test_person )
        test_value = work_qs.count()
        should_be = 1
        error_string = "In " + me + "(): checking if " + test_name + " has been added as author - authors who match = " + str( test_value ) +", should be " + str( should_be )
        self.assertEqual( test_value, should_be, error_string )

        #----------------------------------------------------------------------#
        # ! subjects
        
        # subject count
        test_subject_qs = test_article_data.article_subject_set.all()
        test_subject_count = test_subject_qs.count()

        for test_subject in test_subject_qs:
            
            print( "post-update - subject: " + str( test_subject ) + "; Article_Subject name = " + test_subject.name )
            
        #-- END loop over authors. --#

        # should be 6
        test_value = test_subject_count
        should_be = 6
        error_string = "In " + me + "(): subject count is " + str( test_value ) +", should be " + str( should_be )
        self.assertEqual( test_value, should_be, error_string )
        
        # make sure that West Michigan is not a subject.
        test_name = "West Michigan"
        test_person_qs = Person.look_up_person_from_name( test_name )
        test_person = test_person_qs.get()
        work_qs = test_subject_qs.filter( person = test_person )
        test_value = work_qs.count()
        should_be = 0
        error_string = "In " + me + "(): checking if " + test_name + " has been removed as subject - subjects who match = " + str( test_value ) +", should be " + str( should_be )
        self.assertEqual( test_value, should_be, error_string )
        
        # make sure that Justin VanderVelde (person id 162) is not a subject.
        work_qs = test_subject_qs.filter( person__id = 162 )
        test_value = work_qs.count()
        should_be = 0
        error_string = "In " + me + "(): checking if Justin VanderVelde (162) has been removed - subject matches = " + str( test_value ) +", should be " + str( should_be )
        self.assertEqual( test_value, should_be, error_string )
        
        test_name = "West Michigan"
        test_person_qs = Person.look_up_person_from_name( test_name )
        test_person = test_person_qs.get()
        work_qs = test_subject_qs.filter( person = test_person )
        test_value = work_qs.count()
        should_be = 0
        error_string = "In " + me + "(): checking if " + test_name + " has been removed as subject - subjects who match = " + str( test_value ) +", should be " + str( should_be )
        self.assertEqual( test_value, should_be, error_string )
        
        # and that James Cabalum was added as an author.
        test_name = "James Cabalum"
        test_person_qs = Person.look_up_person_from_name( test_name )
        test_person = test_person_qs.get()
        work_qs = test_author_qs.filter( person = test_person )
        test_value = work_qs.count()
        should_be = 1
        error_string = "In " + me + "(): checking if " + test_name + " has been added as author - authors who match = " + str( test_value ) +", should be " + str( should_be )
        self.assertEqual( test_value, should_be, error_string )

        # source count
        test_source_qs = test_article_data.article_subject_set.filter( subject_type = Article_Subject.SUBJECT_TYPE_QUOTED )
        test_source_count = test_source_qs.count()

        # should be 5
        test_value = test_source_count
        should_be = 5
        error_string = "In " + me + "(): source count is " + str( test_value ) +", should be " + str( should_be )
        self.assertEqual( test_value, should_be, error_string )            

        # spot check one author name, an existing source, and a new source.
        
        #----------------------------------------------------------------------#
        # ! Author "Nate Reens"
        #----------------------------------------------------------------------#
        
        # set author name
        author_name = "Nate Reens"
        test_lookup_name = author_name
        
        # retrieve person
        test_person_qs = Person.look_up_person_from_name( test_lookup_name )
        test_person = test_person_qs.get()
        
        # should be ID 46
        test_value = test_person.id
        should_be = 46
        error_string = "In " + me + "(): test person ID is \"" + str( test_value ) + "\", should be \"" + str( should_be ) + "\""
        self.assertEqual( test_value, should_be, error_string )            
        
        # get Article_Author
        test_article_author_qs = test_article_data.article_author_set.filter( person = test_person )
        
        # should not be one
        test_value = test_article_author_qs.count()
        should_be = 0
        error_string = "In " + me + "(): Article_Author count for \"" + author_name + "\" is \"" + str( test_value ) + "\", should be " + str( should_be ) + "\""
        self.assertEqual( test_value, should_be, error_string )
        
        #----------------------------------------------------------------------#
        # ! Author "James Cabalum"
        #----------------------------------------------------------------------#
        
        # set author name
        author_name = "James Cabalum"
        test_lookup_name = author_name
        
        # retrieve person
        test_person_qs = Person.look_up_person_from_name( test_lookup_name )
        test_person = test_person_qs.get()
        
        # get Article_Author
        test_article_author_qs = test_article_data.article_author_set.filter( person = test_person )
        
        # should be one
        test_value = test_article_author_qs.count()
        should_be = 1
        error_string = "In " + me + "(): Article_Author count for \"" + author_name + "\" is \"" + str( test_value ) + "\", should be " + str( should_be ) + "\""
        self.assertEqual( test_value, should_be, error_string )
        
        #----------------------------------------------------------------------#
        # ! Source "Rick DeGraaf"
        #----------------------------------------------------------------------#
        
        # set source name
        source_name = "Rick DeGraaf"
        test_lookup_name = source_name
        
        # retrieve person
        test_person_qs = Person.look_up_person_from_name( test_lookup_name )
        test_person = test_person_qs.get()
        
        # check title
        test_value = test_person.title
        should_be = "good business"
        error_string = "In " + me + "(): test title is " + str( test_value ) + ", should be " + str( should_be )
        self.assertEqual( test_value, should_be, error_string )            
        
        # get Article_Subject
        test_article_subject_qs = test_article_data.article_subject_set.filter( subject_type = Article_Subject.SUBJECT_TYPE_MENTIONED )
        test_article_subject = test_article_subject_qs.get( person = test_person )
        
        # test Article_Subject title
        test_value = test_article_subject.name
        should_be = "Richard DeGraaf"
        error_string = "In " + me + "(): test Article_Subject title is \"" + str( test_value ) + "\", should be \"" + str( should_be ) + "\""
        self.assertEqual( test_value, should_be, error_string )
        
        # test Article_Subject title
        test_value = test_article_subject.title
        should_be = "good business"
        error_string = "In " + me + "(): test Article_Subject title is \"" + str( test_value ) + "\", should be \"" + str( should_be ) + "\""
        self.assertEqual( test_value, should_be, error_string )
        
        # check for quote and mention.
        
        # ==> mention
        test_mention_qs = test_article_subject.article_subject_mention_set.all()

        # ! - TODO - should be 1, but is 2...
        test_value = test_mention_qs.count()
        should_be = 2
        error_string = "In " + me + "(): mention count is " + str( test_value ) +", should be " + str( should_be )
        self.assertEqual( test_value, should_be, error_string )
        
        # make sure mention text is right.
        for test_mention in test_mention_qs:

            test_value = test_mention.value
            should_be_in = [ test_lookup_name, "Richard DeGraaf" ]
            error_string = "In " + me + "(): mention value is " + str( test_value ) +", should be in " + str( should_be_in )
            self.assertIn( test_value, should_be_in, error_string )
            
            # ! - TODO - test position of mention.

        #-- END loop over mentions --#
        
       
        #----------------------------------------------------------------------#
        # Source "Western Michigan"
        #----------------------------------------------------------------------#
        
        # set source name
        source_name = "West Michigan"
        test_lookup_name = source_name
        
        # retrieve person
        test_person_qs = Person.look_up_person_from_name( test_lookup_name )
        test_person = test_person_qs.get()
        
        # check title
        test_value = test_person.title
        should_be = "nice day on the hill"
        error_string = "In " + me + "(): test title is " + str( test_value ) + ", should be " + str( should_be )
        self.assertEqual( test_value, should_be, error_string )            
        
        # get Article_Subject
        test_article_subject_qs = test_article_data.article_subject_set.filter( subject_type = Article_Subject.SUBJECT_TYPE_QUOTED )
        test_article_subject_qs = test_article_subject_qs.filter( person = test_person )
        
        # test Article_Subject title
        test_value = test_article_subject_qs.count()
        should_be = 0
        error_string = "In " + me + "(): should be no Article_Subject for \"West Michigan\" - count is \"" + str( test_value ) + "\", should be \"" + str( should_be ) + "\""
        self.assertEqual( test_value, should_be, error_string )
                    
    #-- END test method test_process_data_store_json() --#


#-- END test class ArticleCoderTest --#
