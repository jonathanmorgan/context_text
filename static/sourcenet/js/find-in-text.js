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
    
    // ! -----> Class variables

    // Find in Article Text - Dynamic CSS class names
    SOURCENET.FindInText.CSS_CLASS_FOUND_IN_TEXT = "foundInText";
    SOURCENET.FindInText.CSS_CLASS_FOUND_IN_TEXT_MATCHED_WORDS = "foundInTextMatchedWords";
    SOURCENET.FindInText.CSS_CLASS_FOUND_IN_TEXT_RED = "foundInTextRed";
    SOURCENET.FindInText.CSS_CLASS_FOUND_IN_TEXT_MATCHED_WORDS_RED = "foundInTextMatchedWordsRed";
    SOURCENET.FindInText.CSS_CLASS_FOUND_IN_TEXT_GREEN = "foundInTextGreen";
    SOURCENET.FindInText.CSS_CLASS_FOUND_IN_TEXT_MATCHED_WORDS_GREEN = "foundInTextMatchedWordsGreen";
    
    // defaults:
    SOURCENET.FindInText.CSS_CLASS_DEFAULT_P_MATCH = SOURCENET.FindInText.CSS_CLASS_FOUND_IN_TEXT;
    SOURCENET.FindInText.CSS_CLASS_DEFAULT_WORD_MATCH = SOURCENET.FindInText.CSS_CLASS_FOUND_IN_TEXT_MATCHED_WORDS;
    
    // Find in Article Text - HTML element IDs
    SOURCENET.FindInText.INPUT_ID_TEXT_TO_FIND_IN_ARTICLE = "text-to-find-in-article";
    
    // Find in Article Text - HTML for matched word highlighting
    SOURCENET.FindInText.HTML_SPAN_TO_CLASS = "<span class=\""
    SOURCENET.FindInText.HTML_SPAN_AFTER_CLASS = "\">";
    SOURCENET.FindInText.HTML_SPAN_CLOSE = "</span>";
    
    // words to ignore
    SOURCENET.FindInText.text_to_ignore_list = [];
    // SOURCENET.FindInText.text_to_ignore_list.push( "the" );
    // SOURCENET.FindInText.text_to_ignore_list.push( "The" );
    
    // regexp compress internal white space
    SOURCENET.regex_compress_internal_white_space = /\s+/g
    
    // regexp escape regex.
    
    // bobince - https://stackoverflow.com/questions/3561493/is-there-a-regexp-escape-function-in-javascript/3561711#3561711
    //SOURCENET.FindInText.regex_escape_regex = /[-\/\^$*+?.()|[]{}]/g

    // Bynens - https://stackoverflow.com/questions/3115150/how-to-escape-regular-expression-special-characters-using-javascript#9310752
    //SOURCENET.FindInText.regex_escape_regex = /[-[\]{}()*+?.,\\^$|#\s]/g

    // https://simonwillison.net/2006/Jan/20/escape/
    SOURCENET.FindInText.regex_specials = [
      '/', '.', '*', '+', '?', '|',
      '(', ')', '[', ']', '{', '}', '\\'
    ];
    SOURCENET.FindInText.regex_escape_regex_string = '(\\' + SOURCENET.FindInText.regex_specials.join('|\\') + ')';
    SOURCENET.FindInText.regex_escape_regex = new RegExp(
      SOURCENET.FindInText.regex_escape_regex_string,
      'g'
    );
    
    // element cleanup list
    SOURCENET.FindInText.cleanup_in_these_elements = [];
    SOURCENET.FindInText.cleanup_in_these_elements.push( "p" );
    SOURCENET.FindInText.cleanup_in_these_elements.push( "h3" );    
    SOURCENET.FindInText.cleanup_in_these_elements.push( "li" );

    // ! ------> instance variables.
    
    // jquery DOM element that contains text we want to search and highlight.
    this.element_to_search = null;
    
    // current configuration for highlighting matches
    this.css_class_matched_paragraph = SOURCENET.FindInText.CSS_CLASS_DEFAULT_P_MATCH;
    this.css_class_matched_words = SOURCENET.FindInText.CSS_CLASS_DEFAULT_WORD_MATCH;
    
    // clear whenever we search again?
    this.clear_on_new_search = true;
    
    // ignore enclosing element?
    this.ignore_wrapper_element = false;
    
    // case-sensitive?
    this.be_case_sensitive = false;
    
    // lists of CSS classes used in the current instance.
    this.default_find_location = "text"

    // list of known found in text <p> classes
    this.css_class_list_found_in_text = [];
    this.css_class_list_found_in_text.push( SOURCENET.FindInText.CSS_CLASS_DEFAULT_P_MATCH );
    
    // list of known found in text word classes
    this.css_class_list_found_in_text_words = [];
    this.css_class_list_found_in_text_words.push( SOURCENET.FindInText.CSS_CLASS_DEFAULT_WORD_MATCH  );
    
    // match_text variables - count of changes from last call to match_text.
    this.match_text_match_count = -1;
    this.match_text_level = 0;
    
    // find_text_in_string variables - index of first match from last call to find_text_in_string.
    this.find_text_in_string_index = -1;
    
} //-- END SOURCENET.FindInText constructor --//

