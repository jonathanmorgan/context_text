from __future__ import unicode_literals

# python package imports
import six

# django imports
from django.contrib.auth.models import User

# sourcenet imports
from sourcenet.models import Analysis_Reliability_Names
from sourcenet.models import Article
from sourcenet.models import Article_Data
from sourcenet.models import Article_Subject
from sourcenet.models import Person

#-------------------------------------------------------------------------------
# class definitions
#-------------------------------------------------------------------------------


class Reliability_Names( object ):
    
    
    #----------------------------------------------------------------------
    # constants-ish
    #----------------------------------------------------------------------    


    # article info dictionary field names
    ARTICLE_ID = "article_id"
    ARTICLE_DATA_ID_LIST = "article_data_id_list"
    ARTICLE_CODER_ID_LIST = "article_coder_id_list"
    AUTHOR_INFO_DICT = "author_info_dict"
    SUBJECT_INFO_DICT = "subject_info_dict"
    
    # source and author info dicts will use same field names.
    PERSON_ID = "person_id"
    PERSON_NAME = "person_name"
    PERSON_CODER_ID_TO_CODING_INFO_DICT = "person_coder_id_to_coding_info_dict"
    # PERSON_CODER_ID_LIST = "person_coder_id_list"
    
    # coder-specific person coding info map
    PERSON_CODING_INFO_CODER_ID = "coder_id"
    PERSON_CODING_INFO_PERSON_TYPE = "person_type"
    PERSON_CODING_INFO_PERSON_TYPE_INT = "person_type_int"
    PERSON_CODING_INFO_ARTICLE_PERSON_ID = "article_person_id"
    PERSON_CODING_INFO_NAME_LIST = [ PERSON_CODING_INFO_CODER_ID, PERSON_CODING_INFO_PERSON_TYPE, PERSON_CODING_INFO_PERSON_TYPE_INT, PERSON_CODING_INFO_ARTICLE_PERSON_ID ]
    
    # person types
    PERSON_TYPE_AUTHOR = "author"
    PERSON_TYPE_SUBJECT = "subject"
    PERSON_TYPE_SOURCE = "source"

    # Article_Subject subject_types
    SUBJECT_TYPE_MENTIONED = Article_Subject.SUBJECT_TYPE_MENTIONED
    SUBJECT_TYPE_QUOTED = Article_Subject.SUBJECT_TYPE_QUOTED

    # person or subject types to int ID map.
    PERSON_TYPE_TO_INT_MAP = {}
    PERSON_TYPE_TO_INT_MAP[ PERSON_TYPE_AUTHOR ] = 1
    PERSON_TYPE_TO_INT_MAP[ PERSON_TYPE_SUBJECT ] = 2
    PERSON_TYPE_TO_INT_MAP[ PERSON_TYPE_SOURCE ] = 3
    PERSON_TYPE_TO_INT_MAP[ SUBJECT_TYPE_MENTIONED ] = 2
    PERSON_TYPE_TO_INT_MAP[ SUBJECT_TYPE_QUOTED ] = 3
        
    # information about table.
    TABLE_MAX_CODERS = 10

    
    #----------------------------------------------------------------------------
    # instance methods
    #----------------------------------------------------------------------------


    def __init__( self, *args, **kwargs ):
        
        # declare instance variables
        self.article_id_to_info_map = {}
        self.coder_id_to_instance_map = {}        
        self.coder_id_to_index_map = {}
        
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
        
        #print( "++++ found ID: " + str( matching_user_id ) )
        
        # if we have an ID, use it to get User instance.
        if ( matching_user_id > 0 ):
        
            # we do.  Get instance from coder_id_to_instance_dict.
            instance_OUT = coder_id_to_instance_dict.get( matching_user_id, None )
            print( "++++ found User: " + str( instance_OUT ) )
        
        #-- END check to see if we have a User ID. --#
        
        return instance_OUT        
        
    #-- END method get_coder_for_index() --#
    
        
    def output_reliability_data( self, label_IN = "" ):
    
        '''
        Accepts article_info_dict_IN, dictionary that maps article IDs to the
           following:
           - article_id - ID of article.
           - article_data_id_list - list of IDs of Article_Data instances for the
              article.
           - article_coder_id_list - list of IDs of Coders who coded the article.
           - author_dict - dictionary that maps person IDs of authors to dictionary
              that contains details of author, including author ID, name, and 
              map of coder IDs who detected the author to their coding info for
              the author.
           - source_dict - dictionary that maps person IDs of sources to dictionary
              that contains details of source, including source ID, name, and
              map of coder IDs who detected the subject to their coding info for
              the subject.
              
        Loops over the items in the dictionary, processing each.  For each article,
           gets dictionaries of authors and sources and for each author and source,
           outputs a row to the reliability table containing coding information.
           
        Preconditions: expects that you already ran process_articles() with this
           instance.
        '''
    
        # declare variables.
        article_info_dict_IN = None
        article_info_count = -1
        article_info_counter = -1
        current_article_info_dict = {}
        my_article_id = -1
        my_article_info = {}
        my_article_data_id_list = []
        my_article_coder_id_list = []
        my_author_info_dict = {}
        my_subject_info_dict = {}
        my_article = None
        coder_id_to_index_dict = {}
        current_coder_index = -1
        coder_id_to_index_dict = {}
        my_person_id = -1
        my_person_info_dict = {}
        reliability_row = -1
        
        # get map of article IDs to attribution info.
        article_info_dict_IN = self.article_id_to_info_map
        
        # get map of coder IDs to their index number (1 up).
        coder_id_to_index_dict = self.coder_id_to_index_map
    
        # make sure we have something to output.
        if article_info_dict_IN is not None:
        
            # not None.  Initialize count variables.
            article_info_count = len( article_info_dict_IN )
            article_info_counter = 0
            
            # loop over info passed in.
            for my_article_id, my_article_info in six.iteritems( article_info_dict_IN ):
            
                # retrieve elements contained in article_info:
                my_article_data_id_list = my_article_info.get( self.ARTICLE_DATA_ID_LIST, [] )
                my_article_coder_id_list = my_article_info.get( self.ARTICLE_CODER_ID_LIST, [] )
                my_author_info_dict = my_article_info.get( self.AUTHOR_INFO_DICT, {} )
                my_subject_info_dict = my_article_info.get( self.SUBJECT_INFO_DICT, {} )
                
                # set up information needed for reliability row output.
                
                # get article for article ID.
                my_article = Article.objects.get( id = my_article_id )
                
                # for reliability table output, just run through author and source
                #    info.
    
                # got author info?
                if ( ( my_author_info_dict is not None ) and ( len ( my_author_info_dict ) > 0 ) ):
                
                    # loop over the info in the dictionary, calling function to
                    #    output a given person's row to the reliability table for
                    #    each.
                    for my_person_id, my_person_info_dict in six.iteritems( my_author_info_dict ):
                    
                        # call function to output reliability table row.
                        reliability_row = self.output_reliability_name_row( my_article, my_person_info_dict, self.PERSON_TYPE_AUTHOR, label_IN = label_IN )
                        print ( "- author: " + str( reliability_row ) )
                    
                    #-- END loop over author info ---#
                
                #-- END check to see if we have author info. --#
                
                # got source info?
                if ( ( my_subject_info_dict is not None ) and ( len ( my_subject_info_dict ) > 0 ) ):
                
                    # loop over the info in the dictionary, calling function to
                    #    output a given person's row to the reliability table for
                    #    each.
                    for my_person_id, my_person_info_dict in six.iteritems( my_subject_info_dict ):
                    
                        # call function to output reliability table row.
                        reliability_row = self.output_reliability_name_row( my_article, my_person_info_dict, self.PERSON_TYPE_SUBJECT, label_IN = label_IN )
                        print ( "- source: " + str( reliability_row ) )
                    
                    #-- END loop over author info ---#
    
                #-- END check to see if we have author info. --#            
            
            #-- END loop over article_info_dict_IN --#
            
        #-- END check to see if we got something passed in. --#
        
    #-- END method output_reliability_data --##
    
    
    def output_reliability_name_row( self, article_IN, person_info_dict_IN, article_person_type_IN, label_IN = "" ):
        
        '''
        Accepts:
        - article_IN - article this person was detected within.
        - person_info_dict_IN, dictionary that maps person IDs to the
            following:
            - person_id - ID of person found in article.
            - person_name - String name of that person.
            - person_coder_id_to_coding_info_dict - dictionary that maps IDs of
                coders who detected and recorded the presence of that person to
                details of their coding.  For now, just has coder ID, person
                type, and Article_Person record ID.  Could have more information
                in the future.
        - article_person_type_IN, the type of the Article_Person children we are
            processing ("author" or "subject").
        - label_IN - label to assign to this set of data in the database.
         
        Creates an instance of Analysis_Reliability_Names, stores values from
            the dictionary in the appropriate columns, then saves it.
           
        Returns the row model instance, or None if error.
        '''
        
        # return reference
        instance_OUT = None
        
        # declare variables
        me = "output_reliability_name_row"
        coder_id_to_index_map_IN = None
        reliability_instance = None
        my_person_id = -1
        my_person = None
        my_person_name = ""
        my_coder_person_info_dict = None
        coder_count = -1
        current_coder_id = -1
        current_person_coding_info = None
        current_coder_index = -1
        current_coder_user = None
        current_coding_info_name = None
        current_coding_info_value = None
        index_used_list = []
        current_number = -1
        current_index = -1
        
        # declare variables - getting appropriate Article_Data for automated
        article_data_qs = None
        coder_article_data_qs = None
        coder_article_data = None
        coder_article_data_id = -1
        
        # make sure we have everything we need.
        coder_id_to_index_map_IN = self.coder_id_to_index_map

        # article
        if ( article_IN is not None ):
    
            # retrieve the Article_Data QuerySet.    
            article_data_qs = article_IN.article_data_set.all()
        
            # person_info
            if ( person_info_dict_IN is not None ):
            
                # map of coder IDs to indexes
                if ( coder_id_to_index_map_IN is not None ):
                
                    # person type.
                    if ( ( article_person_type_IN is not None ) and ( article_person_type_IN != "" ) ):
                    
                        # got everything.  make reliability row.
                        reliability_instance = Analysis_Reliability_Names()
                        
                        # got a label?
                        if ( ( label_IN is not None ) and ( label_IN != "" ) ):
                        
                            # yes, there is a label.  Add it to row.
                            reliability_instance.label = label_IN
                        
                        #-- END check to see if label --#
                        
                        # get information from info dictionary
                        my_person_id = person_info_dict_IN.get( self.PERSON_ID, -1 )
                        my_person = Person.objects.get( id = my_person_id )
                        my_person_name = person_info_dict_IN.get( self.PERSON_NAME, None )
                        my_coder_person_info_dict = person_info_dict_IN.get( self.PERSON_CODER_ID_TO_CODING_INFO_DICT, {} )
                        
                        # place info inside
                        reliability_instance.article = article_IN
                        reliability_instance.person = my_person
                        reliability_instance.person_name = my_person_name
                        reliability_instance.person_type = article_person_type_IN
                        
                        # check to see if more than TABLE_MAX_CODERS.
                        coder_count = len( my_coder_person_info_dict )
                        if ( coder_count > self.TABLE_MAX_CODERS ):
                        
                            # bad news - print error.
                            print ( "====> In " + me + ": ERROR - more coders ( " + str( coder_count ) + " ) than table allows ( " + str( self.TABLE_MAX_CODERS ) + " ).\"" )
                            
                        #-- END check to see if more coders than slots in table --#
                        
                        # loop over coders.
                        for current_coder_id, current_person_coding_info in six.iteritems( my_coder_person_info_dict ):
                        
                            # look up index.
                            current_coder_index = coder_id_to_index_map_IN.get( current_coder_id, -1 )
                            
                            # get User instance
                            current_coder_user = User.objects.get( id = current_coder_id )
                            
                            # retrieve coder's Article_Data.
                            coder_article_data = None
                            coder_article_data_id = -1
                            coder_article_data_qs = article_data_qs.filter( coder = current_coder_user )
                            
                            # !if automated, filter on coder_type
                            coder_article_data_qs = self.filter_article_data( coder_article_data_qs )
                            
                            # how many?
                            if ( coder_article_data_qs.count() == 1 ):
                            
                                # got one! store information.
                                coder_article_data = coder_article_data_qs.get()
                                coder_article_data_id = coder_article_data.id
                            
                            #-- END check to see if single matching Article_Data --#    
                                
                            # use index to decide in which columns to place
                            #    coder-specific information.
                            if ( current_coder_index != -1 ):
                            
                                # add index to used list if not already there
                                if current_coder_index not in index_used_list:

                                    index_used_list.append( current_coder_index )
                                    
                                else:
                                
                                    # already there?  Error.
                                    print ( "====> In " + me + ": ERROR - index already used - multiple records for coder ID \"" + str( current_coder_id ) + "\"" )
                                    
                                #-- END check to see if index is in our "used" list --#
                            
                                # place info in "coder<index>" fields.
                                
                                # coder# - reference to User who coded.
                                field_name = "coder" + str( current_coder_index )
                                setattr( reliability_instance, field_name, current_coder_user )
                                
                                # coder#_detected - 1, since coder detected this person.
                                field_name = "coder" + str( current_coder_index ) + "_detected"
                                setattr( reliability_instance, field_name, 1 )
    
                                # coder#_person_id - id of person (will be
                                #    subsequently used to smoosh rows together for
                                #    same name, different person IDs).
                                field_name = "coder" + str( current_coder_index ) + "_person_id"
                                setattr( reliability_instance, field_name, my_person_id )
                                
                                # set fields from current_person_coding_info.
                                #     Each name in dictionary corresponds to
                                #     column in database table.
                                for current_coding_info_name, current_coding_info_value in six.iteritems( current_person_coding_info ):
                                
                                    # set field name using name.
                                    field_name = "coder" + str( current_coder_index ) + "_" + current_coding_info_name
                                    
                                    # use that field name to set value.
                                    setattr( reliability_instance, field_name, current_coding_info_value )
                                    
                                #-- END loop over coding info. --#

                                # coder#_article_data_id - id of coder's
                                #    Article_Data row.
                                # Got an ID?
                                if ( coder_article_data_id > 0 ):
                                
                                    # yes.  store it.
                                    field_name = "coder" + str( current_coder_index ) + "_article_data_id"
                                    setattr( reliability_instance, field_name, coder_article_data_id )
                                
                                #-- END check to see if Article_Data ID --#
                            
                            else:
                            
                                print ( "====> In " + me + ": ERROR - no index found for coder ID \"" + str( current_coder_id ) + "\"" )
    
                            #-- END check to make sure coder index isn't -1 --#
                        
                        #-- END loop over coder IDs. --#
                        
                        print( "----> In " + me + ": len( index_used_list ) = " + str( len( index_used_list ) ) )
                        
                        # check to make sure that all indexes were used.
                        if ( len( index_used_list ) < self.TABLE_MAX_CODERS ):
                        
                            # not all used.  put zeroes in fields for indices
                            #    not in the list.
                            for current_number in range( self.TABLE_MAX_CODERS ):
                            
                                # increment value by 1.
                                current_index = current_number + 1
                                
                                # is it in the list?
                                if ( current_index not in index_used_list ):
                                
                                    # no - add values.
                                    
                                    # If you are going to be calculating
                                    #     reliability on a numeric column, you
                                    #     need to set it to 0 here for coders
                                    #     who did not detect the current person,
                                    #     else you'll have NaN problems in R.
                                    # If you don't set it here, column will get
                                    #     default value, usually NULL in SQL.

                                    # coder# - reference to User who coded.
                                    current_coder_user = self.get_coder_for_index( current_index )
                                    field_name = "coder" + str( current_index )
                                    setattr( reliability_instance, field_name, current_coder_user )
                                    
                                    # coder#_detected - 0, since coder did not
                                    #    detect this person.
                                    field_name = "coder" + str( current_index ) + "_detected"
                                    setattr( reliability_instance, field_name, 0 )
        
                                    # coder#_person_id - id of person (0, since
                                    #    coder didn't detect this person).
                                    field_name = "coder" + str( current_index ) + "_person_id"
                                    setattr( reliability_instance, field_name, 0 )
                                                                    
                                    # coder#_person_type_int - person type of 
                                    #    person (0, since coder didn't detect
                                    #    this person).
                                    field_name = "coder" + str( current_index ) + "_person_type_int"
                                    setattr( reliability_instance, field_name, 0 )
                                                                    
                                
                            #-- END loop over numbers 1 through TABLE_MAX_CODERS --#
                            
                        #-- END check to see if all indices used. --#
                        
                        # save
                        reliability_instance.save()
                        
                        # return
                        instance_OUT = reliability_instance
        
                    #-- END check to see if we have person type. --#
    
                #-- END check to see if we have map of coder IDs to indexes. --#
    
            #-- END check to see if we have person info. --#
    
        #-- END check to see if we have an article. --#
        
        return instance_OUT
        
    #-- END method output_reliability_name_row() --#


    def process_articles( self, tag_list_IN = [], limit_to_sources_IN = False ):

        '''
        Grabs articles with a tag in tag_list_IN.  For each, loops through their
           Article_Data to build a dictionary that maps article ID to article
           info. that includes:
           - article_id - ID of article.
           - article_data_id_list - list of IDs of Article_Data instances for the
              article.
           - article_coder_id_list - list of IDs of Coders who coded the article.
           - author_dict - dictionary that maps person IDs of authors to dictionary
              that contains details of author, including author ID, name, and list of
              coders who found the author.
           - source_dict - dictionary that maps person IDs of sources to dictionary
              that contains details of source, including source ID, name, and list of
              coders who found the source.
        '''

        # declare variables - retrieving reliability sample.
        article_qs = None
        current_article = None
        article_data_qs = None
        current_query = None
        article_data_count = -1
        
        # declare variables - compiling information for articles.
        article_id = -1
        article_to_info_dict = None
        article_info_dict = None
        coder_id_to_instance_dict = None
        coder_id_to_index_dict = None
        coder_counter = -1
        current_article_data = None
        article_data_id_list = None
        article_data_author_qs = None
        article_data_subject_qs = None
        article_coder_id_list = None
        article_data_id = -1
        article_data_coder = None
        article_data_coder_id = None
        person_type = ""
        author_info_dict = None
        subject_info_dict = None

        #-------------------------------------------------------------------------------
        # process articles to build data
        #-------------------------------------------------------------------------------
        
        # got a tag list?
        if ( ( tag_list_IN is not None ) and ( len( tag_list_IN ) > 0 ) ):

            # get articles with tags in list passed in.
            article_qs = Article.objects.filter( tags__name__in = tag_list_IN )
            
        #-- END check to see if tag list --#
            
        article_qs = article_qs.order_by( "id" )
        
        # build a dictionary that maps article ID to assorted details about the coding
        #    of each article.
        article_to_info_dict = self.article_id_to_info_map
        
        # For reference, also build up a dictionary of coder IDs that reference
        #    coder instances, so we know how many coders, and coder IDs to
        #    index, from 1 up, so we can keep them straight when outputting
        #    data.
        coder_id_to_instance_dict = self.coder_id_to_instance_map
        coder_id_to_index_dict = self.coder_id_to_index_map
        coder_counter = 0
        
        # loop over the articles.
        for current_article in article_qs:
        
            # initialize variables
            article_info_dict = {}
            article_data_id_list = []
            article_coder_id_list = []
            author_info_dict = {}
            subject_info_dict = {}
        
            # get article_id
            article_id = current_article.id
        
            # get article data for this article
            article_data_qs = current_article.article_data_set.all()
            
            # !filter on automated coder_type
            article_data_qs = self.filter_article_data( article_data_qs )
            
            # how many Article_Data?
            article_data_count = len( article_data_qs )
        
            # output summary row.
            print( "- Article ID: " + str( current_article.id ) + "; Article_Data count: " + str( article_data_count ) )
            
            # for each article, build a dictionary that maps article ID to article info.
            #    that includes:
            # - article_id - ID of article.
            # - article_data_id_list - list of IDs of Article_Data instances for the
            #    article.
            # - article_coder_id_list - list of IDs of Coders who coded the article.
            # - author_dict - dictionary that maps person IDs of authors to dictionary
            #    that contains details of author, including author ID, name, and list of
            #    coders who found the author.
            # - source_dict - dictionary that maps person IDs of sources to dictionary
            #    that contains details of source, including source ID, name, and list of
            #    coders who found the source.
            
            # check to see if article already has an info dictionary (it better not...).
            if article_id in article_to_info_dict:
            
                # retrieve info dictionary
                article_info_dict = article_to_info_dict.get( article_id, {} )
                
            else:
            
                # make new info dictionary and add reference to it to master dictionary.
                article_info_dict = {}
                article_to_info_dict[ article_id ] = article_info_dict
                
            #-- END check to see if article already has an information dictionary. --#
            
            # compile information.
            
            # loop over related Article_Data instances.
            for current_article_data in article_data_qs:
            
                # get coder and coder's User ID.
                article_data_coder = current_article_data.coder
                article_data_coder_id = article_data_coder.id
                
                # If not already there, add to list of IDs of coders for this article.
                if article_data_coder_id not in article_coder_id_list:
        
                    # not there yet, add it.
                    article_coder_id_list.append( article_data_coder_id )
                    
                #-- END check to see if ID is in coder ID list --#
            
                # If not already there, add to master coder dictionary, also.
                if article_data_coder_id not in coder_id_to_instance_dict:
        
                    # not there yet.  Increment coder counter.
                    coder_counter += 1
                    
                    # add coder to instance cache.
                    coder_id_to_instance_dict[ article_data_coder_id ] = article_data_coder
                    
                    # and add to index map.
                    coder_id_to_index_dict[ article_data_coder_id ] = coder_counter
                    
                #-- END check to see if ID is in master coder dictionary --#
                            
                # add Article_Data ID to list.
                article_data_id = current_article_data.id
                article_data_id_list.append( article_data_id )
                
                # get lists of authors and subjects.
                article_data_author_qs = current_article_data.article_author_set.all()

                # all subjects, or just sources?
                if ( limit_to_sources_IN == True ):

                    # just sources.
                    article_data_subject_qs = current_article_data.get_quoted_article_sources_qs()
                    
                else:
                
                    # all subjects (the default).
                    article_data_subject_qs = current_article_data.article_subject_set.all()
                    
                #-- END check to see if all subjects or just sources. --#
                
                # call process_person_qs for authors.
                person_type = self.PERSON_TYPE_AUTHOR
                author_info_dict = self.process_person_qs( article_data_coder, article_data_author_qs, author_info_dict, person_type )
                        
                # and call process_person_qs for subjects.
                person_type = self.PERSON_TYPE_SUBJECT
                subject_info_dict = self.process_person_qs( article_data_coder, article_data_subject_qs, subject_info_dict, person_type )
                        
            #-- END loop over related Article_Data
            
            # update article info dictionary
            article_info_dict[ self.ARTICLE_ID ] = article_id
            article_info_dict[ self.ARTICLE_DATA_ID_LIST ] = article_data_id_list
            article_info_dict[ self.ARTICLE_CODER_ID_LIST ] = article_coder_id_list
            article_info_dict[ self.AUTHOR_INFO_DICT ] = author_info_dict
            article_info_dict[ self.SUBJECT_INFO_DICT ] = subject_info_dict    
        
            # shouldn't need to do anything more - reference to this dictionary is
            #    already in the master map of article IDs to article info.
        
        #-- END loop over articles. --#

    #-- END method process_articles() --#


    def process_person_qs( self, coder_IN, article_person_qs_IN, person_info_dict_IN, article_person_type_IN ):
        
        '''
        Accepts User instance of user who coded the Article, Article_Person
            QuerySet (either Article_Author or Article_Subject) and a dictionary
            to be used to build up a map of IDs to information on people found
            in a given article. Loops over entries and builds up this dictionary
            that maps IDs of persons identified in the text to details on the
            person (including the Person's ID, string name, and a map of coder
            IDs to a dictionary for each coder who detected that person with
            their coding info, at this point their ID and the type they assigned
            to the person).  Returns the updated person_info_dict dictionary.
        '''
        
        # return reference
        person_info_dict_OUT = {}
        
        # declare variables
        me = "process_person_qs"
        current_article_person = None
        coder_id = -1
        person_instance = None
        person_id = -1
        person_name = ""
        person_info = None
        person_coding_info_dict = None
        person_coding_info = None
        current_person_type = None
        current_person_type_int = None
        
        # make sure we have a coder
        if ( coder_IN is not None ):
        
            # make sure we have a queryset.
            if ( article_person_qs_IN is not None ):
            
                # make sure we have a person type passed in.
                if ( ( article_person_type_IN is not None ) and ( article_person_type_IN != "" ) ):
            
                    # got a dictionary passed in?
                    if ( person_info_dict_IN is not None ):
                    
                        person_info_dict_OUT = person_info_dict_IN
                    
                    #-- END check to see if we have a dictionary passed in. --#
            
                    # compile information on authors.
                    for current_article_person in article_person_qs_IN:
                    
                        # get coder ID.
                        coder_id = coder_IN.id
                        
                        # get current person type, different way based on person
                        #     type passed in.
                        # Article_Author QuerySet?
                        if ( article_person_type_IN == self.PERSON_TYPE_AUTHOR ):
                        
                            # only one type of author, so use the type passed in.
                            current_person_type = article_person_type_IN
                        
                        # Article_Subject QuerySet?
                        elif ( ( article_person_type_IN == self.PERSON_TYPE_SUBJECT )
                            or ( article_person_type_IN == self.PERSON_TYPE_SOURCE ) ):
                        
                            # this is an Article_Subject, so get subject_type.
                            current_person_type = current_article_person.subject_type
                            
                        
                        else:
                        
                            # unknown Article_Person type.  set to empty string.
                            current_person_type = ""
                        
                        #-- END check to see how we get person type. --#
                        
                        # also get integer value
                        current_person_type_int = self.PERSON_TYPE_TO_INT_MAP[ current_person_type ]
                        
                        # get person instance.
                        person_instance = current_article_person.person
                    
                        # got one?  Anonymous sources won't have one.  If we find a
                        #    record with no associated person, move on.
                        if ( person_instance is not None ):
                    
                            # get person ID and name.
                            person_id = person_instance.id
                            person_name = person_instance.get_name_string()
                            
                            # create coding info. for this coder.
                            person_coding_info = {}
                            
                            # coder ID
                            person_coding_info[ self.PERSON_CODING_INFO_CODER_ID ] = coder_id
                            
                            # person type
                            person_coding_info[ self.PERSON_CODING_INFO_PERSON_TYPE ]  = current_person_type
                            person_coding_info[ self.PERSON_CODING_INFO_PERSON_TYPE_INT ]  = current_person_type_int
                            
                            # Article_Person child record ID.
                            person_coding_info[ self.PERSON_CODING_INFO_ARTICLE_PERSON_ID ] = current_article_person.id
                            
                            # look for person in person info dictionary.
                            if person_id in person_info_dict_OUT:
                            
                                # person already encountered.  Add coding info
                                #    to the coding info list.
                                person_info = person_info_dict_OUT.get( person_id )
                                
                                # get person_coding_info_list.
                                person_coding_info_dict = person_info.get( self.PERSON_CODER_ID_TO_CODING_INFO_DICT )
                                
                                # append person_coding_info
                                person_coding_info_dict[ coder_id ] = person_coding_info
                                
                            else:
                            
                                # person not in the dictionary yet.  Create new dictionary.
                                person_info = {}
                                
                                # add information.
                                person_info[ self.PERSON_ID ] = person_id
                                person_info[ self.PERSON_NAME ] = person_name
                                
                                # add person coding info. for this coder.
                                person_coding_info_dict = {}
                                person_coding_info_dict[ coder_id ] = person_coding_info
                                person_info[ self.PERSON_CODER_ID_TO_CODING_INFO_DICT ] = person_coding_info_dict
                                
                                # add info to return dictionary.
                                person_info_dict_OUT[ person_id ] = person_info
                                
                            #-- END check to see if person is already in the dictionary. --#
                            
                        else:
                        
                            # no person - output a message.
                            print( "In " + me + ": no person found for record: " + str( current_article_person ) )
                            
                        #-- END check to make sure that person is present. --#
            
                    #-- END loop over persons. --#
                    
                #-- END check to see if we have person type. --#
                
            #-- END check to see if QuerySet passed in. --#  
        
        #-- END check to see if Coder present --#
        
        return person_info_dict_OUT
        
    #-- END method process_person_qs() --#


#-- END class Reliability_Names --#


# declare variables
my_reliability_instance = None
tag_list = None
label = ""

# make reliability instance
my_reliability_instance = Reliability_Names()

# configure so that it limits to automated coder_type of OpenCalais_REST_API_v2.
#my_reliability_instance.limit_to_automated_coder_type = "OpenCalais_REST_API_v2"

# process articles
#tag_list = [ "prelim_reliability", ]
tag_list = [ "prelim_training_002", ]
my_reliability_instance.process_articles( tag_list )

# output to database.
label = "prelim_training_002"
my_reliability_instance.output_reliability_data( label )
