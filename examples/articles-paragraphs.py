# sourcenet imports
from sourcenet.collectors.newsbank.newsbank_helper import NewsBankHelper
from sourcenet.models import Article
from sourcenet.models import Article_RawData

# beautiful soup 4
from bs4 import BeautifulSoup
from bs4 import NavigableString

# beautiful soup helper
from python_utilities.beautiful_soup.beautiful_soup_helper import BeautifulSoupHelper

# import bleach for HTML cleaning
import bleach

# declare variables
test_raw = None
bs = None
bs_div_docBody = None
bs_temp_tag = None
paragraph_list = []
current_element_list = []
current_name = ""
paragraph_counter = -1
paragraph_text = ""
current_paragraph_text = ""
bs_helper = None
graf_counter = -1
graf_count = -1
article_string = ""

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

# loop over the contents of this div.
paragraph_counter = 1
for current_content in bs_temp_tag.contents:

    # output name
    current_name = current_content.name
    print( current_name )
    
    # see if name is br.
    if ( current_name == "br" ):
    
        # yes - paragraph break!  output a message, and the string contents of the tag (just in case).
        print( "=======> paragraph break! - End of paragraph " + str( paragraph_counter ) + ".  HTML element Contents: \"" + str( current_content ) + "\"" )
        
        # add previous paragraph to paragraph list.
        paragraph_text_list = []
        for paragraph_element in current_element_list:
        
            # convert current element to just text.  Is it NavigableString?
            if ( isinstance( paragraph_element, NavigableString) ):
            
                # it is text - convert it to string.
                current_paragraph_text = unicode( paragraph_element )
            
            else:
            
                # not text - just grab all the text out of it.
                #current_paragraph_text = ' '.join( paragraph_element.findAll( text = True ) )
                current_paragraph_text = paragraph_element.get_text( " ", strip = True )
                
            #-- END check to see if current element is text. --#

            # clean up - convert HTML entities
            current_paragraph_text = bs_helper.convert_html_entities( current_paragraph_text )
            
            # strip out extra white space
            current_paragraph_text = ' '.join( current_paragraph_text.split() )
            
            # got any paragraph text?
            current_paragraph_text = current_paragraph_text.strip()
            if ( ( current_paragraph_text != None ) and ( current_paragraph_text != "" ) ):
            
                # yes.  Add to paragraph text.
                paragraph_text_list.append( current_paragraph_text )
                
            #-- END check to see if any text. --#
        
        #-- END loop over paragraph elements. --#
        
        # convert paragraph list to string
        paragraph_text = ' '.join( paragraph_text_list )
        
        # got any text in this paragraph?
        if ( ( paragraph_text != None ) and ( paragraph_text != "" ) ):

            # yes - Add paragraph text to paragraph_list
            paragraph_list.append( paragraph_text )
                    
            # increment paragraph counter
            paragraph_counter += 1
            
        #-- END check to see if paragraph text. --#

        # output paragraph text.
        print( "=======> paragraph text: " + paragraph_text )
        
        # reset current_element_list
        current_element_list = []
    
    else: 
    
        # no. Add current element to list
        current_element_list.append( current_content )
    
    #-- END check to see if <br> --#

#-- END loop over contents. --#

print( "\n\n\n~~~~~~~~~~ After paragraph loop:\n\n\n" )

# how many paragraphs?
graf_count = len( paragraph_list )
if ( graf_count > 0 ):

    # Got at least one. loop over paragraphs
    graf_counter = 0
    article_string = ""
    for graf in paragraph_list:
    
        # increment counter, output paragraph.
        graf_counter += 1
        
        # print our paragraphs in paragraph list.
        print( "- graf " + str( graf_counter ) + ": \"" + graf + "\"" )
        
        # put the paragraph in <p> tags.
        current_paragraph_text = "<p id=\"" + str( graf_counter ) + "\">" + graf + "</p>"
        
        # add to article text.
        article_string += current_paragraph_text
    
    #-- END loop over paragraphs. --#
    
#-- END check to see if anything in paragraph list --#

print( article_string )

# bleach test
allowed_tags = [ 'p', ]
allowed_attrs = {
    'p' : [ 'id', ],
}
article_string = bleach.clean( article_string, allowed_tags, allowed_attrs, strip = True )

print( "\n\nCleaned:\n\n" + article_string + "\n\n")

# variables for playing with the result
bs_grafs = None
bs_p_list = None
current_graf_number = ""
current_graf_text = ""

# use beautiful soup to retrieve all <p> tags.
bs_grafs = BeautifulSoup( article_string )
bs_p_list = bs_grafs.find_all( "p" )

for bs_current_graf in bs_p_list:

    # get paragraph number and text
    current_graf_number = bs_current_graf[ "id" ]
    current_graf_text = bs_current_graf.get_text( " ", strip = True )
    
    # output paragraph.
    print( "- #" + current_graf_number + " : \"" + current_graf_text + "\"" )

#-- END loop over paragraphs --#