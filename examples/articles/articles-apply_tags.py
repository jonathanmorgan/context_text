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
    
    # include only those with certain tags.
    #tags_in_list = [ "prelim_unit_test_001", "prelim_unit_test_002", "prelim_unit_test_003", "prelim_unit_test_004", "prelim_unit_test_005", "prelim_unit_test_006", "prelim_unit_test_007" ]
    tags_in_list = [ "grp_month", ]
    if ( len( tags_in_list ) > 0 ):
    
        # filter
        print( "filtering to just articles with tags: " + str( tags_in_list ) )
        grp_article_qs = grp_article_qs.filter( tags__name__in = tags_in_list )
        
    #-- END check to see if we have a specific list of tags we want to include --#

'''

# imports
from context_text.models import Article
from context_text.article_coding.article_coding import ArticleCoding

# declare variables
params = {}
start_pub_date = ""
end_pub_date = ""
tag_in_list = []
paper_id_in_list = []
section_list = []
article_id_in_list = []
article_qs = None
article_count = -1
current_article = None
tag_value = ""


# first, get a list of articles to code.
#start_pub_date = "2009-12-06"
#end_pub_date = "2009-12-12"
#tag_in_list = "prelim_reliability"
#tag_in_list = "prelim_network"
#tag_in_list = "prelim_unit_test_007"
# NOTE - THIS DOES NOT WORK: tag_in_list = [ "prelim_reliability", "prelim_network" ]
#tag_in_list = "prelim_reliability,prelim_network"
#paper_id_in_list = "1"
#section_list = "Lakeshore,Front Page,City and Region,Business,State"

'''
# set tag value and list of article IDs to tag.
#tag_value = "prelim_network"
#article_id_in_list = [ 21230, 21189, 21228, 21172, 21338, 21290, 21355, 21287, 21161, 21372, 21268, 21311, 21370, 21190, 21350, 21174, 21395, 21428, 21400, 21404, 21471, 21462, 21409, 21435, 21549, 21570, 21551, 21557, 21515, 21501, 21509, 21524, 21512, 21536, 21495, 21483, 21542, 21569, 21608, 21656, 21632, 21578, 21588, 21675, 21604, 21653, 21652, 21620, 21661, 21644, 21629, 21601, 21611, 21619, 21590, 21617, 21579, 21609, 21666, 21627, 21738, 21679, 21758, 21689, 21754, 21756, 21677, 21743, 21719, 21736, 21702, 21699, 21720, 21753, 21855, 21851, 21779, 21782, 21775, 21827, 21808, 21814, 21794, 21820, 21798, 21781, 21813, 21790, 21795, 21828, 21835, 21766, 21829, 21863, 21871, 21867, 21900, 21888, 21899, 21923, 21927, 21880, 21941, 21903, 21925, 21898, 21890, 21931, 21887 ]

# set tag value and list of article IDs to tag.
#tag_value = "prelim_unit_test_002"
#article_id_in_list = [ 55327, 163182, 27459, 318737, 114053, 61763, 54477, 293543, 24994, 4343 ]

# set tag value and list of article IDs to tag.
#tag_value = "prelim_unit_test_003"
#article_id_in_list = [ 43243, 44808, 210962, 176440, 381987, 197261, 163317, 143953, 117333, 265657 ]

# set tag value and list of article IDs to tag.
#tag_value = "prelim_unit_test_005"
#article_id_in_list = [ 4831, 428321, 224205, 38250, 65897, 204366, 11502, 360962, 55309, 168322 ]

# set tag value and list of article IDs to tag.
tag_value = "prelim_unit_test_006"
article_id_in_list = [ 206821, 393270, 205305, 502312, 124085, 194572, 507668, 144914, 26961, 212046 ]

# set tag value and list of article IDs to tag.
tag_value = "prelim_unit_test_007"
article_id_in_list = [ 301421, 278674, 129226, 442001, 8522, 393832, 133315, 933, 392292, 210845 ]
'''

# set tag value and list of article IDs to tag.
tag_value = "prelim_training_001"
article_id_in_list = [ 210962, 318737, 210845, 55327, 442001, 20409, 43243, 107321, 204366, 933, 441982, 278674, 11502, 393270, 114053, 4343, 265657, 144914, 224205, 8522, 13940, 208628, 430963, 5912, 394675, 173981, 468630, 161267, 115737, 283436, 206679, 32594, 54383, 472109, 429682, 140651, 158908, 478518, 128889, 119984 ]

# filter parameters
params[ ArticleCoding.PARAM_START_DATE ] = start_pub_date
params[ ArticleCoding.PARAM_END_DATE ] = end_pub_date
params[ ArticleCoding.PARAM_TAG_LIST ] = tag_in_list
params[ ArticleCoding.PARAM_PUBLICATION_LIST ] = paper_id_in_list
params[ ArticleCoding.PARAM_SECTION_LIST ] = section_list
params[ ArticleCoding.PARAM_ARTICLE_ID_LIST ] = article_id_in_list

# get instance of ArticleCoding
my_article_coding = ArticleCoding()

# set params
my_article_coding.store_parameters( params )

# create query set - ArticleCoding does the filtering for you.
article_qs = my_article_coding.create_article_query_set()

# get articles whose IDs are in the article_id_list
#article_qs = Article.objects.filter( id__in = article_id_in_list )

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