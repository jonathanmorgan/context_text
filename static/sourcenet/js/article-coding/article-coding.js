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

// DEBUG!
SOURCENET.debug_flag = true;


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
            SOURCENET.log_message( "In " + me + "(), next index ( " + my_next_index + " ) not equal to array length ( " + subject_array_length + " )." );
            
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
    var my_subject_array = -1;
    
    // got an index?
    is_index_OK = SOURCENET.is_integer_OK( index_IN, 0 );
    if ( is_index_OK == true )
    {
        
        // I think so...  Get subject array
        my_subject_array = this.subject_array;
        
        //  check to see if index present.
        subject_OUT = my_subject_array[ index_IN ];
        
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
 * Accepts an index into the subject array - Retrieves subject at that index.
 *    If null, nothing there, nothing to remove.  If not null, makes that index
 *    in the array refer to null.  Then, looks for the index value in the values
 *    stored within the name-to-index and person-id-to-index maps.  If index
 *    value found, each key-value pair with the index as the value is removed.
 *    Returns a list of messages.  If empty, success.
 *
 * Postconditions: Also logs warnings to console.log(), so if you want to see if
 *    there are any warnings (tells things like whether the subject exists at
 *    the index passed in, if there might have been more than one name or person
 *    ID that reference the index, etc.).  If it finds bad data, this method
 *    will clean it up.  When we remove a subject at an index, removes all
 *    references to that index in the name and ID to index maps, even if there
 *    are mutiple name or IDs that map.
 *
 * @param {int} index_IN - index in subject array that contains subject we want to remove.
 * @returns {Array:string} - array of status messages that result from processing.
 */
SOURCENET.SubjectStore.prototype.remove_subject_at_index = function( index_IN )
{
    
    // return reference.
    var status_array_OUT = [];
    
    // declare variables
    var me = "SOURCENET.SubjectStore.remove_subject_at_index";
    var selected_index = -1;
    var is_index_OK = false;
    var my_subject_array = -1;
    var subject_to_remove = null;
    var my_subject_name = "";
    var my_subject_person_id = -1;
    var name_to_index_map = {};
    var person_id_to_index_map = {};
    var current_key = "";
    var current_value = "";
    
    // make sure index is an integer.
    selected_index = parseInt( index_IN );
    
    // got an index?
    is_index_OK = SOURCENET.is_integer_OK( selected_index, 0 );
    if ( is_index_OK == true )
    {
        
        // I think so...  Get subject array
        my_subject_array = this.subject_array;
        
        //  check to see if index present.
        subject_to_remove = my_subject_array[ selected_index ];
        
        // is it undefined or null?
        if ( subject_to_remove === undefined )
        {
            
            // it is undefined.  Index not present in array.
            SOURCENET.log_message( "In " + me + "(): Index " + selected_index + " is undefined - not present in array." );
            my_subject_name = null;
            my_subject_person_id = null;
            
        }
        else if ( subject_to_remove == null )
        {
            
            // it is null.  Subject already removed at this index.
            SOURCENET.log_message( "In " + me + "(): Subject at index " + selected_index + " already removed ( == null )." );
            my_subject_name = null;
            my_subject_person_id = null;
            
        }
        else
        {
            
            // there is a subject here.  Get name and person id.
            my_subject_name = subject_to_remove.subject_name;
            my_subject_person_id = subject_to_remove.person_id;
            
            // and, set the index to null.
            my_subject_array[ selected_index ] = null;
            
        } //-- END check to see if subject instance referenced by index is undefined or null. --//
            
            
        // look for values that reference index in:
        // - this.name_to_subject_index_map
        // - this.id_to_subject_index_map
        
        // always check, even of index reference is null or undefined, just as a
        //    sanity check to keep the maps clean.

        // name-to-index map --> this.name_to_subject_index_map
        name_to_index_map = this.name_to_subject_index_map;
        
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
                //    name from the subject.
                if ( current_key != my_subject_name )
                {
                    
                    // matching index, but key doesn't match.  Output message.
                    SOURCENET.log_message( "In " + me + "(): Subject name key \"" + current_key + "\" references index " + current_value + ".  Key should be \"" + my_subject_name + "\".  Hmmm..." );
                    
                }
                
                // remove key-value pair from object.
                delete name_to_index_map[ current_key ];
                
            } //-- END check to see if vkey references the index we've been asked to remove --//
            
        } //-- END loop over keys in this.name_to_subject_index_map --//
        
        // person ID to index map --> this.id_to_subject_index_map
        person_id_to_index_map = this.id_to_subject_index_map;
        
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
                //    person ID from the subject.
                if ( current_key != my_subject_person_id )
                {
                    
                    // matching index, but key doesn't match.  Output message.
                    SOURCENET.log_message( "In " + me + "(): Subject person ID key \"" + current_key + "\" references index " + current_value + ".  Key should be \"" + my_subject_person_id + "\".  Hmmm..." );
                    
                }
                
                // remove key-value pair from object.
                delete person_id_to_index_map[ current_key ];
                
            } //-- END check to see if key references the index we've been asked to remove --//
            
        } //-- END loop over keys in this.name_to_subject_index_map --//
            
    }
    else //-- index is not OK. --//
    {
        
        // no valid index - error - return null
        status_array_OUT.push( "Index " + index_IN + " is not valid - could not remove subject." );
        
    } //-- END check to see if valid index passed in. --//
    
    return status_array_OUT;

} //-- END SOURCENET.SubjectStore method remove_subject_at_index() --//


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
    var me = "SOURCENET.Subject.populate_from_form"
    var form_element = null;
    var temp_element = null;
    var my_subject_name = "";
    var my_is_quoted = false;
    var my_name_and_title = "";
    var my_quote_text = "";
    var my_person_id = null;
    var is_person_id_OK = false;
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
    
    // element found?
    if ( temp_element.length > 0 )
    {    
    
        // get person ID from element.
        my_person_id = temp_element.val();
        
        // is it an OK string?
        is_person_id_OK = SOURCENET.is_string_OK( my_person_id )
        if ( is_person_id_OK == true )
        {

            // looks OK (non-empty).  Convert to int and store it.
            my_person_id = parseInt( my_person_id, 10 );
            this.person_id = my_person_id;

        } //-- END check to see if person_id value present. --//
    
    } //-- END check to see if id_person element present in HTML. --//

    SOURCENET.log_message( "In " + me + "(): Subject JSON = " + JSON.stringify( this ) )
    
    // validate
    validate_status_array_OUT = this.validate()
    
    // SOURCENET.log_message( "validate_status = " + validate_status )
    
    return validate_status_array_OUT;
    
} //-- END SOURCENET.Subject method populate_from_form() --//


