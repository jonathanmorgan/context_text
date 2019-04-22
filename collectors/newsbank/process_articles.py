'''
Copyright 2010-2013 Jonathan Morgan

This file is part of http://github.com/jonathanmorgan/context_text.

context_text is free software: you can redistribute it and/or modify it under the terms of the GNU Lesser General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.

context_text is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.

You should have received a copy of the GNU Lesser General Public License along with http://github.com/jonathanmorgan/context_text. If not, see http://www.gnu.org/licenses/.
'''

# import python libraries
import datetime
import os
import sys

# option parser, for command line arguments
from optparse import OptionParser

# import the Article class.
os.environ.setdefault( "DJANGO_SETTINGS_MODULE", "research.settings" )
sys.path.append( '/home/jonathanmorgan/Documents/django-dev/research' )
from context_text.models import Article
from context_text.models import DEBUG

#================================================================================
# Declare variables
#================================================================================

# options parser
options_parser = None
options = None
args = None

# article instance
my_article = None
options_dict = None
status_message = ""

#================================================================================
# Initialize command line argument processor
#================================================================================

# make an article instance, for use in processing.
my_article = Article()

# make parser instance.
options_parser = OptionParser()

# start_date
options_parser.add_option( "-s", "--start_date", dest = my_article.PARAM_START_DATE, default = None, help = "Start date of date range to collect, in YYYY-MM-DD format." )

# end_date
options_parser.add_option( "-e", "--end_date", dest = my_article.PARAM_END_DATE, default = None, help = "End date of date range to collect, in YYYY-MM-DD format." )

# single_date
options_parser.add_option( "-d", "--single_date", dest = my_article.PARAM_SINGLE_DATE, default = None, help = "Single date to collect, in YYYY-MM-DD format." )

# flag to tell whether we do all processing.
options_parser.add_option( "-a", "--process_all", dest = "autoproc_all", action = "store_true", default = False, help = "If present, runs all possible processing for each article." )

# flag to tell whether we process authors.
options_parser.add_option( "-b", "--process_bylines", dest = "autoproc_authors", action = "store_true", default = False, help = "If present, runs author string processing routines." )

# parse options passed in on command line.
(options, args) = options_parser.parse_args()


#================================================================================
# Do work
#================================================================================


# set debug flag
DEBUG = True

# convert the options to a dictionary.
options_dict = vars( options )

# call the method on the articles.
status_message = Article.process_articles( **options_dict )