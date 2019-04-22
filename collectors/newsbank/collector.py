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
import os
import sys
import traceback

# regular expression library.
import re

# six - Python 2 and 3 support
import six

# HTML parsing
from bs4 import BeautifulSoup
from python_utilities.beautiful_soup.beautiful_soup_helper import BeautifulSoupHelper

# Email
from python_utilities.email.email_helper import EmailHelper

# django model for article
#os.environ.setdefault( "DJANGO_SETTINGS_MODULE", "research.settings" )
#sys.path.append( '/home/jonathanmorgan/Documents/django-dev/research' )
#from context_text.models import Article
#from context_text.models import Import_Error
from context_text.models import Article
from context_text.models import Import_Error

#================================================================================
# Package constants-ish
#================================================================================

SOURCE_NEWS_BANK = "NewsBank"
PLACE_CODE_GRAND_RAPIDS_PRESS = "GRPB"

#================================================================================
# CollectorException class
#================================================================================


class CollectorException( Exception ):

    '''
    This class is a custom exception so I have one of my own to throw, detect.
    '''

    # just make it work exactly like an Exception
    pass

#-- END CollectorException class --#

#================================================================================
# Collector class
#================================================================================

# define Collector parent class.
class Collector( object ):

    '''
    This class is a helper for Crawling and processing files.
    '''

    #============================================================================
    # Constants-ish
    #============================================================================
    

    FORMAT_DATE_STRING = "%Y-%m-%d"
    HEADER_VARIABLE_NAME_USER_AGENT = "User-Agent"
    
    # constants to hold keys for error details
    ERROR_ID = "id"
    ERROR_ITEM = "item"
    ERROR_MESSAGE = "message"
    ERROR_EXCEPTION = "exception"
    
    # error output
    ERROR_OUTPUT_FILE = "file"
    ERROR_OUTPUT_DB = "database"
    ERROR_OUTPUT_NONE = "none"
    
    # defaults
    ERROR_UID_SYSTEM_ERROR = "SYSTEM_ERROR"


    #============================================================================
    # Instance variables
    #============================================================================


    # DEBUG and status variables
    debug = False
    debug_string = ""
    status_string = ""
    total_articles_processed = 0
    current_id = None
    current_item = None
    current_date = datetime.datetime.now() # default to now.
    batch_identifier = datetime.datetime.now().strftime( "%Y.%m.%d-%H.%M.%S" )

    item_list = []
    id_to_item_map = {} # map docid to URL, just so we don't process articles twice (not sure if there is a chance of that, but can't hurt to parse the ID out).
    regex_docid = None
    
    # variable to hold BeautifulSoupHelper, if needed.
    bs_helper = None
    
    # error handling variables
    error_id_to_details_map = {}
    error_limit = -1
    error_output_type = "none"
    system_error_count = 0

    # status email variables
    email_helper = None
    status_email_from = ""
    status_email_to = ""
    status_email_server = "localhost"


    #============================================================================
    # Instance methods
    #============================================================================


    def add_error( self, item_IN = "", id_IN = "", error_message_IN = "", exception_IN = None, stack_trace_IN = "" ):
    
        # declare variables
        me = "add_error"
        item_id = ""
        my_error_map = None
        my_id_regex = None
        error_details = None
        my_output_type = ""
        output_error = False
        debug_message = ""
        
        # got an item?
        if ( item_IN ):
        
            # Do we have an ID passed in?
            if ( id_IN ):
            
                # we have an ID passed in.  Use it.
                item_id = id_IN
                
            else:
            
                # no ID passed in.  Try to parse it out from item.
                item_id = self.get_id_for_item( item_IN )
            
            #-- END check to see if ID passed in. --#
            
            # if we have a doc ID
            if ( item_id ):

                # make model instance
                error_details = Import_Error()
                
                # populate
                error_details.unique_identifier = item_id
                error_details.archive_source = "Newsbank"
                error_details.item = item_IN
                error_details.message = error_message_IN
                error_details.item_date = self.current_date
                error_details.batch_identifier = self.batch_identifier
                
                # Got an exception?
                if ( exception_IN ):
                
                    # output exception and stack trace.
                    error_details.exception = str( exception_IN )
                    error_details.stack_trace = traceback.format_exc()
                    
                elif ( stack_trace_IN ):
                
                    # no exception, but stack trace passed in.
                    error_details.stack_trace = stack_trace_IN
                    
                #-- END check to see if exception --#
                
                # get output type
                my_output_type = self.error_output_type
                
                # output_error
                output_error = True
                
            #-- END check to see if there is an Item ID
            
        # no item.  Got an error message?
        elif ( error_message_IN ):
                
            # got an error, but not about an item.  Increment system error count.
            self.system_error_count += 1
            
            # ID passed in?
            if ( id_IN ):
                
                # Yes, use it.
                item_id = id_IN
                
            else:
                
                # no, generate one.
                item_id = self.ERROR_UID_SYSTEM_ERROR + "-" + self.batch_identifier + "-" + str( self.system_error_count )
                
            #-- END check to see if ID passed in. --#
            
            # populate an error instance.
            error_details = Import_Error()
            error_details.unique_identifier = item_id
            error_details.archive_source = "Newsbank"
            error_details.item = None
            error_details.message = error_message_IN
            error_details.item_date = self.current_date
            error_details.batch_identifier = self.batch_identifier
            
            # output_error
            output_error = True
            
        #-- END check to see if we have an item passed in --#
        
        # See if we are to output error
        if ( output_error == True ):
            
            # if type is database, save.
            if ( my_output_type == self.ERROR_OUTPUT_DB ):

                # it is database.  Save.
                error_details.save()
    
            #-- Check if type is database --#
                
            # Add to the map.
            self.error_id_to_details_map[ error_details.unique_identifier ] = error_details
            
            # set debug message
            debug_message = "error added.  ID: " + item_id + "; Item: " + item_IN + "; message: " + error_message_IN + "; exception: " + str( exception_IN )
                
            
        else:
            
            # Nothing to output.  Error.
            debug_message = "error adding error - add_error invoked, but nothing passed in, so no error added."
            
        #-- END check to see if we output error. --#
    
        # always check error limit and output debug message
        self.check_error_limit()
        self.output_debug( debug_message, "Collector." + me )

    #-- END method add_error() --#


    def add_item_to_queue( self, item_IN, id_IN = "" ):
    
        # declare variables
        item_id = ""
        my_article_queue = None
        my_id_regex = None
        id_results = None
        
        # got a URL?
        if ( item_IN ):
        
            # Do we have an ID passed in?
            if ( id_IN ):
            
                # we have an ID passed in.  Use it.
                item_id = id_IN
                
            else:
            
                # no ID passed in.  Try to parse it out from item.
                item_id = self.get_id_for_item( item_IN )
            
            #-- END check to see if ID passed in. --#
            
            # if we have a doc ID
            if ( item_id ):
            
                # we have a doc ID - add it to map.
                self.id_to_item_map[ item_id ] = item_IN
                
            #-- end check to see if we found a docid --#
            
            # Also add this item to the list.
            self.item_list.append( item_IN )
        
        #-- END check to see if we have an item passed in --#
    
    #-- END method add_item_to_queue() --#


    def check_error_limit( self ):
    
        # declare variables
        my_error_count = -1
        my_error_limit = -1
        status_message = ""
        
        # first, see if we have a limit.
        my_error_limit = self.error_limit
        if ( my_error_limit >= 0 ):
        
            # got a limit.  Get error count.
            my_error_count = self.get_error_count()
            
            # is count greater than or equal to limit?
            if ( my_error_count >= my_error_limit ):
            
                # yup.  We are at or over limit.  Send status message.
                status_message = "Error limit exceded: errors = " + str( my_error_count ) + "; limit = " + str( my_error_limit )
                self.send_status_email( status_message, "Collector status update - error limit exceeded" )
            
            #-- END check to see if error count GTE limit --#
        
        #-- END check to see if error limit. --#
    
    #-- END method check_error_limit() --#


    def collect( self, *args, **kwargs ):

        '''
        This method is the main method that drive the collecting of data - it
           will do the work to build the list of files to process, then will
           call the method to process those files.  For now, implemented in its
           entirety in the child classes, but eventually logic to invoke
           "build_article_list" and then "process_article_list" will move here.
        '''

        # return reference
        status_OUT = "Success!"
        
        # declare variables
        current_date_time_string = ""
        status_message = ""
        
        # initialize
        self.initialize()
        current_date_time_string = datetime.datetime.now().strftime( "%Y.%m.%d-%H.%M.%S" )
        
        # Use try-catch block to try to always die gracefully, output errors.
        try:
        
            # first, call the gather_articles() method.
            self.gather_items( *args, **kwargs )
            
            # Then, see if there are any articles in queue to process.
            if ( len( self.id_to_item_map ) > 0 ):
                
                # there is something in the map.  Process the article queue.
                self.process_item_queue()
                
            #-- END check to see if we have articles to process. --#
            
        except CollectorException as ce:
        
            # CollectorException - output it.
            status_message = "\nERROR: CollectorException caught, message: " + str( ce ) + "\n" + traceback.format_exc()
            print( status_message )
            self.send_status_email( "Collection error at " + current_date_time_string + ".\n\nbatch ID: " + self.batch_identifier + "\n\nmessage:\n" + status_message, "Collector update - collection error - CollectorException caught at " + current_date_time_string + "." )

        except Exception as e:
        
            # unknown exception.
            status_message = "\nERROR: Exception caught, message: " + str( e ) + "\n" + traceback.format_exc()
            print( status_message )
            self.send_status_email( "Collection error at " + current_date_time_string + ".\n\nbatch ID: " + self.batch_identifier + "\n\nmessage:\n" + status_message, "Collector update - collection error - Exception caught at " + current_date_time_string + "." )
            raise
            
        else:
        
            # No exceptions.
            self.send_status_email( "Collection completed successfully at " + current_date_time_string + ".\n\nbatch ID: " + self.batch_identifier, "Collector update - collection completed successfully at " + current_date_time_string + "." )
            
        #-- END try-catch block --#             
        
        # Output errors.
        self.output_errors()
        
        return status_OUT
        
    #--- END method collect() ---#


    def do_include_item( self, item_IN ):
    
        '''
        This method accepts an item.  Checks to see if it should be included or
           not.  Returns true or false.  Defaults to always returning true.
           
        Preconditions: Path to directory must actually point to a directory.
        Postconditions: None. 
        '''        

        # return reference
        include_item_OUT = True
        
        return include_item_OUT

    #-- END function do_include_item() --#
    

    def gather_items( self, *args, **kwargs ):

        '''
        This method is the main method for populating the article queue if the
           parent collect method above is used.
        '''

        # return reference
        status_OUT = ""
        
        return status_OUT
        
    #-- END method gather_items() --#
    

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
            
        #-- END check to see if object is stored in instance --#

        return instance_OUT
    
    #-- END method get_bs_helper() --#


    def get_email_helper( self ):
    
        # return reference
        instance_OUT = None
        
        # get instance.
        instance_OUT = self.email_helper
                
        # got one?
        if ( not( instance_OUT ) ):
        
            # no.  Create and store.
            self.email_helper = EmailHelper()
            
            # set the from and to addresses.
            self.email_helper.set_from_address( self.status_email_from )
            self.email_helper.set_to_address( self.status_email_to )
            
            # try again.  If nothing this time, nothing we can do.  Return it.
            instance_OUT = self.email_helper
            
        #-- END check to see if object is stored in instance --#

        return instance_OUT
    
    #-- END method get_email_helper() --#


    def get_error_count( self ):
    
        '''
        Returns the number of errors in the nested error dictionary.  If no dict,
           returns -1.
        preconditions: Need to have a nested error dict.  If not, get -1.
        postconditions: None
        '''
    
        # return reference
        value_OUT = -1
        
        # declare variables
        error_map = None
        
        # get instance.
        error_map = self.error_id_to_details_map
                
        # got one?
        if ( error_map ):
        
            # yes.  Return len( error_map )
            value_OUT = len( error_map )
            
        else:
        
            # no.  return 0.
            value_OUT = -1
            
        #-- END check to see if regex is stored in instance --#

        return value_OUT
    
    #-- END method get_error_count() --#


    def get_id_for_item( self, item_IN ):

        '''
        Accepts an item, uses id regular expression to try to retrieve the ID.
        '''

        # return reference
        id_OUT = -1
        
        # declare variables
        my_id_regex = None
        id_results = None
        
        # got an item?
        if ( item_IN ):
        
            # yes.  Try to parse out the id.
            my_id_regex = self.get_regex_id()
            
            if ( my_id_regex ):

                # see if we have a doc ID.
                id_results = my_id_regex.findall( item_IN )
                
                self.output_debug( "- *** item id?: " + str( id_results ) + "\n" )
                
                # item_id should be the first result.
                id_OUT = id_results[ 0 ]
                
            #-- END check to see if we have a regex. --#
            
        #-- END check to see if ID passed in. --#

        return id_OUT
        
    #-- END method get_id_for_item() --#


    def get_regex_id( self ):
    
        # return reference
        regex_OUT = None
        
        # get compiled regex.
        regex_OUT = self.regex_docid
        
        return regex_OUT
    
    #-- END method get_regex_id() --#


    def initialize( self ):

        # declare variables
        current_date_time = None
        now_string = ""
    
        # set batch identifier
        current_date_time = datetime.datetime.now()
        now_string = current_date_time.strftime( "%Y.%m.%d-%H.%M.%S" )

        # set batch identifier to now_string
        self.batch_identifier = now_string
    
    #-- END method initialize() --#


    def output_debug( self, message_IN, me_IN = "", prefix_IN = "" ):
    
        '''
        Accepts message string.  If debug is on, passes it to print().  If not,
           does nothing for now.
        '''
        
        # declare variables
        debug_message = ""
    
        # got a message?
        if ( message_IN ):
        
            # only print if debug is on.
            if ( self.debug == True ):
            
                # debug is on.  For now, just print.
                debug_message = message_IN
                
                # got a me value?
                if ( me_IN ):
                    
                    debug_message = "In " + me_IN + ": " + debug_message
                    
                #-- END check to see if routine name passed in. --#
                
                # Got a prefix?
                if ( prefix_IN ):
                    
                    debug_message = prefix_IN + debug_message
                    
                #-- END check to see if prefix. --#
                
                print( debug_message )
            
            #-- END check to see if debug is on --#
        
        #-- END check to see if message. --#
    
    #-- END method output_debug() --#


    def output_errors( self ):

        '''
        Processes errors based on the error output settings in this instance.
        '''

        # declare variables
        my_output_type = ""
        error_map = None
        error_keys = None
        error_count = -1
        current_date_time = None
        now_string = ""
        error_file_name = ""
        error_file = None

        # variables for looping over errors
        error_id = None
        error_item = None
        error_message = None
        error_exception = None
        current_id = -1
        current_details = ""
        import_error_instance = None
        
        # do we output errors?
        my_output_type = self.error_output_type
        if ( ( my_output_type ) and ( my_output_type != self.ERROR_OUTPUT_NONE ) ):
        
            # Need to add output of errors - count, and then pipe to separate error file?
            error_map = self.error_id_to_details_map
            
            # count error keys
            error_keys = error_map.keys()
            error_count = len( error_keys )
            
            self.output_debug( "\n\nError Count: " + str( error_count ) )
            
            # got any errors?
            if ( error_count > 0 ):
            
                # output error messages to separate file.
                current_date_time = datetime.datetime.now()
                now_string = current_date_time.strftime( "%Y.%m.%d-%H.%M.%S" )
               
                # prepare error output
                if ( my_output_type == self.ERROR_OUTPUT_FILE ):
                    
                    # make error log file name.
                    error_file_name = "errors-" + current_date_time.strftime( "%Y.%m.%d-%H.%M.%S" ) + ".log"
            
                    self.output_debug( "\n\nError details written to file " + error_file_name )
            
                elif ( my_output_type == self.ERROR_OUTPUT_DB ):
            
                    self.output_debug( "\n\nError details written to context_text_import_error database table" )
            
                #-- END getting error output set up. --#
                
                # if output type is file, output errors. If output type is 
                #    database, then have been outputting them as they came in,
                #    so we don't lose them.
                # is output type file?
                if ( my_output_type == self.ERROR_OUTPUT_FILE ):

                    # open file for writing
                    with open( error_file_name, "w" ) as error_file:
                
                        # write error count
                        error_file.write( error_file_name + "\n\nError Count: " + str( error_count ) + "\n\n" )
    
                        # loop over errors.
                        error_id = None
                        error_item = None
                        error_message = None
                        error_exception = None
                        for current_id, current_details in error_map.items():
                        
                            # get values for parts of error.
                            error_id = current_details.unique_identifier
                            error_item = current_details.item
                            error_message = current_details.message
                            error_exception = current_details.exception                        
                        
                            # write error
                            error_file.write( "\n- id = " + str( error_id ) + "; item = " + error_item + "; message = " + error_message + "; exception = " + str( error_exception ) )
                            
                        #-- END loop over errors. --#
                
                    #-- END with( error_file ) - close()s file at end of with. --#

                #-- END check to see if output to file system --#
                
            else:
            
                self.output_debug( "\n\nNo errors detected, so no errors to output!" )
                    
                #-- END debug --#
            
            #-- END check to see if there are any errors --#
            
        #-- END check to see if we output errors at all. --#

    #-- END method output_errors --#


    def process_item( self, item_id_IN, item_IN ):

        '''
        This function is called on each item in the item queue.  It should
           be overridden in the child method.  It is called by
           process_item_queue().
        '''
        
        # return reference
        status_OUT = ""
        
        return status_OUT
        
    #-- END method process_item() --#    
    

    def process_item_queue( self, clear_on_finish_IN = True ):

        '''
        Loops over the items in the nested article queue (uses the contents of
           self.id_to_item_map as queue, in no particular order).  For
           each article, for now, just pulls in the body of the HTML and stores
           it in database with status of "unparsed".  Eventually, could build
           rudimentary BS parsing in right here, but for now, just need to get
           the data.
        Preconditions: must have already pulled over the article list page and
           grabbed the appropriate <ul> for processing.
        '''    

        # declare variables
        me = "process_item_queue"
        my_item_queue_map = None
        my_queue_size = -1
        current_id = ""
        current_item = ""
        current_request = None
        current_connection = None
        my_output_directory = ""
        current_output_path = ""
        current_output_file = None
        current_page_contents = ""
        item_counter = 0
        do_clear_queue_on_finish = True
        
        # set flag to clear queue
        do_clear_queue_on_finish = clear_on_finish_IN
                
        # anything in queue?
        my_item_queue_map = self.id_to_item_map
        my_queue_size = len( my_item_queue_map )
        if ( my_queue_size > 0 ):
        
            for current_id, current_item in my_item_queue_map.items():
            
                # increment counter and output debug.
                item_counter += 1

                self.output_debug( "\n\n- item " + str( item_counter ) + " of " + str( my_queue_size ) + " ( total errors: " + str( self.get_error_count() ) + " ): " + current_item + " (" + current_id + ")" )
                
                # store current ID and item
                self.current_id = current_id
                self.current_item = current_item
                
                # add in try/except block, so we can continue processing if
                #    error.
                try:
                
                    # got an item.  Invoke the process_item method.
                    self.process_item( current_id, current_item )
                    
                except Exception as e:
                
                    # exception.  Log it.
                    self.add_error( current_item, current_id, "ERROR: Exception or child caught in Collector." + me + ".", e )
                    
                except:
                
                    # exception not descended from Exception caught.  Log a message.
                    self.add_error( current_item, current_id, "ERROR: Exception not descended from Exception caught in Collector." + me + ".", None, traceback.format_exc() )                    
                    
                #-- END try/except block.
                
            #-- END loop over items. --#
            
            # Once queue is processed, do we clear it out?
            if ( do_clear_queue_on_finish == True ):
            
                # yes.  Clear out map.
                self.item_list = []
                self.id_to_item_map = {}
                
            #-- END check to see if we clear out the queue after processing it --#
            
        #-- END check to make sure we have a queue to process. --#
    
    #-- END method process_item_queue() --#


    def send_status_email( self, message_IN, subject_IN = "Collector status update" ):
    
        '''
        If from and to are both defined, accepts subject and message, makes an
           email using them and the from and to, and then sends the email.
        '''
        
        # return reference
        status_OUT = "Success!"
        
        # declare variables
        my_email_helper = None
        
        # first, see if we have from, to, and server.
        if ( ( self.status_email_from ) and ( self.status_email_to ) and ( self.status_email_server ) ):
        
            # got that.  Got a message?
            if ( message_IN ):
            
                # got what we need.  Get email helper.
                my_email_helper = self.get_email_helper()
                
                # Send message.
                my_email_helper.set_smtp_server_host( self.status_email_server )
                my_email_helper.set_from_address( self.status_email_from )
                my_email_helper.set_to_address( self.status_email_to )
                my_email_helper.set_subject( subject_IN )
                my_email_helper.set_message( message_IN )
                my_email_helper.send_email()
            
            else:
            
                self.output_debug( "ERROR: No message passed in to Controller.send_status_email().  Not sure what to do." )
            
            #-- END check to see if message passed in. --#
        
        #-- END check to make sure we have from and to addresses. --#
        
        return status_OUT
    
    #-- END method send_status_email() --#


#--- END class Collector ---#
