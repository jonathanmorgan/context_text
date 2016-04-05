# imports
from sourcenet.models import Article
from sourcenet.models import Newspaper

# declare variables
selected_newspaper = None
article_qs = None
article_count = -1
article_counter = -1

# declare variables - filtering
local_news_sections = []
affiliation = ""
article_id_list = []
tags_in_list = []
tags_not_in_list = []
filter_out_prelim_tags = False
random_count = -1
article_counter = -1

# declare variables - article processing
current_article = None
current_article_id = -1
section_string = ""
author_string = ""
article_text = None
find_string = ""
author_FIT_values = None
paragraph_list = None
graf_1 = ""
graf_1_lower = ""
graf_1_has_name_count = 0
graf_1_has_name_id_list = []
graf_1_has_name_section_list = []
graf_1_no_name_id_list = []
graf_1_no_name_section_list = []
graf_1_no_name_text_list = []
graf_1_no_name_yes_author_count = 0
graf_1_has_by_count = 0
graf_1_has_by_id_list = []
graf_1_has_by_section_list = []
graf_1_no_by_id_list = []
graf_1_no_by_section_list = []
graf_1_no_by_text_list = []
graf_1_no_by_yes_author_count = 0
graf_2 = ""
graf_2_lower = ""
graf_2_has_DN_count = 0
graf_2_has_DN_id_list = []
graf_2_has_DN_section_list = []
graf_2_no_DN_id_list = []
graf_2_no_DN_section_list = []

# declare variables - size of random sample we want
#random_count = 60

# declare variables - also, apply tag?
do_apply_tag = False
tag_to_apply = "minnesota3-20160328"

# set up "local, regional and state news" sections
#local_news_sections.append( "Lakeshore" )
#local_news_sections.append( "Front Page" )
#local_news_sections.append( "City and Region" )
#local_news_sections.append( "Business" )
#local_news_sections.append( "Religion" )
#local_news_sections.append( "State" )
#local_news_sections.append( "Special" )
#local_news_sections = Article.GRP_NEWS_SECTION_NAME_LIST

# start with all articles
article_qs = Article.objects.all()

# The Detroit News
# get newspaper instance for TDN.
selected_newspaper = Newspaper.objects.get( id = 2 )

# and, with an in-house author
#article_qs = article_qs.filter( Article.Q_GRP_IN_HOUSE_AUTHOR )

# and no columns
#article_qs = article_qs.exclude( index_terms__icontains = "Column" )

# date range, newspaper, section list, and in-house reporters.
article_qs = Article.filter_articles( qs_IN = article_qs,
                                      start_date = "2009-12-01",
                                      end_date = "2009-12-31",
                                      newspaper = selected_newspaper )

'''
                                      ,
                                      section_name_list = local_news_sections,
                                      custom_article_q = Article.Q_GRP_IN_HOUSE_AUTHOR )

'''

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

# do we want a random sample?
random_count = 147
if ( random_count > 0 ):

    # to get random, order them by "?", then use slicing to retrieve requested
    #     number.
    article_qs = article_qs.order_by( "?" )[ : random_count ]
    
#-- END check to see if we want random sample --#

# this is a nice algorithm, also:
# - http://www.titov.net/2005/09/21/do-not-use-order-by-rand-or-how-to-get-random-rows-from-table/

# ! LIMIT
#article_qs = article_qs[ : 10 ]

# ! loop over articles
article_count = article_qs.count()
article_counter = 0
article_id_list = []

# init graf 1 author summary info
graf_1_has_name_count = 0
graf_1_has_name_id_list = []
graf_1_has_name_section_list = []
graf_1_no_name_id_list = []
graf_1_no_name_section_list = []
graf_1_no_name_text_list = []
graf_1_no_name_yes_author_count = 0

# init graf 1 by summary info
graf_1_has_by_count = 0
graf_1_has_by_id_list = []
graf_1_has_by_section_list = []
graf_1_no_by_id_list = []
graf_1_no_by_section_list = []
graf_1_no_by_text_list = []
graf_1_no_by_yes_author_count = 0