/**
 * Converts subject to a string value.
 */
SOURCENET.Subject.prototype.to_string = function()
{
    
    // return reference
    var value_OUT = "";
    
    // declare variables.
    var my_person_id = -1;
    var is_person_id_OK = false
    var my_subject_name = "";
    var am_I_quoted = false;
    
    // got person ID?
    my_person_id = this.person_id;
    is_person_id_OK = SOURCENET.is_integer_OK( my_person_id, 1 );
    if ( is_person_id_OK == true )
    {
        value_OUT += my_person_id;
    }
    else
    {
        value_OUT += "new";
    }
    value_OUT += " - ";
    
    // name.
    my_subject_name = this.subject_name;
    value_OUT += my_subject_name;
    
    // subject type
    am_I_quoted = this.is_quoted;
    if( am_I_quoted == true )
    {
        value_OUT += " - source";
    }
    else
    {
        value_OUT += " - subject";
    }
    
    return value_OUT;
    
} //-- END SOURCENET.Subject method to_string() --//


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
        // SOURCENET.log_message( "status = " + status_string )
        
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
    var temp_element = null;
    var on_deck_person_element = null;
    
    // clear the coding form.
    
    // subject-name
    temp_element = $( '#subject-name' );
    temp_element.val( "" );
    
    // is-quoted
    temp_element = $( '#is-quoted' );
    temp_element.prop( 'checked', false );    

    // subject-name-and-title
    temp_element = $( '#subject-name-and-title' );
    temp_element.val( "" );
    
    // source-quote-text
    temp_element = $( '#source-quote-text' );
    temp_element.val( "" );
    
    // id_person
    temp_element = $( '#id_person' );
    temp_element.val( "" );
    
    // clear out <div> inside <div id="id_person_on_deck">.
    
    // get on-deck <div>.
    on_deck_person_element = $( '#id_person_on_deck' );
    
    // remove anonymous <div> inside.
    on_deck_person_element.find( 'div' ).remove();
    
    // add a new empty div.
    temp_element = $( '<div></div>' );
    on_deck_person_element.append( temp_element );
    
    // make status message array (empty message will clear status area).
    status_message_array = [];
    status_message_array.push( status_message_IN );
    
    // output it.
    SOURCENET.output_status_messages( status_message_array );
    
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
    var li_id_prefix = "";
    var my_subject_store = null;
    var subject_list_ul_element = null;
    var subject_index = -1;
    var subject_count = -1;
    var current_subject = null;
    var current_li_id = "";
    var current_li_selector = "";
    var current_li_element = null;
    var current_li_element_count = -1;
    var got_subject = false;
    var subject_string = "";
    var got_li = false;
    var do_create_li = false;
    var do_update_li = false;
    var do_remove_li = false;
    var li_contents = "";
    var button_element = null;
    
    // initialize variables
    li_id_prefix = "subject-";
    
    // get subject store
    my_subject_store = SOURCENET.get_subject_store();
    
    // for now, display by SOURCENET.log_message()-ing JSON string.
    //SOURCENET.log_message( "In " + me + "(): SubjectStore = " + JSON.stringify( my_subject_store ) );
    
    // get <ul id="subject-list-ul" class="subjectListUl">
    subject_list_ul_element = $( '#subject-list-ul' );
    
    // loop over the subjects in the list.
    subject_count = my_subject_store.subject_array.length;
    SOURCENET.log_message( "In " + me + "(): Subject Count = " + subject_count );
    for( subject_index = 0; subject_index < subject_count; subject_index++ )
    {
        
        // initialize variables.
        got_subject = false;
        got_li = false;
        do_create_li = false;
        do_update_li = false;
        do_remove_li = false;
        button_element = null;
        
        // get subject.
        current_subject = my_subject_store.get_subject_at_index( subject_index );

        // got subject?
        if ( current_subject != null )
        {
            // yes - set flag, update subject_string.
            got_subject = true;
            subject_string = current_subject.to_string();
            
        }
        else
        {
            // SOURCENET.log_message( "In " + me + "(): no subject for index " + subject_index );
            subject_string = "null";
        } //-- END check to see if subject --//
        
        SOURCENET.log_message( "In " + me + "(): Subject " + subject_index + ": " + subject_string );
        
        // try to get <li> for that index.
        current_li_id = li_id_prefix + subject_index;
        current_li_selector = "#" + current_li_id;
        current_li_element = subject_list_ul_element.find( current_li_selector );
        current_li_element_count = current_li_element.length;
        //SOURCENET.log_message( "DEBUG: li element: " + current_li_element + "; length = " + current_li_element_count );
        
        // matching <li> found?
        if ( current_li_element_count > 0 )
        {
            
            // yes - set flag.
            got_li = true;

        } //-- END check to see if <li> --//
        
        // based on subject and li, what do we do?
        if ( got_li == true )
        {
            
            //SOURCENET.log_message( "In " + me + "(): FOUND <li> for " + current_li_id );
            // got subject?
            if ( got_subject == true )
            {
                
                // yes.  convert to string and replace value, in case there have
                //    been changes.
                do_create_li = false;
                do_update_li = true;
                do_remove_li = false;
                
            }
            else
            {
                
                // no subject - remove <li>
                do_create_li = false;
                do_update_li = false;
                do_remove_li = true;                
                
            }
            
        }
        else //-- no <li> --//
        {
            
            //SOURCENET.log_message( "In " + me + "(): NO <li> for " + current_li_id );
            // got subject?
            if ( got_subject == true )
            {
                
                // yes.  convert to string and replace value, in case there have
                //    been changes.
                do_create_li = true;
                do_update_li = true;
                do_remove_li = false;
                
            }
            else
            {
                
                // no subject - nothing to do.
                do_create_li = false;
                do_update_li = false;
                do_remove_li = false;                
                
            }

        } //-- END check to see if <li> for current subject. --//
        
        // Do stuff!
        
        SOURCENET.log_message( "In " + me + "(): WHAT TO DO?: do_create_li = " + do_create_li + "; do_update_li = " + do_update_li + "; do_remove_li = " + do_remove_li )
        
        // crate new <li>?
        if ( do_create_li == true )
        {
            
            // create li with id = li_id_prefix + subject_index, store in
            //    current_li_element.
            current_li_element = $( '<li>Empty</li>' )
            current_li_element.attr( "id", li_id_prefix + subject_index );
            
            // prepend it to the subject_list_ul_element
            subject_list_ul_element.prepend( current_li_element )
            
        } //-- END check to see if do_create_li --//
        
        // update contents of <li>?
        if ( do_update_li == true )
        {
            
            // for now, just place subject string in <li>.
            li_contents = subject_string;
            
            // !TODO - add "Delete" button
            // (and other stuff needed for that to work.)
            li_contents += '<input type="button" id="remove-subject-' + subject_index + '" name="remove-subject-' + subject_index + '" value="Remove" onclick="SOURCENET.remove_subject( ' + subject_index + ' )" />'
            
            current_li_element.html( li_contents );
            
        } //-- END check to see if do_update_li --//
        
        // delete <li>?
        if ( do_remove_li == true )
        {
            
            // delete <li>.
            current_li_element.remove()
            
        } //-- END check to see if do_delete_li --//
        
    } //-- END loop over subjects in list --//
    
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
 * Accepts a message.  If console.log() is available, calls that.  If not, does
 *    nothing.
 */
