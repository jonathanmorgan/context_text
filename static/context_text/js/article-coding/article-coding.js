//============================================================================//
// javascript for article coding.
//============================================================================//

// ! requires context_text.js
// ! requires find-in-text.js

//----------------------------------------------------------------------------//
// !====> namespace!
//----------------------------------------------------------------------------//


var CONTEXT_TEXT = CONTEXT_TEXT || {};


//----------------------------------------------------------------------------//
// !====> namespaced variables
//----------------------------------------------------------------------------//


// JSON to prepopulate page if we are editing.
CONTEXT_TEXT.data_store_json = null;
CONTEXT_TEXT.article_data_id = -1;

// person store used to keep track of authors and persons while coding.
CONTEXT_TEXT.data_store = null;

// DEBUG!
CONTEXT_TEXT.debug_flag = false;

// JSON property names
CONTEXT_TEXT.JSON_PROP_PERSON_NAME = "person_name";
CONTEXT_TEXT.JSON_PROP_FIXED_PERSON_NAME = "fixed_person_name";
CONTEXT_TEXT.JSON_PROP_PERSON_TYPE = "person_type";
CONTEXT_TEXT.JSON_PROP_TITLE = "title";
CONTEXT_TEXT.JSON_PROP_PERSON_ORGANIZATION = "person_organization";
CONTEXT_TEXT.JSON_PROP_QUOTE_TEXT = "quote_text";
CONTEXT_TEXT.JSON_PROP_PERSON_INDEX = "person_index";
CONTEXT_TEXT.JSON_PROP_PERSON_ID = "person_id";
CONTEXT_TEXT.JSON_PROP_ORIGINAL_PERSON_TYPE = "original_person_type";
CONTEXT_TEXT.JSON_PROP_ARTICLE_PERSON_ID = "article_person_id";

// person types:
CONTEXT_TEXT.PERSON_TYPE_SOURCE = "source";
CONTEXT_TEXT.PERSON_TYPE_SUBJECT = "subject";
CONTEXT_TEXT.PERSON_TYPE_AUTHOR = "author";
CONTEXT_TEXT.PERSON_TYPE_ARRAY = [ CONTEXT_TEXT.PERSON_TYPE_SOURCE, CONTEXT_TEXT.PERSON_TYPE_SUBJECT, CONTEXT_TEXT.PERSON_TYPE_AUTHOR ];

// Article coding submit button values
CONTEXT_TEXT.ARTICLE_CODING_SUBMIT_BUTTON_VALUE_WAIT = "Please wait...";
CONTEXT_TEXT.ARTICLE_CODING_SUBMIT_BUTTON_VALUE_PROCESS = "Process Article Coding";
CONTEXT_TEXT.ARTICLE_CODING_SUBMIT_BUTTON_VALUE_RESET = "Process Article Coding!";

// ! HTML element IDs
CONTEXT_TEXT.DIV_ID_PERSON_CODING = "person-coding";
CONTEXT_TEXT.INPUT_ID_PERSON_NAME = "person-name";
// see CONTEXT_TEXT.INPUT_ID_FIXED_PERSON_NAME below.
CONTEXT_TEXT.INPUT_ID_PERSON_TYPE = "person-type";
CONTEXT_TEXT.INPUT_ID_TITLE = "person-title";
CONTEXT_TEXT.INPUT_ID_ORGANIZATION = "person-organization";
CONTEXT_TEXT.INPUT_ID_QUOTE_TEXT = "source-quote-text";
CONTEXT_TEXT.INPUT_ID_PERSON_INDEX = "data-store-person-index";
CONTEXT_TEXT.INPUT_ID_MATCHED_PERSON_ID = "matched-person-id";
CONTEXT_TEXT.INPUT_ID_ORIGINAL_PERSON_TYPE = "original-person-type";
CONTEXT_TEXT.INPUT_ID_ARTICLE_PERSON_ID = "article-person-id";
CONTEXT_TEXT.DIV_ID_LOOKUP_PERSON_EXISTING_ID = "lookup-person-existing-id";

// HTML elements - fix person name
CONTEXT_TEXT.DIV_ID_FIX_PERSON_NAME_LINK = "fix-person-name-link";
CONTEXT_TEXT.DIV_ID_FIX_PERSON_NAME = "fix-person-name";
CONTEXT_TEXT.INPUT_ID_FIXED_PERSON_NAME = "fixed-person-name";


// HTML elements - form submission
CONTEXT_TEXT.INPUT_ID_SUBMIT_ARTICLE_CODING = "input-submit-article-coding";
CONTEXT_TEXT.INPUT_ID_DATA_STORE_JSON = "id_data_store_json";

// django-ajax-select HTML
CONTEXT_TEXT.INPUT_ID_AJAX_ID_PERSON = "id_person";
CONTEXT_TEXT.INPUT_ID_AJAX_ID_PERSON_TEXT = "id_person_text";
CONTEXT_TEXT.DIV_ID_AJAX_ID_PERSON_ON_DECK = "id_person_on_deck";

// Find in Article Text - Dynamic CSS class names
//CONTEXT_TEXT.CSS_CLASS_FOUND_IN_TEXT = "foundInText";
//CONTEXT_TEXT.CSS_CLASS_FOUND_IN_TEXT_MATCHED_WORDS = "foundInTextMatchedWords";

// Find in Article Text - HTML element IDs
//CONTEXT_TEXT.INPUT_ID_TEXT_TO_FIND_IN_ARTICLE = "text-to-find-in-article";

// Find in Article Text - HTML for matched word highlighting
//CONTEXT_TEXT.HTML_SPAN_MATCHED_WORDS = "<span class=\"" + CONTEXT_TEXT.CSS_CLASS_FOUND_IN_TEXT_MATCHED_WORDS + "\">";
//CONTEXT_TEXT.HTML_SPAN_CLOSE = "</span>";

// Compress white space in values?
CONTEXT_TEXT.compress_white_space = false;


//----------------------------------------------------------------------------//
// !====> function definitions
//----------------------------------------------------------------------------//


/**
 * Opposite of CONTEXT_TEXT.fix_person_name() - show()s link to fix person name, 
 *     hides form input and buttons to fix person name, removes current value
 *     from "fixed-person-name" <input>.
 *
 * Preconditions: None.
 *
 * Postconditions: show()s link to fix person name, hides form input and buttons
 *     to fix person name, removes current value from "fixed-person-name"
 *     <input>.
 */
CONTEXT_TEXT.cancel_fix_person_name = function()
{
    // declare variables
    var me = "CONTEXT_TEXT.cancel_fix_person_name";
    var fix_link_div_id = "";
    var fix_link_div = null;
    var fix_area_div_id = "";
    var fix_area_div = null;
    var input_element = null;
    
    // get div that contains actual fix area and hide() it.
    fix_area_div_id = CONTEXT_TEXT.DIV_ID_FIX_PERSON_NAME;
    fix_area_div = $( '#' + fix_area_div_id );
    fix_area_div.hide();

    // clear fixed-person-name <input>.
    CONTEXT_TEXT.clear_fixed_person_name();
    
    // get div that contains link and show() it.
    fix_link_div_id = CONTEXT_TEXT.DIV_ID_FIX_PERSON_NAME_LINK;
    fix_link_div = $( '#' + fix_link_div_id );
    fix_link_div.show();
    
} //-- END function CONTEXT_TEXT.cancel_fix_person_name() --//


/**
 * Clears out hidden input used to hold the Article_Person ID for the current
 *     person (Article_Author or Article_Source, depending on the type).
 *
 * Preconditions: for anything to appear, CONTEXT_TEXT.data_store must have been
 *     initialized and at least one person added to it, and you must have loaded
 *     existing coding - new coding won't have these IDs.
 *
 * @param {string} status_message_IN - message to place in status area.  If undefined, null, or "", no message output.
 */
CONTEXT_TEXT.clear_article_person_id = function( status_message_IN )
{
    
    // declare variables.
    var me = "CONTEXT_TEXT.clear_article_person_id";
    var status_message_array = [];
    var temp_element = null;
    var on_deck_person_element = null;
    
    // clear the coding form.
    CONTEXT_TEXT.log_message( "Top of " + me );
        
    // article-person-id
    temp_element = $( '#' + CONTEXT_TEXT.INPUT_ID_ARTICLE_PERSON_ID );
    temp_element.val( -1 );
        
    // got a status message?
    if ( ( status_message_IN != null ) && ( status_message_IN != "" ) )
    {
        // make status message array (empty message will clear status area).
        status_message_array = [];
        status_message_array.push( status_message_IN );
        
        // output it.
        CONTEXT_TEXT.output_status_messages( status_message_array );
    }
    
} //-- END function CONTEXT_TEXT.clear_article_person_id() --//


/**
 * Clears out coding form and status message area, and optionally displays a
 *    status message if one passed in.
 *
 * Preconditions: for anything to appear, CONTEXT_TEXT.data_store must have been
 *    initialized and at least one person added to it.
 *
 * @param {string} status_message_IN - message to place in status area.  If undefined, null, or "", no message output.
 */
CONTEXT_TEXT.clear_coding_form = function( status_message_IN )
{
    
    // declare variables.
    var me = "CONTEXT_TEXT.clear_coding_form";
    var person_property_list = null;
    var person_property_info = null;
    var current_index = -1;
    var property_count = -1;
    var current_property_name = "";
    var current_property_info = null;
    var clear_form_function = null;
    var input_id = "";
    var default_value = "";
    var temp_element = null;
    
    // declare variables - outputting status messages.
    var is_status_message_OK = false;
    var status_message_array = [];
    
    // clear the coding form.
    CONTEXT_TEXT.log_message( "Top of " + me );

    // get property info.
    person_property_list = CONTEXT_TEXT.Person_property_name_list;
    person_property_info = CONTEXT_TEXT.Person_property_name_to_info_map;
        
    // loop over properties
    property_count = person_property_list.length;
    for ( current_index = 0; current_index < property_count; current_index++ )
    {
        
        // get current property name.
        current_property_name = person_property_list[ current_index ];
        
        // retrieve the property info.
        current_property_info = person_property_info[ current_property_name ];
        
        // clear the field.
        current_property_info.clear_value();
        
    } //-- END loop over Person properties --//
    
    // clear any find-in-article-text matches, and clear find text entry field.
    CONTEXT_TEXT.clear_find_in_text();
    
    // got a status message?
    if ( ( status_message_IN != null ) && ( status_message_IN != "" ) )
    {
        // make status message array (empty message will clear status area).
        status_message_array = [];
        status_message_array.push( status_message_IN );
        
        // output it.
        CONTEXT_TEXT.output_status_messages( status_message_array );
    }
    
} //-- END function CONTEXT_TEXT.clear_coding_form() --//


/**
 * Retrieves all the <p> tags that make up the article text, removes class
 *     "foundInText" from any where that class is present.
 *
 * Preconditions: None.
 *
 * Postconditions: Updates classes on article <p> tags so none are assigned
 *     "foundInText".
 */
CONTEXT_TEXT.clear_find_in_text_matches = function(  )
{
    
    // declare variables
    var me = "CONTEXT_TEXT.clear_find_in_text_matches";
    var article_paragraphs = null;
    
    // get article <p> tags.
    article_paragraphs = CONTEXT_TEXT.get_article_paragraphs();
    
    // remove class "foundInText" from all.
    article_paragraphs.toggleClass( CONTEXT_TEXT.CSS_CLASS_FOUND_IN_TEXT, false );
    
    // set all paragraphs' html() back to their text()...
    article_paragraphs.each( function()
        {
            // declare variables.
            var jquery_p_element = null;
            var paragraph_html = "";
            var paragraph_text = "";
            var span_index = -1;
            
            // get paragraph text
            jquery_p_element = $( this );
            paragraph_html = jquery_p_element.html();
            paragraph_text = jquery_p_element.text();
            
            // is there a matched words span present in html?
            span_index = paragraph_html.indexOf( CONTEXT_TEXT.HTML_SPAN_MATCHED_WORDS );
            
            // if found, update store plain text .
            if ( span_index > -1 )
            {
                
                // store plain text in <p>.html() to remove any HTML.
                jquery_p_element.html( paragraph_text );
                                    
            } //-- END check to see if <span> found --//
        } //-- END anonymous function called on each paragraph --//
    );

} //-- END function CONTEXT_TEXT.clear_find_in_text_matches() --//


/**
 * Loads current person_name value into field where it can be manually fixed.
 */
CONTEXT_TEXT.clear_fixed_person_name = function()
{
    
    // declare variables
    var input_element = null;

    // get fixed_person_name text field,  place value there.
    input_element = $( '#' + CONTEXT_TEXT.INPUT_ID_FIXED_PERSON_NAME );
    input_element.val( "" );
    
} //-- END function CONTEXT_TEXT.clear_fixed_person_name() --//


/**
 * Clears out matched person ID hidden input, then also clears out the <div>
 *     where the existing matched person ID is displayed.
 *
 * Preconditions: None
 *
 * @param {string} status_message_IN - message to place in status area.  If undefined, null, or "", no message output.
 */
CONTEXT_TEXT.clear_matched_person_id = function( status_message_IN )
{
    
    // declare variables.
    var me = "CONTEXT_TEXT.clear_matched_person_id";
    var status_message_array = [];
    var temp_element = null;
    var on_deck_person_element = null;
    
    // clear the coding form.
    CONTEXT_TEXT.log_message( "Top of " + me );
        
    // matched-person-id
    temp_element = $( '#' + CONTEXT_TEXT.INPUT_ID_MATCHED_PERSON_ID );
    temp_element.val( -1 );
    
    // get <div> inside person lookup area where we display that there is an ID.
    temp_element = $( '#' + CONTEXT_TEXT.DIV_ID_LOOKUP_PERSON_EXISTING_ID );
    temp_element.empty();

    // got a status message?
    if ( ( status_message_IN != null ) && ( status_message_IN != "" ) )
    {
        // make status message array (empty message will clear status area).
        status_message_array = [];
        status_message_array.push( status_message_IN );
        
        // output it.
        CONTEXT_TEXT.output_status_messages( status_message_array );
    }
    
} //-- END function CONTEXT_TEXT.clear_matched_person_id() --//


/**
 * Clears out hidden input used to hold the original person type value when we
 *     update existing coding.
 *
 * Preconditions: None.
 *
 * @param {string} status_message_IN - message to place in status area.  If undefined, null, or "", no message output.
 */
CONTEXT_TEXT.clear_original_person_type = function( status_message_IN )
{
    
    // declare variables.
    var me = "CONTEXT_TEXT.clear_original_person_type";
    var status_message_array = [];
    var temp_element = null;
    var on_deck_person_element = null;
    
    // clear the coding form.
    CONTEXT_TEXT.log_message( "Top of " + me );
        
    // original-person-type
    temp_element = $( '#' + CONTEXT_TEXT.INPUT_ID_ORIGINAL_PERSON_TYPE );
    temp_element.val( "" );
        
    // got a status message?
    if ( ( status_message_IN != null ) && ( status_message_IN != "" ) )
    {
        // make status message array (empty message will clear status area).
        status_message_array = [];
        status_message_array.push( status_message_IN );
        
        // output it.
        CONTEXT_TEXT.output_status_messages( status_message_array );
    }
    
} //-- END function CONTEXT_TEXT.clear_original_person_type() --//


/**
 * Clears out and resets all fields related to choosing a person ID for the
 *     current person.  This includes the AJAX lookup fields and fields and
 *     <div>s used to hold a previously selected person ID.
 *
 * Preconditions: None.
 *
 * @param {string} status_message_IN - message to place in status area.  If undefined, null, or "", no message output.
 */
CONTEXT_TEXT.clear_person_id = function( status_message_IN )
{
    
    // declare variables.
    var me = "CONTEXT_TEXT.clear_person_id";
    var status_message_array = [];
    var temp_element = null;
    var on_deck_person_element = null;
    
    // clear the coding form.
    CONTEXT_TEXT.log_message( "Top of " + me );
        
    // clear out the person lookup form
    CONTEXT_TEXT.clear_person_lookup_form( true, null );
    
    // clear out the matched person ID
    CONTEXT_TEXT.clear_matched_person_id( null );
    
    // got a status message?
    if ( ( status_message_IN != null ) && ( status_message_IN != "" ) )
    {
        // make status message array (empty message will clear status area).
        status_message_array = [];
        status_message_array.push( status_message_IN );
        
        // output it.
        CONTEXT_TEXT.output_status_messages( status_message_array );
    }
    
} //-- END function CONTEXT_TEXT.clear_original_person_type() --//


/**
 * Clears out all inputs and divs related to the DAL person looker-upper.
 *
 * Preconditions: None
 *
 * @param {string} status_message_IN - message to place in status area.  If undefined, null, or "", no message output.
 */
