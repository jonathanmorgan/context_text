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


class Reliability_Ties( object ):
    
    
    #----------------------------------------------------------------------
    # constants-ish
    #----------------------------------------------------------------------    


    # shared author and relation info dictionary field names
    PERSON_ID = "person_id"
    PERSON_NAME = "person_name"
    
    # author info dictionary field names
    SOURCE_ID_TO_INFO_MAP = "source_id_to_info_map"    

    # relation info dictionary field names
    #PERSON_ID = "person_id"
    #PERSON_NAME = "person_name"
    CODER_1_ID_LIST = "coder_1_id_list"
    CODER_1_COUNT = "coder_1_count"
    CODER_2_ID_LIST = "coder_2_id_list"
    CODER_2_COUNT = "coder_2_count"
    CODER_3_ID_LIST = "coder_3_id_list"
    CODER_3_COUNT = "coder_3_count"
    
    # person types
    PERSON_TYPE_AUTHOR = Analysis_Reliability_Ties.PERSON_TYPE_AUTHOR
    PERSON_TYPE_SOURCE = Analysis_Reliability_Ties.PERSON_TYPE_SOURCE
    
    # information about table.
    TABLE_MAX_CODERS = 3

    
    #----------------------------------------------------------------------------
    # instance methods
    #----------------------------------------------------------------------------


    def __init__( self, *args, **kwargs ):
        
        # declare instance variables
        self.author_to_source_info_map = {}
        self.coder_id_to_instance_map = {}
        self.coder_id_to_index_map = {}
        
    #-- END method __init__() --#
    

    def get_author_info( self, person_IN ):
        
        '''
        Accepts author Person instance.  Looks for author in
           self.author_to_source_info_map.  If author ID is associated with a
           dictionary, returns it.  If not, makes one, populates it, stores it
           in map, then returns it.
        '''    

        # return reference
        info_OUT = None
        
        # declare variables
        me = "get_author_info"
        author_to_info_map = None
        person_id = -1
        info_dict = None
        person_name = None
        
        # get author-to-info map
        author_to_info_map = self.author_to_source_info_map

        # get person ID
        person_id = person_IN.id
        
        print( "==== IN " + me + ": author ID = " + str( person_id ) )
        
        # is person in map?
        if ( person_id in author_to_info_map ):
        
            # yes.  Retrieve the info and return it.
            info_OUT = author_to_info_map.get( person_id, None )
            
            print( "++++ In " + me + ": Author info present = " + str( info_OUT ) )
        
        else:
        
            # no.  Make dictionary, populate it, add it to map, then return it.
            info_dict = {}
            person_name = person_IN.get_name_string()
            
            # set values.
            info_dict[ self.PERSON_ID ] = person_id
            info_dict[ self.PERSON_NAME ] = person_name
            info_dict[ self.SOURCE_ID_TO_INFO_MAP ] = {}

            # add to map.
            author_to_info_map[ person_id ] = info_dict
            
            print( "++++ In " + me + ": Author info NOT present. Created new." )
            
            # return the new info object.
            info_OUT = self.get_author_info( person_IN )
        
        #-- END check to see if person in map --#
       
        return info_OUT 
        
    #-- END method get_author_info() --#

    
    def get_coder_for_index( self, index_IN ):
        
        '''
        Accepts a coder index.  Uses it to get ID of coder associated with that
           index, and returns instance of that User.  If none found, returns
           None.
        '''
        
        # return reference
        instance_OUT = None
        
        # declare variables
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
        
        print( "++++ found ID: " + str( matching_user_id ) )
        
        # if we have an ID, use it to get User instance.
        if ( matching_user_id > 0 ):
        
            # we do.  Get instance from coder_id_to_instance_dict.
            instance_OUT = coder_id_to_instance_dict.get( matching_user_id, None )
            print( "++++ found User: " + str( instance_OUT ) )
        
        #-- END check to see if we have a User ID. --#
        
        return instance_OUT        
        
    #-- END method get_coder_for_index() --#
    
        
    def get_source_info( self, person_IN, author_info_IN ):
        
        '''
        Accepts source Person instance and author_info dictionary.  Looks for
           source in nested source info dictionary.  If source ID is associated
           with a dictionary, returns it.  If not, makes one, populates it,
           stores it in source info map, then returns it.
        '''    

        # return reference
        info_OUT = None
        
        # declare variables
        me = "get_source_info"
        source_to_info_map = None
        source_info_dict = None
        person_id = -1
        info_dict = None
        person_name = None
        
        # got author_info?
        if ( author_info_IN is not None ):

            # get source-to-info map
            source_to_info_map = author_info_IN.get( self.SOURCE_ID_TO_INFO_MAP, None )
            
            # got source info map?
            if ( source_to_info_map is not None ):
    
                # yes.  Get source's person ID.
                person_id = person_IN.id
                
                # is person in map?
                if ( person_id in source_to_info_map ):
                
                    # yes.  Retrieve the info and return it.
                    info_OUT = source_to_info_map.get( person_id, None )
                    print( "++++ In " + me + ": Source info already present = " + str( info_OUT ) )
                
                else:
                
                    # no.  Make dictionary, populate it, add it to map, then return it.
                    info_dict = {}
                    person_name = person_IN.get_name_string()
                    
                    # set values.
                    info_dict[ self.PERSON_ID ] = person_id
                    info_dict[ self.PERSON_NAME ] = person_name
                    info_dict[ self.CODER_1_ID_LIST ] = []
                    info_dict[ self.CODER_1_COUNT ] = 0
                    info_dict[ self.CODER_2_ID_LIST ] = []
                    info_dict[ self.CODER_2_COUNT ] = 0
                    info_dict[ self.CODER_3_ID_LIST ] = []
                    info_dict[ self.CODER_3_COUNT ] = 0
                    
                    # add to source info map.
                    source_to_info_map[ person_id ] = info_dict
                    
                    print( "++++ In " + me + ": Source info not present, created new." )

                    # return the new info object.
                    info_OUT = self.get_source_info( person_IN, author_info_IN )
                    
                #-- END check to see if person in map --#
            
            else:
            
                # ERROR - no source info map.  Corrupt author info.
                print( "ERROR - in " + me + ": author info has no map of sources to source info.  Nothing more I can do here." )
                info_OUT = None
            
            #-- END check to make sure author info has source map --#
            
        #-- END check to see if author info --#
       
        return info_OUT 
        
    #-- END method get_source_info() --#

    
    def output_reliability_data( self, label_IN = "" ):
    
        '''
        Accepts a label, which should be applied to the reliability rows output.
           Uses internal map of authors to author info and source info to output
           a row per author-source combination, where each row contains author's
           person ID, source's person ID, and count of articles in which up to
           three coders recorded that the author quoted the source.
           
        Preconditions: expects that you already ran process_articles() with this
           instance.
        '''
    
        # declare variables.
        me = "output_reliability_data"
        author_info_dict_IN = None
        my_author_id = -1
        my_author_info = None
        author_person = None
        author_name = ""
        source_to_info_dict = None
        my_source_id = -1
        my_source_info = None
        reliability_row = None
        source_person = None
        source_name = ""
        my_coder1_id_list = None
        my_coder1_mention_count = -1
        my_coder2_id_list = None
        my_coder2_mention_count = -1
        my_coder3_id_list = None
        my_coder3_mention_count = -1
        coder_count = -1
        coder_id = -1
        coder_instance = None
         
        # get map of authors to author and source info.
        author_info_dict_IN = self.author_to_source_info_map
        
        # loop over authors
        for my_author_id, my_author_info in six.iteritems( author_info_dict_IN ):
        
            # get info for author person
            author_person = Person.objects.get( id = my_author_id )
            author_name = author_person.get_name_string()
            
            # get source info map.
            source_to_info_dict = my_author_info.get( self.SOURCE_ID_TO_INFO_MAP, None )
            
            # loop over sources
            for my_source_id, my_source_info in six.iteritems( source_to_info_dict ):
            
                # create and populate an output row instance per source.
                reliability_row = Analysis_Reliability_Ties()
                
                # label
                reliability_row.label = label_IN
                
                # Author information
                reliability_row.person = author_person
                reliability_row.person_name = author_name
                reliability_row.person_type = Analysis_Reliability_Ties.PERSON_TYPE_AUTHOR
                reliability_row.relation_type = Analysis_Reliability_Ties.RELATION_AUTHOR_TO_SOURCE
                
                # Source information
                source_person = Person.objects.get( id = my_source_id )
                source_name = source_person.get_name_string()
                
                # add to row/model instance.
                reliability_row.relation_person = source_person
                reliability_row.relation_person_name = source_name
                reliability_row.relation_person_type = Analysis_Reliability_Ties.PERSON_TYPE_SOURCE
                
                # Coding information
                my_coder1_id_list = my_source_info.get( self.CODER_1_ID_LIST )
                my_coder1_mention_count = my_source_info.get( self.CODER_1_COUNT )
                print( "---> In " + me + ": coder 1 id list = " + str( my_coder1_id_list ) + "; mention_count = " + str( my_coder1_mention_count ) )
                my_coder2_id_list = my_source_info.get( self.CODER_2_ID_LIST )
                my_coder2_mention_count = my_source_info.get( self.CODER_2_COUNT )
                print( "---> In " + me + ": coder 2 id list = " + str( my_coder2_id_list ) + "; mention_count = " + str( my_coder2_mention_count ) )
                my_coder3_id_list = my_source_info.get( self.CODER_3_ID_LIST )
                my_coder3_mention_count = my_source_info.get( self.CODER_3_COUNT )
                print( "---> In " + me + ": coder 3 id list = " + str( my_coder3_id_list ) + "; mention_count = " + str( my_coder3_mention_count ) )

                # add to row/model instance.
                
                # coder 1
                if ( ( my_coder1_id_list is not None ) and ( len( my_coder1_id_list ) > 0 ) ):
                
                    # got at least 1 coder:
                    coder_count = len( my_coder1_id_list )
                    if ( coder_count == 1 ):
                    
                        # just one coder - place in coder1.
                        coder_id = my_coder1_id_list[ 0 ]
                        coder_instance = User.objects.get( id = coder_id )
                        reliability_row.coder1 = coder_instance
                        
                    elif ( coder_count > 1 ):
                    
                        # more than one, or none (ERROR).  convert list to
                        #    string, store in coder1_id_list.
                        reliability_row.coder1_id_list = ",".join( map( str, my_coder1_id_list ) )
                        
                    #-- END check to see what we do with Coder ID(s).
                    
                    # mention count
                    reliability_row.coder1_mention_count = my_coder1_mention_count
                    
                #-- END check to see if coder 1 is present. --#
                
                # coder 2
                if ( ( my_coder2_id_list is not None ) and ( len( my_coder2_id_list ) > 0 ) ):
                
                    # got at least 1 coder:
                    coder_count = len( my_coder2_id_list )
                    if ( coder_count == 1 ):
                    
                        # just one coder - place in coder1.
                        coder_id = my_coder2_id_list[ 0 ]
                        coder_instance = User.objects.get( id = coder_id )
                        reliability_row.coder2 = coder_instance
                        
                    else:
                    
                        # more than one, or none (ERROR).  convert list to
                        #    string, store in coder2_id_list.
                        reliability_row.coder2_id_list = ",".join( map( str, my_coder2_id_list ) )
                        
                    #-- END check to see what we do with Coder ID(s).
                    
                    # mention count
                    reliability_row.coder2_mention_count = my_coder2_mention_count
                    
                #-- END check to see if coder 2 is present. --#

                # coder 3
                if ( ( my_coder3_id_list is not None ) and ( len( my_coder3_id_list ) > 0 ) ):
                
                    # got at least 1 coder:
                    coder_count = len( my_coder3_id_list )
                    if ( coder_count == 1 ):
                    
                        # just one coder - place in coder1.
                        coder_id = my_coder3_id_list[ 0 ]
                        coder_instance = User.objects.get( id = coder_id )
                        reliability_row.coder3 = coder_instance
                        
                    else:
                    
                        # more than one, or none (ERROR).  convert list to
                        #    string, store in coder3_id_list.
                        reliability_row.coder3_id_list = ",".join( map( str, my_coder3_id_list ) )
                        
                    #-- END check to see what we do with Coder ID(s).
                    
                    # mention count
                    reliability_row.coder3_mention_count = my_coder3_mention_count
                    
                #-- END check to see if coder 3 is present. --#
                
                print( "In " + me + ": reliability_row before save() - " + str( reliability_row ) )
                
                # save the row.
                reliability_row.save()
            
            #-- END loop over sources --#

        #-- END loop over authors. --#
        
    #-- END method output_reliability_data --##
    
    
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
        
        article_qs = article_qs[ : 2 ]
            
        # build a dictionary that maps author ID to information on that author
        #    and the sources the author quoted in stories included in selected
        #    articles.
        author_to_source_info_dict = self.author_to_source_info_map
        
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
            article_data_qs = article_data_qs.order_by( "-coder__id" )
            
            # how many Article_Data?
            article_data_count = len( article_data_qs )
        
            # output summary row.
            print( "- In " + me + ": Article ID = " + str( current_article.id ) + "; Article_Data count = " + str( article_data_count ) )
            
            # for each article, update dictionary that maps author ID to author
            #    info. that includes:
            # - author Person ID.
            # - author name
            # - source_dict - dictionary that maps person IDs of sources to dictionary
            #    that contains details of source, including source ID, name, and list of
            #    coders who found the source.
            
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

    #-- END method process_articles() --#


    def process_relations( self, article_data_IN ):
        
        '''
        Accepts Article_Data instance whose relations we need to process.  For
           each author, updates author and relation information.
        '''
        
        # return reference
        status_OUT = ""
        
        # declare variables
        me = "process_relations"
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
        
            # Get coder info...
            article_data_coder = article_data_IN.coder
            
            # ... author QuerySet...
            article_author_qs = article_data_IN.article_author_set.all()
                        
            # ...and source QuerySet.
            article_source_qs = article_data_IN.article_source_set.all()
            
            # for each author...
            for current_author in article_author_qs:
            
                # get author person, author info.
                author_person = current_author.person
                author_info_dict = self.get_author_info( author_person )
                    
                # update author info for each related source.
                for current_source in article_source_qs:
                
                    # get source person
                    source_person = current_source.person
                    
                    # call method to update source info
                    self.update_source_info( source_person, author_info_dict, article_data_coder )
                
                #-- END loop over sources --#

            #-- END check to see if QuerySet passed in. --#  
        
        #-- END check to see if Coder present --#
        
        return status_OUT
        
    #-- END method process_relations() --#


    def update_source_info( self, source_person_IN, author_info_dict_IN, coder_user_IN ):
        
        # return reference
        status_OUT = ""
        
        # declare variables
        me = "update_source_info"
        source_info_dict = {}
        coder_user_id = -1
        coder_index = -1
        property_name = ""
        coder_id_list = None
        coder_match_count = -1
        
        # make sure we have a source person
        if ( source_person_IN is not None ):
        
            # make sure we have author info.
            if ( author_info_dict_IN is not None ):
            
                # coder?
                if ( coder_user_IN is not None ):
                
                    # got everything we need.  Get source info dict out of
                    #    author info.
                    source_info_dict = self.get_source_info( source_person_IN, author_info_dict_IN )
                    
                    # got something back?
                    if ( source_info_dict is not None ):
                    
                        # We do.  now to figure out which coder's data to
                        #    update.  Get coder's user ID.
                        coder_user_id = coder_user_IN.id
                        
                        # get index for that ID.
                        coder_index = self.coder_id_to_index_map.get( coder_user_id, -1 )
                        
                        # index greater than 0?
                        if ( coder_index > 0 ):
                        
                            # it is.  Update source info for the index.
                            
                            # coder ID - property name is lower case, not upper
                            #    case (like constant-ish name that holds it).
                            property_name = "coder_" + str( coder_index ) + "_id_list"
                            print( "prop name = " + property_name )
                            coder_id_list = source_info_dict.get( property_name, None )
                            
                            # coder's ID not in coder ID list?
                            if ( coder_user_id not in coder_id_list ):
                            
                                # not there - add it.
                                coder_id_list.append( coder_user_id )
                                
                            #-- END check to see if coder in coder ID list --#
                            
                            # match count
                            property_name = "coder_" + str( coder_index ) + "_count"
                            print( "prop name = " + property_name )
                            coder_match_count = source_info_dict.get( property_name, -1 )

                            # increment match count.
                            if ( coder_match_count >= 0 ):
                            
                                # add one
                                coder_match_count += 1
                                
                                # put back in info.
                                source_info_dict[ property_name ] = coder_match_count
                                
                            #-- END check to see if match count is valid --#
                            
                            # shouldn't need to do anything more here - because
                            #    of pass by reference, everything should be all
                            #    updated.
                        
                        #-- END check to see if index greater than 0 --# 
                    
                    #-- END check to see if we have source info --#
                
                #-- END check to make sure we have a coder. --#
            
            #-- END check to make sure we have author info. --#
        
        #-- END check for source person --#
        
        return status_OUT
    
    #-- END method update_source_info() --#


#-- END class Reliability_Ties --#


# declare variables
my_reliability_instance = None
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
my_reliability_instance = Reliability_Ties()

# place dictionaries in instance.
my_reliability_instance.coder_id_to_instance_map = coder_id_to_instance_dict
my_reliability_instance.coder_id_to_index_map = coder_id_to_index_dict

# process articles
tag_list = [ "prelim_network", ]
my_reliability_instance.process_articles( tag_list )

# output to database.
label = "prelim_network"
my_reliability_instance.output_reliability_data( label )
