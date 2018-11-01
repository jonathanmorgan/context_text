//============================================================================//
// javascript for article coding.
//============================================================================//

//----------------------------------------------------------------------------//
// !====> namespace!
//----------------------------------------------------------------------------//


var SOURCENET = SOURCENET || {};


//----------------------------------------------------------------------------//
// !====> namespaced variables
//----------------------------------------------------------------------------//


// DEBUG!
SOURCENET.debug_flag = false;

// Compress white space in values?
SOURCENET.compress_white_space = true;
SOURCENET.regex_compress_white_space = /\s+/g


//----------------------------------------------------------------------------//
// !====> function definitions
//----------------------------------------------------------------------------//


/**
 * Accepts string, uses regular expression to compress runs of internal white
 *     space to a single space, returns the result.
 */
SOURCENET.compress_internal_white_space = function( string_IN ) 
{
    // return reference
    var string_OUT = null;
    
    // replace more than one contiguous internal white space
    //     character with a single space.
    string_OUT = string_IN.replace( SOURCENET.regex_compress_white_space, ' ' );
    
    return string_OUT;

} //-- end function SOURCENET.compress_internal_white_space --//
 

SOURCENET.decode_html = function( html_IN )
{
    // from: http://stackoverflow.com/questions/7394748/whats-the-right-way-to-decode-a-string-that-has-special-html-entities-in-it?lq=1

    // return reference
    var text_OUT = "";

    // declare variables
    var txt = null;

    // create textarea
    txt = document.createElement("textarea");

    // store HTML inside
    txt.innerHTML = html_IN;

    // get value back out.
    text_OUT = txt.value;
    
    return text_OUT;
}


/**
 * Accepts id of select whose selected value we want to retrieve.  After making
 *    sure we have an OK ID, looks for select with that ID.  If one found, finds
 *    selectedIndex, retrieves option at that index, and retrieves value from
 *    that option.  Returns the selected value.
 *
 * Preconditions: None.
 *
 * Postconditions: None.
 *
 * @param {string} select_id_IN - HTML id attribute value for select whose selected value we want to retrieve.
 * @returns {string} - selected value of select matching ID passed in, else null if error.
 */
SOURCENET.get_selected_value_for_id = function( select_id_IN )
{
    
    // return reference
    var value_OUT = null;
    
    // declare variables
    var me = "SOURCENET.get_selected_value_for_id";
    
    // just call get_value_for_id()
    value_OUT = SOURCENET.get_value_for_id( select_id_IN, null );
    
    return value_OUT;
    
} //-- END function SOURCENET.get_selected_value_for_id() --//


/**
 * Accepts id of input whose value we want to retrieve.  After making sure we
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
SOURCENET.get_value_for_id = function( id_IN, default_IN )
{
    
    // return reference
    var value_OUT = null;
    
    // declare variables
    var me = "SOURCENET.get_value_for_id";
    var is_id_OK = false;
    var element = null;
    var value = "";
    
    // is ID passed in OK?
    is_id_OK = SOURCENET.is_string_OK( id_IN );
    if ( is_id_OK == true )
    {
            
        // get select element.
        element = $( '#' + id_IN );
        
        // get selected value
        value = element.val();
        
        // return it.
        value_OUT = value;
        
    }
    else
    {
    
        // select ID is empty.  Return default.
        value_OUT = default_IN;
        
    }
    
    SOURCENET.log_message( "In " + me + "(): element ID = " + id_IN + "; value = " + value_OUT );
    
    return value_OUT;
    
} //-- END function SOURCENET.get_value_for_id() --//


/**
 * Accepts boolean variable.  Checks to see if it is OK.  If undefined, null, or
 *     "", returns false.  If not equal to either true or false, returns false.
 *     Otherwise, returns true.
 *
 * @param {boolean} value_IN - boolean value to check for OK-ness.
 * @returns {boolean} - if value is undefined, null, or "", returns false. If
 *     not equal to either true or false, returns false. Otherwise returns true.
 */
SOURCENET.is_boolean_OK = function( value_IN )
{
    
    // return reference
    var is_OK_OUT = true;
    
    if ( ( value_IN !== undefined ) && ( value_IN != null ) && ( value_IN != "" ) )
    {
        // not empty or null.  Is the value an actual boolean? 
        if ( !!value_IN === value_IN )
        {
            // Actually a boolean value.  OK!
            is_OK_OUT = true;
        }
        else
        {
            
            // not a real boolean, not OK!
            is_OK_OUT = false;

        }
        
    }
    else
    {
        
        // not OK.
        is_OK_OUT = false;
        
    }
    
    return is_OK_OUT;
    
} //-- END function SOURCENET.is_boolean_OK() --//


