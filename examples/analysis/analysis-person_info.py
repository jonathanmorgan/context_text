from __future__ import unicode_literals

# python package imports
import six

# django imports
from django.contrib.auth.models import User

# sourcenet imports
from sourcenet.models import Analysis_Reliability_Ties
from sourcenet.models import Article
from sourcenet.models import Person

#-------------------------------------------------------------------------------
# class definitions
#-------------------------------------------------------------------------------


class Analysis_Person_Info( object ):
    
    '''
    Creates data structured as follows, in self.coder_index_to_data_map:

    - self.coder_index_to_data_map - map of coder index to coder data.  Data for each coder is in a dictionary with the following keys:

        - self.PROP_CODER_AUTHOR_DATA = "coder_author_data" - maps to dictionary that maps author IDs of all authors the coder found in the set of articles processed by this class to a dictionary of information on each author.  Author info dictionary includes:

            - self.PROP_AUTHOR_SHARED_SOURCE_INFO = "author_shared_source_info" - refers to dictionary that maps source ID to source information for sources quoted by the author who were also quoted by other authors.  For each source, the source info dictionary contains:

                - self.PROP_SHARED_SOURCE_ID = "shared_source_id" - ID of source.
                - self.PROP_SHARED_SOURCE_AUTHOR_LIST = "shared_source_author_list" - list of authors who quoted the source.

            - self.PROP_AUTHOR_SHARED_SOURCE_AUTHORS_LIST = "author_shared_source_authors_list" - list of authors who quoted any one or more sources that the current author also quoted.
            - self.PROP_AUTHOR_SOURCE_COUNT = "author_source_count" - count of sources for the author (length of source list above).
            - self.PROP_AUTHOR_SHARED_SOURCE_COUNT = "author_shared_source_count" - count of shared sources (length of shared source info dictionary above).
            - self.PROP_AUTHOR_ARTICLE_ID_LIST = "author_article_id_list" - list of ids of articles written by author included in analysis.

        - self.PROP_CODER_SOURCE_DATA = "coder_source_data" - maps to dictionary that maps source IDs of all sources the coder found in the set of articles processed by this class to a dictionary of information on each source.  Source info dictionary includes:
        
            - self.PROP_SOURCE_AUTHOR_LIST = "source_author_list" - for each source, a list of the authors who quoted that source.
            
        - self.PROP_CODER_AUTHOR_ID_LIST = "coder_author_id_list" - list of IDs of authors this coder found.
        - self.PROP_CODER_AUTHOR_SOURCE_COUNT_LIST = "coder_author_source_count_list" - list of source counts per author, in same order as list of author IDs.
        - self.PROP_CODER_AUTHOR_SHARED_COUNT_LIST = "coder_author_shared_count_list" - list of shared source counts per author, in same order as list of author IDs.
        - self.PROP_CODER_AUTHOR_ARTICLE_COUNT_LIST = "coder_author_article_count_list" - list of counts of articles in this analysis for each author.
    '''
        
    #----------------------------------------------------------------------
    # constants-ish
    #----------------------------------------------------------------------    

    
    # retrieving reliability row fields by name
    COLUMN_NAME_PREFIX_CODER = "coder"
    COLUMN_NAME_SUFFIX_MENTION_COUNT = "_mention_count"
    COLUMN_NAME_SUFFIX_ID_LIST = "_id_list"
    
    # person types
    PERSON_TYPE_AUTHOR = Analysis_Reliability_Ties.PERSON_TYPE_AUTHOR
    PERSON_TYPE_SOURCE = Analysis_Reliability_Ties.PERSON_TYPE_SOURCE
    
    # information about table.
    TABLE_MAX_CODERS = 3
    
    # coder data property names
    PROP_CODER_AUTHOR_DATA = "coder_author_data"
    PROP_CODER_SOURCE_DATA = "coder_source_data"
    PROP_CODER_AUTHOR_ID_LIST = "coder_author_id_list"
    PROP_CODER_AUTHOR_SOURCE_COUNT_LIST = "coder_author_source_count_list"
    PROP_CODER_AUTHOR_SHARED_COUNT_LIST = "coder_author_shared_count_list"
    PROP_CODER_AUTHOR_ARTICLE_COUNT_LIST = "coder_author_article_count_list"

    # author property names
    PROP_AUTHOR_SOURCE_LIST = "author_source_list"
    PROP_AUTHOR_SHARED_SOURCE_INFO = "author_shared_source_info"
    PROP_AUTHOR_SHARED_SOURCE_AUTHORS_LIST = "author_shared_source_authors_list"
    PROP_AUTHOR_SOURCE_COUNT = "author_source_count"
    PROP_AUTHOR_SHARED_SOURCE_COUNT = "author_shared_source_count"
    PROP_AUTHOR_ARTICLE_ID_LIST = "author_article_id_list"
    
    # shared source property names
    PROP_SHARED_SOURCE_ID = "shared_source_id"
    PROP_SHARED_SOURCE_AUTHOR_LIST = "shared_source_author_list"

    # source property names
    PROP_SOURCE_AUTHOR_LIST = "source_author_list"

    
    #----------------------------------------------------------------------------
    # instance methods
    #----------------------------------------------------------------------------


    def __init__( self, *args, **kwargs ):
        
        # declare instance variables
        self.coder_id_to_instance_map = {}
        self.coder_id_to_index_map = {}
        self.coder_index_to_data_map = {}
        
        # variables to filter reliability row lookup.
        self.reliability_row_label = ""
        
    #-- END method __init__() --#
    

    def get_coder_author_data( self, coder_IN ):
        
        '''
        Accepts a coder instance.  Uses it to get author data associated with
           that coder, and returns data dictionary.  If none found, creates
           empty dictionary, stores it for the coder's ID, then returns it.
        '''
        
        # return reference
        instance_OUT = None
        
        # declare variables
        me = "get_coder_author_data"

        # call method to retrieve data
        instance_OUT = self.get_coder_data_property_dict( coder_IN, self.PROP_CODER_AUTHOR_DATA )
        
        return instance_OUT        
        
    #-- END method get_coder_author_data() --#
    
        
    def get_coder_data( self, coder_IN ):
        
        '''
        Accepts a coder instance.  Uses it to get data associated with that
           coder, and returns data dictionary.  If none found, creates empty
           dictionary, stores it for the coder's ID, then returns it.
        '''
        
        # return reference
        instance_OUT = None
        
        # declare variables
        me = "get_coder_data"
        coder_index_to_data_dict = {}
        coder_user_id = -1
        coder_id_to_index_dict = {}
        coder_index = -1
        
        # make sure we have a coder instance passed in.
        if ( coder_IN is not None ):
        
            # get map from instance
            coder_index_to_data_dict = self.coder_index_to_data_map
            
            # get coder ID.
            coder_user_id = coder_IN.id
            
            # get index for ID.
            coder_id_to_index_dict = self.coder_id_to_index_map
            coder_index = coder_id_to_index_dict.get( coder_user_id, -1 )
            
            # make sure we have an index.  If not, error, return None.
            if ( ( coder_index is not None ) and ( coder_index > 0 ) ):
    
                # Get instance from coder_index_to_data_dict.
                instance_OUT = coder_index_to_data_dict.get( coder_index, None )
                
                # got one?
                if ( instance_OUT is None ):
                
                    # no - need to make new dictionary, store it for user, then
                    #    return it.
                    instance_OUT = {}
                    instance_OUT[ self.PROP_CODER_SOURCE_DATA ] = {}
                    coder_index_to_data_dict[ coder_index ] = instance_OUT
                    
                #-- END check to see if coder already has data. --#
                
            else:
            
                # no index, should be at this point - return None.
                instance_OUT = None
                print( "ERROR - In " + me + ": no index found for coder ID " + str( coder_user_id ) )       
            
            # -- END check to see if index for Coder's ID. --#
                
        #-- END check to see if we have a Coder instance passed in. --#
        
        return instance_OUT        
        
    #-- END method get_coder_data() --#
    
        
    def get_coder_data_property_dict( self, coder_IN, prop_name_IN ):
        
        '''
        Accepts a coder instance.  Uses it to get data associated with that
           coder, and returns data dictionary.  If none found, creates empty
           dictionary, stores it for the coder's ID, then returns it.
        '''
        
        # return reference
        instance_OUT = None
        
        # declare variables
        me = "get_coder_data_property_dict"
        coder_user_id = -1
        coder_data_dict = {}
        
        # make sure we have a coder instance passed in...
        if ( coder_IN is not None ):
        
            # ...and a property name.
            if ( ( prop_name_IN is not None ) and ( prop_name_IN != "" ) ):
        
                # get coder ID.
                coder_user_id = coder_IN.id
        
                # Get coder's data dictionary.
                coder_data_dict = self.get_coder_data( coder_IN )
                
                # retrieve the coder's source data.
                instance_OUT = coder_data_dict.get( prop_name_IN, None )
                
                # got one?
                if ( instance_OUT is None ):
                
                    # no - need to make new dictionary, store it and return it.
                    instance_OUT = {}
                    coder_data_dict[ prop_name_IN ] = instance_OUT
                    
                #-- END check to see if coder already has source data. --#
                    
                print( "++++ In " + me + ": found " + prop_name_IN + " data for user " + str( coder_user_id ) )
            
            #-- END check to see if we have property name passed in. --#
        
        #-- END check to see if we have a Coder instance passed in. --#
        
        return instance_OUT        
        
    #-- END method get_coder_data_property_dict() --#
    
        
    def get_coder_for_index( self, index_IN ):
        
        '''
        Accepts a coder index.  Uses it to get ID of coder associated with that
           index, and returns instance of that User.  If none found, returns
           None.
        '''
        
        # return reference
        instance_OUT = None
        
        # declare variables
        me = "get_coder_for_index"
        coder_id_to_index_dict = {}
        coder_id_to_instance_dict = {}
        coder_user_id = -1
        coder_index = -1
        matching_user_id = -1
        
        # get maps from instance
        coder_id_to_index_dict = self.coder_id_to_index_map
        coder_id_to_instance_dict = self.coder_id_to_instance_map
        
        # first, use index to get coder ID.
        for coder_user_id, coder_index in six.iteritems( coder_id_to_index_dict ):
        
            # check to see if current index matches that passed in.
            if ( index_IN == coder_index ):
            
                # yes - store the ID.
                matching_user_id = coder_user_id
            
            #-- END check to see if indices match --#
            
        #-- END loop over ID-to-index map. --#
        
        print( "++++ In " + me + ": found ID: " + str( matching_user_id ) )
        
        # if we have an ID, use it to get User instance.
        if ( matching_user_id > 0 ):
        
            # we do.  Get instance from coder_id_to_instance_dict.
            instance_OUT = coder_id_to_instance_dict.get( matching_user_id, None )
            print( "++++ In " + me + ": found User: " + str( instance_OUT ) )
        
        #-- END check to see if we have a User ID. --#
        
        return instance_OUT        
        
    #-- END method get_coder_for_index() --#
    
        
    def get_coder_source_data( self, coder_IN ):
        
        '''
        Accepts a coder instance.  Uses it to get source data associated with
           that coder, and returns data dictionary.  If none found, creates
           empty dictionary, stores it for the coder's ID, then returns it.
        '''
        
        # return reference
        instance_OUT = None
        
        # declare variables
        me = "get_coder_source_data"

        # call method to retrieve data
        instance_OUT = self.get_coder_data_property_dict( coder_IN, self.PROP_CODER_SOURCE_DATA )
                
        return instance_OUT        
        
    #-- END method get_coder_source_data() --#
    
        
    def process_articles( self, tag_list_IN = [] ):

        '''
        Grabs articles with a tag in tag_list_IN.  For each, loops through their
           Article_Data to update a dictionary that maps authors to author info,
           sources cited in articles, and counts of the number of articles in
           the selected set that mention each source, as coded by one to three
           different coders.
        '''
        
        # declare variables - retrieving reliability sample.
        me = "process_articles"
        article_qs = None
        article_count = -1
        current_article = None
        article_data_qs = None
        article_data_count = -1
        article_data_counter = -1
        
        # declare variables - compiling information for articles.
        article_id = -1
        author_to_source_info_dict = None
        coder_id_to_instance_dict = None
        coder_id_to_index_dict = None
        current_article_data = None
        coder_index = -1
        coder_1_article_data = None
        coder_2_article_data = None
        coder_3_article_data = None

        #-------------------------------------------------------------------------------
        # process articles to build data
        #-------------------------------------------------------------------------------
        
        # got a tag list?
        if ( ( tag_list_IN is not None ) and ( len( tag_list_IN ) > 0 ) ):

            # get articles with tags in list passed in.
            article_qs = Article.objects.filter( tags__name__in = tag_list_IN )
            
        #-- END check to see if tag list --#
        
        article_qs = article_qs.order_by( "id" )
        
        #article_qs = article_qs[ : 2 ]
            
        # For reference, also build up a dictionary of coder IDs that reference
        #    coder instances, so we know how many coders, and coder IDs to
        #    index, from 1 up, so we can keep them straight when outputting
        #    data.
        coder_id_to_instance_dict = self.coder_id_to_instance_map
        coder_id_to_index_dict = self.coder_id_to_index_map
        
        # loop over the articles.
        article_data_counter = 0
        for current_article in article_qs:
        
            # initialize variables
            article_coder_id_list = []
            author_info_dict = {}
            source_info_dict = {}
            coder_1_article_data = None
            coder_2_article_data = None
            coder_3_article_data = None
        
            # get article_id
            article_id = current_article.id
        
            # get article data for this article
            article_data_qs = current_article.article_data_set.all()
            
            # order by coder ID, descending, so we always use coder 6 as
            #    coder #1 if they coded an article.
            article_data_qs = article_data_qs.order_by( "-coder__id" )
            
            # how many Article_Data?
            article_data_count = len( article_data_qs )
        
            # output summary row.
            print( "- In " + me + ": Article ID = " + str( current_article.id ) + "; Article_Data count = " + str( article_data_count ) )
            
            # for each article, make or update row in reliability table that
            #    matches the author and source, and label if one is specified
            #    in this object's instance (self.reliability_row_label).
            
            # compile information.
            
            # loop over related Article_Data instances, filtering so we only
            #    have one set of data for coder 1 (user ID 6, if no user 6,
            #    user ID 4), and coder 2 (user ID 2).
            for current_article_data in article_data_qs:
            
                article_data_counter += 1
            
                print( "---> In " + me + ": article data #" + str( article_data_counter ) + " - " + str( current_article_data ) )
            
                # get coder and coder's User ID.
                article_data_coder = current_article_data.coder
                article_data_coder_id = article_data_coder.id
                
                # assume that coder ID to index and instance maps are already
                #    set up.
                
                # get index for this user.
                coder_index = coder_id_to_index_dict.get( article_data_coder_id, -1 )
                
                print( "-------> In " + me + ": Coder ID = " + str( article_data_coder_id ) + "; index = " + str( coder_index ) )
                
                # if no article_data yet stored for that index, store this one.
                #    If something already stored, move on.
                if ( coder_index == 1 ):
                
                    # do we have article data stored yet?
                    if ( coder_1_article_data is None ):
                    
                        # no - but we do now - store current.
                        coder_1_article_data = current_article_data
                        
                    #-- END check to see if coder_1_article_data. --#
                
                elif ( coder_index == 2 ):
                
                    # do we have article data stored yet?
                    if ( coder_2_article_data is None ):
                    
                        # no - but we do now - store current.
                        coder_2_article_data = current_article_data
                        
                    #-- END check to see if coder_2_article_data. --#
                
                elif ( coder_index == 3 ):
                
                    # do we have article data stored yet?
                    if ( coder_3_article_data is None ):
                    
                        # no - but we do now - store current.
                        coder_3_article_data = current_article_data
                        
                    #-- END check to see if coder_3_article_data. --#
                
                #-- END check to see which index we have --#
                        
            #-- END loop over related Article_Data
            
            # call process_relations for coder 1 if instance.
            if ( coder_1_article_data is not None ):

                print( "\n\nIn " + me + ": article " + str( article_id ) + ", processing coder 1\n" )
                self.process_relations( coder_1_article_data )
                
            #-- END check to see if coder_1_article_data --#
            
            # call process_relations for coder 2 if instance.
            if ( coder_2_article_data is not None ):

                # call process_relations for coder 2.
                print( "\n\nIn " + me + ": article " + str( article_id ) + ", processing coder 2\n" )
                self.process_relations( coder_2_article_data )
                
            #-- END check to see if coder_2_article_data --#
                        
            # call process_relations for coder 2 if instance.
            if ( coder_3_article_data is not None ):

                # call process_relations for coder 3.
                print( "\n\nIn " + me + ": article " + str( article_id ) + ", processing coder 3\n" )
                self.process_relations( coder_3_article_data )
            
            #-- END check to see if coder_3_article_data --#
        
        #-- END loop over articles. --#
        
        # now, look over all the resulting data to update each coder's author
        #    data so it includes information on sources shared between authors.
        self.update_author_shared_sources()
        
        # finally, summarize data.
        self.summarize_data()
        
        # summary
        print( "" )

        if ( ( self.reliability_row_label is not None ) and ( self.reliability_row_label != "" ) ):
            print( "Assigned label " + self.reliability_row_label + " to created rows." )
        #-- END check to see if label set. --#
            
        article_count = article_qs.count()
        print( "Processed " + str( article_count ) + " Articles." )
        print( "Processed " + str( article_data_counter ) + " Article_Data records." )

    #-- END method process_articles() --#


    def process_relations( self, article_data_IN ):
        
        '''
        Accepts Article_Data instance whose relations we need to process.  For
           each source, updates author and relation information.
        '''
        
        # return reference
        status_OUT = ""
        
        # declare variables
        me = "process_relations"
        article_id = -1
        article_data_coder = None
        article_author_qs = None
        article_source_qs = None
        current_author = None
        author_person = None
        author_info_dict = None
        current_source = None
        source_person = None
        
        # make sure we have an instance
        if ( article_data_IN is not None ):
        
            # get article ID.
            article_id = article_data_IN.article_id
            
            # Get coder info...
            article_data_coder = article_data_IN.coder
            
            # ... author QuerySet...
            article_author_qs = article_data_IN.article_author_set.all()
                        
            # ...and source QuerySet.
            article_source_qs = article_data_IN.article_source_set.all()
            
            # for each author...
            for current_author in article_author_qs:
            
                # get author person.
                author_person = current_author.person
                
                # update author article id list
                self.update_author_article_id_list( article_data_coder, author_person, article_id )
                    
                # update author info for each related source.
                for current_source in article_source_qs:
                
                    # get source person
                    source_person = current_source.person
                    
                    # call method to update author info.
                    self.update_author_info( author_person, source_person, article_data_coder )
                
                    # call method to update source info.
                    self.update_source_info( author_person, source_person, article_data_coder )
                    
                #-- END loop over sources --#

            #-- END check to see if QuerySet passed in. --#  
        
        #-- END check to see if Coder present --#
        
        return status_OUT
        
    #-- END method process_relations() --#


    def summarize_data( self ):
        
        '''
        Uses internal data to create summary information, for ease of analysis.
        
        Preconditions: assumes that all update_*() methods have been called
           already such that data is processed and ready to be summarized.
           
        Postconditions: updates coder, author, and source info dictionaries with
           summary information.
        '''
        
        # return reference
        status_OUT = None

        # declare variables
        me = "summarize_data"
        coder_index_to_data_dict = None
        coder_index = -1
        coder_data_dict = None
        coder_author_id_list = None
        coder_author_source_count_list = None
        coder_author_shared_count_list = None
        author_id = -1
        author_info = None
        source_list = None
        source_count = -1
        shared_source_info = None
        shared_source_count = -1
        article_count = -1
        author_article_id_list = None
        coder_author_article_count_list = None
        
        print( "" )
        print( "Start of " + me + "():" )
        
        # get dict that holds map of coder index to coder data.
        coder_index_to_data_dict = self.coder_index_to_data_map
                
        # loop over the dictionary to process each coder/index.
        for coder_index, coder_data_dict in six.iteritems( coder_index_to_data_dict ):
        
            print( "Summarizing coder index " + str( coder_index ) )
        
            # initialize data.
            coder_author_id_list = []
            coder_author_source_count_list = []
            coder_author_shared_count_list = []
            coder_author_article_count_list = []

            # retrieve author data dictionary.
            author_id_to_data_dict = coder_data_dict.get( self.PROP_CODER_AUTHOR_DATA, None )
            
            # loop over authors
            for author_id, author_info in six.iteritems( author_id_to_data_dict ):
        
                # initialize variables    
                source_list = None
                source_count = -1
                shared_source_info = None
                shared_source_count = -1
                
                # add id to ID list
                coder_author_id_list.append( author_id )
        
                # get source list...
                source_list = author_info.get( self.PROP_AUTHOR_SOURCE_LIST, None )
            
                # ...and shared source info from author data.
                shared_source_info = author_info.get( self.PROP_AUTHOR_SHARED_SOURCE_INFO, None )
                
                # get lengths and add to author info and appropriate lists.
                
                # source count
                source_count = 0
                if ( source_list is not None ):
                
                    # got a source list.
                    source_count = len( source_list )
                    
                #-- END check to see if list is None --#
                author_info[ self.PROP_AUTHOR_SOURCE_COUNT ] = source_count
                coder_author_source_count_list.append( source_count )
            
                # shared source count
                shared_source_count = 0
                if ( shared_source_info is not None ):

                    shared_source_count = len( shared_source_info )
                    
                #-- END check to see if dictionary is None --#
                author_info[ self.PROP_AUTHOR_SHARED_SOURCE_COUNT ] = shared_source_count
                coder_author_shared_count_list.append( shared_source_count )
                
                # get author's article count and add to coder list.
                author_article_id_list = author_info.get( self.PROP_AUTHOR_ARTICLE_ID_LIST, [] )
                article_count = len( author_article_id_list )
                coder_author_article_count_list.append( article_count )
                print( "******** In " + me + "(): Summarizing coder index " + str( coder_index ) + "; author " + str( author_id ) + "; article ID list = " + str( author_article_id_list ) )
            
            #-- END loop over authors. --#
            
            # add lists to coder's data.
            coder_data_dict[ self.PROP_CODER_AUTHOR_ID_LIST ] = coder_author_id_list
            coder_data_dict[ self.PROP_CODER_AUTHOR_SOURCE_COUNT_LIST ] = coder_author_source_count_list
            coder_data_dict[ self.PROP_CODER_AUTHOR_SHARED_COUNT_LIST ] = coder_author_shared_count_list
            coder_data_dict[ self.PROP_CODER_AUTHOR_ARTICLE_COUNT_LIST ] = coder_author_article_count_list
            
        #-- END loop over coders. --#
        
        return status_OUT
        
    #-- END method summarize_data --#


    def update_author_article_id_list( self, coder_user_IN, author_person_IN, article_id_IN ):
        
        # return reference
        status_OUT = ""
        
        # declare variables
        me = "update_author_article_id_list"
        author_person_id = None
        source_person_id = None
        coder_author_data_dict = None
        author_info_dict = None
        author_article_id_list = None
        
        # make sure we have an author person...
        if ( author_person_IN is not None ):
        
            # get ID
            author_person_id = author_person_IN.id
        
            # ...and a coder.
            if ( coder_user_IN is not None ):
            
                # got everything we need.  Get data for the current coder.
                coder_author_data_dict = self.get_coder_author_data( coder_user_IN )
                
                # got something back?
                if ( coder_author_data_dict is not None ):

                    # yes.  Get author info.
                    author_info_dict = coder_author_data_dict.get( author_person_id, None )
                    
                    # got any?
                    if ( author_info_dict is None ):
                    
                        # no.  Add some.
                        author_info_dict = {}
                        author_info_dict[ self.PROP_AUTHOR_SOURCE_LIST ] = []
                        author_info_dict[ self.PROP_AUTHOR_ARTICLE_ID_LIST ] = []
                        coder_author_data_dict[ author_person_id ] = author_info_dict
                        
                    #-- END check to see if author info present. --#
                    
                    # Should have one now.  Get list of articles by this author.
                    author_article_id_list = author_info_dict.get( self.PROP_AUTHOR_ARTICLE_ID_LIST, None )
                    
                    # got a list?
                    if ( author_article_id_list is None ):
                    
                        # no - first time author processed. --#
                        author_article_id_list = []
                        author_info_dict[ self.PROP_AUTHOR_ARTICLE_ID_LIST ] = author_article_id_list
                    
                    #-- END check to see if list of author's related sources is present. --#
                    
                    # Is article_id in list?
                    if ( article_id_IN not in author_article_id_list ):
                    
                        # no.  Add it.
                        author_article_id_list.append( article_id_IN )
                        
                    #-- END check to see if source in author's source list --#
                    
                else:
                
                    # error.  Should always have source info after calling
                    #    get_coder_author_data().
                    pass
                
                #-- END check to see if we have author info --#
            
            #-- END check to make sure we have a coder. --#
        
        #-- END check for author person --#
        
        return status_OUT
    
    #-- END method update_author_article_id_list() --#


    def update_author_info( self, author_person_IN, source_person_IN, coder_user_IN ):
        
        # return reference
        status_OUT = ""
        
        # declare variables
        me = "update_author_info"
        author_person_id = None
        source_person_id = None
        coder_author_data_dict = None
        author_info_dict = None
        author_source_list = None
        
        # make sure we have an author person...
        if ( author_person_IN is not None ):
        
            # get ID
            author_person_id = author_person_IN.id
        
            # ...and a source person...
            if ( source_person_IN is not None ):
            
                # get ID
                source_person_id = source_person_IN.id
            
                # ...and a coder.
                if ( coder_user_IN is not None ):
                
                    # got everything we need.  Get data for the current coder.
                    coder_author_data_dict = self.get_coder_author_data( coder_user_IN )
                    
                    # got something back?
                    if ( coder_author_data_dict is not None ):

                        # yes.  Get author info.
                        author_info_dict = coder_author_data_dict.get( author_person_id, None )
                        
                        # got any?
                        if ( author_info_dict is None ):
                        
                            # no.  Add some.
                            author_info_dict = {}
                            author_info_dict[ self.PROP_AUTHOR_SOURCE_LIST ] = []
                            author_info_dict[ self.PROP_AUTHOR_ARTICLE_ID_LIST ] = []
                            coder_author_data_dict[ author_person_id ] = author_info_dict
                            
                        #-- END check to see if author info present. --#
                        
                        # Should have one now.  Get list of sources quoted by
                        #    this author.
                        author_source_list = author_info_dict.get( self.PROP_AUTHOR_SOURCE_LIST, None )
                        
                        # got a list?
                        if ( author_source_list is None ):
                        
                            # no - first time author processed. --#
                            author_source_list = []
                            author_info_dict[ self.PROP_AUTHOR_SOURCE_LIST ] = author_source_list
                        
                        #-- END check to see if list of author's related sources is present. --#
                        
                        # Is source in list?
                        if ( source_person_id not in author_source_list ):
                        
                            # no.  Add it.
                            author_source_list.append( source_person_id )
                            
                        #-- END check to see if source in author's source list --#
                        
                    else:
                    
                        # error.  Should always have source info after calling
                        #    get_coder_author_data().
                        pass
                    
                    #-- END check to see if we have author info --#
                
                #-- END check to make sure we have a coder. --#
            
            #-- END check to make sure we have source person. --#
        
        #-- END check for author person --#
        
        return status_OUT
    
    #-- END method update_author_info() --#


    def update_author_shared_sources( self ):
        
        '''
        Within the data for each coder (as defined by index, rather than a coder
           ID), looks through the source data to find instances where a source
           was quoted by multiple authors, then updates the authors' data so it
           contains lists of the sources who were shared and the other authors
           who quoted each source.
           
        Preconditions: this method is invoked at the end of process_articles().
           If you invoke it on its own, you must already have called
           process_articles() such that the author and source data are populated
           for each coder, as referenced by the variable
           self.coder_index_to_data_map.
           
        Postconditions: the data for each coder is updated to include a list of
           the shared sources for the author, a list of authors to which the
           current author is related based on shared sources, and an accounting
           per source of authors who also quoted that source.
        '''
        
        # return reference
        status_OUT = ""
        
        # declare variables
        me = "update_author_shared_sources"
        coder_index_to_data_dict = None
        coder_index = -1
        coder_data_dict = None
        author_id_to_data_dict = None
        source_id_to_data_dict = None
        source_id = -1
        source_data_dict = None
        source_author_list = None
        source_author_count = -1
        
        # declare variables - processing for sources with multiple authors.
        shared_author_id = -1
        shared_author_data = None
        author_shared_sources = None
        author_related_authors = None
        shared_source_dict = None
        current_related_author_id = -1

        print( "" )
        print( "Start of " + me + "():" )

        # retrieve coder data dict.
        coder_index_to_data_dict = self.coder_index_to_data_map
        
        # loop over the dictionary to process each index.
        for coder_index, coder_data_dict in six.iteritems( coder_index_to_data_dict ):
        
            # retrieve author and source data dictionaries.
            author_id_to_data_dict = coder_data_dict.get( self.PROP_CODER_AUTHOR_DATA, None )
            source_id_to_data_dict = coder_data_dict.get( self.PROP_CODER_SOURCE_DATA, None )
            
            # start with source data - loop looking for sources with more than
            #    one author.
            for source_id, source_data_dict in six.iteritems( source_id_to_data_dict ):
            
                # get author list.
                source_author_list = source_data_dict.get( self.PROP_SOURCE_AUTHOR_LIST, None )
                
                # get count of authors for source
                source_author_count = len( source_author_list )
                
                # if greater than 1, need to process.
                if ( source_author_count > 1 ):
                
                    print( "In " + me + ": multiple authors ( " + str( source_author_list ) + " for source " + str( source_id ) )
                    
                    # for each author, need to get their data and add info on
                    #    shared source.
                    for shared_author_id in source_author_list:
                    
                        # get data for author
                        shared_author_data = author_id_to_data_dict[ shared_author_id ]
                        
                        # see if the author has anything stored for shared
                        #    sources.
                        author_shared_sources = shared_author_data.get( self.PROP_AUTHOR_SHARED_SOURCE_INFO, None )
                        author_related_authors = shared_author_data.get( self.PROP_AUTHOR_SHARED_SOURCE_AUTHORS_LIST, None )
                        if ( author_shared_sources is None ):
                        
                            # no.  Add shared source info and list of authors
                            #    with whom the current author shared sources.
                            author_shared_sources = {}
                            shared_author_data[ self.PROP_AUTHOR_SHARED_SOURCE_INFO ] = author_shared_sources
                            author_related_authors = []
                            shared_author_data[ self.PROP_AUTHOR_SHARED_SOURCE_AUTHORS_LIST ] = author_related_authors
                        
                        #-- END check to see if author has shared source information --#
                        
                        # add information on source to shared source info.
                        #   - in self.PROP_AUTHOR_SHARED_SOURCE_INFO
                        
                        # is shared source already captured?
                        if ( source_id not in author_shared_sources ):
                        
                            # no.  Populate dictionary...
                            shared_source_dict = {}
                            shared_source_dict[ self.PROP_SHARED_SOURCE_ID ] = source_id
                            shared_source_dict[ self.PROP_SHARED_SOURCE_AUTHOR_LIST ] = source_author_list

                            # ...then add it to author's shared source info.
                            author_shared_sources[ source_id ] = shared_source_dict
                            
                        else:
                        
                            # if present, output message, but also leave alone.
                            print( "In " + me + ": Source " + str( source_id ) + " already in shared sources for author " + str( shared_author_id ) + ".  This should not have happened..." )
                            
                        #-- END check to see if source is in author's list of shared sources. --#
                        
                        # make sure all related authors are in list of authors
                        #   with whom the current author shares sources.
                        for current_related_author_id in source_author_list:
                        
                            # is author in master list?
                            if ( current_related_author_id not in author_related_authors ):
                            
                                # no.  Add it.
                                author_related_authors.append( current_related_author_id )
                                
                            #-- END check to see if related author is in author's list. --#
                         
                        #-- END loop over related authors for current source --#
                    
                    #-- END loop over shared author data. --#
                
                else:
                
                    # only one author for this source - moving on.
                    pass
                
                #-- END check to see if more than one author for the current source. --#
            
            #-- END loop over sources. --#
        
        #-- END loop over coders. --#
        
        return status_OUT
    
    #-- END method update_author_shared_sources() --#


    def update_source_info( self, author_person_IN, source_person_IN, coder_user_IN ):
        
        # return reference
        status_OUT = ""
        
        # declare variables
        me = "update_source_info"
        author_person_id = None
        source_person_id = None
        coder_source_data_dict = None
        source_info_dict = None
        source_author_list = None
        
        # make sure we have an author person...
        if ( author_person_IN is not None ):
        
            # get ID
            author_person_id = author_person_IN.id
        
            # ...and a source person...
            if ( source_person_IN is not None ):
            
                # get ID
                source_person_id = source_person_IN.id
            
                # ...and a coder.
                if ( coder_user_IN is not None ):
                
                    # got everything we need.  Get data for the current coder.
                    coder_source_data_dict = self.get_coder_source_data( coder_user_IN )
                    
                    # got something back?
                    if ( coder_source_data_dict is not None ):

                        # yes.  Get source info.
                        source_info_dict = coder_source_data_dict.get( source_person_id, None )
                        
                        # got any?
                        if ( source_info_dict is None ):
                        
                            # no.  Add some.
                            source_info_dict = {}
                            source_info_dict[ self.PROP_SOURCE_AUTHOR_LIST ] = []
                            coder_source_data_dict[ source_person_id ] = source_info_dict
                            
                        #-- END check to see if source info present. --#
                        
                        # Should have one now.  Get list of authors who quoted
                        #    this source.
                        source_author_list = source_info_dict.get( self.PROP_SOURCE_AUTHOR_LIST, None )
                        
                        # got a list?
                        if ( source_author_list is None ):
                        
                            # no - first time source and author are related. --#
                            source_author_list = []
                            source_info_dict[ self.PROP_SOURCE_AUTHOR_LIST ] = source_author_list
                        
                        #-- END check to see if list of source's related authors is present. --#
                        
                        # Is author in list?
                        if ( author_person_id not in source_author_list ):
                        
                            # no.  Add it.
                            source_author_list.append( author_person_id )
                            
                        #-- END check to see if author in source's author list --#
                    
                    else:
                    
                        # error.  Should always have source info after calling
                        #    get_coder_source_data().
                        pass
                    
                    #-- END check to see if we have source info --#
                
                #-- END check to make sure we have a coder. --#
            
            #-- END check to make sure we have source persons. --#
        
        #-- END check for author person --#
        
        return status_OUT
    
    #-- END method update_source_info() --#