# init graf 2 summary info
graf_2_has_DN_count = 0
graf_2_has_DN_id_list = []
graf_2_has_DN_section_list = []
graf_2_no_DN_id_list = []
graf_2_no_DN_section_list = []

# LOOP
for current_article in article_qs:

    article_counter = article_counter + 1

    # output article.
    print( "- Article " + str( article_counter ) + " of " + str( article_count ) + ": " + str( current_article ) )
    
    # store off article data
    current_article_id = current_article.id
    author_string = current_article.author_string
    section_string = current_article.section
    
    # look for it in article - FIT...?

    # get article text for article.
    article_text = current_article.article_text_set.get()
    
    # then, call find_in_text (FIT) method on mention plus suffix (to
    #    make sure we get the right "he", for example).
    find_string = author_string

    # find in text!
    author_FIT_values = article_text.find_in_text( find_string )
    
    print( "====> Looking for " + find_string + ": " + str( author_FIT_values ) )

    # get paragraph list
    paragraph_list = article_text.get_paragraph_list()
    
    # get and output paragraphs 1 and 2:
    graf_1 = paragraph_list[ 0 ]
    graf_1_lower = graf_1.lower()
    graf_2 = paragraph_list[ 1 ]
    graf_2_lower = graf_2.lower()
    
    print( "====> Paragraph 1: " + graf_1 )
    
    # Does graf_1 contain author's name
    if ( author_string.lower() in graf_1_lower ):
    
        # yes it does.  Increment counter
        graf_1_has_name_count += 1

        # store article ID
        graf_1_has_name_id_list.append( current_article_id )

        # add section to list.
        if ( section_string not in graf_1_has_name_section_list ):
        
            # not there yet - add it.
            graf_1_has_name_section_list.append( section_string )
        
        #-- END check to see if section already in list. --#
        
        print( "========> Paragraph 1 contains name \"" + str( author_string ) + "\"!" )

    else:
    
        # no name in graf 1 - store article ID
        graf_1_no_name_id_list.append( current_article_id )

        # add section to list.
        if ( section_string not in graf_1_no_name_section_list ):
        
            # not there yet - add it.
            graf_1_no_name_section_list.append( section_string )
        
        #-- END check to see if section already in list. --#
        
        # add the paragraph text to list
        if ( graf_1 not in graf_1_no_name_text_list ):
        
            # not there yet - add it.
            graf_1_no_name_text_list.append( author_string + " | " + graf_1 )
            
        #-- END check to avoid duplication in paragraph text list --#
        
    #-- END check to see if contains author name. --#

    # Does graf_1 contain the word "by"
    if ( "by" in graf_1_lower ):
    
        # yes it does.  Increment counter
        graf_1_has_by_count += 1

        # store article ID
        graf_1_has_by_id_list.append( current_article_id )

        # add section to list.
        if ( section_string not in graf_1_has_by_section_list ):
        
            # not there yet - add it.
            graf_1_has_by_section_list.append( section_string )
        
        #-- END check to see if section already in list. --#
        
        print( "========> Paragraph 1 contains \"by\"!" )

    else:
    
        # no "by" in graf 1 - store article ID
        graf_1_no_by_id_list.append( current_article_id )

        # add section to list.
        if ( section_string not in graf_1_no_by_section_list ):
        
            # not there yet - add it.
            graf_1_no_by_section_list.append( section_string )
        
        #-- END check to see if section already in list. --#
        
        # add the paragraph text to list
        if ( graf_1 not in graf_1_no_by_text_list ):
        
            # not there yet - add it.
            graf_1_no_by_text_list.append( graf_1 )
            
        #-- END check to avoid duplication in paragraph text list --#
        
        # Even though no "by", is name here?
        if ( author_string.lower() in graf_1_lower ):
        
            # yup.  Make a note.
            graf_1_no_by_yes_author_count += 1
            
        #-- END check to see if name is there even though "by" is not --#
        
    #-- END check to see if contains "by".

    print( "====> Paragraph 2: " + graf_2 )
    
    # Does graf_2 contain the words "Detroit News"
    if ( "detroit news" in graf_2_lower ):
    
        # yes it does.  Increment counter
        graf_2_has_DN_count += 1
        
        # store article ID
        graf_2_has_DN_id_list.append( current_article_id )

        # add section to list.
        if ( section_string not in graf_2_has_DN_section_list ):
        
            # not there yet - add it.
            graf_2_has_DN_section_list.append( section_string )
        
        #-- END check to see if section already in list. --#
        
        print( "========> Paragraph 2 contains \"detroit news\"!" )

    else:
    
        # no "by" in graf 1 - store article ID
        graf_2_no_DN_id_list.append( current_article_id )

        # add section to list.
        if ( section_string not in graf_2_no_DN_section_list ):
        
            # not there yet - add it.
            graf_2_no_DN_section_list.append( section_string )
        
        #-- END check to see if section already in list. --#
        
    #-- END check to see if contains "detroit news".
    
    # add IDs to article_id_list
    article_id_list.append( str( current_article.id ) )
    
    # apply a tag while we are at it?
    if ( ( do_apply_tag == True ) and ( tag_to_apply is not None ) and ( tag_to_apply != "" ) ):
    
        # yes, please.  Add tag.
        current_article.tags.add( tag_to_apply )
        
    #-- END check to see if we apply tag. --#

    # output the tags.
    print( "====> Tags for article " + str( current_article.id ) + " : " + str( current_article.tags.all() ) )
   
