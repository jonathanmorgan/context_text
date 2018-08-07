//----------------------------------------------------------------------------//
// !==> SOURCENET namespace!
//----------------------------------------------------------------------------//


var SOURCENET = SOURCENET || {};


//----------------------------------------------------------------------------//
// !==> FindInText class
//----------------------------------------------------------------------------//


// requires:
// - param-container.js


//------------------------------------//
// !----> FindInText constructor
//------------------------------------//


/**
 * Represents one of the pieces of information about an entity stored in an
 *     object.
 * @constructor
 */
SOURCENET.FindInText = function()
{
    
    // Class variables

    // Find in Article Text - Dynamic CSS class names
    SOURCENET.FindInText.CSS_CLASS_FOUND_IN_TEXT = "foundInText";
    SOURCENET.FindInText.CSS_CLASS_FOUND_IN_TEXT_MATCHED_WORDS = "foundInTextMatchedWords";
    SOURCENET.FindInText.CSS_CLASS_FOUND_IN_TEXT_RED = "foundInTextRed";
    SOURCENET.FindInText.CSS_CLASS_FOUND_IN_TEXT_MATCHED_WORDS_RED = "foundInTextMatchedWordsRed";
    
    // defaults:
    SOURCENET.FindInText.CSS_CLASS_DEFAULT_P_MATCH = SOURCENET.CSS_CLASS_FOUND_IN_TEXT_RED;
    SOURCENET.FindInText.CSS_CLASS_DEFAULT_WORD_MATCH = SOURCENET.CSS_CLASS_FOUND_IN_TEXT_MATCHED_WORDS_RED;
    
    // Find in Article Text - HTML element IDs
    SOURCENET.FindInText.INPUT_ID_TEXT_TO_FIND_IN_ARTICLE = "text-to-find-in-article";
    
    // Find in Article Text - HTML for matched word highlighting
    SOURCENET.FindInText.HTML_SPAN_TO_CLASS = "<span class=\""
    SOURCENET.FindInText.HTML_SPAN_AFTER_CLASS = "\">";
    SOURCENET.FindInText.HTML_SPAN_CLOSE = "</span>";

    // instance variables.
    
    // jquery DOM element that contains text we want to search and highlight.
    this.element_to_search = null;
    
    // current configuration for highlighting matches
    this.css_class_matched_paragraph = SOURCENET.FindInText.CSS_CLASS_DEFAULT_P_MATCH;
    this.css_class_matched_words = SOURCENET.FindInText.CSS_CLASS_DEFAULT_WORD_MATCH;
    
    // clear whenever we search again?
    this.clear_on_new_search = true;
    
    // ignore <p> tags?
    this.ignore_p_tags = false
    
    // lists of CSS classes used in the current instance.

    // list of known found in text <p> classes
    this.css_class_list_found_in_text = [];
    this.css_class_list_found_in_text.push( SOURCENET.FindInText.CSS_CLASS_DEFAULT_P_MATCH );
    
    // list of known found in text word classes
    this.css_class_list_found_in_text_words = [];
    this.css_class_list_found_in_text_words.push( SOURCENET.FindInText.CSS_CLASS_DEFAULT_WORD_MATCH  );
    
} //-- END SOURCENET.FindInText constructor --//

//--------------------------------//
// !----> FindInText methods
//--------------------------------//


/**
 * Retrieves all the <p> tags that make up the article text, removes class
 *     "foundInText" from any where that class is present.
 *
 * Preconditions: None.
 *
 * Postconditions: Updates classes on article <p> tags so none are assigned
 *     "foundInText".
 */
SOURCENET.FindInText.prototype.clear_all_find_in_text_matches = function()
{
    
    // declare variables
    var me = "SOURCENET.FindInText.prototype.clear_all_find_in_text_matches";

    // call the clear method with the master lists.
    this.clear_find_in_text_matches( this.css_class_list_found_in_text, this.css_class_list_found_in_text_words );

} //-- END function SOURCENET.clear_find_in_text_matches() --//


/**
 * Retrieves all the <p> tags that make up the article text, removes class
 *     "foundInText" from any where that class is present.
 *
 * Preconditions: None.
 *
 * Postconditions: Updates classes on article <p> tags so none are assigned
 *     "foundInText".
 */
