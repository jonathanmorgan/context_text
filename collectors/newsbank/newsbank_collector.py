'''
Copyright 2010-2013 Jonathan Morgan

This file is part of http://github.com/jonathanmorgan/context_text.

context_text is free software: you can redistribute it and/or modify it under the terms of the GNU Lesser General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.

context_text is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.

You should have received a copy of the GNU Lesser General Public License along with http://github.com/jonathanmorgan/context_text. If not, see http://www.gnu.org/licenses/.
'''

'''
This code file contains a class that can be used to pull down articles from
   Newsbank.  It currently works on a newspaper level - you tell it a
   newspaper, a date range, and a set of sections you want to include, if
   present, and it will loop over the dates, pulling in all articles from the
   specified sections.
'''

#================================================================================
# Imports
#================================================================================

# imports
import datetime
import gc
import os
import sys

# regular expression library.
import re

# six - Python 2 and 3 support
import six

#import urllib2
from six.moves import urllib
#import cookielib
from six.moves import http_cookiejar
from six.moves.urllib.request import build_opener
from six.moves.urllib.request import HTTPCookieProcessor
from six.moves.urllib.request import Request

# HTML parsing
from bs4 import BeautifulSoup
from python_utilities.beautiful_soup.beautiful_soup_helper import BeautifulSoupHelper

# collector parent class
from collector import Collector

# Newsbank helper
from newsbank_helper import NewsBankHelper

# django model for article
#os.environ.setdefault( "DJANGO_SETTINGS_MODULE", "research.settings" )
#sys.path.append( '/home/jonathanmorgan/Documents/django-dev/research' )
#from research.context_text.models import Article
#from research.context_text.models import Newspaper
from context_text.models import Article
from context_text.models import Newspaper
import django.db

#================================================================================
# Package constants-ish
#================================================================================

SOURCE_NEWS_BANK = "NewsBank"
PLACE_CODE_GRAND_RAPIDS_PRESS = "GRPB"
DEFAULT_DATE_FORMAT = "%Y-%m-%d"


#================================================================================
# NewsBankCollector class
#================================================================================


# define NewsBankCollector class.
class NewsBankCollector( Collector ):

    '''
    This class holds methods and instance variables specific to newsbank
       collecting.  For now, just includes the variables and methods needed to
       hold and initialize a NewsBankHelper instance.
    '''

    #============================================================================
    # Instance variables
    #============================================================================

    # instance of newsbank helper
    my_newsbank_helper = NewsBankHelper()
    newsbank_helper_debug = False
    
    # variables for URL and request generation
    protocol = "http"
    host = "infoweb.newsbank.com.proxy1.cl.msu.edu"
    user_agent = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.7; rv:7.0.1) Gecko/20100101 Firefox/7.0.1"
    
    # allow for missing dates?
    allow_missing_dates = True
    
    #============================================================================
    # Instance methods
    #============================================================================


    def get_newsbank_helper( self ):
    
        # return reference
        instance_OUT = None
        
        # get instance.
        instance_OUT = self.my_newsbank_helper
        
        # got one?
        if ( not( instance_OUT ) ):
        
            # no.  Initialize.
            self.initialize_newsbank_helper()
            
            # try again.  If nothing this time, nothing we can do.  Return it.
            instance_OUT = self.my_newsbank_helper
            
            # tell someone we made a new connection.
            self.output_debug( "*** in get_newsbank_helper(), made a new helper." )

        #-- END check to see if object is stored in instance --#

        return instance_OUT
    
    #-- END method get_url_opener() --#


    def initialize( self ):
    
        # initialize newsbank helper
        self.initialize_newsbank_helper()
    
    #-- END method initialize_url_opener() --#


    def initialize_newsbank_helper( self ):
    
        # declare variables
        helper_instance = None
        
        # create newsbank helper instance.
        helper_instance = NewsBankHelper()
        
        # place values in it.
        helper_instance.protocol = self.protocol
        helper_instance.host = self.host
        helper_instance.user_agent = self.user_agent
        helper_instance.DEBUG = self.DEBUG
        
        # store it in instance variable.
        self.my_newsbank_helper = helper_instance
        
    #-- END method initialize_url_opener() --#


#-- END class NewsBankCollector --#


#================================================================================
# NewsBankWebCollector class
#================================================================================