//----------------------------------//
// !----> FindInText static methods
//----------------------------------//


/**
 * Accepts list of strings to ignore, after checking to make sure it is a list
 *     with at least one thing in it, concats it with the existing
 *     text_to_ignore_list.
 *
 * Preconditions: None.
 *
 * Postconditions: Updates SOURCENET.FindInText.text_to_ignore_list.
 */
SOURCENET.FindInText.add_to_ignore_list = function( ignore_list_IN )
{
    
    // declare variables
    var me = "SOURCENET.FindInText.add_to_ignore_list";
    
    // got anything?
    if ( ( ignore_list_IN !== undefined ) && ( ignore_list_IN != null ) && ( ignore_list_IN.length > 0 ) )
    {
        
        // yes.  concat the list passed in to the actual list.
        SOURCENET.FindInText.text_to_ignore_list = SOURCENET.FindInText.text_to_ignore_list.concat( ignore_list_IN )
    }

} //-- END function SOURCENET.add_to_ignore_list() --//


/**
 * Empties SOURCENET.FindInText.text_to_ignore_list.
 *
 * Preconditions: None.
 *
 * Postconditions: Empties SOURCENET.FindInText.text_to_ignore_list.
 */
SOURCENET.FindInText.clear_ignore_list = function()
{
    
    // declare variables
    var me = "SOURCENET.FindInText.add_to_ignore_list";
    
    // yes.  concat the list passed in to the actual list.
    SOURCENET.FindInText.text_to_ignore_list = []

} //-- END function SOURCENET.clear_ignore_list() --//


/**
 * Retrieves all the <p> tags that make up the article text, removes class
 *     "foundInText" from any where that class is present.
 *
 * Preconditions: None.
 *
 * Postconditions: Updates classes on article <p> tags so none are assigned
 *     "foundInText".
 */
SOURCENET.FindInText.clear_word_matches_in_element = function( element_IN, word_class_list_IN )
{

    // declare variables.
    var me = "SOURCENET.FindInText.clear_word_matches_in_element";
    var local_debug_flag = false;
    var jquery_p_element = null;
    var paragraph_html = "";
    var paragraph_text = "";
    var word_class_list_length = -1;
    var word_class_list_index = -1;
    var current_word_css_class = null;
    var span_index = -1;
    var found_highlight = false;
    var span_list = null;
    var dom_element = null;
    
    // get element text
    jquery_element = $( element_IN );
    paragraph_html = jquery_element.html();
    paragraph_text = jquery_element.text();
    output_html = paragraph_html;
    
    // is there a matched words CSS class present in html?
    word_class_list_length = word_class_list_IN.length;
    for ( word_class_list_index = 0; word_class_list_index < word_class_list_length; word_class_list_index++ )
    {

        // get class from list.
        current_word_css_class = word_class_list_IN[ word_class_list_index ];
        
        // look for class in paragraph.
        span_index = paragraph_html.indexOf( current_word_css_class );
        
        // if found, retrieve all spans, replace them with their text contents,
        //     then set found_highlight to true.
        if ( span_index > -1 )
        {
            
            // retrieve all spans with class = current_word_css_class
            span_jquery_list = jquery_element.find( "span[class='" + current_word_css_class + "']" )
            
            // for each, get HTML and text, split the output_html on HTML
            //     string, then join with just the text.
            span_jquery_list.each( 
                function()
                {
                    // declare variables.
                    jquery_span_element = null;
                    var span_html = "";
                    var span_text = "";
                   
                    // get html and text.
                    jquery_span_element = $( this );
                    span_html = jquery_span_element.html();
                    span_text = jquery_span_element.text();
                    
                    // replace span with text.
                    jquery_span_element.replaceWith( span_text );

                    //SOURCENET.log_message( "**** In " + me + "(): span_html = \"" + span_html + "\"; span_text = \"" + span_text + "\"" );
                } //-- END anonymous function called on each span --//
            )
            found_highlight = true;
            
        } //-- end check to see if highlighting found. --//
        
        // highlighting found?
        if ( found_highlight == true )
        {
            // yes - compact adjacent text nodes together.
            dom_element = jquery_element.get( 0 );
            dom_element.normalize();
        }

    } //-- end loop over CSS classes --//
    
} //-- END method clear_word_matches_in_element() --//


