'''
Copyright 2010-2013 Jonathan Morgan

This file is part of http://github.com/jonathanmorgan/sourcenet.

sourcenet is free software: you can redistribute it and/or modify it under the terms of the GNU Lesser General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.

sourcenet is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.

You should have received a copy of the GNU Lesser General Public License along with http://github.com/jonathanmorgan/sourcenet. If not, see http://www.gnu.org/licenses/.
'''

'''
This code file contains a class that implements functions for interacting with
   the online database of Newsbank.  It mostly includes methods for building and
   connecting to URLs that represent issues of newspapers and articles within an
   issue, and then Beautiful Soup code for interacting with the HTML contents of
   those pages once they are retrieved.  The actual work of retrieving pages is
   outside the scope of this class.
'''

#================================================================================
# Imports
#================================================================================

# imports
import cookielib
import datetime
import os
import sys
import urllib2
from xml.sax import saxutils

# regular expression library.
import re

# HTML parsing
from bs4 import BeautifulSoup
from bs4 import NavigableString
from python_utilities.beautiful_soup.beautiful_soup_helper import BeautifulSoupHelper

# django model for article
#os.environ.setdefault( "DJANGO_SETTINGS_MODULE", "research.settings" )
#sys.path.append( '/home/jonathanmorgan/Documents/django-dev/research' )
#from sourcenet.models import Article
from sourcenet.models import Article

#================================================================================
# Package constants-ish
#================================================================================


SOURCE_NEWS_BANK = "NewsBank"
PLACE_CODE_GRAND_RAPIDS_PRESS = "GRPB"


#================================================================================
# NewsBankCollector class
#================================================================================

