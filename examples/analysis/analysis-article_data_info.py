# imports
from sourcenet.models import Article_Data
from sourcenet.models import Person
from django.contrib.auth.models import User
import six

# declare variables
article_data_qs = None
temp_author = None
author_in_list = []
coder_to_article_id_list_map = {}
article_data_instance = None
article_data_id = -1
current_coder = None
current_coder_id = -1
current_article = None
current_article_id = None
coder_article_id_list = None
coder_article_count = -1

# keep track of authors.
all_authors_list = []
coder_to_author_id_list_map = {}
coder_author_id_list = None
author_qs = None
article_author = None
author_person = None
author_person_id = -1
coder_author_count = -1

# keep track of sources.
all_sources_list = []
coder_to_source_id_list_map = {}
coder_source_id_list = None
source_qs = None
article_source = None
source_person = None
source_person_id = -1
coder_source_count = -1

# get all article data for articles with tag "prelim_network".
article_data_qs = Article_Data.objects.filter( article__tags__name = "prelim_network" )

# make list of authors we want.
#temp_author = Person.objects.get( id = 591 )
#author_in_list.append( temp_author )
#temp_author = Person.objects.get( id = 599 )
#author_in_list.append( temp_author )
#article_data_qs = article_data_qs.filter( article_author__person__in = author_in_list )

# if we care, filter out based on automated coder having a certain coder_type
coder_type_list = [ "OpenCalais_REST_API_v2", ]
article_data_qs = Article_Data.filter_automated_by_coder_type( article_data_qs, coder_type_list )

# loop over article datas
for article_data_instance in article_data_qs:

    # article data ID
    article_data_id = article_data_instance.id
    
    # get coder and ID.
    current_coder = article_data_instance.coder
    current_coder_id = current_coder.id
    
    # get article ID
    current_article = article_data_instance.article
    current_article_id = current_article.id
    
    #--------------------------------------------------------------------------#
    # list of articles per coder.
    #--------------------------------------------------------------------------#

    # look for coder in article map.
    if ( current_coder_id not in coder_to_article_id_list_map ):
    
        # not there.  Add ID and empty list.
        coder_to_article_id_list_map[ current_coder_id ] = []
    
    #-- END check to see if coder in map. --#
    
    # get article list for current ID.
    coder_article_id_list = coder_to_article_id_list_map.get( current_coder_id, None )

    # see if current article ID is in list.
    if ( current_article_id not in coder_article_id_list ):
    
        # it is not. Add it.
        coder_article_id_list.append( current_article_id )
        
    else:
    
        # it is - probably shouldn't be duplicates.
        print( "Article ID " + str( current_article_id ) + " already in list ( " + str( coder_article_id_list ) + " ) for coder " + str( current_coder_id ) )
        
    #-- END check to see if article already in list --#
    
    #--------------------------------------------------------------------------#
    # list of authors per coder.
    #--------------------------------------------------------------------------#

    # look for coder in author map.
    if ( current_coder_id not in coder_to_author_id_list_map ):
    
        # not there.  Add ID and empty list.
        coder_to_author_id_list_map[ current_coder_id ] = []
    
    #-- END check to see if coder in map. --#
    
    # get author list for current ID.
    coder_author_id_list = coder_to_author_id_list_map.get( current_coder_id, None )
    
    # get the QuerySet of authors for the Article_Data.
    author_qs = article_data_instance.article_author_set.all()

    # loop over sources.
    for article_author in author_qs:
    
        # get person and person ID from article_author
        author_person = article_author.person
        author_person_id = author_person.id

        # see if current author ID is in coder's list.
        if ( author_person_id not in coder_author_id_list ):
        
            # it is not. Add it.
            coder_author_id_list.append( author_person_id )
            
        else:
        
            # it is - could be duplicates, but output anyway.
            print( "Author ID " + str( author_person_id ) + " already in list ( " + str( coder_author_id_list ) + " ) for coder " + str( current_coder_id ) )
            
        #-- END check to see if author already in list --#
        
        # see if current author ID is in overall list.
        if ( author_person_id not in all_authors_list ):
        
            # nope.  Add it.
            all_authors_list.append( author_person_id )
        
        #-- END check to see if authors is in all sources list --#

    #-- END loop over article authors --#

    #--------------------------------------------------------------------------#
    # list of sources per coder.
    #--------------------------------------------------------------------------#

    # look for coder in source map.
    if ( current_coder_id not in coder_to_source_id_list_map ):
    
        # not there.  Add ID and empty list.
        coder_to_source_id_list_map[ current_coder_id ] = []
    
    #-- END check to see if coder in map. --#
    
    # get source list for current ID.
    coder_source_id_list = coder_to_source_id_list_map.get( current_coder_id, None )
    
    # get the QuerySet of sources for the Article_Data.
    source_qs = article_data_instance.get_quoted_article_sources_qs()

    # loop over sources.
    for article_source in source_qs:
    
        # get person and person ID from article_source
        source_person = article_source.person
        
        # got a person source?
        if ( source_person is not None ):

            # it is a person - process.
            source_person_id = source_person.id
    
            # see if current source ID is in coder's list.
            if ( source_person_id not in coder_source_id_list ):
            
                # it is not. Add it.
                coder_source_id_list.append( source_person_id )
                
            else:
            
                # it is - could be duplicates, but output anyway.
                print( "Source ID " + str( source_person_id ) + " already in list ( " + str( coder_source_id_list ) + " ) for coder " + str( current_coder_id ) )
                
            #-- END check to see if source already in list --#
            
            # see if current source ID is in overall list.
            if ( source_person_id not in all_sources_list ):
            
                # nope.  Add it.
                all_sources_list.append( source_person_id )
            
            #-- END check to see if sources is in all sources list --#
            
        #-- END check to see if the source was a person --#

    #-- END loop over article sources --#
    