/**
 * Accepts integer variable.  Checks to see if it is OK.  If undefined, null, or
 *    less than min value, returns false.  Otherwise, returns true.
 *
 * @param {int} integer_IN - Integer value to check for OK-ness.
 * @param {int} min_value_IN - minimum OK value.
 * @returns {boolean} - if string is undefined, null, or "", returns false.  Otherwise returns true.
 */
SOURCENET.is_integer_OK = function( integer_IN, min_value_IN )
{
    
    // return reference
    var is_OK_OUT = true;
    
    // declare variables.
    var min_value = 0;
    
    // if nothing passed in for min_value, default to 0
    if ( ( min_value_IN !== undefined ) && ( min_value_IN != null ) )
    {
        
        // default passed in.  Use it.
        min_value = min_value_IN;
        
    }
    else
    {
        
        // nothing passed in.  Default to 0.
        min_value = 0;
        
    }
    
    if ( ( integer_IN !== undefined ) && ( integer_IN != null ) && ( integer_IN >= min_value ) )
    {
        
        // OK!
        is_OK_OUT = true;
        
    }
    else
    {
        
        // not OK.
        is_OK_OUT = false;
        
    }
    
    return is_OK_OUT;
    
} //-- END function SOURCENET.is_integer_OK() --//


/**
 * Accepts string variable.  Checks to see if it is OK.  If undefined, null, or
 *    "", returns false.  Otherwise, returns true.
 *
 * @param {string} string_IN - String value to check for OK-ness.
 * @returns {boolean} - if string is undefined, null, or "", returns false.  Otherwise returns true.
 */
SOURCENET.is_string_OK = function( value_IN, do_allow_empty_IN )
{
    
    // return reference
    var is_OK_OUT = true;
    
    // declare variables
    var is_value_ok = false;
    var allow_empty = false;

    // initialize
    is_value_ok = SOURCENET.is_boolean_OK( do_allow_empty_IN );
    if ( ( is_value_ok === false ) || ( do_allow_empty_IN === undefined ) || ( do_allow_empty_IN == null ) )
    {
        // nothing passed in.  default to not allowing empty.
        allow_empty = false
    }
    else
    {
        
        // use value passed in.
        allow_empty = do_allow_empty_IN
        
    }
    
    if ( ( value_IN !== undefined ) && ( value_IN != null ) )
    {
        
        // do we care about empty?
        if ( allow_empty == true )
        {
            // no - OK
            is_ok_OUT = true;
        }
        else if ( ( allow_empty == false ) && ( value_IN != "" ) )
        {            
            // yes, and the value isn't empty string.  OK!
            is_OK_OUT = true;
        }
        else if ( ( allow_empty == false ) && ( value_IN == "" ) )
        {
            // empty, but no empties allowed. Not OK.
            is_OK_OUT = false;
        }
        else
        {
            // not OK.  Probably empty string.
            is_OK_OUT = false;
        }
        
    }
    else
    {
        
        // not OK.
        is_OK_OUT = false;
        
    }
    
    return is_OK_OUT;
    
} //-- END function SOURCENET.is_string_OK() --//


/**
 * Accepts a message.  If console.log() is available, calls that.  If not, does
 *    nothing.
 */
SOURCENET.log_message = function( message_IN )
{
    
    // declare variables
    var output_flag = true;
    
    // set to SOURCENET.debug_flag
    output_flag = SOURCENET.debug_flag;
    
    // check to see if we have console.log() present.
    if ( ( window.console ) && ( window.console.log ) && ( output_flag == true ) )
    {

        // console is available
        console.log( message_IN );
        
    } //-- END check to see if console.log() present. --//
    
} //-- END function SOURCENET.log_message() --//


/**
 * Clears out coding form and status message area, and optionally displays a
 *    status message if one passed in.
 *
 * @param {Array:string} status_message_array_IN - array of messages to place in status area.  If undefined, null, or [], no messages output and message area is cleared and hidden.
 */