/**
 * Accepts string, uses regular expression to compress runs of internal white
 *     space to a single space, returns the result.
 */
SOURCENET.FindInText.compress_internal_white_space = function( string_IN ) 
{
    // return reference
    var string_OUT = null;
    
    // replace more than one contiguous internal white space
    //     character with a single space.
    string_OUT = string_IN.replace( SOURCENET.regex_compress_white_space, ' ' );
    
    return string_OUT;

} //-- end function SOURCENET.compress_internal_white_space --//
 

/**
 * Accepts regex string.  Escapes any characters that have meaning in regex,
 *     then creates RegExp instance using escaped string.  Returns RegExp
 *
 * Preconditions: None.
 *
 * Postconditions: Returns new RegExp instance.
 */
SOURCENET.FindInText.create_regex = function( regex_string_IN, be_case_sensitive_IN )
{
    
    // return reference
    var regex_OUT = null;

    // declare variables
    var me = "SOURCENET.FindInText.prototype.create_regex";
    var escaped_string = null;
    var regex_flags = "";
    
    // escape string
    escaped_string = regex_string_IN.replace( SOURCENET.FindInText.regex_escape_regex, '\\$1' );
    
    // parameters for regex.
    if ( be_case_sensitive_IN == true )
    {
        
        // case-sensitive.
        regex_flags = "g";

    }
    else
    {
    
        // case-insensitive...
        regex_flags = "gi";
        
    } //-- END check for case-sensitive --//
    
    // create the regex
    regex_OUT = new RegExp( escaped_string, regex_flags );
    
    return regex_OUT;
    
} //-- END method create_regex()
  

SOURCENET.FindInText.is_text_ignored = function( text_IN )
{
    // based on https://stackoverflow.com/a/24718430
    
    // return reference
    var is_ignored_OUT = false;

    // declare variables
    var me = "SOURCENET.FindInText.is_text_ignored";
    var lower_case_ignore_list = null;
    var lower_case_text = null;
    var ignore_index = -1;

    // convert ignore list to lower case - eventually, cache this or something.
    lower_case_ignore_list = SOURCENET.FindInText.text_to_ignore_list.map(
        function( value )
        {
            return value.toLowerCase();
        }
    );
    
    // convert text to lower case.
    lower_case_text = text_IN.toLowerCase();
    
    // look for lower case text in lower case ignore list.
    ignore_index = lower_case_ignore_list.indexOf( lower_case_text );

    // is it in the ignore list?
    if ( ignore_index < 0 )
    {
        // not found in list, so not ignored.
        is_ignored_OUT = false;
    }
    else
    {
        // in list - ignored.
        is_ignored_OUT = true;
    }
    
    //console.log( "In " + me + ": lower_case_text = " + lower_case_text + "; lower_case_ignore_list = " + lower_case_ignore_list + "; ignore_index = " + ignore_index )

    return is_ignored_OUT;
    
} //-- END function is_text_ignored() --//


//----------------------------------------------------------------------------//
// !----> FindInText instance methods
//----------------------------------------------------------------------------//


/**
 * Retrieves all the <p> tags that make up the article text, removes class
 *     "foundInText" from any where that class is present.
 *
 * Preconditions: None.
 *
 * Postconditions: Updates classes on article <p> tags so none are assigned
 *     "foundInText".
 */