#-- END class Analysis_Person_Info --#


# declare variables
my_analysis_instance = None
coder_rs = None
current_coder = None
current_coder_id = -1
coder_index = -1
coder_id_to_index_dict = {}
coder_id_to_instance_dict = {}
tag_list = None
label = ""

# get coders we want to include in analysis.
coder_rs = User.objects.filter( id__in = [ 2, 4, 6 ] )

# set up coder maps.
coder_index = 0
for current_coder in coder_rs:

    # increment coder index
    coder_index = coder_index + 1

    # get coder's user id
    current_coder_id = current_coder.id
    
    # add to ID-to-instance map
    coder_id_to_instance_dict[ current_coder_id ] = current_coder
    
    # add to ID-to-index map
    coder_id_to_index_dict[ current_coder_id ] = coder_index

#-- END loop over coders --#

# manually set up the ID to index map so the humans both map to 1, automated
#    maps to 2.
coder_id_to_index_dict[ 6 ] = 1
coder_id_to_index_dict[ 4 ] = 1
coder_id_to_index_dict[ 2 ] = 2

# make reliability instance
my_analysis_instance = Analysis_Person_Info()

# place dictionaries in instance.
my_analysis_instance.coder_id_to_instance_map = coder_id_to_instance_dict
my_analysis_instance.coder_id_to_index_map = coder_id_to_index_dict

