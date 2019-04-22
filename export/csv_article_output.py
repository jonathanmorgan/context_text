'''
Copyright 2010-2013 Jonathan Morgan

This file is part of http://github.com/jonathanmorgan/context_text.

context_text is free software: you can redistribute it and/or modify it under the terms of the GNU Lesser General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.

context_text is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.

You should have received a copy of the GNU Lesser General Public License along with http://github.com/jonathanmorgan/context_text. If not, see http://www.gnu.org/licenses/.
'''

__author__="jonathanmorgan"
__date__ ="$May 1, 2010 6:26:35 PM$"

if __name__ == "__main__":
    print( "Hello World" )

#===============================================================================
# imports (in alphabetical order by package, then by name)
#===============================================================================


# import Python libraries for CSV output
import copy
import csv

# six imports - support Pythons 2 and 3
import six
# import StringIO
from six import StringIO

# Django DB classes, just to play with...
#from django.db.models import Count # for aggregating counts of authors, sources.
#from django.db.models import Max   # for getting max value of author, source counts.

# Import the classes for our context_text application
#from context_text.models import Article
#from context_text.models import Article_Author
from context_text.models import Article_Subject
#from context_text.models import Person
from context_text.models import Topic


#===============================================================================
# classes (in alphabetical order by name)
#===============================================================================

