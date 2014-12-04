# imports

# sourcenet imports
from sourcenet.models import Article
from sourcenet.article_coding.article_coding import ArticleCoding

# declare variables
start_pub_date = None # should be datetime instance
end_pub_date = None # should be datetime instance
tag_in_list = []
paper_id_in_list = []
params = {}
my_article_coding = None
article_qs = None

# first, get a list of articles to code.
start_pub_date = "2009-12-06"
end_pub_date = "2009-12-12"
tag_in_list = "prelim,horse"
paper_id_in_list = "1"
section_list = ""

# filter parameters
params[ ArticleCoding.PARAM_START_DATE ] = start_pub_date
params[ ArticleCoding.PARAM_END_DATE ] = end_pub_date
#params[ ArticleCoding.PARAM_TAG_LIST ] = tag_in_list
params[ ArticleCoding.PARAM_PUBLICATION_LIST ] = paper_id_in_list
#params[ ArticleCoding.PARAM_SECTION_LIST ] = section_list

# filter using ArticleCoding

# get instance of ArticleCoding
my_article_coding = ArticleCoding()

# set params
my_article_coding.store_parameters( params )

# create query set
article_qs = my_article_coding.create_article_query_set()

# make instance of article coder - also ArticleCoding...

# give it list of articles.

# ready go!