SOURCENET.FindInText.prototype.clear_find_in_text_matches = function( p_class_list_IN, word_class_list_IN )
{
    
    // declare variables
    var me = "SOURCENET.FindInText.prototype.clear_find_in_text_matches";
    var article_paragraphs = null;
    var list_length = -1;
    var list_index = -1;
    var current_css_class = null;
    
    // get article <p> tags.
    article_paragraphs = this.get_paragraphs();

    // remove each class in p class list passed in.
    list_length = this.p_class_list_IN.length;
    for ( list_index = 0; list_index < list_length; list_index++ )
    {

        // get class from list.
        current_css_class = this.css_class_list_found_in_text[ list_index ];
        
        // toggle class
        article_paragraphs.toggleClass( current_css_class, false );

    } //-- end loop over CSS classes --//
        
    // set all paragraphs' html() back to their text()...
    article_paragraphs.each( function()
        {
            // declare variables.
            var jquery_p_element = null;
            var paragraph_html = "";
            var paragraph_text = "";
            var word_class_list_length = -1;
            var word_class_list_index = -1;
            var current_word_css_class = null;
            var span_index = -1;
            var found_highlight = false;
            
            // get paragraph text
            jquery_p_element = $( this );
            paragraph_html = jquery_p_element.html();
            paragraph_text = jquery_p_element.text();
            
            // is there a matched words CSS class present in html?
            word_class_list_length = this.word_class_list_IN.length;
            for ( word_class_list_index = 0; word_class_list_index < word_class_list_length; word_class_list_index++ )
            {
        
                // get class from list.
                current_word_css_class = this.word_class_list_IN[ list_index ];
                
                // look for class in paragraph.
                span_index = paragraph_html.indexOf( current_word_css_class );
                
                // if found, set flag to true.
                if ( span_index > -1 )
                {
                    
                    // found one.  Need to clear HTML.
                    found_highlight = true;
                    
                } //-- end check to see if highlighting found. --//
        
            } //-- end loop over CSS classes --//
                    
            // if found, update store plain text in place of HTML.
            if ( found_highlight == true )
            {
                
                // store plain text in <p>.html() to remove any HTML.
                jquery_p_element.html( paragraph_text );
                                    
            } //-- END check to see if <span> found --//
        } //-- END anonymous function called on each paragraph --//
    );

} //-- END function SOURCENET.clear_find_in_text_matches() --//


/**
 * Accepts string to search inside and string to look for inside.  Looks for
 *     find_text_IN, inside the string_IN.  If it finds it, wraps the matched
 *     text in a span so it stands out.
 *
 * Preconditions: Must have found text you want to process.  Must also have
 *     exact text you are sesarching for.
 *
 * Postconditions: if match found, will wrap the matched text in a span so it
 *     stands out.
 */
SOURCENET.FindInText.prototype.find_text_in_string = function( string_IN,
                                                               find_text_IN )
{

    // return reference
    var string_OUT = null;

    // declare variables.
    var me = "SOURCENET.FindInText.prototype.find_text_in_string";
    var search_in_text = null;
    var work_text = "";
    var current_find_text = "";
    var found_index = -1;
    var text_around_match_list = null;
    var match_html = "";
    var current_text_index = -1;
    var new_html = "";
    
    // declare variables - initialize from instance variables
    var ignore_p_tags = false;
    var clear_on_new_search = false;
    var match_word_css_class = null;
    
    // initialize
    work_text = string_IN;
    match_word_css_class = this.get_css_class_matched_words();

    SOURCENET.log_message( "In " + me + "(): find text \"" + find_text_IN + "\"; element text = " + work_text );
    
    // get current find item.
    current_find_text = find_text_IN;
    
    // look for text.
    found_index = work_text.indexOf( current_find_text );
    
    // got at least 1 match?
    if ( found_index >= 0 )
    {

        // found a match - split on the text we matched.
        text_around_match_list = work_text.split( current_find_text );
        
        // add a span around the matched words.
        matched_words_html = SOURCENET.HTML_SPAN_TO_CLASS;
        matched_words_html += match_word_css_class;
        matched_words_html += SOURCENET.HTML_SPAN_AFTER_CLASS;
        matched_words_html += current_find_text;
        matched_words_html += SOURCENET.HTML_SPAN_CLOSE;
        
        // put together again, but with <span>-ed matched word rather than just
        //    the words themselves.
        work_text = text_around_match_list.join( matched_words_html );

    } //-- END check to see if match --//
    
    // return work_text
    string_OUT = work_text;
    
    return string_OUT;

} //-- END function SOURCENET.find_text_in_string --//


