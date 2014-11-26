from __future__ import unicode_literals

'''
Copyright 2010-2014 Jonathan Morgan

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


# parent abstract class.
from sourcenet.article_coding.article_coder import ArticleCoder


#================================================================================
# Package constants-ish
#================================================================================


#================================================================================
# OpenCalaisArticleCoder class
#================================================================================

# define OpenCalaisArticleCoder class.
class OpenCalaisArticleCoder( ArticleCoder ):

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
    

    # status constants
    STATUS_SUCCESS = "Success!"
    

    #============================================================================
    # Instance variables
    #============================================================================

    
    # debug
    debug = False

    
    #============================================================================
    # Instance methods
    #============================================================================


    def __init__( self ):

        # call parent's __init__() - I think...
        super( OpenCalaisArticleCoder, self ).__init__()

    #-- END method __init__() --#


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


#-- END class OpenCalaisArticleCoder --#