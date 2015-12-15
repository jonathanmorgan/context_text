# imports
from sourcenet.models import Article
from sourcenet.models import Articles_To_Migrate

# import python_utilities
from python_utilities.logging.summary_helper import SummaryHelper

# declare variables
my_summary_helper = None
summary_string = ""
article_list = None
article_to_process = -1
current_article = None
current_headline = ""
current_pub_date = ""
current_text = ""
is_matched = False
matching_article_list = None
match_count = -1
match_article = None
match_counter = -1

# auditing
single_match_counter = 0
multi_match_counter = 0
no_match_counter = 0
archive_match_counter = 0

# initialize summary helper
my_summary_helper = SummaryHelper()

# get a list of all the articles to migrate that don't have an article ID.
article_list = Articles_To_Migrate.objects.filter( article = None ).order_by( 'id' )

# get number of articles to process
articles_to_process = article_list.count()
print( articles_to_process )

# loop over articles.
for current_article in article_list:

    # look for plain old articles that have same headline.
    current_headline = current_article.headline
    print( "" )
    print( "==> article " + str( current_article.id ) + ": " + str( current_article ) )
    matching_article_list = Article.objects.filter( headline = current_headline )
    
    # filter also on pub date.
    current_pub_date = current_article.pub_date
    matching_article_list = matching_article_list.filter( pub_date = current_pub_date )
    
    # get count.
    match_count = matching_article_list.count()
    print( "    - HEADLINE match_count = " + str( match_count ) )
    
    # if match count = 1, store reference to that article in article to migrate.
    if ( match_count == 1 ):
    
        # increment counter
        single_match_counter += 1
    
        # it is 1.  huzzah.
        match_article = matching_article_list[ 0 ]
        print( "        - Matching article: " + str( match_article ) )
        
        # add article to row and save.
        current_article.article = match_article
        current_article.save()
        is_matched = True
        
    elif ( match_count > 1 ):
    
        # increment counter
        multi_match_counter += 1
        is_matched = False
    
        # if greater than one, list them.
        match_counter = 0
        for match_article in matching_article_list:
        
            match_counter += 1
            
            # print the match.
            print( "        - Matching article #" + str( match_counter ) + " ( edition: " + match_article.edition + " ): " + str( match_article ) )
            
            # see if UID of migrate article matches archive ID of match.
            if ( current_article.unique_identifier == match_article.archive_id ):
            
                # it do!
                print( "!!!! newsbank ID matches!" )
            
            #-- END check to see if alternate ID matches.
        
        #-- END loop over matches --#
    
    else:
    
        # no match.

        # increment counter
        no_match_counter += 1
        is_matched = False
        
    #-- END check to see if match count is 1 --#

    # if not matched, try starting with archive ID.
    if ( is_matched == False ):
    
        # look for articles with archive_id equal to unique_identifier
        matching_article_list = Article.objects.filter( archive_id = current_article.unique_identifier )
        matching_article_list = matching_article_list.filter( pub_date = current_pub_date )
        match_count = matching_article_list.count()
        print( "    - ARCHIVE ID match count: " + str( match_count ) )
    
        # if greater than zero, list them.
        if ( match_count == 1 ):
        
            # one match. Store it.
            # it is 1.  huzzah.
            match_article = matching_article_list[ 0 ]
            print( "        - archive ID match: " + str( match_article ) )
            
            # add article to row and save.
            current_article.article = match_article
            current_article.save()
            archive_match_counter += 1
        
        elif ( match_count > 0 ):
        
            # loop over all of the matches.
            match_counter = 0
            for match_article in matching_article_list:
            
                match_counter += 1
                
                # print the match.
                print( "        - archive ID Match ( edition: " + match_article.edition + " ): " + str( match_article ) )
                        
            #-- END loop over matches --#

        #-- END check to see if one or more id matches. --#

    #-- END check to see if matches based on archive ID. --#

#-- END loop over article list --#

# add info. to summary outputter.
my_summary_helper.set_prop_value( "single_match_counter", single_match_counter )
my_summary_helper.set_prop_desc( "single_match_counter", "Single Match" )

my_summary_helper.set_prop_value( "multi_match_counter", multi_match_counter )
my_summary_helper.set_prop_desc( "multi_match_counter", "Multiple Match" )

my_summary_helper.set_prop_value( "no_match_counter", no_match_counter )
my_summary_helper.set_prop_desc( "no_match_counter", "No Match" )

my_summary_helper.set_prop_value( "archive_match_counter", archive_match_counter )
my_summary_helper.set_prop_desc( "archive_match_counter", "No Match, but archive ID found" )

# set stop time.
my_summary_helper.set_stop_time()

# generate summary string.
summary_string += my_summary_helper.create_summary_string( item_prefix_IN = "==> " )
print( summary_string )