SOURCENET.log_message = function( message_IN )
{
    
    // declare variables
    output_flag = true;
    
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
            current_message = status_message_array_IN[ message_index ]
            
            // create <li>, append to <ul>.
            message_li_element = $( '<li>' + current_message + '</li>' )
            message_li_element.attr( "id", "message-" + message_index );
            
            // append it to the message_area_ul_element
            message_area_ul_element.append( message_li_element )
            
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
    // declare variables
    var me = "SOURCENET.process_subject_coding";
    var form_element = null;
    var subject_instance = null;
    var status_message_array = [];
    var status_message_count = -1;
    var status_string = "";
    var subject_store = null;
    var subject_add_message_array = [];
    var subject_add_error_count = -1;

    SOURCENET.log_message( "In " + me + "(): PROCESS SUBJECT CODING!!!" );
    
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
        SOURCENET.log_message( "In " + me + "(): Valid subject.  Adding to SubjectStore." );
        
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
            SOURCENET.clear_coding_form( "Added: " + subject_instance.to_string() );

        }
        else
        {
            
            // errors - output messages.
            SOURCENET.output_status_messages( subject_add_message_array );
            
        } //-- END check for errors adding subject to SubjectStore. --//
        
    }
    else
    {
        
        // not valid - for now, add message overall status message.
        status_message_array.push( "Subject not valid." );
        
    }
    
    // got any messages?
    status_message_count = status_message_array.length;
    if ( status_message_count > 0 )
    {
        
        // yes, there are messages.  Output them.
        SOURCENET.output_status_messages( status_message_array )
        
    } //-- END check to see if messages --//    
    
} //-- END function SOURCENET.process_subject_coding() --#


