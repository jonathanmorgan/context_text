# imports
from sourcenet.models import Article
from sourcenet.models import Newspaper

# declare variables - Grand Rapids Press
grp_local_news_sections = []
grp_newspaper = None
grp_article_qs = None
current_article = None
author_string = ""
slash_index = -1
affiliation = ""
article_count = -1
article_counter = -1
article_id_list = []
tags_in_list = []
tags_not_in_list = []

# declare variables - size of random sample we want
random_count = 20

# declare variables - also, apply tag?
do_apply_tag = False
tag_to_apply = ""

# set up "local, regional and state news" sections
grp_local_news_sections.append( "Lakeshore" )
grp_local_news_sections.append( "Front Page" )
grp_local_news_sections.append( "City and Region" )
grp_local_news_sections.append( "Business" )
grp_local_news_sections.append( "Religion" )
grp_local_news_sections.append( "State" )
grp_local_news_sections.append( "Special" )

# Grand Rapids Press
# get newspaper instance for GRP.
grp_newspaper = Newspaper.objects.get( id = 1 )

'''
# populate author_affiliation in Article table for GR Press.
grp_article_qs = Article.objects.filter( newspaper = grp_newspaper )
grp_article_qs = grp_article_qs.filter( author_string__contains = "/" )
grp_article_qs = grp_article_qs.filter( author_affiliation__isnull = True )

article_count = grp_article_qs.count()
article_counter = 0
for current_article in grp_article_qs:

    article_counter = article_counter + 1

    # output article.
    print( "- Article " + str( article_counter ) + " of " + str( article_count ) + ": " + str( current_article ) )
    
    # get author_string
    author_string = current_article.author_string
    
    # find "/"
    slash_index = author_string.find( "/" )
    
    # got one?
    if ( slash_index > -1 ):
    
        # yes.  get everything after the slash.
        affiliation = author_string[ ( slash_index + 1 ) : ]
        
        # strip off white space
        affiliation = affiliation.strip()
        
        print( "    - Affiliation = \"" + affiliation + "\"" )
        
        current_article.author_affiliation = affiliation
        current_article.save()
        
    #-- END check to see if "/" present.
    
#-- END loop over articles. --#
'''

# now, need to find local news articles to test on.
grp_article_qs = Article.objects.filter( newspaper = grp_newspaper )

# only the locally implemented sections
grp_article_qs = grp_article_qs.filter( section__in = Article.GRP_NEWS_SECTION_NAME_LIST )

# and, with an in-house author
grp_article_qs = grp_article_qs.filter( Article.Q_GRP_IN_HOUSE_AUTHOR )

# how many is that?
article_count = grp_article_qs.count()

print( "Article count before pulling out those with tags that contain \"prelim\": " + str( article_count ) )

# ==> tags

# tags to exclude
#tags_not_in_list = [ "prelim_reliability", "prelim_network" ]
if ( len( tags_not_in_list ) > 0 ):

    # exclude those in a list
    print( "filtering out articles with tags: " + str( tags_not_in_list ) )
    grp_article_qs = grp_article_qs.exclude( tags__name__in = tags_not_in_list )

else:

    # if not specified, filter out all articles with any tag whose name contains
    #    "prelim".
    print( "filtering out articles with tags that contain \"prelim\"" )
    grp_article_qs = grp_article_qs.exclude( tags__name__contains = "prelim" )
    
#-- END check to see if we have a specific list of tags we want to exclude --#

# include only those with certain tags.
#tags_in_list = [ "prelim_unit_test_001", "prelim_unit_test_002", "prelim_unit_test_003", "prelim_unit_test_004", "prelim_unit_test_005", "prelim_unit_test_006", "prelim_unit_test_007" ]
if ( len( tags_in_list ) > 0 ):

    # filter
    print( "filtering to just articles with tags: " + str( tags_in_list ) )
    grp_article_qs = grp_article_qs.filter( tags__name__in = tags_in_list )
    
#-- END check to see if we have a specific list of tags we want to include --#

# how many is that?
article_count = grp_article_qs.count()

print( "Article count after tag filtering: " + str( article_count ) )

# to get random, order them by "?", then use slicing to just grab 10 or so.
grp_article_qs = grp_article_qs.order_by( "?" )[ : random_count ]

# this is a nice algorithm, also:
# - http://www.titov.net/2005/09/21/do-not-use-order-by-rand-or-how-to-get-random-rows-from-table/

# make list of article IDs.
article_id_list = []
for current_article in grp_article_qs:

    # add IDs to article_id_list
    article_id_list.append( str( current_article.id ) )
    
    # apply a tag while we are at it?
    if ( ( do_apply_tag == True ) and ( tag_to_apply is not None ) and ( tag_to_apply != "" ) ):
    
        # yes, please.  Add tag.
        current_article.tags.add( tag_value )
        
        # output the tags.
        print( "- Tags for article " + str( current_article.id ) + " : " + str( current_article.tags.all() ) )

    #-- END check to see if we apply tag. --#
    
#-- END loop over articles --#

# output the list.
print( "List of " + str( random_count ) + " local GRP staff article IDs: " + ", ".join( article_id_list ) )