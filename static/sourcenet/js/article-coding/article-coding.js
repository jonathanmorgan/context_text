//============================================================================//
// javascript for article coding.
//============================================================================//

//----------------------------------------------------------------------------//
// !==> namespace!
//----------------------------------------------------------------------------//


var SOURCENET = SOURCENET || {};


//----------------------------------------------------------------------------//
// !==> namespaced variables
//----------------------------------------------------------------------------//


// JSON to prepopulate page if we are editing.
SOURCENET.subject_JSON = "";

// subject store used to keep track of subjects while coding.
SOURCENET.subject_store = null;


//----------------------------------------------------------------------------//
// !==> object definitions
//----------------------------------------------------------------------------//


//=====================//
// !----> SubjectStore
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
    var status_array_OUT = [];
    
    // declare variables.
    var is_ok_to_add = true;
    var validation_status_array = [];
    var validation_status_count = -1;
    var has_person_id = false
    var my_person_id = -1;
    var is_person_id_OK = false;
    var subject_person_id_index = -1;
    var my_subject_name = "";
    var is_subject_name_OK = false;
    var subject_name_index = -1;
    var subject_index = -1;
    var name_map_status_array = [];
    var id_map_status_array = [];
    
    // make sure we have a subject.
    if ( ( subject_IN !== undefined ) && ( subject_IN != null ) )
    {
        
        // got a subject.  Is it valid?
        validation_status_array = subject_IN.validate();
        validation_status_count = validation_status_array.length;
        if ( validation_status_count == 0 )
        {
            
            // valid.  Got a person ID?
            my_person_id = subject_IN.person_id;
            is_person_id_OK = SOURCENET.is_integer_OK( my_person_id, 1 );
            if ( is_person_id_OK == true )
            {
                
                // got a person ID.
                has_person_id = true;
                
                // Is that ID already in map of IDs to array indices?
                subject_person_id_index = this.get_index_for_person_id( my_person_id );
                if ( subject_person_id_index >= 0 )
                {
                    
                    // already in map...  Error.
                    is_ok_to_add = false;
                    status_array_OUT.push( "Person ID " + my_person_id + " already present in SubjectStore." );
                    
                }
                
            } //-- END check to see if person ID already present. --//
            
            // Got a subject name?
            my_subject_name = subject_IN.subject_name;
            is_subject_name_OK = SOURCENET.is_string_OK( my_subject_name );
            if ( is_subject_name_OK == true )
            {
                
                // subject name present (as it should be at this point).  See if
                //    this name is already in the SubjectStore.
                subject_name_index = this.get_index_for_subject_name( my_subject_name );
                if ( subject_name_index >= 0 )
                {
                    
                    // already in map...  Error.
                    is_ok_to_add = false;
                    status_array_OUT.push( "Subject name " + my_subject_name + " already present in SubjectStore." );
                    
                } //-- END check to see if subject's name already mapped to a subject --//
                
            }
            else
            {
                
                // no name! ERROR.
                is_ok_to_add = false;
                status_array_OUT.push( "Subject has no name.  Not sure how you got this far, but error." );
                
            } //-- END check to see if subject's name present. --//

            // OK to add?
            if ( is_ok_to_add == true )
            {
                
                // no errors so far...  Add subject to array.
                subject_index = this.add_subject_to_array( subject_IN );
                
                // got an index back?
                if ( subject_index > -1 )
                {
                    
                    // got one.  Now, add to map of name and ID to index.
                    
                    // add to name map.
                    name_map_status_array = this.update_subject_in_name_map( subject_IN, subject_index );
                    
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
                            
                            // yes.  Add mapping of person ID to subject array
                            //    index.
                            id_map_status_array = this.update_subject_in_person_id_map( subject_IN, subject_index );
                            
                            // any errors?
                            if ( id_map_status_array.length > 0 )
                            {
                                
                                // yes.  Add to status array, fall out.
                                status_array_OUT = status_array_OUT.concat( id_map_status_array );
                            
                            } //-- END check to see if errors from adding to id map --//
                            
                        } //-- END check to see if has person ID --//
                        
                    } //-- END check to see if errors adding subject to name map. --//
                    
                }
                else
                {
                
                    // no.  Interesting.  Error.
                    status_array_OUT.push( "attempt to add subject to Array resulted in no index.  Not good." );
                    
                } //-- END check to see if index of subject greater than -1. --//
                
            } //-- END check to see if OK to add? --//
            
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
 * Assumptions: We always push subjects onto array, never remove.  Index should
 *    equal this.subject_array.length - 1, but keep separate variables as well
 *    as a sanity check.
 *
 * @param {Subject} subject_IN - subject we want to add to the subject array.
 * @returns {int} - index of subject in subject array.
 */
