'''
Copyright 2014 Jonathan Morgan

This file is part of http://github.com/jonathanmorgan/sourcenet.

sourcenet is free software: you can redistribute it and/or modify it under the terms of the GNU Lesser General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.

sourcenet is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.

You should have received a copy of the GNU Lesser General Public License along with http://github.com/jonathanmorgan/sourcenet. If not, see http://www.gnu.org/licenses/.
'''

__author__="jonathanmorgan"
__date__ ="$May 1, 2010 6:26:35 PM$"

if __name__ == "__main__":
    print "Hello World"

#===============================================================================
# imports (in alphabetical order by package, then by name)
#===============================================================================

# python libraries
import csv
import StringIO

# Django DB classes, just to play with...
#from django.db.models import Count # for aggregating counts of authors, sources.
#from django.db.models import Max   # for getting max value of author, source counts.

# Import the classes for our SourceNet application
#from sourcenet.models import Article
#from sourcenet.models import Article_Author
from sourcenet.models import Article_Source
#from sourcenet.models import Person
#from sourcenet.models import Topic

# parent class.
from sourcenet.export.ndo_csv_matrix import NDO_CSVMatrix

#===============================================================================
# classes (in alphabetical order by name)
#===============================================================================

class NDO_TabDelimitedMatrix( NDO_CSVMatrix ):

    
    #---------------------------------------------------------------------------
    # CONSTANTS-ish
    #---------------------------------------------------------------------------

    # output type
    MY_OUTPUT_TYPE = "tab_delimited_matrix"

    # LOCAL_DEBUG_FLAG
    LOCAL_DEBUG_FLAG = False


    #---------------------------------------------------------------------------
    # instance variables
    #---------------------------------------------------------------------------


    #---------------------------------------------------------------------------
    # __init__() method
    #---------------------------------------------------------------------------


    def __init__( self ):

        # call parent's __init__() - I think...
        super( NDO_TabDelimitedMatrix, self ).__init__()

        # override things set in parent.
        self.output_type = self.MY_OUTPUT_TYPE
        self.debug = "NDO_TabDelimitedMatrix debug:\n\n"

        # initialize variables.
        self.csv_string_buffer = None
        self.csv_writer = None
        self.delimiter = "\t"

        # variables for outputting result as file
        self.mime_type = "text/tab-separated-values"
        self.file_extension = "tab"

    #-- END method __init__() --#


    #---------------------------------------------------------------------------
    # instance methods, in alphabetical order
    #---------------------------------------------------------------------------


#-- END class NDO_CSVMatrix --#