#-- END loop over articles. --#

# output details.
print( "========================================" )
print( "Found " + str( article_counter ) + " articles ( " + str( article_count ) + " )." )

# name in 1st paragraph?
print( "\n" )
print( "Found " + str( len( graf_1_has_name_id_list ) ) + " ( " + str( graf_1_has_name_count ) + " ) articles WITH name in 1st graf." )
print( "----> Sections: "  + str( graf_1_has_name_section_list ) )
print( "----> IDs: "  + str( graf_1_has_name_id_list ) )
print( "" )
print( "Found " + str( len( graf_1_no_name_id_list ) ) + " articles WITHOUT name in 1st graf." )
print( "----> Sections: "  + str( graf_1_no_name_section_list ) )
print( "----> IDs: "  + str( graf_1_no_name_id_list ) )
print( "----> graf text: "  + str( graf_1_no_name_text_list ) )
print( "----> got name?: " + str( graf_1_no_name_yes_author_count ) )

# "by" in 1st paragraph?
print( "\n" )
print( "Found " + str( len( graf_1_has_by_id_list ) ) + " ( " + str( graf_1_has_by_count ) + " ) articles WITH \"by\" in 1st graf." )
print( "----> Sections: "  + str( graf_1_has_by_section_list ) )
print( "----> IDs: "  + str( graf_1_has_by_id_list ) )
print( "" )
print( "Found " + str( len( graf_1_no_by_id_list ) ) + " articles WITHOUT \"by\" in 1st graf." )
print( "----> Sections: "  + str( graf_1_no_by_section_list ) )
print( "----> IDs: "  + str( graf_1_no_by_id_list ) )
print( "----> graf text: "  + str( graf_1_no_by_text_list ) )
print( "----> got name?: " + str( graf_1_no_by_yes_author_count ) )

# "detroit news" in 2nd paragraph?
print( "\n" )
print( "Found " + str( len( graf_2_has_DN_id_list ) ) + " ( " + str( graf_2_has_DN_count ) + " ) articles WITH \"detroit news\" in 1st graf." )
print( "----> Sections: "  + str( graf_2_has_DN_section_list ) )
print( "----> IDs: "  + str( graf_2_has_DN_id_list ) )
print( "" )
print( "Found " + str( len( graf_2_no_DN_id_list ) ) + " articles WITHOUT \"by\" in 1st graf." )
print( "----> Sections: "  + str( graf_2_no_DN_section_list ) )
print( "----> IDs: "  + str( graf_2_no_DN_id_list ) )

# all article IDs in set.
print( "\n" )
print( "List of " + str( len( article_id_list ) ) + " filtered article IDs: " + ", ".join( article_id_list ) )