SOURCENET.output_status_messages = function( status_message_array_IN )
{
    
    // declare variables.
    var me = "SOURCENET.output_status_messages";
    var message_area_div_element = null;
    var message_area_ul_id = "";
    var message_area_ul_class = "";
    var message_area_ul_empty_html = "";
    var message_area_ul = null;
    var message_count = -1;
    var message_index = -1;
    var current_message = "";
    var message_li_element = null;
    
    // set variables
    message_area_ul_id = "status-message-list";
    message_area_ul_class = "statusMessageList";
    message_area_ul_empty_html = '<ul id="' + message_area_ul_id + '" class="' + message_area_ul_class + '"></ul>';

    // get <div id="status-message-area" class="statusMessageArea">
    message_area_div_element = $( '#status-message-area' );
    
    // get <ul id="status-message-list" class="statusMessageList">
    message_area_ul_element = message_area_div_element.find( '#status-message-list' );
    
    // got message array?
    if ( ( status_message_array_IN !== undefined ) && ( status_message_array_IN != null ) && ( status_message_array_IN.length > 0 ) )
    {
        
        // got messages.
        
        // got <ul>?
        if ( message_area_ul_element.length > 0 )
        {
            
            // remove the <ul>
            message_area_ul_element.remove();
            
        } //-- END check to see if ul inside <div> --//
        
        // make new <ul>.
        message_area_ul_element = $( message_area_ul_empty_html );
        
        // add it to the <div>.
        message_area_div_element.append( message_area_ul_element );
        
        // loop over messages
        message_count = status_message_array_IN.length;
        for( message_index = 0; message_index < message_count; message_index++ )
        {
            
            // get message
            current_message = status_message_array_IN[ message_index ];
            
            // create <li>, append to <ul>.
            message_li_element = $( '<li>' + current_message + '</li>' );
            message_li_element.attr( "id", "message-" + message_index );
            
            // append it to the message_area_ul_element
            message_area_ul_element.append( message_li_element );
            
        } //-- END loop over messages --//
        
        // show the <div> if not already.
        message_area_div_element.show();
        
    }
    else //-- no messages --//
    {
        
        // Hide the <div>.
        message_area_div_element.hide();
        
        // got <ul>?
        if ( message_area_ul_element.length > 0 )
        {
            
            // remove the <ul>
            message_area_ul_element.remove();
            
        } //-- END check to see if ul inside <div> --//
        
    } //-- END check to see if message array is populated.
    
} //-- END function SOURCENET.output_status_messages() --//


/**
 * Accepts id of select whose selected value we want to set, and value we want
 *    to be selected.  After making sure we have an OK ID, looks for select with
 *    that ID.  If one found, sets to the value passed in.  Returns the selected
 *    value.
 *
 * Preconditions: None.
 *
 * Postconditions: None.
 *
 * @param {string} select_id_IN - HTML id attribute value for select whose selected value we want to retrieve.
 * @returns {string} - selected value of select matching ID passed in, else null if error.
 */
SOURCENET.set_selected_value_for_id = function( select_id_IN, select_value_IN )
{
    
    // return reference
    var value_OUT = null;
    
    // declare variables
    var me = "SOURCENET.set_selected_value_for_id";
    var is_select_id_OK = false;
    var select_element = null;
    
    // just call SOURCENET.set_value_for_id()
    value_OUT = SOURCENET.set_value_for_id( select_id_IN, select_value_IN );
    
    SOURCENET.log_message( "In " + me + "(): <select> ID = " + select_id_IN + "; value = " + value_OUT );
    
    return value_OUT;
    
} //-- END function SOURCENET.set_selected_value_for_id() --//


/**
 * Accepts id of element whose value we want to set, and value we want
 *    to be set.  After making sure we have an OK ID, looks for element with
 *    that ID.  If one found, sets to the value passed in.  Returns the value.
 *
 * Preconditions: None.
 *
 * Postconditions: None.
 *
 * @param {string} element_id_IN - HTML id attribute value for element whose value we want to set.
 * @returns {string} - value of element matching ID passed in, else null if error.
 */
SOURCENET.set_value_for_id = function( element_id_IN, value_IN )
{
    
    // return reference
    var value_OUT = null;
    
    // declare variables
    var me = "SOURCENET.set_value_for_id";
    var is_element_id_OK = false;
    var element = null;
    
    // select ID passed in OK?
    is_element_id_OK = SOURCENET.is_string_OK( element_id_IN );
    if ( is_element_id_OK == true )
    {
        
        // get element.
        element = $( '#' + element_id_IN );
        
        // set value
        element.val( value_IN );
        
        // get value.
        value_OUT = SOURCENET.get_value_for_id( element_id_IN );
    
    }
    else
    {
    
        // element ID is empty.  Return null.
        value_OUT = null;
        
    }
    
    SOURCENET.log_message( "In " + me + "(): HTML element ID = " + element_id_IN + "; value = " + value_OUT );
    
    return value_OUT;
    
} //-- END function SOURCENET.set_value_for_id() --//


