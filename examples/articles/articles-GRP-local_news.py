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
random_count = 10
article_id_list = []

# set up "local, regional and state news" sections
grp_local_news_sections.append( "Lakeshore" )
grp_local_news_sections.append( "Front Page" )
grp_local_news_sections.append( "City and Region" )
grp_local_news_sections.append( "Business" )
grp_local_news_sections.append( "Religion" )
grp_local_news_sections.append( "State" )

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

# now, filter to exclude those with tags whose name contains "prelim"
grp_article_qs = grp_article_qs.exclude( tags__name__contains = "prelim" )

# how many is that?
article_count = grp_article_qs.count()

print( "Article count after pulling out those with tags that contain \"prelim\": " + str( article_count ) )

# to get random, order them by "?", then use slicing to just grab 10 or so.
grp_article_qs = grp_article_qs.order_by( "?" )[ : random_count ]

# this is a nice algorithm, also:
# - http://www.titov.net/2005/09/21/do-not-use-order-by-rand-or-how-to-get-random-rows-from-table/

# make list of article IDs.
article_id_list = []
for current_article in grp_article_qs:

    # add IDs to article_id_list
    article_id_list.append( str( current_article.id ) )
    
#-- END loop over articles --#

# output the list.
print( "List of " + str( random_count ) + " local GRP staff article IDs: " + ", ".join( article_id_list ) )