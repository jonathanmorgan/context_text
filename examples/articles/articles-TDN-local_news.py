# support Python 3:
from __future__ import unicode_literals

#==============================================================================#
# ! imports
#==============================================================================#

# Django query object for OR-ing selection criteria together.
from django.db.models import Q

# imports - python_utilities
from python_utilities.logging.logging_helper import LoggingHelper

# imports - context_text
from context_text.collectors.newsbank.newspapers.DTNB import DTNB
from context_text.models import Article
from context_text.models import Article_Text
from context_text.models import Newspaper

#==============================================================================#
# ! declare variables
#==============================================================================#
selected_newspaper = None
article_qs = None
article_count = -1
article_counter = -1

# declare variables - filtering
start_date = ""
end_date = ""
local_news_sections = []
section_name_in_list = []
custom_article_q = None
affiliation = ""
article_id_list = []
article_id_in_list = []
tags_in_list = []
tags_not_in_list = []
filter_out_prelim_tags = False
random_count = -1
limit_count = -1
article_counter = -1

# declare variables - capturing author info.
do_capture_author_info = False
processing_counter = -1
processing_id_list = []
processing_section_list = []

# declare variables - size of random sample we want
#random_count = 60

# declare variables - also, apply tag?
do_apply_tag = False
tags_to_apply_list = []

# declare variables - details on author string anomalies
anomaly_detail = {}
author_anomaly_article_id = -1
author_anomaly_author_string = ""
author_anomaly_graf_1 = ""
author_anomaly_graf_2 = ""
anomaly_detail_string = ""

#==============================================================================#
# ! configure filters
#==============================================================================#

# ==> Article.filter_articles()
# date range, newspaper, section list, and custom Q().
start_date = ""
end_date = ""
selected_newspaper = None
section_name_in_list = None
custom_article_q = None

# month of local news from Detroit News from 2009-12-01 to 2009-12-31
start_date = "2009-12-01"
end_date = "2009-12-31"
selected_newspaper = Newspaper.objects.get( id = 2 ) # Detroit News

# limit to "local, regional and state news" sections.
section_name_in_list = DTNB.NEWS_SECTION_NAME_LIST

# limit to staff reporters.
#custom_article_q = DTNB.Q_IN_HOUSE_AUTHOR

# ==> article IDs - include
#article_id_in_list = None

# tests
#article_id_in_list = [ 90603 ]
#article_id_in_list = [ 90875 ]
#article_id_in_list = [ 91600 ]
#article_id_in_list = [ 91885 ]
#article_id_in_list = [ 91640 ]
#article_id_in_list = [ 91394 ]
#article_id_in_list = [ 91378 ]
#article_id_in_list = [ 90726 ]

# collective author names ("Detroit News staff", "The Detroit News", etc.)
#article_id_in_list = [ 92050 ]
#article_id_in_list = [ 92052 ]
#article_id_in_list = [ 92055 ]
#article_id_in_list = [ 92059 ]
#article_id_in_list = [ 92060 ]
#article_id_in_list = [ 92078 ]
#article_id_in_list = [ 92101 ]
#article_id_in_list = [ 92103 ]

# multiple names in byline
#article_id_in_list = [ 92069 ] # "Steve Pardo and Tom Greenwood"
#article_id_in_list = [ 92093 ] # "George Hunter, Tom Greenwood and Mark Hicks"


article_id_in_list = [ 92075 ]

# ==> tags - exclude
#tags_not_in_list = [ "prelim_reliability", "prelim_network" ]
tags_not_in_list = None

# ==> tags - include only those with certain tags.
#tags_in_list = [ "prelim_reliability", "prelim_network" ]
#tags_in_list = [ "prelim_reliability", ]
tags_in_list = None

# ==> filter out "*prelim*" tags?
filter_out_prelim_tags = False

# ==> ORDER BY - do we want a random sample?
#random_count = 10
random_count = -1

#==============================================================================#
# ! configure processing
#==============================================================================#

do_capture_author_info = True
do_apply_tag = False
tags_to_apply_list = []
#tags_to_apply_list = [ "minnesota1-20160409", "minnesota2-20160409", "minnesota3-20160409" ]

#==============================================================================#
# ! filtering
#==============================================================================#

# start with all articles
article_qs = Article.objects.all()

# ! ==> call Article.filter_articles()
article_qs = Article.filter_articles( qs_IN = article_qs,
                                      start_date = start_date,
                                      end_date = end_date,
                                      newspaper = selected_newspaper,
                                      section_name_list = section_name_in_list,
                                      custom_article_q = custom_article_q )

