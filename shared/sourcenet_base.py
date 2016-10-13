from __future__ import unicode_literals

'''
Copyright 2010-2016 Jonathan Morgan

This file is part of http://github.com/jonathanmorgan/sourcenet.

sourcenet is free software: you can redistribute it and/or modify it under the terms of the GNU Lesser General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.

sourcenet is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.

You should have received a copy of the GNU Lesser General Public License along with http://github.com/jonathanmorgan/sourcenet. If not, see http://www.gnu.org/licenses/.
'''

#===============================================================================
# imports (in alphabetical order by package, then by name)
#===============================================================================


# python base imports
import calendar
#from datetime import date
import datetime

# django classes
from django.contrib.auth.models import User
from django.db.models import Q

# python_utilities
from python_utilities.parameters.param_container import ParamContainer
from python_utilities.rate_limited.basic_rate_limited import BasicRateLimited

#===============================================================================
# classes (in alphabetical order by name)
#===============================================================================

class SourcenetBase( BasicRateLimited ):


    #---------------------------------------------------------------------------
    # CONSTANTS-ish
    #---------------------------------------------------------------------------

    # status constants
    STATUS_SUCCESS = "Success!"
    STATUS_ERROR_PREFIX = "Error: "
    
    # django_config properties
    DJANGO_CONFIG_APPLICATION_SOURCENET_DB_ADMIN = "sourcenet-db-admin"
    DJANGO_CONFIG_PROP_DB_USERNAME = "db_username"
    DJANGO_CONFIG_PROP_DB_PASSWORD = "db_password"
    DJANGO_CONFIG_PROP_DB_HOST = "db_host"
    DJANGO_CONFIG_PROP_DB_PORT = "db_port"
    DJANGO_CONFIG_PROP_DB_NAME = "db_name"    
    
    # defaults
    DEFAULT_DATE_FORMAT = "%Y-%m-%d"
    
    # standard date parameter names
    PARAM_SINGLE_DATE = 'single_date'
    PARAM_START_DATE = 'start_date'   # publication date - articles will be included that were published on or after this date.
    PARAM_END_DATE = 'end_date'   # publication date - articles will be included that were published on or before this date.
    PARAM_DATE_RANGE = 'date_range'   # For date range fields, enter any number of paired date ranges, where dates are in the format YYYY-MM-DD, dates are separated by the string " to ", and each pair of dates is separated by two pipes ("||").  Example: 2009-12-01 to 2009-12-31||2010-02-01 to 2010-02-28

    
    # network selection parameters we expect.
    PARAM_NEWSPAPER_ID = "newspaper_id"  # ID of newspaper whose articles we want.
    PARAM_NEWSPAPER_NEWSBANK_CODE = "newspaper_newsbank_code"  # Newsbank Code of newspaper whose articles we want.
    PARAM_NEWSPAPER_INSTANCE = "newspaper"  # Newspaper instance whose articles we want.
    PARAM_NEWSPAPER_ID_IN_LIST = "newspaper_id_in_list"  # list of IDs of Newspapers whose articles we want.
    PARAM_PUBLICATION_LIST = 'publications'   # list of IDs of newspapers you want included.
    PARAM_TOPIC_LIST = 'topics'   # list of IDs of topics whose data you want included.
    PARAM_SECTION_NAME = 'section_name'   # list of tag values that you want included.
    PARAM_SECTION_NAME_LIST = 'section_name_list'  # list of names of sections you want included articles to be members of.
    PARAM_SECTION_LIST = 'section_list'   # alternate for list of names of sections you want included articles to be members of.
    PARAM_TAGS_IN_LIST = "tags_in_list_IN"  # comma-delimited string list of tag values that you want included.
    PARAM_TAGS_NOT_IN_LIST = "tags_not_in_list_IN"  # comma-delimited string list of tag values that you want excluded.
    PARAM_TAG_LIST = 'tags_list'   # comma-delimited string list of tag values that you want included.
    PARAM_UNIQUE_ID_LIST = 'unique_identifiers'   # list of unique identifiers of articles whose data you want included.
    PARAM_ARTICLE_ID_LIST = 'article_id_list'   # list of ids of articles whose data you want included.
    PARAM_CUSTOM_ARTICLE_Q = 'custom_article_q'  # pre-built Q() instance to use to filter articles.  Can be anything you want!
    PARAM_GET_DISTINCT_RECORDS = "get_distinct_records"  # For whatever model is being queried or filtered, only get one instance of a record that has a given ID.

    # Article_Data filter parameters.
    PARAM_CODERS = "coders"
    PARAM_CODER_TYPE_FILTER_TYPE = "coder_type_filter_type"
    PARAM_CODER_TYPES_LIST = "coder_types_list"
    

    # constants for parsing date range string
    PARAM_DATE_RANGE_ITEM_SEPARATOR = '||'
    PARAM_DATE_RANGE_DATE_SEPARATOR = ' to '
    PARAM_DATE_RANGE_DATE_FORMAT = '%Y-%m-%d'
    
    # params for processing articles
    PARAM_APPLY_TAGS_LIST = 'apply_tags_list'

    # types of params.
    PARAM_TYPE_INT = ParamContainer.PARAM_TYPE_INT
    PARAM_TYPE_LIST = ParamContainer.PARAM_TYPE_LIST
    PARAM_TYPE_STRING = ParamContainer.PARAM_TYPE_STRING

    # Dictionary of parameters to their types, for use in debug method.
    PARAM_NAME_TO_TYPE_MAP = {}

    # variables for choosing yes or no.
    CHOICE_YES = 'yes'
    CHOICE_NO = 'no'

    # choices for yes or no decision.
    CHOICES_YES_OR_NO_LIST = [
        ( CHOICE_NO, "No" ),
        ( CHOICE_YES, "Yes" )
    ]

    # automated coder user
    CODER_USERNAME_AUTOMATED = "automated"
    CODER_USER_AUTOMATED = None
    
    # ground truth coding user
    CODER_USERNAME_GROUND_TRUTH = "ground_truth"
    CODER_USER_GROUND_TRUTH = None
        

    #============================================================================
    # instance variables
    #============================================================================


    # request variables
    request = None
    parameters = None
    
    # rate-limiting
    is_rate_limited = False
    
    
    #-----------------------------------------------------------------------------
    # class methods
    #-----------------------------------------------------------------------------


    @classmethod
    def get_automated_coding_user( cls, create_if_no_match_IN = True, *args, **kwargs ):
    
        '''
        Can't reference django models in class context anymore in models files:
            http://stackoverflow.com/questions/25537905/django-1-7-throws-django-core-exceptions-appregistrynotready-models-arent-load
        So, this method gets User instance for automated user username instead.
        '''
        
        # return reference
        user_OUT = None

        # declare variables
        temp_user = None
        temp_password = ""
        
        # User already retrieved?
        if ( cls.CODER_USER_AUTOMATED == None ):
        
            # use a try to detect if no automated user.
            try:
            
                # get user
                temp_user = User.objects.get( username = cls.CODER_USERNAME_AUTOMATED )
                
                # store it
                cls.CODER_USER_AUTOMATED = temp_user
                
            except:
            
                # exception in get() call - create and return new user?
                if ( create_if_no_match_IN == True ):
                
                    # set password to current time stamp.
                    temp_password = datetime.datetime.utcnow()
                    temp_password = calendar.timegm( temp_password.timetuple() )
                    temp_password = str( temp_password )
                
                    # create user with username, password, no email.
                    temp_user = User.objects.create_user( cls.CODER_USERNAME_AUTOMATED, None, temp_password )
                    
                    # add information to user.
                    temp_user.first_name = "Automated"
                    temp_user.last_name = "Processing"
                    
                    # save user.
                    temp_user.save()
                    
                    # store user in class
                    cls.CODER_USER_AUTOMATED = temp_user
                    
                #-- END check to see if we create a user. ---#
            
            #-- END try/except for looking up automated user. --#
            
        #-- END check to see if user already stored in class. --#

        # return it.
        user_OUT = cls.CODER_USER_AUTOMATED

        return user_OUT
        
    #-- END class method get_automated_coding_user() --#
    
    
    @classmethod
    def get_ground_truth_coding_user( cls, create_if_no_match_IN = True, *args, **kwargs ):
    
        '''
        Can't reference django models in class context anymore in models files:
            http://stackoverflow.com/questions/25537905/django-1-7-throws-django-core-exceptions-appregistrynotready-models-arent-load
        So, this method gets User instance for ground truth user username instead.
        '''
        
        # return reference
        user_OUT = None

        # declare variables
        temp_user = None
        temp_password = ""
        
        # User already retrieved?
        if ( cls.CODER_USER_GROUND_TRUTH == None ):
        
            # use a try to detect if no ground truth user.
            try:
            
                # get user
                temp_user = User.objects.get( username = cls.CODER_USERNAME_GROUND_TRUTH )
                
                # store it
                cls.CODER_USER_GROUND_TRUTH = temp_user
                
            except:
            
                # exception in get() call - create and return new user?
                if ( create_if_no_match_IN == True ):
                
                    # set password to current time stamp.
                    temp_password = datetime.datetime.utcnow()
                    temp_password = calendar.timegm( temp_password.timetuple() )
                    temp_password = str( temp_password )
                
                    # create user with username, password, no email.
                    temp_user = User.objects.create_user( cls.CODER_USERNAME_GROUND_TRUTH, None, temp_password )
                    
                    # add information to user.
                    temp_user.first_name = "Coding"
                    temp_user.last_name = "Ground Truth"
                    
                    # save user.
                    temp_user.save()
                    
                    # store user in class
                    cls.CODER_USER_GROUND_TRUTH = temp_user
                    
                #-- END check to see if we create a user. ---#
            
            #-- END try/except for looking up ground truth user. --#
            
        #-- END check to see if user already stored in class. --#

        # return it.
        user_OUT = cls.CODER_USER_GROUND_TRUTH

        return user_OUT
        
    #-- END class method get_ground_truth_coding_user() --#
    
    
    @classmethod
    def parse_multiple_date_range_string( cls, date_range_IN ):
        
        """
            Method: parse_date_range()
            
            Purpose: Accepts a date range string, parses it, and returns a list
               of date ranges that need to be OR-ed together.  The text in date
               range field can be parsed out into date ranges - semi-colon
               delimited, " to " between dates that bound a range.  Could add
               more complexity later.  As soon as we start doing that, need an
               object for date ranges.  For now, not so much.

            Ex.:
                2009-12-01 to 2009-12-31;2010-02-01 to 2010-02-28
                
            Params:
            - date_range_IN - date range string we need to parse.
            
            Returns:
            - List of Lists - List of pairs of date instances (two item lists) that are to be OR-ed together.
        """
        
        # return reference
        date_range_list_OUT = []
        
        # declare variables
        date_range_list = None
        date_range_string = ''
        date_range_date_list = ''
        from_string = ''
        to_string = ''
        from_date = None
        to_date = None
        date_pair_list = None
        
        # got a date range value?
        if ( ( date_range_IN is not None ) and ( date_range_IN != '' ) ):
        
            # got something - break it up on ";"
            date_range_list = date_range_IN.split( cls.PARAM_DATE_RANGE_ITEM_SEPARATOR )

            # iterate over list, splitting each item on " to " and then if two
            #    things found, place them in a list and append that list to the
            #    output list.
            for date_range_string in date_range_list:

                # split on " to "
                date_range_date_list = date_range_string.split( cls.PARAM_DATE_RANGE_DATE_SEPARATOR )

                # grab dates
                from_string = date_range_date_list[ 0 ]
                to_string = date_range_date_list[ 1 ]

                # make sure we have two values.  If not, do nothing.
                if ( ( from_string != '' ) and ( to_string != '' ) ):

                    # convert to date instances
                    from_date = datetime.datetime.strptime( from_string, cls.PARAM_DATE_RANGE_DATE_FORMAT )
                    from_date = from_date.date()
                    to_date = datetime.datetime.strptime( to_string, cls.PARAM_DATE_RANGE_DATE_FORMAT )
                    to_date = to_date.date()

                    # put the date()s in a list.
                    date_pair_list = [ from_date, to_date ]

                    # add list to output list.
                    date_range_list_OUT.append( date_pair_list )

                #-- END check to see if we have two values. --#

            #-- END loop over date range strings --#
        
        #-- END check to see if date range value set. --#
        
        return date_range_list_OUT

    #-- END parse_multiple_date_range_string() --#


    #---------------------------------------------------------------------------
    # __init__() method
    #---------------------------------------------------------------------------


    def __init__( self ):

        # call parent's __init__()
        super( SourcenetBase, self ).__init__()

        # declare variables
        self.request = None
        self.parameters = ParamContainer()
        
        # rate limiting
        self.is_rate_limited = False

        # define parameters - should do this in "child.__init__()".
        self.define_parameters( self.PARAM_NAME_TO_TYPE_MAP )        
        
        # set logger name (for LoggingHelper parent class: (LoggingHelper --> BasicRateLimited --> SourcenetBase).
        self.set_logger_name( "sourcenet.shared.sourcenet_base" )
        
    #-- END method __init__() --#


    #---------------------------------------------------------------------------
    # instance methods, in alphabetical order
    #---------------------------------------------------------------------------


    def debug_parameters( self ):

        # return reference
        string_OUT = ''

        # declare variables
        my_params = None
        
        # call get_param_as_list()
        my_params = self.get_param_container()
        string_OUT = my_params.debug_parameters()

        return string_OUT

    #-- end method debug_parameters() ------------------------------------------


    def define_parameters( self, param_name_to_type_mape_IN = None ):

        # return reference
        params_OUT = None

        # declare variables
        my_param_container = None
        request_IN = None
        expected_params = None
        param_name = ''
        param_type = ''

        # retrieve ParamContainer instance
        my_param_container = self.get_param_container()
        
        # get anything back?
        if ( my_param_container ):
        
            # got a name-to-type map?
            if ( param_name_to_type_mape_IN is not None ):
            
                # get list of expected params
                expected_params = param_name_to_type_mape_IN
                
                # loop over expected parameters, grabbing each and adding it to the
                #    parameter container.
                for param_name, param_type in expected_params.items():
    
                    # define in parameter container.
                    my_param_container.define_parameter( param_name, param_type )
    
                #-- END loop over expected parameters --#
                
            #-- END check to see if we have a map of param names to types. --#

        #-- END check to see if we have a request --#
        
        # set parameter container back.
        self.set_param_container( my_param_container )
        
        params_OUT = self.get_param_container()

        return params_OUT

    #-- end method define_parameters() ------------------------------------------


    def get_param( self, param_name_IN, default_IN = None ):
        
        # return reference
        value_OUT = ""
        
        # declare variables
        my_params = None
        
        # try to retrieve value - for now, reference nested parameters.
        my_params = self.get_param_container()
        value_OUT = my_params.get_param( param_name_IN, default_IN, delimiter_IN )
        
        return value_OUT
        
    #-- END method get_param() --#
    

    def get_param_as_list( self, param_name_IN, default_IN = [], delimiter_IN = ',' ):
        
        # return reference
        list_OUT = []
        
        # declare variables
        my_params = None
        
        # call get_param_as_list()
        my_params = self.get_param_container()
        list_OUT = my_params.get_param_as_list( param_name_IN, default_IN, delimiter_IN )
        
        return list_OUT

    #-- END method get_param_as_list() --#
    

    def get_param_as_str( self, param_name_IN, default_IN = '' ):
        
        # return reference
        value_OUT = ""
        
        # declare variables
        my_params = None
        
        # call get_param_as_str()
        my_params = self.get_param_container()
        value_OUT = my_params.get_param_as_str( param_name_IN, default_IN )
        
        return value_OUT
        
    #-- END method get_param_as_str() --#
    

    def get_param_container( self ):
        
        # return reference
        value_OUT = None
        
        # try to retrieve value - for now, reference nested request.POST
        value_OUT = self.parameters
        
        # got one?
        if ( value_OUT is None ):
        
            # no.  Make one, store it, then return it.
            value_OUT = ParamContainer()
            self.set_param_conatiner( value_OUT )

            # return container.
            value_OUT = self.parameters
        
        #-- END check to see if param container --#
        
        return value_OUT
        
    #-- END method get_param_container() --#
    

    def parse_date_range( self, date_range_IN ):
        
        """
            Method: parse_date_range()
            
            Purpose: Accepts a date range string, parses it, and returns a list
               of date ranges that need to be OR-ed together.  The text in date
               range field can be parsed out into date ranges - semi-colon
               delimited, " to " between dates that bound a range.  Could add
               more complexity later.  As soon as we start doing that, need an
               object for date ranges.  For now, not so much.

            Ex.:
                2009-12-01 to 2009-12-31;2010-02-01 to 2010-02-28
                
            Params:
            - date_range_IN - date range string we need to parse.
            
            Returns:
            - List of Lists - List of pairs of date instances (two item lists) that are to be OR-ed together.
        """
        
        # return reference
        date_range_list_OUT = []
        
        # call class method.
        date_range_list_OUT = SourcenetBase.parse_multiple_date_range_string( date_range_IN )
        
        return date_range_list_OUT

    #-- END parse_date_range() --#


    def set_param_container( self, param_container_IN ):

        """
            Method: set_param_container()

            Purpose: accepts a ParamContainer instance, stores it in instance.

            Params:
            - param_container_IN - ParamContainer instance.
        """

        # declare variables

        # store the parameter container
        self.parameters = param_container_IN

    #-- END method set_param_container() --#


    def set_request( self, request_IN ):

        """
            Method: set_request()

            Purpose: accepts a request, stores it in instance, then grabs the
                POST from the request and stores that as the params.

            Params:
            - request_IN - django HTTPRequest instance.
        """

        # declare variables
        params_IN = None
        my_param_container = None

        # got a request?
        if ( request_IN ):
        
            # store the request
            self.request = request_IN

            # get the parameter container
            my_param_container = self.get_param_container()

            # set request in container.
            my_param_container.set_request( request_IN )

        #-- END check to see if we have a request --#

    #-- END method set_request() --#


    def store_parameters( self, params_IN ):

        """
            Method: set_param_container()

            Purpose: accepts a ParamContainer instance, stores it in instance.

            Params:
            - param_container_IN - ParamContainer instance.
        """

        # declare variables
        my_param_container = None

        # get the parameter container
        my_parameter_container = self.get_param_container()
        
        # store parameters in the container.
        my_parameter_container.set_parameters( params_IN )

    #-- END method store_parameters() --#


#-- END class SourcenetBase --#