# imports
from sourcenet.models import Article_Data
from django.contrib.auth.models import User

# declare variables - filter article data to clear
automated_user = None
article_data_qs = None
article_id_in_list = []

# declare variables - variables used while clearing.
article_data_count = -1
article_data = None
article_author_count = -1
article_source_count = -1
related_article = None
article_tags = []
article_author = None
article_source = None
article_id_list = []
article_data_id_list = []
article_author_id_list = []
article_source_id_list = []
do_delete = False

# get User with name "automated"
automated_user = User.objects.filter( username = "automated" ).get()

# find all Article_Data for automated user.
article_data_qs = Article_Data.objects.filter( coder = automated_user )

#------------------------------------------------------------------------------#
# FILTER - filter on coder type?
#------------------------------------------------------------------------------#

article_data_coder_type_in_list = [ 'OpenCalais_REST_API' ]
if ( ( article_data_coder_type_in_list is not None ) and ( len( article_data_coder_type_in_list ) > 0 ) ):

    # filter on coder type.
    article_data_qs = article_data_qs.filter( coder_type__in = article_data_coder_type_in_list )

#-- END check to see if coder types to filter on --#

#------------------------------------------------------------------------------#
# FILTER - filter on related article tags?
#------------------------------------------------------------------------------#

article_tag_in_list = [ 'prelim_network', 'prelim_reliability' ]
if ( ( article_tag_in_list is not None ) and ( len( article_tag_in_list ) > 0 ) ):

    # filter on tags
    article_data_qs = article_data_qs.filter( article__tags__name__in = article_tag_in_list )

#-- END check to see if tags to filter on --#

#------------------------------------------------------------------------------#
# FILTER - filter on related article IDs?
#------------------------------------------------------------------------------#

#article_id_in_list = [ 360962 ]
#article_id_in_list = [ 28598 ]
# article_id_in_list = [ 21653, 21756 ]
if ( ( article_id_in_list is not None ) and ( len( article_id_in_list ) > 0 ) ):

    # yes.
    article_data_qs = article_data_qs.filter( article__id__in = article_id_in_list )

#-- END check to see if filter on specific IDs. --#

# how many?
article_data_count = article_data_qs.count()

print( "Found " + str( article_data_count ) + " Article_Data for automated coder." )

# tell me more...
for article_data in article_data_qs:

    # add id to data list
    article_data_id_list.append( str( article_data.id ) )

    # how many Article_Author?
    article_author_count = article_data.article_author_set.count()
    
    # how many Article_Source
    article_source_count = article_data.article_source_set.count()

    print( "- Article_Data " + str( article_data.id ) + " - authors: " + str( article_author_count ) + "; sources: " + str( article_source_count ) + "; details: " + str( article_data ) )
    
    # loop over article_authors
    for article_author in article_data.article_author_set.all():
    
        # add id to data list
        article_author_id_list.append( str( article_author.id ) )

        print( "    - ==> Article_Author: " + str( article_author ) )
        
    #-- END loop over article_author_set --#
    
    # loop over article_sources
    for article_source in article_data.article_source_set.all():
    
        # add id to data list
        article_source_id_list.append( str( article_source.id ) )

        print( "    - ==> Article_Source: " + str( article_source ) )
        
    #-- END loop over article_author_set --#
    
    # get article...
    related_article = article_data.article
    
    # add ID to list
    article_id_list.append( str( related_article.id ) )
    
    # ...and get tags
    article_tags = related_article.tags.all()
    
    if ( len( article_tags ) == 0 ):
    
        print( "    - NO TAGS HOLY SMOKES NO WAY!!!" )
    
    else:
    
        print( "    - related article tags: " + str( article_tags ) )
    
    #-- END check if there are tags --#
    
    # delete Article_Data and children?
    if ( do_delete == True ):
    
        # yes - delete.
        article_data.delete()
        
    #-- END check to see if we delete or not... --#
    
#-- END loop over article data. --#

print( "\n\nID lists:\n" )
print( "- Article ( " + str( len( article_id_list ) ) + " ): " + str( ", ".join( article_id_list ) ) )
print( "- Article_Data ( " + str( len( article_data_id_list ) ) + " ): " + str( ", ".join( article_data_id_list ) ) )
print( "- Article_Author ( " + str( len( article_author_id_list ) ) + " ): " + str( ", ".join( article_author_id_list ) ) )
print( "- Article_Source ( " + str( len( article_source_id_list ) ) + " ): " + str( ", ".join( article_source_id_list ) ) )

# delete Article_Data and children?
if ( do_delete == False ):

    # yes - delete.
    print( "\n\n====> NOTE: do_delete == False - DRY RUN - no changes made." )
    
#-- END check to see if we delete or not... --#
    