CONTEXT_TEXT.clear_person_lookup_form = function( do_clear_matched_id_IN, status_message_IN )
{
    
    // declare variables.
    var me = "CONTEXT_TEXT.clear_person_lookup_form";
    var status_message_array = [];
    var dal_select_element = null;
    var dal_display_span_element = null;
    
    // clear the coding form.
    CONTEXT_TEXT.log_message( "Top of " + me );

    // Clear the autocomplete
    dal_select_element = $( ':input[name=person]' );
    dal_select_element.val( null ).trigger( 'click' );

    // wipe any stored display information.
    dal_display_span_element = $( '#select2-id_person-container' )
    dal_display_span_element.text( "" )
    dal_display_span_element.attr( 'title', "" );
        
    // do we clear out any matched person ID?
    if ( do_clear_matched_id_IN == true )
    {
        
        // yes, clear it out.
        CONTEXT_TEXT.clear_matched_person_id();
        
    }
    
    // got a status message?
    if ( ( status_message_IN != null ) && ( status_message_IN != "" ) )
    {
        // make status message array (empty message will clear status area).
        status_message_array = [];
        status_message_array.push( status_message_IN );
        
        // output it.
        CONTEXT_TEXT.output_status_messages( status_message_array );
    }
    
} //-- END function CONTEXT_TEXT.clear_person_lookup_form() --//


/**
 * Clears out person type field, then calls a function to reset the form for the
 *     default (empty, so non-subject) person type.
 *
 * Preconditions: None.
 *
 * @param {string} status_message_IN - message to place in status area.  If undefined, null, or "", no message output.
 */
CONTEXT_TEXT.clear_person_type = function( status_message_IN )
{
    
    // declare variables.
    var me = "CONTEXT_TEXT.clear_person_type";
    var status_message_array = [];
    var temp_element = null;
    var on_deck_person_element = null;
    
    // clear the coding form.
    CONTEXT_TEXT.log_message( "Top of " + me );
        
    // person-type
    temp_element = $( '#' + CONTEXT_TEXT.INPUT_ID_PERSON_TYPE );
    temp_element.val( "" );
    
    // call CONTEXT_TEXT.process_selected_person_type();
    CONTEXT_TEXT.process_selected_person_type();
        
    // got a status message?
    if ( ( status_message_IN != null ) && ( status_message_IN != "" ) )
    {
        // make status message array (empty message will clear status area).
        status_message_array = [];
        status_message_array.push( status_message_IN );
        
        // output it.
        CONTEXT_TEXT.output_status_messages( status_message_array );
    }
    
} //-- END function CONTEXT_TEXT.clear_person_type() --//


/**
 * Repaints the area where coded persons are displayed.
 *
 * Preconditions: for anything to appear, CONTEXT_TEXT.data_store must have been
 *    initialized and at least one person added to it.
 */
CONTEXT_TEXT.display_persons = function()
{
    
    // declare variables.
    var me = "CONTEXT_TEXT.display_persons";
    var row_id_prefix = "";
    var my_data_store = null;
    var person_list_element = null;
    var person_index = -1;
    var person_count = -1;
    var current_person = null;
    var current_row_id = "";
    var current_row_selector = "";
    var current_row_element = null;
    var current_row_element_count = -1;
    var got_person = false;
    var person_string = "";
    var got_row= false;
    var do_create_row = false;
    var do_update_row = false;
    var do_remove_row = false;
    var row_contents = "";
    var button_element = null;
    
    // declare variables - make form to submit list.
    var active_person_count = -1;
    var div_person_list_element = null;
    var form_element = null;
    
    // initialize variables
    row_id_prefix = "person-";
    
    // get person store
    my_data_store = CONTEXT_TEXT.get_data_store();
    
    // for now, display by CONTEXT_TEXT.log_message()-ing JSON string.
    //CONTEXT_TEXT.log_message( "In " + me + "(): DataStore = " + JSON.stringify( my_data_store ) );
    
    // get <table id="person-list-table" class="personListTable">
    person_list_element = $( '#person-list-table' );
    
    // loop over the persons in the list.
    person_count = my_data_store.person_array.length;
    CONTEXT_TEXT.log_message( "In " + me + "(): Person Count = " + person_count );
    
    // check to see if one or more persons.
    if ( person_count > 0 )
    {

        // at least 1 - loop.
        active_person_count = 0;
        for( person_index = 0; person_index < person_count; person_index++ )
        {
            
            // initialize variables.
            got_person = false;
            got_row = false;
            do_create_row = false;
            do_update_row = false;
            do_remove_row = false;
            button_element = null;
            
            // get person.
            current_person = my_data_store.get_person_at_index( person_index );
    
            // got person?
            if ( current_person != null )
            {
                // yes - set flag, update person_string.
                got_person = true;
                active_person_count += 1;
                person_string = current_person.to_table_cell_html();
                
            }
            else
            {
    
                // CONTEXT_TEXT.log_message( "In " + me + "(): no person for index " + person_index );
                person_string = "null";
    
            } //-- END check to see if person --//
            
            CONTEXT_TEXT.log_message( "In " + me + "(): Person " + person_index + ": " + person_string );
            
            // try to get <tr> for that index.
            current_row_id = row_id_prefix + person_index;
            current_row_selector = "#" + current_row_id;
            current_row_element = person_list_element.find( current_row_selector );
            current_row_element_count = current_row_element.length;
            //CONTEXT_TEXT.log_message( "DEBUG: row element: " + current_row_element + "; length = " + current_row_element_count );
            
            // matching row found?
            if ( current_row_element_count > 0 )
            {
                
                // yes - set flag.
                got_row = true;
    
            } //-- END check to see if row --//
            
            // based on person and row, what do we do?
            if ( got_row == true )
            {
                
                //CONTEXT_TEXT.log_message( "In " + me + "(): FOUND <li> for " + current_li_id );
                // got person?
                if ( got_person == true )
                {
                    
                    // yes.  convert to string and replace value, in case there have
                    //    been changes.
                    do_create_row = false;
                    do_update_row = true;
                    do_remove_row = false;
                    
                }
                else
                {
                    
                    // no person - remove row
                    do_create_row = false;
                    do_update_row = false;
                    do_remove_row = true;                
                    
                }
                
            }
            else //-- no row --//
            {
                
                //CONTEXT_TEXT.log_message( "In " + me + "(): NO row for " + current_row_id );
                // got person?
                if ( got_person == true )
                {
                    
                    // yes.  convert to string and replace value, in case there have
                    //    been changes.
                    do_create_row = true;
                    do_update_row = true;
                    do_remove_row = false;
                    
                }
                else
                {
                    
                    // no person - nothing to do.
                    do_create_row = false;
                    do_update_row = false;
                    do_remove_row = false;                
                    
                }
    
            } //-- END check to see if row for current person. --//
            
            // Do stuff!
            
            CONTEXT_TEXT.log_message( "In " + me + "(): WHAT TO DO?: do_create_row = " + do_create_row + "; do_update_row = " + do_update_row + "; do_remove_row = " + do_remove_row );
            
            // crate new row?
            if ( do_create_row == true )
            {
                
                // create row with id = row_id_prefix + person_index, store in
                //    current_row_element.
                current_row_element = $( '<tr></tr>' );
                current_row_element.attr( "id", row_id_prefix + person_index );
                
                // prepend it to the person_list_element
                person_list_element.prepend( current_row_element );
                
            } //-- END check to see if do_create_li --//
            
            // update contents of <tr>?
            if ( do_update_row == true )
            {
                
                // for now, just place person string in a <td>.
                row_contents = person_string;
                
                // (and other stuff needed for that to work.)
                row_contents += '<td><input type="button" id="remove-person-' + person_index + '" name="remove-person-' + person_index + '" value="Remove" onclick="CONTEXT_TEXT.remove_person( ' + person_index + ' )" /></td>';
                
                current_row_element.html( row_contents );
                
            } //-- END check to see if do_update_li --//
            
            // delete <tr>?
            if ( do_remove_row == true )
            {
                
                // delete <li>.
                current_row_element.remove();
                
            } //-- END check to see if do_delete_li --//
            
        } //-- END loop over persons in list --//
        
        // try to find the form element.
        form_element = $( '#submit-article-coding' );
        
        // got active people?
        if ( active_person_count > 0 )
        {
            
            // make sure form is visible.
            CONTEXT_TEXT.log_message( "In " + me + "(): active people, show coding submit <form>." );
            form_element.show();
                        
        }
        else //-- no active people. --//
        {
            
            // no active people, hide form.
            CONTEXT_TEXT.log_message( "In " + me + "(): no people, hide coding submit <form>." );
            form_element.hide();
                    
        } //-- END check to see if active people. --//
        
    }
    else
    {
        
        // nothing in list.  Move on, but output log since I'm not sure why we
        //    got here.
        CONTEXT_TEXT.log_message( "In " + me + "(): Nothing in person_array.  Moving on." );
        
    } //-- END check to see if at least 1 item in list. --//
    
} //-- END function CONTEXT_TEXT.display_persons() --//


/**
 * Retrieves current person's last name, then looks for it in article text.
 *
 * Preconditions: None.
 *
 * Postconditions: Updates classes on article <p> tags so any that contain
 *     current last name are assigned "foundInText".
 */
CONTEXT_TEXT.find_last_name_in_article_text = function( find_text_IN )
{
    // declare variables
    var me = "CONTEXT_TEXT.find_last_name_in_article_text";
    var last_name_text = "";
    var input_element = null;
    
    // get last name
    last_name_text = CONTEXT_TEXT.get_person_last_name_value();
    //CONTEXT_TEXT.log_message( "In " + me + "(): last name text : " + last_name_text );

    // get text-to-find-in-article text field, place value.
    input_element = $( '#' + CONTEXT_TEXT.INPUT_ID_TEXT_TO_FIND_IN_ARTICLE );
    input_element.val( last_name_text );
    
    // find in text.
    CONTEXT_TEXT.find_in_article_text( last_name_text );
    
} //-- END function CONTEXT_TEXT.find_last_name_in_article_text() --//


/**
 * Hides link to fix person name, reveals form input and buttons to fix person
 *     name, places current name in "fixed-person-name" <input>.
 *
 * Preconditions: None.
 *
 * Postconditions: Hides link to fix person name, reveals form input and buttons
 *     to fix person name, places current name in "fixed-person-name" <input>.
 */
CONTEXT_TEXT.fix_person_name = function()
{
    // declare variables
    var me = "CONTEXT_TEXT.fix_person_name";
    var fix_link_div_id = "";
    var fix_link_div = null;
    var fix_area_div_id = "";
    var fix_area_div = null;
    var input_element = null;
    
    // get div that contains link and hide() it.
    fix_link_div_id = CONTEXT_TEXT.DIV_ID_FIX_PERSON_NAME_LINK;
    fix_link_div = $( '#' + fix_link_div_id );
    fix_link_div.hide();
    
    // load name into fixed-person-name <input>.
    CONTEXT_TEXT.load_person_name_to_fix();
    
    // get div that contains actual fix area and show() it.
    fix_area_div_id = CONTEXT_TEXT.DIV_ID_FIX_PERSON_NAME;
    fix_area_div = $( '#' + fix_area_div_id );
    fix_area_div.show();

} //-- END function CONTEXT_TEXT.fix_person_name() --//


/**
 * checks to see if DataStore instance already around.  If so, returns it.
 *    If not, creates one, stores it, then returns it.
 *
 * Preconditions: None.
 *
 * Postconditions: If DataStore instance not already present in
 *    CONTEXT_TEXT.data_store, one is created and stored there before it is
 *    returned.
 */
CONTEXT_TEXT.get_data_store = function()
{
    
    // return reference
    var instance_OUT = null;
    
    // declare variables
    var me = "CONTEXT_TEXT.get_data_store";
    var my_data_store = null;
    
    // see if there is already a person store.
    my_data_store = CONTEXT_TEXT.data_store;
    if ( my_data_store == null )
    {
        
        // nope.  Make one, store it, then recurse.
        my_data_store = new CONTEXT_TEXT.DataStore();
        CONTEXT_TEXT.data_store = my_data_store;
        instance_OUT = CONTEXT_TEXT.get_data_store();
        
    }
    else
    {
        
        instance_OUT = my_data_store;
        
    }
    
    return instance_OUT;
    
} //-- END function CONTEXT_TEXT.get_data_store() --//


/**
 * Retrieves value in fixed_person_name input.  If none present, returns null.
 *
 * Preconditions: None.
 *
 * Postconditions: None
 */
CONTEXT_TEXT.get_fixed_person_name_value = function()
{
    
    // return reference
    var value_OUT = null;
    
    // declare variables
    var me = "CONTEXT_TEXT.get_fixed_person_name_value";
    var name_input_name = "";
    
    // get name of input for name from CONTEXT_TEXT.
    name_input_name = CONTEXT_TEXT.INPUT_ID_PERSON_NAME;

    // get value for that name.
    value_OUT = CONTEXT_TEXT.get_value_for_id( CONTEXT_TEXT.INPUT_ID_FIXED_PERSON_NAME, null );
    
    return value_OUT;
    
} //-- END function CONTEXT_TEXT.get_fixed_person_name_value() --//


/**
 * Looks for person ID in the AJAX person lookup.  If an ID is found there,
 *     returns that.  If not, then looks for a previous matched-person-id, which
 *     is returned if found.  If neither is found, returns null.
 *
 * Preconditions: None.
 *
 * Postconditions: None
 */
CONTEXT_TEXT.get_person_id_value = function()
{
    
    // return reference
    var value_OUT = null;
    
    // declare variables
    var me = "CONTEXT_TEXT.get_person_id_value";
    var is_person_id_ok = false;
    var ajax_person_id_element = null;
    var my_person_id = -1;
    var matched_person_id_element = null;
    
    var person_type_prop_name = "";
    var person_type_prop_info = null;
    var quote_text_prop_name = "";
    var quote_text_prop_info = null;
    var person_type = "";
    var quote_text = "";
    
    // init 
    
    // get element from AJAX person lookup that would hold selected ID.
    ajax_person_id_element = $( '#' + CONTEXT_TEXT.INPUT_ID_AJAX_ID_PERSON );
    
    // element found?
    if ( ajax_person_id_element.length > 0 )
    {    
    
        // get person ID from element.
        my_person_id = ajax_person_id_element.val();
        
        // is it an OK string?
        is_person_id_ok = CONTEXT_TEXT.is_string_OK( my_person_id );
        if ( is_person_id_ok == true )
        {

            // looks OK (non-empty).  Convert to int and store it.
            my_person_id = parseInt( my_person_id, 10 );
            value_OUT = my_person_id;

        } //-- END check to see if person_id value present. --//
    
    } //-- END check to see if id_person element present in HTML. --//
    
    //------------------------------------------------------------------------//
    // got a person ID?
    is_person_id_ok = CONTEXT_TEXT.is_integer_OK( value_OUT, 1 )
    if ( is_person_id_ok == false )
    {
        
        // no ID.  Try to retrieve from hidden "matched-person-id" input.
        matched_person_id_element = $( '#' + CONTEXT_TEXT.INPUT_ID_MATCHED_PERSON_ID );
        my_person_id = matched_person_id_element.val()
        
        // is it an OK string?
        is_person_id_ok = CONTEXT_TEXT.is_string_OK( my_person_id );
        if ( is_person_id_ok == true )
        {
            
            // there is a value from a previous match.  Convert to int, store.
            my_person_id = parseInt( my_person_id, 10 );
            value_OUT = my_person_id;

        } //-- END check to see if previous match person ID present. --//
        
    } //-- END check to see if person ID set from ajax lookup form --//
    
    return value_OUT;
    
} //-- END function CONTEXT_TEXT.get_person_id_value() --//


/**
 * Retrieves value in person_name input.  If one found, parses on spaces and
 *     returns the last token in the list ("last name"). If nothing present,
 *     returns null.
 *
 * Preconditions: None.
 *
 * Postconditions: None
 */
CONTEXT_TEXT.get_person_last_name_value = function()
{
    
    // return reference
    var value_OUT = null;
    
    // declare variables
    var me = "CONTEXT_TEXT.get_person_last_name_value";
    var current_person_name = "";
    var is_name_OK = false;
    var name_part_list = null;
    var name_part_count = -1;
    
    // get person name.
    current_person_name = CONTEXT_TEXT.get_person_name();

    // is name OK?
    is_name_OK = CONTEXT_TEXT.is_string_OK( current_person_name );
    if ( is_name_OK == true )
    {
        
        // got name. split into a list of tokens on space.
        name_part_list = current_person_name.split( " " );
        
        // got anything?
        if ( name_part_list != null )
        {
            
            // how many matches?
            name_part_count = name_part_list.length;
            if ( name_part_count > 0 )
            {
                
                // more than one.  Take last one in the list.
                value_OUT = name_part_list[ name_part_count - 1 ];
                
            }
            else
            {
                
                // nothing in list.  return null.
                value_OUT = null;
                
            } //-- END check to see if name parts exist. --//
    
        }
        else
        {
            
            // no list?  eek... return null.
            value_OUT = null;
            
        } //-- END check to see if list returned. --//
        
    }
    else
    {
        
        // not OK.  Return null.
        value_OUT = null;
        
    } //-- END check to see if name is OK. --//

    return value_OUT;
    
} //-- END function CONTEXT_TEXT.get_person_last_name_value() --//


/**
 * Retrieves value in person_name input.  If none present, returns null.
 *
 * Preconditions: None.
 *
 * Postconditions: None
 */
CONTEXT_TEXT.get_person_name = function()
{
    
    // return reference
    var value_OUT = null;
    
    // declare variables
    var me = "CONTEXT_TEXT.get_person_name";
    var fixed_name = "";
    var is_fixed_name_OK = false;
    
    // first, try to get fixed_person_name.
    fixed_name = CONTEXT_TEXT.get_fixed_person_name_value();
    is_fixed_name_OK = CONTEXT_TEXT.is_string_OK( fixed_name );
    if ( is_fixed_name_OK == false )
    {
        
        // no fixed name.  get person_name.
        value_OUT = CONTEXT_TEXT.get_person_name_value();
        
    }
    else
    {
        
        // looks like there is a fixed name.  Use it.
        value_OUT = fixed_name;
        
    }
    
    return value_OUT;
    
} //-- END function CONTEXT_TEXT.get_person_name() --//


