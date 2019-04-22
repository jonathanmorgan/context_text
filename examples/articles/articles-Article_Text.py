# context_text imports
from context_text.collectors.newsbank.newsbank_helper import NewsBankHelper
from context_text.models import Article
from context_text.models import Article_RawData
from context_text.models import Article_Text

# beautiful soup 4
from bs4 import BeautifulSoup
from bs4 import NavigableString

# beautiful soup helper
from python_utilities.beautiful_soup.beautiful_soup_helper import BeautifulSoupHelper

# import bleach for HTML cleaning
# import bleach

# import classes for HTML cleaning
from python_utilities.strings.html_helper import HTMLHelper
from python_utilities.strings.string_helper import StringHelper

# declare variables
test_raw = None
bs = None
bs_div_docBody = None
bs_temp_tag = None
my_newsbank_helper = None
cleaned_article_body = ""
test_article_text = None
original_text = ""
new_text = ""
plain_text = ""
paragraph_list = []
current_paragraph = ""
paragraph_counter = -1
word_list = []
current_word = ""
word_counter = -1

# initialize BS helper
bs_helper = BeautifulSoupHelper()

# get article raw data with ID of 2
test_raw = Article_RawData.objects.get( id = 2 )

# load raw content into a BeautifulSoup instance
bs = BeautifulSoup( test_raw.content )

# retrieve main content <div> for a NewsBank HTML article.
bs_div_docBody = bs.find( "div", NewsBankHelper.HTML_CLASS_DOC_BODY )

# get nested <div> that contains article content.
bs_temp_tag = bs_div_docBody.find( "div", NewsBankHelper.HTML_CLASS_MAIN_TEXT )

# print the original HTML
print( "Original HTML:" )
print( str( bs_temp_tag ) )

# clean it up with NewsBankHelper
my_newsbank_helper = NewsBankHelper()
cleaned_article_body = my_newsbank_helper.clean_article_body( bs_temp_tag )

# output
print( "\n\n\nCleaned article body:" )
print( cleaned_article_body )

# retrieve Article_Text for this article.
test_article_text = Article_Text.objects.get( id = 2 )

# retrieve and print the original
original_text = test_article_text.get_content()
print( "\n\n\nOriginal content:" )
print( original_text )

# set text
test_article_text.set_text( cleaned_article_body )

# retrieve and print
new_text = test_article_text.get_content()
print( "\n\n\nNew content:" )
print( new_text )

# retrieve text without HTML and print.
plain_text = test_article_text.get_content_sans_html()
print( "\n\n\nContent sans HTML:" )
print( plain_text )

# retrieve paragraph list and print.
paragraph_list = test_article_text.get_paragraph_list()
print( "\n\n\nparagraph list:" )

paragraph_counter = 0
for current_paragraph in paragraph_list:

    paragraph_counter += 1
    print( str( paragraph_counter ) + " - " + current_paragraph )
    
#-- END loop over paragraph list. --#

# retrieve word list and print.
word_list = test_article_text.get_word_list()
print( "\n\n\nword list:" )

word_counter = 0
for current_word in word_list:

    word_counter += 1
    print( str( word_counter ) + " - " + current_word )
    
#-- END loop over paragraph list. --#