class CsvArticleOutput( object ):


    #---------------------------------------------------------------------------
    # CONSTANTS-ish
    #---------------------------------------------------------------------------


    # article output type constants
    ARTICLE_OUTPUT_TYPE_ARTICLE_PER_LINE = 'article_per_line'
    ARTICLE_OUTPUT_TYPE_SOURCE_PER_LINE = 'source_per_line'
    ARTICLE_OUTPUT_TYPE_AUTHOR_PER_LINE = 'author_per_line'

    OUTPUT_TYPE_CHOICES_LIST = [
        ( ARTICLE_OUTPUT_TYPE_ARTICLE_PER_LINE, "One article per line" ),
        ( ARTICLE_OUTPUT_TYPE_SOURCE_PER_LINE, "One source per line" ),
        ( ARTICLE_OUTPUT_TYPE_AUTHOR_PER_LINE, "One author per line" )
    ]

    # CSV list output types
    CSV_LIST_OUTPUT_TYPE_HEADERS = 'headers'
    CSV_LIST_OUTPUT_TYPE_VALUES = 'values'


    #---------------------------------------------------------------------------
    # __init__() method
    #---------------------------------------------------------------------------


    def __init__( self ):

        # declare variables
        self.query_set = None
        self.output_type = CsvArticleOutput.ARTICLE_OUTPUT_TYPE_ARTICLE_PER_LINE

        # variables for use in processing an output request.
        self.header_prefix = ''
        self.max_topics = -1
        self.max_locations = -1
        self.max_authors = -1
        self.max_sources = -1
        
        # CSV python library outputter, stored in case a method needs to output
        #    directly to it instead of allowing a parent routine aggregate lists
        #    and then output them all at once.
        self.csv_output = None

    #-- END method __init__() --#


    #---------------------------------------------------------------------------
    # instance methods, in alphabetical order
    #---------------------------------------------------------------------------


    def create_article_list( self, output_type_IN, article_data_IN = None, header_prefix_IN = ''):

        """
            Method: create_article_list

            Purpose: Accepts an output type, an optional Article_Data model
               instance and an optional header prefix.  If output type is
               "values" and model instance is passed in, uses the values in the
               instance to populate the list. If no instance, puts empty strings
               in all the columns.  If output type of "headers", creates list of
               headers for article columns.  When creating a header list,
               if header prefix is passed in, appends the prefix to the front of
               every header.

            Params:
            - output_type_IN - output type, either "values" or "headers".
            - article_data_IN - optional - Article_Data model instance to use to populate values for this article.
            - header_prefix_IN - optional - prefix to append to the beginning of each header.

            Returns:
            - list - list of either the article's data, or the headers for an article.

        """

        # return reference
        list_OUT = []

        # declare variables
        my_article = None
        article_data_id = ''
        article_id = ''
        article_unique_identifier = ''
        article_coder = ''
        article_newspaper = ''
        article_newspaper_name = ''
        article_pub_date = ''
        article_section = ''
        article_page = ''
        article_headline = ''
        article_type = ''
        article_is_sourced = ''
        article_can_code = ''

        #-----------------------------------------------------------------------
        # set the variables
        #-----------------------------------------------------------------------

        # check output type
        if ( output_type_IN == CsvArticleOutput.CSV_LIST_OUTPUT_TYPE_VALUES ):

            # outputting values.
            
            # Got an Article_Data instance?
            if ( article_data_IN is not None ):
            
                # get info from article_data_IN
                article_data_id = article_data_IN.id
                article_coder = article_data_IN.coder.id
                article_type = article_data_IN.article_type
                article_is_sourced = article_data_IN.is_sourced
                article_can_code = article_data_IN.can_code
                
                # Check to see if we have a nested Article
                my_article = article_data_IN.article

            else:
            
                # No.  set Article_Data variables to empty, set flag to say we
                #    output empty article data, as well.
                article_data_id = ""
                article_coder = ""
                article_type = ""
                article_is_sourced = ""
                article_can_code = ""
                
                # no article data?  Yikes.
                my_article = None
                
            #-- END check to see if ArticleData passed in --#

            # Got an Article?
            if ( ( my_article ) and ( my_article is not None ) ):

                # set values from the Article instance
                article_id = my_article.id
                article_unique_identifier = my_article.unique_identifier

                article_newspaper = my_article.newspaper
                if ( article_newspaper is not None ):
                    article_newspaper_name = article_newspaper.name
                else:
                    article_newspaper_name = 'no paper'
                #-- END check to see if paper present. --#
                
                article_pub_date = my_article.pub_date.strftime( '%Y-%m-%d' )
                article_section = my_article.section
                article_page = my_article.page
                article_headline = my_article.headline

            else:                

                # no Article instance, set values to empty string.
                article_id = ''
                article_unique_identifier = ''
                article_newspaper_name = ''
                article_pub_date = ''
                article_section = ''
                article_page = ''
                article_headline = ''

            #-- END check to see if Article model instance was passed in --#

        else:

            # type is not values, so output headers
            
            # from Article_Data
            article_data_id = header_prefix_IN + "article_data_id"
            article_coder = header_prefix_IN + "coder_id"
            article_type = header_prefix_IN + "article_type"
            article_is_sourced = header_prefix_IN + "is_sourced"
            article_can_code = header_prefix_IN + "can_code"

            # from Article
            article_id = header_prefix_IN + "article_id"
            article_unique_identifier = header_prefix_IN + "unique_identifier"
            article_newspaper_name = header_prefix_IN + "newspaper"
            article_pub_date = header_prefix_IN + "pub_date"
            article_section = header_prefix_IN + "section"
            article_page = header_prefix_IN + "page"
            article_headline = header_prefix_IN + "headline"

        #-- END population of values based on presence of Article --#


        #-----------------------------------------------------------------------
        # append the article information
        #-----------------------------------------------------------------------

        # add article information to the list.  For now, leave them in the same
        #    order as before, but with article_data_id at the beginning of each.
        list_OUT.append( article_data_id )
        list_OUT.append( article_id )
        list_OUT.append( article_unique_identifier )
        list_OUT.append( article_coder )
        list_OUT.append( article_newspaper_name )
        list_OUT.append( article_pub_date )
        list_OUT.append( article_section )
        list_OUT.append( article_page )
        list_OUT.append( article_headline )
        list_OUT.append( article_type )
        list_OUT.append( article_is_sourced )
        list_OUT.append( article_can_code )

        # again, handle topics and locations little differently depending on
        #    whether we are doing headers or values.

        #-----------------------------------------------------------------------
        # append topics
        #-----------------------------------------------------------------------

        list_OUT.extend( self.create_topic_list( output_type_IN, article_data_IN, header_prefix_IN ) )

        #-----------------------------------------------------------------------
        # append locations
        #-----------------------------------------------------------------------

        list_OUT.extend( self.create_location_list( output_type_IN, article_data_IN, header_prefix_IN ) )

        return list_OUT

    #-- END method create_article_list() --#


    def create_author_list( self, output_type_IN, article_author_IN = None, header_prefix_IN = ''):
        
        """
            Method: create_author_list
            
            Purpose: Accepts an output type, an optional Article_Author model
               instance and an optional header prefix.  If output type is
               "values" and model instance is passed in, uses the values in the
               instance to populate the list. If no instance, puts empty strings
               in all the columns.  If output type of "headers", creates list of
               headers for article_author columns.  When creating a header list,
               if header prefix is passed in, appends the prefix to the front of
               every header.

            Params:
            - output_type_IN - output type, either "values" or "headers".
            - article_author_IN - optional - Article_Author model instance to use to populate values for this author.
            - header_prefix_IN - optional - prefix to append to the beginning of each header.

            Returns:
            - list - list of either the author's data, or the headers for an author.
            
        """
        
        # return reference
        list_OUT = []

        # declare variables
        author_type = ''

        # check output type
        if ( output_type_IN == CsvArticleOutput.CSV_LIST_OUTPUT_TYPE_VALUES ):

            # outputting values.  Got an author?
            if ( article_author_IN is not None ):

                # got an Article_Author instance - set type value from the instance
                author_type = article_author_IN.author_type
                author_person = article_author_IN.person

            else:

                # no author instance, set values to empty string.
                author_type = ''
                author_person = None

        else:

            # output type not values, so output headers.
            author_type = header_prefix_IN + 'type'
            author_person = None

        #-- END population of values based on presence of Article_Author --#
        
        list_OUT.append( author_type )
        list_OUT.extend( self.create_person_list( output_type_IN, author_person, header_prefix_IN ) )
        
        return list_OUT
        
    #-- END method create_author_list() --#


    def create_document_list( self, output_type_IN, document_IN = None, header_prefix_IN = '' ):

        """
            Method: create_document_list

            Purpose: Accepts an output type, an optional Document model
               instance and an optional header prefix.  If output type is
               "values" and model instance is passed in, uses the values in the
               instance to populate the list. If no instance, puts empty strings
               in all the columns.  If output type of "headers", creates list of
               headers for document columns.  When creating a header list,
               if header prefix is passed in, appends the prefix to the front of
               every header.

            Params:
            - output_type_IN - output type, either "values" or "headers".
            - organization_IN - optional - Organization model instance to use to populate values for this organization.
            - header_prefix_IN - optional - prefix to append to the beginning of each header.

            Returns:
            - list - list of either the person's data, or the headers for a person.
        """
        
        # return reference
        list_OUT = []

        # declare variables
        document_id = ''
        document_name = ''

        # check output type
        if ( output_type_IN == CsvArticleOutput.CSV_LIST_OUTPUT_TYPE_VALUES ):

            # got a document?
            if ( document_IN is not None ):

                document_id = document_IN.id
                document_name = document_IN.name

            else:

                document_id = ''
                document_name = ''

            #-- END check to see if instance is populated.

        else:

            # output type not values, so output headers.
            document_id = header_prefix_IN + 'document_id'
            document_name = header_prefix_IN + 'document_name'

        #-- END output type handling.

        # add person values on to end of list.
        list_OUT.append( document_id )
        list_OUT.append( document_name )

        return list_OUT

    #-- END function create_document_list() --#

    
    def create_header_list( self ):

        """
            Method: create_header_list

            Purpose: creates header list for outputting articles based on the
               currently selected output type.  If single article per line, uses
               the max_* variables to figure out how many locations, authors and
               sources we need to make columns to hold (so the greatest number
               of each in any article can be accomodated).  If single source per
               line, only makes columns for one source, but as many as needed
               for authors, locations.  If single author per line, only makes
               columns for one author, but as many as needed for sources,
               locations.

            Preconditions: The *_max instance variables must be set in this
               instance for this method to work.

            Returns:
            - list - list of items to be appended to the first line in the CSV file.
        """

        # return reference
        list_OUT = []

        # declare variables
        # parameters set in instance
        max_authors_IN = -1
        max_sources_IN = -1
        header_prefix_IN = ''
        output_type_IN = ''
        list_output_type = ''

        # author variables
        article_author_count = ''

        # source variables
        article_source_count = ''

        # variable to hold prefixes for authors, sources.
        person_header_prefix = ''

        # get the max counts
        max_authors_IN = self.max_authors
        max_sources_IN = self.max_sources
        header_prefix_IN = self.header_prefix
        output_type_IN = self.output_type

        # append article information.
        list_OUT.extend( self.create_article_list( CsvArticleOutput.CSV_LIST_OUTPUT_TYPE_HEADERS, None, header_prefix_IN) )

        # initialize a shared output type variable
        list_output_type = CsvArticleOutput.CSV_LIST_OUTPUT_TYPE_HEADERS


        #-----------------------------------------------------------------------
        # author information
        #-----------------------------------------------------------------------

        # first, see how many authors this article has.
        article_author_count = header_prefix_IN + "author_count"
        #article_authors = article_IN.article_author_set.all()

        # add count to output.
        list_OUT.append( article_author_count )

        # add headers for author depending on output type.
        if ( output_type_IN == CsvArticleOutput.ARTICLE_OUTPUT_TYPE_AUTHOR_PER_LINE ):

            # one author per line, so just output one set of author columns.
            person_header_prefix = header_prefix_IN + 'author_'
            # add in an author number column?
            list_OUT.extend( self.create_author_list( list_output_type, None, person_header_prefix ) )

        else:

            # add on enough headers to fill in total number of authors we need.
            for i in range( 1, max_authors_IN + 1 ):

                i_string = str( i )
                person_header_prefix = header_prefix_IN + 'author_' + i_string + '_'
                list_OUT.extend( self.create_author_list( list_output_type, None, person_header_prefix ) )

            #-- END loop to pad end of list of authors --#

        #-- END check to see if we have one or many authors --#

        #-----------------------------------------------------------------------
        # source type counts
        #-----------------------------------------------------------------------

        # first, see how many sources this article has.
        article_source_count = header_prefix_IN + "source_count"
        list_OUT.append( article_source_count )

        # ...and output headers for columns of counts broken out by type.
        # loop over types in alphabetical order, appending each to list as we
        #    go.
        for current_type in sorted( Article_Subject.SOURCE_TYPE_TO_ID_MAP.iterkeys() ):

            # get count for type
            current_type_count = article_source_count + "_" + current_type
            list_OUT.append( current_type_count )

        #-- END loop over source types --#

        #-----------------------------------------------------------------------
        # source information
        #-----------------------------------------------------------------------

        # add source headers based on output type.  If single source per line,
        #    just add one set of headers.  If not, add max_sources sets of
        #    headers.
        if ( output_type_IN == CsvArticleOutput.ARTICLE_OUTPUT_TYPE_SOURCE_PER_LINE ):

            # one author per line, so just output one set of author columns.
            person_header_prefix = header_prefix_IN + 'source_'
            # add in an author number column?
            list_OUT.extend( self.create_source_list( list_output_type, None, person_header_prefix ) )

        else:

            # not one source per line, so loop over sources
            for i in range( 1, max_sources_IN + 1 ):

                # get data.
                i_string = str( i )
                person_header_prefix = header_prefix_IN + 'source_' + i_string + '_'
                list_OUT.extend( self.create_source_list( list_output_type, None, person_header_prefix) )

            #-- END loop over sources --#

        #-- END check for output type for headers.

        return list_OUT

    #-- END method create_header_list() --#


    def create_location_list( self, output_type_IN, article_data_IN = None, header_prefix_IN = ''):

        """
            Method: create_location_list

            Purpose: Accepts an output type, an optional Article_Data model
               instance and an optional header prefix.  If output type is
               "values" and model instance is passed in, uses the locations in
               the instance, in combination with the max_locations instance
               variable, to populate the list. If no instance or max_locations
               is 0, returns nothing.  If output type of "headers", creates list
               of headers for max_locations locations.  When creating a header
               list, if header prefix is passed in, appends the prefix to the
               front of every header.

            Params:
            - output_type_IN - output type, either "values" or "headers".
            - article_data_IN - optional - Article model instance to use to populate location values for this article.
            - header_prefix_IN - optional - prefix to append to the beginning of each header.

            Returns:
            - list - list of either the article's location data, or the headers for an article's locations.

        """

        # return reference
        list_OUT = []

        # declare variables

        # fields in actually in an article
        max_locations_IN = -1

        # related locations (not captured in current study).
        article_locations = None
        article_locations_count = ''

        # grab max_locations
        max_locations_IN = self.max_locations


        #-----------------------------------------------------------------------
        # set the variables
        #-----------------------------------------------------------------------

        # check output type
        if ( output_type_IN == CsvArticleOutput.CSV_LIST_OUTPUT_TYPE_VALUES ):

            # outputting values.  Got an article?
            if ( article_data_IN is not None ):

                # got an Article instance - set type value from the instance
                article_locations = article_data_IN.locations.order_by( 'id' )
                article_locations_count = article_locations.count()

            else:

                # no article instance, set values to empty string.
                article_locations = None
                article_locations_count = ''

        else:

            article_locations = None
            article_locations_count = header_prefix_IN + "location_count"

        #-- END population of values based on presence of Article --#


        #-----------------------------------------------------------------------
        # append locations
        #-----------------------------------------------------------------------

        # always append locations count
        list_OUT.append( article_locations_count )

        # will behave differently if values or headers.  Which are we?
        if ( output_type_IN == CsvArticleOutput.CSV_LIST_OUTPUT_TYPE_VALUES ):

            # locations - append associated locations, then append empties until
            #    we have appended max_locations_IN locations.
            location_count = 0
            for current_location in article_locations:

                # append the location's name
                list_OUT.append( str( current_location ) )

                # increment location counter
                location_count += 1

            #-- END loop over locations

            # loop over the remaining spaces we need to fill.
            for i in range( 1, max_locations_IN - location_count + 1 ):

                # add empty value
                list_OUT.append( '' )

            #-- END loop to fill in rest of locations. --#

        else:

            # not values, so headers - append headers for each location up to
            #    max_locations.
            # locations - append() max_locations location headers to output list.

            # loop over the max locations in any article.
            for i in range( 1, max_locations_IN + 1 ):

                # add empty value
                list_OUT.append( header_prefix_IN + 'location_' + str( i ) )

            #-- END loop to fill in rest of locations. --#

        #-- END conditional to determine what we append based on output type --#

        return list_OUT

    #-- END method create_location_list() --#


    def create_organization_list( self, output_type_IN, organization_IN = None, header_prefix_IN = ''):

        """
            Method: create_organization_list

            Purpose: Accepts an output type, an optional Organization model
               instance and an optional header prefix.  If output type is
               "values" and model instance is passed in, uses the values in the
               instance to populate the list. If no instance, puts empty strings
               in all the columns.  If output type of "headers", creates list of
               headers for organization columns.  When creating a header list,
               if header prefix is passed in, appends the prefix to the front of
               every header.

            Params:
            - output_type_IN - output type, either "values" or "headers".
            - organization_IN - optional - Organization model instance to use to populate values for this organization.
            - header_prefix_IN - optional - prefix to append to the beginning of each header.

            Returns:
            - list - list of either the person's data, or the headers for a person.
        """

        # return reference
        list_OUT = []

        # declare variables
        organization_id = ''
        organization_name = ''

        # check output type
        if ( output_type_IN == CsvArticleOutput.CSV_LIST_OUTPUT_TYPE_VALUES ):

            # got an organization?
            if ( organization_IN is not None ):

                organization_id = organization_IN.id
                organization_name = organization_IN.name

            else:

                organization_id = ''
                organization_name = ''

            #-- END check to see if instance is populated.

        else:

            # output type not values, so output headers.
            organization_id = header_prefix_IN + 'organization_id'
            organization_name = header_prefix_IN + 'organization_name'

        #-- END output type handling.

        # add person values on to end of list.
        list_OUT.append( organization_id )
        list_OUT.append( organization_name )

        return list_OUT

    #-- END method create_organization_list() --#


    def create_person_list( self, output_type_IN, person_IN = None, header_prefix_IN = ''):

        """
            Method: create_person_list

            Purpose: Accepts an output type, an optional Person model
               instance and an optional header prefix.  If output type is
               "values" and model instance is passed in, uses the values in the
               instance to populate the list. If no instance, puts empty strings
               in all the columns.  If output type of "headers", creates list of
               headers for person columns.  When creating a header list,
               if header prefix is passed in, appends the prefix to the front of
               every header.

            Params:
            - output_type_IN - output type, either "values" or "headers".
            - person_IN - optional - Person model instance to use to populate values for this person.
            - header_prefix_IN - optional - prefix to append to the beginning of each header.

            Returns:
            - list - list of either the person's data, or the headers for a person.
        """

        # return reference
        list_OUT = []

        # declare variables
        person_id = -1
        person_first_name = ''
        person_middle_name = ''
        person_last_name = ''
        person_gender = ''

        # what is our output type?
        if ( output_type_IN == CsvArticleOutput.CSV_LIST_OUTPUT_TYPE_VALUES ):

            # got a person?
            if ( person_IN is not None ):

                # yes, set values from person model instance.
                person_id = person_IN.id
                person_first_name = person_IN.first_name
                person_middle_name = person_IN.middle_name
                person_last_name = person_IN.last_name
                person_gender = person_IN.gender

            else:

                # if not model instance, set to empty strings.
                person_id = ''
                person_first_name = ''
                person_middle_name = ''
                person_last_name = ''
                person_gender = ''

            #-- END check to see if instance is populated.

        else:

            # if not values, we output headers.
            person_id = header_prefix_IN + 'person_id'
            person_first_name = header_prefix_IN + 'first_name'
            person_middle_name = header_prefix_IN + 'middle_name'
            person_last_name = header_prefix_IN + 'last_name'
            person_gender = header_prefix_IN + 'gender'

        #-- END check of output type.

        # add person values on to end of list.
        list_OUT.append( person_id )
        list_OUT.append( person_first_name )
        list_OUT.append( person_middle_name )
        list_OUT.append( person_last_name )
        list_OUT.append( person_gender )

        return list_OUT

    #-- END method create_person_list() --#


    def create_source_count_list( self, output_type_IN, article_data_IN = None, header_prefix_IN = ''):

        """
            Method: create_source_count_list

            Purpose: Accepts an output type, an optional Article_Data model
               instance and an optional header prefix.  If output type is
               "values" and model instance is passed in, uses the sources in the
               instance to populate the list. If no instance, puts empty strings
               in all the columns.  If output type of "headers", creates list of
               headers for article columns.  When creating a header list,
               if header prefix is passed in, appends the prefix to the front of
               every header.

            Params:
            - output_type_IN - output type, either "values" or "headers".
            - article_data_IN - optional - Article_Data model instance to use to populate source count values for this article.
            - header_prefix_IN - optional - prefix to append to the beginning of each header.

            Returns:
            - list - list of either the article's source count data, or the headers for a source count columns.

        """

        # return reference
        list_OUT = []

        # declare variables
        article_source_set = None
        article_source_count = -1
        article_source_counts_by_type = None
        current_type = ''
        current_type_count = -1


        #-----------------------------------------------------------------------
        # set the variables
        #-----------------------------------------------------------------------

        # check output type
        if ( output_type_IN == CsvArticleOutput.CSV_LIST_OUTPUT_TYPE_VALUES ):

            # outputting values.  Got an article?
            if ( article_data_IN is not None ):

                # yes.  Set the article count.
                article_source_set = article_data_IN.get_quoted_article_sources_qs()
                article_source_count = article_source_set.count()

            else:

                # no, so make the column empty.
                article_source_count = ''

        else:

            # not values, so headers - place header name in source count.
            article_source_count = header_prefix_IN + "source_count"

        #-- END population of values based on presence of Article --#


        #-----------------------------------------------------------------------
        # append topic information
        #-----------------------------------------------------------------------

        # regardless of output type, append source count contents
        list_OUT.append( article_source_count )

        # for outputting sources, different based on output type.
        if ( output_type_IN == CsvArticleOutput.CSV_LIST_OUTPUT_TYPE_VALUES ):

            # ...and broken out by type.
            article_source_counts_by_type = article_data_IN.get_source_counts_by_type()

            # loop over the counts in alphabetical order of type, appending each to
            #    list as we go.
            for current_type in sorted( Article_Subject.SOURCE_TYPE_TO_ID_MAP.iterkeys() ):

                # get count for type
                if current_type in article_source_counts_by_type:

                    # type is in dictionary - yay
                    current_type_count = article_source_counts_by_type[ current_type ]

                else:

                    # type is not in dictionary... Count = 0.
                    current_type_count = 0

                #-- END check to see if current type is in dictionary of counts.

                list_OUT.append( current_type_count )

            #-- END loop over source types --#

        else:

            # not values, so headers.
            # output headers for columns of counts broken out by type.
            # loop over types in alphabetical order, appending each to list as
            #   we go.
            for current_type in sorted( Article_Subject.SOURCE_TYPE_TO_ID_MAP.iterkeys() ):

                # set column header for type
                current_type_count = article_source_count + "_" + current_type
                list_OUT.append( current_type_count )

            #-- END loop over source types --#

        #-- END appending source counts --#

        return list_OUT

    #-- END method create_source_count_list() --#


    def create_source_list( self, output_type_IN, article_source_IN, header_prefix_IN = ''):

        """
            Method: create_source_list

            Purpose: Accepts an output type, an optional Article_Subject model
               instance for a source, and an optional header prefix.  If output type is
               "values" and model instance is passed in, uses the values in the
               instance to populate the list. If no instance, puts empty strings
               in all the columns.  If output type of "headers", creates list of
               headers for article_source columns.  When creating a header list,
               if header prefix is passed in, appends the prefix to the front of
               every header.

            Params:
            - output_type_IN - output type, either "values" or "headers".
            - article_source_IN - optional - Article_Subject instance to use to populate values for this author.
            - header_prefix_IN - optional - prefix to append to the beginning of each header.

            Returns:
            - list - list of either the source's data, or the headers for an source.

        """

        # return reference
        list_OUT = []

        # declare variables
        source_type = ''
        source_title = ''
        source_more_title = ''
        source_contact_type = ''
        source_capacity = ''
        source_localness = ''
        source_notes = ''
        source_person = None
        source_organization = None
        source_document = None

        # what is our output type?
        if ( output_type_IN == CsvArticleOutput.CSV_LIST_OUTPUT_TYPE_VALUES ):

            # values - got an Article_Subject model instance?
            if ( article_source_IN is not None ):

                # got a source.  Use it to populate fields.
                source_type = article_source_IN.source_type
                source_title = article_source_IN.title
                source_more_title = article_source_IN.more_title
                source_contact_type = article_source_IN.source_contact_type
                source_capacity = article_source_IN.source_capacity
                source_localness = article_source_IN.localness
                source_notes = article_source_IN.notes
                source_person = article_source_IN.person
                source_organization = article_source_IN.organization
                source_document = article_source_IN.document

            else:

                # no source, so outputting headers.
                source_type = ''
                source_title = ''
                source_more_title = ''
                source_contact_type = ''
                source_capacity = ''
                source_localness = ''
                source_notes = ''
                source_person = None
                source_organization = None
                source_document = None

            #-- END check to see if we have an Article_Subject model instance --#

        else:

            # output type not values, so outputting headers.
            source_type = header_prefix_IN + "type"
            source_title = header_prefix_IN + "title"
            source_more_title = header_prefix_IN + "more_title"
            source_contact_type = header_prefix_IN + "contact_type"
            source_capacity = header_prefix_IN + "capacity"
            source_localness = header_prefix_IN + "localness"
            source_notes = header_prefix_IN + "notes"
            source_person = None
            source_organization = None
            source_document = None

        #-- END check of output type. --#

        # add info to list.
        list_OUT.append( source_type )
        list_OUT.append( source_title )
        list_OUT.append( source_more_title )
        list_OUT.append( source_contact_type )
        list_OUT.append( source_capacity )
        list_OUT.append( source_localness )
        list_OUT.append( source_notes )

        # add objects to list.
        list_OUT.extend( self.create_person_list( output_type_IN, source_person, header_prefix_IN ) )
        list_OUT.extend( self.create_organization_list( output_type_IN, source_organization, header_prefix_IN ) )
        list_OUT.extend( self.create_document_list( output_type_IN, source_document, header_prefix_IN ) )

        return list_OUT

    #-- END method create_source_list() --#


    def create_topic_list( self, output_type_IN, article_data_IN = None, header_prefix_IN = ''):

        """
            Method: create_topic_list

            Purpose: Accepts an output type, an optional Article_Data model
               instance and an optional header prefix.  If output type is
               "values" and model instance is passed in, uses the topics in the
               instance to populate the list. If no instance, puts empty strings
               in all the columns.  If output type of "headers", creates list of
               headers for article columns.  When creating a header list,
               if header prefix is passed in, appends the prefix to the front of
               every header.

            Params:
            - output_type_IN - output type, either "values" or "headers".
            - article_data_IN - optional - Article_Data model instance to use to populate topics values for this article.
            - header_prefix_IN - optional - prefix to append to the beginning of each header.

            Returns:
            - list - list of either the article's topics, or the headers for an article's topics.

        """

        # return reference
        list_OUT = []

        # declare variables
        all_topics = None
        article_topics = None
        article_topics_count = ''
        current_topic = None
        topic_name = ''

        # variables for topic values
        topic_id = -1
        topic_dictionary = None
        #topic_count = -1
        current_topic = ''
        topic_column_value = ''
        topic_test = None

        #-----------------------------------------------------------------------
        # set the variables
        #-----------------------------------------------------------------------

        # check output type
        if ( output_type_IN == CsvArticleOutput.CSV_LIST_OUTPUT_TYPE_VALUES ):

            # outputting values.  Got an article?
            if ( article_data_IN is not None ):

                # also can deal with topics and locations.
                article_topics = article_data_IN.topics.all()
                article_topics_count = article_topics.count()

            else:

                # also can deal with topics and locations.
                article_topics = None
                article_topics_count = ''

        else:

            #article_topics = article_IN.topics.all()
            all_topics = None
            #article_topics = None
            article_topics_count = header_prefix_IN + "topic_count"
            current_topic = None
            topic_name = ''

        #-- END population of values based on presence of Article --#


        #-----------------------------------------------------------------------
        # append topic information
        #-----------------------------------------------------------------------

        # regardless of output type, append topic count contents
        list_OUT.append( article_topics_count )

        # both output types use a list of all topics, so retrieve it here, so we
        #    can make sure it is sorted the same way regardless of output type.
        all_topics = Topic.objects.order_by( 'name' )

        # for outputting topics, different based on output type.
        if ( output_type_IN == CsvArticleOutput.CSV_LIST_OUTPUT_TYPE_VALUES ):

            # topic values - there is a total count of topics, and then a column
            #    for each topic, and we want to put a 1 in the columns of topics
            #    that are associated with this article.

            # first, build a dictionary that maps topic ID to article topic for all
            #    topics associated with this instance.
            topic_dictionary = {}
            for current_topic in article_topics:

                # add the topic to the dictionary.
                topic_id = current_topic.id
                topic_dictionary[ topic_id ] = current_topic

            #-- END loop over topics

            # loop over all_topics, creating and populating a column for each.
            for current_topic in all_topics:

                # initialize topic_column_value to 0
                topic_column_value = str( 0 )
                topic_test = None

                # see if this topic is assigned to the article.
                topic_id = current_topic.id
                if ( topic_dictionary.has_key( topic_id ) ):
                    topic_test = topic_dictionary[ topic_id ]

                # is the topic present
                if ( topic_test ):

                    # yes, it is present. Set column value to 1.
                    topic_column_value = str( 1 )

                #-- END check to see if topic is assigned on article.

                # append value for this topic.
                list_OUT.append( topic_column_value )

            #-- END loop to create columns for topics. --#

        else:

            # not values, so headers.

            # loop over all_topics, creating a column for each.
            for current_topic in all_topics:

                # add column for topic
                topic_name = current_topic.name
                list_OUT.append( header_prefix_IN + 'topic_' + topic_name )

            #-- END loop to create columns for topics. --#

        #-- END appending topics --#

        return list_OUT

    #-- END method create_topic_list() --#


    def render_article_author_per_line( self, article_data_IN, output_csv_IN = None ):

        """
            Method: render_article_per_line

            Purpose: Accepts an Article_Data instance, renders an output line per
               author in the article, including all article information on each
               line.  Does not return anything.  Appends each line directly to
               output.

            Params:
            - article_data_IN - article that we are going to render in CSV.
            - output_csv_IN - optional way to pass in a CSV output object to which you want each line appended.
        """

        # return reference
        article_list_OUT = []

        # declare variables
        output_csv = None
        list_output_type = ''
        max_authors_IN = -1
        article_author_count = -1
        article_authors = None
        current_author = None
        max_sources_IN = -1
        article_source_set = None
        article_source_count = -1
        article_sources = None
        current_source = None
        article_list_pre_author = []
        article_list_post_author = []

        # set the list output type so we can re-use throughout.
        list_output_type = CsvArticleOutput.CSV_LIST_OUTPUT_TYPE_VALUES

        # see if output_csv_IN passed in.  If not, look for one in our instance.
        if ( output_csv_IN is not None ):

            output_csv = output_csv_IN

        else:

            # no csv outputter passed in.  Try using the one from the instance.
            output_csv = self.csv_output

        #-- END check to see if we have output_csv. --#

        # make sure we have an article.
        if ( article_data_IN is not None ):

            # grab max_authors_IN and max_sources_IN.
            max_authors_IN = self.max_authors
            max_sources_IN = self.max_sources

            # first need to render the parts of the article that will go with
            #    each author, so, the article, the source type counts and the
            #    source list.  Store article in article_list_pre_author, store
            #    the source stuff in article_list_post_author, then loop over
            #    authors and for each author:
            #    - copy article_list_pre_author into article_list_OUT
            #    - extend the current author into article_list_OUT
            #    - copy article_list_post_author into article_list_OUT
            #    - use output_csv to output the row for the source.
            #    - reset article_list_OUT and begin again.

            # render information actually held in article.
            article_list_pre_author.extend( self.create_article_list( list_output_type, article_data_IN ) )

            #-------------------------------------------------------------------
            # source type counts
            #-------------------------------------------------------------------

            # Output counts of sources - total, and broken out by source type.
            article_list_post_author.extend( self.create_source_count_list( list_output_type, article_data_IN, '' ) )

            #-------------------------------------------------------------------
            # source information
            #-------------------------------------------------------------------

            # loop over sources
            article_source_set = article_data_IN.get_quoted_article_sources_qs()
            article_sources = article_source_set.order_by( 'person' )
            article_source_count = article_sources.count()
            for current_source in article_sources:

                # append source to list
                article_list_post_author.extend( self.create_source_list( list_output_type, current_source, '' ) )

            #-- END loop over sources --#

            # add on enough blanks to fill in total number of authors we need.
            for i in range( 1, int( max_sources_IN ) - article_source_count + 1 ):

                # add empty sources to the list.
                article_list_post_author.extend( self.create_source_list( list_output_type, None, '' ) )

            #-- END loop to pad end of list of sources --#

            #-------------------------------------------------------------------
            # author information
            #-------------------------------------------------------------------

            # first, see how many authors this article has.
            article_authors = article_data_IN.article_author_set.order_by( 'person' )
            article_author_count = article_authors.count()

            # add author count to pre-author output.
            article_list_pre_author.append( article_author_count )

            # got any authors at all?
            if ( article_author_count > 0 ):

                # we do. loop over authors
                for current_author in article_authors:

                    # initialize article_list_OUT and add on pre-author stuff
                    article_list_OUT = []
                    article_list_OUT.extend( copy.deepcopy( article_list_pre_author ) )

                    # add author to list.
                    article_list_OUT.extend( self.create_author_list( list_output_type, current_author, '' ) )

                    # add post-author stuff(source information)
                    article_list_OUT.extend( copy.deepcopy( article_list_post_author ) )

                    # write the line to the output file
                    output_csv.writerow( article_list_OUT )

                #-- END loop over authors --#

            else:

                # initialize article_list_OUT and add on pre-author stuff
                article_list_OUT = []
                article_list_OUT.extend( copy.deepcopy( article_list_pre_author ) )

                # add author to list.
                article_list_OUT.extend( self.create_author_list( list_output_type, current_author, '' ) )

                # add post-author stuff(source information)
                article_list_OUT.extend( copy.deepcopy( article_list_post_author ) )

                # write the line to the output file
                output_csv.writerow( article_list_OUT )

            #-- END check to see if any authors --#

        #-- END check to see if an article is passed in. --#

        #return article_list_OUT

    #-- END method render_article_author_per_line() --#


    def render_article_per_line( self, article_data_IN ):

        """
            Method: render_article_per_line

            Purpose: Accepts an Article_Data row, renders that article all on one
               line.  Returns the list of elements to add to a CSV file for this
               article, in the order they should be appended.

            Params:
            - article_data_IN - article that we are going to render in CSV.

            Returns:
            - article_list_OUT - list of the information for this article, ready to be added to a csv instance.
        """

        # return reference
        article_list_OUT = []

        # declare variables
        list_output_type = ''
        max_authors_IN = -1
        article_author_count = -1
        article_authors = None
        current_author = None
        max_sources_IN = -1
        article_source_set = None
        article_source_count = -1
        article_sources = None
        current_source = None

        # set the list output type so we can re-use throughout.
        list_output_type = CsvArticleOutput.CSV_LIST_OUTPUT_TYPE_VALUES

        # make sure we have an article.
        if ( article_data_IN is not None ):

            # grab max_authors_IN and max_sources_IN.
            max_authors_IN = self.max_authors
            max_sources_IN = self.max_sources

            # render information actually held in article.
            article_list_OUT.extend( self.create_article_list( list_output_type, article_data_IN ) )

            #-------------------------------------------------------------------
            # author information
            #-------------------------------------------------------------------

            # first, see how many authors this article has.
            article_authors = article_data_IN.article_author_set.order_by( 'person' )
            article_author_count = article_authors.count()

            # add count to output.
            article_list_OUT.append( article_author_count )

            # loop over authors
            for current_author in article_authors:

                # add author to list.
                article_list_OUT.extend( self.create_author_list( list_output_type, current_author, '' ) )

            #-- END loop over authors --#

            # add on enough blanks to fill in total number of authors we need.
            for i in range( 1, int( max_authors_IN ) - article_author_count + 1 ):

                # add empty author to list.
                article_list_OUT.extend( self.create_author_list( list_output_type, None, '' ) )

            #-- END loop to pad end of list of authors --#

            #-------------------------------------------------------------------
            # source type counts
            #-------------------------------------------------------------------

            # Output counts of sources - total, and broken out by source type.
            article_list_OUT.extend( self.create_source_count_list( list_output_type, article_data_IN, '' ) )

            #-------------------------------------------------------------------
            # source information
            #-------------------------------------------------------------------

            # loop over sources
            article_source_set = article_data_IN.get_quoted_article_sources_qs()
            article_source_count = article_source_set.count()
            article_sources = article_source_set.order_by( 'person' )
            for current_source in article_sources:

                # append source to list
                article_list_OUT.extend( self.create_source_list( list_output_type, current_source, '' ) )

            #-- END loop over sources --#

            # add on enough blanks to fill in total number of authors we need.
            for i in range( 1, int( max_sources_IN ) - article_source_count + 1 ):

                # add empty sources to the list.
                article_list_OUT.extend( self.create_source_list( list_output_type, None, '' ) )

            #-- END loop to pad end of list of sources --#

        #-- END check to see if an article is passed in. --#

        return article_list_OUT

    #-- END method render_article_per_line() --#


    def render_article_source_per_line( self, article_data_IN, output_csv_IN = None ):

        """
            Method: render_article_source_per_line

            Purpose: Accepts an Article_Data instance, renders an output line per
               source in the article, including all article information on each
               line.  Does not return anything.  Appends each line directly to
               output.

            Params:
            - article_data_IN - article that we are going to render in CSV.
            - output_csv_IN - optional way to pass in a CSV output object to which you want each line appended.
        """

        # return reference
        article_list_OUT = []

        # declare variables
        output_csv = None
        list_output_type = ''
        max_authors_IN = -1
        article_author_count = -1
        article_authors = None
        current_author = None
        max_sources_IN = -1
        article_source_set = None
        article_source_count = -1
        article_sources = None
        current_source = None
        article_list_pre_source = []

        # set the list output type so we can re-use throughout.
        list_output_type = CsvArticleOutput.CSV_LIST_OUTPUT_TYPE_VALUES

        # see if output_csv_IN passed in.  If not, look for one in our instance.
        if ( output_csv_IN is not None ):

            output_csv = output_csv_IN

        else:

            # no csv outputter passed in.  Try using the one from the instance.
            output_csv = self.csv_output

        #-- END check to see if we have output_csv. --#

        # make sure we have an article.
        if ( article_data_IN is not None ):

            # grab max_authors_IN and max_sources_IN.
            max_authors_IN = self.max_authors
            max_sources_IN = self.max_sources

            # first need to render the parts of the article that will go with
            #    each source so, the article, the author list, and the source
            #    type counts.  Store this all in article_list_pre_source, then
            #    for each source:
            #    - copy article_list_pre_source into article_list_OUT
            #    - extend the current source into article_list_OUT
            #    - use output_csv to output the row for the source.
            #    - reset article_list_OUT and begin again.

            # render information actually held in article.
            article_list_pre_source.extend( self.create_article_list( list_output_type, article_data_IN ) )

            #-------------------------------------------------------------------
            # author information
            #-------------------------------------------------------------------

            # first, see how many authors this article has.
            article_authors = article_data_IN.article_author_set.order_by( 'person' )
            article_author_count = article_authors.count()

            # add count to output.
            article_list_pre_source.append( article_author_count )

            # loop over authors
            for current_author in article_authors:

                # add author to list.
                article_list_pre_source.extend( self.create_author_list( list_output_type, current_author, '' ) )

            #-- END loop over authors --#

            # add on enough blanks to fill in total number of authors we need.
            for i in range( 1, int( max_authors_IN ) - article_author_count + 1 ):

                # add empty author to list.
                article_list_pre_source.extend( self.create_author_list( list_output_type, None, '' ) )

            #-- END loop to pad end of list of authors --#

            #-------------------------------------------------------------------
            # source type counts
            #-------------------------------------------------------------------

            # Output counts of sources - total, and broken out by source type.
            article_list_pre_source.extend( self.create_source_count_list( list_output_type, article_data_IN, '' ) )

            #-------------------------------------------------------------------
            # source information
            #-------------------------------------------------------------------

            # loop over sources, outputting a row for each.
            article_source_set = article_data_IN.get_quoted_article_sources_qs()
            article_sources = article_source_set.order_by( 'person' )
            article_source_count = article_sources.count()

            # check if we have any sources.  Should output article even if no
            #    sources.
            if ( article_source_count > 0 ):

                # got sources - loop.
                for current_source in article_sources:

                    # first, place a copy of article_list_pre_source in
                    #    article_list_OUT
                    article_list_OUT = []
                    article_list_OUT.extend( copy.deepcopy( article_list_pre_source ) )

                    # append source to list
                    article_list_OUT.extend( self.create_source_list( list_output_type, current_source, '' ) )

                    # output the source
                    output_csv.writerow( article_list_OUT )

                #-- END loop over sources --#

            else:

                # no sources.  Output one row with blank values for source.
                # first, place a copy of article_list_pre_source in
                #    article_list_OUT
                article_list_OUT = []
                article_list_OUT.extend( copy.deepcopy( article_list_pre_source ) )

                # append source to list
                article_list_OUT.extend( self.create_source_list( list_output_type, current_source, '' ) )

                # output the source
                output_csv.writerow( article_list_OUT )

            #-- END check to make sure there are sources --#

        #-- END check to see if an article is passed in. --#

        #return article_list_OUT

    #-- END method render_article_source_per_line() --#


    def render( self ):

        """
            Assumes query set of articles has been placed in this instance.
               Uses the query set to output CSV data in the format specified in
               the output_type instance variable.  If one line per article, has
               sets of columns for as many authors and sources as are present in
               the articles with the most authors and sources, respectively.

            Preconditions: assumes that we have a query set of articles stored
               in the instance.  If not, does nothing, returns empty string.

            Postconditions: returns the CSV network data, in a string.

            Parameters:
            - request_IN - django HTTP request instance that contains parameters we use to generate network data.

            Returns:
            - String - CSV output for the network described by the articles selected based on the parameters passed in.
        """

        # return reference
        csv_OUT = ''

        # declare variables
        article_data_query_set = None
        current_topic_count = -1
        current_location_count = -1
        current_author_count = -1
        article_source_set = None
        current_source_count = -1
        topic_max = -1
        location_max = -1
        author_max = -1
        source_max = -1
        output_type_IN = ''

        # Variables for using django magic to derive counts.
        #counts_query_set = None
        #count_results = None
        #magic_author_max = -1
        #magic_source_max = -1

        header_list = None
        current_article_data = None
        output_string_buffer = None
        output_csv = None
        current_article_list = None
        #current_list_of_article_lists = None

        # first, get an article query set based on the input parameters.
        #article_query_set = output_create_network_query_set( request_IN )
        article_data_query_set = self.query_set

        # first, need to figure out max number of authors, sources - Loop over the
        #    article query set to figure out the max of each.
        for current_article_data in article_data_query_set:

            # retrieve source and author counts.
            current_topic_count = current_article_data.topics.count()
            current_location_count = current_article_data.locations.count()
            current_author_count = current_article_data.article_author_set.count()
            
            # get sources, then count().
            article_source_set = current_article_data.get_quoted_article_sources_qs()
            current_source_count = article_source_set.count()

            # compare current counts to max counts, update max if current is
            #    greater.
            if ( current_topic_count > topic_max ):

                topic_max = current_topic_count

            #-- END topic count max check. --#

            if ( current_location_count > location_max ):

                location_max = current_location_count

            #-- END location count max check. --#

            if ( current_author_count > author_max ):

                author_max = current_author_count

            #-- END author count max check. --#

            if ( current_source_count > source_max ):

                source_max = current_source_count

            #-- END author count max check. --#

        #-- END loop over articles to get max number of sources, authors. --#

        # Store the max counts.
        self.max_topics = topic_max
        self.max_locations = location_max
        self.max_authors = author_max
        self.max_sources = source_max

        # Might be able to use django aggregate magic for this, instead.
        # annotate, aggregate query string to retrieve author_count.  Works, but is
        #    buggy in 1.1.
        #counts_query_set = article_query_set.annotate( author_count_JSM = Count( 'article_author' ) )
        #count_results = counts_query_set.aggregate( max_authors = Max( 'author_count_JSM' ) )
        #magic_author_max = count_results[ 'max_authors' ]

        # annotate, aggregate query string to retrieve source_count.  Works, but is
        #    buggy in 1.1.
        #counts_query_set = article_query_set.annotate( source_count_JSM = Count( 'article_source' ) )
        #count_results = counts_query_set.aggregate( max_sources = Max( 'source_count_JSM' ) )
        #magic_source_max = count_results[ 'max_sources' ]

        # Then, once we know the max author and source counts, we loop over each
        #    article and add it to the CSV output.

        # Initialize CSV output.
        output_string_buffer = StringIO()
        output_csv = csv.writer( output_string_buffer )
        self.csv_output = output_csv

        # get output type
        output_type_IN = self.output_type

        # render the header.
        header_list = self.create_header_list()
        output_csv.writerow( header_list )

        if ( output_type_IN == CsvArticleOutput.ARTICLE_OUTPUT_TYPE_ARTICLE_PER_LINE ):

            # loop over articles.
            for current_article_data in article_data_query_set:

                # pass current_article to render_article_per_line, place result
                #    in the output csv file.
                current_article_list = self.render_article_per_line( current_article_data )

                # got something back?
                if ( current_article_list ):

                    # yes - add it to the output.
                    output_csv.writerow( current_article_list )

                #-- END check to see if we got a list back. --#

            #-- END loop over articles to output to CSV.

        elif ( output_type_IN == CsvArticleOutput.ARTICLE_OUTPUT_TYPE_SOURCE_PER_LINE ):

            # loop over articles.
            for current_article_data in article_data_query_set:

                # pass current_article CSV output buffer to
                #    render_article_source_per_line, let it deal with placing
                #    each source's row in the CSV output.
                self.render_article_source_per_line( current_article_data, output_csv )

            #-- END loop over articles to output to CSV.

        elif ( output_type_IN == CsvArticleOutput.ARTICLE_OUTPUT_TYPE_AUTHOR_PER_LINE ):

            # loop over articles.
            for current_article_data in article_data_query_set:

                # pass current_article CSV output buffer to
                #    render_article_author_per_line, let it deal with placing
                #    each author's row in the CSV output.
                self.render_article_author_per_line( current_article_data, output_csv )

            #-- END loop over articles to output to CSV.

        #-- END check to see what our output type is --#

        # debug output
        #output_csv.writerow( [ author_max, source_max ] )
        #output_csv.writerow( [ magic_author_max, magic_source_max ] )

        # store the CSV file in our output string.
        csv_OUT = output_string_buffer.getvalue()

        # close the string buffer.
        output_string_buffer.close()

        return csv_OUT

    #-- END render_articles() --#


    def set_output_type( self, value_IN ):

        """
            Method: set_output_type()

            Purpose: accepts an output type, stores it in instance.

            Params:
            - value_IN - String output type value.
        """

        # got a request?
        if ( value_IN ):

            # store request
            self.output_type = value_IN

        #-- END check to see if we have a value --#

    #-- END method set_output_type() --#


    def set_query_set( self, value_IN ):

        """
            Method: set_request()

            Purpose: accepts a request, stores it in instance, then grabs the POST
               from the request and stores that as the params.

            Params:
            - request_IN - django HTTPRequest instance.
        """

        # got a request?
        if ( value_IN ):

            # store request
            self.query_set = value_IN

        #-- END check to see if we have a value --#

    #-- END method set_query_set() --#


#-- END class CsvArticleOutput --#