/**
 * Retrieves value in person_name input.  If none present, returns null.
 *
 * Preconditions: None.
 *
 * Postconditions: None
 */
CONTEXT_TEXT.get_person_name_value = function()
{
    
    // return reference
    var value_OUT = null;
    
    // declare variables
    var me = "CONTEXT_TEXT.get_person_name_value";
    var name_input_name = "";
    
    // get name of input for name from CONTEXT_TEXT.
    name_input_name = CONTEXT_TEXT.INPUT_ID_PERSON_NAME;

    // get value for that name.
    value_OUT = CONTEXT_TEXT.get_value_for_id( CONTEXT_TEXT.INPUT_ID_PERSON_NAME, null );
    
    return value_OUT;
    
} //-- END function CONTEXT_TEXT.get_person_name_value() --//


/**
 * Retrieves value in quote_text input.  If none present, returns default value.
 *     If current person_type is not source, also returns empty value (no quote
 *     text for authors or subjects - they should be sources).
 *
 * Preconditions: None.
 *
 * Postconditions: None
 */
CONTEXT_TEXT.get_quote_text_value = function()
{
    
    // return reference
    var value_OUT = null;
    
    // declare variables
    var me = "CONTEXT_TEXT.get_quote_text_value";
    var person_type_prop_name = "";
    var person_type_prop_info = null;
    var quote_text_prop_name = "";
    var quote_text_prop_info = null;
    var person_type = "";
    var quote_text = "";
    
    // get property info for person_type...
    person_type_prop_name = CONTEXT_TEXT.PersonProperty_names.PERSON_TYPE;
    person_type_prop_info = CONTEXT_TEXT.Person_property_name_to_info_map[ person_type_prop_name ];
        
    // ...and quote_text.
    quote_text_prop_name = CONTEXT_TEXT.PersonProperty_names.QUOTE_TEXT;
    quote_text_prop_info = CONTEXT_TEXT.Person_property_name_to_info_map[ quote_text_prop_name ];
    
    // get quote_text from form (so avoid recursive calls to this function).
    quote_text = quote_text_prop_info.get_value_from_form();
    
    // get person_type
    person_type = person_type_prop_info.get_value();
    
    // only return quote text if person type is "source".
    if ( person_type == CONTEXT_TEXT.PERSON_TYPE_SOURCE )
    {
        
        // it is a source - save quote text.
        value_OUT = quote_text;

    } //-- END check to see if person is "source". --//
    
    return value_OUT;
    
} //-- END function CONTEXT_TEXT.get_quote_text_value() --//


/**
 * Accepts index to person in DataStore.person_array.  Retrieves person instance
 *     at the index passed in.  If not null, calls Person.populate_form() to
 *     put its values into the form.
 */
CONTEXT_TEXT.load_person_into_form = function( person_index_IN )
{
    
    // declare variables
    var me = "CONTEXT_TEXT.load_person_into_form";
    var is_index_OK = false;
    var my_data_store = null;
    var my_person_instance = null;
    var status_message_array = [];
    
    CONTEXT_TEXT.log_message( "In " + me + "(): person_index_IN = " + person_index_IN );
    
    // see if index is OK.
    is_index_OK = CONTEXT_TEXT.is_integer_OK( person_index_IN );
    if ( is_index_OK == true )
    {
        
        // retrieve data store.
        my_data_store = CONTEXT_TEXT.get_data_store();
        
        // get person at index passed in.
        my_person_instance = my_data_store.get_person_at_index( person_index_IN );
        
        // call populate_form()
        my_person_instance.populate_form();
        
        // place last name in text-to-find-in-article <input>, then try to find
        //     in text.
        CONTEXT_TEXT.find_last_name_in_article_text();
    }
    else
    {
       
        // make status message array (empty message will clear status area).
        status_message_array = [];
        status_message_array.push( "Could not load person data - invalid index ( \"" + person_index_IN + "\" )" );
    
        // output it.
        CONTEXT_TEXT.output_status_messages( status_message_array );
 
    }
    
} //-- END function CONTEXT_TEXT.load_person_into_form() --//
 
 
/**
 * Loads current person_name value into field where it can be manually fixed.
 */
CONTEXT_TEXT.load_person_name_to_fix = function()
{
    
    // declare variables
    var name_text = "";
    var input_element = null;

    // get selection
    name_text = CONTEXT_TEXT.get_person_name_value();
    //CONTEXT_TEXT.log_message( "source text : " + source_text );

    // get fixed_person_name text field,  place value there.
    input_element = $( '#' + CONTEXT_TEXT.INPUT_ID_FIXED_PERSON_NAME );
    input_element.val( name_text );
    
} //-- END function CONTEXT_TEXT.load_person_name_to_fix() --//


/**
 * Gets fixed_person_name value.  If not empty, enables the fix_person_name
 *     part of the form, then places value there.  If empty, puts default in
 *     <input>, but does not enable the field by default.
 */
CONTEXT_TEXT.load_value_fixed_person_name = function( person_IN )
{
    // declare variables
    var me = "CONTEXT_TEXT.load_fixed_person_name_value";
    var fixed_person_name_property_name = null;
    var fixed_person_name_property_info = null;
    var input_id = "";
    var fixed_person_name = "";
    var value_to_load = "";

    // get property info for fixed-person-name.
    fixed_person_name_property_name = CONTEXT_TEXT.PersonProperty_names.FIXED_PERSON_NAME;
    fixed_person_name_property_info = CONTEXT_TEXT.Person_property_name_to_info_map[ fixed_person_name_property_name ];
    
    // and get input_id of input for this field.
    input_id = fixed_person_name_property_info.input_id;
    default_value = fixed_person_name_property_info.default_value;

    // get fixed-person-name value
    fixed_person_name = person_IN.fixed_person_name;

    // got a value?
    if ( ( fixed_person_name != null ) && ( fixed_person_name != "" ) )
    {
        // yes - reveal field to fix person name if present.
        CONTEXT_TEXT.fix_person_name();
        
        // store value in element
        value_to_load = fixed_person_name;
    }
    else
    {
        // no value in instance, so set to default.
        value_to_load = default_value;
    } //-- END check to see if we have value --//
    
    // place value_to_load in input.
    CONTEXT_TEXT.set_value_for_id( input_id, value_to_load );
    
} //-- END function CONTEXT_TEXT.load_value_fixed_person_name() --//



/**
 * Gets fixed_person_name value.  If not empty, enables the fix_person_name
 *     part of the form, then places value there.  If empty, puts default in
 *     <input>, but does not enable the field by default.
 */
CONTEXT_TEXT.load_value_person_id = function( person_IN )
{
    // declare variables
    var me = "CONTEXT_TEXT.load_value_person_id";
    var person_id_property_name = null;
    var person_id_property_info = null;
    var input_id = "";
    var person_id = "";
    var value_to_load = "";
    var is_value_ok = false;
    
    // declare variables - additional HTML updates.
    var temp_element = null;
    var temp_li = null;
    var temp_html = "";
    var temp_ul = null;

    // get property info for person_id.
    person_id_property_name = CONTEXT_TEXT.PersonProperty_names.PERSON_ID;
    person_id_property_info = CONTEXT_TEXT.Person_property_name_to_info_map[ person_id_property_name ];
    
    // and get input_id of input for this field.
    input_id = person_id_property_info.input_id;
    default_value = person_id_property_info.default_value;

    // get fixed-person-name value
    person_id = person_IN.person_id;
    
    // is it OK?
    is_value_OK = CONTEXT_TEXT.is_integer_OK( person_id, 1 );
    if ( is_value_OK == true )
    {
        // store value in element
        value_to_load = person_id;
        CONTEXT_TEXT.set_value_for_id( input_id, value_to_load );

        // get <div> inside person lookup area where we display that there is an ID.
        temp_element = $( '#' + CONTEXT_TEXT.DIV_ID_LOOKUP_PERSON_EXISTING_ID );
        
        // empty it.
        temp_element.empty();
        
        // create <li>
        temp_li = $( "<li></li>" );
        
        // place text in <li>.
        temp_li.text( "Selected Person ID is " + value_to_load + ". " );
        
        // add button to clear existing ID.
        temp_html = $( "<input type=\"button\" id=\"clear-matched-id\" name=\"clear-matched-id\" value=\"<== Remove\" onclick=\"CONTEXT_TEXT.clear_matched_person_id( '' )\" />" );
        temp_li.append( temp_html );

        // make a <ul> and add the <li> to it.
        temp_ul = $( "<ul></ul>" );
        temp_ul.append( temp_li );        

        // append it all to the HTML element in question.        
        temp_element.append( temp_ul );
    }
    else
    {
        // no value in instance, so set to default value.
        value_to_load = default_value;
        CONTEXT_TEXT.set_value_for_id( input_id, value_to_load );
    } //-- END check to see if we have value --//

} //-- END function CONTEXT_TEXT.load_value_person_id() --//



/**
 * Gets person_type value.  If not empty, enables the fix_person_name
 *     part of the form, then places value there.  If empty, puts default in
 *     <input>, but does not enable the field by default.
 */
CONTEXT_TEXT.load_value_person_type = function( person_IN )
{
    // declare variables
    var me = "CONTEXT_TEXT.load_value_person_type";
    var person_type_property_name = null;
    var person_type_property_info = null;
    var input_id = "";
    var person_type = "";
    var value_to_load = "";
    var temp_value = "";

    // get property info for fixed-person-name.
    person_type_property_name = CONTEXT_TEXT.PersonProperty_names.PERSON_TYPE;
    person_type_property_info = CONTEXT_TEXT.Person_property_name_to_info_map[ person_type_property_name ];
    
    // and get input_id of input for this field.
    input_id = person_type_property_info.input_id;
    default_value = person_type_property_info.default_value;

    // get person_type
    person_type = person_IN.person_type;

    // got a value?
    if ( ( person_type != null ) && ( person_type != "" ) )
    {
        // yes - store value in element
        value_to_load = person_type;
    }
    else
    {
        // no value in instance, so set to default.
        value_to_load = default_value;
    } //-- END check to see if we have value --//
    
    // place value_to_load in input.
    temp_value = CONTEXT_TEXT.set_selected_value_for_id( input_id, value_to_load );
    
    // process the selected person type:
    CONTEXT_TEXT.process_selected_person_type();
    
    // sanity check
    if ( temp_value != person_type )
    {
        
        // the value of the select is not what we passed to it.
        CONTEXT_TEXT.log_message( "In " + me + "(): value for select with ID = " + input_id + " is \"" + temp_value + "\"; should be = \"" + person_type + "\"" );
        
    }
    
} //-- END function CONTEXT_TEXT.load_value_person_type() --//


/**
 * Event function that is called when coder is finished coding a particular
 *    person and is ready to add him or her to the list of persons in the
 *    article.
 *
 * Preconditions: Person coding form should be filled out as thoroughly as
 *    possible.  At the least, must have a person name.  If none present, the
 *    person is invalid, will not be accepted.
 *
 * Postconditions: If person accepted, after this function is called, the
 *    person will be added to the internal structures to list and map persons,
 *    and will also be added to the list of persons who have been coded so far.
 */
CONTEXT_TEXT.process_selected_person_type = function()
{
    // declare variables
    var me = "CONTEXT_TEXT.process_selected_person_type";
    var selected_value = "";
    var p_source_quote_element = null;

    CONTEXT_TEXT.log_message( "In " + me + "(): Process Selected Person Type!" );
    
    // get select element.
    selected_value = CONTEXT_TEXT.get_selected_value_for_id( 'person-type' );
    
    // get "textarea-source-quote-text" <p> tag.
    p_source_quote_element = $( '#textarea-source-quote-text' );
    
    // is it "source"?
    if ( selected_value == CONTEXT_TEXT.PERSON_TYPE_SOURCE )
    {
        
        // it is "source".  show() the "textarea-source-quote-text" <p> tag.
        p_source_quote_element.show();
        
    }
    else
    {
        
        // it is not "source".  hide() the "textarea-source-quote-text" <p> tag.
        p_source_quote_element.hide();
        
    } //-- END check to see if person type is "source" or not. --//
    
} //-- END function CONTEXT_TEXT.process_selected_person_type() --#


/**
 * Event function that is called when coder is finished coding a particular
 *    person and is ready to add him or her to the list of persons in the
 *    article.
 *
 * Preconditions: Person coding form should be filled out as thoroughly as
 *    possible.  At the least, must have a person type and name.  If either not
 *    present, the person is invalid, will not be accepted.
 *
 * Postconditions: If person accepted, after this function is called, the
 *    person will be added to the internal structures to list and map persons,
 *    and will also be added to the list of persons who have been coded so far.
 */
CONTEXT_TEXT.process_person_coding = function()
{
    // declare variables
    var me = "CONTEXT_TEXT.process_person_coding";
    var form_element = null;
    var person_instance = null;
    var status_message_array = [];
    var status_message_count = -1;
    var work_element = null;
    var existing_person_index = -1;
    var status_string = "";
    var data_store = null;
    var person_message_array = [];
    var person_error_count = -1;

    CONTEXT_TEXT.log_message( "In " + me + "(): PROCESS PERSON CODING!!!" );
    
    // get form element.
    form_element = $( '#' + CONTEXT_TEXT.DIV_ID_PERSON_CODING );
    
    // create Person instance.
    person_instance = new CONTEXT_TEXT.Person();
    
    // populate it from the form.
    status_message_array = person_instance.populate_from_form( form_element );
    
    // valid?
    status_message_count = status_message_array.length;
    if ( status_message_count == 0 )
    {
        
        // valid.
        CONTEXT_TEXT.log_message( "In " + me + "(): Valid person.  Adding to DataStore." );
        
        // get person store
        data_store = CONTEXT_TEXT.get_data_store();
        
        // add person
        person_message_array = data_store.process_person( person_instance );
        
        // errors?
        person_error_count = person_message_array.length;
        if ( person_error_count == 0 )
        {
            
            // no errors.

            // output person store
            CONTEXT_TEXT.display_persons();
                    
            // clear the coding form.
            CONTEXT_TEXT.clear_coding_form( "Processed: " + person_instance.to_string() );

        }
        else
        {
            
            // errors - output messages.
            CONTEXT_TEXT.output_status_messages( person_message_array );
            
        } //-- END check for errors adding person to DataStore. --//
        
    }
    else
    {
        
        // not valid - for now, add message to overall status message.
        status_message_array.push( "Person not valid." );
        
    }
    
    // got any messages?
    status_message_count = status_message_array.length;
    if ( status_message_count > 0 )
    {
        
        // yes, there are messages.  Output them.
        CONTEXT_TEXT.output_status_messages( status_message_array );
        
    } //-- END check to see if messages --//    
    
} //-- END function CONTEXT_TEXT.process_person_coding() --#


/**
 * Accepts the index of a person in the DataStore's person_array that one
 *    wants removed.  Gets the DataStore and calls the
 *    remove_person_at_index() method on it to remove the person, then calls
 *    CONTEXT_TEXT.display_persons() to repaint the list of persons.  If any
 *    status messages, outputs them at the end using
 *    CONTEXT_TEXT.output_status_messages()
 */
CONTEXT_TEXT.remove_person = function( person_index_IN )
{
    
    // declare variables
    var me = "CONTEXT_TEXT.remove_person";
    var selected_index = -1;
    var is_index_OK = false;
    var status_message_array = [];
    var status_message_count = -1;
    var data_store = null;
    var person_remove_message_array = [];
    var person_remove_error_count = -1;

    // make sure index is an integer.
    selected_index = parseInt( person_index_IN );
    
    // got an index?
    is_index_OK = CONTEXT_TEXT.is_integer_OK( selected_index, 0 );
    if ( is_index_OK == true )
    {
        
        // get person store
        data_store = CONTEXT_TEXT.get_data_store();
        
        // remove person
        person_remove_message_array = data_store.remove_person_at_index( selected_index );
        
        CONTEXT_TEXT.log_message( "In " + me + "(): Person Store: " + JSON.stringify( data_store ) );
        
        // errors?
        person_remove_error_count = person_remove_message_array.length;
        if ( person_remove_error_count == 0 )
        {
            
            // no errors.

            // output person store
            CONTEXT_TEXT.display_persons();
            
            // add status message.
            status_message_array.push( "Removed person at index " + selected_index );
            
        }
        else
        {
            
            // errors - append to status_message_array.
            status_message_array = status_message_array.concat( person_remove_message_array );
            
        } //-- END check for errors removing person from DataStore. --//
        
    }
    else
    {
        
        // not valid - for now, output message(s).
        status_message_array.push( "Index value of " + selected_index + " is not valid.  Can't remove person." );
        
    }
    
    // got any messages?
    status_message_count = status_message_array.length;
    if ( status_message_count > 0 )
    {
        
        // yes, there are messages.  Output them.
        CONTEXT_TEXT.output_status_messages( status_message_array );
        
    } //-- END check to see if messages --//
        
} //-- END function CONTEXT_TEXT.remove_person --//