# how many is that?
article_count = article_qs.count()
print( "Article count before filtering on Article IDs: " + str( article_count ) )

# ! ==> article IDs in list
if ( ( article_id_in_list is not None ) and ( len( article_id_in_list ) > 0 ) ):

    # include those in a list
    print( "filtering articles to those with IDs: " + str( article_id_in_list ) )
    article_qs = article_qs.filter( id__in = article_id_in_list )

#-- END check to see if we have a specific list of tags we want to exclude --#

# how many is that?
article_count = article_qs.count()
print( "Article count before filtering on tags: " + str( article_count ) )

# ! ==> tags - exclude

# tags to exclude
if ( ( tags_not_in_list is not None ) and ( len( tags_not_in_list ) > 0 ) ):

    # exclude those in a list
    print( "exclude-ing articles with tags: " + str( tags_not_in_list ) )
    article_qs = article_qs.exclude( tags__name__in = tags_not_in_list )

#-- END check to see if we have a specific list of tags we want to exclude --#

# ! ==> tags - include only those with certain tags.
if ( ( tags_in_list is not None ) and ( len( tags_in_list ) > 0 ) ):

    # filter
    print( "filtering to just articles with tags: " + str( tags_in_list ) )
    article_qs = article_qs.filter( tags__name__in = tags_in_list )
    
#-- END check to see if we have a specific list of tags we want to include --#

# ! ==> filter out "*prelim*" tags?
if ( filter_out_prelim_tags == True ):

    # ifilter out all articles with any tag whose name contains "prelim".
    print( "filtering out articles with tags that contain \"prelim\"" )
    article_qs = article_qs.exclude( tags__name__icontains = "prelim" )
    
#-- END check to see if we filter out "prelim_*" tags --#

# how many is that?
article_count = article_qs.count()

print( "Article count after tag filtering: " + str( article_count ) )

# just want un-cleaned-up:
article_qs = article_qs.filter( Q( cleanup_status = Article.CLEANUP_STATUS_NEW ) | Q( cleanup_status__isnull = True ) )
article_count = article_qs.count()

print( "Article count after filtering on cleanup_status - filter out any that have already been cleaned up: " + str( article_count ) )

# ! ==> ORDER BY - do we want a random sample?
#random_count = 10
if ( random_count > 0 ):

    # to get random, order them by "?", then use slicing to retrieve requested
    #     number.
    article_qs = article_qs.order_by( "?" )[ : random_count ]

else:

    # order by ID (can't re-order once a slice is taken, so can't re-order if
    #     random sample).
    article_qs = article_qs.order_by( "id" )

#-- END check to see if we want random sample --#

# this is a nice algorithm, also:
# - http://www.titov.net/2005/09/21/do-not-use-order-by-rand-or-how-to-get-random-rows-from-table/

# how many is that?
article_count = article_qs.count()
print( "Article count after ORDER-ing: " + str( article_count ) )

# ! ==> LIMIT
# limit_count = 1
if ( limit_count > 0 ):

    article_qs = article_qs[ : limit_count ]
    
#-- END check to see if we limit. --#

# how many is that?
article_count = article_qs.count()
print( "Article count after LIMIT-ing: " + str( article_count ) )

#==============================================================================#
# ! analyze_author_info()
#==============================================================================#

# create instance of DTNB.
tdn = DTNB()

# run analysis.
tdn.analyze_author_info( article_qs )

# output details.
tdn.output_debug_message( "========================================" )
tdn.output_debug_message( "Found " + str( tdn.article_counter ) + " articles ( " + str( tdn.article_count ) + " )." )

# name in 1st paragraph?
tdn.output_debug_message( "\n" )
tdn.output_debug_message( "Found " + str( len( tdn.graf_1_has_name_id_list ) ) + " ( " + str( tdn.graf_1_has_name_count ) + " ) articles WITH name in 1st graf." )
#tdn.output_debug_message( "----> Sections: " + str( sorted( tdn.graf_1_has_name_section_list ) ) )
#tdn.output_debug_message( "----> IDs: " + str( sorted( tdn.graf_1_has_name_id_list ) ) )
tdn.output_debug_message( "" )
tdn.output_debug_message( "Found " + str( len( tdn.graf_1_no_name_id_list ) ) + " articles WITHOUT name in 1st graf." )
tdn.output_debug_message( "----> Sections: " + str( sorted( tdn.graf_1_no_name_section_list ) ) )
tdn.output_debug_message( "----> IDs (sorted): " + str( sorted( tdn.graf_1_no_name_id_list ) ) )
tdn.output_debug_message( "----> IDs: " + str( tdn.graf_1_no_name_id_list ) )
tdn.output_debug_message( "----> graf text: " )
tdn.output_debug_message( "----> NO NAME 1st GRAF anomaly details: " )

