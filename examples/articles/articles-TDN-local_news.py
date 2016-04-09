# imports - python_utilities
from python_utilities.logging.logging_helper import LoggingHelper

# imports
from sourcenet.collectors.newsbank.newspapers.DTNB import DTNB
from sourcenet.models import Article
from sourcenet.models import Article_Text
from sourcenet.models import Newspaper

# declare variables
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
tags_in_list = []
tags_not_in_list = []
filter_out_prelim_tags = False
random_count = -1
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
tags_to_apply_list = [ "minnesota1-20160409", "minnesota2-20160409", "minnesota3-20160409" ]

# set up "local, regional and state news" sections
#local_news_sections.append( "Lakeshore" )
#local_news_sections.append( "Front Page" )
#local_news_sections.append( "City and Region" )
#local_news_sections.append( "Business" )
#local_news_sections.append( "Religion" )
#local_news_sections.append( "State" )
#local_news_sections.append( "Special" )
#local_news_sections = DTNB.NEWS_SECTION_NAME_LIST

# start with all articles
article_qs = Article.objects.all()

# The Detroit News
# get newspaper instance for TDN.
selected_newspaper = Newspaper.objects.get( id = 2 )

# and, with an in-house author
#article_qs = article_qs.filter( Article.Q_GRP_IN_HOUSE_AUTHOR )

# and no columns
#article_qs = article_qs.exclude( index_terms__icontains = "Column" )

# date range, newspaper, section list, and custom Q().
start_date = ""
end_date = ""
#section_name_in_list = None
#custom_article_q = None

# month of in house local news from GRP from 2009-12-01 to 2009-12-31
#start_date = "2009-12-01"
#end_date = "2009-12-31"
section_name_in_list = DTNB.NEWS_SECTION_NAME_LIST
custom_article_q = DTNB.Q_IN_HOUSE_AUTHOR

article_qs = Article.filter_articles( qs_IN = article_qs,
                                      start_date = start_date,
                                      end_date = end_date,
                                      newspaper = selected_newspaper,
                                      section_name_list = section_name_in_list,
                                      custom_article_q = custom_article_q )

# how many is that?
article_count = article_qs.count()

print( "Article count before filtering on tags: " + str( article_count ) )

# ! ==> tags

# tags to exclude
#tags_not_in_list = [ "prelim_reliability", "prelim_network" ]
if ( len( tags_not_in_list ) > 0 ):

    # exclude those in a list
    print( "filtering out articles with tags: " + str( tags_not_in_list ) )
    article_qs = article_qs.exclude( tags__name__in = tags_not_in_list )

#-- END check to see if we have a specific list of tags we want to exclude --#

# include only those with certain tags.
#tags_in_list = [ "prelim_reliability", "prelim_network" ]
tags_in_list = [ "prelim_reliability", ]
if ( len( tags_in_list ) > 0 ):

    # filter
    print( "filtering to just articles with tags: " + str( tags_in_list ) )
    article_qs = article_qs.filter( tags__name__in = tags_in_list )
    
#-- END check to see if we have a specific list of tags we want to include --#

# filter out "*prelim*" tags?
#filter_out_prelim_tags = True
if ( filter_out_prelim_tags == True ):

    # ifilter out all articles with any tag whose name contains "prelim".
    print( "filtering out articles with tags that contain \"prelim\"" )
    article_qs = article_qs.exclude( tags__name__icontains = "prelim" )
    
#-- END check to see if we filter out "prelim_*" tags --#

# how many is that?
article_count = article_qs.count()

print( "Article count after tag filtering: " + str( article_count ) )

# just want un-cleaned-up:
#article_qs = article_qs.filter( cleanup_status = Article.CLEANUP_STATUS_NEW )
#article_count = article_qs.count()

#print( "Article count after filtering for cleanup_status: " + str( article_count ) )


# do we want a random sample?
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

# ! LIMIT
#article_qs = article_qs[ : 10 ]