SOURCENET.FindInText.prototype.clear_all_find_in_text_matches = function( element_id_IN )
{
    
    // declare variables
    var me = "SOURCENET.FindInText.prototype.clear_all_find_in_text_matches";

    // call the clear method with the master lists.
    this.clear_find_in_text_matches( element_id_IN, this.css_class_list_found_in_text, this.css_class_list_found_in_text_words );

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
SOURCENET.FindInText.prototype.clear_find_in_text_matches = function( element_id_IN,
                                                                      wrapper_class_list_IN,
                                                                      word_class_list_IN )
{
    
    // declare variables
    var me = "SOURCENET.FindInText.prototype.clear_find_in_text_matches";
    var cleanup_element_list = null;
    var cleanup_element_count = -1;
    var cleanup_element_index = -1;
    var cleanup_element_name = "";
    var article_elements = null;
    var list_length = -1;
    var list_index = -1;
    var current_css_class = null;
    
    // loop over cleanup element name list
    cleanup_element_list = SOURCENET.FindInText.cleanup_in_these_elements;
    cleanup_element_count = cleanup_element_list.length;
    for( cleanup_element_index = 0; cleanup_element_index < cleanup_element_count; cleanup_element_index++ )
    {
        
        // get current cleanup element.
        cleanup_element_name = cleanup_element_list[ cleanup_element_index ];
        
        // get article tags with that name.
        article_elements = this.get_elements_by_name( element_id_IN, cleanup_element_name );
    
        // remove each class in wrapper class list passed in.
        list_length = wrapper_class_list_IN.length;
        for ( list_index = 0; list_index < list_length; list_index++ )
        {
    
            // get class from list.
            current_css_class = wrapper_class_list_IN[ list_index ];
            
            // toggle class
            article_elements.toggleClass( current_css_class, false );
    
        } //-- end loop over CSS classes --//
            
        // set all elements' html() back to their text()...
        article_elements.each( function()
            {
                // call static method to clear work matches.
                SOURCENET.FindInText.clear_word_matches_in_element( this, word_class_list_IN )
            } //-- END anonymous function called on each element --//
        );
        
    } //-- END loop over cleanup element names. --//
    
} //-- END function SOURCENET.clear_find_in_text_matches() --//


/**
 * Configures instance to highlight in red.
 *
 * Preconditions: None.
 *
 * Postconditions: Updates instance to highlight in red.
 */
SOURCENET.FindInText.prototype.config_green_highlight = function()
{
    
    // declare variables
    var me = "SOURCENET.FindInText.prototype.config_green_highlight";
    
    // configure SOURCENET.text_finder
    this.set_css_class_matched_paragraph( SOURCENET.FindInText.CSS_CLASS_FOUND_IN_TEXT_GREEN );
    this.set_css_class_matched_words( SOURCENET.FindInText.CSS_CLASS_FOUND_IN_TEXT_MATCHED_WORDS_GREEN );
    
} //-- END method config_green_highlight()
  

/**
 * Configures instance to highlight in red.
 *
 * Preconditions: None.
 *
 * Postconditions: Updates instance to highlight in red.
 */
SOURCENET.FindInText.prototype.config_red_highlight = function()
{
    
    // declare variables
    var me = "SOURCENET.FindInText.prototype.config_red_highlight";
    
    // configure SOURCENET.text_finder
    this.set_css_class_matched_paragraph( SOURCENET.FindInText.CSS_CLASS_FOUND_IN_TEXT_RED );
    this.set_css_class_matched_words( SOURCENET.FindInText.CSS_CLASS_FOUND_IN_TEXT_MATCHED_WORDS_RED );
    
} //-- END method config_red_highlight()
  

/**
 * Configures instance to highlight in yellow.
 *
 * Preconditions: None.
 *
 * Postconditions: Updates instance to highlight in yellow.
 */
SOURCENET.FindInText.prototype.config_yellow_highlight = function()
{
    
    // declare variables
    var me = "SOURCENET.FindInText.prototype.config_yellow_highlight";
    
    // configure SOURCENET.text_finder
    this.set_css_class_matched_paragraph( SOURCENET.FindInText.CSS_CLASS_FOUND_IN_TEXT );
    this.set_css_class_matched_words( SOURCENET.FindInText.CSS_CLASS_FOUND_IN_TEXT_MATCHED_WORDS );
    
} //-- END method config_yellow_highlight()
  

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
SOURCENET.FindInText.prototype.find_text_in_string = function( find_text_IN,
                                                               string_IN )
{

    // return reference
    var string_OUT = null;

    // declare variables.
    var me = "SOURCENET.FindInText.prototype.find_text_in_string";
    var local_debug_flag = true;
    var search_in_text = null;
    var work_text = "";
    var current_find_text = "";
    var current_find_regex = null;
    var is_ignored = false;
    var found_index = -1;
    var text_around_match_list = null;
    var match_html = "";
    var current_text_index = -1;
    var new_html = "";
    var be_case_sensitive = false;
    var matches_array = null;
    var unique_matches_array = null;
    var current_match = "";
    
    // declare variables - initialize from instance variables
    var ignore_wrapper_element = false;
    var clear_on_new_search = false;
    var match_word_css_class = null;
    
    // initialize
    string_OUT = string_IN;
    work_text = string_IN;
    match_word_css_class = this.get_css_class_matched_words();
    ignore_wrapper_element = this.ignore_wrapper_element;
    be_case_sensitive = this.be_case_sensitive;

    // SOURCENET.log_message( "In " + me + "(): find text \"" + find_text_IN + "\"; element text = " + work_text );
    
    // get current find item.
    current_find_text = find_text_IN;
    
    // is it something we ignore?
    is_ignored = SOURCENET.FindInText.is_text_ignored( current_find_text );
    if ( is_ignored == false )
    {
        
        // look for text.
        if ( be_case_sensitive == true )
        {
            
            // case-sensitive.
            found_index = work_text.indexOf( current_find_text );

        }
        else
        {
        
            // case-insensitive...
            
            // ...regex.
            current_find_regex = SOURCENET.FindInText.create_regex( current_find_text, false );
            found_index = work_text.search( current_find_regex );
            
        }
        
        this.find_text_in_string_index = found_index;
        
        // got at least 1 match?
        if ( found_index >= 0 )
        {
    
            // found a match - split on the text we matched.
            if ( be_case_sensitive == true )
            {
                
                // case-sensitive.
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
    
            }
            else
            {
            
                // case-insensitive... find matches
                unique_matches_array = [];
                matches_array = work_text.match( current_find_regex );
                for ( var i = 0; i < matches_array.length; i++ )
                {
                    // get current match.
                    current_match = matches_array[ i ];
                    
                    // is it in unique list?
                    if ( unique_matches_array.indexOf( current_match ) < 0 )
                    {
                        // no. add it.
                        unique_matches_array.push( current_match );
                    }
                } //-- END loop over matches. --//
                
                // loop over unique matches, swapping each out.
                for ( var i = 0; i < unique_matches_array.length; i++ )
                {
                    // get current match.
                    current_match = unique_matches_array[ i ];
                    
                    // split on it.
                    text_around_match_list = work_text.split( current_match );
        
                    // add a span around the matched words.
                    matched_words_html = SOURCENET.HTML_SPAN_TO_CLASS;
                    matched_words_html += match_word_css_class;
                    matched_words_html += SOURCENET.HTML_SPAN_AFTER_CLASS;
                    matched_words_html += current_match;
                    matched_words_html += SOURCENET.HTML_SPAN_CLOSE;
                    
                    // put together again, but with <span>-ed matched word rather than just
                    //    the words themselves.
                    work_text = text_around_match_list.join( matched_words_html );
    
                }

                //if ( local_debug_flag == true )
                //{
                //    //SOURCENET.log_message( "**** In " + me + "(): MATCH \"" + find_text_IN + "\", work_text = \"" + work_text + "\"" );
                //    SOURCENET.log_message( "**** In " + me + "(): unique_matches_array = \"" + unique_matches_array + "\"" );
                //    SOURCENET.log_message( "**** In " + me + "(): matches_array = \"" + matches_array + "\"" );
                //}

            }
    
            if ( local_debug_flag == true )
            {
                //SOURCENET.log_message( "**** In " + me + "(): MATCH \"" + find_text_IN + "\", work_text = \"" + work_text + "\"" );
                SOURCENET.log_message( "**** In " + me + "(): MATCH \"" + find_text_IN + "\"" );
            }
        
        }
        else
        {
            if ( local_debug_flag == true )
            {
                //SOURCENET.log_message( "**** In " + me + "(): NO MATCH \"" + find_text_IN + "\", work_text = \"" + work_text + "\"" );
                SOURCENET.log_message( "**** In " + me + "(): NO MATCH \"" + find_text_IN + "\"" );
            }
        } //-- END check to see if match --//

    }
    else
    {
        
        // log that we ignored a word.
        SOURCENET.log_message( "**** In " + me + "(): Ignoring \"" + current_find_text + "\", text_to_ignore_list = \"" + SOURCENET.FindInText.text_to_ignore_list + "\"" );
        
    }
    
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
    var ignore_wrapper_element = false;
    var match_word_css_class = null;
    
    // initialize
    string_OUT = string_IN;
    work_text = string_IN;
    match_word_css_class = this.get_css_class_matched_words();
    ignore_wrapper_element = this.ignore_wrapper_element;

    SOURCENET.log_message( "In " + me + "(): find text list = " + find_text_list_IN + "; element text = " + work_text );
    
    // get count of items in list.
    find_text_item_count = find_text_list_IN.length;
    
    // loop over items.
    for ( current_index = 0; current_index < find_text_item_count; current_index++ )
    {
        
        // get current find item.
        current_find_text = find_text_list_IN[ current_index ];
        
        // look for text.
        work_text = this.find_text_in_string( current_find_text, work_text );

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
    var ignore_wrapper_element = false;
    var match_word_css_class = null;
    
    // initialize
    match_word_css_class = this.get_css_class_matched_words();
    ignore_wrapper_element = this.ignore_wrapper_element;

    // get element text and html
    jquery_element = jquery_element_IN;
    element_html = jquery_element.html();
    
    SOURCENET.log_message( "In " + me + "(): find text list = " + find_text_list_IN + "; element HTML = " + element_html );
    
    // call this.find_text_list_in_string().
    updated_html = this.find_text_list_in_string( element_html, find_text_list_IN );
    
    // any matches?
    if ( ( updated_html !== undefined ) && ( updated_html != null ) && ( updated_html != "" ) && ( updated_html != element_html ) )
    {
        
        // html string was changed - found at least one match.
        found_match_OUT = true;
        
        // update HTML in element.
        jquery_element.html( updated_html );
        
    }
    else
    {
        
        if ( updated_html != element_html )
        {
            
            // error - no HTML came back.
            SOURCENET.log_message( "In " + me + "(): updated_html = " + updated_html + "; element HTML = " + element_html );
            
        }

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
    var ignore_wrapper_element = false;
    var match_word_css_class = null;
    
    // initialize
    match_word_css_class = this.get_css_class_matched_words();
    ignore_wrapper_element = this.ignore_wrapper_element;

    // get element text and html
    jquery_element = jquery_element_IN;
    element_text = jquery_element.text();
    
    SOURCENET.log_message( "In " + me + "(): find text list = " + find_text_list_IN + "; element text = " + element_text );
    
    // call this.find_text_list_in_string().
    updated_text = this.find_text_list_in_string( element_text, find_text_list_IN );
    
    // any matches?
    if ( updated_text != element_text )
    {
        
        // html string was changed - found at least one match.
        found_match_OUT = true;
        
        // update HTML in element.
        jquery_element.html( updated_text );
        
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
SOURCENET.FindInText.prototype.find_text_in_element = function( jquery_element_IN,
                                                                find_text_list_IN,
                                                                fail_over_to_text_IN )
{
    
    // return reference
    var found_match_OUT = false;

    // declare variables.
    var me = "SOURCENET.FindInText.prototype.find_text_in_element";
    var ignore_wrapper_element = false;
    var jquery_element = null;
    var match_p_css_class = null;
    var match_word_css_class = null;
    var be_case_sensitive = false;
    var fail_over_to_text = false;
    var where_to_look = null;
    var use_match_text = true;
    
    // declare variables - match_text function.
    var find_text_count = -1;
    var find_text_index = -1;
    var is_ignored = false;
    var current_find_text = null;
    var dom_element = null;
    var regex_flags = null;
    var match_text_regex = null;

    // initialize
    ignore_wrapper_element = this.ignore_wrapper_element;
    match_p_css_class = this.get_css_class_matched_paragraph();
    match_word_css_class = this.get_css_class_matched_words();
    be_case_sensitive = this.be_case_sensitive;
    fail_over_to_text = fail_over_to_text_IN;
    if ( fail_over_to_text === undefined )
    {
        
        // defaults to true, the old way.
        fail_over_to_text = true;
        
    }
    where_to_look = this.default_find_location;

    // look for text in HTML element
    jquery_element = jquery_element_IN;
    
    SOURCENET.log_message( "In " + me + "(): where_to_look = " + where_to_look + "; use_match_text = " + use_match_text + "; jquery_element tagName = " + jquery_element.get( 0 ).tagName + ", class = " + jquery_element.attr("class") + " and id = " + jquery_element.attr("id") );

    // use match_text?
    if ( use_match_text == true )
    {
        
        // loop over list of text to find.
        find_text_count = find_text_list_IN.length
        for ( find_text_index = 0; find_text_index < find_text_count; find_text_index++ )
        {
        
            // get text
            current_find_text = find_text_list_IN[ find_text_index ];
            
            SOURCENET.log_message( "In " + me + "(): current_find_text = \"" + current_find_text + "\"" );

            // is it something we ignore?
            is_ignored = SOURCENET.FindInText.is_text_ignored( current_find_text );
            if ( is_ignored == false )
            {
                
                // set up call to match_text
                
                // get actual DOM element
                dom_element = jquery_element.get( 0 );
                
                // make regexp.
                //match_text_regex = new RegExp( current_find_text, regex_flags );
                match_text_regex = SOURCENET.FindInText.create_regex( current_find_text, be_case_sensitive );
                
                SOURCENET.log_message( "In " + me + "(): match_text_regex = \"" + match_text_regex + "\"" );

                // call match_text
                this.match_text(
                    dom_element,
                    match_text_regex,
                    function( node, match, offset )
                    {
                        var span = document.createElement( "span" );
                        span.className = match_word_css_class;
                        span.textContent = match;
                        return span;
                    }
                );
                
            }
            
        } //-- END loop over find_text_list --//
        
        // found any matches?
        if ( this.match_text_match_count > 0 )
        {
            // yes
            found_match_OUT = true;
        }
        else
        {
            // no
            found_match_OUT = false;
        }
        
    }
    else
    {
        
        // Where to look?
        if ( where_to_look == "html" )
        {
            
            // HTML
            found_match_OUT = this.find_text_list_in_element_html( jquery_element, find_text_list_IN );
            
            // did we find match?
            if ( ( found_match_OUT == false ) && ( fail_over_to_text == true ) )
            {
        
                // Fail over to text.
                found_match_OUT = this.find_text_list_in_element_text( jquery_element, find_text_list_IN );
        
            } //-- END check if no match and fail over to text. --//
    
        }
        else
        {
    
            // Text
            found_match_OUT = this.find_text_list_in_element_text( jquery_element, find_text_list_IN );
    
        } //-- END check where to look. --//
    
        // did we find match?
        if ( ( found_match_OUT == true ) && ( ignore_wrapper_element == false ) )
        {
    
            // For matches, add class passed in.
            jquery_element.toggleClass( match_p_css_class, true );
    
        } //-- END check if found match? --//

    }

    return found_match_OUT;

} //-- END function SOURCENET.find_text_in_element --//


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
    var me = "SOURCENET.find_text_in_p_tag";
    
    // call generic element method.
    found_match_OUT = this.find_text_in_element( p_tag_jquery_IN, find_text_list_IN, fail_over_to_text_IN );
    
    return found_match_OUT;

} //-- END function SOURCENET.find_text_in_p_tag --//


/**
 * Retrieves all the <p> tags that make up the article text, returns them in a
 *     list.  If none found, returns empty list.  If error, returns null.
 *
 * Preconditions: None.
 *
 * Postconditions: None.
 */
SOURCENET.FindInText.prototype.get_elements_by_name = function( look_in_element_id_IN, element_name_to_find_IN )
{
    
    // return reference
    var elements_OUT = null;
    
    // declare variables
    var me = "SOURCENET.FindInText.prototype.get_elements_by_name";
    var jquery_element = null;
    
    // retrieve element in which we should look (id/name = look_in_element_id_IN).
    jquery_element = $( '#' + look_in_element_id_IN );
    
    // find all tags with name = element_name_to_find_IN.
    grafs_OUT = jquery_element.find( element_name_to_find_IN );

    return grafs_OUT;
    
} //-- END method get_elements_by_name() --//


/**
 * Retrieves all the <p> tags that make up the article text, returns them in a
 *     list.  If none found, returns empty list.  If error, returns null.
 *
 * Preconditions: None.
 *
 * Postconditions: None.
 */
SOURCENET.FindInText.prototype.get_paragraphs = function( element_id_IN )
{
    
    // return reference
    var grafs_OUT = null;
    
    // declare variables
    var me = "SOURCENET.FindInText.prototype.get_paragraphs";

    // call get_elements_by_name() with "p".
    grafs_OUT = self.get_elements_by_name( element_id_IN, "p" );

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


/**
 * Accepts Javascript DOM node, regex that we want to match, and a callback
 *     function that should accept node, match string, and offset, and return a
 *     DOM Node that you want inserted in place of the match.
 *
 * Example call:
 * matchText(
 *     document.getElementsByTagName("article")[0],
 *     new RegExp("\\b" + searchTerm + "\\b", "g"),
 *     function( node, match, offset ) 
 *     {
 *         var span = document.createElement("span");
 *         span.className = "search-term";
 *         span.textContent = match;
 *         return span;
 *     }
 * );
 *
 * from: https://stackoverflow.com/a/29301739
 */
SOURCENET.FindInText.prototype.match_text = function( node, regex, callback, excludeElements )
{ 

    excludeElements || (excludeElements = ['script', 'style', 'iframe', 'canvas']);
    
    // init recursion bookkeeping
    this.match_text_level += 1
    
    // only zero out this.match_text_match_count if level is 1.
    if ( this.match_text_level == 1 )
    {
        this.match_text_match_count = 0;        
    }
    
    // declare variables
    var me = "SOURCENET.FindInText.prototype.match_text";
    var debug_message = "";
    var child = null;
    var child_node_type = null;
    var node_tag_name = null;
    var ignore_wrapper_element = true;
    var match_p_css_class = "";
    var jquery_node = null;
    var node_html = null;
    var node_text = null;
    
    // initialize
    ignore_wrapper_element = this.ignore_wrapper_element;
    match_p_css_class = this.get_css_class_matched_paragraph();
    jquery_node = $( node );
    node_html = jquery_node.html()
    node_text = jquery_node.text()
    
    // child
    child = node.firstChild;
    if ( ( child !== undefined ) && ( child != null ) )
    {
                
        child_node_type = child.nodeType;
        
    }
    
    // debug message
    debug_message = "In " + me + "():"
    debug_message += " node tagName = " + node_tag_name;
    debug_message += "; child nodeType = " + child_node_type;
    if ( child_node_type == 3 )
    {
        debug_message += "; child.data = " + child.data;
    }
    debug_message += "; this.match_text_level = " + this.match_text_level;
    
    
    // is regex in html?
    if ( node_html.search( regex ) > -1 )
    {
        SOURCENET.log_message( debug_message + "; found regex match ( regex = " + regex + " ) in node HTML = " + node_html );
    }
    
    // is regex in text?
    if ( node_text.search( regex ) > -1 )
    {
        SOURCENET.log_message( debug_message + "; found regex match ( regex = " + regex + " ) in node text = " + node_text );
    }
    
    // get node name
    node_tag_name = node.tagName;

    while ( child ) {

        switch ( child.nodeType )
        {

            case 1:

                if ( excludeElements.indexOf( child.tagName.toLowerCase() ) > -1 )
                {
                    break;
                }
                this.match_text( child, regex, callback, excludeElements );
                break;
            
            case 3:
                
                var bk = 0;
                child.data.replace( regex, function( all )
                    {
                        var args = [].slice.call( arguments );
                        var offset = args[ args.length - 2 ];
                        var newTextNode = child.splitText( offset + bk );
                        var tag = null;

                        bk -= child.data.length + all.length;
    
                        newTextNode.data = newTextNode.data.substr( all.length );
                        tag = callback.apply( window, [ child ].concat( args ) );
                        child.parentNode.insertBefore( tag, newTextNode );
                        child = newTextNode;
                    
                        // got a match - increment counter.
                        this.match_text_match_count++;
                        SOURCENET.log_message( "In " + me + "(): args = " + args + "; found match all = " + all );
                        
                        // we have a match, do we also highlight the <p>?
                        //     Check if we are ignoring wrapper element, and if not,
                        //     limit to just changing <p> tags.
                        if ( ( ignore_wrapper_element == false ) && ( node_tag_name.toLowerCase() == "p" ) )
                        {
                    
                            // For matches, add class passed in.
                            $( node ).toggleClass( match_p_css_class, true );
                    
                        } //-- END check if found match? --//
                        
                        // call normalize() on parent to make sure adjacent text
                        //     nodes are combined.
                        child.parentNode.normalize()
                    }
                );
                
                regex.lastIndex = 0;

                break;
        }

        child = child.nextSibling;
    }

    // init recursion bookkeeping
    this.match_text_level -= 1
    
    return node;
}

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