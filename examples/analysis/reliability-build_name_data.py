# imports
from sourcenet.models import Article

# declare variables - retrieving reliability sample.
article_qs = None
current_article = None
article_data_qs = None
article_data_count = -1

# declare variables - compiling information for articles.
article_id = -1
article_to_info_dict = None
article_info_dict = None
coder_dict = None
current_article_data = None
article_data_id_list = None
article_coder_id_list = None
article_data_id = -1
article_data_coder = None
article_data_coder_id = None
author_info_dict = None
source_info_dict = None

# dictionary field names
ARTICLE_ID = "article_id"
ARTICLE_DATA_ID_LIST = "article_data_id_list"
ARTICLE_CODER_ID_LIST = "article_coder_id_list"
AUTHOR_INFO_DICT = "author_info_dict"
SOURCE_INFO_DICT = "source_info_dict"

# source and author info dicts will use same field names.
PERSON_ID = "person_id"
PERSON_NAME = "person_name"
PERSON_CODER_ID_LIST = "person_coder_id_list"


#-------------------------------------------------------------------------------
# function definitions
#-------------------------------------------------------------------------------


def process_person_qs( coder_IN, article_person_qs_IN, person_info_dict_IN ):
    
    '''
    Accepts User instance of user who coded the Article, Article_Person QuerySet
       (either Article_Author or Article_Source) and a dictionary to be used to
       build up a map of IDs to information on people found in a given article.
       Loops over entries and builds up this dictionary that maps IDs of persons
       identified in the text to details on the person (including the Person's
       ID, string name, and the coders who detected that person).  Returns the
       dictionary.
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
    person_coder_list = None
    
    # make sure we have a coder
    if ( coder_IN is not None ):
    
        # make sure we have a queryset.
        if ( article_person_qs_IN is not None ):
        
            # got a dictionary passed in?
            if ( person_info_dict_IN is not None ):
            
                person_info_dict_OUT = person_info_dict_IN
            
            #-- END check to see if we have a dictionary passed in. --#
    
            # compile information on authors.
            for current_article_person in article_person_qs_IN:
            
                # get coder ID.
                coder_id = coder_IN.id
            
                # get person instance.
                person_instance = current_article_person.person
            
                # got one?  Anonymous sources won't have one.  If we find a
                #    record with no associated person, move on.
                if ( person_instance is not None ):
            
                    # get person ID and name.
                    person_id = person_instance.id
                    person_name = person_instance.get_name_string()
                    
                    # look for person in person info dictionary.
                    if person_id in person_info_dict_OUT:
                    
                        # person already encountered.  Add the coder ID to the coder
                        #    list.
                        person_info = person_info_dict_OUT.get( person_id )
                        
                        # get coder list.
                        person_coder_list = person_info.get( PERSON_CODER_ID_LIST )
                        
                        # append coder ID.
                        person_coder_list.append( coder_id )
                        
                    else:
                    
                        # person not in the dictionary yet.  Create new dictionary.
                        person_info = {}
                        
                        # add information.
                        person_info[ PERSON_ID ] = person_id
                        person_info[ PERSON_NAME ] = person_name
                        person_info[ PERSON_CODER_ID_LIST ] = [ coder_id, ]
                        
                        # add info to return dictionary.
                        person_info_dict_OUT[ person_id ] = person_info
                        
                    #-- END check to see if person is already in the dictionary. --#
                    
                else:
                
                    # no person - output a message.
                    print( "In " + me + ": no person found for record: " + str( current_article_person ) )
                    
                #-- END check to make sure that person is present. --#
    
            #-- END loop over persons. --#
            
        #-- END check to see if QuerySet passed in. --#  
    
    #-- END check to see if Coder present --#
    
    return person_info_dict_OUT
    
#-- END function process_person_qs() --#


#-------------------------------------------------------------------------------
# process articles to build data
#-------------------------------------------------------------------------------


# get articles with tag of "prelim_reliability"
article_qs = Article.objects.filter(tags__name = "prelim_reliability" )
article_qs = article_qs.order_by( "id" )

# build a dictionary that maps article ID to assorted details about the coding
#    of each article.
article_to_info_dict = {}

# For reference, also build up a dictionary of coder IDs that reference coder
#    instances, so we know how many coders.
coder_dict = {}

# loop over the articles.
for current_article in article_qs:

    # initialize variables
    article_info_dict = {}
    article_data_id_list = []
    article_coder_id_list = []
    author_info_dict = {}
    source_info_dict = {}

    # get article_id
    article_id = current_article.id

    # get article data for this article
    article_data_qs = current_article.article_data_set.all()
    
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
        if article_data_coder_id not in coder_dict:

            # not there yet, add it.
            coder_dict[ article_data_coder_id ] = article_data_coder
            
        #-- END check to see if ID is in master coder dictionary --#
    
        # add Article_Data ID to list.
        article_data_id = current_article_data.id
        article_data_id_list.append( article_data_id )
        
        # get lists of authors and sources.
        article_data_author_qs = current_article_data.article_author_set.all()
        article_data_source_qs = current_article_data.article_source_set.all()
        
        # call process_person_qs for authors.
        author_info_dict = process_person_qs( article_data_coder, article_data_author_qs, author_info_dict )
                
        # and call process_person_qs for sources.
        source_info_dict = process_person_qs( article_data_coder, article_data_source_qs, source_info_dict )
                
    #-- END loop over related Article_Data
    
    # update artucle info dictionary
    article_info_dict[ ARTICLE_ID ] = article_id
    article_info_dict[ ARTICLE_DATA_ID_LIST ] = article_data_id_list
    article_info_dict[ ARTICLE_CODER_ID_LIST ] = article_coder_id_list
    article_info_dict[ AUTHOR_INFO_DICT ] = author_info_dict
    article_info_dict[ SOURCE_INFO_DICT ] = source_info_dict    

    # shouldn't need to do anything more - reference to this dictionary is
    #    already in the master map of article IDs to article info.

#-- END loop over articles. --#


#-------------------------------------------------------------------------------
# output data
#-------------------------------------------------------------------------------


# to start, just print.
print( article_to_info_dict )

# columns we want...
# - article_id
# - person_id
# - person_name
# - coder_1_detected
# - coder_1_person_id
# - coder_2_detected
# - coder_2_person_id
# - coder_3_detected
# - coder_3 person_id