SOURCENET.SubjectStore.prototype.add_subject_to_array = function( subject_IN )
{
    
    // return reference
    var index_OUT = -1;
    
    // declare variables
    var me = "SOURCENET.SubjectStore.prototype.add_subject_to_array";
    var my_subject_array = []
    var my_next_index = -1;
    var my_latest_index = -1;
    var subject_array_length = -1;
    
    // got a subject?
    if ( ( subject_IN !== undefined ) && ( subject_IN != null ) )
    {
        
        // yes - get relevant variables.
        my_subject_array = this.subject_array;
        my_next_index = this.next_subject_index;
        my_latest_index = this.latest_subject_index;
    
        // push subject onto array.
        my_subject_array.push( subject_IN );
        
        // increment next index, make sure it equals length - 1.
        my_next_index += 1;
        subject_array_length = my_subject_array.length;
        if ( my_next_index != subject_array_length )
        {
            
            // hmmm... Disconnect.  Next index should equal length of current
            //    array since arrays are 0-indexed and we only ever add one.
            //    Output alert.
            alert( "In " + me + "(), next index ( " + my_next_index + " ) not equal to array length ( " + subject_array_length + " )." );
            
        }
                    
        // Store next and latest values based on array length.
        this.next_subject_index = subject_array_length;
        
        // return index of length of array minus 1.
        index_OUT = subject_array_length -1
        this.latest_subject_index = index_OUT;

    }
    else
    {
        
        // no.  Return -1.
        index_OUT = -1;
        
    } //-- END check to see if subject instance.
    
    return index_OUT;
    
} //-- END SOURCENET.SubjectStore method add_subject_to_array() --//


/**
 * Accepts a person ID - Checks to see if ID is a key in the map of person IDs
 *    to indexes in the master subject array.  If so, returns that index.  If
 *    not, returns -1.
 *
 * @param {int} person_id_IN - person ID of subject we want to find in subject
 *    array.
 * @returns {int} - index of subject in subject array, or -1 if person ID not
 *    found.
 */
SOURCENET.SubjectStore.prototype.get_index_for_person_id = function( person_id_IN )
{
    
    // return reference.
    var index_OUT = -1;
    
    // declare variables
    var is_person_id_OK = false;
    var id_to_index_map = null
    var is_in_map = false;
    
    // got an ID?
    is_person_id_OK = SOURCENET.is_integer_OK( person_id_IN, 1 )
    if ( is_person_id_OK == true )
    {
        
        // get id_to_index_map.
        id_to_index_map = this.id_to_subject_index_map;
        
        // see if ID passed in is a key in this.id_to_subject_index_map.hasOwnProperty( my_person_id );
        is_in_map = id_to_index_map.hasOwnProperty( person_id_IN );
        if ( is_in_map == true )
        {
            
            // it is in the subject store.  retrieve index for this person ID.
            index_OUT = id_to_index_map[ person_id_IN ];
            
        }
        else
        {
            
            // not in map.  Return -1.
            index_OUT = -1;
            
        }
        
    }
    else
    {
        
        // no ID passed in.  Return -1.
        index_OUT = -1;
        
    } //-- END check to see if ID passed in. --//

    return index_OUT;

} //-- END SOURCENET.SubjectStore method get_index_for_person_id() --//


/**
 * Accepts a subject name - Checks to see if name string is a key in the map of
 *    subject names to indexes in the master subject array.  If so, returns that
 *    index.  If not, returns -1.
 *
 * @param {string} subject_name_IN - name string for subject we want to find in
 *    subject array.
 * @returns {int} - index of subject in subject array, or -1 if subject name not
 *    found.
 */