# output author name anomaly details.
for anomaly_detail in tdn.graf_1_no_name_detail_list:

    # get anomaly details
    author_anomaly_article_id = anomaly_detail.get( DTNB.AUTHOR_ANOMALY_DETAIL_ARTICLE_ID, -1 )
    author_anomaly_author_string = anomaly_detail.get( DTNB.AUTHOR_ANOMALY_DETAIL_AUTHOR_STRING, "" )
    author_anomaly_graf_1 = anomaly_detail.get( DTNB.AUTHOR_ANOMALY_DETAIL_GRAF_1, "" )
    author_anomaly_graf_2 = anomaly_detail.get( DTNB.AUTHOR_ANOMALY_DETAIL_GRAF_2, "" )
    
    # output them.
    anomaly_detail_string = "--------> article ID: " + str( author_anomaly_article_id )
    anomaly_detail_string += "\n- author_string: " + str( author_anomaly_author_string )
    anomaly_detail_string += "\n- graf 1: " + author_anomaly_graf_1
    anomaly_detail_string += "\n- graf 2: " + author_anomaly_graf_2
    anomaly_detail_string += "\n"
    tdn.output_debug_message( anomaly_detail_string )

#-- END loop over author anomaly details --#

tdn.output_debug_message( "----> got name?: " + str( tdn.graf_1_no_name_yes_author_count ) )

# "by" in 1st paragraph?
tdn.output_debug_message( "\n" )
tdn.output_debug_message( "Found " + str( len( tdn.graf_1_has_by_id_list ) ) + " ( " + str( tdn.graf_1_has_by_count ) + " ) articles WITH \"by\" in 1st graf." )
#tdn.output_debug_message( "----> Sections: " + str( sorted( tdn.graf_1_has_by_section_list ) ) )
#tdn.output_debug_message( "----> IDs: " + str( sorted( tdn.graf_1_has_by_id_list ) ) )
tdn.output_debug_message( "" )
tdn.output_debug_message( "Found " + str( len( tdn.graf_1_no_by_id_list ) ) + " articles WITHOUT \"by\" in 1st graf." )
tdn.output_debug_message( "----> Sections: " + str( sorted( tdn.graf_1_no_by_section_list ) ) )
tdn.output_debug_message( "----> IDs (sorted): " + str( sorted( tdn.graf_1_no_by_id_list ) ) )
tdn.output_debug_message( "----> IDs: " + str( tdn.graf_1_no_by_id_list ) )
tdn.output_debug_message( "----> graf text: " )
tdn.output_debug_message( "----> NO BY 1st GRAF anomaly details: " )

# output author name anomaly details.
for anomaly_detail in tdn.graf_1_no_by_detail_list:

    # get anomaly details
    author_anomaly_article_id = anomaly_detail.get( DTNB.AUTHOR_ANOMALY_DETAIL_ARTICLE_ID, -1 )
    author_anomaly_author_string = anomaly_detail.get( DTNB.AUTHOR_ANOMALY_DETAIL_AUTHOR_STRING, "" )
    author_anomaly_graf_1 = anomaly_detail.get( DTNB.AUTHOR_ANOMALY_DETAIL_GRAF_1, "" )
    author_anomaly_graf_2 = anomaly_detail.get( DTNB.AUTHOR_ANOMALY_DETAIL_GRAF_2, "" )
    
    # output them.
    anomaly_detail_string = "--------> article ID: " + str( author_anomaly_article_id )
    anomaly_detail_string += "\n- author_string: " + str( author_anomaly_author_string )
    anomaly_detail_string += "\n- graf 1: " + author_anomaly_graf_1
    anomaly_detail_string += "\n- graf 2: " + author_anomaly_graf_2
    anomaly_detail_string += "\n"
    tdn.output_debug_message( anomaly_detail_string )

#-- END loop over author anomaly details --#

tdn.output_debug_message( "----> got name?: " + str( tdn.graf_1_no_by_yes_author_count ) )