# define NewsBankWebCollector class.
class NewsBankWebCollector( NewsBankCollector ):

    '''
    This class is a helper for Collecting articles out of NewsBank.  It depends
       on urllib2, http_cookiejar, and datetime.
    '''

    #============================================================================
    # Instance variables
    #============================================================================

    # variables for collecting across a date range.
    start_date = ""
    end_date = ""
    dates_to_process = []
    place_code = ""
    newspaper_for_place = ""
    section_include_list = []
    section_exclude_list = []
    cookie_jar = None
    url_opener = None
    regex_section_name = None
    
    # error-handling.
    ignore_missing_issues = False
    
    # variables to control output.
    output_directory = "." # output directory, default to current directory.
    do_database_output = False
    do_files_output = True
    
    # instance of newsbank helper - inherited from NewsBankCollector parent.
    #my_newsbank_helper = NewsBankHelper()
    
    
    # variables for URL and request generation - protocol, host, and user-agent
    #    inherited from NewsBankCollector parent.
    #protocol = "http"
    #host = "infoweb.newsbank.com.proxy1.cl.msu.edu"
    #user_agent = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.7; rv:7.0.1) Gecko/20100101 Firefox/7.0.1"
    always_new_connection = False
    init_url = "http://infoweb.newsbank.com/best/usyearend"
    
    #============================================================================
    # Instance methods
    #============================================================================


    def add_date( self, date_IN ):
    
        '''
        This method accepts a string date in YYYY-MM-DD format.  Converts it into
           a datetime.datetime instance, then adds it to the list of dates to be
           processed.
        Preconditions: date must be in the format YYYY-MM-DD.
        Postconditions: adds the date to the list of dates to be processed.
           Returns the datetime instance.
        '''
        
        # return reference
        datetime_OUT = None
        
        # got a date?
        if ( date_IN ):
        
            # parse date.
            datetime_OUT = datetime.datetime.strptime( date_IN, DEFAULT_DATE_FORMAT )
            
            # add to array
            self.add_datetime( datetime_OUT )

        #-- END check to make sure we have a date. --#
        
        return datetime_OUT        
    
    #-- END method add_date() --#


    def add_datetime( self, datetime_IN ):
    
        '''
        Accepts a datetime.datetime instance, adds it to list of dates to
           process.
        Preconditions: date must be a datetime.datetime instance.
        Postconditions: Date passed in is added to the list.
        '''
        
        # declare variables
        my_date_list = None
    
        # got one?
        if ( datetime_IN ):
    
            # get date list
            my_date_list = self.dates_to_process
            
            # is date passed in already in the list?
            # for now, not looking...
    
            # add to date list
            self.dates_to_process.append( datetime_IN )
            
        #-- END check to make sure something passed in --#
    
    #-- END method add_datetime() --#


    def add_date_range( self, start_date_IN, end_date_IN ):
    
        '''
        This method accepts string start and end dates in YYYY-MM-DD format.
           Converts them into datetime.datetime instances, then adds the two
           dates and all in between to the list of dates to be processed.
        Preconditions: start and end dates must be in the format YYYY-MM-DD.
        Postconditions: adds the two dates and all in between to the list of
           dates to be processed.
        '''
        
        # return reference
        status_OUT = "Success!"
        
        # declare variables
        me = "add_date_range"
        start_date = None
        end_date = None
        current_date = None
        current_timedelta = ""
        
        # got a start date and an end date.
        if ( ( start_date_IN ) and ( end_date_IN ) ):

            # parse date strings into datetime.datetime.
            start_date = datetime.datetime.strptime( start_date_IN, DEFAULT_DATE_FORMAT )
            end_date = datetime.datetime.strptime( end_date_IN, DEFAULT_DATE_FORMAT )
        
            # loop over the dates, from start date to end date.
            current_date = start_date
            current_timedelta = end_date - current_date

            self.output_debug( "\n*** overall date difference = start: " + str( current_date ) + "; end: " + str( end_date ) + "; delta: " + str( end_date - current_date ) + "\n\n" )

            # loop over dates as long as difference between current and end is 0
            #    or greater.
            while ( current_timedelta.days > -1 ):

                self.output_debug( "\n*** current date difference = current: " + str( current_date ) + "; end: " + str( end_date ) + "; delta: " + str( current_timedelta ) + "\n\n" )
                
                # add current date to list.
                self.add_datetime( current_date )

                # add one to current date.
                current_date = current_date + datetime.timedelta( days = 1 )
                current_timedelta = end_date - current_date

            #-- END loop over dates --#
            
        else:
        
            status_OUT = "ERROR: One or both of dates in date range missing.  Could not process."
        
        #-- END check to make sure that we have start and end dates --#
        
        return status_OUT
    
    #-- END method add_date_range() --#


    def create_article_request( self, article_path_IN ):
    
        '''
        This method accepts an absolute path to an article.  This is the full
           path and query string part of the URL needed to access an article. It
           uses this path to generate a urllib2 Request instance for the path
           using the protocol and host specified in this instance.
        Returns the Request instance, or None if there was an error.        
        '''
        
        # return reference
        request_OUT = None
        
        # declare variables
        me = "create_article_request"
        nb_helper = None
        url_string = ""

        # get newsbank helper
        nb_helper = self.get_newsbank_helper()
        
        # got helper?
        if ( nb_helper ):

            # make sure we have a date and a place code.
            if ( article_path_IN ):
            
                # retrieve URL for date and place.
                request_OUT = nb_helper.create_article_request( article_path_IN )
                
            #-- END check to see if we have the things we need to generate request --#
        
        else:
        
            # error - no helper instance?
            self.output_debug( "=== In " + me + ": could not get newsbank helper, so couldn't create article request.\n" )
        
        #-- END check to see if we have newsbank helper. --#
        
        return request_OUT
    
    #-- END method create_article_request --#


    def create_issue_request( self, date_IN, place_code_IN ):
    
        '''
        This method accepts a date and a place code, uses them to generate a urllib2
           Request instance for that date and place.
        Returns the Request instance, or None if there was an error.        
        '''
        
        # return reference
        request_OUT = None
        
        # declare variables
        me = "create_issue_request"
        nb_helper = None
        url_string = ""
        date_string = ""

        # get newsbank helper
        nb_helper = self.get_newsbank_helper()
        
        # got helper?
        if ( nb_helper ):

            # make sure we have a date and a place code.
            if ( ( date_IN ) and ( place_code_IN ) ):
            
                # we do. Create a request.
                request_OUT = nb_helper.create_issue_request( date_IN, place_code_IN )
                
            #-- END check to see if we have the things we need to generate request --#

        else:
        
            # error - no helper instance?
            self.output_debug( "=== In " + me + ": could not get newsbank helper, so couldn't create issue request.\n" )
        
        #-- END check to see if we have newsbank helper. --#
        
        return request_OUT

    #-- END method create_issue_request --#


    def create_request( self, url_IN ):
    
        '''
        This method accepts a URLL, uses it to generate a urllib2 Request
           instance for that URL with headers configured to match information in
           this instance.
        Returns the Request instance, or None if there was an error.        
        '''
        
        # return reference
        request_OUT = None
        
        # declare variables

        # make sure we have a URL.
        if ( url_IN ):
        
            if ( self.debug == True ):
            
                # ouput the request.
                print( ">>> making request for URL: " + str( url_IN ) + "\n" )
            
            #-- END debug output --#
            
            # we do. Create a request.
            request_OUT = Request( url_IN, None, { self.HEADER_VARIABLE_NAME_USER_AGENT : self.user_agent } )

        #-- END check to see if we have the things we need to generate request --#
        
        return request_OUT
    
    #-- END method create_request --#


    def gather_items( self, *args, **kwargs ):
    
        '''
        This method accepts a start date, an end date, and a place code.
           Traverses the issues for each date from start to end for that place.

        For each issue/date, this method works in two parts:
        - First, it parses the HTML of a given date (or issue)'s page to
           store URLs for all the articles for that issue in an instance
           variable article queue (a map of docid to URL).
        - Second, it loops over the articles in the queue, loads and
           processes each, then clears the queue for the next issue.
        
        Preconditions: None.
        Postconditions: None. 
        '''
        
        # return reference
        status_OUT = "Success!"
        
        # declare variables
        date_list = None
        place_code_IN = None
        my_url_opener = None
        current_date = ""
        date_counter = -1
        current_request = None
        current_connection = None
        current_content = ""
        current_info = ""
        current_url = ""

        # make sure we have dates to process, and a place code.
        date_list = self.dates_to_process
        place_code_IN = self.place_code
        if ( ( date_list ) and ( len( date_list ) > 0 ) and ( place_code_IN ) ):
        
            # get url_opener
            my_url_opener = self.get_url_opener()

            # loop over the dates to process.
            print( "\n*** dates to process: " + str( len( date_list ) ) + "\n\n" )
            date_counter = 0

            for current_date in date_list:

                # update counter.
                date_counter += 1
                
                # store current date in instance.
                self.current_date = current_date

                print( "\n*** current date ( " + str( date_counter ) + " ): " + str( current_date ) + "\n\n" )

                # create request for current date's issue.
                current_request = self.create_issue_request( current_date, place_code_IN )
                
                # get connection to page.
                current_connection = my_url_opener.open( current_request )

                # pass connection on to method that deals with a given issue.
                self.process_issue( current_connection )
                
                # close the connection
                current_connection.close()
                
                # check to see if the array and the map are the same length (to
                #    see if there were any URLs where we could not parse out the
                #    docid).
                if ( self.debug == True ):
                
                    # map and URL list lengths are different.  Doh.
                    self.output_debug( "\ndocid-to-URL map size = " + str( len( self.id_to_item_map ) ) )
                    # + "):\n\t" + str( self.id_to_item_map ) + "\n" )
                    self.output_debug( "\narticle URL list size = " + str( len( self.item_list ) ) )
                    # + "):\n\t" + str( self.item_list ) + "\n" )

                    if ( len( self.id_to_item_map ) != len( self.item_list ) ):

                        # message that sizes are different
                        self.output_debug( "\nerror: map and list are different sizes.\n" )
                    
                    #-- END check to see if list and map are same size --#

                #-- END debug output --#

                # Now, check if there is anything in the queue.
                if ( len( self.id_to_item_map ) > 0 ):
                
                    # there is something in the map.  Process the article queue.
                    self.process_item_queue()
                
                #-- END check to see if we have articles to process. --#
                
                # memory management.
                gc.collect()
                django.db.reset_queries()
                
            #-- END loop over dates. --#

        #-- END check to see if we have the things we need to generate date-index URLs --#
        
        return status_OUT
    
    #-- END method gather_items --#


    def generate_issue_url( self, date_IN, place_code_IN ):
    
        '''
        This method accepts a date and a place code, uses them to generate a URL
           like the one below:
            
        http://infoweb.newsbank.com.proxy2.cl.msu.edu/iw-search/we/InfoWeb?p_product=NewsBank&p_theme=aggregated5&p_action=listissue&d_place=GRPB&f_source=GRPB&f_issue=2011-09-12&f_length=45&f_limit=no
        
        Returns the string URL.        
        '''
        
        # return reference
        url_OUT = ""
        
        # declare variables
        nb_helper = None

        # get newsbank helper
        nb_helper = self.get_newsbank_helper()

        
        # make sure we have a date and a place code.
        if ( ( date_IN ) and ( place_code_IN ) ):
        
            # generate URL
            url_OUT = nb_helper.generate_issue_url( date_IN, place_code_IN )
            
        #-- END check to see if we have the things we need to generate URL --#
        
        return url_OUT
    
    #-- END method generate_issue_url --#


    def get_newsbank_helper( self ):
    
        # return reference
        instance_OUT = None
        
        # get instance.
        instance_OUT = self.my_newsbank_helper
        
        # got one?
        if ( not( instance_OUT ) ):
        
            # no.  Initialize.
            self.initialize_newsbank_helper()
            
            # try again.  If nothing this time, nothing we can do.  Return it.
            instance_OUT = self.my_newsbank_helper
            
            # tell someone we made a new newsbank helper.
            self.output_debug( "*** in get_newsbank_helper(), made a new helper." )

        #-- END check to see if object is stored in instance --#

        return instance_OUT
    
    #-- END method get_url_opener() --#


    def get_regex_id( self ):
    
        # return reference
        regex_OUT = None
        
        # declare variables
        nb_helper = None
        
        # get newsbank helper
        nb_helper = self.get_newsbank_helper()
        
        # get compiled regex.
        regex_OUT = nb_helper.get_regex_id()

        # store it in instance just in case parent class needs it.
        self.regex_docid = regex_OUT

        return regex_OUT
    
    #-- END method get_regex_id() --#


    def get_regex_section_name( self ):
    
        # return reference
        regex_OUT = None
        
        # declare variables
        nb_helper = None
        
        # get newsbank helper
        nb_helper = self.get_newsbank_helper()
        
        # get compiled regex.
        regex_OUT = nb_helper.get_regex_section_name()

        # store it in instance just in case parent class needs it.
        self.regex_section_name = regex_OUT

        return regex_OUT
    
    #-- END method regex_section_name() --#


    def get_url_opener( self, do_create_new_IN = None ):
    
        # return reference
        url_opener_OUT = None
        
        # declare variables
        get_new_connection = False
        
        # set variable for new connection.  First, get default from instance variable.
        get_new_connection = self.always_new_connection
        
        # see if method call overrides instance variable setting.
        if ( do_create_new_IN != None ):
        
            # something passed in.  Use it.
            get_new_connection = do_create_new_IN
        
        #-- END check to see if method call overrides instance variable --#
        
        # get URL opener.
        url_opener_OUT = self.url_opener
        
        # got one?
        if ( ( not( url_opener_OUT ) ) or ( get_new_connection == True ) ):
        
            # no.  Initialize.
            self.initialize_url_opener()
            
            # try again.  If nothing this time, nothing we can do.  Return it.
            url_opener_OUT = self.url_opener
            
            # tell someone we made a new url opener.
            self.output_debug( "*** in get_url_opener(), made a new connection." )

        #-- END check to see if url_opener is stored in instance --#

        return url_opener_OUT
    
    #-- END method get_url_opener() --#


    def initialize( self ):
    
        # initialize URL opener.
        self.initialize_url_opener()
        
        # initialize newsbank helper
        self.initialize_newsbank_helper()
    
    #-- END method initialize_url_opener() --#


    def initialize_newsbank_helper( self ):
    
        # declare variables
        helper_instance = None
        
        # create newsbank helper instance.
        helper_instance = NewsBankHelper()
        
        # place values in it.
        helper_instance.protocol = self.protocol
        helper_instance.host = self.host
        helper_instance.user_agent = self.user_agent
        helper_instance.DEBUG = self.newsbank_helper_debug
        helper_instance.place_code = self.place_code
        helper_instance.newspaper_for_place = self.newspaper_for_place
        
        # store it in instance variable.
        self.my_newsbank_helper = helper_instance
        
    #-- END method initialize_url_opener() --#


    def initialize_url_opener( self ):
    
        # declare variables
        init_request = None
        current_connection = None
        
        # initialize URL opener.
        self.cookie_jar = http_cookiejar.CookieJar()
        self.url_opener = build_opener( HTTPCookieProcessor( self.cookie_jar ) )
        
        # do we have an init URL?
        if ( self.init_url ):
        
            # got one.  Create request.
            init_request = self.create_request( self.init_url )
            
            # access the init URL.
            current_connection = self.url_opener.open( init_request )
            current_connection.read()
            current_connection.close()
        
        #-- END check to see if init URL --#
    
    #-- END method initialize_url_opener() --#


    def process_article_list( self, bs_article_list_ul_IN ):

        '''
        Accepts a BeautifulSoup <ul> Tag instance.  Uses BS to retrieve all <li>
           tags from within, and then retrieves article information for each and
           adds it to article processing queue nested inside this instance.
        Preconditions: must have already pulled over the article list page and
           grabbed the appropriate <ul> for processing.
        '''    

        # declare variables
        me = "process_article_list"
        nb_helper = None
        article_url_list = None
        current_article_url = ""
        
        # got a <ul>?
        if ( bs_article_list_ul_IN ):
        
            # first, grab our newsbank helper
            nb_helper = self.get_newsbank_helper()
            
            # got one?
            if ( nb_helper ):
            
                # call the method to process the article list, return a list
                #    of URLs.
                article_url_list = nb_helper.process_article_list( bs_article_list_ul_IN )
                
                # got anything?
                if ( len( article_url_list ) > 0 ):
                
                    # we have some.  Loop and add to queue.
                    for current_article_url in article_url_list:
                    
                        # add each URL to the queue.
                        self.add_item_to_queue( current_article_url )
                    
                    #-- END loop over article URLs --#
                
                #-- END check to see if we have any articles in the list --#
            
            else:
            
                # error - no helper instance?
                self.output_debug( "=== In " + me + ": could not get newsbank helper, so couldn't process article list.\n" )

            #-- END check to make sure we have a helper. --#
            
        #-- END check to make sure we have a list to process. --#
    
    #-- END method process_article_list() --#


    def process_item( self, id_IN, item_IN ):

        '''
        Accepts an id and an item. Pulls in the body of the HTML, parses it,
           then stores it - can store file to file system, insert parsed record
           into database, or both.
        Preconditions: must have already pulled over the article list page and
           grabbed the appropriate <ul> for processing.
        '''    

        # declare variables
        current_docid = ""
        current_url = ""
        nb_helper = None
        my_url_opener = None
        current_request = None
        current_connection = None
        my_output_directory = ""
        current_output_path = ""
        current_output_file = None
        current_page_contents = ""
        current_status = ""
        article_counter = 0
                
        # make sure we have an ID and a URL
        if ( ( id_IN ) and ( item_IN ) ):
        
            # set variables
            current_docid = id_IN
            current_url = item_IN

            # get URL opener.
            my_url_opener = self.get_url_opener()
    
            # create request for current article.
            current_request = self.create_article_request( current_url )
                
            # get connection to page.
            current_connection = my_url_opener.open( current_request )
                
            # get HTML body.
            current_page_contents = current_connection.read()
                
            # *** Need to parse item, to make sure that it is valid.
            # Get NewsBankHelper
            nb_helper = self.get_newsbank_helper()
                
            # parse (and pass flag that says if we want to store in database)
            current_status = nb_helper.process_file_contents( current_docid, current_page_contents, self.do_database_output )
            
            # Success?
            if ( current_status == nb_helper.STATUS_SUCCESS ):
            
                # parse successful.  Do we output to file system?
                if ( self.do_files_output == True ):

                    # for now, just dump in files to the output directory specified in instance.open a file
                    my_output_directory = self.output_directory
                    current_output_path = my_output_directory + "/" + current_docid + ".html"
                    with open( current_output_path, "w" ) as current_output_file:
                        
                        # write the contents of the page to the file.
                        current_output_file.write( current_page_contents )
                    
                    #-- END with - automatically calls current_output_file.close() --#
                        
                #-- END check to see if we output to file system. --#
                    
            else:
                
                # ERROR - article did not parse.
                self.add_error( current_url, current_docid, current_status )
                
            #-- END check to see if article parsed successfully --#

        #-- END check to see if id and actual item passed in. --#                
    
    #-- END method process_item() --#


    def process_issue( self, connection_IN ):
    
        '''
        Accepts the connection to a page that contains links to all the
           articles in an issue.  Retrieves all sections, loops over them to
           build a list of article URLs that need to be processed.  Then, once
           list is built, loops over the list to process each article, calling
           process_item for each, passing it the URL of each individual
           article.
        postconditions: Does not close out connection.  Calling routine is
           responsible for that.
        '''
        
        # declare variables
        current_content = ""
        current_info = ""
        current_url = ""
        soup_instance = None
        articles_div = None
        current_element = None
        current_class_name = ""
        current_element_name = ""
        current_section = ""
        my_section_name_regex = None
        regex_results = None
    
        # make sure we have a connection.
        if ( connection_IN ):

            current_content = connection_IN.read()
            current_info = connection_IN.info()
            current_url = connection_IN.geturl()
    
            if ( self.debug == True ):
            
                self.debug_string += "\n*** Test Page URL:\n\n"
                self.debug_string += current_url
                self.debug_string += "\n*** Test Page info:\n\n"
                self.debug_string += str( current_info )
                self.debug_string += "\n*** Test Page HTML:\n\n"
                self.debug_string += current_content
                
            #-- END debug --#
        
            # first, use beautiful soup to get the div with id = "articles".
            # Initialize BeautifulSoup object with HTML string.
            soup_instance = BeautifulSoup( current_content )
            
            # use find method to get div whose ID is "articles"
            articles_div = soup_instance.find( 'div', id = "articles" )
            
            # got anything?
            if ( articles_div ):
            
                # loop over the child elements.  Should encounter a series of
                #    pairs of <h3> and <ul> elements.
                for current_element in articles_div:
                
                    # first, see what type of class we have.  Only need to deal with tags.
                    current_class_name = current_element.__class__.__name__
                    
                    # got a tag?
                    if ( current_class_name == "Tag" ):
                    
                        # get the name of the element.
                        current_element_name = current_element.name
                        
                        #self.output_debug( "- *** current element name: " + current_element_name + "\n" )
                        
                        # if element name is <h3>, get the section name.
                        if ( current_element_name.upper() == "H3" ):
                            
                            # we have <h3> - get section name (2nd child of <h3>).
                            current_section = current_element.contents[ 1 ]
                            
                            # remember to strip off label from front.
                            my_section_name_regex = self.get_regex_section_name()
                            regex_result = my_section_name_regex.findall( current_section )
                            current_section = regex_result[ 0 ].strip()
                            
                            self.output_debug( "- *** current section: " + current_section + "\n" )
                            
                        elif ( current_element_name.upper() == "UL" ):
                        
                            # this is a list of articles.  Need to parse the nested
                            #    <li> tags to get headline, URL.
                            self.output_debug( "- *** article list for section " + current_section + "\n" )
                            
                            # call the method to process the article list
                            self.process_article_list( current_element )
                        
                        #else:
                        
                            # not <h3> or <ul> - ignore.
                        
                        #-- END check to see what element we have.
                        
                    # else:
                    
                        # not a Tag.  Probably NavigableString (white space).  Output
                        #    details for debug, for now.
                        #self.output_debug( "- *** current Element (class = " + current_element.__class__.__name__ + "):\n" + str( current_element ) + "\n  *** END element\n" )
                        
                    #-- END check to see if Tag --#
                    
                #-- END loop over elements inside div with id = "articles". --#
                
            else:
                
                # Ignore missing issues?
                if ( self.ignore_missing_issues == False ):
                    
                    self.add_error( "", "", "Missing issue found for date " + str( self.current_date ) + "." )
                    
                else:
                    
                    self.output_debug( "Ignoring missing issues - missing issue found for date " + str( self.current_date ) + ".", me )
                    
                #-- END check to see if we are ignoring missing issues. --#
                
            #-- END check to see if anything in current issue. --#
            
        #-- END check to see if connection passed in. --#    
    
    #-- END method process_issue() --#
    
    
    def set_place_code( self, value_IN = "" ):
    
        # declare variables
        me = "set_place_code"
        newspaper_qs = None
        newspaper_count = -1
        newspaper_instance = None
        
        self.output_debug( "Setting place code to \"" + value_IN + "\"", me )
        
        # Store the place code in the instance variable.
        self.place_code = value_IN
        
        # Got a place code?
        if ( value_IN ):
            
            # We have a place code.  Try to find newspaper to match.
            newspaper_qs = Newspaper.objects.filter( newsbank_code = value_IN )
            
            # got any results?
            newspaper_count = newspaper_qs.count()
            
            if ( newspaper_count == 1 ):
                
                # got one.  Load it and store it.
                newspaper_instance = newspaper_qs.get()
                self.newspaper_for_place = newspaper_instance
                self.output_debug( "Found newspaper - " + str( newspaper_instance ), me )
                
            else:
                
                # Either multiple matching newspapers, or none.  Error either
                #    way.
                self.output_debug( "ERROR - newspaper count is not 1 ( " + str( newspaper_count ) + " ).", me )
                
            #-- END check to see if we found a newspaper. --#
            
        else:
            
            # emptying out value, so empty the current_newspaper.
            self.newspaper_for_place = None
            self.output_debug( "Empty place code set, so emptying out newspaper instance.", me )
            
        #-- END check to see if place code passed in. --#
    
    #-- END method set_place_code() --#
    

