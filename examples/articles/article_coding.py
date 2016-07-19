# imports

# sourcenet imports
from sourcenet.models import Article
from sourcenet.article_coding.article_coding import ArticleCoding

# declare variables

# declare variables - article filter parameters
start_pub_date = None # should be datetime instance
end_pub_date = None # should be datetime instance
tag_in_list = []
paper_id_in_list = []
section_list = []
article_id_in_list = []
params = {}

# declare variables - processing
my_article_coding = None
article_qs = None
article_count = -1
coding_status = ""
do_limit_to_one = False
do_coding = False

# first, get a list of articles to code.

# ! Set param values.

# ==> start and end dates
#start_pub_date = "2009-12-06"
#end_pub_date = "2009-12-12"

# ==> tagged articles
#tag_in_list = "prelim_reliability"
#tag_in_list = "prelim_network"
#tag_in_list = "prelim_unit_test_007"
#tag_in_list = [ "prelim_reliability", "prelim_network" ]
#tag_in_list = [ "prelim_reliability_test" ] # 60 articles - Grand Rapids only.
tag_in_list = [ "prelim_reliability_combined" ] # 87 articles, Grand Rapids and Detroit.

# ==> IDs of newspapers to include.
#paper_id_in_list = "1"

# ==> names of sections to include.
#section_list = "Lakeshore,Front Page,City and Region,Business"

# ==> just limit to specific articles by ID.
#article_id_in_list = [ 360962 ]
#article_id_in_list = [ 28598 ]
#article_id_in_list = [ 21653, 21756 ]
#article_id_in_list = [ 90948 ]
#article_id_in_list = [ 21627, 21609, 21579 ]

# filter parameters
params[ ArticleCoding.PARAM_START_DATE ] = start_pub_date
params[ ArticleCoding.PARAM_END_DATE ] = end_pub_date
params[ ArticleCoding.PARAM_TAG_LIST ] = tag_in_list
params[ ArticleCoding.PARAM_PUBLICATION_LIST ] = paper_id_in_list
params[ ArticleCoding.PARAM_SECTION_LIST ] = section_list
params[ ArticleCoding.PARAM_ARTICLE_ID_LIST ] = article_id_in_list

# set coder you want to use.

# OpenCalais REST API v.2
params[ ArticleCoding.PARAM_CODER_TYPE ] = ArticleCoding.ARTICLE_CODING_IMPL_OPEN_CALAIS_API_V2

# get instance of ArticleCoding
my_article_coding = ArticleCoding()

# set params
my_article_coding.store_parameters( params )

# create query set - ArticleCoding does the filtering for you.
article_qs = my_article_coding.create_article_query_set()

# limit to one for an initial test?
if ( do_limit_to_one == True ):

    # yes.
    article_qs = article_qs[ : 1 ]

#-- END check to see if limit to one record. --#

# get article count
article_count = article_qs.count()

# Do coding?
if ( do_coding == True ):

    # yes - make sure we have at least one article:
    if ( article_count > 0 ):

        # invoke the code_article_data( self, query_set_IN ) method.
        coding_status = my_article_coding.code_article_data( article_qs )
    
        # output status
        print( "\n\n==============================\n\nCoding status: \"" + coding_status + "\"" )
    
    #-- END check to see if article count. --#
    
else:
    
    # output matching article count.
    print( "do_coding == False, so dry run" )
    print( "- query params:" )
    print( params )
    print( "- matching article count: " + str( article_count ) )
    
#-- END check to see if we do_coding --#
