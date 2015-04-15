# imports
from sourcenet.models import Article

# Django imports
from django.db.models import Q
from django.contrib.auth.models import User

# declare variables
article_qs = None
user1 = None
user2 = None


# first, get articles.
article_qs = Article.objects.all()

# next set up basic filters to match the network output I've been testing
article_qs = article_qs.filter( pub_date__gte = '2009-12-06' )
article_qs = article_qs.filter( pub_date__lte = '2009-12-12' )
article_qs.count() # 1194
article_qs = article_qs.filter( newspaper_id = 1 )
article_qs.count() # 818

# now, need to see how many have Article_Data coded by either brianbowe or
#    jonathanmorgan.

# get users.
user1 = User.objects.get( username = 'jonathanmorgan' )
user2 = User.objects.get( username = 'brianbowe' )
article_qs = article_qs.filter( article_data_set__in = [ user1, user2 ] )
