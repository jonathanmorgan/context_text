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

# option parser, for command line arguments
from optparse import OptionParser

# import the NewsbankCollector class.
from newsbank_collector import NewsBankWebCollector

#================================================================================
# Declare variables
#================================================================================

# options parser
options_parser = None
options = None
args = None

# variables to hold stuff related to http client and cookies.
newsbank_collector = None

# variables to hold info on current page.
connection = ""

# variables to hold information about time span we are looking at.
start_date_IN = None
end_date_IN = None
current_date = None
date_IN = ""
date_list_IN = None
date_list = None

# other parameters to describe how we process.
place_code_IN = ""
output_directory_IN = ""
do_database_output_IN = False
do_file_output_IN = False
ignore_missing_issues_IN = False

#================================================================================
# Initialize command line argument processor
#================================================================================


# make parser instance.
options_parser = OptionParser()

# start_date
options_parser.add_option( "-s", "--start_date", dest = "start_date", default = None, help = "Start date of date range to collect, in YYYY-MM-DD format." )

# end_date
options_parser.add_option( "-e", "--end_date", dest = "end_date", default = None, help = "End date of date range to collect, in YYYY-MM-DD format." )

# single_date
options_parser.add_option( "-d", "--single_date", dest = "single_date", default = None, help = "Single date to collect, in YYYY-MM-DD format." )

# date_list
options_parser.add_option( "-l", "--date_list", dest = "date_list", default = None, help = "List of dates to collect, in YYYY-MM-DD format, separated by commas." )

# output_directory
options_parser.add_option( "-o", "--output_directory", dest = "output_directory", default = "/home/jonathanmorgan/Documents/work/MSU/2011-3-fall/CAS992/articles", help = "Path of directory into which we will place articles that we gather." )

# place_code
options_parser.add_option( "-p", "--place_code", dest = "place_code", default = "GRPB", help = "Place code of news organization whose papers we will gather.  Defaults to Grand Rapids Press (GRPB).  Detroit News = DTNB." )

# flag to tell whether we add to database or not
options_parser.add_option( "-m", "--output_to_database", dest = "output_to_database", action = "store_true", default = False, help = "If present, parses and stores articles into database in addition to storing them on the file system." )

# flag to tell whether we store on file system
options_parser.add_option( "-f", "--output_to_files", dest = "output_to_files", action = "store_true", default = False, help = "If present, stores article HTML on the file system." )

# flag to tell whether we ignore missing issues
options_parser.add_option( "-i", "--ignore_missing_issues", dest = "ignore_missing_issues", action = "store_true", default = False, help = "If present, allows for gaps in date range where issues are missing." )

# send status emails from
options_parser.add_option( "-a", "--email_from", dest = "email_from", default = "", help = "Email address from which you want status emails to be sent." )

# output_directory
options_parser.add_option( "-b", "--email_to", dest = "email_to", default = "", help = "Email address (es - if multiple, comma-separated list) to which you want status emails to be sent." )

# parse options passed in on command line.
(options, args) = options_parser.parse_args()


#================================================================================
# Do work
#================================================================================


# make new instance of collector
newsbank_collector = NewsBankWebCollector()

# set debug flag
newsbank_collector.debug = True
newsbank_collector.newsbank_helper_debug = False

# tell it to not create a new connection every time.
newsbank_collector.always_new_connection = False

# set up error handling.
newsbank_collector.error_limit = 10
newsbank_collector.error_output_type = newsbank_collector.ERROR_OUTPUT_DB
newsbank_collector.status_email_from = options.email_from
newsbank_collector.status_email_to = options.email_to

# set up date range we will process.

# before layoffs
#start_date = datetime.date( 2009, 7, 8 )
#end_date = datetime.date( 2009, 8, 8 )
# set output directory.
#collector.output_directory = "/home/jonathanmorgan/Documents/work/MSU/2011-3-fall/CAS992/asgt2/articles-before"

# after layoffs
#start_date = datetime.date( 2010, 7, 8 )
#end_date = datetime.date( 2010, 8, 8 )
# set output directory.
#collector.output_directory = "/home/jonathanmorgan/Documents/work/MSU/2011-3-fall/CAS992/asgt2/articles-after"

# day-by-day
# before layoffs
#before_or_after = "before"
#current_date = datetime.date( 2009, 7, 8 )  # 98
#current_date = datetime.date( 2009, 7, 9 )  # 98
#current_date = datetime.date( 2009, 7, 10 ) # 89
#current_date = datetime.date( 2009, 7, 11 ) # 106
#current_date = datetime.date( 2009, 7, 12 ) # 236 - Sunday
#current_date = datetime.date( 2009, 7, 13 ) # 71
#current_date = datetime.date( 2009, 7, 14 ) # 85
#current_date = datetime.date( 2009, 7, 15 ) # 107
#current_date = datetime.date( 2009, 7, 16 ) # 121
#current_date = datetime.date( 2009, 7, 17 ) # 114
#current_date = datetime.date( 2009, 7, 18 ) # 89
#current_date = datetime.date( 2009, 7, 19 ) # 238 - Sunday
#current_date = datetime.date( 2009, 7, 20 ) # 67
#current_date = datetime.date( 2009, 7, 21 ) # 96
#current_date = datetime.date( 2009, 7, 22 ) # 103
#current_date = datetime.date( 2009, 7, 23 ) # 92
#current_date = datetime.date( 2009, 7, 24 ) # 109
#current_date = datetime.date( 2009, 7, 25 ) # 92
#current_date = datetime.date( 2009, 7, 26 ) # 231 - Sunday
#current_date = datetime.date( 2009, 7, 27 ) # 86
#current_date = datetime.date( 2009, 7, 28 ) # 95
#current_date = datetime.date( 2009, 7, 29 ) # 98
#current_date = datetime.date( 2009, 7, 30 ) # 99
#current_date = datetime.date( 2009, 7, 31 ) # 98
#current_date = datetime.date( 2009, 8, 1 )  # 86
#current_date = datetime.date( 2009, 8, 2 )  # 257 - Sunday
#current_date = datetime.date( 2009, 8, 3 )  # 84
#current_date = datetime.date( 2009, 8, 4 )  # 106
#current_date = datetime.date( 2009, 8, 5 )  # 99
#current_date = datetime.date( 2009, 8, 6 )  # 95
#current_date = datetime.date( 2009, 8, 7 )  # 100
#current_date = datetime.date( 2009, 8, 8 )  # 104
#total: 3649

