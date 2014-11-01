# sourcenet imports
from sourcenet.collectors.newsbank.newsbank_helper import NewsBankHelper
from sourcenet.models import Article
from sourcenet.models import Article_RawData

# python utilities
from python_utilities.beautiful_soup.beautiful_soup_helper import BeautifulSoupHelper
from python_utilities.django_utils.django_memory_helper import DjangoMemoryHelper
from python_utilities.django_utils.queryset_helper import QuerySetHelper
from python_utilities.logging.summary_helper import SummaryHelper

# beautiful soup 4
from bs4 import BeautifulSoup

# declare variables
DEBUG_FLAG = False
my_summary_helper = None
summary_string = ""
articles_to_process_qs = None
article_count = -1
article_qs = None
article_counter = -1
article_raw_data_count = -1
article_raw_data = None
article_raw_content = ""
article_text_count = -1
article_text = None
no_raw_data_list = []
multiple_raw_data_list = []
no_text_list = []
multiple_text_list = []
done_counter = -1

# memory management
mem_counter = -1
mem_counter_limit = 1000

# variables - text processing
bs = None
bs_div_docBody = None
bs_div_mainText = None
my_newsbank_helper = None
cleaned_article_body = ""
original_text = ""

# initialize summary helper
my_summary_helper = SummaryHelper()

# First, get all Articles that have archive_source = "NewsBank"
articles_to_process_qs = Article.objects.filter( archive_source = "NewsBank" )

# get article count.
article_count = articles_to_process_qs.count()

# loop over the articles.  First, use QuerySetHelper to get an iterator over the
#    records that won't load them all into memory at once.
#article_qs = articles_to_process_qs
article_qs = QuerySetHelper.queryset_generator( articles_to_process_qs )

# set up loop variables.
article_counter = 0
mem_counter = 0
no_raw_data_list = []
multiple_raw_data_list = []
no_text_list = []
multiple_text_list = []
done_counter = 0

# loop over the articles
for article in article_qs:

    # increment counters
    article_counter += 1
    mem_counter += 1
    
    # output article summary
    print ( "- Article " + str( article_counter ) + " of " + str( article_count ) + ": " + str( article ) )
    
    # see how many rawdata records the article has (should only ever be 1).
    article_raw_data_count = article.article_rawdata_set.count()
    
    # got one?
    if ( article_raw_data_count == 1 ):

        # get the raw data for the article.
        article_raw_data = article.article_rawdata_set.get()
        
    elif ( article_raw_data_count > 1 ):
    
        # multiple raw data records.
        multiple_raw_data_list.append( article.id )
        article_raw_data = None
    
    else:
    
        # no raw data records (or negative?).
        no_raw_data_list.append( article.id )
        article_raw_data = None
    
    #-- END check to see how many rawdata records --#

    # got raw data?
    if ( article_raw_data != None ):
    
        # see how many text records the article has (should only ever be 1).
        article_text_count = article.article_text_set.count()
        
        # got text?
        if ( article_text_count == 1 ):
    
            # get the text for the article.
            article_text = article.article_text_set.get()
            
        elif ( article_text_count > 1 ):
        
            # multiple text records.
            multiple_text_list.append( article.id )
            article_text = None
        
        else:
        
            # no text records (or negative?).
            no_text_list.append( article.id )
            article_text = None
        
        #-- END check to see how many rawdata records --#

        # got Article_Text?
        if ( article_text != None ):
            
            # already done?
            if ( article_text.status != "done" ):

                # no.  Re-process raw HTML to derive new, better text.
    
                # load raw content into a BeautifulSoup instance
                article_raw_content = article_raw_data.content
                bs = BeautifulSoup( article_raw_content )
                
                # retrieve main content <div> for a NewsBank HTML article.
                bs_div_docBody = bs.find( "div", NewsBankHelper.HTML_CLASS_DOC_BODY )
                
                # Got a <div id="docBody"> tag?
                if ( bs_div_docBody != None ):
                
                    # get nested <div> that contains article content.
                    bs_div_mainText = bs_div_docBody.find( "div", NewsBankHelper.HTML_CLASS_MAIN_TEXT )
                    
                    # print the original HTML
                    if ( DEBUG_FLAG == True ):
                        print( "Original HTML:" )
                        print( str( bs_div_mainText ) )
                    #-- END DEBUG --#
                                
                    # clean it up with NewsBankHelper
                    my_newsbank_helper = NewsBankHelper()
                    cleaned_article_body = my_newsbank_helper.clean_article_body( bs_div_mainText )
                    
                    # print the original HTML
                    if ( DEBUG_FLAG == True ):
                        # output
                        print( "\n\n\nCleaned article body:" )
                        print( cleaned_article_body )
        
                        # retrieve and print the original
                        original_text = article_text.get_content()
                        print( "\n\n\nOriginal content:" )
                        print( original_text )
                        
                        # same?
                        if ( cleaned_article_body == original_text ):
                            print( "====> SAME!" )
                        else:
                            print( "====> DIFFERENT!" )
                        #-- END check to see if same? --#
                    #-- END DEBUG --#
                    
                    # set text
                    article_text.set_text( cleaned_article_body )
                    
                    # set status
                    article_text.status = "done"
                    
                    # save
                    article_text.save()
                    
                else:
                
                    # No document body - moving on.
                    print( "====> NO <div id=\"docBody\">" )
                
                #-- END check to see if <div id="docBody"> --#
                
            else:
            
                # Already done.
                print( "====> ALREADY DONE" )
                done_counter += 1
            
            #-- END check to see if article already done. --#
            
        else:
            
            # output error message
            print( "====> NO TEXT" )
            
        #-- END check to see if article text --#
        
    else:
        
        # output error message
        print( "====> NO RAW DATA" )
        
    #-- END check to see if raw data --#
    
    # time to garbage collect?
    if ( mem_counter == mem_counter_limit ):
    	
    	# manage memory
    	DjangoMemoryHelper.free_memory()
    	
    	# reset mem_counter
    	mem_counter = 0
    	
    #-- END check to see if we manage memory now --#
    
#-- END loop over articles --#

# End of loop book-keeping.
# set stop time.
my_summary_helper.set_stop_time()

# add info. to summary outputter.
my_summary_helper.set_prop_value( "article_count", article_counter )
my_summary_helper.set_prop_desc( "article_count", "Article count" )

my_summary_helper.set_prop_value( "done_counter", done_counter )
my_summary_helper.set_prop_desc( "done_counter", "Article DONE count" )

my_summary_helper.set_prop_value( "no_text_list", ", ".join( map( str, no_text_list ) ) )
my_summary_helper.set_prop_desc( "no_text_list", "Articles with no text" )

my_summary_helper.set_prop_value( "multiple_text_list", ", ".join( map( str, multiple_text_list ) ) )
my_summary_helper.set_prop_desc( "multiple_text_list", "Articles with multiple text" )

my_summary_helper.set_prop_value( "no_raw_data_list", ", ".join( map( str, no_raw_data_list ) ) )
my_summary_helper.set_prop_desc( "no_raw_data_list", "Articles with no raw data" )

my_summary_helper.set_prop_value( "multiple_raw_data_list", ", ".join( map( str, multiple_raw_data_list ) ) )
my_summary_helper.set_prop_desc( "multiple_raw_data_list", "Articles with multiple raw data" )

# generate summary string.
summary_string += my_summary_helper.create_summary_string( item_prefix_IN = "==> " )
print( summary_string )