# label for reliability rows created and used in this session.
label = "prelim_network_fixed_authors"
my_analysis_instance.reliability_row_label = label

# process articles
tag_list = [ "prelim_network", ]
my_analysis_instance.process_articles( tag_list )

#output lists of counts of sources and shared source by author

# declare variables - looking at data
coder_index_to_data_dict = None
coder_index = -1
coder_data_dict = None
coder_author_id_list = None
coder_author_source_count_list = None
coder_author_shared_count_list = None
coder_author_article_count_list = None
mean_source_count = -1
mean_shared_count = -1
mean_article_count = -1
author_index = -1
shared_count = -1
temp_author_id_list = []
temp_source_count_list = []
temp_shared_count_list = []
temp_article_count_list = []

# for each coder, get authors.
coder_index_to_data_dict = my_analysis_instance.coder_index_to_data_map
        
# loop over the dictionary to process each index.
for coder_index, coder_data_dict in six.iteritems( coder_index_to_data_dict ):

    # get data for coder
    coder_author_id_list = coder_data_dict.get( Analysis_Person_Info.PROP_CODER_AUTHOR_ID_LIST, None )
    coder_author_source_count_list = coder_data_dict.get( Analysis_Person_Info.PROP_CODER_AUTHOR_SOURCE_COUNT_LIST, None )
    coder_author_shared_count_list = coder_data_dict.get( Analysis_Person_Info.PROP_CODER_AUTHOR_SHARED_COUNT_LIST, None )
    coder_author_article_count_list = coder_data_dict.get( Analysis_Person_Info.PROP_CODER_AUTHOR_ARTICLE_COUNT_LIST, None )

    # output
    print( "" )
    print( "================================================================================" )
    print( "Data for Coder index " + str( coder_index ) + ":" )

    print( "" )
    print( "==> All authors" )
    print( "- author ID list = " + str( coder_author_id_list ) )    
    print( "- author source count list = " + str( coder_author_source_count_list ) )    
    print( "- author shared count list = " + str( coder_author_shared_count_list ) )    
    print( "- author article count list = " + str( coder_author_article_count_list ) )    

    # and some computations

    # author count
    print( "- author count = " + str( len( coder_author_id_list ) ) )
    
    # mean source count per author
    mean_source_count = float( sum( coder_author_source_count_list ) ) / len( coder_author_source_count_list )
    print( "- mean source count per author = " + str( mean_source_count ) )
    
    # mean shared count per author
    mean_shared_count = float( sum( coder_author_shared_count_list ) ) / len( coder_author_shared_count_list )
    print( "- mean shared count per author = " + str( mean_shared_count ) )
    
    # mean article count per author
    mean_article_count = float( sum( coder_author_article_count_list ) ) / len( coder_author_article_count_list )
    print( "- mean article count per author = " + str( mean_article_count ) )
    
    # the same, but just for those with shared sources.
    author_index = -1
    temp_author_id_list = []
    temp_source_count_list = []
    temp_shared_count_list = []
    temp_article_count_list = []

    for shared_count in coder_author_shared_count_list:
    
        # increment index
        author_index += 1
        
        # greater than 0?
        if ( shared_count > 0 ):
        
            # yes, add info to temp lists.
            temp_author_id_list.append( coder_author_id_list[ author_index ] )
            temp_source_count_list.append( coder_author_source_count_list[ author_index ] )
            temp_shared_count_list.append( coder_author_shared_count_list[ author_index ] )
            temp_article_count_list.append( coder_author_article_count_list[ author_index ] )
            
        #-- END check to see if shared count > 0 --#
    
    #-- END loop over shared_count_list --#

    print( "" )
    print( "==> Authors with shared sources" )
    print( "- author ID list = " + str( temp_author_id_list ) )    
    print( "- author source count list = " + str( temp_source_count_list ) )    
    print( "- author shared count list = " + str( temp_shared_count_list ) )    
    print( "- author article count list = " + str( temp_article_count_list ) )    

    # and some computations

    # author count
    print( "- author count = " + str( len( temp_author_id_list ) ) )
    
    # mean source count per author with shared sources
    mean_source_count = float( sum( temp_source_count_list ) ) / len( temp_source_count_list )
    print( "- mean source count per author with shared sources = " + str( mean_source_count ) )
    
    # mean shared count per author with shared sources
    mean_shared_count = float( sum( temp_shared_count_list ) ) / len( temp_shared_count_list )
    print( "- mean shared count per author with shared sources = " + str( mean_shared_count ) )
    
    # mean article count per author
    mean_article_count = float( sum( temp_article_count_list ) ) / len( temp_article_count_list )
    print( "- mean article count per author = " + str( mean_article_count ) )
    
#-- END loop over coders. --#