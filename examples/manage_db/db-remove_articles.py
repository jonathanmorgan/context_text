# imports
from sourcenet.models import Article
from django.contrib.auth.models import User

# declare variables - filter articles to delete
article_qs = None
article_id_in_list = []
article_id_not_in_list = []
article_tag_in_list = []
article_tag_not_in_list = []

# declare variables - variables used while clearing.
article_count = -1
article_counter = -1
current_article = None
article_id_list = []
temp_article_id_list = []
article_data_count = -1
article_data = None
article_data_id_list = []
article_tags = []
do_delete = False

#==============================================================================#
# !FILTER
#==============================================================================#

# Get all Articles.
article_qs = Article.objects.all()

#------------------------------------------------------------------------------#
# FILTER - filter on article IDs?
#------------------------------------------------------------------------------#

#article_id_in_list = [ 21161 ]
if ( ( article_id_in_list is not None ) and ( len( article_id_in_list ) > 0 ) ):

    # yes.
    article_qs = article_qs.filter( pk__in = article_id_in_list )

#-- END check to see if filter on specific IDs. --#

#------------------------------------------------------------------------------#
# FILTER - delete all articles except those whose IDs are specified?
#------------------------------------------------------------------------------#

# article_id_not_in_list = [ 21409, 21483, 21509, 21512, 21627, 21661, 21719, 21738, 21790, 21827, 21890, 21925, 28274, 28499, 28598, 28610, 28649, 28741, 28846, 90948, 90983, 91000, 91036, 91038, 91068, 91071, 91112, 91114, 91132, 91133, 91157, 91197, 91199, 91254, 94104, 94110, 94125, 94128, 94140, 94301, 94311, 94326, 94405, 94417, 94430, 94442 ]
if ( ( article_id_not_in_list is not None ) and ( len( article_id_not_in_list ) > 0 ) ):

    # filter - all articles except those in list.
    article_qs = article_qs.exclude( pk__in = article_id_not_in_list )

#-- END check to see if coder types to filter on --#

#------------------------------------------------------------------------------#
# FILTER - filter on related article tags?
#------------------------------------------------------------------------------#

#article_tag_in_list = [ 'prelim_network', 'prelim_reliability' ]
article_tag_in_list = []
if ( ( article_tag_in_list is not None ) and ( len( article_tag_in_list ) > 0 ) ):

    # filter on tags
    article_qs = article_qs.filter( tags__name__in = article_tag_in_list )

#-- END check to see if tags to filter on --#

#------------------------------------------------------------------------------#
# FILTER - exclude based on article tags ?
#------------------------------------------------------------------------------#

#article_tag_in_list = [ 'prelim_network', 'prelim_reliability' ]
#article_tag_not_in_list = [ 'prelim_reliability', ]
if ( ( article_tag_not_in_list is not None ) and ( len( article_tag_not_in_list ) > 0 ) ):

    # filter on tags
    article_qs = article_qs.exclude( tags__name__in = article_tag_not_in_list )

#-- END check to see if tags to filter on --#

#==============================================================================#
# !PROCESSING
#==============================================================================#

# how many?
article_count = article_qs.count()

print( "Found " + str( article_count ) + " Article instances to remove." )

# tell me more...
article_counter = 0
for current_article in article_qs:

    # increment article_counter
    article_counter += 1

    # add id to lists
    article_id_list.append( str( current_article.id ) )
    temp_article_id_list.append( str( current_article.id ) )

    # how many Article_Data?
    #article_data_count = current_article.article_data_set.count()
    #print( "- Article " + str( current_article.id ) + " - Article_Data count: " + str( article_data_count ) + "; details: " + str( current_article ) )
    
    # loop over Article_Data
    for article_data in current_article.article_data_set.all():
    
        # add id to list
        article_data_id_list.append( str( article_data.id ) )

        #print( "    - ==> Article_Data: " + str( article_data ) )
        
    #-- END loop over article_author_set --#
    
    '''
    # get tags
    article_tags = current_article.tags.all()
    
    if ( len( article_tags ) == 0 ):
    
        print( "    - NO TAGS HOLY SMOKES NO WAY!!!" )
    
    else:
    
        print( "    - related article tags: " + str( article_tags ) )
    
    #-- END check if there are tags --#
    '''
    
    # delete Article and children?
    if ( do_delete == True ):
    
        # yes - delete.
        current_article.delete()
        
    #-- END check to see if we delete or not... --#
    
    # output something every thousand articles.
    if ( ( article_counter % 1000 ) == 0 ):
    
        print( "processed " + str( article_counter ) + " articles: " + ", ".join( temp_article_id_list ) )
        temp_article_id_list = []
        
    #-- END check to see if time to output something. --#
    
#-- END loop over article data. --#

print( "\n\nID lists:\n" )
print( "- article_id_list count = " + str( len( article_id_list ) ) )
print( "- article_data_id_list count = " + str( len( article_data_id_list ) ) )

# delete Article and children?
if ( do_delete == False ):

    # yes - delete.
    print( "\n\n====> NOTE: do_delete == False - DRY RUN - no changes made." )
    
#-- END check to see if we delete or not... --#
    