# define NewsBankCollector class.
class NewsBankHelper( object ):

    '''
    This class is a helper for Collecting articles out of NewsBank.  It implements
       functions for interacting with the online database of Newsbank.  It mostly
       includes methods for building and connecting to URLs that represent issues
       of newspapers and articles within an issue, and then Beautiful Soup code
       for interacting with the HTML contents of those pages once they are
       retrieved.  The actual work of retrieving pages is outside the scope of
       this class.
    Preconditions: It depends on cookielib, datetime, os, re, sys, urllib2 and
       BeautifulSoup 3.
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
    
    # status constants
    STATUS_SUCCESS = "Success!"
    

    #============================================================================
    # Instance variables
    #============================================================================

    
    # debug
    debug = False

    # variables for collecting across a date range.
    regex_docid = None
    regex_section_name = None
    regex_white_space = re.compile(r'\s+')
    
    # variables for URL and request generation
    place_code = ""
    newspaper_for_place = None
    protocol = "http"
    host = "infoweb.newsbank.com"
    user_agent = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.7; rv:7.0.1) Gecko/20100101 Firefox/7.0.1"
    always_new_connection = True
    
    # variables for configuring processing
    check_for_duplicates = True
    do_on_duplicate = DO_ON_DUPLICATE_UPDATE
    duplicate_count = 0
    
    # variable to hold BeautifulSoupHelper, if needed.
    bs_helper = None

    
    #============================================================================
    # Instance methods
    #============================================================================


    def clean_article_body( self, bs_body_tag_IN ):

        '''
        Accepts article body nested in BeautifulSoup instance (assumes it is the
           body copy of the article, perhaps with some HTML mixed in, but not the
           full HTML of the article).  Looks for paragraph breaks (two <br> tags
           on two subsequent lines), uses these to split document into a list of
           paragraphs, stripping all HTML out of each paragraph and swapping
           contiguous runs of white space more than 1 character long for a single
           space.  Counts paragraphs, then wraps each paragraph string in a <p>
           tag with paragraph number stored in "id" attribute of <p> tag, then
           combines all paragraph strings into one string and returns the string.
           
        Preconditions: Article body must have been parsed into a BeautifulSoup
            element instance.  Shouldn't be the entire HTML, just the article
            body.
           
        Postconditions: Returns article body as a string with all HTML removed
           except for <p> tags wrapping each paragraph, and all runs of white
           space longer than 1 character converted to a single space.  Does not
           alter the BeautifulSoup instance passed in.
           
        Parameters:
        - bs_body_element_IN - BeautifulSoup 4 element instance that contains HTML body copy of article.
        
        Returns:
        - String - Returns article with all HTML removed except for <p> tags wrapping each paragraph, and all runs of white space longer than 1 character converted to a single space.
        '''
        
        # return reference
        body_string_OUT = ""
        
        # declare variables
        my_bs_helper = None
        paragraph_list = []
        current_element_list = []
        current_name = ""
        paragraph_counter = -1
        paragraph_text = ""
        paragraph_text_list = []
        current_paragraph_text = ""
        bs_helper = None
        graf_counter = -1
        graf_count = -1
        article_string = ""
        
        # initialize BS helper
        my_bs_helper = self.get_bs_helper()
        
        # loop over the contents of this div.
        paragraph_counter = 1
        current_element_list = []
        for current_content in bs_body_tag_IN.contents:
        
            # get name of element - <br> elements are divider between paragraphs.
            current_name = current_content.name
            
            # see if name is br.
            if ( current_name == "br" ):
            
                # yes - paragraph break!
                
                #output a message, and the string contents of the tag (just in case).
                #print( "=======> paragraph break! - End of paragraph " + str( paragraph_counter ) + ".  HTML element Contents: \"" + str( current_content ) + "\"" )
                
                # process elements of previous paragraph, add to paragraph list.
                paragraph_text_list = []
                for paragraph_element in current_element_list:
                
                    # convert current element to just text.  Is it NavigableString?
                    if ( isinstance( paragraph_element, NavigableString) ):
                    
                        # it is NavigableString - convert it to string.
                        current_paragraph_text = unicode( paragraph_element )
                    
                    else:
                    
                        # not text - just grab all the text out of it.
                        #current_paragraph_text = ' '.join( paragraph_element.findAll( text = True ) )
                        current_paragraph_text = paragraph_element.get_text( " ", strip = True )
                        
                    #-- END check to see if current element is text. --#
        
                    # clean up - convert HTML entities
                    current_paragraph_text = my_bs_helper.convert_html_entities( current_paragraph_text )
                    
                    # strip out extra white space
                    current_paragraph_text = ' '.join( current_paragraph_text.split() )
                    
                    # got any paragraph text?
                    current_paragraph_text = current_paragraph_text.strip()
                    if ( ( current_paragraph_text != None ) and ( current_paragraph_text != "" ) ):
                    
                        # yes.  Add to paragraph text.
                        paragraph_text_list.append( current_paragraph_text )
                        
                    #-- END check to see if any text. --#
                
                #-- END loop over paragraph elements. --#
                
                # convert paragraph list to string
                paragraph_text = ' '.join( paragraph_text_list )
                
                # got any text in this paragraph?
                if ( ( paragraph_text != None ) and ( paragraph_text != "" ) ):
        
                    # yes - Add paragraph text to paragraph_list
                    paragraph_list.append( paragraph_text )
                            
                    # increment paragraph counter
                    paragraph_counter += 1
                    
                #-- END check to see if paragraph text. --#
        
                # output paragraph text.
                #print( "=======> paragraph text: " + paragraph_text )
                
                # reset current_element_list
                current_element_list = []
            
            else: 
            
                # no. Add current element to list
                current_element_list.append( current_content )
            
            #-- END check to see if <br> --#
        
        #-- END loop over contents. --#
        
        #print( "\n\n\n~~~~~~~~~~ After paragraph loop:\n\n\n" )
        
        # how many paragraphs?
        graf_count = len( paragraph_list )
        if ( graf_count > 0 ):
        
            # Got at least one. loop over paragraphs
            graf_counter = 0
            body_string_OUT = ""
            for graf in paragraph_list:
            
                # increment counter, output paragraph.
                graf_counter += 1
                
                # print our paragraphs in paragraph list.
                #print( "- graf " + str( graf_counter ) + ": \"" + graf + "\"" )
                
                # put the paragraph in <p> tags.
                current_paragraph_text = "<p id=\"" + str( graf_counter ) + "\">" + graf + "</p>"
                
                # add to article text.
                body_string_OUT += current_paragraph_text
            
            #-- END loop over paragraphs. --#
            
        #-- END check to see if anything in paragraph list --#
        
        return body_string_OUT
        
    #-- END method clean_article_body() --#

            
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
        url_string = ""

        # make sure we have an article path.
        if ( article_path_IN ):
        
            # retrieve URL for date and place.
            url_string = self.generate_url( article_path_IN )
            
            # got a URL?
            if ( url_string ):
                
                # we do. Create a request.
                request_OUT = self.create_request( url_string )
                
            #-- END check to see if we have a URL string --#
            
        #-- END check to see if we have the things we need to generate request --#
        
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
        url_string = ""
        date_string = ""
        my_protocol = ""
        my_host = ""

        # make sure we have a date and a place code.
        if ( ( date_IN ) and ( place_code_IN ) ):
        
            # retrieve URL for date and place.
            url_string = self.generate_issue_url( date_IN, place_code_IN )
            
            # got a URL?
            if ( url_string ):
                
                # we do. Create a request.
                request_OUT = self.create_request( url_string )
                
            #-- END check to see if we have a URL string --#
            
        #-- END check to see if we have the things we need to generate request --#
        
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
        
            self.output_debug( ">>> making request for URL: " + str( url_IN ) + "\n" )
            
            # we do. Create a request.
            request_OUT = urllib2.Request( url_IN, None, { self.HEADER_VARIABLE_NAME_USER_AGENT : self.user_agent } )

        #-- END check to see if we have the things we need to generate request --#
        
        return request_OUT
    
    #-- END method create_request --#


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
        date_string = ""
        my_protocol = ""
        my_host = ""

        # make sure we have a date and a place code.
        if ( ( date_IN ) and ( place_code_IN ) ):
        
            # convert date_IN into a string.
            date_string = date_IN.strftime( self.FORMAT_DATE_STRING )
            
            # got anything?
            if ( date_string ):
            
                # yes.  Generate absolute path for issue.
                my_protocol = self.protocol
                my_host = self.host
                
                url_OUT = "/iw-search/we/InfoWeb?p_product=NewsBank&p_theme=aggregated5&p_action=listissue&d_place=%s&f_source=%s&f_issue=%s&f_length=45&f_limit=no" % ( place_code_IN, place_code_IN, date_string )
                
                # then, call self.generate_url() to tack on protocol and host.
                url_OUT = self.generate_url( url_OUT )
            
            #-- END check to see if conversion to string worked --#
            
        #-- END check to see if we have the things we need to generate URL --#
        
        return url_OUT
    
    #-- END method generate_issue_url --#


    def generate_url( self, absolute_path_IN ):
    
        '''
        This method accepts the absolute path part of a URL, prepends protocol
           and host name based on settings within this object.

        Returns the string URL.        
        '''
        
        # return reference
        url_OUT = ""
        
        # declare variables
        my_protocol = ""
        my_host = ""

        # make sure we have a path.
        if ( absolute_path_IN ):
        
            # yes.  Generate URL.
            my_protocol = self.protocol
            my_host = self.host
            
            url_OUT = "%s://%s%s" % ( my_protocol, my_host, absolute_path_IN )
            
        #-- END check to see if we have the things we need to generate URL --#
        
        return url_OUT
    
    #-- END method generate_url --#


    def get_article_instance( self, id_IN ):
    
        # return reference
        article_OUT = None
        
        # declare variables
        me = "get_article_instance"
        article_instance = None
        do_duplicate_check = False
        duplicate_action = ""
        existing_article_qs = None
        existing_article_count = -1
        existing_article = None

        # do we have an ID?
        if ( id_IN ):

            # create article instance to use in interacting with database.
            # do we check for duplicates?
            do_duplicate_check = self.check_for_duplicates
            if ( do_duplicate_check == True ):
    
                # get do_on_duplicate value
                duplicate_action = self.do_on_duplicate
            
                # Use the Article object to look for an existing article with the
                #    id passed in.
                existing_article_qs = Article.objects.filter( unique_identifier = id_IN )
                existing_article_count = existing_article_qs.count()
                
                # got one or more duplicates?
                if ( existing_article_count == 1 ):
                
                    # one duplicate.  We have options.  Get the one row.
                    existing_article = existing_article_qs.get( unique_identifier = id_IN )
                
                    # Yes.  We have a duplicate.  What do we do about it?
                    if ( duplicate_action == self.DO_ON_DUPLICATE_UPDATE ):
                    
                        # We are updating existing record.  Use instance
                        #    retrieved from database.
                        article_instance = existing_article
                        
                        self.output_debug( "=== in " + me + ": article with ID " + id_IN + " is already in database.  Updating." )
        
                    elif ( duplicate_action == self.DO_ON_DUPLICATE_INSERT ):
                    
                        # We are inserting again.  Set article_instance to new
                        #    article and data integrity be damned.
                        article_instance = Article()
                        
                        self.output_debug( "=== in " + me + ": article with ID " + id_IN + " is already in database.  Inserting new anyway." )
        
                    elif ( duplicate_action == self.DO_ON_DUPLICATE_SKIP ):
                    
                        # Skipping - set article_instance to empty.
                        article_instance = None
                        
                        self.output_debug( "=== in " + me + ": article with ID " + id_IN + " is already in database.  Skipping." )
        
                    else:
                    
                        # Unknown duplicate action - skip.
                        article_instance = None
                        
                        self.output_debug( "=== in " + me + ": article with ID " + id_IN + " is already in database.  Unknown duplicate action (\"" + duplicate_action + "\"), so skipping." )
        
                    #-- END check to see what we do now that we have found a duplicate --#
                    
                elif ( existing_article_count > 1 ):
                
                    # more than one duplicate.  If action is to insert, insert,
                    #    else, skip.
                    if ( duplicate_action == self.DO_ON_DUPLICATE_INSERT ):
                    
                        # We are inserting again.  Set article_instance to new
                        #    article and data integrity be damned.
                        article_instance = Article()
                        
                        self.output_debug( "=== in " + me + ": multiple articles with ID " + id_IN + " are already in database.  Inserting new anyway." )
        
                    elif ( duplicate_action == self.DO_ON_DUPLICATE_SKIP ):
                    
                        # Skipping - set article_instance to empty.
                        article_instance = None
                        
                        self.output_debug( "=== in " + me + ": multiple articles with ID " + id_IN + " are already in database.  Skipping." )
        
                    else:
                    
                        # Unknown duplicate action - skip.
                        article_instance = None
                        
                        self.output_debug( "=== in " + me + ": multiple articles with ID " + id_IN + " are already in database.  Unknown (or invalid when multiple duplicates present) duplicate action (\"" + duplicate_action + "\"), so skipping." )
        
                    #-- END check to see what we do now that we have found a duplicate --#
        
                else:
            
                    # No existing article.  Make a new Article() instance to process.
                    article_instance = Article()
        
                #-- END check to see if duplicate query returned anything. --#
            
            else:
        
                # No duplicate check.  Make a new Article() instance to process.
                article_instance = Article()
    
            #-- END check to see if we check for duplicates --#
            
        #-- END check to see if ID passed in --#
        
        article_OUT = article_instance

        return article_OUT
    
    #-- END method get_article_instance() --#


    def get_bs_helper( self ):
    
        # return reference
        instance_OUT = None
        
        # get instance.
        instance_OUT = self.bs_helper
                
        # got one?
        if ( not( instance_OUT ) ):
        
            # no.  Create and store.
            self.bs_helper = BeautifulSoupHelper()
            
            # try again.  If nothing this time, nothing we can do.  Return it.
            instance_OUT = self.bs_helper
            
        #-- END check to see if regex is stored in instance --#

        return instance_OUT
    
    #-- END method get_bs_helper() --#


    def get_regex_id( self ):
    
        # return reference
        regex_OUT = None
        
        # get compiled regex.
        regex_OUT = self.regex_docid
        
        # got one?
        if ( not( regex_OUT ) ):
        
            # no.  Create and store.
            self.regex_docid = re.compile( "[\\?&]p_docid=([^&#]*)" )
            
            # try again.  If nothing this time, nothing we can do.  Return it.
            regex_OUT = self.regex_docid
            
        #-- END check to see if regex is stored in instance --#

        return regex_OUT
    
    #-- END method get_regex_id() --#


    def get_regex_section_name( self ):
    
        # return reference
        regex_OUT = None
        
        # get compiled regex.
        regex_OUT = self.regex_section_name
        
        # got one?
        if ( not( regex_OUT ) ):
        
            # no.  Create and store.
            self.regex_section_name = re.compile( "Section:&nbsp;(.*)" )
            
            # try again.  If nothing this time, nothing we can do.  Return it.
            regex_OUT = self.regex_section_name
            
        #-- END check to see if regex is stored in instance --#

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
            
            # tell someone we made a new connection.
            self.output_debug( "*** in get_url_opener(), made a new connection." )

        #-- END check to see if url_opener is stored in instance --#

        return url_opener_OUT
    
    #-- END method get_url_opener() --#


    def initialize_url_opener( self ):
    
        # initialize URL opener.
        self.cookie_jar = cookielib.CookieJar()
        self.url_opener = urllib2.build_opener( urllib2.HTTPCookieProcessor( self.cookie_jar ) )
    
    #-- END method initialize_url_opener() --#


    def output_debug( self, message_IN ):
    
        '''
        Accepts message string.  If debug is on, passes it to print().  If not,
           does nothing for now.
        '''
    
        # got a message?
        if ( message_IN ):
        
            # only print if debug is on.
            if ( self.debug == True ):
            
                # debug is on.  For now, just print.
                print( message_IN )
            
            #-- END check to see if debug is on --#
        
        #-- END check to see if message. --#
    
    #-- END method output_debug() --#


    def process_article_list( self, bs_article_list_ul_IN ):

        '''
        Accepts a BeautifulSoup <ul> Tag instance.  Uses BS to retrieve all <li>
           tags from within, and then retrieves article information for each and
           adds it to list of URLs that it returns.
        Preconditions: must have already pulled over the article list page and
           grabbed the appropriate <ul> for processing.
        Postconditions: None
        '''
        
        # return reference
        article_array_OUT = []

        # declare variables
        li_list = None
        bs_current_li = None
        bs_current_a = None
        current_href = ""
        current_headline = ""
        
        # got a <ul>?
        if ( bs_article_list_ul_IN ):
        
            # first, need to get all <li> elements.
            li_list = bs_article_list_ul_IN.findAll( 'li' )
            
            # got any <li>s?
            if ( ( li_list ) and ( len( li_list ) > 0 ) ):
            
                # we have <li>s.  Loop and process.
                for bs_current_li in li_list:
                
                    # get a, pull out value of href, string.
                    bs_current_a = bs_current_li.a
                    current_href = bs_current_a[ 'href' ]
                    current_headline = bs_current_a.string
                    
                    # for now, just print what we've found.
                    self.output_debug( "=== current article ===\n\t- headline: " + current_headline + ";\n\t- href: " + str( current_href ) + "\n" )
                
                    # add URl to queue.
                    article_array_OUT.append( current_href )
                    
                #-- END loop over article <li>s --#
                
            #-- END check to make sure we have some <li>s --#
            
        #-- END check to make sure we have a list to process. --#
        
        return article_array_OUT
    
    #-- END method process_article_list() --#


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

        # variables to hold properties of an article
        my_section = ""
        my_page = ""
        my_edition = ""
        my_index_terms = ""
        my_archive_id = ""
        my_corrections = ""
        my_copyright = ""
        my_permalink = ""
        my_unknown_tags = ""
        unknown_separator = ""

        # variables for actually parsing article
        bs_helper = None
        bs_current_item = None # could be element, or could be text.
        is_tag = False
        current_class = ""
        current_class_attr = ""
        last_text = ""
        next_element = None
        current_tag_name = ""
        current_tag_value = ""
        unknown_tag_list = []
        
        # get BeautifulSoupHelper instance
        bs_helper = self.get_bs_helper()

        # make sure we have something to return.
        if ( ( tag_element_list_IN ) and ( article_instance_IN ) ):
        
            # we have an article instance.  Place it in return reference.
            article_OUT = article_instance_IN
        
            # Got a source info element?
            if ( tag_element_list_IN ):
            
                # got it.  Now start retrieving and processing tags.  Loop over
                #    all children of sourceInfo.  For each span whose class is
                #    "tagName", see if contents of tagName attribute match one
                #    of our known attributes.  If so, great.  Process it.  If
                #    not, doh.  Add name and value to unknown tags string, which
                #    we'll then store in the notes field in the article.
                for bs_current_item in tag_element_list_IN:
                
                    # first, get class name of current item to see what we have.
                    is_tag = False
                    current_class_attr = ""
                    next_element = None
                    next_string = None
                    
                    # is it a Tag or NavigableText?
                    is_tag = bs_helper.bs_is_tag( bs_current_item )
                    if ( is_tag == True ):
                    
                        # We have a tag.  See if it is 'class="tagName"'.
                        if ( bs_current_item.has_key( "class" ) ):

                            # we have a class - grab it.
                            current_class_attr = bs_current_item[ "class" ]
                            
                        #-- END retrieval of class attribute. --#
                        
                        # self.output_debug( "<<< <<< Current Class attribute: " + current_class_attr )

                        # Is class "tagName"?
                        if ( current_class_attr == self.HTML_CLASS_TAG_NAME ):
                        
                            # This is a tagname element.  Name is the text in the
                            #    current element.  Text value is string contents
                            #    of next element in tag_element_list_IN.  Get
                            #    element, then get string inside it.
                            # First, get tag name from current element.
                            current_tag_name = bs_current_item.string
                            current_tag_name = current_tag_name.strip()
                            
                            # Then get value from next sibling.
                            next_element = bs_current_item.nextSibling
                            current_tag_value = next_element.string
                            current_tag_value = bs_helper.convert_html_entities( current_tag_value )
                            
                            # See if this works as I think it does.
                            self.output_debug( "<<< <<< Current tag - name: " + current_tag_name + "; value: " + current_tag_value )
                            
                            # see where we store value, based on tag name.
                            if ( current_tag_name == self.NB_TAG_NAME_EDITION ):
                            
                                # edition
                                article_OUT.edition = current_tag_value
                                
                            elif ( current_tag_name == self.NB_TAG_NAME_SECTION ):
                            
                                # section
                                article_OUT.section = current_tag_value
                                
                            elif ( current_tag_name == self.NB_TAG_NAME_PAGE ):
                            
                                # page
                                article_OUT.page = current_tag_value
                                
                            elif ( current_tag_name == self.NB_TAG_NAME_CORRECTION ):
                            
                                # correction
                                article_OUT.corrections = current_tag_value
                                
                            elif ( current_tag_name == self.NB_TAG_NAME_INDEX_TERMS ):
                            
                                # index terms.  See if there are any already.
                                #   If yes, concatenate.
                                if ( my_index_terms ):
                                
                                    # already something there.  Combine them.
                                    my_index_terms += "; " + current_tag_value
                                    
                                else:
                                
                                    # none set yet - place this there.
                                    my_index_terms = current_tag_value
                                    
                                #-- END check to see if extra index terms already. --#
                                
                            elif ( current_tag_name == self.NB_TAG_NAME_RECORD_NUMBER ):
                            
                                # Record Number:
                                article_OUT.archive_id = current_tag_value
                                
                            else:
                            
                                # unknown tag.  Add to list.
                                unknown_tag_list.append( current_tag_name + "=" + current_tag_value )
                                
                            #-- END check to see which tag we are dealing with. --#
                        
                        #-- END check to see if tagName --#
                        
                    else:
                    
                        # Not a tag - Navigable Text.  Store in last_text.
                        last_text = bs_current_item.string
                    
                    #-- END check to see if tag --#
                
                #-- END loop over elements in sourceInfo div --#
                
                # If done, place the concatenated list of unknown tags into the notes field.
                if ( len( unknown_tag_list ) > 0 ):
                
                    # unknown tags.  Add to notes.
                    article_OUT.notes = "; ".join( unknown_tag_list )
                
                #-- END check to see if unknown tags --#
                
                # Then, check if we have index terms.  If so, place them in object.
                if ( my_index_terms != "" ):
                
                    # we have index terms.  Place them in the object.
                    article_OUT.index_terms = my_index_terms
                
                #-- END check to see if index terms --#
                
                # output last_text - should be the copyright statement. #
                self.output_debug( "<<< <<< Copyright = " + last_text )
                article_OUT.copyright = last_text
            
            #-- END check to see if we found a sourceInfo --#
            
            '''
            my_section = ""
            my_page = ""
            my_edition = ""
            my_index_terms = ""
            my_archive_id = ""
            my_corrections = ""
            my_copyright = ""
            '''
            
        else:
        
            # for now, just print what we've found.
            self.output_debug( "=== in process_file_contents(): no contents passed in." )
        
        #-- END check to see if contents_IN has something in it --#

        return article_OUT
                
    #-- END method process_article_tag_list() --#
                
                
    def process_file_contents( self, id_IN, contents_IN, do_update_IN = True ):

        '''
        Accepts the contents of a file (the HTML of a NewsBank article).  Uses
           BeautifulSoup to process contents, build a django Article instance
           from SourceNet models, and store the article in the database.
           
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
        status_OUT = self.STATUS_SUCCESS

        # declare variables
        me = "process_file_contents"
        
        # variables to hold properties of an article
        my_source_string = ""
        my_pub_date = ""
        my_section = ""
        my_page = ""
        my_author_string = ""
        my_headline = ""
        my_text = ""
        my_edition = ""
        my_index_terms = ""
        my_archive_id = ""
        my_corrections = ""
        my_copyright = ""
        my_permalink = ""

        # variables for actually parsing article
        bs_helper = None
        article_instance = None
        bs_article = None
        bs_div_docBody = None
        bs_div_openUrl = None
        bs_h3_docCite = None
        bs_span_pubName = None
        bs_temp_tag = None
        bs_current_element = None
        current_class_attr = ""
        current_string = ""
        bs_div_sourceInfo = None
        bs_current_item = None # could be element, or could be text.
        current_class = ""
        error_string = ""

        # make sure we have something in contents
        if ( ( id_IN ) and ( contents_IN ) ):
        
            # create Beautiful Soup instance for this article.
            bs_article = BeautifulSoup( contents_IN )
            bs_helper = self.get_bs_helper()
            
            # get the docbody div, which has everything except the permalink.
            bs_div_docBody = bs_article.find( "div", self.HTML_CLASS_DOC_BODY )
            
            # do we have a docbody BeautifulSoup object?  If no, problem
            #    retrieving original file - no sense parsing.
            if ( bs_div_docBody ):
                
                # get article instance to use in interacting with database.
                article_instance = self.get_article_instance( id_IN )
                                
                # check to see if we process - decided by whether there is something
                #    in article_instance or not.  If no, skip and move to next
                #    article.
                if ( article_instance ):
    
                    # place stuff we already know into model.
                    # Now, only set if we save, after saving.
                    #article_instance.raw_html = contents_IN
                    article_instance.unique_identifier = id_IN
                    article_instance.archive_source = SOURCE_NEWS_BANK
                    
                    # got a related newspaper to nest?
                    if ( self.newspaper_for_place ):
                        
                        article_instance.newspaper = self.newspaper_for_place
                    
                    #-- END check to see if there is a related newspaper instance --#
                    
                    # Use Beautiful Soup to parse out all of the data from the HTML file.
                    
                    # --- headline
        
                    bs_h3_docCite = bs_div_docBody.find( "h3", self.HTML_CLASS_DOC_CITE )
                    my_headline = bs_h3_docCite.string
                    my_headline = bs_helper.convert_html_entities( my_headline )
                    
                    # strip out extra white space (tabs, newlines, etc.).
                    my_headline = self.regex_white_space.sub( " ", my_headline )
                    my_headline = my_headline.strip()
        
                    self.output_debug( "<<< headline: " + my_headline )
                    
                    # For source string and date, first get span that holds paper name
                    bs_span_pubName = bs_div_docBody.find( "span", self.HTML_CLASS_PUB_NAME )
                    
                    # --- source_string
        
                    # source string is text contents of pubName span.
                    my_source_string = bs_span_pubName.string
                    
                    self.output_debug( "<<< source_string: " + my_source_string )
        
                    # --- pub_date
        
                    # to get date, first get parent of pubName span.
                    bs_temp_tag = bs_span_pubName.parent
                    
                    # just get the text within this parent element.
                    #my_pub_date = self.bs_get_child_text( bs_temp_tag )
                    my_pub_date = bs_helper.bs_get_cleaned_direct_child_text( bs_temp_tag )
                    
                    self.output_debug( "<<< pub_date (before conversion): " + str( my_pub_date ) )
                    
                    # got anything?
                    if ( my_pub_date ):
                    
                        # yes.  Should be formatted: "- Wednesday, July 8, 2009", so 
                        #    "- %A, %B %d, %Y" - convert to datetime.
                        my_pub_date = datetime.datetime.strptime( my_pub_date, "- %A, %B %d, %Y" )
                    
                    #-- END check to see if pub date is populated --#
                    
                    self.output_debug( "<<< pub_date (after conversion): " + str( my_pub_date ) )
                    
                    # --- author_string
                    
                    # get div with class "sourceInfo"
                    bs_temp_tag = bs_div_docBody.find( "div", self.HTML_CLASS_SOURCE_INFO )
                    
                    # get nested text
                    #my_author_string = self.bs_get_child_text( bs_temp_tag )
                    my_author_string = bs_helper.bs_get_cleaned_direct_child_text( bs_temp_tag )
        
                    self.output_debug( "<<< author_string: " + my_author_string )
        
                    # --- text
                    
                    # get div with class "mainText"
                    bs_temp_tag = bs_div_docBody.find( "div", self.HTML_CLASS_MAIN_TEXT )
                    
                    # clean up the article body text.
                    my_text = self.clean_article_body( bs_temp_tag )

                    self.output_debug( "<<< text: " + my_text )
                    
                    # Next we get stuff that is in tags.  First, retrieve sourceInfo div
                    #    that is direct child of docbody.  Use recursive = False.
                    bs_div_sourceInfo = bs_div_docBody.find( "div", self.HTML_CLASS_SOURCE_INFO, recursive = False )
        
                    # Did we find the element that holds the list of tags?
                    if ( bs_div_sourceInfo ):
                    
                        # got a tag list.  Process it.
                        article_instance = self.process_article_tag_list( bs_div_sourceInfo, article_instance )
        
                        '''
                        my_section = ""
                        my_page = ""
                        my_edition = ""
                        my_index_terms = ""
                        my_archive_id = ""
                        my_corrections = ""
                        my_copyright = ""
                        '''
        
                    
                    #-- END check to make sure we have a tag list. --#
                    
                    # get permalink
                    bs_div_openUrl = bs_article.find( "div", id = self.HTML_ID_OPEN_URL )
                    
                    # get anchor tag within that container
                    bs_temp_tag = bs_div_openUrl.find( "a" )
        
                    # does the tag we found have an href attribute?
                    if ( bs_temp_tag.has_key( "href" ) ):
                    
                        # yes.
                        my_permalink = bs_temp_tag[ "href" ]
                        article_instance.permalink = my_permalink.strip()
                        
                        self.output_debug( "<<< permalink: " + my_permalink )
                     
                    #-- END check to see if we have a URL for permalink. --#
                    
                    # Add items to article instance
                    article_instance.headline = my_headline
                    article_instance.source_string = my_source_string
                    article_instance.pub_date = my_pub_date
                    article_instance.author_string = my_author_string
                    article_instance.author_varchar = my_author_string
                    
                    # Now, only set if we save, after saving.
                    #article_instance.text = my_text
                    
                    # Do we update?  If you want body text, raw html saved, you
                    #    have to do an update.
                    if ( do_update_IN == True ):

                        # save the item/article to the database.
                        article_instance.save()
                        
                        # set text and raw html.
                        article_instance.set_text( my_text )
                        article_instance.set_raw_html( contents_IN )                        
                        
                    #-- END check to see if we do an update. --#
                    
                else:
                
                    # Skipping this article - probably because of duplicate checking.
                    self.output_debug( "=== in " + me + "(): no article_instance, so skipping article with ID " + id_IN + ", probably because it is a duplicate of one already in the database (duplicate action: " + self.do_on_duplicate + ")." )
    
                #-- END check to see if we process. --#
                
            else:
            
                # No docBody div, so can't process.  Log error, update status, fall out.
                error_string = "ERROR in NewsBankHelper." + me + ": No div with class docBody in article with ID = " + id_IN + ", so can't process article."
                status_OUT = error_string
                #self.add_error( self.current_item, self.current_id, error_string )
            
            #-- END check to see if we have a docBody <div> --#
                        
        else:
        
            # for now, just print what we've found.
            self.output_debug( "=== in process_file_contents(): no contents passed in." )
        
            error_string = "ERROR in NewsBankHelper." + me + ": No content for article with ID = " + id_IN + ", so can't process article."
            status_OUT = error_string
            #self.add_error( self.current_item, self.current_id, error_string )

        #-- END check to see if contents_IN has something in it --#
                
        return status_OUT
                
    #-- END method process_file_contents() --#
  

#-- END class NewsBankHelper --#