# imports

import six

# context_text imports
from context_text.models import Article
from context_text.article_coding.article_coding import ArticleCoding

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
do_i_print_updates = True
my_article_coding = None
article_qs = None
article_count = -1
coding_status = ""
limit_to = -1
do_coding = False

# declare variables - results
success_count = -1
success_list = None
got_errors = False
error_count = -1
error_dictionary = None
error_article_id = -1
error_status_list = None
error_status = ""
error_status_counter = -1

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
#tag_in_list = [ "prelim_reliability_combined" ] # 87 articles, Grand Rapids and Detroit.
#tag_in_list = [ "prelim_training_001" ]
tag_in_list = [ "grp_month" ]

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
#article_id_in_list = [ 48778 ]
#article_id_in_list = [ 6065 ]
#article_id_in_list = [ 221858 ]
#article_id_in_list = [ 23804, 22630 ]
article_id_in_list = [ 23804 ]

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
my_article_coding.do_print_updates = do_i_print_updates

# set params
my_article_coding.store_parameters( params )

# create query set - ArticleCoding does the filtering for you.
article_qs = my_article_coding.create_article_query_set()

# limit for an initial test?
if ( ( limit_to is not None ) and ( isinstance( limit_to, int ) == True ) and ( limit_to > 0 ) ):

    # yes.
    article_qs = article_qs[ : limit_to ]

#-- END check to see if limit --#

# get article count
article_count = article_qs.count()

print( "Query params:" )
print( params )
print( "Matching article count: " + str( article_count ) )

# Do coding?
if ( do_coding == True ):

    print( "do_coding == True - it's on!" )

    # yes - make sure we have at least one article:
    if ( article_count > 0 ):

        # invoke the code_article_data( self, query_set_IN ) method.
        coding_status = my_article_coding.code_article_data( article_qs )
    
        # output status
        print( "\n\n==============================\n\nCoding status: \"" + coding_status + "\"" )
        
        # get success count
        success_count = my_article_coding.get_success_count()
        print( "\n\n====> Count of articles successfully processed: " + str( success_count ) )    
        
        # if successes, list out IDs.
        if ( success_count > 0 ):
        
            # there were successes.
            success_list = my_article_coding.get_success_list()
            print( "- list of successfully processed articles: " + str( success_list ) )
        
        #-- END check to see if successes. --#
        
        # got errors?
        got_errors = my_article_coding.has_errors()
        if ( got_errors == True ):
        
            # get error dictionary
            error_dictionary = my_article_coding.get_error_dictionary()
            
            # get error count
            error_count = len( error_dictionary )
            print( "\n\n====> Count of articles with errors: " + str( error_count ) )
            
            # loop...
            for error_article_id, error_status_list in six.iteritems( error_dictionary ):
            
                # output errors for this article.
                print( "- errors for article ID " + str( error_article_id ) + ":" )
                
                # loop over status messages.
                error_status_counter = 0
                for error_status in error_status_list:
                
                    # increment status
                    error_status_counter += 1

                    # print status
                    print( "----> status #" + str( error_status_counter ) + ": " + error_status )
                    
                #-- END loop over status messages. --#
            
            #-- END loop over articles. --#
   
        #-- END check to see if errors --#
    
    #-- END check to see if article count. --#
    
else:
    
    # output matching article count.
    print( "do_coding == False, so dry run" )
    
#-- END check to see if we do_coding --#