# after layoffs
before_or_after = "after"
#current_date = datetime.date( 2010, 7, 7 )  # 94
#current_date = datetime.date( 2010, 7, 8 )  # 103
#current_date = datetime.date( 2010, 7, 9 )  # 93
#current_date = datetime.date( 2010, 7, 10 ) # 76
#current_date = datetime.date( 2010, 7, 11 ) # 169 - Sunday
#current_date = datetime.date( 2010, 7, 12 ) # 90
#current_date = datetime.date( 2010, 7, 13 ) # 87
#current_date = datetime.date( 2010, 7, 14 ) # 93
#current_date = datetime.date( 2010, 7, 15 ) # 85
#current_date = datetime.date( 2010, 7, 16 ) # 77
#current_date = datetime.date( 2010, 7, 17 ) # 80
#current_date = datetime.date( 2010, 7, 18 ) # 209 - Sunday
#current_date = datetime.date( 2010, 7, 19 ) # 68
#current_date = datetime.date( 2010, 7, 20 ) # 78
#current_date = datetime.date( 2010, 7, 21 ) # 83
#current_date = datetime.date( 2010, 7, 22 ) # 90
#current_date = datetime.date( 2010, 7, 23 ) # 84
#current_date = datetime.date( 2010, 7, 24 ) # 80
#current_date = datetime.date( 2010, 7, 25 ) # 198 - Sunday
#current_date = datetime.date( 2010, 7, 26 ) # 85
#current_date = datetime.date( 2010, 7, 27 ) # 88
#current_date = datetime.date( 2010, 7, 28 ) # 91
#current_date = datetime.date( 2010, 7, 29 ) # 84
#current_date = datetime.date( 2010, 7, 30 ) # 85
#current_date = datetime.date( 2010, 7, 31 ) # 66
#current_date = datetime.date( 2010, 8, 1 )  # 221 - Sunday
#current_date = datetime.date( 2010, 8, 2 )  # 74
#current_date = datetime.date( 2010, 8, 3 )  # 97
#current_date = datetime.date( 2010, 8, 4 )  # 96
#current_date = datetime.date( 2010, 8, 5 )  # 84
#current_date = datetime.date( 2010, 8, 6 )  # 93
#current_date = datetime.date( 2010, 8, 7 )  # 76
#current_date = datetime.date( 2010, 8, 8 )  # 193 - Sunday
#total: 3370

# test...
#before_or_after = "test"
#current_date = datetime.date( 2010, 7, 8 )  # ?

# process incoming arguments

# process date arguments
date_IN = options.single_date
date_list_IN = options.date_list
start_date_IN = options.start_date
end_date_IN = options.end_date

if ( date_IN ):

    # add this date to collector to process.
    newsbank_collector.add_date( date_IN )

elif ( date_list_IN ):
    
    # split list on comma, then add each date.
    date_list = date_list_IN.split( ',' )
    
    # loop over dates
    for current_date in date_list:
        
        # add date.
        newsbank_collector.add_date( current_date )
        
    #-- END loop over date list. --#
    
else:

    # no current date.  Try to use date range.
    newsbank_collector.add_date_range( start_date_IN, end_date_IN )
  
#-- END processing of dates. --#

# process place code.
place_code_IN = options.place_code

# process output directory.
output_directory_IN = options.output_directory

# get flag for outputting to database.
do_database_output_IN = options.output_to_database

# get flag for outputting to file system.
do_file_output_IN = options.output_to_files

# do we ignore missing issues?
ignore_missing_issues_IN = options.ignore_missing_issues

# Make sure we have dates to process
if ( len( newsbank_collector.dates_to_process ) > 0 ):

    # set place code.
    newsbank_collector.set_place_code( place_code_IN )
    
    # set output type flags.
    newsbank_collector.do_database_output = do_database_output_IN
    newsbank_collector.do_files_output = do_file_output_IN
    
    # set error handling options
    newsbank_collector.ignore_missing_issues = ignore_missing_issues_IN
    
    # if outputting files, set the output directory
    if ( do_file_output_IN == True ):
    
        # set output directory.
        newsbank_collector.output_directory = output_directory_IN
        
        # try to make this directory if it doesn't exist.
        if ( not os.path.isdir( newsbank_collector.output_directory ) ):
        
            # Path isn't to a directory. Try creating it.
            os.makedirs( newsbank_collector.output_directory )
        
        #-- END check to see if directory exists. --#
    
    #-- END check to see if we are doing file output. --#
    
    #print( "start date = " + str( start_date ) + "; end date = " + str( end_date ) )

    # call the method to loop over dates.
    newsbank_collector.collect()
    
else:

    print( "ERROR - no dates set, so can't collect." )

#-- END check to see if we have a current date.