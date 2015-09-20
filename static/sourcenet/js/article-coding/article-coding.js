//============================================================================//
// javascript for article coding.
//============================================================================//

//----------------------------------------------------------------------------//
// namespace!
//----------------------------------------------------------------------------//


var SOURCENET = SOURCENET || {};


//----------------------------------------------------------------------------//
// namespaced variables
//----------------------------------------------------------------------------//


// JSON to prepopulate page if we are editing.
var SOURCENET.subject_JSON = "";

// subject store used to keep track of subjects while coding.
var SOURCENET.subject_store = null;


//----------------------------------------------------------------------------//
// object definitions
//----------------------------------------------------------------------------//


//=====================//
// SubjectStore
//=====================//

// SubjectStore constructor

/**
 * Stores and indexes subjects in an article.
 * @constructor
 */
SOURCENET.SubjectStore = function()
{
    // instance variables
    this.subject_array = [];
    this.next_subject_index = 0;
    this.name_to_subject_index_map = {};
    this.id_to_subject_index_map = {};
    
    // instance variables - status messages
    this.status_message_array = [];
    this.latest_subject_index = -1;
}

// SubjectStore methods

/**
 * Accepts a Subject instance.  First, checks to see if the subject is valid.
 *    If no, returns validation messages as error.  If subject has a person ID,
 *    checks to see if the ID is already a key in this.id_to_subject_map.  If
 *    so, returns an error.  If no ID, checks to see if name is already in
 *    this.name_to_subject_map.  If so, returns an error.  If no errors, then
 *    adds the subject to all the appropriate places:
 *    - this.subject_array
 *    - this.name_to_subject_map with subject_name as key, subject instance as
 *       value.
 *    - if person ID, this.id_to_subject_map with person ID as key, subject
 *       instance as value.
 */
SOURCENET.SubjectStore.prototype.add_subject = function( subject_IN )
{
    
    // return reference
    status_array_OUT = [];
    
    // declare variables.
    is_ok_to_add = true;
    subject_type = "";
    validation_status_array = [];
    validation_status_count = -1;
    my_person_id = -1;
    is_id_in_map = false;
    my_subject_name = "";
    
    // make sure we have a subject.
    subject_type = 
    if ( ( subject_IN !== undefined ) && ( subject_IN != null ) )
    {
        
        // got a subject.  Is it valid?
        validation_status_array = subject_IN.validate();
        validation_status_count = validation_status_array.length;
        if ( validation_status_count == 0 )
        {
            
            // valid.  Got a person ID?
            my_person_id = subject_IN.person_id;
            if ( ( my_person_id != null ) && ( my_person_id > 0 ) )
            {
                
                // got a person ID.  Is that ID already in map of IDs to array
                //    indices?
                is_id_in_map = this.id_to_subject_index_map.hasOwnProperty( my_person_id );
                if ( is_id_in_map == true )
                {
                    
                    // already in map...  Error.
                    is_ok_to_add = false;
                    status_array_OUT.push( "Person ID " + my_person_id + " already present in SubjectStore." )
                    
                }
                
            } //-- END check to see if person ID present. --//
            
            // Got a subject name?
            my_subject_name = subject_IN.subject_name;
            if ( ( my_subject_name != null ) && ( my_subject_name != "" ) )
            {
                
                // subject name present (as it should be at this point).  See if
                //    this name is already in the SubjectStore
                
                
            }

            
        }
        else
        {

            // not valid.  Error.  Concat validation errors with any other
            //    errors.
            status_array_OUT = status_array_OUT.concat( validation_status_array );

        } //-- END check to see if subject is valid. --//
        
    }
    else
    {
        
        // no subject passed in.  Error.
        status_array_OUT.push( "No subject instance passed in." );
        
    } //-- END check to see if subject passed in. --//
    
    return status_array_OUT;
    
} //-- END SOURCENET.SubjectStore method add_subject() --//


/**
 * Accepts a Subject instance - adds it to the subject array at the next index.
 *    Returns the index.  Subject is not checked to see if it is a duplicate.
 *    At this point, it is too late for that.  You should have checked earlier.
 *
 * @param {Subject} subject_IN - subject we want to add to the subject array.
 * @returns {int} - index of subject in subject array.
 */
SOURCENET.SubjectStore.prototype.add_subject_to_array = function( subject_IN )
{
    alert( "NEED TO MAKE SubjectStore.add_subject_to_array()." );
} //-- END SOURCENET.SubjectStore method add_subject_to_array() --//


/**
 * Accepts a person ID - Checks to see if ID is a key in the 
 *
 * @param {Subject} subject_IN - subject we want to add to the subject array.
 * @returns {int} - index of subject in subject array.
 */
