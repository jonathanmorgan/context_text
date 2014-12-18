from __future__ import unicode_literals

'''
Copyright 2010-2014 Jonathan Morgan

This file is part of http://github.com/jonathanmorgan/sourcenet.

sourcenet is free software: you can redistribute it and/or modify it under the terms of the GNU Lesser General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.

sourcenet is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.

You should have received a copy of the GNU Lesser General Public License along with http://github.com/jonathanmorgan/sourcenet. If not, see http://www.gnu.org/licenses/.
'''

#===============================================================================
# imports (in alphabetical order by package, then by name)
#===============================================================================


# python base imports
#from datetime import date
from datetime import datetime
import operator

# django database classes
from django.db.models import Q

# python_utilities
from python_utilities.parameters.param_container import ParamContainer

# Import the classes for our SourceNet application
from sourcenet.models import Article
from sourcenet.models import Article_Data

# Import other Article coder classes
from sourcenet.article_coding.open_calais_article_coder import OpenCalaisArticleCoder

# Import sourcenet shared classes.
from sourcenet.shared.sourcenet_base import SourcenetBase


#===============================================================================
# classes (in alphabetical order by name)
#===============================================================================

class ArticleCoding( SourcenetBase ):


    #---------------------------------------------------------------------------
    # CONSTANTS-ish
    #---------------------------------------------------------------------------

    # network selection parameters we expect. - moved to parent
    #PARAM_START_DATE = 'start_date'   # publication date - articles will be included that were published on or after this date.
    #PARAM_END_DATE = 'end_date'   # publication date - articles will be included that were published on or before this date.
    #PARAM_DATE_RANGE = 'date_range'   # For date range fields, enter any number of paired date ranges, where dates are in the format YYYY-MM-DD, dates are separated by the string " to ", and each pair of dates is separated by two pipes ("||").  Example: 2009-12-01 to 2009-12-31||2010-02-01 to 2010-02-28
    #PARAM_PUBLICATION_LIST = 'publications'   # list of IDs of newspapers you want included.
    #PARAM_TAG_LIST = 'tags_list'   # list of tag values that you want included.
    #PARAM_SECTION_LIST = 'section_list'   # list of tag values that you want included.
    #PARAM_UNIQUE_ID_LIST = 'unique_identifiers'   # list of unique identifiers of articles whose data you want included.
    #PARAM_ARTICLE_ID_LIST = 'article_id_list'   # list of ids of articles whose data you want included.

    # parameters that are unique to this class.
    PARAM_CODER_TYPE = 'coder_type'   # list of ids of articles whose data you want included.

    # constants for parsing date range string - moved to parent
    #PARAM_DATE_RANGE_ITEM_SEPARATOR = '||'
    #PARAM_DATE_RANGE_DATE_SEPARATOR = ' to '
    #PARAM_DATE_RANGE_DATE_FORMAT = '%Y-%m-%d'

    # types of params.
    #PARAM_TYPE_LIST = 'list'
    #PARAM_TYPE_STRING = 'string'

    # Dictionary of parameters to their types, for use in debug method.
    PARAM_NAME_TO_TYPE_MAP = {
        SourcenetBase.PARAM_START_DATE : ParamContainer.PARAM_TYPE_STRING,
        SourcenetBase.PARAM_END_DATE : ParamContainer.PARAM_TYPE_STRING,
        SourcenetBase.PARAM_DATE_RANGE : ParamContainer.PARAM_TYPE_STRING,
        SourcenetBase.PARAM_PUBLICATION_LIST : ParamContainer.PARAM_TYPE_LIST,
        SourcenetBase.PARAM_TAG_LIST : ParamContainer.PARAM_TYPE_LIST,
        SourcenetBase.PARAM_SECTION_LIST : ParamContainer.PARAM_TYPE_LIST,
        SourcenetBase.PARAM_UNIQUE_ID_LIST : ParamContainer.PARAM_TYPE_STRING,
        SourcenetBase.PARAM_ARTICLE_ID_LIST : ParamContainer.PARAM_TYPE_STRING,
        PARAM_CODER_TYPE : ParamContainer.PARAM_TYPE_STRING,
    }

    # variables for choosing yes or no.
    #CHOICE_YES = 'yes'
    #CHOICE_NO = 'no'

    # choices for yes or no decision.
    #CHOICES_YES_OR_NO_LIST = [
    #    ( CHOICE_NO, "No" ),
    #    ( CHOICE_YES, "Yes" )
    #]

    # Article coding implementation choices.
    ARTICLE_CODING_IMPL_OPEN_CALAIS_API = "open_calais_api"
    ARTICLE_CODING_IMPL_CHOICES_LIST = [ ARTICLE_CODING_IMPL_OPEN_CALAIS_API, ]
    ARTICLE_CODING_IMPL_DEFAULT = ARTICLE_CODING_IMPL_OPEN_CALAIS_API


    #---------------------------------------------------------------------------
    # __init__() method
    #---------------------------------------------------------------------------


    def __init__( self ):

        # call parent's __init__()
        super( ArticleCoding, self ).__init__()

        # declare variables
        #self.request = None
        #self.parameters = ParamContainer()

        # define parameters
        #self.define_parameters( ArticleCoding.PARAM_NAME_TO_TYPE_MAP )
        
    #-- END method __init__() --#


    #---------------------------------------------------------------------------
    # instance methods, in alphabetical order
    #---------------------------------------------------------------------------


    def code_article_data( self, query_set_IN ):

        """
            Accepts query set of Articles.  Creates a new instance of the
               ArticleCoder class for coder_type passed in, places the query set
               in it, sets up its instance variables appropriately according to
               the request, then codes the attribution in the articles using the
               coder class.  Returns status message.  Results in Article_Data for
               each attribution detected by the coder in each article.  Checks
               for the attribution to already have been detected using article,
               paragraph number, etc.  If so, does not create an additional
               Article_Data instance (could add a flag for this later if
               needed...).
            Preconditions: assumes that we have a query set of Articles passed
               in that we can store in the instance.  If not, does nothing,
               returns empty string.
            Postconditions: Returns status message.  Results in Article_Data for
               each attribution detected by the coder in each article.  Checks
               for the attribution to already have been detected using article,
               paragraph number, etc.  If so, does not create an additional
               Article_Data instance (could add a flag for this later if
               needed...).

            Parameters:
            - query_set_IN - django HTTP request instance that contains parameters we use to generate network data.

            Returns:
            - String - Status message.
        """

        # return reference
        status_OUT = ''

        # declare variables
        article_coder = None

        # do we have a query set?
        if ( query_set_IN ):

            # create instance of ArticleCoder.
            article_coder = self.get_coder_instance()

            # initialize it.
            article_coder.set_query_set( query_set_IN )
            article_coder.set_person_dictionary( person_dictionary )

            # initialize ArticleCoder instance from params.
            my_params = self.get_param_container()
            article_coder.initialize_from_params( my_params )

            # render and return the result.
            status_OUT = article_coder.code_articles()

            # add some debug?
            if ( ArticleCoder.DEBUG_FLAG == True ):

                # yup.
                status_OUT += "\n\n" + network_data_outputter.debug + "\n\n"

            #-- END check to see if we have debug to output. --#
        #-- END check to make sure we have a query set. --#

        return status_OUT

    #-- END code_article_data() --#


    def create_article_query_set( self, param_prefix_IN = '' ):

        # return reference
        query_set_OUT = None

        # declare variables
        params_IN = None
        start_date_IN = ''
        end_date_IN = ''
        date_range_IN = ''
        publication_list_IN = None
        tag_list_IN = None
        section_list_IN = None
        unique_id_list_IN = ''
        article_id_list_IN = ''
        date_range_list = None
        date_range_pair = None
        range_start_date = None
        range_end_date = None
        date_range_q = None
        date_range_q_list = None
        current_item = None
        current_query = None
        query_list = []

        # get the request
        params_IN = self.get_param_container()

        # got a request?
        if ( params_IN ):

            # retrieve the incoming parameters
            start_date_IN = self.get_param_as_str( param_prefix_IN + SourcenetBase.PARAM_START_DATE, '' )
            end_date_IN = self.get_param_as_str( param_prefix_IN + SourcenetBase.PARAM_END_DATE, '' )
            date_range_IN = self.get_param_as_str( param_prefix_IN + SourcenetBase.PARAM_DATE_RANGE, '' )
            publication_list_IN = self.get_param_as_list( param_prefix_IN + SourcenetBase.PARAM_PUBLICATION_LIST, None )
            tag_list_IN = self.get_param_as_list( param_prefix_IN + SourcenetBase.PARAM_TAG_LIST, None )
            unique_id_list_IN = self.get_param_as_list( param_prefix_IN + SourcenetBase.PARAM_UNIQUE_ID_LIST, None )
            article_id_list_IN = self.get_param_as_list( param_prefix_IN + SourcenetBase.PARAM_ARTICLE_ID_LIST, None )
            section_list_IN = self.get_param_as_list( param_prefix_IN + SourcenetBase.PARAM_SECTION_LIST, None )

            # get all articles to start
            query_set_OUT = Article.objects.all()

            # now filter based on parameters passed in.
            # start date
            if ( start_date_IN != '' ):

                # set up query instance
                current_query = Q( pub_date__gte = start_date_IN )

                # add it to list of queries
                query_list.append( current_query )

            #-- END processing of start_date --#

            # end date
            if ( end_date_IN != '' ):

                # set up query instance
                current_query = Q( pub_date__lte = end_date_IN )

                # add it to list of queries
                query_list.append( current_query )

            #-- END processing of end_date --#

            # date range?
            if ( date_range_IN != '' ):

                # first, break up the string into a list of start and end dates.
                date_range_list = self.parse_date_range( date_range_IN )
                date_range_q_list = []

                # loop over the date ranges, create a Q for each, and then store
                #    that Q in our Q list.
                for date_range_pair in date_range_list:

                    # get start and end datetime.date instances.
                    range_start_date = date_range_pair[ 0 ]
                    range_end_date = date_range_pair[ 1 ]

                    # make Q
                    date_range_q = Q( pub_date__gte = range_start_date ) & Q( pub_date__lte = range_end_date )

                    # add Q to Q list.
                    date_range_q_list.append( date_range_q )

                #-- END loop over date range items. --#

                # see if there is anything in date_range_q_list.
                if ( len( date_range_q_list ) > 0 ):

                    # There is something.  Convert it to one big ORed together
                    #    Q and add that to the list.
                    current_query = reduce( operator.__or__, date_range_q_list )

                    # add this to the query list.
                    query_list.append( current_query )

                #-- END check to see if we have any valid date ranges.

            #-- END processing of date range --#

            # publications
            if ( ( publication_list_IN is not None ) and ( len( publication_list_IN ) > 0 ) ):

                # set up query instance
                current_query = Q( newspaper__id__in = publication_list_IN )

                # add it to the query list
                query_list.append( current_query )

            #-- END processing of publications --#

            # tags
            if ( ( tag_list_IN is not None ) and ( len( tag_list_IN ) > 0 ) ):

                # set up query instance
                current_query = Q( tags__name__in = tag_list_IN )

                # add it to the query list
                query_list.append( current_query )

            #-- END processing of tags --#

            # unique identifiers IN list
            if ( ( unique_id_list_IN is not None ) and ( len( unique_id_list_IN ) > 0 ) ):

                # set up query instance to look for articles with
                #    unique_identifier in the list of values passed in.  Not
                #    quoting, since django should do that.
                current_query = Q( unique_identifier__in = unique_id_list_IN )

                # add it to list of queries
                query_list.append( current_query )

            #-- END processing of unique_identifiers --#

            # article ID IN list
            if ( ( article_id_list_IN is not None ) and ( len( article_id_list_IN ) > 0 ) ):

                # set up query instance to look for articles with
                #    ID in the list of values passed in.  Not
                #    quoting, since django should do that.
                current_query = Q( id__in = article_id_list_IN )

                # add it to list of queries
                query_list.append( current_query )

            #-- END processing of article IDs --#

            # section string list
            if ( ( section_list_IN is not None ) and ( len( section_list_IN ) > 0 ) ):

                # set up query instance to look for articles with
                #    ID in the list of values passed in.  Not
                #    quoting, since django should do that.
                current_query = Q( section__in = section_list_IN )

                # add it to list of queries
                query_list.append( current_query )

            #-- END processing of section names --#

            # now, add them all to the QuerySet - try a loop
            for query_item in query_list:

                # append each filter to query set.
                query_set_OUT = query_set_OUT.filter( query_item )

            #-- END loop over query set items --#

        else:
        
            # no param container present.  Error.
            query_set_OUT = None
        
        #-- END check to make sure we have a param container. --#

        return query_set_OUT

    #-- end method create_query_set() ------------------------------------------


    def get_coder_instance( self ):

        '''
        Assumes there is an output type property specified in the POST parameters
           passed in as part of the current request.  Retrieves this output type,
           creates a NetworkDataOutput implementer instance to match the type,
           then returns the instance.  If no type or unknown type, returns None.
        '''
        
        # return reference
        coder_instance_OUT = None

        # declare variables
        coder_type_IN = ""

        # get output type.
        coder_type_IN = self.get_string_param( self.PARAM_CODER_TYPE, self.ARTICLE_CODING_IMPL_DEFAULT )
        
        # make instance for coder type.
        if ( coder_type_IN == self.ARTICLE_CODING_IMPL_OPEN_CALAIS_API ):
        
            # Open Calais API.
            coder_instance_OUT = OpenCalaisArticleCoder()
        
        else:
        
            # no output type, or unknown.  Make simple output matrix.
            coder_instance_OUT = OpenCalaisArticleCoder()
        
        #-- END check to see what type we have. --#
        
        return coder_instance_OUT

    #-- END get_coder_instance() --#


#-- END class ArticleCoding --#