SOURCENET.SubjectStore.prototype.get_index_for_subject_name = function( subject_name_IN )
{
    
    // return reference.
    var index_OUT = -1;
    
    // declare variables
    var is_subject_name_OK = false;
    var name_to_index_map = null;
    var is_in_map = false;
    
    // got a name?
    is_subject_name_OK = SOURCENET.is_string_OK( subject_name_IN );
    if ( is_subject_name_OK == true )
    {

        // get id_to_index_map.
        name_to_index_map = this.name_to_subject_index_map;
        
        // see if ID passed in is a key in this.id_to_subject_index_map.hasOwnProperty( my_person_id );
        is_in_map = name_to_index_map.hasOwnProperty( subject_name_IN );
        if ( is_in_map == true )
        {
            
            // it is in the subject store.  retrieve index for this person ID.
            index_OUT = name_to_index_map[ subject_name_IN ];
            
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

} //-- END SOURCENET.SubjectStore method get_index_for_subject_name() --//


/**
 * Accepts an index into the subject array - Checks to see if index is present
 *    in master person array, if so, returns what is in that index.  If not,
 *    returns null.
 *
 * @param {int} index_IN - index in subject array whose contents we want.
 * @returns {SOURCENET.Subject} - instance of subject at the index passed in.
 */
SOURCENET.SubjectStore.prototype.get_subject_at_index = function( index_IN )
{
    
    // return reference.
    var subject_OUT = null;
    
    // declare variables
    var is_index_OK = false;
    var subject_array = -1;
    
    // got an index?
    is_index_OK = SOURCENET.is_integer_OK( index_IN, 0 );
    if ( is_index_OK == true )
    {
        
        // I think so...  Get subject array
        subject_array = this.subject_array;
        
        //  check to see if index present.
        subject_OUT = subject_array[ index_IN ];
        
        // is it undefined?
        if ( subject_OUT === undefined )
        {
            
            // it is.  For this function, return null instead.
            subject_OUT = null;
            
        } //-- END check to see if undefined --//
        
    }
    else
    {
        
        // no valid index - error - return null
        subject_OUT = null;
        
    } //-- END check to see if valid index passed in. --//
    
    return subject_OUT;

} //-- END SOURCENET.SubjectStore method get_subject_at_index() --//


/**
 * Accepts a person ID - Checks to see if index in master person array tied to
 *    the person ID.  If so, retrieves subject at that index and returns it.  If
 *    not, returns null.
 *
 * @param {string} subject_name_IN - name string of subject we want to find in
 *    subject array.
 * @returns {SOURCENET.Subject} - instance of subject related to the person ID passed in.
 */
SOURCENET.SubjectStore.prototype.get_subject_for_name = function( subject_name_IN )
{
    
    // return reference.
    var subject_OUT = null;
    
    // declare variables
    var is_subject_name_OK = false;
    var subject_index = -1;
    
    // got a name?
    is_subject_name_OK = SOURCENET.is_string_OK( subject_name_IN );
    if ( is_subject_name_OK == true )
    {

        // I think so...  See if there is an entry in name map for this name.
        subject_index = this.get_index_for_subject_name( subject_name_IN );
        
        // is subject_index present, and greater than -1?
        if ( ( subject_index !== undefined ) && ( subject_index != null ) && ( subject_index >= 0 ) )
        {
            
            // looks like there is an index.  Get subject at that index.
            subject_OUT = this.get_subject_at_index( subject_index );
            
        }
        else
        {
            
            // not present in map object.  Return null.
            subject_OUT = null;
            
        }
        
    }
    else
    {
        
        // no name - error - return null
        subject_OUT = null;
        
    }
    
    return subject_OUT;

} //-- END SOURCENET.SubjectStore method get_subject_for_name() --//


/**
 * Accepts a person ID - Checks to see if index in master person array tied to
 *    the person ID.  If so, retrieves subject at that index and returns it.  If
 *    not, returns null.
 *
 * @param {int} person_id_IN - person ID of subject we want to find in subject
 *    array.
 * @returns {SOURCENET.Subject} - instance of subject related to the person ID passed in.
 */
SOURCENET.SubjectStore.prototype.get_subject_for_person_id = function( person_id_IN )
{
    
    // return reference.
    var subject_OUT = null;
    
    // declare variables
    var is_person_id_OK = false;
    var subject_index = -1;
    
    // got an ID?
    is_person_id_OK = SOURCENET.is_integer_OK( person_id_IN, 1 );
    if ( is_person_id_OK == true )
    {
        
        // I think so...  See if there is an entry in ID map for this ID.
        subject_index = this.get_index_for_person_id( person_id_IN );
        
        // is subject_index present, and greater than -1?
        if ( ( subject_index !== undefined ) && ( subject_index != null ) && ( subject_index >= 0 ) )
        {
            
            // looks like there is an index.  Get subject at that index.
            subject_OUT = this.get_subject_at_index( subject_index );
            
        }
        else
        {
            
            // not present in map object.  Return null.
            subject_OUT = null;
            
        }
        
    }
    else
    {
        
        // no ID - error - return null
        subject_OUT = null;
        
    }
    
    return subject_OUT;

} //-- END SOURCENET.SubjectStore method get_subject_for_person_id() --//


/**
 * Accepts a Subject instance and that subject's index in the subject array.
 *    If both passed in, updates mapping of name to index in name_to_index_map
 *    in SubjectStore.  If not, does nothing.
 *
 * @param {Subject} subject_IN - subject we want to add to update in the map of subject name strings to indexes in subject array.
 * @param {int} index_IN - index in subject array we want name associated with.  If -1 passed in, effectively removes subject from map.
 * @returns {Array} - Array of status messages - empty array = success.
 */
SOURCENET.SubjectStore.prototype.update_subject_in_name_map = function( subject_IN, index_IN )
{
    
    // return reference
    var status_array_OUT = [];
    
    // declare variables.
    var me = "SOURCENET.SubjectStore.prototype.update_subject_in_name_map";
    var subject_name = "";
    var is_subject_name_OK = false;
    var my_name_to_index_map = {};
    
    // got a subject?
    if ( ( subject_IN !== undefined ) && ( subject_IN != null ) )
    {
        
        // yes - get relevant variables.
        my_name_to_index_map = this.name_to_subject_index_map;
        
        // get subject name
        subject_name = subject_IN.subject_name;
        
        // got a name?
        is_subject_name_OK = SOURCENET.is_string_OK( subject_name );
        if ( is_subject_name_OK == true )
        {
            
            // yes.  Set value for that name in map.
            my_name_to_index_map[ subject_name ] = index_IN;
            
        }
        else
        {
            
            // no - error.
            status_array_OUT.push( "In " + me + "(): no name in subject.  Can't do anything." );
            
        }

    }
    else
    {
        
        // no.  Error.
        status_array_OUT.push( "No subject passed in.  What?" );
        
    } //-- END check to see if subject instance.
    
    return status_array_OUT;
    
} //-- END SOURCENET.SubjectStore method update_subject_in_name_map() --//


/**
 * Accepts a Subject instance and that subject's index in the subject array.
 *    If both passed in, checks to make sure that the subject record has a
 *    person ID.  If so, updates mapping of person ID to index in
 *    id_to_subject_index_map in SubjectStore.  If either no subject or no
 *    person ID, does nothing.
 *
 * @param {Subject} subject_IN - subject we want to update in the map of person IDs to subject array indexes.
 * @param {int} index_IN - index in subject array we want name associated with.  If -1 passed in, effectively removes subject from map.
 * @returns {Array} - Array of status messages - empty array = success.
 */
SOURCENET.SubjectStore.prototype.update_subject_in_person_id_map = function( subject_IN, index_IN )
{
    
    // return reference
    var status_array_OUT = [];
    
    // declare variables.
    var me = "SOURCENET.SubjectStore.prototype.update_subject_in_person_id_map";
    var subject_person_id = -1;
    var is_person_id_OK = false;
    var my_person_id_to_index_map = {};
    
    // got a subject?
    // got a subject?
    if ( ( subject_IN !== undefined ) && ( subject_IN != null ) )
    {
        
        // yes - get relevant variables.
        my_person_id_to_index_map = this.id_to_subject_index_map;
        
        // get subject name
        subject_person_id = subject_IN.person_id;
        
        // got a person id?
        is_person_id_OK = SOURCENET.is_integer_OK( subject_person_id, 1 )
        if ( is_person_id_OK == true )
        {
            
            // yes.  Set value for that name in map.
            my_person_id_to_index_map[ subject_person_id ] = index_IN;
            
        }
        else
        {
            
            // no - error.
            status_array_OUT.push( "In " + me + "(): no name in subject.  Can't do anything." );
            
        }

    }
    else
    {
        
        // no.  Error.
        status_array_OUT.push( "No subject passed in.  What?" );
        
    } //-- END check to see if subject instance.
    
    return status_array_OUT;

} //-- END SOURCENET.SubjectStore method update_subject_in_person_id_map() --//


//=====================//
// END SubjectStore
//=====================//


//=====================//
// !----> Subject
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
    my_person_id = parseInt( my_person_id, 10 );
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
// !==> function definitions
//----------------------------------------------------------------------------//


/**
 * Clears out coding form and status message area, and optionally displays a
 *    status message if one passed in.
 *
 * Preconditions: for anything to appear, SOURCENET.subject_store must have been
 *    initialized and at least one source added to it.
 *
 * @param {string} status_message_IN - message to place in status area.  If undefined, null, or "", no message output.
 */
SOURCENET.clear_coding_form = function( status_message_IN )
{
    
    // declare variables.
    var me = "SOURCENET.clear_coding_form";
    var is_status_message_OK = false;
    var status_message_array = [];
    
    // for now, display by alert()-ing JSON string.
    alert( "Eventually will clear coding form.  Not just yet..." );
    
    // !TODO - clear the coding form.
    
    // !TODO - clear the status message area.
    
    // if message, output it.
    is_status_message_OK = SOURCENET.is_string_OK( status_message_IN );
    if ( is_status_message_OK == true )
    {
        
        // make status message array.
        status_message_array = [];
        status_message_array.push( status_message_IN );
        
        // output it.
        SOURCENET.output_status_messages( status_message_array );
        
    } //-- END check to see if status message is OK. --//

    
} //-- END function SOURCENET.clear_coding_form() --//


/**
 * Repaints the area where coded subjects are displayed.
 *
 * Preconditions: for anything to appear, SOURCENET.subject_store must have been
 *    initialized and at least one source added to it.
 */
SOURCENET.display_subjects = function()
{
    
    // declare variables.
    var me = "SOURCENET.display_subjects";
    var my_subject_store = null;
    
    // get subject store
    my_subject_store = SOURCENET.get_subject_store();
    
    // for now, display by alert()-ing JSON string.
    alert( "SubjectStore = " + JSON.stringify( my_subject_store ) );
    
    // !TODO - repaint list of subjects.
    
} //-- END function SOURCENET.display_subjects() --//


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
    
    // return reference
    var instance_OUT = null;
    
    // declare variables
    var me = "SOURCENET.get_subject_store";
    var my_subject_store = null;
    
    // see if there is already a subject store.
    my_subject_store = SOURCENET.subject_store;
    if ( my_subject_store == null )
    {
        
        // nope.  Make one, store it, then recurse.
        my_subject_store = new SOURCENET.SubjectStore();
        SOURCENET.subject_store = my_subject_store;
        instance_OUT = SOURCENET.get_subject_store();
        
    }
    else
    {
        
        instance_OUT = my_subject_store;
        
    }
    
    return instance_OUT;
    
} //-- END function SOURCENET.get_subject_store() --//


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
SOURCENET.is_string_OK = function( string_IN )
{
    
    // return reference
    var is_OK_OUT = true;
    
    if ( ( string_IN !== undefined ) && ( string_IN != null ) && ( string_IN != "" ) )
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
    
} //-- END function SOURCENET.is_string_OK() --//


/**
 * Clears out coding form and status message area, and optionally displays a
 *    status message if one passed in.
 *
 * @param {Array:string} status_message_IN - array of messages to place in status area.  If undefined, null, or [], no messages output.
 */
SOURCENET.output_status_messages = function( status_message_array_IN )
{
    
    // declare variables.
    var me = "SOURCENET.output_status_messages";
    
    // for now, display by alert()-ing JSON string.
    alert( "Status messages: " + JSON.stringify( status_message_array_IN ) );
    
    // !TODO - if messages, output them.
    
} //-- END function SOURCENET.output_status_messages() --//


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
    var form_element = null;
    var subject_instance = null;
    var status_message_array = [];
    var status_message_count = -1;
    var status_string = "";
    var subject_store = null;
    var subject_add_message_array = [];
    var subject_add_error_count = -1;

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
        
        // get subject store
        subject_store = SOURCENET.get_subject_store();
        
        // add subject
        subject_add_message_array = subject_store.add_subject( subject_instance );
        
        // errors?
        subject_add_error_count = subject_add_message_array.length;
        if ( subject_add_error_count == 0 )
        {
            
            // no errors.

            // output subject store
            SOURCENET.display_subjects();
                    
            // clear the coding form.
            SOURCENET.clear_coding_form( "Success!" );

        }
        else
        {
            
            // errors - output messages.
            SOURCENET.output_status_messages( subject_add_message_array );
            
        } //-- END check for errors adding subject to SubjectStore. --//
        
    }
    else
    {
        
        // not valid - for now, output message(s).
        status_string = status_message_array.join( ", " );
        alert( "Subject not valid: " + status_string );
        
    }
    
} //-- END function SOURCENET.process_subject_coding() --#


//----------------------------------------------------------------------------//
// !==> jquery event handlers
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