SOURCENET.SubjectStore.prototype.get_index_for_person_id = function( person_id_IN )
{
    
    // return reference.
    index_OUT = -1;
    
    // declare variables
    id_to_index_map = null
    is_in_map = false;
    
    // get id_to_index_map.
    id_to_index_map = this.id_to_subject_index_map[ person_id_IN ];
    
    // see if ID passed in is a key in this.id_to_subject_index_map.hasOwnProperty( my_person_id );
    is_in_map = id_to_index_map.hasOwnProperty( person_id_IN );
    if ( is_in_map == true )
    {
        
        // it is in the subject store.  retrieve index for this person ID.
        index_OUT = id_to_index_map[ person_id_IN ];
        
    }

    alert( "!NEED TO FINISH;" );
    
    return index_OUT;

} //-- END SOURCENET.SubjectStore method get_index_for_person_id() --//


//=====================//
// END SubjectStore
//=====================//


//=====================//
// Subject
//=====================//

// Subject constructor

/**
 * Represents a subject in an article.
 * @constructor
 */
SOURCENET.Subject = function()
{
    // instance variables
    this.subject_name = "";
    this.is_quoted = false;
    this.name_and_title = "";
    this.quote_text = "";
    this.person_id = null;
    //this.location_of_name = "";
} //-- END SOURCENET.Subject constructor --//

// Subject methods

/**
 * populates Subject object instance from form inputs.
 * @param {jquery element} form_element_IN - Form element that contains inputs we will use to populate this instance.
 * @returns {Array} - list of validation messages.  If empty, all is well.  If array.length > 0, then there were validation errors.
 */
SOURCENET.Subject.prototype.populate_from_form = function( form_element_IN )
{
    
    // return reference
    var validate_status_array_OUT = [];

    // declare variables
    var form_element = null;
    var temp_element = null;
    var my_subject_name = "";
    var my_is_quoted = false;
    var my_name_and_title = "";
    var my_quote_text = "";
    var my_person_id = null;
    var subject_name_input_element = null;

    // get form element
    form_element = form_element_IN
    
    // retrieve values from form inputs and store in instance.
    
    // subject-name
    temp_element = $( '#subject-name' );
    my_subject_name = temp_element.val();
    this.subject_name = my_subject_name;
    
    // is-quoted
    temp_element = $( '#is-quoted' );
    my_is_quoted = temp_element.prop( 'checked' );    
    this.is_quoted = my_is_quoted;

    // subject-name-and-title
    temp_element = $( '#subject-name-and-title' );
    my_name_and_title = temp_element.val();
    this.name_and_title = my_name_and_title;
    
    // source-quote-text
    temp_element = $( '#source-quote-text' );
    my_quote_text = temp_element.val();
    this.quote_text = my_quote_text;
    
    // id_person
    temp_element = $( '#id_person' );
    my_person_id = temp_element.val();
    this.person_id = my_person_id;

    alert( JSON.stringify( this ) )
    
    // validate
    validate_status_array_OUT = this.validate()
    
    // alert( "validate_status = " + validate_status )
    
    return validate_status_array_OUT;
    
} //-- END SOURCENET.Subject method populate_from_form() --//


/**
 * validates Subject object instance.
 * @returns {Array} - list of validation messages.  If empty, all is well.  If array.length > 0, then there were validation errors.
 */
SOURCENET.Subject.prototype.validate = function()
{

    // return reference
    var status_array_OUT = [];  // empty list = valid, non-empty list = list of error messages, invalid.

    // declare variables
    var my_name = "";
    var status_string = "";
    
    
    // must have a name
    my_name = this.subject_name;
    if ( ( my_name == null ) || ( my_name == "" ) )
    {
        // no name - invalid.
        status_array_OUT.push( "Must have a name." );
    }
    
    // convert list of status messages to string.
    //if ( status_list_OUT.length > 0 )
    //{
        
        // join the messages.
        //status_string = status_list_OUT.join( ", " );
        // alert( "status = " + status_string )
        
    //}
    
    return status_array_OUT;
    
} //-- END SOURCENET.Subject method validate() --//

//=====================//
// END Subject
//=====================//


//----------------------------------------------------------------------------//
// function definitions
//----------------------------------------------------------------------------//


/**
 * checks to see if SubjectStore instance already around.  If so, returns it.
 *    If not, creates one, stores it, then returns it.
 *
 * Preconditions: None.
 *
 * Postconditions: If SubjectStore instance not already present in
 *    SOURCENET.subject_store, one is created and stored there before it is
 *    returned.
 */
SOURCENET.get_subject_store = function()
{
    
    alert( "Getting Subject Store...eventually!" );
    
} //-- END function SOURCENET.get_subject_store() --//


