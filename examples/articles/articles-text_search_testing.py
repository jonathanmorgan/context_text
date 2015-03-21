# imports
from sourcenet.models import Article

# declare variables
test_string = ""
test_article = None
test_article_text = None
test_find_ctext = []
test_find_graf = []
canonical_text = ""
ctext_index = -1
paragraph_list = []
graf_index = -1

# test string that spans paragraphs
#test_string = "home, Randy Smith said. \"It's unfortunate,\" Randy Smith said. \"He lived to hunt, and that's what brought us all"
#test_string = "Randy Smith said. \"It's unfortunate,\" Randy Smith said. \"He lived to hunt, and that's what brought us all"
#test_string = "Smith said. \"It's unfortunate,\" Randy Smith said. \"He lived to hunt, and that's what brought us all"
test_string = "said. \"It's unfortunate,\" Randy Smith said. \"He lived to hunt, and that's what brought us all"

print( "Test String: " + test_string )

# get article and Article_Text that contains this string.
test_article = Article.objects.filter( id = 65897 ).get()
test_article_text = test_article.article_text_set.get()

# test on canonical text.
test_find_ctext = test_article_text.find_in_canonical_text( test_string )

# test on paragraph list.
test_find_graf = test_article_text.find_in_paragraph_list( test_string )

# output results
print( "--> canonical text match list: " + str( test_find_ctext ) )

# output at that character in ctext
canonical_text = test_article_text.get_content()
for ctext_index in test_find_ctext:

    print( "- index: " + str( ctext_index ) + " -- " + canonical_text[ ctext_index : ] )
    
#-- END loop over match indices --#

print( "--> paragraph match list: " + str( test_find_graf ) )

# output the matching paragraph.
paragraph_list = test_article_text.get_paragraph_list()
for graf_index in test_find_graf:

    print( "- graf #: " + str( graf_index ) + " -- " + paragraph_list[ graf_index - 1 ] )
    
#-- END loop over matching paragraphs --#