/**
 * Accepts string to search inside and list of strings to look for inside.
 *     for each item in the list, checks to see if the string is in the text.
 *     If it finds it, wraps the matched text in a span so it stands out.
 *
 * Preconditions: Must have found text you want to process.  Must also have
 *     broken out list of search text items as you want (split on spaces, or
 *     don't, etc.).
 *
 * Postconditions: if match found, will wrap the matched text in a span so it
 *     stands out.
 */
SOURCENET.FindInText.prototype.find_text_list_in_string = function( string_IN,
                                                                    find_text_list_IN )
{

    // return reference
    var string_OUT = null;

    // declare variables.
    var me = "SOURCENET.FindInText.prototype.find_text_list_in_string";
    var search_in_text = null;
    var work_text = "";
    var find_text_item_count = -1;
    var current_index = -1;
    var current_find_text = "";
    
    // declare variables - initialize from instance variables
    var match_word_css_class = null;
    
    // initialize
    string_OUT = string_IN;
    match_word_css_class = this.get_css_class_matched_words();

    SOURCENET.log_message( "In " + me + "(): find text list = " + find_text_list_IN + "; element text = " + work_text );
    
    // get count of items in list.
    find_text_item_count = find_text_list_IN.length;
    
    // loop over items.
    for ( current_index = 0; current_index < find_text_item_count; current_index++ )
    {
        
        // get current find item.
        current_find_text = find_text_list_IN[ current_index ];
        
        // look for text.
        work_text = this.find_text_in_string( work_text, current_find_text );

    } //-- END loop over find text items --//
    
    // return work_text
    string_OUT = work_text;
    
    return string_OUT;

} //-- END function SOURCENET.find_text_list_in_string --//


/**
 * Accepts jquery <p> element instance and list of strings to look for inside.
 *     for each item in the list, checks to see if the string is in the text.
 *     If it finds it, updates classes on <p> tag to assign "foundInText",
 *     and wraps the matched text in a span so it stands out.
 *
 * Preconditions: Must have found paragraph tag you want to process and have it
 *     in a jquery instance.  Must also have broken out list of search text
 *     items as you want (split on spaces, or don't, etc.).
 *
 * Postconditions: if match found, will update the <p> in the jquery instance
 *     passed in.
 */
SOURCENET.FindInText.prototype.find_text_list_in_element_html = function( jquery_element_IN,
                                                                          find_text_list_IN )
{

    // return reference
    var found_match_OUT = false;

    // declare variables.
    var me = "SOURCENET.FindInText.prototype.find_text_list_in_element_html";
    var jquery_element = null;
    var element_html = "";
    var updated_html = "";
    
    // declare variables - initialize from instance variables
    var match_word_css_class = null;
    
    // initialize
    match_word_css_class = this.get_css_class_matched_words();

    // get element text and html
    jquery_element = jquery_element_IN;
    element_html = jquery_element.html();
    
    SOURCENET.log_message( "In " + me + "(): find text list = " + find_text_list_IN + "; element HTML = " + element_html );
    
    // call this.find_text_list_in_string().
    updated_html = find_text_list_in_string( element_html, find_text_list_IN );
    
    // any matches?
    if ( updated_html != element_html )
    {
        
        // html string was changed - found at least one match.
        found_match_OUT = true;
        
        // update HTML in element.
        jquery_element.html( updated_html );
        
    }
    else
    {
        
        // no change, nothing found.
        found_match_OUT = false;
        
    } //-- END check to see if text found --//
    
    return found_match_OUT;

} //-- END function SOURCENET.find_text_list_in_element_html --//


