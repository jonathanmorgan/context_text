//----------------------------------------------------------------------------//
// !==> SOURCENET namespace!
//----------------------------------------------------------------------------//


var SOURCENET = SOURCENET || {};


//----------------------------------------------------------------------------//
// !==> ParamContainer class
//----------------------------------------------------------------------------//


//----------------------------------------------------------------------------//
// !----> ParamContainer constructor
//----------------------------------------------------------------------------//

/**
 * Represents one of the pieces of information about an entity stored in an
 *     object.
 * @constructor
 */
SOURCENET.ParamContainer = function()
{   
    
    // class variables
    SOURCENET.ParamContainer.PARAM_TYPE_INTEGER = 'int';
    SOURCENET.ParamContainer.PARAM_TYPE_LIST = 'list';
    SOURCENET.ParamContainer.PARAM_TYPE_STRING = 'string';

    
    // names of properties
    this.params_dictionary = {};
    this.param_name_to_type_dict = {};
    
} //-- END SOURCENET.ParamContainer constructor --//


//----------------------------------------------------------------------------//
// !----> ParamContainer methods
//----------------------------------------------------------------------------//


/**
 * Method: define_parameter()
 *
 * Purpose: accepts the name and type of a parameter, adds them to the
 *     internal dict that maps param names to their types.
 *
 * Params:
 * - name_IN - name of parameter we are defining.
 * - type_IN - type of parameter - should be one of the PARAM_TYPE_* class constants-ish.
 */
SOURCENET.ParamContainer.prototype.define_parameter = function( name_IN, type_IN )
{

    // declare variables
    name_to_type_dict = null;
    
    // get dict
    name_to_type_dict = this.param_name_to_type_dict;

    // add parameter
    name_to_type_dict[ name_IN ] = type_IN;
    
} //-- END method define_parameter() --//


SOURCENET.ParamContainer.prototype.get_parameters = function()
{
        
    // return reference
    dict_OUT = {};
    
    // declare variables
    
    // try to retrieve value - for now, reference nested request.POST
    dict_OUT = this.params_dictionary;
    
    return dict_OUT;

} //-- END method get_parameters() --//


SOURCENET.ParamContainer.prototype.get_param = function( param_name_IN, default_IN )
{
        
        // return reference
        value_OUT = "";
        
        // declare variables
        my_params = null;
        
        // try to retrieve value - for now, reference nested parameters.
        my_params = this.get_parameters();
        value_OUT = my_params[ param_name_IN ];
        
        // got a value?
        if ( value_OUT === undefined )
        {
            
            // no - use default.
            value_OUT = default_IN;
            
        }
        
        return value_OUT;
        
} //-- END method get_param() --//
    

SOURCENET.ParamContainer.prototype.get_param_type = function( param_name_IN )
{
    
        // return reference
        value_OUT = "";
        
        // declare variables
        name_to_type_map = null;
        
        // try to retrieve type - for now, reference nested parameters.
        name_to_type_map = this.param_name_to_type_dict;
        value_OUT = name_to_type_map[ param_name_IN ];
        
        return value_OUT

} //-- END method get_param_type() --//
        

/**
 * Method: set_parameter_value()
 *
 * Purpose: accepts parameter name and value, stores value in nested parameter
 *     dictionary for that parameter name.
 * Postconditions: Returns value set for name.
 *
 * Params:
 * - name_IN - name of parameter we are setting.
 * - value_IN - value to store for that param name.
 */
SOURCENET.ParamContainer.prototype.set_parameter_value = function( name_IN, value_IN )
{

    // return reference
    value_OUT = null;

    // declare variables
    param_dictionary = null;

    // got a param name?
    if ( ( name_IN !== undefined ) && ( name_IN != null ) && ( name_IN != "" ) )
    {
        
        // get parameter dictionary
        param_dictionary = this.get_parameters();
        
        // store the value in the name.
        param_dictionary[ name_IN ] = value_IN;

    } //-- END check to see if we have a name --//
    
    value_OUT = this.get_param( name_IN );
    
    return value_OUT;
    
} //-- END method set_parameter_value() --//


/** 
 * Method: set_parameters()
 *
 * Purpose: accepts a dict of parameters, stores it in instance.
 *
 * Params:
 * - dict_IN - dict of parameter names mapped to values.
 */
SOURCENET.ParamContainer.prototype.set_parameters = function( dict_IN )
{
    
    // declare variables

    // got a request?
    if ( ( dict_IN !== undefined ) && ( dict_IN != null ) )
    {

        // store params
        this.params_dictionary = dict_IN;

    } //-- END check to see if we have a dictionary --//

    
} //-- END method set_parameters() --//


//-- END class ParamContainer --//