/**
 * Creates basic form with a submit button whose onsubmit event calls
 *    CONTEXT_TEXT.render_coding_form_inputs.  On submit, that method pulls the
 *    data needed to submit together and places it in hidden <inputs> associated
 *    with this form, and if no problems, returns true so form submits.  Returns
 *    <form> jquery element, suitable for adding to an element on the page.
 *
 * Postconditions: none.
 */
CONTEXT_TEXT.render_coding_form = function()
{

    // return reference
    form_element_OUT = true;
    
    // declare variables
    form_HTML_string = "";
    
    // build form HTML string.
    form_HTML_string += '<form method="post" name="submit-article-coding" id="submit-article-coding">';
    form_HTML_string += '<input type="submit" value="Submit Article Coding" name="input-submit-article-coding" id=input-submit-article-coding" onsubmit="CONTEXT_TEXT.render_coding_form_inputs( this )" />';
    form_HTML_string += '</form>';
    
    // render into JQuery element.
    form_element_OUT = $( form_HTML_string );
    
    return form_element_OUT;
   
} //-- END function to render form to submit coding.


/**
 * Accepts <form> jquery instance.  Adds inputs to the form to hold serialized
 *    JSON object of the DataStore, the results of the coding.  Designed to
 *    be used as a <form>'s onsubmit event handler.
 *
 * Postconditions: Will return false, causing submit to abort, if errors or
 *    warnings.  If returns false, also outputs messages of why using
 *    output_status_messages().
 *
 * References:
 *    - http://stackoverflow.com/questions/6099301/dynamically-adding-html-form-field-using-jquery
 *    - http://www.w3schools.com/js/js_popup.asp
 *
 * @param {jquery:element} form_IN - <form> we are going to append inputs to.
 */
CONTEXT_TEXT.render_coding_form_inputs = function( form_IN )
{

    // return reference
    do_submit_OUT = true;
    
    // declare variables
    me = "CONTEXT_TEXT.render_coding_form_inputs";
    form_element = null;
    my_data_store = null;
    author_count = -1;
    is_author_count_valid = false;
    source_count = -1;
    is_source_count_valid = false;
    do_confirm_submit = true;
    ok_to_submit = false;
    data_store_json = "";
    data_store_json_input_element = null;
    submit_button_element = null;
        
    // convert form DOM element to JQuery object.
    //form_element = $( form_IN )
    
    // get person store
    my_data_store = CONTEXT_TEXT.get_data_store();
    
    //------------------------------------------------------------------------//
    // validation
    //------------------------------------------------------------------------//

    // Is there at least one author?
    author_count = my_data_store.get_person_count( CONTEXT_TEXT.PERSON_TYPE_AUTHOR );
    if ( author_count <= 0 )
    {
        
        // no author - see if that is correct.
        is_author_count_valid = confirm( "No authors coded.  Is this correct?" );
        if ( is_author_count_valid == false )
        {
            
            // oops - forgot to code author.  Back to form.
            do_submit_OUT = false;
            CONTEXT_TEXT.log_message( "In " + me + "(): forgot to code author - back to form!" );
            
        } //-- END check to see if no authors --//
        
    } //-- END check to see if author count is 0 --//
    
    // canceled?
    if ( do_submit_OUT == true )
    {
        
        // not canceled yet, keep checking...
        
        // Is there at least one source?
        source_count = my_data_store.get_person_count( CONTEXT_TEXT.PERSON_TYPE_SOURCE );
        if ( source_count <= 0 )
        {
            
            // no sources - see if that is correct.
            is_source_count_valid = confirm( "No sources coded.  Is this correct?" );
            if ( is_source_count_valid == false )
            {
                
                // oops - forgot to code sources.  Back to form.
                do_submit_OUT = false;
                CONTEXT_TEXT.log_message( "In " + me + "(): forgot to code sources - back to form!" );
                
            } //-- END check to see if no sources --//
            
        } //-- END check to see if source count is 0 --//

    } //-- END check to see if we are already canceled, so don't need to keep checking --//
    
    // !TODO - check for sources that don't have quote selected?
    
    // canceled?
    if ( do_submit_OUT == true )
    {
        
        // not canceled yet, keep checking...
        
        // confirm submit?
        if ( do_confirm_submit == true )
        {
            
            // We are confirming submit - ask for confirmation.
            ok_to_submit = confirm( "OK to submit coding?" );
            if ( ok_to_submit == false )
            {
                
                // Not ready to submit just yet.  Back to form.
                do_submit_OUT = false;
                CONTEXT_TEXT.log_message( "In " + me + "(): User not ready to submit.  Back to the form!" );
                
            } //-- END check to see if ready to submit --//
            
        } //-- END check to see if we are confirming submission --//
        
    } //-- END check to see if we are already canceled, so don't need to keep checking --//
    
    // no sense doing anything more if we aren't submitting.
    if ( do_submit_OUT == true )
    {
        
        // need JSON of DataStore.
        data_store_json = JSON.stringify( my_data_store );
        
        // add it to the hidden input:
        // <input id="id_data_store_json" name="data_store_json" type="hidden">
        
        // get <input> element
        input_id_string = "#" + CONTEXT_TEXT.INPUT_ID_DATA_STORE_JSON;
        data_store_json_input_element = $( input_id_string );

        // make sure we found the element.
        if ( data_store_json_input_element.length > 0 )
        {
            
            // got it.  Place JSON in it.
            data_store_json_input_element.val( data_store_json );
            
            // explicitly set to true.
            do_submit_OUT = true;

            // do_submit_OUT = false;
            if ( do_submit_OUT == false )
            {
                
                CONTEXT_TEXT.log_message( "In " + me + "(): Placed the following JSON in \"" + input_id_string + "\"" );
                CONTEXT_TEXT.log_message( "In " + me + "(): " + data_store_json );            

            } //-- END check to see if we output debug.
            
        }
        else
        {
            
            // did not find <input> element.  Log message, don't submit.
            do_submit_OUT = false;
            CONTEXT_TEXT.log_message( "In " + me + "(): Could not find input for selector: \"" + input_id_string + "\".  No place to put JSON.  Back to form!" );
            
        } //-- END check to see if we found input element. --//
        
    } //-- END check to see if validation was OK before we actually populate inputs. --//
    
    // are we allowing submit?
    if ( do_submit_OUT == true )
    {
        
        // we are.  Retrieve submit button, disable it, and then change text
        //    to say "Please wait...".
        submit_button_element = $( "#" + CONTEXT_TEXT.INPUT_ID_SUBMIT_ARTICLE_CODING );
        submit_button_element.prop( 'disabled', true );
        submit_button_element.val( CONTEXT_TEXT.ARTICLE_CODING_SUBMIT_BUTTON_VALUE_WAIT );
        
    } //-- END check to see if we are submitting. --//
    
    return do_submit_OUT;
   
} //-- END function to render form to submit coding.


//----------------------------------------------------------------------------//
// !====> object definitions
//----------------------------------------------------------------------------//


//=====================//
// !--> DataStore
//=====================//

// DataStore constructor

/**
 * Stores and indexes persons in an article.
 * @constructor
 */
CONTEXT_TEXT.DataStore = function()
{
    // instance variables
    this.person_array = [];
    this.next_person_index = 0;
    this.name_to_person_index_map = {};
    this.id_to_person_index_map = {};
    
    // instance variables - status messages
    this.status_message_array = [];
    this.latest_person_index = -1;
}

// CONTEXT_TEXT.DataStore methods

/**
 * Accepts a Person instance.  First, checks to see if the person is valid.
 *    If no, returns validation messages as error.  If person has a person ID,
 *    checks to see if the ID is already a key in this.id_to_person_index_map.
 *    If so, returns an error.  If no ID, checks to see if name is already in
 *    this.name_to_person_index_map.  If so, returns an error.  If no errors,
 *    then adds the person to all the appropriate places:
 *    - this.person_array
 *    - this.name_to_person_index_map with person_name as key, index of person
 *       in the person_array as the value.
 *    - if person ID, this.id_to_person_index_map with person ID as key, index
 *       of person in the person_array as the value.
 */
CONTEXT_TEXT.DataStore.prototype.add_person = function( person_IN )
{
    
    // return reference
    var status_array_OUT = [];
    
    // declare variables.
    var me = "CONTEXT_TEXT.DataStore.prototype.add_person"
    var is_ok_to_add = true;
    var validation_status_array = [];
    var validation_status_count = -1;
    var has_person_id = false
    var my_person_id = -1;
    var is_person_id_ok = false;
    var person_id_index = -1;
    var my_person_name = "";
    var is_person_name_OK = false;
    var person_name_index = -1;
    var person_index = -1;
    var name_map_status_array = [];
    var id_map_status_array = [];
    
    CONTEXT_TEXT.log_message( "Top of " + me )
    
    // make sure we have a person.
    if ( ( person_IN !== undefined ) && ( person_IN != null ) )
    {
        
        // got a person.  Is it valid?
        validation_status_array = person_IN.validate();
        validation_status_count = validation_status_array.length;
        if ( validation_status_count == 0 )
        {
            
            // valid.  Got a person ID?
            my_person_id = person_IN.person_id;
            is_person_id_ok = CONTEXT_TEXT.is_integer_OK( my_person_id, 1 );
            if ( is_person_id_ok == true )
            {
                
                // got a person ID.
                has_person_id = true;
                
                // Is that ID already in map of IDs to array indices?
                person_id_index = this.get_index_for_person_id( my_person_id );
                if ( person_id_index >= 0 )
                {
                    
                    // already in map...  Error.
                    is_ok_to_add = false;
                    status_array_OUT.push( "Person ID " + my_person_id + " already present in DataStore." );
                    
                }
                
            } //-- END check to see if person ID already present. --//
            
            // Got a person name?
            my_person_name = person_IN.person_name;
            is_person_name_OK = CONTEXT_TEXT.is_string_OK( my_person_name );
            if ( is_person_name_OK == true )
            {
                
                // person name present (as it should be at this point).  See if
                //    this name is already in the DataStore.
                person_name_index = this.get_index_for_person_name( my_person_name );
                if ( person_name_index >= 0 )
                {
                    
                    // already in map...  Error.
                    is_ok_to_add = false;
                    status_array_OUT.push( "Person name " + my_person_name + " already present in DataStore." );
                    
                } //-- END check to see if person's name already mapped to a person --//
                
            }
            else
            {
                
                // no name! ERROR.
                is_ok_to_add = false;
                status_array_OUT.push( "Person has no name.  Not sure how you got this far, but error." );
                
            } //-- END check to see if person's name present. --//

            // OK to add?
            if ( is_ok_to_add == true )
            {
                
                // no errors so far...  Add person to array.
                person_index = this.add_person_to_array( person_IN );
                
                // got an index back?
                if ( person_index > -1 )
                {
                    
                    // got one.  Now, add to map of name and ID to index.
                    
                    // add to name map.
                    name_map_status_array = this.update_person_in_name_map( person_IN, person_index );
                    
                    // any errors?
                    if ( name_map_status_array.length > 0 )
                    {
                        
                        // yes.  Add to status array, fall out.
                        status_array_OUT = status_array_OUT.concat( name_map_status_array );
                    
                    }
                    else //-- added to name map just fine. --//
                    {
                        
                        // got a person ID?
                        if ( has_person_id == true )
                        {
                            
                            // yes.  Add mapping of person ID to person array
                            //    index.
                            id_map_status_array = this.update_person_in_person_id_map( person_IN, person_index );
                            
                            // any errors?
                            if ( id_map_status_array.length > 0 )
                            {
                                
                                // yes.  Add to status array, fall out.
                                status_array_OUT = status_array_OUT.concat( id_map_status_array );
                            
                            } //-- END check to see if errors from adding to id map --//
                            
                        } //-- END check to see if has person ID --//
                        
                    } //-- END check to see if errors adding person to name map. --//
                    
                }
                else
                {
                
                    // no.  Interesting.  Error.
                    status_array_OUT.push( "attempt to add person to Array resulted in no index.  Not good." );
                    
                } //-- END check to see if index of person greater than -1. --//
                
            } //-- END check to see if OK to add? --//
            
        }
        else
        {

            // not valid.  Error.  Concat validation errors with any other
            //    errors.
            status_array_OUT = status_array_OUT.concat( validation_status_array );

        } //-- END check to see if person is valid. --//
        
    }
    else
    {
        
        // no person passed in.  Error.
        status_array_OUT.push( "No person instance passed in." );
        
    } //-- END check to see if person passed in. --//
    
    return status_array_OUT;
    
} //-- END CONTEXT_TEXT.DataStore method add_person() --//


/**
 * Accepts a Person instance - adds it to the person array at the next index.
 *    Returns the index.  Person is not checked to see if it is a duplicate.
 *    At this point, it is too late for that.  You should have checked earlier.
 *
 * Assumptions: We always push persons onto array, never remove.  Index should
 *    equal this.person_array.length - 1, but keep separate variables as well
 *    as a sanity check.
 *
 * @param {Person} person_IN - person we want to add to the person array.
 * @returns {int} - index of person in person array.
 */
CONTEXT_TEXT.DataStore.prototype.add_person_to_array = function( person_IN )
{
    
    // return reference
    var index_OUT = -1;
    
    // declare variables
    var me = "CONTEXT_TEXT.DataStore.prototype.add_person_to_array";
    var my_person_array = [];
    var my_next_index = -1;
    var my_latest_index = -1;
    var person_array_length = -1;
    
    // got a person?
    if ( ( person_IN !== undefined ) && ( person_IN != null ) )
    {
        
        // yes - get relevant variables.
        my_person_array = this.person_array;
        my_next_index = this.next_person_index;
        my_latest_index = this.latest_person_index;
    
        // push person onto array.
        my_person_array.push( person_IN );
        
        // increment next index, make sure it equals length - 1.
        my_next_index += 1;
        person_array_length = my_person_array.length;
        if ( my_next_index != person_array_length )
        {
            
            // hmmm... Disconnect.  Next index should equal length of current
            //    array since arrays are 0-indexed and we only ever add one.
            //    Output alert.
            CONTEXT_TEXT.log_message( "In " + me + "(), next index ( " + my_next_index + " ) not equal to array length ( " + person_array_length + " )." );
            
        }
                    
        // Store next and latest values based on array length.
        this.next_person_index = person_array_length;
        
        // return index of length of array minus 1.
        index_OUT = person_array_length -1;
        this.latest_person_index = index_OUT;
        
        // and store index in person instance.
        person_IN.person_index = index_OUT;

    }
    else
    {
        
        // no.  Return -1.
        index_OUT = -1;
        
    } //-- END check to see if person instance.
    
    return index_OUT;
    
} //-- END CONTEXT_TEXT.DataStore method add_person_to_array() --//


/**
 * Accepts a person ID - Checks to see if ID is a key in the map of person IDs
 *    to indexes in the master person array.  If so, returns that index.  If
 *    not, returns -1.
 *
 * @param {int} person_id_IN - person ID of person we want to find in person
 *    array.
 * @returns {int} - index of person in person array, or -1 if person ID not
 *    found.
 */
CONTEXT_TEXT.DataStore.prototype.get_index_for_person_id = function( person_id_IN )
{
    
    // return reference.
    var index_OUT = -1;
    
    // declare variables
    var is_person_id_ok = false;
    var id_to_index_map = null;
    var is_in_map = false;
    
    // got an ID?
    is_person_id_ok = CONTEXT_TEXT.is_integer_OK( person_id_IN, 1 );
    if ( is_person_id_ok == true )
    {
        
        // get id_to_index_map.
        id_to_index_map = this.id_to_person_index_map;
        
        // see if ID passed in is a key in this.id_to_person_index_map.hasOwnProperty( my_person_id );
        is_in_map = id_to_index_map.hasOwnProperty( person_id_IN );
        if ( is_in_map == true )
        {
            
            // it is in the person store.  retrieve index for this person ID.
            index_OUT = id_to_index_map[ person_id_IN ];
            
        }
        else
        {
            
            // not in map.  Return -1.
            index_OUT = -1;
            
        } //-- END check to see if person ID is in ID-to-index map.
        
    }
    else
    {
        
        // no ID passed in.  Return -1.
        index_OUT = -1;
        
    } //-- END check to see if ID passed in. --//

    return index_OUT;

} //-- END CONTEXT_TEXT.DataStore method get_index_for_person_id() --//


/**
 * Accepts a person name - Checks to see if name string is a key in the map of
 *    person names to indexes in the master person array.  If so, returns that
 *    index.  If not, returns -1.
 *
 * @param {string} person_name_IN - name string for person we want to find in
 *    person array.
 * @returns {int} - index of person in person array, or -1 if person name not
 *    found.
 */
CONTEXT_TEXT.DataStore.prototype.get_index_for_person_name = function( person_name_IN )
{
    
    // return reference.
    var index_OUT = -1;
    
    // declare variables
    var is_person_name_OK = false;
    var name_to_index_map = null;
    var is_in_map = false;
    
    // got a name?
    is_person_name_OK = CONTEXT_TEXT.is_string_OK( person_name_IN );
    if ( is_person_name_OK == true )
    {

        // get id_to_index_map.
        name_to_index_map = this.name_to_person_index_map;
        
        // see if ID passed in is a key in this.id_to_person_index_map.hasOwnProperty( my_person_id );
        is_in_map = name_to_index_map.hasOwnProperty( person_name_IN );
        if ( is_in_map == true )
        {
            
            // it is in the person store.  retrieve index for this person ID.
            index_OUT = name_to_index_map[ person_name_IN ];
            
        }
        else
        {
            
            // nope.  Return -1.
            index_OUT = -1;
            
        }
        
    }
    else
    {
        
        // no name passed in.  Return -1.
        index_OUT = -1;
        
    }

    return index_OUT;

} //-- END CONTEXT_TEXT.DataStore method get_index_for_person_name() --//


