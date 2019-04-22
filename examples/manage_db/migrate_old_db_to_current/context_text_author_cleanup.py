# context_text imports
from context_text.models import Article_Author

# import python_utilities
from python_utilities.logging.summary_helper import SummaryHelper

# declare variables
me = "context_text_author_cleanup.py"
my_summary_helper = None
summary_string = ""
article_author_rs = None
author_counter = 0
current_article_author = None
current_article_data = None
current_article = None
current_author_string = ""
author_parts = None
author_parts_length = -1

# auditing
org_string_counter = 0
article_source_counter = 0
bad_author_string_counter = 0

# initialize summary helper
my_summary_helper = SummaryHelper()

# retrieve all article author rows where organization_string is empty.
article_author_rs = Article_Author.objects.filter( organization_string__isnull = True )

# loop
for current_article_author in article_author_rs:

    author_counter += 1

    # get article data
    current_article_data = current_article_author.article_data
    
    # get article
    current_article = current_article_data.article
    
    # get author string
    current_author_string = current_article.author_varchar
    
    # for now, just print it.
    print ( "- author #" + str( author_counter ) + ": " + current_author_string )

    # got one?
    if ( ( current_author_string ) and ( current_author_string != "" ) ):
    
        # got an author string.  Parse it.  First, break out organization.
        # split author string on "/"
        author_parts = current_author_string.split( '/' )
        
        # got two parts?
        author_parts_length = len( author_parts )
        if ( author_parts_length == 2 ):
        
            org_string_counter += 1
            
            # we do.  2nd part = organization
            author_organization = author_parts[ 1 ]
            author_organization = author_organization.strip()
            
        elif ( author_parts_length == 1 ):
        
            article_source_counter += 1
            
            # just author.  Use the source string from the article.
            author_organization = current_article.source_string.strip()
        
        elif ( ( author_parts_length == 0 ) or ( author_parts_length > 2 ) ):
        
            # error.  what to do?
            bad_author_string_counter += 1
            status_OUT = "ERROR - in " + me + ": splitting on '/' resulted in either an empty array or more than two things.  This isn't right ( " + current_author_string + " )."
            
        #-- END check results of splitting on "/" --#
        
        # Got something?
        if ( ( author_organization ) and ( author_organization != "" ) ):
            
            # save it.
            print( "    - org. string: " + author_organization )
            current_article_author.organization_string = author_organization
            current_article_author.save()
            
        #-- END check to see if there is an organization. --#
        
    #-- END check to see if we have an author string --#

#-- END loop over authros with no organization_string --#

# set stop time.
my_summary_helper.set_stop_time()

# add info. to summary outputter.
my_summary_helper.set_prop_value( "org_string_counter", org_string_counter )
my_summary_helper.set_prop_desc( "org_string_counter", "Found org. string" )

my_summary_helper.set_prop_value( "article_source_counter", article_source_counter )
my_summary_helper.set_prop_desc( "article_source_counter", "Using Article Source" )

my_summary_helper.set_prop_value( "bad_author_string_counter", bad_author_string_counter )
my_summary_helper.set_prop_desc( "bad_author_string_counter", "Bad Author String" )

# generate summary string.
summary_string += my_summary_helper.create_summary_string( item_prefix_IN = "==> " )
print( summary_string )