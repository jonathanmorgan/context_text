# imports
from sourcenet.models import Article_Data
from sourcenet.models import Person
from django.contrib.auth.models import User
import six

# declare variables
article_data_qs = None
tag_in_list = []
article_data_count = -1
article_data = None
coder_to_count_map = {}
current_coder = None
current_coder_id = -1
current_coder_username = ""
current_coder_count = -1
article_to_coder_list_map = {}
current_article = None
current_article_id = -1
current_coder_list = None

# get list of Article_Data
article_data_qs = Article_Data.objects.all()

# first, filter Article_Data to articles with one or more tags.
tag_in_list = [ 'prelim_reliability_test', ]
article_data_qs = article_data_qs.filter( article__tags__name__in = tag_in_list )

# first, just see what our count is.
article_data_count = article_data_qs.count()

# loop, building a count per user.
for article_data in article_data_qs:

    # get coder and ID
    current_coder = article_data.coder
    current_coder_id = current_coder.id
    current_coder_username = current_coder.username
    
    # get current count.
    current_coder_count = coder_to_count_map.get( current_coder_username, 0 )    # update count map

    # incremenet
    current_coder_count += 1
    
    # store back in map.
    coder_to_count_map[ current_coder_username ] = current_coder_count
    
    # get article and ID
    current_article = article_data.article
    current_article_id = current_article.id
    
    # get list of coder IDs associated with article.
    current_coder_list = article_to_coder_list_map.get( current_article_id, [] )
    
    # see if current coder is in list.
    if ( current_coder_username not in current_coder_list ):
    
        # nope.  Add them.
        current_coder_list.append( current_coder_username )
        
    #-- END check to see if coder in article's list.
    
    # store list back in map.
    article_to_coder_list_map[ current_article_id ] = current_coder_list
    
#-- END loop over Article_Data --#