/**
 * Accepts an index into the person array - Checks to see if index is present
 *    in master person array, if so, returns what is in that index.  If not,
 *    returns null.
 *
 * @param {int} index_IN - index in person array whose contents we want.
 * @returns {CONTEXT_TEXT.Person} - instance of person at the index passed in.
 */
CONTEXT_TEXT.DataStore.prototype.get_person_at_index = function( index_IN )
{
    
    // return reference.
    var person_OUT = null;
    
    // declare variables
    var is_index_OK = false;
    var my_person_array = -1;
    
    // got an index?
    is_index_OK = CONTEXT_TEXT.is_integer_OK( index_IN, 0 );
    if ( is_index_OK == true )
    {
        
        // I think so...  Get person array
        my_person_array = this.person_array;
        
        //  check to see if index present.
        person_OUT = my_person_array[ index_IN ];
        
        // is it undefined?
        if ( person_OUT === undefined )
        {
            
            // it is.  For this function, return null instead.
            person_OUT = null;
            
        } //-- END check to see if undefined --//
        
    }
    else
    {
        
        // no valid index - error - return null
        person_OUT = null;
        
    } //-- END check to see if valid index passed in. --//
    
    return person_OUT;

} //-- END CONTEXT_TEXT.DataStore method get_person_at_index() --//


/**
 * Accepts a person ID - Checks to see if index in master person array tied to
 *    the person ID.  If so, retrieves person at that index and returns it.  If
 *    not, returns null.
 *
 * @param {string} person_name_IN - name string of person we want to find in
 *    person array.
 * @returns {CONTEXT_TEXT.Person} - instance of person related to the person ID passed in.
 */
CONTEXT_TEXT.DataStore.prototype.get_person_count = function( person_type_IN )
{
    
    // return reference.
    var count_OUT = 0;
    
    // declare variables
    var me = "CONTEXT_TEXT.DataStore.prototype.get_person_count";
    var is_person_type_OK = false;
    var person_type = null;
    var my_person_array = null;
    var person_array_length = -1;
    var person_index = -1;
    var person_counter = -1;
    var current_person = -1;
    var current_person_type = "";
    
    // got a type?
    is_person_type_OK = CONTEXT_TEXT.is_string_OK( person_type_IN );
    if ( is_person_type_OK == true )
    {

        // yes.  store it.
        person_type = person_type_IN;
        
    }
    else
    {
        
        // no - set to null.
        person_type = null;
        
    } //-- END check to see if person type populated. --//
    
    // get person array.
    my_person_array = this.person_array;
    
    // loop over array.
    person_array_length = my_person_array.length;
    person_counter = 0;
    for( person_index = 0; person_index < person_array_length; person_index++ )
    {
        
        // increment counter
        person_counter += 1;
        
        // get item at current index.
        current_person = my_person_array[ person_index ];
        
        // is it null?
        if ( current_person != null )
        {
            
            // not null.  Do we have a type?
            if ( person_type != null )
            {
                
                // we are limiting to a particular person type.  Get person's
                //    type.
                current_person_type = current_person.person_type;
                
                // is person's type = selected type?
                if ( current_person_type == person_type )
                {
                    
                    // yes - add to count.
                    count_OUT += 1;
                    
                }
                
            }
            else
            {
                
                // no - increment count.
                count_OUT += 1;
                
            } //-- END check to see if type --//
            
        } //-- END check if person associated with current array index --//
        
    } //-- END loop over person_array --//
    
    CONTEXT_TEXT.log_message( "In " + me + "(): type = " + person_type + "; count = " + count_OUT );
    
    return count_OUT;

} //-- END CONTEXT_TEXT.DataStore method get_person_count() --//


/**
 * Accepts a person ID - Checks to see if index in master person array tied to
 *    the person ID.  If so, retrieves person at that index and returns it.  If
 *    not, returns null.
 *
 * @param {string} person_name_IN - name string of person we want to find in
 *    person array.
 * @returns {CONTEXT_TEXT.Person} - instance of person related to the person ID passed in.
 */
CONTEXT_TEXT.DataStore.prototype.get_person_for_name = function( person_name_IN )
{
    
    // return reference.
    var person_OUT = null;
    
    // declare variables
    var is_person_name_OK = false;
    var person_index = -1;
    var is_person_index_OK = false;
    
    // got a name?
    is_person_name_OK = CONTEXT_TEXT.is_string_OK( person_name_IN );
    if ( is_person_name_OK == true )
    {

        // I think so...  See if there is an entry in name map for this name.
        person_index = this.get_index_for_person_name( person_name_IN );
        
        // is person_index present, and greater than -1?
        is_person_index_OK = CONTEXT_TEXT.is_integer_OK( person_index, 0 );
        if ( is_person_index_OK == true )
        {
            
            // looks like there is an index.  Get person at that index.
            person_OUT = this.get_person_at_index( person_index );
            
        }
        else
        {
            
            // not present in map object.  Return null.
            person_OUT = null;
            
        }
        
    }
    else
    {
        
        // no name - error - return null
        person_OUT = null;
        
    }
    
    return person_OUT;

} //-- END CONTEXT_TEXT.DataStore method get_person_for_name() --//


/**
 * Accepts a person ID - Checks to see if index in master person array tied to
 *    the person ID.  If so, retrieves person at that index and returns it.  If
 *    not, returns null.
 *
 * @param {int} person_id_IN - person ID of person we want to find in person
 *    array.
 * @returns {CONTEXT_TEXT.Person} - instance of person related to the person ID passed in.
 */
CONTEXT_TEXT.DataStore.prototype.get_person_for_person_id = function( person_id_IN )
{
    
    // return reference.
    var person_OUT = null;
    
    // declare variables
    var is_person_id_ok = false;
    var person_index = -1;
    var is_person_index_OK = false;
    
    // got an ID?
    is_person_id_ok = CONTEXT_TEXT.is_integer_OK( person_id_IN, 1 );
    if ( is_person_id_ok == true )
    {
        
        // I think so...  See if there is an entry in ID map for this ID.
        person_index = this.get_index_for_person_id( person_id_IN );
        
        // is person_index present, and greater than -1?
        is_person_index_OK = CONTEXT_TEXT.is_integer_OK( person_index, 0 );
        if ( is_person_index_OK == true )
        {
            
            // looks like there is an index.  Get person at that index.
            person_OUT = this.get_person_at_index( person_index );
            
        }
        else
        {
            
            // not present in map object.  Return null.
            person_OUT = null;
            
        }
        
    }
    else
    {
        
        // no ID - error - return null
        person_OUT = null;
        
    }
    
    return person_OUT;

} //-- END CONTEXT_TEXT.DataStore method get_person_for_person_id() --//


/**
 * Checks to see if CONTEXT_TEXT.data_store_json is not null and not "".  If
 *    populated, retrieves value in variable, converts JSON string to Javascript
 *    objects, then uses those objects to populate DataStore.
 *
 * @param {int} person_id_IN - person ID of person we want to find in person
 *    array.
 * @returns {int} - index of person in person array, or -1 if person ID not
 *    found.
 */
CONTEXT_TEXT.DataStore.prototype.load_from_json = function()
{
    
    // declare variables
    var me = "CONTEXT_TEXT.DataStore.load_from_json";
    var my_data_store_json_string = "";
    var my_data_store_json = null;
    var my_next_person_index = -1;
    var my_name_to_person_index_map = {};
    var my_id_to_person_index_map = {};
    var my_status_message_array = [];
    var my_latest_person_index = -1;

    // declare variables - person processing.
    var my_person_array = [];
    var person_count = -1;
    var person_index = -1;
    var current_person_type = "";
    var current_original_person_type = "";
    var current_article_person_id = "";
    var current_person_name = "";
    var current_fixed_person_name = "";
    var current_title = "";
    var current_person_organization = "";
    var current_quote_text = "";
    var current_person_id = "";
    var current_person_index = -1;
    var current_person_data = null;
    var current_person = null;
    
    // got JSON?
    if ( ( CONTEXT_TEXT.data_store_json != null ) && ( CONTEXT_TEXT.data_store_json != "" ) )
    {
        
        // it is null.  Person already removed at this index.
        CONTEXT_TEXT.log_message( "In " + me + "(): Making sure this is running." );

        // try to parse JSON string into javascript objects.
        my_data_store_json_string = CONTEXT_TEXT.data_store_json;

        CONTEXT_TEXT.log_message( "In " + me + "(): JSON before decode: " + my_data_store_json_string );

        // decode
        my_data_store_json_string = CONTEXT_TEXT.decode_html( my_data_store_json_string );

        CONTEXT_TEXT.log_message( "In " + me + "(): JSON after decode: " + my_data_store_json_string );

        // parse to JSON objects
        my_data_store_json = JSON.parse( my_data_store_json_string );

        // use the pieces of the JSON to populate this object.
        my_person_array = my_data_store_json[ "person_array" ];
        my_next_person_index = my_data_store_json[ "next_person_index" ];
        my_name_to_person_index_map = my_data_store_json[ "name_to_person_index_map" ];
        my_id_to_person_index_map = my_data_store_json[ "id_to_person_index_map" ];
        my_status_message_array = my_data_store_json[ "status_message_array" ];
        my_latest_person_index = my_data_store_json[ "latest_person_index" ];

        // loop over person array to create and store CONTEXT_TEXT.Person
        //    instances.
        // how many we got?
        person_count = my_person_array.length;

        CONTEXT_TEXT.log_message( "In " + me + "(): person_count = " + person_count );

        // !---- person loop
        for ( person_index = 0; person_index < person_count; person_index++ )
        {

            CONTEXT_TEXT.log_message( "In " + me + "(): person_index = " + person_index );

            // get person at current index
            current_person_data = my_person_array[ person_index ];

            // get values
            current_person_type = current_person_data[ "person_type" ];
            current_original_person_type = current_person_data[ "original_person_type" ];
            current_article_person_id = current_person_data[ "article_person_id" ];
            current_person_name = current_person_data[ "person_name" ];
            current_fixed_person_name = current_person_data[ "fixed_person_name" ];
            current_title = current_person_data[ "title" ];
            current_person_organization = current_person_data[ "person_organization" ];
            current_quote_text = current_person_data[ "quote_text" ];
            current_person_id = current_person_data[ "person_id" ];
            current_person_index = current_person_data[ "person_index" ];
            current_article_person_id = current_person_data[ "article_person_id" ];

            // create and populate Person instance.
            current_person = new CONTEXT_TEXT.Person();
            
            // person type
            current_person.person_type = current_person_type;
            current_person.original_person_type = current_original_person_type;

            // ID for Article_Person descendent instance, based on person_type:
            //     Article_Subject ID if source or subject, Article_Author ID if
            //     this person is an author.
            current_person.article_person_id = current_article_person_id;
            
            // person name - are verbatim and name different?
            if ( ( current_fixed_person_name != null )
                && ( current_fixed_person_name != "" )
                && ( current_fixed_person_name != current_person_name ) )
            {
                
                // they are different - store each in their appropriate field.
                current_person.person_name = current_person_name;
                current_person.fixed_person_name = current_fixed_person_name;
                
            }
            else
            {
                
                // nothing fancy, just resting a bit.
                current_person.person_name = current_person_name;
                current_person.fixed_person_name = "";

            } //-- END check to see if name has been fixed --//
            
            current_person.title = current_title;
            current_person.person_organization = current_person_organization;
            current_person.quote_text = current_quote_text;
            current_person.person_id = current_person_id;
            current_person.person_index = person_index;

            // add person to this DataStore.
            this.add_person( current_person );

        } //-- END loop over persons --//

        /*
        // No need to do this - add_person() builds all this stuff for you.
        // then store off all the rest of the stuff.
        this.next_person_index = my_next_person_index;
        this.name_to_person_index_map = my_name_to_person_index_map;
        this.id_to_person_index_map = my_id_to_person_index_map;
        this.status_message_array = my_status_message_array;
        this.latest_person_index = my_latest_person_index;
         */

    } //-- END check to see if JSON passed in. --//

} //-- END CONTEXT_TEXT.DataStore method load_from_json() --//


/**
 * Accepts a Person instance.  Checks if there is a person index in instance.
 *     If so, calls update_person().  If not, calls add_person().
 *     Returns the status array that results from either invocation.
 */
CONTEXT_TEXT.DataStore.prototype.process_person = function( person_IN )
{
    
    // return reference
    var status_array_OUT = [];
    
    // declare variables.
    var me = "CONTEXT_TEXT.DataStore.prototype.process_person"
    var my_person_index = -1
    var is_index_ok = true;
    
    CONTEXT_TEXT.log_message( "Top of " + me );
    
    // got a valid index?
    my_person_index = person_IN.person_index
    is_index_ok = CONTEXT_TEXT.is_integer_OK( my_person_index, 0 );
    if ( is_index_ok == true )
    {
        
        // We do.  Call update_person().
        status_array_OUT = this.update_person( person_IN );
        
    }
    else
    {
        
        // We do not.  Call add_person().
        status_array_OUT = this.add_person( person_IN );
        
    }
    
    return status_array_OUT;
    
} //-- END DataStore method process_person() --//


/**
 * Accepts an index into the person array - Retrieves person at that index.
 *    If null, nothing there, nothing to remove.  If not null, makes that index
 *    in the array refer to null.  Then, looks for the index value in the values
 *    stored within the name-to-index and person-id-to-index maps.  If index
 *    value found, each key-value pair with the index as the value is removed.
 *    Returns a list of messages.  If empty, success.
 *
 * Postconditions: Also logs warnings to console.log(), so if you want to see if
 *    there are any warnings (tells things like whether the person exists at
 *    the index passed in, if there might have been more than one name or person
 *    ID that reference the index, etc.).  If it finds bad data, this method
 *    will clean it up.  When we remove a person at an index, removes all
 *    references to that index in the name and ID to index maps, even if there
 *    are mutiple name or IDs that map.
 *
 * @param {int} index_IN - index in person array that contains person we want to remove.
 * @returns {Array:string} - array of status messages that result from processing.
 */
CONTEXT_TEXT.DataStore.prototype.remove_person_at_index = function( index_IN )
{
    
    // return reference.
    var status_array_OUT = [];
    
    // declare variables
    var me = "CONTEXT_TEXT.DataStore.remove_person_at_index";
    var selected_index = -1;
    var is_index_OK = false;
    var my_person_array = -1;
    var person_to_remove = null;
    var my_person_name = "";
    var my_person_id = -1;
    var name_to_index_map = {};
    var person_id_to_index_map = {};
    var current_key = "";
    var current_value = "";
    
    // make sure index is an integer.
    selected_index = parseInt( index_IN );
    
    // got an index?
    is_index_OK = CONTEXT_TEXT.is_integer_OK( selected_index, 0 );
    if ( is_index_OK == true )
    {
        
        // I think so...  Get person array
        my_person_array = this.person_array;
        
        //  check to see if index present.
        person_to_remove = my_person_array[ selected_index ];
        
        // is it undefined or null?
        if ( person_to_remove === undefined )
        {
            
            // it is undefined.  Index not present in array.
            CONTEXT_TEXT.log_message( "In " + me + "(): Index " + selected_index + " is undefined - not present in array." );
            my_person_name = null;
            my_person_id = null;
            
        }
        else if ( person_to_remove == null )
        {
            
            // it is null.  Person already removed at this index.
            CONTEXT_TEXT.log_message( "In " + me + "(): Person at index " + selected_index + " already removed ( == null )." );
            my_person_name = null;
            my_person_id = null;
            
        }
        else
        {
            
            // there is a person here.  Get name and person id.
            my_person_name = person_to_remove.person_name;
            my_person_id = person_to_remove.person_id;
            
            // and, set the index to null.
            my_person_array[ selected_index ] = null;
            
        } //-- END check to see if person instance referenced by index is undefined or null. --//
            
            
        // look for values that reference index in:
        // - this.name_to_person_index_map
        // - this.id_to_person_index_map
        
        // always check, even of index reference is null or undefined, just as a
        //    sanity check to keep the maps clean.

        // name-to-index map --> this.name_to_person_index_map
        name_to_index_map = this.name_to_person_index_map;
        
        // loop over keys, checking if value for each matches value of index_IN.
        for ( current_key in name_to_index_map )
        {
            
            // get value.
            current_value = name_to_index_map[ current_key ];
            
            // convert to integer (just in case).
            current_value = parseInt( current_value );
            
            // compare to selected_index.
            if ( current_value == selected_index )
            {
                
                // we have a match.  Sanity check - see if the key matches the
                //    name from the person.
                if ( current_key != my_person_name )
                {
                    
                    // matching index, but key doesn't match.  Output message.
                    CONTEXT_TEXT.log_message( "In " + me + "(): Person name key \"" + current_key + "\" references index " + current_value + ".  Key should be \"" + my_person_name + "\".  Hmmm..." );
                    
                }
                
                // remove key-value pair from object.
                delete name_to_index_map[ current_key ];
                
            } //-- END check to see if vkey references the index we've been asked to remove --//
            
        } //-- END loop over keys in this.name_to_person_index_map --//
        
        // person ID to index map --> this.id_to_person_index_map
        person_id_to_index_map = this.id_to_person_index_map;
        
        // loop over keys, checking if value for each matches value of index_IN.
        for ( current_key in person_id_to_index_map )
        {
            
            // get value.
            current_value = person_id_to_index_map[ current_key ];
            
            // convert to integer (just in case).
            current_value = parseInt( current_value );
            
            // compare to selected_index.
            if ( current_value == selected_index )
            {
                
                // we have a match.  Sanity check - see if the key matches the
                //    person ID from the person.
                if ( current_key != my_person_id )
                {
                    
                    // matching index, but key doesn't match.  Output message.
                    CONTEXT_TEXT.log_message( "In " + me + "(): Person ID key \"" + current_key + "\" references index " + current_value + ".  Key should be \"" + my_person_id + "\".  Hmmm..." );
                    
                }
                
                // remove key-value pair from object.
                delete person_id_to_index_map[ current_key ];
                
            } //-- END check to see if key references the index we've been asked to remove --//
            
        } //-- END loop over keys in this.name_to_person_index_map --//
            
    }
    else //-- index is not OK. --//
    {
        
        // no valid index - error - return null
        status_array_OUT.push( "Index " + index_IN + " is not valid - could not remove person." );
        
    } //-- END check to see if valid index passed in. --//
    
    return status_array_OUT;

} //-- END CONTEXT_TEXT.DataStore method remove_person_at_index() --//