/**
 * Accepts the index of a subject in the SubjectStore's subject_array that one
 *    wants removed.  Gets the SubjectStore and calls the
 *    remove_subject_at_index() method on it to remove the subject, then calls
 *    SOURCENET.display_subjects() to repaint the list of subjects.  If any
 *    status messages, outputs them at the end using
 *    SOURCENET.output_status_messages()
 */
SOURCENET.remove_subject = function( subject_index_IN )
{
    
    // declare variables
    var me = "SOURCENET.remove_subject";
    var selected_index = -1;
    var is_index_OK = false;
    var status_message_array = [];
    var status_message_count = -1;
    var subject_store = null;
    var subject_remove_message_array = [];
    var subject_remove_error_count = -1;

    // make sure index is an integer.
    selected_index = parseInt( subject_index_IN );
    
    // got an index?
    is_index_OK = SOURCENET.is_integer_OK( selected_index, 0 );
    if ( is_index_OK == true )
    {
        
        // get subject store
        subject_store = SOURCENET.get_subject_store();
        
        // remove subject
        subject_remove_message_array = subject_store.remove_subject_at_index( selected_index );
        
        SOURCENET.log_message( "In " + me + "(): Subject Store: " + JSON.stringify( subject_store ) );
        
        // errors?
        subject_remove_error_count = subject_remove_message_array.length;
        if ( subject_remove_error_count == 0 )
        {
            
            // no errors.

            // output subject store
            SOURCENET.display_subjects();
            
            // add status message.
            status_message_array.push( "Removed subject at index " + selected_index );
            
        }
        else
        {
            
            // errors - append to status_message_array.
            status_message_array = status_message_array.concat( subject_remove_message_array );
            
        } //-- END check for errors adding subject to SubjectStore. --//
        
    }
    else
    {
        
        // not valid - for now, output message(s).
        status_message_array.push( "Index value of " + selected_index + " is not valid.  Can't remove subject." );
        
    }
    
    // got any messages?
    status_message_count = status_message_array.length;
    if ( status_message_count > 0 )
    {
        
        // yes, there are messages.  Output them.
        SOURCENET.output_status_messages( status_message_array )
        
    } //-- END check to see if messages --//
        
} //-- END function SOURCENET.remove_subject --//


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
                //SOURCENET.log_message( "selected text : " + selected_text );
                
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
                selected_text = selected_text.trim();
                //SOURCENET.log_message( "selected text : " + selected_text );
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
                selected_text = selected_text.trim();
                //SOURCENET.log_message( "selected text : " + selected_text );
                
                // see if there is already something there.
                subject_name_and_title_element = $( '#subject-name-and-title' )
                existing_text = subject_name_and_title_element.val()
                //SOURCENET.log_message( "Existing text: " + existing_text )
                
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
                selected_text = selected_text.trim();
                //SOURCENET.log_message( "selected text : " + selected_text );
                
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
                //SOURCENET.log_message( "source text : " + source_text );

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