/**
 * Accepts jquery <p> element instance and list of strings to look for inside.
 *     for each item in the list, checks to see if the string is in the text.
 *     If it finds it, updates classes on <p> tag to assign "foundInText",
 *     and wraps the matched text in a span so it stands out.
 *
 * Preconditions: Must have found paragraph tag you want to process and have it
 *     in a jquery instance.  Must also have broken out list of search text
 *     items as you want (split on spaces, or don't, etc.).
 *
 * Postconditions: if match found, will update the <p> in the jquery instance
 *     passed in.
 */
SOURCENET.FindInText.prototype.find_text_list_in_element_text = function( jquery_element_IN,
                                                                          find_text_list_IN )
{

    // return reference
    var found_match_OUT = false;

    // declare variables.
    var me = "SOURCENET.FindInText.prototype.find_text_list_in_element_html";
    var jquery_element = null;
    var element_text = "";
    var updated_text = "";
    
    // declare variables - initialize from instance variables
    var match_word_css_class = null;
    
    // initialize
    match_word_css_class = this.get_css_class_matched_words();

    // get element text and html
    jquery_element = jquery_element_IN;
    element_text = jquery_element.text();
    
    SOURCENET.log_message( "In " + me + "(): find text list = " + find_text_list_IN + "; element text = " + element_text );
    
    // call this.find_text_list_in_string().
    updated_text = find_text_list_in_string( element_text, find_text_list_IN );
    
    // any matches?
    if ( updated_text != element_text )
    {
        
        // html string was changed - found at least one match.
        found_match_OUT = true;
        
        // update HTML in element.
        jquery_element.text( updated_text );
        
    }
    else
    {
        
        // no change, nothing found.
        found_match_OUT = false;
        
    } //-- END check to see if text found --//
    
    return found_match_OUT;

} //-- END function SOURCENET.find_text_list_in_element_text --//


/**
 * Accepts jquery <p> element instance and list of strings to look for inside.
 *     for each item in the list, checks to see if the string is in the text.
 *     If it finds it, updates classes on <p> tag to assign "foundInText",
 *     and wraps the matched text in a span so it stands out.
 *
 * Preconditions: Must have found paragraph tag you want to process and have it
 *     in a jquery instance.  Must also have broken out list of search text
 *     items as you want (split on spaces, or don't, etc.).
 *
 * Postconditions: if match found, will update the <p> in the jquery instance
 *     passed in.
 */
SOURCENET.FindInText.prototype.find_text_in_p_tag = function( p_tag_jquery_IN,
                                                              find_text_list_IN,
                                                              fail_over_to_text_IN )
{
    
    // return reference
    var found_match_OUT = false;

    // declare variables.
    var me = "SOURCENET.find_in_p_tag";
    var jquery_p_element = null;
    var match_p_css_class = null;
    var fail_over_to_text = false;
    
    // initialize
    match_p_css_class = this.get_css_class_matched_paragraph();
    fail_over_to_text = fail_over_to_text_IN;
    if ( fail_over_to_text === undefined )
    {
        
        // defaults to true, the old way.
        fail_over_to_text = true;
        
    }

    // look for text in HTML element
    jquery_p_element = p_tag_jquery_IN;
    found_match_OUT = this.find_text_list_in_element_html( jquery_p_element, find_text_list_IN );
    
    // did we find match?
    if ( ( found_match_OUT == false ) && ( fail_over_to_text == true ) )
    {

        // Fail over to text.
        found_match_OUT = this.find_text_list_in_element_text( jquery_p_element, find_text_list_IN );

    } //-- END check if no match and fail over to text. --//

    // did we find match?
    if ( found_match_OUT == true )
    {

        // For matches, add class passed in.
        jquery_p_element.toggleClass( match_p_css_class, true );

    } //-- END check if found match? --//
    
    return found_match_OUT;

} //-- END function SOURCENET.find_in_p_tag --//


/**
 * Retrieves all the <p> tags that make up the article text, returns them in a
 *     list.  If none found, returns empty list.  If error, returns null.
 *
 * Preconditions: None.
 *
 * Postconditions: None.
 */
SOURCENET.FindInText.prototype.get_paragraphs = function( jquery_element_IN )
{
    
    // return reference
    var grafs_OUT = null;
    
    // declare variables
    var me = "SOURCENET.FindInText.prototype.get_paragraphs";
    var jquery_element = null;
    
    // retrieve HTML element we are searching in.
    jquery_element = jquery_element_IN;
    
    // find all <p> tags.
    grafs_OUT = jquery_element.find( "p" );

    return grafs_OUT;
    
} //-- END method get_paragraphs() --//