/**
 * Accepts a Person instance that contains an index in person array.  First, 
 *     checks to see if the person is valid.  If no, returns validation messages
 *     as error.  If valid, checks to make sure that there is an index in the
 *     person.  If not, returns an error.  If no errors, updates information on
 *     the person in all the appropriate places:
 *     - this.person_array
 *     - this.name_to_person_index_map with person_name as key, index of person
 *         in the person_array as the value.
 *     - if person ID, this.id_to_person_index_map with person ID as key, index
 *         of person in the person_array as the value.
 */
CONTEXT_TEXT.DataStore.prototype.update_person = function( person_IN )
{
    
    // return reference
    var status_array_OUT = [];
    
    // declare variables.
    var me = "CONTEXT_TEXT.DataStore.prototype.update_person_at_index"
    var is_index_ok = true;
    var is_ok_to_update = true;
    var validation_status_array = [];
    var validation_status_count = -1;
    var person_index = -1;
    var my_person_id = -1;
    var has_person_id = false;
    var name_map_status_array = [];
    var id_map_status_array = [];
    
    CONTEXT_TEXT.log_message( "Top of " + me );
    
    // make sure we have a person.
    if ( ( person_IN !== undefined ) && ( person_IN != null ) )
    {
        
        // and make sure we have an index.
        index_IN = person_IN.person_index;
        is_index_ok = CONTEXT_TEXT.is_integer_OK( index_IN, 0 );
        if ( is_index_ok == true )
        {
        
            // got an index and a person.  Is person valid?
            validation_status_array = person_IN.validate();
            validation_status_count = validation_status_array.length;
            if ( validation_status_count == 0 )
            {
                
                // do update-specific validation here - none for now...
                is_ok_to_update = true;
                
                // make sure that index passed in matches index in person.
                person_index = person_IN.person_index;
                if ( person_index != index_IN )
                {
                    
                    // they do not match.  This is an error.
                    is_ok_to_update = false;
                    status_array_OUT.push( "Index mismatch: index_IN = " + index_IN + "; person_IN.person_index = " + person_index );
                
                } //-- END check to see if index passed in matches person_IN --#
            
                // OK to update?
                if ( is_ok_to_update == true )
                {
                    
                    // no errors so far...  Update in person array.
                    this.person_array[ index_IN ] = person_IN;
                    
                    // update in name map.
                    name_map_status_array = this.update_person_in_name_map( person_IN, index_IN );
                    
                    // any errors?
                    if ( name_map_status_array.length > 0 )
                    {
                        
                        // yes.  Add to status array, fall out.
                        status_array_OUT = status_array_OUT.concat( name_map_status_array );
                    
                    }
                    else //-- added to name map just fine. --//
                    {
                        
                        // got a person ID?
                        my_person_id = person_IN.person_id;
                        has_person_id = CONTEXT_TEXT.is_integer_OK( my_person_id, 1 );
                        if ( has_person_id == true )
                        {
                            
                            // yes. Update mapping of person ID to person array
                            //    index.
                            id_map_status_array = this.update_person_in_person_id_map( person_IN, index_IN );
                            
                            // any errors?
                            if ( id_map_status_array.length > 0 )
                            {
                                
                                // yes.  Add to status array, fall out.
                                status_array_OUT = status_array_OUT.concat( id_map_status_array );
                            
                            } //-- END check to see if errors from updating in id map --//
                            
                        } //-- END check to see if has person ID --//
                        
                    } //-- END check to see if errors updating person in name map. --//
                        
                } //-- END check to see if OK to update? --//
                
            }
            else
            {
    
                // not valid.  Error.  Concat validation errors with any other
                //    errors.
                status_array_OUT = status_array_OUT.concat( validation_status_array );
    
            } //-- END check to see if person is valid. --//
            
        }
        else
        {
            
            // no index passed in.  Error.
            status_array_OUT.push( "No index passed in." );
            
        } //-- END check to see if index passed in --//
        
    }
    else
    {
        
        // no person passed in.  Error.
        status_array_OUT.push( "No person instance passed in." );
        
    } //-- END check to see if person passed in. --//
    
    return status_array_OUT;
    
} //-- END CONTEXT_TEXT.DataStore method update_person_at_index() --//


/**
 * Accepts a Person instance and that person's index in the person array.
 *     If both passed in, updates mapping of name to index in name_to_index_map
 *     in DataStore.  If not, does nothing.
 *
 * @param {Person} person_IN - person we want to add to update in the map of person name strings to indexes in person array.
 * @param {int} index_IN - index in person array we want name associated with.  If -1 passed in, effectively removes person from map.
 * @returns {Array} - Array of status messages - empty array = success.
 */
CONTEXT_TEXT.DataStore.prototype.update_person_in_name_map = function( person_IN, index_IN )
{
    
    // return reference
    var status_array_OUT = [];
    
    // declare variables.
    var me = "CONTEXT_TEXT.DataStore.prototype.update_person_in_name_map";
    var my_person_name = "";
    var is_person_name_OK = false;
    var my_name_to_index_map = {};
    
    // got a person?
    if ( ( person_IN !== undefined ) && ( person_IN != null ) )
    {
        
        // yes - get relevant variables.
        my_name_to_index_map = this.name_to_person_index_map;
        
        // get person name
        my_person_name = person_IN.person_name;
        
        // got a name?
        is_person_name_OK = CONTEXT_TEXT.is_string_OK( my_person_name );
        if ( is_person_name_OK == true )
        {
            
            // yes.  Set value for that name in map.
            my_name_to_index_map[ my_person_name ] = index_IN;
            
        }
        else
        {
            
            // no - error.
            status_array_OUT.push( "In " + me + "(): no name in person.  Can't do anything." );
            
        }

    }
    else
    {
        
        // no.  Error.
        status_array_OUT.push( "No person passed in.  What?" );
        
    } //-- END check to see if person instance.
    
    return status_array_OUT;
    
} //-- END CONTEXT_TEXT.DataStore method update_person_in_name_map() --//


/**
 * Accepts a Person instance and that person's index in the person array.
 *    If both passed in, checks to make sure that the person record has a
 *    person ID.  If so, updates mapping of person ID to index in
 *    id_to_person_index_map in DataStore.  If either no person or no
 *    person ID, does nothing.
 *
 * @param {Person} person_IN - person we want to update in the map of person IDs to person array indexes.
 * @param {int} index_IN - index in person array we want name associated with.  If -1 passed in, effectively removes person from map.
 * @returns {Array} - Array of status messages - empty array = success.
 */
CONTEXT_TEXT.DataStore.prototype.update_person_in_person_id_map = function( person_IN, index_IN )
{
    
    // return reference
    var status_array_OUT = [];
    
    // declare variables.
    var me = "CONTEXT_TEXT.DataStore.prototype.update_person_in_person_id_map";
    var person_id = -1;
    var is_person_id_ok = false;
    var my_person_id_to_index_map = {};
    
    // got a person?
    if ( ( person_IN !== undefined ) && ( person_IN != null ) )
    {
        
        // yes - get relevant variables.
        my_person_id_to_index_map = this.id_to_person_index_map;
        
        // get person ID.
        person_id = person_IN.person_id;
        
        // got a person id?
        is_person_id_ok = CONTEXT_TEXT.is_integer_OK( person_id, 1 )
        if ( is_person_id_ok == true )
        {
            
            // yes.  Set value for that name in map.
            my_person_id_to_index_map[ person_id ] = index_IN;
            
        }
        else
        {
            
            // no - error.
            status_array_OUT.push( "In " + me + "(): no ID in person.  Can't do anything." );
            
        } //-- END check to see if person ID present --//

    }
    else
    {
        
        // no.  Error.
        status_array_OUT.push( "No person passed in.  What?" );
        
    } //-- END check to see if person instance.
    
    return status_array_OUT;

} //-- END CONTEXT_TEXT.DataStore method update_person_in_person_id_map() --//


//=====================//
// END DataStore
//=====================//


//=======================//
// !--> PersonProperty
//=======================//

// PersonProperty Property Names
CONTEXT_TEXT.PersonProperty_names = {};
CONTEXT_TEXT.PersonProperty_names[ "PERSON_NAME" ] = CONTEXT_TEXT.JSON_PROP_PERSON_NAME; // "person_name"
CONTEXT_TEXT.PersonProperty_names[ "FIXED_PERSON_NAME" ] = CONTEXT_TEXT.JSON_PROP_FIXED_PERSON_NAME; // "fixed_person_name"
CONTEXT_TEXT.PersonProperty_names[ "PERSON_TYPE" ] = CONTEXT_TEXT.JSON_PROP_PERSON_TYPE; // "person_type"
CONTEXT_TEXT.PersonProperty_names[ "TITLE" ] = CONTEXT_TEXT.JSON_PROP_TITLE; // "title"
CONTEXT_TEXT.PersonProperty_names[ "PERSON_ORGANIZATION" ] = CONTEXT_TEXT.JSON_PROP_PERSON_ORGANIZATION; // "person_organization"
CONTEXT_TEXT.PersonProperty_names[ "QUOTE_TEXT" ] = CONTEXT_TEXT.JSON_PROP_QUOTE_TEXT; // "quote_text"
CONTEXT_TEXT.PersonProperty_names[ "PERSON_INDEX" ] = CONTEXT_TEXT.JSON_PROP_PERSON_INDEX; // "person_index"
CONTEXT_TEXT.PersonProperty_names[ "PERSON_ID" ] = CONTEXT_TEXT.JSON_PROP_PERSON_ID; // "person_id"
CONTEXT_TEXT.PersonProperty_names[ "ORIGINAL_PERSON_TYPE" ] = CONTEXT_TEXT.JSON_PROP_ORIGINAL_PERSON_TYPE; // "original_person_type"
CONTEXT_TEXT.PersonProperty_names[ "ARTICLE_PERSON_ID" ] = CONTEXT_TEXT.JSON_PROP_ARTICLE_PERSON_ID; // "article_person_id"

// PersonProperty Property Types
CONTEXT_TEXT.PersonProperty_data_types = {};
CONTEXT_TEXT.PersonProperty_data_types[ "INTEGER" ] = "integer";
CONTEXT_TEXT.PersonProperty_data_types[ "STRING" ] = "string";

// PersonProperty Property Input Types
CONTEXT_TEXT.PersonProperty_input_types = {};
CONTEXT_TEXT.PersonProperty_input_types[ "TEXT" ] = "text";
CONTEXT_TEXT.PersonProperty_input_types[ "TEXTAREA" ] = "textarea";
CONTEXT_TEXT.PersonProperty_input_types[ "HIDDEN" ] = "hidden";
CONTEXT_TEXT.PersonProperty_input_types[ "SELECT" ] = "select";

// PersonProperty constructor

/**
 * Represents one of the pieces of information about a person stored in the
 *     Person object.
 * @constructor
 */
CONTEXT_TEXT.PersonProperty = function()
{   
    // names of properties
    this.prop_names = CONTEXT_TEXT.PersonProperty_names;
    
    // item types
    this.prop_data_types = CONTEXT_TEXT.PersonProperty_data_types;

    // input types
    this.input_types = CONTEXT_TEXT.PersonProperty_input_types;
            
    // instance variables
    this.name = null;
    this.type = null;
    this.default_value = null;
    this.min_value = null;
    this.default_value = null;
    this.input_id = null;
    this.input_type = null;
    this.function_load_form = null;
    this.function_get_value = null;
    this.function_clear_form = null;
} //-- END CONTEXT_TEXT.PersonProperty constructor --//

// PersonProperty methods


/**
 * For property defined in current instance, checks to see if there is a clear
 *     function specified.  If so, calls it.  If not, looks up the input ID
 *     for the property and places the default value in that input.
 *
 * Preconditions: None.
 *
 * Postconditions: None.
 */
CONTEXT_TEXT.PersonProperty.prototype.clear_value = function()
{
    
    // declare variables
    var me = "CONTEXT_TEXT.PersonProperty.prototype.clear_value";
    var clear_form_function = "";
    var input_id = "";
    var default_value = "";

    // got a function for clearing form?
    clear_form_function = this.function_clear_form;
    if ( clear_form_function != null )
    {
        
        // there is a function to call for clearing.  Call it.
        clear_form_function();
        
    }
    else
    {
        
        // no function.  Use <input> ID and default value to clear by
        //     resetting the <input> to the default value.
        input_id = this.input_id;
        default_value = this.default_value;
        
        // call CONTEXT_TEXT.set_value_for_id()
        CONTEXT_TEXT.set_value_for_id( input_id, default_value );
        
    } //-- END check to see if we have a clear function to call --//
    
} //-- END method CONTEXT_TEXT.PersonProperty.prototype.clear_value --//
        

/**
 * Checks to see if there is a "get_value" function referenced in this instance.
 *     If so, calls it.  If not, calls get_value_from_form() on this instance to
 *     retrieve the value from the form in the standard way.  Returns value,
 *     regardless of how it was found, returns null if not found or error.
 *
 * Preconditions: None.
 *
 * Postconditions: None.
 *
 * @returns {string} - value of input matching ID passed in, else null if error.
 */
CONTEXT_TEXT.PersonProperty.prototype.get_value = function()
{
    // return reference
    var value_OUT = null;

    // declare variables
    var me = "CONTEXT_TEXT.PersonProperty.prototype.get_value";
    
    // declare variables - processing person properties.
    var get_value_function = null;
    
    // retrieve info on current property.
    get_value_function = this.function_get_value;
    
    // got a function for getting property value?
    if ( get_value_function != null )
    {
        
        // there is a function to call for retrieving value..  Call it.
        value_OUT = get_value_function();
        
    }
    else
    {
        
        // no fancy function - get value from form.
        value_OUT = this.get_value_from_form();
        
    } //-- END check to see if we have a clear function to call --//

    return value_OUT;
    
} //-- END PersonProperty method get_value() --#


/**
 * Gets id of input whose value we want to retrieve from current instance. Looks
 *     for input with that ID.  If one found, gets value from that input and
 *     returns it.
 *
 * Preconditions: None.
 *
 * Postconditions: None.
 *
 * @returns {string} - value of input matching ID passed in, else null if error.
 */
CONTEXT_TEXT.PersonProperty.prototype.get_value_from_form = function()
{
    // return reference
    var value_OUT = [];

    // declare variables
    var me = "CONTEXT_TEXT.PersonProperty.prototype.get_value_from_form";
    
    // declare variables - processing person properties.
    var data_type = "";
    var default_value = "";
    var input_id = -1;
    var input_type = "";
    var select_input_type = "";
    var integer_data_type = "";
    
    // initialize values
    select_input_type = CONTEXT_TEXT.PersonProperty_input_types[ "SELECT" ];
    integer_data_type = CONTEXT_TEXT.PersonProperty_data_types[ "INTEGER" ]
        
    // retrieve info on current property.
    data_type = this.type;
    default_value = this.default_value;
    input_id = this.input_id;
    input_type = this.input_type;
    
    // see how we retrieve value based on input type - there are
    //     separate functions for <select> and <input> (though they work
    //     the same at this point).
    if ( input_type == select_input_type )
    {
        
        // <select> - use CONTEXT_TEXT.get_selected_value_for_id().
        value_OUT = CONTEXT_TEXT.get_selected_value_for_id( input_id );
        
    }
    else
    {
    
        // if not select, treat all the rest the same - call
        //     CONTEXT_TEXT.get_value_for_id().
        value_OUT = CONTEXT_TEXT.get_value_for_id( input_id, default_value );
        
    }

    // based on data type, see if we need to do anything to the value.
    if ( data_type == integer_data_type )
    {
        
        // integer - cast potentially string value to be an integer.
        value_OUT = parseInt( value_OUT, 10 );
        
    }

    return value_OUT;
    
} //-- END PersonProperty method get_value_from_form() --#


