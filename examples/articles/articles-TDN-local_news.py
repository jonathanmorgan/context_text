# imports
from sourcenet.models import Article
from sourcenet.models import Newspaper

# declare variables - The Detroit News
tdn_local_news_sections = []
tdn_newspaper = None
tdn_article_qs = None
article_count = -1
article_counter = -1
current_article = None
author_string = ""
article_text = None
paragraph_list = []
affiliation = ""

# set up "local, regional and state news" sections
tdn_local_news_sections.append( "Lakeshore" )
tdn_local_news_sections.append( "Front Page" )
tdn_local_news_sections.append( "City and Region" )
tdn_local_news_sections.append( "Business" )
tdn_local_news_sections.append( "Religion" )
tdn_local_news_sections.append( "State" )

# Detroit News
# get newspaper instance for TDN.
tdn_newspaper = Newspaper.objects.get( id = 2 )

# populate author_affiliation in Article table for Detroit News.
tdn_article_qs = Article.objects.filter( newspaper = tdn_newspaper )
tdn_article_qs = tdn_article_qs.filter( author_affiliation__isnull = True )
tdn_article_qs = tdn_article_qs.exclude( author_string__contains = ';' )
tdn_article_qs = tdn_article_qs[ : 10 ]

article_count = tdn_article_qs.count()
article_counter = 0
for current_article in tdn_article_qs:

    article_counter = article_counter + 1

    # output article.
    print( "- Article " + str( article_counter ) + " of " + str( article_count ) + ": " + str( current_article ) )

    # get author string
    section = current_article.section
    author_string = current_article.author_string
    author_varchar = current_article.author_varchar
    
    print( "    - section = \"" + section + "\"" )
    print( "    - author = string: \"" + author_string + "\"; varchar: " + author_varchar )

    # get article_text.
    article_text = current_article.article_text_set.get()

    # retrieve list of paragraphs
    paragraph_list = article_text.get_paragraph_list()
    
    # output contents of paragraphs 0, 1, and 2.
    print( "    - graf 1: " + paragraph_list[ 0 ] )
    print( "    - graf 2: " + paragraph_list[ 1 ] )
    print( "    - graf 3: " + paragraph_list[ 2 ] )
    
#-- END loop over articles. --#