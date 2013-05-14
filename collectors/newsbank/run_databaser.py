'''
Copyright 2010-2013 Jonathan Morgan

This file is part of http://github.com/jonathanmorgan/sourcenet.

sourcenet is free software: you can redistribute it and/or modify it under the terms of the GNU Lesser General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.

sourcenet is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.

You should have received a copy of the GNU Lesser General Public License along with http://github.com/jonathanmorgan/sourcenet. If not, see http://www.gnu.org/licenses/.
'''

# import python libraries
import datetime
import os
import sys

# import base Collector class
from collector import Collector

# import the NewsbankCollector class.
from newsbank_collector import FileSystemCollector

# django model for error storage
#os.environ.setdefault( "DJANGO_SETTINGS_MODULE", "research.settings" )
#sys.path.append( '/home/jonathanmorgan/Documents/django-dev/research' )
#from research.sourcenet.models import Import_Error
from sourcenet.models import Import_Error

#================================================================================
# Declare variables
#================================================================================

# variables to hold stuff related to http client and cookies.
fs_collector = None

# variables to hold information about time span we are looking at.
processing_date = ""
date_IN = ""
date_array = None
date_year = -1
date_month = -1
date_day = -1
current_date = None
directory_path = ""

# error handling
error_map = None
error_keys = None
error_count = -1
current_date_time = None
now_string = ""
error_file_name = ""
error_file = None
import_error_instance = None
error_string = ""

ERROR_OUTPUT_FILE = "file"
ERROR_OUTPUT_DB = "database"
ERROR_OUTPUT_NONE = "none"
error_output_type = ERROR_OUTPUT_DB

#================================================================================
# Do work
#================================================================================

# make new instance of collector
fs_collector = FileSystemCollector()

# set debug flag
fs_collector.debug = True

# set path of directory we want to pull articles in from
#fs_collector.directory_path = "/home/jonathanmorgan/Documents/work/MSU/2011-3-fall/CAS992/articles-test/test"
#fs_collector.directory_path = "/home/jonathanmorgan/Documents/work/MSU/2011-3-fall/CAS992/articles-before"
#fs_collector.directory_path = "/home/jonathanmorgan/Documents/work/MSU/2011-3-fall/CAS992/articles-after/"

# by-date
processing_date = "2010-07-15"

# see if there is a date passed as the first argument after the program name
#    on the command line.
if ( len( sys.argv ) > 1 ):

    # more than just the name of the script on the command line.  Get value in
    #    first argument.
    date_IN = sys.argv[ 1 ]
    
    # check to see if it is a date?
    # convert to datetime.date - parse on "-".
    date_array = date_IN.split( "-" )
    date_year = int( date_array[ 0 ] )
    date_month = int( date_array[ 1 ] )
    date_day = int( date_array[ 2 ] )
    current_date = datetime.date( date_year, date_month, date_day )
    
    # if we get here, no exceptions, so store date_IN as processing_date
    processing_date = date_IN

#-- END retrieving date from arguments on command line --#    

# Make sure we have a date
if ( processing_date ):

    fs_collector.directory_path = "/home/jonathanmorgan/Documents/work/MSU/2011-3-fall/CAS992/articles-after/" + processing_date + "/"
    
    # do check for duplicates.
    fs_collector.check_for_duplicates = True
    
    # call the method to loop over dates.
    fs_collector.collect()
    
    # do we output errors?
    if ( ( error_output_type ) and ( error_output_type != ERROR_OUTPUT_NONE ) ):
    
        # Need to add output of errors - count, and then pipe to separate error file?
        error_map = fs_collector.error_id_to_details_map
        
        # count error keys
        error_keys = error_map.keys()
        error_count = len( error_keys )
        print( "\n\nError Count: " + str( error_count ) )
        
        # got any errors?
        if ( error_count > 0 ):
        
            # output error messages to separate file.
            current_date_time = datetime.datetime.now()
            now_string = current_date_time.strftime( "%Y.%m.%d-%H.%M.%S" )
           
            # prepare error output
            if ( error_output_type == ERROR_OUTPUT_FILE ):
                
                # make error log file name.
                error_file_name = "errors-" + current_date_time.strftime( "%Y.%m.%d-%H.%M.%S" ) + ".log"
        
                # open file for writing
                error_file = open( error_file_name, 'w' )
            
                # write error count
                error_file.write( error_file_name + "\n\nError Count: " + str( error_count ) + "\n\n" )
                
                print( "\n\nError details written to file " + error_file_name )
        
            elif ( error_output_type == ERROR_OUTPUT_DB ):
        
                print( "\n\nError details written to sourcenet_import_error database table" )
        
            #-- END getting error output set up. --#
            
            # loop over errors
            error_id = None
            error_item = None
            error_message = None
            error_exception = None
            for current_id, current_details in error_map.items():
            
                # get values for parts of error.
                error_id = current_details[ Collector.ERROR_ID ]
                error_item = current_details[ Collector.ERROR_ITEM ]
                error_message = current_details[ Collector.ERROR_MESSAGE ]
                error_exception = current_details[ Collector.ERROR_EXCEPTION ]
                    
                # output error details
                if ( error_output_type == ERROR_OUTPUT_FILE ):
                
                    # write error
                    error_file.write( "\n- id = " + str( error_id ) + "; item = " + error_item + "; message = " + error_message + "; exception = " + str( error_exception ) )
                    
                elif ( error_output_type == ERROR_OUTPUT_DB ):
                
                    # make model instance
                    import_error_instance = Import_Error()
                    
                    # populate
                    import_error_instance.unique_identifier = error_id
                    import_error_instance.archive_source = "Newsbank"
                    import_error_instance.item = error_item
                    import_error_instance.message = error_message
                    import_error_instance.exception = str( error_exception )
                    import_error_instance.batch_identifier = now_string
                    
                    # save
                    import_error_instance.save()
                
                #-- END getting error output set up. --#
            
            #-- End loop over errors --#
            
            # If file, close the file.
            if ( error_output_type == ERROR_OUTPUT_FILE ):
            
                # close file.
                error_file.close()
                
            #-- END check to see if outputting errors to file --#
            
        else:
        
            print( "\n\nNo errors detected, so no errors to output!" )
        
        #-- END check to see if there are any errors --#
        
    #-- END check to see if we output errors at all. --#
    
else:

    print( "ERROR - no date set, so can't database." )

#-- END check to see if we have a date. --#