/**
 * Checks to see if there is a "load_form" function referenced in this instance.
 *     If so, calls it.  If not, calls put_value_into_form() on this instance to
 *     retrieve the value from the form in the standard way.  Returns value,
 *     regardless of how it was found, returns null if not found or error.
 *
 * Preconditions: None.
 *
 * Postconditions: None.
 *
 * @returns {string} - value of input matching ID passed in, else null if error.
 */
CONTEXT_TEXT.PersonProperty.prototype.put_value = function( person_IN )
{
    // return reference
    var value_OUT = null;

    // declare variables
    var me = "CONTEXT_TEXT.PersonProperty.prototype.put_value";
    
    // declare variables - processing person properties.
    var load_form_function = null;
    
    // retrieve info on current property.
    load_form_function = this.function_load_form;
    
    // got a function for loading property value into form?
    if ( load_form_function != null )
    {
        
        // there is a function to call for retrieving value..  Call it.
        value_OUT = load_form_function( person_IN );
        
    }
    else
    {
        
        // no fancy function - get value place into form.
        value_OUT = this.put_value_into_form( person_IN );
        
    } //-- END check to see if we have a clear function to call --//

    return value_OUT;
    
} //-- END PersonProperty method put_value() --#


/**
 * Accepts person instance whose value we want to put into form.  After making
 *     sure we
 *     have an OK ID, looks for input with that ID.  If one found, gets value
 *     from that input and returns it.
 *
 * Preconditions: None.
 *
 * Postconditions: None.
 *
 * @param {string} id_IN - HTML id attribute value for input whose value we want to retrieve.
 * @returns {string} - value of input matching ID passed in, else null if error.
 */
CONTEXT_TEXT.PersonProperty.prototype.put_value_into_form = function( person_IN )
{
    // return reference
    var value_OUT = [];

    // declare variables
    var me = "CONTEXT_TEXT.PersonProperty.prototype.put_value_into_form";
    var property_element = null;
        
    // declare variables - processing person properties.
    var property_name = "";
    var data_type = "";
    var default_value = "";
    var input_id = -1;
    var input_type = "";
    var select_input_type = "";
    var integer_data_type = "";
    var my_value = null;
    var is_value_OK = false;
    
    // got a person?
    if ( person_IN != null )
    {
        
        // initialize values
        select_input_type = CONTEXT_TEXT.PersonProperty_input_types[ "SELECT" ];
        integer_data_type = CONTEXT_TEXT.PersonProperty_data_types[ "INTEGER" ];
            
        // retrieve info on current property.
        property_name = this.name;
        data_type = this.type;
        default_value = this.default_value;
        input_id = this.input_id;
        input_type = this.input_type;
        
        // get the property value.
        my_value = person_IN[ property_name ];
        
        // if integer data type, see if the integer is valid.
        if ( data_type == integer_data_type )
        {
            
            // it is an integer.  Is it OK?
            is_value_OK = CONTEXT_TEXT.is_integer_OK( my_value, 0 );
            
        }
        else
        {
            
            // not integer.  Check as string.
            is_value_OK = CONTEXT_TEXT.is_string_OK( my_value );
            
        }
        
        // Is the value OK?
        if ( is_value_OK == false )
        {
            
            // no.  Use default.
            my_value = default_value;
            
        }
        
        // see how we put in form value based on input type - there are
        //     separate functions for <select> and <input> (though they work
        //     the same at this point).
        if ( input_type == select_input_type )
        {
            
            // <select> - use CONTEXT_TEXT.set_selected_value_for_id().
            value_OUT = CONTEXT_TEXT.set_selected_value_for_id( input_id, my_value );
            
        }
        else
        {
        
            // if not select, treat all the rest the same - call
            //     CONTEXT_TEXT.set_value_for_id().
            value_OUT = CONTEXT_TEXT.set_value_for_id( input_id, my_value );
            
        } //-- END check to see if the input we are messing with is a <select>. --//
    
    } //-- END check to make sure person_IN is not null --//

    return value_OUT;
    
} //-- END PersonProperty method put_value_into_form() --#


//=====================//
// !--> Person
//=====================//

// !---- Person properties

// declare a variable
var temp_property = null;

// make list of properties, map names to info.
CONTEXT_TEXT.Person_property_name_list = [];
CONTEXT_TEXT.Person_property_name_to_info_map = {};

// person_name
temp_property = new CONTEXT_TEXT.PersonProperty();
temp_property.name = temp_property.prop_names.PERSON_NAME;
temp_property.type = temp_property.prop_data_types.STRING;
temp_property.default_value = "";
temp_property.min_value = null;
temp_property.input_id = CONTEXT_TEXT.INPUT_ID_PERSON_NAME;
temp_property.input_type = temp_property.input_types.TEXTAREA;
temp_property.function_load_form = null;
temp_property.function_get_value = null;
temp_property.function_clear_form = null;
CONTEXT_TEXT.Person_property_name_to_info_map[ temp_property.name ] = temp_property;
CONTEXT_TEXT.Person_property_name_list.push( temp_property.name );

// fixed_person_name
temp_property = new CONTEXT_TEXT.PersonProperty();
temp_property.name = temp_property.prop_names.FIXED_PERSON_NAME;
temp_property.type = temp_property.prop_data_types.STRING;
temp_property.default_value = "";
temp_property.min_value = null;
temp_property.input_id = CONTEXT_TEXT.INPUT_ID_FIXED_PERSON_NAME;
temp_property.input_type = temp_property.input_types.TEXTAREA;
temp_property.function_load_form = CONTEXT_TEXT.load_value_fixed_person_name;
temp_property.function_get_value = null;
temp_property.function_clear_form = CONTEXT_TEXT.cancel_fix_person_name;
CONTEXT_TEXT.Person_property_name_to_info_map[ temp_property.name ] = temp_property;
CONTEXT_TEXT.Person_property_name_list.push( temp_property.name );

// person_type
temp_property = new CONTEXT_TEXT.PersonProperty();
temp_property.name = temp_property.prop_names.PERSON_TYPE;
temp_property.type = temp_property.prop_data_types.STRING;
temp_property.default_value = "";
temp_property.min_value = null;
temp_property.input_id = CONTEXT_TEXT.INPUT_ID_PERSON_TYPE;
temp_property.input_type = temp_property.input_types.SELECT;
temp_property.function_load_form = CONTEXT_TEXT.load_value_person_type;
temp_property.function_get_value = null;
temp_property.function_clear_form = CONTEXT_TEXT.clear_person_type;
CONTEXT_TEXT.Person_property_name_to_info_map[ temp_property.name ] = temp_property;
CONTEXT_TEXT.Person_property_name_list.push( temp_property.name );

// title
temp_property = new CONTEXT_TEXT.PersonProperty();
temp_property.name = temp_property.prop_names.TITLE;
temp_property.type = temp_property.prop_data_types.STRING;
temp_property.default_value = "";
temp_property.min_value = null;
temp_property.input_id = CONTEXT_TEXT.INPUT_ID_TITLE;
temp_property.input_type = temp_property.input_types.TEXTAREA;
temp_property.function_load_form = null;
temp_property.function_get_value = null;
temp_property.function_clear_form = null;
CONTEXT_TEXT.Person_property_name_to_info_map[ temp_property.name ] = temp_property;
CONTEXT_TEXT.Person_property_name_list.push( temp_property.name );

// person_organization
temp_property = new CONTEXT_TEXT.PersonProperty();
temp_property.name = temp_property.prop_names.PERSON_ORGANIZATION;
temp_property.type = temp_property.prop_data_types.STRING;
temp_property.default_value = "";
temp_property.min_value = null;
temp_property.input_id = CONTEXT_TEXT.INPUT_ID_ORGANIZATION;
temp_property.input_type = temp_property.input_types.TEXTAREA;
temp_property.function_load_form = null;
temp_property.function_get_value = null;
temp_property.function_clear_form = null;
CONTEXT_TEXT.Person_property_name_to_info_map[ temp_property.name ] = temp_property;
CONTEXT_TEXT.Person_property_name_list.push( temp_property.name );

// quote_text
temp_property = new CONTEXT_TEXT.PersonProperty();
temp_property.name = temp_property.prop_names.QUOTE_TEXT;
temp_property.type = temp_property.prop_data_types.STRING;
temp_property.default_value = "";
temp_property.min_value = null;
temp_property.input_id = CONTEXT_TEXT.INPUT_ID_QUOTE_TEXT;
temp_property.input_type = temp_property.input_types.TEXTAREA;
temp_property.function_load_form = null;
temp_property.function_get_value = CONTEXT_TEXT.get_quote_text_value;
temp_property.function_clear_form = null;
CONTEXT_TEXT.Person_property_name_to_info_map[ temp_property.name ] = temp_property;
CONTEXT_TEXT.Person_property_name_list.push( temp_property.name );

// person_index
temp_property = new CONTEXT_TEXT.PersonProperty();
temp_property.name = temp_property.prop_names.PERSON_INDEX;
temp_property.type = temp_property.prop_data_types.INTEGER;
temp_property.default_value = -1;
temp_property.min_value = 0;
temp_property.input_id = CONTEXT_TEXT.INPUT_ID_PERSON_INDEX;
temp_property.input_type = temp_property.input_types.HIDDEN;
temp_property.function_load_form = null;
temp_property.function_get_value = null;
temp_property.function_clear_form = null;
CONTEXT_TEXT.Person_property_name_to_info_map[ temp_property.name ] = temp_property;
CONTEXT_TEXT.Person_property_name_list.push( temp_property.name );

// person_id
temp_property = new CONTEXT_TEXT.PersonProperty();
temp_property.name = temp_property.prop_names.PERSON_ID;
temp_property.type = temp_property.prop_data_types.INTEGER;
temp_property.default_value = -1;
temp_property.min_value = 1;
temp_property.input_id = CONTEXT_TEXT.INPUT_ID_MATCHED_PERSON_ID;
temp_property.input_type = temp_property.input_types.TEXT;
temp_property.function_load_form = CONTEXT_TEXT.load_value_person_id;
temp_property.function_get_value = CONTEXT_TEXT.get_person_id_value;
temp_property.function_clear_form = CONTEXT_TEXT.clear_person_id;
CONTEXT_TEXT.Person_property_name_to_info_map[ temp_property.name ] = temp_property;
CONTEXT_TEXT.Person_property_name_list.push( temp_property.name );

// original_person_type
temp_property = new CONTEXT_TEXT.PersonProperty();
temp_property.name = temp_property.prop_names.ORIGINAL_PERSON_TYPE;
temp_property.type = temp_property.prop_data_types.STRING;
temp_property.default_value = "";
temp_property.min_value = null;
temp_property.input_id = CONTEXT_TEXT.INPUT_ID_ORIGINAL_PERSON_TYPE;
temp_property.input_type = temp_property.input_types.HIDDEN;
temp_property.function_load_form = null;
temp_property.function_get_value = null;
temp_property.function_clear_form = CONTEXT_TEXT.clear_original_person_type;
CONTEXT_TEXT.Person_property_name_to_info_map[ temp_property.name ] = temp_property;
CONTEXT_TEXT.Person_property_name_list.push( temp_property.name );

// article_person_id
temp_property = new CONTEXT_TEXT.PersonProperty();
temp_property.name = temp_property.prop_names.ARTICLE_PERSON_ID;
temp_property.type = temp_property.prop_data_types.INTEGER;
temp_property.default_value = -1;
temp_property.min_value = 1;
temp_property.input_id = CONTEXT_TEXT.INPUT_ID_ARTICLE_PERSON_ID;
temp_property.input_type = temp_property.input_types.HIDDEN;
temp_property.function_load_form = null;
temp_property.function_get_value = null;
temp_property.function_clear_form = CONTEXT_TEXT.clear_article_person_id;
CONTEXT_TEXT.Person_property_name_to_info_map[ temp_property.name ] = temp_property;
CONTEXT_TEXT.Person_property_name_list.push( temp_property.name );

CONTEXT_TEXT.log_message( "Property names: " + CONTEXT_TEXT.Person_property_name_list );

// Person constructor

/**
 * Represents a person in an article.
 * @constructor
 */
CONTEXT_TEXT.Person = function()
{   
    // declare variables
    var me = "CONTEXT_TEXT.Person() constructor";
    var property = null;
    
    // instance variables
    this.person_name = "";
    this.fixed_person_name = "";
    this.person_type = "";
    this.title = "";
    this.person_organization = "";
    this.quote_text = "";
    this.person_index = -1;
    this.person_id = null;
    this.original_person_type = "";
    this.article_person_id = -1;
    
    // make list of properties, map names to info.
    //this.property_name_list = CONTEXT_TEXT.Person_property_name_list;
    //this.property_name_to_info_map = CONTEXT_TEXT.Person_property_name_to_info_map;

} //-- END CONTEXT_TEXT.Person constructor --//

// !---- Person methods

/**
 * populates Person entry form inputs from values in this object instance.
 */
CONTEXT_TEXT.Person.prototype.populate_form = function()
{
    
    // return reference
    var validate_status_array_OUT = [];

    // declare variables
    var me = "CONTEXT_TEXT.Person.populate_form";
    
    // declare variables - processing person properties.
    var my_person_name = "";
    var person_property_list = null;
    var person_property_info = null;
    var property_count = -1;
    var current_index = -1;
    var current_property_name = "";
    var current_property_info = null;
    var current_value = "";
    var data_type = "";
    var default_value = "";
    var input_id = -1;
    var input_type = "";
    var get_value_function = null;
    var status_message_array = null;

    // start by clearing coding form
    CONTEXT_TEXT.clear_coding_form( "Loading data" );

    // retrieve values from instance and use to populate the form.
    
    // get property info.
    person_property_list = CONTEXT_TEXT.Person_property_name_list;
    person_property_info = CONTEXT_TEXT.Person_property_name_to_info_map;
        
    // loop over properties
    property_count = person_property_list.length;
    for ( current_index = 0; current_index < property_count; current_index++ )
    {
        
        // get current property name.
        current_property_name = person_property_list[ current_index ];
        
        // retrieve the property info.
        current_property_info = person_property_info[ current_property_name ];
        
        // load the value
        current_value = current_property_info.put_value( this );
        
        // is it the name?
        if ( current_property_name == CONTEXT_TEXT.JSON_PROP_PERSON_NAME )
        {
            
            // yes - store person name.
            my_person_name = current_value;
            
        } //-- END check to see if person name --//
        
    } //-- END loop over Person properties --//
    
    // got a person name?
    if ( ( my_person_name != null ) && ( my_person_name != "" ) )
    {
        
        // yes.  make status message array (empty message will clear status area).
        status_message_array = [];
        status_message_array.push( "Loaded data for person: " + my_person_name );
        
        // output it.
        CONTEXT_TEXT.output_status_messages( status_message_array );

        
    } //-- END check to see if person name --//

    CONTEXT_TEXT.log_message( "In " + me + "(): Person JSON = " + JSON.stringify( this ) );
    
    // validate
    validate_status_array_OUT = this.validate();
    
    // CONTEXT_TEXT.log_message( "validate_status = " + validate_status )
    
    return validate_status_array_OUT;
    
} //-- END CONTEXT_TEXT.Person method populate_form() --//


/**
 * populates Person object instance from form inputs.
 * @param {jquery element} form_element_IN - Form element that contains inputs we will use to populate this instance.
 * @returns {Array} - list of validation messages.  If empty, all is well.  If array.length > 0, then there were validation errors.
 */
CONTEXT_TEXT.Person.prototype.populate_from_form = function( form_element_IN )
{
    
    // return reference
    var validate_status_array_OUT = [];

    // declare variables
    var me = "CONTEXT_TEXT.Person.populate_from_form";
    
    // declare variables - processing person properties.
    var person_property_list = null;
    var person_property_info = null;
    var property_count = -1;
    var current_index = -1;
    var current_property_name = "";
    var current_property_info = null;
    var current_value = "";
    var data_type = "";
    var default_value = "";
    var input_id = -1;
    var input_type = "";
    var get_value_function = null;
    var select_input_type = "";
    var integer_data_type = "";
    
    // initialize values
    select_input_type = CONTEXT_TEXT.PersonProperty_input_types[ "SELECT" ];
    integer_data_type = CONTEXT_TEXT.PersonProperty_data_types[ "INTEGER" ];

    // get form element
    form_element = form_element_IN
    
    // retrieve values from form inputs and store in instance.
    
    // get property info.
    person_property_list = CONTEXT_TEXT.Person_property_name_list;
    person_property_info = CONTEXT_TEXT.Person_property_name_to_info_map;
        
    // loop over properties
    property_count = person_property_list.length;
    for ( current_index = 0; current_index < property_count; current_index++ )
    {
        
        // get current property name.
        current_property_name = person_property_list[ current_index ];
        
        // retrieve the property info.
        current_property_info = person_property_info[ current_property_name ];
        
        // get the value
        current_value = current_property_info.get_value();
        
        // place the value in the specified property.
        property_name = current_property_info.name;
        this[ property_name ] = current_value;

    } //-- END loop over Person properties --//

    CONTEXT_TEXT.log_message( "In " + me + "(): Person JSON = " + JSON.stringify( this ) );
    
    // validate
    validate_status_array_OUT = this.validate();
    
    // CONTEXT_TEXT.log_message( "validate_status = " + validate_status )
    
    return validate_status_array_OUT;
    
} //-- END CONTEXT_TEXT.Person method populate_from_form() --//


