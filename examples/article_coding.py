# imports

# sourcenet imports
from sourcenet.models import Article

# declare variables
article_qs = None
start_pub_date = None # should be datetime instance
end_pub_date = None # should be datetime instance
tag_in_list = []
paper_id_in_list = []

# first, get a list of articles to code.

# start with all articles.
article_list = Article.objects.all()

# filter using ArticleCoding...

'''

# filter on publication date?
if ( ( start_pub_date != None ) or ( end_pub_date != None ) ):

    # there is one or the other of the date range filters.
    if start_pub_date != None:
    
        # get articles with publication date greater than or equal to date.
        article_list = article_list.filter( pub_date_gte = start_pub_date )
    
    #-- END check to see if start date filter --#

    if end_pub_date != None:
    
        # get articles with publication date less than or equal to date.
        article_list = article_list.filter( pub_date_lte = end_pub_date )
    
    #-- END check to see if start date filter --#

#-- END check to see if publication date filters. --#

# filter on tags assigned to article?
if ( ( tag_in_list != None ) and ( len( tag_in_list ) > 0 ) ):

    # filter down to just Articles with tags in list.
    pass

#-- END check to see if list of tags to filter on --#

# filter on paper?
if ( ( paper_id_in_list != None ) and ( len( paper_id_in_list ) > 0 ) ):

    # filter to just articles associated with papers whose IDs are in list.
    pass
    
#-- END check to see if list of paper IDs is populated. --#

'''

# make instance of article coder - also ArticleCoding...

# give it list of articles.

# ready go!