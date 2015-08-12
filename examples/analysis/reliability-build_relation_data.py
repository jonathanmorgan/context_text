from __future__ import unicode_literals

# python package imports
import six

# django imports
from django.contrib.auth.models import User

# sourcenet imports
from sourcenet.models import Analysis_Reliability_Ties
from sourcenet.models import Article
from sourcenet.models import Article_Data
from sourcenet.models import Person

#-------------------------------------------------------------------------------
# class definitions
#-------------------------------------------------------------------------------


class Reliability_Ties( object ):
    
    
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

    
    #----------------------------------------------------------------------------
    # instance methods
    #----------------------------------------------------------------------------


    def __init__( self, *args, **kwargs ):
        
        # declare instance variables
        self.coder_id_to_instance_map = {}
        self.coder_id_to_index_map = {}
        
        # variables to filter reliability row lookup.
        self.reliability_row_label = ""
        
        # variable to hold desired automated coder type
        self.limit_to_automated_coder_type = ""
        
    #-- END method __init__() --#
    

    def filter_article_data( self, article_data_qs_IN ):
        
        '''
        Accepts Article_Data QuerySet.  Filters it based on any nested variables
           that relate to filtering (at this point, just
           self.limit_to_automated_coder_type).  Returns filtered QuerySet.
        '''
        
        # return reference
        qs_OUT = None
        
        # declare variables
        automated_coder_type = None
        coder_type_list = []
        
        # start by just returning what is passed in.
        qs_OUT = article_data_qs_IN
        
        # see if we have a coder type.
        automated_coder_type = self.limit_to_automated_coder_type
        if ( ( automated_coder_type is not None ) and ( automated_coder_type != "" ) ):
        
            # got one.  Filter the QuerySet.
            coder_type_list = [ automated_coder_type, ]
            qs_OUT = Article_Data.filter_automated_by_coder_type( qs_OUT, coder_type_list )
        
        #-- END check to see if automated coder type. --#
        
        return qs_OUT
    
    #-- END method filter_article_data() --#


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
    
        
    def get_reliability_row( self, author_person_IN, source_person_IN ):
        
        '''
        Accepts author and source persons.  Retrieves label nested inside this
           instance.  Uses these to try to retrieve an existing reliability row.
           If match found, returns it.  If none found, creates one, initializes
           it and saves it, then returns reference to it.
        '''
        
        # return reference
        instance_OUT = None
        
        # declare variables
        me = "get_reliability_row"
        author_id = -1
        author_name = ""
        source_id = -1
        source_name = ""
        reliability_label = ""
        reliability_qs = None
        result_count = -1
        
        # make sure we have an author...
        if ( author_person_IN is not None ):
        
            # ...and a source.
            if ( source_person_IN is not None ):

                # get info for author person
                author_id = author_person_IN.id
                author_name = author_person_IN.get_name_string()
                
                # get info for source person.
                source_id = source_person_IN.id
                source_name = source_person_IN.get_name_string()
                
                # get label
                reliability_label = self.reliability_row_label
                
                # set up filters.
                reliability_qs = Analysis_Reliability_Ties.objects.all()
                reliability_qs = reliability_qs.filter( person = author_person_IN )
                reliability_qs = reliability_qs.filter( person_type = Analysis_Reliability_Ties.PERSON_TYPE_AUTHOR )
                reliability_qs = reliability_qs.filter( relation_person = source_person_IN )
                realibility_qs = reliability_qs.filter( relation_person_type = Analysis_Reliability_Ties.PERSON_TYPE_SOURCE )
                reliability_qs = reliability_qs.filter( relation_type = Analysis_Reliability_Ties.RELATION_AUTHOR_TO_SOURCE )
                
                # got a label?
                if ( ( reliability_label is not None ) and ( reliability_label != "" ) ):
                
                    # yes - filter on it.
                    reliability_qs = reliability_qs.filter( label = reliability_label )
                
                #-- END check for label --#

                # got any matches?
                result_count = reliability_qs.count()
                if ( result_count == 1 ):
                
                    # got one.  Return it.
                    instance_OUT = reliability_qs.get()
                    
                elif ( result_count > 1 ):
                
                    # multiple matches.  Yikes.
                    print( "ERROR In " + me + ": Multiple matches returned for author " + str( author_person_IN ) + "; source " + str( source_person_IN ) + "; label = " + reliability_label )
                    
                else:
                
                    # well, looks like no existing row - create and populate.
                    reliability_row = Analysis_Reliability_Ties()
                    
                    # label
                    if ( ( reliability_label is not None ) and ( reliability_label != "" ) ):

                        reliability_row.label = reliability_label
                        
                    #-- END check to see if label. --#
                    
                    # Author information
                    reliability_row.person = author_person_IN
                    reliability_row.person_name = author_name
                    reliability_row.person_type = Analysis_Reliability_Ties.PERSON_TYPE_AUTHOR
                    reliability_row.relation_type = Analysis_Reliability_Ties.RELATION_AUTHOR_TO_SOURCE
                    
                    # source information
                    reliability_row.relation_person = source_person_IN
                    reliability_row.relation_person_name = source_name
                    reliability_row.relation_person_type = Analysis_Reliability_Ties.PERSON_TYPE_SOURCE
                    
                    # Coding information
                    reliability_row.coder1 = None
                    reliability_row.coder1_mention_count = 0
                    reliability_row.coder1_id_list = ""
                    reliability_row.coder2 = None
                    reliability_row.coder2_mention_count = 0
                    reliability_row.coder2_id_list = ""
                    reliability_row.coder3 = None
                    reliability_row.coder3_mention_count = 0
                    reliability_row.coder3_id_list = ""
                                        
                    print( "In " + me + ": reliability_row before save() - " + str( reliability_row ) )
                    
                    # save the row.
                    reliability_row.save()
                    
                    # return reference.
                    instance_OUT = reliability_row
                    
                 #-- END check to see how many matches we have in reliability table --#   
                    
            else:
            
                print( "ERROR In " + me + ": No source person passed in, can't retrieve row." )
    
            #-- END check to see if source --#

        else:
        
            print( "ERROR In " + me + ": No author person passed in, can't retrieve row." )

        #-- END check to see if author --#
        
        return instance_OUT
        
    #-- END method get_reliability_row() --#


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
            
            # !filter on automated coder_type
            article_data_qs = self.filter_article_data( article_data_qs )
            
            # !hack
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
            article_source_qs = article_data_IN.get_quoted_article_sources_qs()
            
            # for each author...
            for current_author in article_author_qs:
            
                # get author person.
                author_person = current_author.person
                    
                # update author info for each related source.
                for current_source in article_source_qs:
                
                    # get source person
                    source_person = current_source.person
                    
                    # call method to update reliability row.
                    self.update_reliability_row( author_person, source_person, article_data_coder )
                
                #-- END loop over sources --#

            #-- END check to see if QuerySet passed in. --#  
        
        #-- END check to see if Coder present --#
        
        return status_OUT
        
    #-- END method process_relations() --#


    def update_reliability_row( self, author_person_IN, source_person_IN, coder_user_IN ):
        
        # return reference
        status_OUT = ""
        
        # declare variables
        me = "update_reliability_row"
        reliability_row = None
        coder_user_id = -1
        coder_index = -1
        attr_name = ""
        coder = None
        coder_id = -1
        coder_mention_count = -1
        coder_id_list_string = ""
        coder_id_list = []        
        
        # make sure we have an author person...
        if ( author_person_IN is not None ):
        
            # ...and a source person...
            if ( source_person_IN is not None ):
            
                # ...and a coder.
                if ( coder_user_IN is not None ):
                
                    # got everything we need.  Get reliability row for person
                    #    and source.
                    reliability_row = self.get_reliability_row( author_person_IN, source_person_IN )
                    
                    # got something back?
                    if ( reliability_row is not None ):
                    
                        # We do.  now to figure out which coder's data to
                        #    update.  Get coder's user ID.
                        coder_user_id = coder_user_IN.id
                        
                        # get index for that ID.
                        coder_index = self.coder_id_to_index_map.get( coder_user_id, -1 )
                        
                        # index greater than 0?
                        if ( coder_index > 0 ):
                        
                            # it is.  Update reliability row for the index.
                            
                            # coder#
                            attr_name = "coder" + str( coder_index )
                            coder = getattr( reliability_row, attr_name )
                            
                            # got a coder?
                            if ( coder is not None ):
                            
                                # one in row already.  Is it the same as the one
                                #    passed in?
                                coder_id = coder.id
                                if ( coder_id != coder_user_id ):
                                
                                    # not the same.  ID alread in list?
                                    attr_name = "coder" + str( coder_index ) + "_id_list"
                                    coder_id_list_string = getattr( reliability_row, attr_name )
                                    
                                    # anything there?
                                    if ( ( coder_id_list_string is None ) or ( coder_id_list_string == "" ) ):
                                    
                                        # no list.  Make one with the two IDs.
                                        coder_id_list = []
                                        coder_id_list.append( str( coder_id ) )
                                        coder_id_list.append( str( coder_user_id ) )
                                        
                                        # convert to string
                                        coder_id_list_string = ",".join( coder_id_list )
                                        
                                        # add to record.
                                        setattr( reliability_row, attr_name, coder_id_list_string )
                                        
                                    else:
                                    
                                        # already something there.  Parse it.
                                        coder_id_list = coder_id_list_string.split( "," )
                                        
                                        # see if coder_id is already in list.
                                        if ( coder_id not in coder_id_list ):
                                        
                                            # not there.  Add it to list...
                                            coder_id_list.append( str( coder_id ) )
                                            
                                            # ...convert list to string...
                                            coder_id_list_string = ",".join( coder_id_list )
                                            
                                            # ...then update reliabilty row.
                                            setattr( reliability_row, attr_name, coder_id_list_string )
                                            
                                        else:
                                        
                                            # already in list.  Nothing to do.
                                            pass
                                        
                                        #-- END check to see if ID already in list. --#
                                            
                                    #-- END check to see if coder_id_list has anything in it --#
                                    
                                else:
                                
                                    # same as already here.  Nothing to do.
                                    pass
                                
                                #-- END check to see if the same --#
                            
                            else:
                            
                                # no coder in row - store this one there.
                                setattr( reliability_row, attr_name, coder_user_IN )
                                
                            #-- END check to see if there is a coder in the instance for this index. --#
                            
                            # coder#_mention_count
                            attr_name = "coder" + str( coder_index ) + "_mention_count"
                            coder_mention_count = getattr( reliability_row, attr_name )
                            
                            # increment the count.
                            coder_mention_count += 1
                            
                            # put updated count in reliability_row.
                            setattr( reliability_row, attr_name, coder_mention_count )
                                                        
                            # save updated record.
                            reliability_row.save()
                        
                        else:
                        
                            # error - index not greater than 0.
                            print( "ERROR In " + me + ": coder index = " + str( coder_index ) + " for coder " + str( coder_user_IN ) + ".  Should be 1 or greater." )
                        
                        #-- END check to see if index greater than 0 --# 
                    
                    #-- END check to see if we have source info --#
                
                #-- END check to make sure we have a coder. --#
            
            #-- END check to make sure we have author info. --#
        
        #-- END check for source person --#
        
        return status_OUT
    
    #-- END method update_reliability_row() --#


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

# configure so that it limits to automated coder_type of OpenCalais_REST_API_v2.
my_reliability_instance.limit_to_automated_coder_type = "OpenCalais_REST_API_v2"

# label for reliability rows created and used in this session.
label = "prelim_network_fixed_authors"
my_reliability_instance.reliability_row_label = label

# process articles
tag_list = [ "prelim_network", ]
my_reliability_instance.process_articles( tag_list )