/**
 * Converts person to a string value.
 */
CONTEXT_TEXT.Person.prototype.to_string = function()
{
    
    // return reference
    var value_OUT = "";
    
    // declare variables.
    var my_person_id = -1;
    var is_person_id_ok = false;
    var my_person_name = "";
    var my_person_type = "";
    
    // got person ID?
    my_person_id = this.person_id;
    is_person_id_ok = CONTEXT_TEXT.is_integer_OK( my_person_id, 1 );
    if ( is_person_id_ok == true )
    {
        value_OUT += my_person_id;
    }
    else
    {
        value_OUT += "new";
    }
    value_OUT += " - ";
    
    // name.
    my_person_name = this.person_name;
    value_OUT += my_person_name;
    
    // person type
    my_person_type = this.person_type;
    value_OUT += " - " + my_person_type;

    return value_OUT;
    
} //-- END CONTEXT_TEXT.Person method to_string() --//


/**
 * Converts person to a string value.
 */
CONTEXT_TEXT.Person.prototype.to_table_cell_html = function()
{
    
    // return reference
    var value_OUT = "";
    
    // declare variables.
    var my_person_id = -1;
    var is_person_id_ok = false;
    var my_person_name = "";
    var my_person_type = "";
    var my_person_index = -1;
    
    // person type
    my_person_type = this.person_type;
    value_OUT += "<td>" + my_person_type + "</td>";

    // name.
    my_person_name = this.person_name;
    my_person_index = this.person_index;
    value_OUT += "<td><a href=\"#\" onclick=\"CONTEXT_TEXT.load_person_into_form( " + my_person_index + " ); return false;\">" + my_person_name + "</a></td>";

    // got person ID?
    my_person_id = this.person_id;
    is_person_id_ok = CONTEXT_TEXT.is_integer_OK( my_person_id, 1 );
    value_OUT += "<td>";
    if ( is_person_id_ok == true )
    {
        value_OUT += my_person_id;
    }
    else
    {
        value_OUT += "new";
    }
    value_OUT += "</td>";
    
    
    return value_OUT;
    
} //-- END CONTEXT_TEXT.Person method to_table_cell_html() --//


/**
 * validates Person object instance.
 * @returns {Array} - list of validation messages.  If empty, all is well.  If array.length > 0, then there were validation errors.
 */
CONTEXT_TEXT.Person.prototype.validate = function()
{

    // return reference
    var status_array_OUT = [];  // empty list = valid, non-empty list = list of error messages, invalid.

    // declare variables
    var my_name = "";
    var is_name_OK = false;
    var my_person_type = "";
    var is_person_type_OK = false;
    var status_string = "";
    
    
    //------------------------------------------------------------------------//
    // must have a name
    my_name = this.person_name;
    is_name_OK = CONTEXT_TEXT.is_string_OK( my_name );
    if ( is_name_OK == false )
    {
        // no name - invalid.
        status_array_OUT.push( "Must have a name." );
    }
    
    //------------------------------------------------------------------------//
    // must have a person type
    my_person_type = this.person_type;
    
    // check if empty.
    is_person_type_OK = CONTEXT_TEXT.is_string_OK( my_person_type );
    if ( is_person_type_OK == true )
    {
        // not empty - make sure it is a known value.
        if ( CONTEXT_TEXT.PERSON_TYPE_ARRAY.indexOf( my_person_type ) == -1 )
        {
            
            // it is not.  Curious.  Error.
            status_array_OUT.push( "Person type value " + my_person_type + " is unknown ( known values: " + CONTEXT_TEXT.PERSON_TYPE_ARRAY + " )" );
            
        }
    }
    else
    {
        
        // no person type.  Got to have one.
        status_array_OUT.push( "Must have a person type." );
        
    } //-- END Check to see if there is a person type. --//
    
    // convert list of status messages to string.
    //if ( status_list_OUT.length > 0 )
    //{
        
        // join the messages.
        //status_string = status_list_OUT.join( ", " );
        // CONTEXT_TEXT.log_message( "status = " + status_string )
        
    //}
    
    return status_array_OUT;
    
} //-- END CONTEXT_TEXT.Person method validate() --//

//=====================//
// END Person
//=====================//

//----------------------------------------------------------------------------//
// !====> jquery event handlers
//----------------------------------------------------------------------------//


// javascript to keep the coding area on right from scrolling off page.
$( function(){

    // set the offset pixels automatically on how much the sidebar height is.
    // plus the top margin or header height
    //var offsetPixels = $('.sidebarBox').outerHeight() + 30;
    var offsetPixels = 0;
        
    $(window).scroll( function() {
        if ( $(window).scrollTop() > offsetPixels ) {
            $('.scrollingBox').css({
                'position': 'fixed',
                'top': '40px'
            });
        } else {
            $('.scrollingBox').css({
                'position': 'static'
            });
        }
    });
});

// ! document.ready( button - #select-text )
// javascript to pull text selection into a text input.
// Get selected text / 選択部分のテキストを取得
$( document ).ready(
    function()
    {
        $( '#select-text' ).click(        
            function()
            {
                // declare variables
                var selected_text = "";
                var selected_text_input = null;
    
                // get selection
                selected_text = $.selection();
                //CONTEXT_TEXT.log_message( "selected text : " + selected_text );
                
                // get input
                selected_text_input = $( '#selected-text' );
                
                // set value
                selected_text_input.val( selected_text );
            }
        )
    }
);


// ! document.ready( button - #store-name )
// javascript to store selected text as source name.
$( document ).ready(
    function()
    {
        $( '#store-name' ).click(        
            function()
            {
                // declare variables
                var selected_text = "";
                var last_name_text = "";
                var input_element = null;
    
                // get selection
                selected_text = $.selection();
                selected_text = selected_text.trim();
                
                if ( CONTEXT_TEXT.compress_white_space == true )
                {
                    // replace more than one contiguous internal white space
                    //     character with a single space.
                    selected_text = selected_text.replace( /\s+/g, ' ' );
                }

                //CONTEXT_TEXT.log_message( "selected text : \"" + selected_text + "\"" );

                $( '#' + CONTEXT_TEXT.INPUT_ID_PERSON_NAME ).val( selected_text );
                
                // place last name in text-to-find-in-article <input>, then try
                //     to find in text.
                CONTEXT_TEXT.find_last_name_in_article_text();
                
                // clear out the fix name area.
                CONTEXT_TEXT.cancel_fix_person_name();
            }
        )
    }
); //-- END document.ready( #store-name ) --//


// ! document.ready( button - #fix-person-name )
// javascript to copy name from #source-name to the Lookup text field.
$( document ).ready(
    function()
    {
        $( '#fix-person-name' ).click(        
            function()
            {
                // declare variables
                var name_text = "";
                var person_lookup = "";
                var input_element = null;
    
                // get selection
                name_text = CONTEXT_TEXT.get_person_name_value();
                //CONTEXT_TEXT.log_message( "source text : " + source_text );

                // get id_person_text_element text field,  place value, then
                //    fire lookup event.
                input_element = $( '#' + CONTEXT_TEXT.INPUT_ID_FIXED_PERSON_NAME );
                input_element.val( name_text );
            }
        )
    }
); //-- END document.ready( button - #fix-person-name ) --//


// ! document.ready( button - #store-title )
// javascript to store selected text as source name + title.
$( document ).ready(
    function()
    {
        $( '#store-title' ).click(        
            function()
            {
                // declare variables
                var selected_text = "";
                var person_title_element = null;
                var existing_text = "";
    
                // get selection
                selected_text = $.selection();
                selected_text = selected_text.trim();
                //CONTEXT_TEXT.log_message( "selected text : " + selected_text );
                
                // see if there is already something there.
                person_title_element = $( '#' + CONTEXT_TEXT.INPUT_ID_TITLE );
                existing_text = person_title_element.val();
                //CONTEXT_TEXT.log_message( "Existing text: " + existing_text )
                
                // something already there?
                if ( existing_text != "" )
                {

                    // yes - append new to the end.
                    person_title_element.val( existing_text + " " + selected_text );
                    
                }
                else
                {
                    
                    // no - just overwrite.
                    person_title_element.val( selected_text );
                    
                }

            }
        )
    }
); //-- END document.ready( #store-title ) --//


// ! document.ready( button - #store-organization )
// javascript to store selected text as organization.
$( document ).ready(
    function()
    {
        $( '#store-organization' ).click(        
            function()
            {
                // declare variables
                var selected_text = "";
                var person_organization_element = null;
                var existing_text = "";
    
                // get selection
                selected_text = $.selection();
                selected_text = selected_text.trim();
                
                if ( CONTEXT_TEXT.compress_white_space == true )
                {
                    // replace more than one contiguous internal white space
                    //     character with a single space.
                    selected_text = selected_text.replace( /\s+/g, ' ' );
                }

                //CONTEXT_TEXT.log_message( "selected text : " + selected_text );
                
                // see if there is already something there.
                person_organization_element = $( '#' + CONTEXT_TEXT.INPUT_ID_ORGANIZATION );
                existing_text = person_organization_element.val();
                //CONTEXT_TEXT.log_message( "Existing text: " + existing_text )
                
                // something already there?
                if ( existing_text != "" )
                {

                    // yes - append new to the end.
                    person_organization_element.val( existing_text + " " + selected_text );
                    
                }
                else
                {
                    
                    // no - just overwrite.
                    person_organization_element.val( selected_text );
                    
                }

            }
        )
    }
); //-- END document.ready( #store-organization ) --//


// ! document.ready( button - #store-quote-text )
// javascript to store selected text as source's quotation text.
$( document ).ready(
    function()
    {
        $( '#store-quote-text' ).click(        
            function()
            {
                // declare variables
                var selected_text = "";
                var source_quote_text_element = null;
                var is_quoted_element = null;
                var is_quoted = false;
                var source_quote_text_value = "";
    
                // get selection
                selected_text = $.selection();
                selected_text = selected_text.trim();
                
                if ( CONTEXT_TEXT.compress_white_space == true )
                {
                    // replace more than one contiguous internal white space
                    //     character with a single space.
                    selected_text = selected_text.replace( /\s+/g, ' ' );
                }
                
                CONTEXT_TEXT.log_message( "selected text : " + selected_text );
                
                // get source-quote-text element.
                source_quote_text_element = $( '#' + CONTEXT_TEXT.INPUT_ID_QUOTE_TEXT );
                
                // store selected text.
                source_quote_text_element.val( selected_text );
                
            } //-- END click() nested anonymous function. --//
        ) //-- END click() method call. --//
    } //-- END ready() nested anonymous function --//
); //-- END document.ready( button - #store-quote-text ) call --//

// ! ----> buttons - person lookup

// ! document.ready( button - #lookup-person-name )
// javascript to copy name from #source-name to the Lookup text field.
$( document ).ready(
    function()
    {
        $( '#lookup-person-name' ).click(        
            function()
            {
                // declare variables
                var source_text = "";
                var person_lookup = "";
    
                // get selection
                source_text = CONTEXT_TEXT.get_person_name();
                //CONTEXT_TEXT.log_message( "source text : " + source_text );

                // try writing to clipboard.
                navigator.clipboard.writeText( source_text )

                // get id_person_text_element text field,  place value, then
                //    fire lookup event.
                // id_person_text_element = $( '#' + CONTEXT_TEXT.INPUT_ID_AJAX_ID_PERSON_TEXT );
                // id_person_text_element.val( source_text );
                // id_person_text_element.trigger( 'keydown' );
                
                // You'd think some of these might work to fire event...
                //    ...but they don't.
                //id_person_text_element.trigger( "search", "" );
                //id_person_text_element.autocomplete( "search", "" );
                //id_person_text_element.data( "ui-autocomplete" )._trigger( "change" );
                //id_person_text_element.keyup()
                //id_person_text_element.click()
                //id_person_text_element.trigger( 'init-autocomplete' );
                //id_person_text_element.trigger( 'added' );

                // tried other elements, too - #id_person_on_deck.
                //id_person_on_deck_element = $( '#id_person_on_deck' );
                //id_person_on_deck_element.trigger( 'added' );
                //id_person_on_deck_element.autocomplete( "search", "" );

                // tried other elements, too - #id_person
                //id_person_element = $( '#id_person' );
                //id_person_element.trigger( 'added' );
                //id_person_element.autocomplete( "search", "" );

            }
        )
    }
); //-- END document.ready( button - #lookup-person-name ) --//


// ! ----> buttons - find in article text


// ! document.ready( button - #find-name-in-article-text )
// javascript to copy name from #source-name to the Find in Article Text text
//     input.
$( document ).ready(
    function()
    {
        $( '#find-name-in-article-text' ).click(        
            function()
            {
                // declare variables
                var value = "";
    
                // get name text
                value = CONTEXT_TEXT.get_person_name();

                // send to find input.
                CONTEXT_TEXT.send_text_to_find_input( value );
                
                CONTEXT_TEXT.log_message( "In document.ready( button - #find-name-in-article-text ) - match text : " + value );                
            }
        )
    }
); //-- END document.ready( button - #find-name-in-article-text ) --//


// ! document.ready( button - #find-last-name-in-article-text )
// javascript to copy last name from #source-name to the Find in Article Text
//     text input.
$( document ).ready(
    function()
    {
        $( '#find-last-name-in-article-text' ).click(        
            function()
            {
                // declare variables
                var value = "";
    
                // get name text
                value = CONTEXT_TEXT.get_person_last_name_value();

                // send to find input.
                CONTEXT_TEXT.send_text_to_find_input( value );
                
                CONTEXT_TEXT.log_message( "In document.ready( button - #find-last-name-in-article-text ) - match text : " + value );                
            }
        )
    }
); //-- END document.ready( button - #find-last-name-in-article-text ) --//


// ! document.ready( button - #find-in-article-text )
// javascript to look for whatever is in the <input> with
//     id="text-to-find-in-article" inside the article's text, and highlight any
//     paragraphs that contain a match.
$( document ).ready(
    function()
    {
        $( '#find-in-article-text' ).click(        
            function()
            {

                // declare variables
                var me = "document.ready( button - #find-in-article-text )";
                var input_element = "";
                var find_text = "";
    
                // get text-to-find-in-article text field,  get value, then
                //    find_in_article_text().
                input_element = $( '#' + CONTEXT_TEXT.INPUT_ID_TEXT_TO_FIND_IN_ARTICLE );
                find_text = input_element.val();

                //CONTEXT_TEXT.log_message( "In " + me + " - find text : " + find_text );

                // find in text...
                CONTEXT_TEXT.find_in_article_text( find_text );
                
            }
        )
    }
); //-- END document.ready( button - #find-in-article-text ) --//


// ! document.ready( button - #clear-find-in-article-text )
// javascript to unmark all paragraphs that have matches in them.
$( document ).ready(
    function()
    {
        $( '#clear-find-in-article-text' ).click(        
            function()
            {
                // declare variables
                var me = "document.ready( button - #clear-find-in-article-text )";
                var name_text = "";
                var input_element = "";
    
                // clear matches.
                CONTEXT_TEXT.clear_find_in_text();
                
                CONTEXT_TEXT.log_message( "In " + me );
            }
        )
    }
); //-- END document.ready( button - #clear-find-in-article-text ) --//


// ! ----> load existing coding data

// !document.ready( load existing coding data )
// javascript to load existing coding data if present.
$( document ).ready(

    function()
    {

        // declare variables
        var me = "CONTEXT_TEXT.load_existing_coding_data";
        var my_data_store = null;
    
        // got anything to load?
        if ( ( CONTEXT_TEXT.data_store_json != null ) && ( CONTEXT_TEXT.data_store_json != "" ) )
        {
            
            // yes - get person store
            my_data_store = CONTEXT_TEXT.get_data_store();
        
            // call load_from_json()
            my_data_store.load_from_json();

            // repaint coding area
            CONTEXT_TEXT.display_persons();
        
        }
    
    }

); //-- END document.ready( load existing coding data ) --//


// ! ----> force activation of coding submit button.


// !document.ready( activate coding submit button )
// javascript to load existing coding data if present.
$( document ).ready(

    function()
    {

        // declare variables
        var me = "CONTEXT_TEXT.activate_coding_submit_button";
        var submit_button_element = null;
        var submit_button_disabled = false;
        var submit_button_value = "";
    
        // Retrieve submit button, enable it, and then change text
        //    to say "Submit Article Coding!".
        submit_button_element = $( '#' + CONTEXT_TEXT.INPUT_ID_SUBMIT_ARTICLE_CODING );
        
        // if disabled, enable.
        submit_button_disabled = submit_button_element.prop( 'disabled' );
        if ( submit_button_disabled == true )
        {
            
            // disabled.  Enable.
            submit_button_element.prop( 'disabled', false );
            
        }

        // Make sure value isn't "Please wait..."
        submit_button_value = submit_button_element.val();
        if ( submit_button_value == CONTEXT_TEXT.ARTICLE_CODING_SUBMIT_BUTTON_VALUE_WAIT )
        {
            
            // it says wait.  Change it to reset value.
            submit_button_element.val( CONTEXT_TEXT.ARTICLE_CODING_SUBMIT_BUTTON_VALUE_RESET );
            
        }
    
    }

); //-- END document.ready( activate coding submit button ) --//
