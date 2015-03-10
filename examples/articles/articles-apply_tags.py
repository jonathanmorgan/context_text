'''
django-taggit documentation: https://github.com/alex/django-taggit

Adding tags to a model:

    from django.db import models
    
    from taggit.managers import TaggableManager
    
    class Food(models.Model):
        # ... fields here
    
        tags = TaggableManager()

Interacting with a model that has tags:

    >>> apple = Food.objects.create(name="apple")
    >>> apple.tags.add("red", "green", "delicious")
    >>> apple.tags.all()
    [<Tag: red>, <Tag: green>, <Tag: delicious>]
    >>> apple.tags.remove("green")
    >>> apple.tags.all()
    [<Tag: red>, <Tag: delicious>]
    >>> Food.objects.filter(tags__name__in=["red"])
    [<Food: apple>, <Food: cherry>]

'''

# imports
from sourcenet.models import Article

# declare variables
article_qs = None
article_id_list = []
article_count = -1
current_article = None
tag_value = ""

# set tag value and list of article IDs to tag.
#tag_value = "prelim_network"
#article_id_list = [ 21230, 21189, 21228, 21172, 21338, 21290, 21355, 21287, 21161, 21372, 21268, 21311, 21370, 21190, 21350, 21174, 21395, 21428, 21400, 21404, 21471, 21462, 21409, 21435, 21549, 21570, 21551, 21557, 21515, 21501, 21509, 21524, 21512, 21536, 21495, 21483, 21542, 21569, 21608, 21656, 21632, 21578, 21588, 21675, 21604, 21653, 21652, 21620, 21661, 21644, 21629, 21601, 21611, 21619, 21590, 21617, 21579, 21609, 21666, 21627, 21738, 21679, 21758, 21689, 21754, 21756, 21677, 21743, 21719, 21736, 21702, 21699, 21720, 21753, 21855, 21851, 21779, 21782, 21775, 21827, 21808, 21814, 21794, 21820, 21798, 21781, 21813, 21790, 21795, 21828, 21835, 21766, 21829, 21863, 21871, 21867, 21900, 21888, 21899, 21923, 21927, 21880, 21941, 21903, 21925, 21898, 21890, 21931, 21887 ]

# set tag value and list of article IDs to tag.
tag_value = "prelim_unit_test_002"
article_id_list = [ 55327, 163182, 27459, 318737, 114053, 61763, 54477, 293543, 24994, 4343 ]

# get articles whose IDs are in the article_id_list
article_qs = Article.objects.filter( id__in = article_id_list )

# first, just make sure that worked.
article_count = article_qs.count()

# Check count of articles retrieved.
print( "Got " + str( article_count ) + " articles to tag with \"" + tag_value + "\"." )

# loop over articles.
for current_article in article_qs:

    # add tag.
    current_article.tags.add( tag_value )
    
    # output the tags.
    print( "- Tags for article " + str( current_article.id ) + " : " + str( current_article.tags.all() ) )
    
#-- END loop over articles --#