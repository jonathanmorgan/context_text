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
article_id_in_list = []
article_count = -1
coding_status = ""
do_coding = False

# first, get a list of articles to code.
start_pub_date = "2009-12-06"
end_pub_date = "2009-12-12"
#tag_in_list = "prelim_reliability"
#tag_in_list = "prelim_network"
#tag_in_list = "prelim_unit_test_007"
# NOTE - THIS DOES NOT WORK: tag_in_list = [ "prelim_reliability", "prelim_network" ]
tag_in_list = "prelim_reliability,prelim_network"
paper_id_in_list = "1"
section_list = "Lakeshore,Front Page,City and Region,Business"

# filter parameters
#params[ ArticleCoding.PARAM_START_DATE ] = start_pub_date
#params[ ArticleCoding.PARAM_END_DATE ] = end_pub_date
params[ ArticleCoding.PARAM_TAG_LIST ] = tag_in_list
#params[ ArticleCoding.PARAM_PUBLICATION_LIST ] = paper_id_in_list
#params[ ArticleCoding.PARAM_SECTION_LIST ] = section_list

# set coder you want to use.

# OpenCalais REST API
params[ ArticleCoding.PARAM_CODER_TYPE ] = ArticleCoding.ARTICLE_CODING_IMPL_OPEN_CALAIS_API_V2

# get instance of ArticleCoding
my_article_coding = ArticleCoding()

# set params
my_article_coding.store_parameters( params )

# create query set - ArticleCoding does the filtering for you.
article_qs = my_article_coding.create_article_query_set()

# limit to one for an initial test?
#article_qs = article_qs[ : 1 ]

# filter on related article IDs?
#article_id_in_list = [ 360962 ]
#article_id_in_list = [ 28598 ]
#article_id_in_list = [ 21653, 21756 ]
#article_id_in_list = [ 90948 ]
#article_id_in_list = [ 21627, 21609, 21579 ]
if ( len( article_id_in_list ) > 0 ):

    # yes.
    article_qs = article_qs.filter( id__in = article_id_in_list )

#-- END check to see if filter on specific IDs. --#

# make sure we have at least one article
article_count = article_qs.count()

# Do coding?
if ( do_coding == True ):

    # yes - as long as we have articles.
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
