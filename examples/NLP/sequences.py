# imports
from context_text.models import Article
from context_text.models import Article_Text

# get article
test_article = Article.objects.filter( id = 90948 ).get()

# get article_text
article_text = test_article.article_text_set.get()

# string to find.
#test_string = "Sales through November are less than 15,000, down 54 percent, according to Autodata Corp. Toyota Motor Corp. showed the A-BAT concept, a small hybrid unibody pickup, at the 2008 Detroit auto show but has no immediate plans to put it into production, said spokesman John McCandless."
#test_string = "Diaz said. A car-based pickup was already in the"
test_string = "The emphasis is going to be on getting a vehicle that is still true to the Ram brand image and also gets excellent miles per gallon rating and at an attractive price point"

print( "==> test string: " + test_string )

# try the find_in_text() method.
result = article_text.find_in_text( test_string )

print( result )

# get values out of result
canonical_index_list = result[ Article_Text.FIT_CANONICAL_INDEX_LIST ]
first_word_number_list = result[ Article_Text.FIT_FIRST_WORD_NUMBER_LIST ]
plain_index_list = result[ Article_Text.FIT_TEXT_INDEX_LIST ]
last_word_number_list = result[ Article_Text.FIT_LAST_WORD_NUMBER_LIST ]
paragraph_number_list = result[ Article_Text.FIT_PARAGRAPH_NUMBER_LIST ]

print( "\n==> first and last word(s) returned:\n" )

# get word list
word_list = article_text.get_word_list()

# what is the word at first_word_number?
word_count = 0
for first_word_number in first_word_number_list:

    word_count = word_count + 1

    print( " - first_word_number = " + str( first_word_number ) + ", word = " + word_list[ first_word_number - 1 ] )

    last_word_number = last_word_number_list[ word_count - 1 ]
    print( " - last_word_number = " + str( last_word_number ) + ", word = " + word_list[ last_word_number - 1 ] )

#-- END loop over first words returned. --#
    
print( "\n==> paragraph(s) returned:\n" )

# get paragraph list
paragraph_list = article_text.get_paragraph_list()

# what is paragraph at paragraph_number?
paragraph_count = 0
for paragraph_number in paragraph_number_list:

    paragraph_count = paragraph_count + 1
    print( " - " + str( paragraph_count ) + " - paragraph_number = " + str( paragraph_number ) + " : " + paragraph_list[ paragraph_number - 1 ] )

#-- END loop over paragraph numbers returned. --#

print( "\n==> plain text index(ices) returned:\n" )

# get text
plain_text = article_text.get_content_sans_html()

# print text from canonical index on, to see if it is indeed the quote.
plain_index_count = 0
for plain_index in plain_index_list:

    plain_index_count = plain_index_count + 1
    print( " - " + str( plain_index_count ) + " - plain_index = " + str( plain_index ) + " : " + plain_text[ plain_index : ] )
    
#-- END loop over canonical indices returned. --#

print( "\n==> canonical text index(ices) returned:\n" )

# get text
canonical_text = article_text.get_content()

# print text from canonical index on, to see if it is indeed the quote.
canonical_index_count = 0
for canonical_index in canonical_index_list:

    canonical_index_count = canonical_index_count + 1
    print( " - " + str( canonical_index_count ) + " - canonical_index = " + str( canonical_index ) + " : " + canonical_text[ canonical_index : ] )
    
#-- END loop over canonical indices returned. --#