#-- END loop over Article_Data ---#

#==============================================================================#
# output details on each coder's articles.
#==============================================================================#

# loop over coder IDs in map, output count of articles, plus values in list.
for current_coder_id, coder_article_id_list in six.iteritems( coder_to_article_id_list_map ):

    # get count of articles.
    coder_article_count = len( coder_article_id_list )
    
    # output.
    print( "- Coder " + str( current_coder_id ) + ": " + str( coder_article_count ) + " articles, list: " + str( sorted( coder_article_id_list ) ) )
    
#-- END loop over coders and their articles. --#

# get articles for coder ID 4 (me) and 6 (brian)
coder_six_article_list = coder_to_article_id_list_map.get( 6, None )
coder_four_article_list = coder_to_article_id_list_map.get( 4, None )

# see if I had any articles at all...
if ( coder_four_article_list is not None ):

    # loop over coder four's articles, see how many are also in coder 6's list.
    for current_article_id in coder_four_article_list:
    
        # is this article in coder 6's list?
        if ( current_article_id in coder_six_article_list ):
        
            # it is!
            print( "- " + str( current_article_id ) + " - BOTH" )
        
        else:
        
            # it is not!
            print( "- " + str( current_article_id ) + " - ONLY 4" )
        
        #-- END check to see if article ID is in list. --#
        
    #-- END loop over coder 4's articles. --#
    
else:

    # no articles for coder 4 - output a message.
    print( "- no articles for coder 4, so all articles were coded by 6." )
    
#-- END check to see if anything by coder 4. --#

#==============================================================================#
# output details on each coder's authors.
#==============================================================================#

print( "\n\nAuthors:")

# loop over coder IDs in map, output count of authors, plus values in list.
for current_coder_id, coder_author_id_list in six.iteritems( coder_to_author_id_list_map ):

    # get count of articles.
    coder_author_count = len( coder_author_id_list )
    
    # output.
    print( "- Coder " + str( current_coder_id ) + ": " + str( coder_author_count ) + " authors, list: " + str( sorted( coder_author_id_list ) ) )
    
#-- END loop over coders and their authors. --#

# output.
print( "- Total: " + str( len( all_authors_list ) ) + " authors, list: " + str( sorted( all_authors_list ) ) )

#==============================================================================#
# output details on each coder's sources.
#==============================================================================#

print( "\n\nSources:")

# loop over coder IDs in map, output count of sources, plus values in list.
for current_coder_id, coder_source_id_list in six.iteritems( coder_to_source_id_list_map ):

    # get count of articles.
    coder_source_count = len( coder_source_id_list )
    
    # output.
    print( "- Coder " + str( current_coder_id ) + ": " + str( coder_source_count ) + " sources, list: " + str( sorted( coder_source_id_list ) ) )
    
#-- END loop over coders and their sources.. --#

# output.
print( "- Total: " + str( len( all_sources_list ) ) + " sources, list: " + str( sorted( all_sources_list ) ) )