#-- END class NewsBankWebCollector --#


#================================================================================
# FileSystemCollector class
#================================================================================


# define FileSystemCollector class.
class FileSystemCollector( NewsBankCollector ):

    '''
    This class is a helper for parsing and storing articles retrieved in HTML
       form from NewsBank.
    '''

    #============================================================================
    # Constants-ish
    #============================================================================
    

    FORMAT_DATE_STRING = "%Y-%m-%d"
    HEADER_VARIABLE_NAME_USER_AGENT = "User-Agent"
    
    # details of HTML in an article
    HTML_CLASS_DOC_BODY = "docBody"
    HTML_CLASS_DOC_CITE = "docCite"
    HTML_CLASS_PUB_NAME = "pubName"
    HTML_CLASS_SOURCE_INFO = "sourceInfo"
    HTML_CLASS_MAIN_TEXT = "mainText"
    HTML_CLASS_TAG_NAME = "tagName"
    HTML_ID_OPEN_URL = "openUrl"
    HTML_TAG_NAME_SPAN = "span"
    
    # details of NewsBank tags
    NB_TAG_NAME_EDITION = "Edition:"
    NB_TAG_NAME_SECTION = "Section:"
    NB_TAG_NAME_PAGE = "Page:"
    NB_TAG_NAME_CORRECTION = "Correction:"
    NB_TAG_NAME_INDEX_TERMS = "Index Terms:"
    NB_TAG_NAME_RECORD_NUMBER = "Record Number:"

    # constants for holding what to do if duplicate found.
    DO_ON_DUPLICATE_UPDATE = "update" # update instead of insert.
    DO_ON_DUPLICATE_INSERT = "insert" # create a duplicate record.  Pow!
    DO_ON_DUPLICATE_SKIP = "skip" # skip and move on to next article.

    #============================================================================
    # Instance variables
    #============================================================================

    # variables for collecting all files within a directory and its children.
    directory_path = ""
    section_include_list = []
    section_exclude_list = []
    
    # variables for configuring processing
    check_for_duplicates = True
    do_on_duplicate = DO_ON_DUPLICATE_UPDATE
    duplicate_count = 0
    
    # instance of newsbank helper - inherited from NewsBankCollector
    #my_newsbank_helper = NewsBankHelper()

    
    #============================================================================
    # Instance methods
    #============================================================================


    def do_include_item( self, item_IN ):
    
        '''
        This method accepts an item.  Checks to see if it should be included or
           not.  Returns true or false.  Defaults to checking if item's ID can be
           identified by the ID regular expression.  If not, doesn't include
           item.
           
        Preconditions: Path to directory must actually point to a directory.
        Postconditions: None. 
        '''        

        # return reference
        include_item_OUT = False
        
        # declare variables
        regex_is_item = None
        regex_result = None
        
        # got an item?
        if ( item_IN ):

            # pull in the regex we'll use to test.
            regex_is_item = self.get_regex_id()
            
            # run it.
            regex_result = regex_is_item.findall( item_IN )
            
            # got anything?
            if ( len( regex_result ) > 0 ):
            
                # yes - this is an item.  Return True.
                include_item_OUT = True
                
            else:
            
                # no - not an item.  Return False.
                include_item_OUT = False
                
            #-- END chec to see if anything resulted from regex. --#

        else:
        
            # no item, so don't include nothing.
            include_item_OUT = False

        #-- END check to make sure we have an item. --#
            
        return include_item_OUT

    #-- END function do_include_item() --#
    

    def gather_items( self, *args, **kwargs ):
    
        '''
        This method uses a directory path and a place code stored in instance.
           Traverses the directory and all children looking for HTML files to
           parse.  For each file to process adds it to queue, saving article
           path instead of URL.
           
        Preconditions: Path to directory must actually point to a directory.
        Postconditions: None. 
        '''
        
        # return reference
        status_OUT = "Success!"
        
        # declare variables
        directory_path_IN = ""
        is_directory = False
            
        # make sure we have a directory in which we start and a place code.
        directory_path_IN = self.directory_path
        if ( directory_path_IN ):
        
            # first, see if the directory path is a directory.
            is_directory = os.path.isdir( directory_path_IN )
            
            if ( is_directory ):
            
                # It is a directory.  Now, need to call recursive function
                #    to descend into directory structure and add all HTML files
                #    it finds to the article queue.
                self.gather_items_from_directory( directory_path_IN )                
            
            #-- END check to see if directory path refers to a directory --#

        #-- END check to see if we have the things we need to generate URL --#
        
        return status_OUT
    
    #-- END method gather_items --#


    def gather_items_from_directory( self, directory_path_IN, *args, **kwargs ):
    
        '''
        Accepts a directory path.  First checks to make sure the directory is a
           directory.  Then, opens the directory and looks for:
           1) Directories inside this directory.  Uses os.walk to make a list of all child directories, If it finds any, it calls this
              function again, passing it the path to the child directory.
           2) HTML files (files that end in ".html").  If it finds any, adds
              the path to the HTML file to the article queue, then exits.
           
        Preconditions: Path to directory must actually point to a directory.
        Postconditions: Paths of all HTML files encountered are added to the
           article queue for processing. 
        '''
        
        # return reference
        status_OUT = "Success!"
        
        # declare variables
        directory_path_IN = ""
        is_directory = False
        directory = None
        current_directory_path = ""
        child_directories = None
        child_files = None
        current_file = ""
        include_item = False
        regex_get_id = None
        regex_result = None
        current_id = ""
            
        # make sure we have a directory in which we start and a place code.
        directory_path_IN = self.directory_path
        if ( directory_path_IN ):
        
            # first, see if the directory path is a directory.
            is_directory = os.path.isdir( directory_path_IN )
            
            if ( is_directory ):
            
                # It is a directory.  Use walk to traverse all directories,
                #    then use the glob package to just grab *.html files
                #    from each directory, add them to the queue.
                for current_directory_path, child_directories, child_files in os.walk( directory_path_IN ):
                
                    # for now, just print what we've found.
                    self.output_debug( "=== current directory === path: " + current_directory_path + "; file count: " + str( len( child_files ) ) + "\n" )

                    # are there child files?
                    if ( child_files ):
                    
                        # yes, there are child files.  Loop over them, looking
                        #    for file names that end in ".html".
                        for current_file in child_files:
                        
                            # initialize variables
                            include_item = False
                            
                            # should current item be included?
                            include_item = self.do_include_item( current_file )
                            
                            # got anything in result?
                            if ( include_item == True ):
                            
                                # got something.  Get ID, add item to queue.
                                regex_get_id = self.get_regex_id()
                                regex_result = regex_get_id.findall( current_file )
                                current_id = regex_result[ 0 ].strip()
                                self.add_item_to_queue( current_directory_path + "/" + current_file, current_id )
                            
                            #-- END check to see if we include current item. --#

                        #-- END loop over child files --#
                    
                    #-- END check to see if child files --#
                
                #-- END walk over directories starting in directory_path_IN --#
            
            #-- END check to see if directory path refers to a directory --#

        #-- END check to see if we have the things we need to generate URL --#
        
        return status_OUT
    
    #-- END method gather_items_from_directory --#


    def get_regex_id( self ):
    
        # return reference
        regex_OUT = None
        
        # get compiled regex.
        regex_OUT = self.regex_docid
        
        # got one?
        if ( not( regex_OUT ) ):
        
            # no.  Create and store.
            self.regex_docid = re.compile( "(.*)\.html$", re.IGNORECASE )
            
            # try again.  If nothing this time, nothing we can do.  Return it.
            regex_OUT = self.regex_docid
            
        #-- END check to see if regex is stored in instance --#

        return regex_OUT
    
    #-- END method get_regex_id() --#


    def process_article_tag_list( self, tag_element_list_IN, article_instance_IN ):

        '''
        Accepts the contents of the top-level sourceInfo element that contains
           the tags for a given article.  Parses out the different tags, adds
           them to fields in article_instance_IN if known, if not, builds up a 
           string that contains unknown name-value pairs, for auditing.
           
        Preconditions: You must have already opened and read the file, and have
           already used BeautifulSoup to pull out the div that contains the tags.
           
        Postconditions: Article model is returned updated based on the tags
           in the tag list passed in.  Article instance is not saved.  That is
           the responsibility of the calling routine.
        '''
        
        # return reference
        article_OUT = None

        # declare variables
        nb_helper = None
        
        # get NewsBank helper
        nb_helper = self.get_newsbank_helper()
        
        # process the article tag list.
        article_OUT = nb_helper.process_article_tag_list( tag_element_list_IN, article_instance_IN )
                
        return article_OUT
                
    #-- END method process_article_tag_list() --#
                
                
    def process_file_contents( self, id_IN, contents_IN ):

        '''
        Accepts the contents of a file (the HTML of a NewsBank article).  Uses
           BeautifulSoup to process contents, build a django Article instance
           from context_text models, and store the article in the database.
           
        Preconditions: You must have already opened and read the file, so you can
           pass the contents to this program.  Duplicate check assumes you will
           only have one copy of a duplicate article.  If you use the INSERT
           duplicate action, you'll have to clean that mess up yourself.
           
        Postconditions: Article model will insert contents of this page into
           database as long as no fatal parsing errors.  If duplicate found,
           either updates existing record, inserts another new record with
           same ID, or skips record.  If you insert, then try to update that
           same record again in a subsequent run, this code will throw an
           exception.  Allows duplication, but you have to clean it up in the
           django admin.
        '''
        
        # return reference
        status_OUT = "Success!"

        # declare variables
        nb_helper = None
        
        # get NewsBank helper
        nb_helper = self.get_newsbank_helper()
        
        # process the article tag list.
        status_OUT = nb_helper.process_file_contents( id_IN, contents_IN )

        return status_OUT
                
    #-- END method process_file_contents() --#
                
                
    def process_item( self, id_IN, item_IN ):

        '''
        Accepts an ID and the path to an article that we need to parse and insert
           into the database.  Opens file, creates instance of article model, and
           uses BeautifulSoup to pull information out of HTML and place them in
           model.
        Preconditions: item passed in must be the path of a file, and that file
           must contain Newsbank article HTML.
        '''    

        # return reference
        status_OUT = "Success!"
        
        # declare variables
        me = "process_item"
        item_file = None
        was_file_opened = False
        file_contents = ""
        status_message = ""
        
        # got an id and an item?
        if ( ( id_IN ) and ( item_IN ) ):
        
            # Try/catch with exception handling specific to this implementation.
            try:
                
                # first, need to read in article HTML.
                with open( item_IN, 'r' ) as item_file:
    
                    # file open succeeded
                    was_file_opened = True
                    
                    # read contents as string.
                    file_contents = item_file.read()
                    
                    # process contents of file
                    status_OUT = self.process_file_contents( id_IN, file_contents )
                            
                #-- END processing of file. --#
                
                # for now, just print what we've found.
                #self.output_debug( "=== current article ===\n\t- id: " + id_IN + ";\n\t- item: " + str( item_IN ) + "\n" )
                
            except AttributeError as ae:
            
                # exception.  Log it.
                status_message = "ERROR: AttributeError or child caught in FileSystemCollector." + me + "."
                self.add_error( item_IN, id_IN, status_message, ae )
                status_OUT = status_message
                
            except Exception as e:
            
                # unknown exception.
                status_message = "ERROR: Exception caught in FileSystemCollector." + me + "."
                self.add_error( item_IN, id_IN, status_message, e )
                status_OUT = status_message
            
            #-- END try/except block.

        #-- END check to make sure we have an item to process. --#
        
        return status_OUT
    
    #-- END method process_item() --#


#-- END class FileSystemCollector --#