# "detroit news" in 2nd paragraph?
tdn.output_debug_message( "\n" )
tdn.output_debug_message( "Found " + str( len( tdn.graf_2_has_DN_id_list ) ) + " ( " + str( tdn.graf_2_has_DN_count ) + " ) articles WITH \"detroit news\" in 2nd graf." )
#tdn.output_debug_message( "----> Sections: " + str( sorted( tdn.graf_2_has_DN_section_list ) ) )
#tdn.output_debug_message( "----> IDs: " + str( sorted( tdn.graf_2_has_DN_id_list ) ) )
tdn.output_debug_message( "" )
tdn.output_debug_message( "Found " + str( len( tdn.graf_2_no_DN_id_list ) ) + " articles WITHOUT \"detroit news\" in 2nd graf." )
tdn.output_debug_message( "----> Sections: " + str( sorted( tdn.graf_2_no_DN_section_list ) ) )
tdn.output_debug_message( "----> IDs: " + str( sorted( tdn.graf_2_no_DN_id_list ) ) )
tdn.output_debug_message( "----> graf text: " )
tdn.output_debug_message( "----> NO \"detroit news\" 2nd GRAF anomaly details: " )

# output author name anomaly details.
for anomaly_detail in tdn.graf_2_no_DN_detail_list:

    # get anomaly details
    author_anomaly_article_id = anomaly_detail.get( DTNB.AUTHOR_ANOMALY_DETAIL_ARTICLE_ID, -1 )
    author_anomaly_author_string = anomaly_detail.get( DTNB.AUTHOR_ANOMALY_DETAIL_AUTHOR_STRING, "" )
    author_anomaly_graf_1 = anomaly_detail.get( DTNB.AUTHOR_ANOMALY_DETAIL_GRAF_1, "" )
    author_anomaly_graf_2 = anomaly_detail.get( DTNB.AUTHOR_ANOMALY_DETAIL_GRAF_2, "" )
    
    # output them.
    anomaly_detail_string = "--------> article ID: " + str( author_anomaly_article_id )
    anomaly_detail_string += "\n- author_string: " + str( author_anomaly_author_string )
    anomaly_detail_string += "\n- graf 1: " + author_anomaly_graf_1
    anomaly_detail_string += "\n- graf 2: " + author_anomaly_graf_2
    anomaly_detail_string += "\n"
    tdn.output_debug_message( anomaly_detail_string )

#-- END loop over author anomaly details --#

# all article IDs in set.
#tdn.output_debug_message( "\n" )
#tdn.output_debug_message( "List of " + str( len( tdn.article_id_list ) ) + " filtered article IDs: " + str( sorted( tdn.article_id_list ) ) )

#==============================================================================#
# ! processing - apply tags, capture author info
#==============================================================================#

# loop over articles?
if ( ( do_apply_tag == True ) or ( do_capture_author_info == True ) ):

    # capture author information
    processing_counter = 0
    processing_id_list = []
    processing_section_list = []
    for current_article in article_qs:
    
        # increment counter
        processing_counter += 1
        
        # update auditing information
        processing_id_list.append( current_article.id )
        if ( current_article.section not in processing_section_list ):

            # add hitherto unseen section to list.
            processing_section_list.append( current_article.section )
            
        #-- END check to see if we've already captured this section. --#
        
        print( "\nArticle " + str( processing_counter ) + " of " + str( article_count ) + ": " + str( current_article ) )

        # ! ==> capture_author_info()
        
        # are we capturing author info?
        if ( do_capture_author_info ):
    
            print( "- Attempting to capture author information from body of article.")
    
            # call capture_author_info()
            capture_status = tdn.capture_author_info( current_article )
            capture_status_list = capture_status.get_message_list()
            
            # output status list
            print( "====> " + str( processing_counter ) + " - Article ID: " + str( current_article.id ) + "; capture_status = " + str( capture_status ) )
            
        #-- END check to see if we try to capture author info --#
        
        # ! ==> apply tags
        
        # apply tag(s) while we are at it?
        if ( ( do_apply_tag == True ) and ( tags_to_apply_list is not None ) and ( len( tags_to_apply_list ) > 0 ) ):
        
            print( "- Applying tags " + str( tags_to_apply_list ) + " to article.")

            # yes, please.  Loop over tags list.
            for tag_to_apply in tags_to_apply_list:
            
                # tag the article with each tag in the list.
                current_article.tags.add( tag_to_apply )
                
                print( "====> Applied tag \"" + tag_to_apply + "\"." )
                
            #-- END loop over tag list. --#
            
            print( "- Tags for article " + str( current_article.id ) + " : " + str( current_article.tags.all() ) )
            
        #-- END check to see if we apply tag. --#
        
    #-- END loop over articles to capture author info. --#
    
    print( "\n" )
    print( "Processed " + str( processing_counter ) + " filtered article IDs: " + str( sorted( processing_id_list ) ) + " in the following sections of the paper: " + str( processing_section_list ) )

#-- END check to see if there is work to do. --#