SOURCENET.FindInText.prototype.get_css_class_matched_paragraph = function()
{

    // return reference
    var value_OUT = null;
    
    // declare variables
    
    // get value stored in instance.
    value_OUT = this.css_class_matched_paragraph;
    
    // see if undefined.
    if ( value_OUT === undefined )
    {
        
        // undefined - set to default, then return default.
        this.set_css_class_matched_paragraph( SOURCENET.FindInText.CSS_CLASS_DEFAULT_P_MATCH );
        
        // recursive call to get the default.
        value_OUT = this.get_css_class_matched_paragraph();

    } //-- END check to see if undefined --//
    
    return value_OUT;
    
} //-- END method get_css_class_matched_paragraph() --//


SOURCENET.FindInText.prototype.get_css_class_matched_words = function()
{

    // return reference
    var value_OUT = null;
    
    // declare variables
    
    // get value stored in instance.
    value_OUT = this.css_class_matched_words;
    
    // see if undefined.
    if ( value_OUT === undefined )
    {
        
        // undefined - set to default, then return default.
        this.set_css_class_matched_words( SOURCENET.FindInText.CSS_CLASS_DEFAULT_WORD_MATCH );
        
        // recursive call to get the new value, to make sure it was set.
        value_OUT = this.get_css_class_matched_words();

    } //-- END check to see if undefined --//
    
    return value_OUT;
    
} //-- END method get_css_class_matched_words() --//


SOURCENET.FindInText.prototype.get_element_to_search = function()
{

    // return reference
    var value_OUT = null;
    
    // declare variables
    
    // get value stored in instance.
    value_OUT = this.element_to_search;
    
    return value_OUT;
    
} //-- END method get_element_to_search() --//


SOURCENET.FindInText.prototype.set_css_class_matched_paragraph = function( value_IN )
{

    // return reference
    var value_OUT = null;
    
    // declare variables
    var index_in_class_list = -1;
    
    // is it undefined?
    if ( value_IN !== undefined )
    {
        
        // no - store the value.
        this.css_class_matched_paragraph = value_IN;
           
    } //-- END check to see if undefined --//
    
    // check to see if already in this.css_class_list_found_in_text
    index_in_class_list = this.css_class_list_found_in_text.indexOf( value_IN );
    if ( index_in_class_list == -1 )
    {
        
        // not there.  Add it.
        this.css_class_list_found_in_text.push( value_IN );
        
    }
    
    // return the value in the instance variable.
    value_OUT = this.get_css_class_matched_paragraph();

} //-- END method set_css_class_matched_paragraph() --//


SOURCENET.FindInText.prototype.set_css_class_matched_words = function( value_IN )
{

    // return reference
    var value_OUT = null;
    
    // declare variables
    var index_in_class_list = -1;
    
    // is it undefined?
    if ( value_IN !== undefined )
    {
        
        // no - store the value.
        this.css_class_matched_words = value_IN;
           
    } //-- END check to see if undefined --//
    
    // check to see if already in this.css_class_list_found_in_text_words
    index_in_class_list = this.css_class_list_found_in_text_words.indexOf( value_IN );
    if ( index_in_class_list == -1 )
    {
        
        // not there.  Add it.
        this.css_class_list_found_in_text_words.push( value_IN );
        
    }
    
    // return the value in the instance variable.
    value_OUT = this.get_css_class_matched_words();

} //-- END method set_css_class_matched_words() --//

SOURCENET.FindInText.prototype.set_element_to_search = function( value_IN )
{

    // return reference
    var value_OUT = null;
    
    // declare variables
    
    // is it undefined?
    if ( value_IN !== undefined )
    {
        
        // no - store the value.
        this.element_to_search = value_IN;
           
    } //-- END check to see if undefined --//
    
    // return the value in the instance variable.
    value_OUT = this.get_element_to_search();

} //-- END method set_element_to_search() --//


// create instance
SOURCENET.text_finder = new SOURCENET.FindInText()