# imports
from context_text.models import Article

# declare variables
test_article_id = -1
test_prefix = ""
test_value = ""
test_suffix = ""
test_string = ""
test_article = None
test_article_text = None
test_find_ctext = []
test_find_graf = []
canonical_text = ""
ctext_index = -1
paragraph_list = []
graf_index = -1

# declare variables for plain text matching.
plain_text = ""
test_find_plain_text_list = []
full_text_index = -1
prefix_length = -1

'''
#------------------------------------------------------------------------------#
# article 65897 - test string that spans paragraphs
#------------------------------------------------------------------------------#

test_article_id = 65897
#test_string = "home, Randy Smith said. \"It's unfortunate,\" Randy Smith said. \"He lived to hunt, and that's what brought us all"
#test_string = "Randy Smith said. \"It's unfortunate,\" Randy Smith said. \"He lived to hunt, and that's what brought us all"
#test_string = "Smith said. \"It's unfortunate,\" Randy Smith said. \"He lived to hunt, and that's what brought us all"
test_string = "said. \"It's unfortunate,\" Randy Smith said. \"He lived to hunt, and that's what brought us all"
'''

#------------------------------------------------------------------------------#
# article 4831 - test string at end of article.
#------------------------------------------------------------------------------#

test_article_id = 4831
#test_string = "home, Randy Smith said. \"It's unfortunate,\" Randy Smith said. \"He lived to hunt, and that's what brought us all"
#test_string = "Randy Smith said. \"It's unfortunate,\" Randy Smith said. \"He lived to hunt, and that's what brought us all"
#test_string = "Smith said. \"It's unfortunate,\" Randy Smith said. \"He lived to hunt, and that's what brought us all"
test_prefix = 'jets that could come in extra special to us," '
test_value = "she"
test_suffix = " said."
test_string = test_prefix + test_value + test_suffix

print( "Test String: " + test_string )

# get article and Article_Text that contains this string.
test_article = Article.objects.filter( id = test_article_id ).get()
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

#==============================================================================#
# Plain text testing.
#==============================================================================#

plain_text = test_article_text.get_content_sans_html()

# Look for full search string.
test_find_plain_text_list = test_article_text.find_in_plain_text( test_string )

print( "--> plain text match list: " + str( test_find_plain_text_list ) )

for plain_text_index in test_find_plain_text_list:

    print( "- plain text match: " + str( plain_text_index ) + " -- " + plain_text[ plain_text_index : ] )
    full_text_index = plain_text_index
    
#-- END loop over full string matches --#

# Look for just value plus suffix
test_string = test_value + test_suffix
test_find_plain_text_list = test_article_text.find_in_plain_text( test_string )

print( "--> plain text match list: " + str( test_find_graf ) )

for plain_text_index in test_find_plain_text_list:

    calculated_index = full_text_index + len( test_prefix )
    print( "- plain text match: " + str( plain_text_index ) + "; calulated index = " + str( calculated_index ) + " -- " + plain_text[ plain_text_index : ] )
    
#-- END loop over value+suffix matches --#