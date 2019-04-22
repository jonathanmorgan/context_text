"""
This file contains tests of the context_text Person model (and by extension
   Abstract_Person).

Functions tested:
- Person.look_up_person_from_name()
"""

# django imports
import django.test

# context_text imports
from context_text.models import Person
from context_text.tests.test_helper import TestHelper


class PersonModelTest( django.test.TestCase ):
    
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


#-- END test class PersonModelTest --#