# how many is that?
article_count = article_qs.count()
print( "Article count after ordering: " + str( article_count ) )

# create instance of DTNB.
tdn = DTNB()

# run analysis.
tdn.analyze_author_info( article_qs )

# output details.
print( "========================================" )
print( "Found " + str( tdn.article_counter ) + " articles ( " + str( tdn.article_count ) + " )." )

# name in 1st paragraph?
print( "\n" )
print( "Found " + str( len( tdn.graf_1_has_name_id_list ) ) + " ( " + str( tdn.graf_1_has_name_count ) + " ) articles WITH name in 1st graf." )
print( "----> Sections: " + str( sorted( tdn.graf_1_has_name_section_list ) ) )
print( "----> IDs: " + str( sorted( tdn.graf_1_has_name_id_list ) ) )
print( "" )
print( "Found " + str( len( tdn.graf_1_no_name_id_list ) ) + " articles WITHOUT name in 1st graf." )
print( "----> Sections: " + str( sorted( tdn.graf_1_no_name_section_list ) ) )
print( "----> IDs (sorted): " + str( sorted( tdn.graf_1_no_name_id_list ) ) )
print( "----> IDs: " + str( tdn.graf_1_no_name_id_list ) )
print( "----> graf text: "  + str( tdn.graf_1_no_name_text_list ) )
print( "----> got name?: " + str( tdn.graf_1_no_name_yes_author_count ) )

# "by" in 1st paragraph?
print( "\n" )
print( "Found " + str( len( tdn.graf_1_has_by_id_list ) ) + " ( " + str( tdn.graf_1_has_by_count ) + " ) articles WITH \"by\" in 1st graf." )
print( "----> Sections: " + str( sorted( tdn.graf_1_has_by_section_list ) ) )
print( "----> IDs: " + str( sorted( tdn.graf_1_has_by_id_list ) ) )
print( "" )
print( "Found " + str( len( tdn.graf_1_no_by_id_list ) ) + " articles WITHOUT \"by\" in 1st graf." )
print( "----> Sections: " + str( sorted( tdn.graf_1_no_by_section_list ) ) )
print( "----> IDs (sorted): " + str( sorted( tdn.graf_1_no_by_id_list ) ) )
print( "----> IDs: " + str( tdn.graf_1_no_by_id_list ) )
print( "----> graf text: "  + str( tdn.graf_1_no_by_text_list ) )
print( "----> got name?: " + str( tdn.graf_1_no_by_yes_author_count ) )

# "detroit news" in 2nd paragraph?
print( "\n" )
print( "Found " + str( len( tdn.graf_2_has_DN_id_list ) ) + " ( " + str( tdn.graf_2_has_DN_count ) + " ) articles WITH \"detroit news\" in 2nd graf." )
print( "----> Sections: " + str( sorted( tdn.graf_2_has_DN_section_list ) ) )
print( "----> IDs: " + str( sorted( tdn.graf_2_has_DN_id_list ) ) )
print( "" )
print( "Found " + str( len( tdn.graf_2_no_DN_id_list ) ) + " articles WITHOUT \"detroit news\" in 2nd graf." )
print( "----> Sections: " + str( sorted( tdn.graf_2_no_DN_section_list ) ) )
print( "----> IDs: " + str( sorted( tdn.graf_2_no_DN_id_list ) ) )

# all article IDs in set.
print( "\n" )
print( "List of " + str( len( tdn.article_id_list ) ) + " filtered article IDs: " + str( sorted( tdn.article_id_list ) ) )

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

        # are we capturing author info?
        if ( do_capture_author_info ):
    
            print( "- Attempting to capture author information from body of article.")
    
            # call capture_author_info()
            capture_status_list = tdn.capture_author_info( current_article )
            
            # output status list
            print( "====> " + str( processing_counter ) + " - Article ID: " + str( current_article.id ) + "; capture_status_list = " + str( capture_status_list ) )
            
        #-- END check to see if we try to capture author info --#
        
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