/**
 * Event function that is called when coder is finished coding a particular
 *    subject and is ready to add him or her to the list of subjects in the
 *    article.
 *
 * Preconditions: Subject coding form should be filled out as thoroughly as
 *    possible.  At the least, must have a subject name.  If none present, the
 *    subject is invalid, will not be accepted.
 *
 * Postconditions: If subject accepted, after this function is called, the
 *    subject will be added to the internal structures to list and map subjects,
 *    and will also be added to the list of subjects who have been coded so far.
 */
SOURCENET.process_subject_coding = function()
{
    alert( "PROCESS SUBJECT CODING!!!" );
    
    // declare variables
    form_element = null;
    subject_instance = null;
    status_message_array = [];
    status_message_count = -1;
    status_string = "";

    // get form element.
    form_element = $( '#subject-coding' );
    
    // create Subject instance.
    subject_instance = new SOURCENET.Subject();
    
    // populate it from the form.
    status_message_array = subject_instance.populate_from_form( form_element );
    
    // valid?
    status_message_count = status_message_array.length
    if ( status_message_count == 0 )
    {
        
        // valid.
        alert( "Valid subject.  Adding to SubjectStore." );
        
    }
    else
    {
        
        // not valid - for now, output message(s).
        status_string = status_message_array.join( ", " );
        alert( "Subject not valid: " + status_string );
        
    }
    
} //-- END function process_subject_coding() --#


//----------------------------------------------------------------------------//
// jquery event handlers
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
                //alert( "selected text : " + selected_text );
                
                // get input
                selected_text_input = $( '#selected-text' )
                
                // set value
                selected_text_input.val( selected_text );
            }
        )
    }
);

// javascript to store selected text as source name.
// Get selected text / 選択部分のテキストを取得
$( document ).ready(
    function()
    {
        $( '#store-name' ).click(        
            function()
            {
                // declare variables
                var selected_text = "";
    
                // get selection
                selected_text = $.selection();
                //alert( "selected text : " + selected_text );
                $( '#subject-name' ).val( selected_text );
            }
        )
    }
);

// javascript to store selected text as source name + title.
// Get selected text / 選択部分のテキストを取得
$( document ).ready(
    function()
    {
        $( '#store-name-and-title' ).click(        
            function()
            {
                // declare variables
                var selected_text = "";
                var subject_name_and_title_element = null;
                var existing_text = "";
    
                // get selection
                selected_text = $.selection();
                //alert( "selected text : " + selected_text );
                
                // see if there is already something there.
                subject_name_and_title_element = $( '#subject-name-and-title' )
                existing_text = subject_name_and_title_element.val()
                //alert( "Existing text: " + existing_text )
                
                // something already there?
                if ( existing_text != "" )
                {

                    // yes - append new to the end.
                    subject_name_and_title_element.val( existing_text + " " + selected_text );
                    
                }
                else
                {
                    
                    // no - just overwrite.
                    subject_name_and_title_element.val( selected_text );
                    
                }

            }
        )
    }
);

// javascript to store selected text as source's quotation text.
// Get selected text / 選択部分のテキストを取得
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
                //alert( "selected text : " + selected_text );
                
                // get source-quote-text element.
                source_quote_text_element = $( '#source-quote-text' )
                
                // store selected text.
                source_quote_text_element.val( selected_text );
                
                // see if "is-quoted" is checked.
                is_quoted_element = $( '#is-quoted' )
                is_quoted = is_quoted_element.prop( 'checked' )

                // get contents of source-quote-text
                source_quote_text_value = source_quote_text_element.val()
                
                // quoted?
                if ( is_quoted == false )
                {
                    // not yet - got text?
                    if ( ( source_quote_text_value != null ) && ( source_quote_text_value != "" ) )
                    {
                        // yes - set checkbox.
                        is_quoted_element.prop( 'checked', true )
                    }
                } //-- END check to see if is-quoted checkbox checked --//
            } //-- END click() nested anonymous function. --//
        ) //-- END click() method call. --//
    } //-- END ready() nested anonymous function --//
); //-- END document.ready() call --//

// javascript to copy name from #source-name to the Lookup text field.
$( document ).ready(
    function()
    {
        $( '#lookup-subject-name' ).click(        
            function()
            {
                // declare variables
                var source_text = "";
                var person_lookup = "";
    
                // get selection
                source_text = $( '#subject-name' ).val();
                //alert( "source text : " + source_text );

                // get lookup text field,  place value, then change().
                person_lookup = $( '#id_person_text' )
                person_lookup.val( source_text );
                person_lookup.keyup()
                //person_lookup.click()
                //person_lookup.trigger('init-autocomplete');
            }
        )
    }
);