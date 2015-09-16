//============================================================================//
// javascript for article coding.
//============================================================================//

//----------------------------------------------------------------------------//
// namespace!
//----------------------------------------------------------------------------//

var SOURCENET = SOURCENET || {};

//----------------------------------------------------------------------------//
// object definitions
//----------------------------------------------------------------------------//


//=====================//
// Subject
//=====================//

// Subject constructor

SOURCENET.Subject = function()
{
    // instance variables
    this.subject_name = "";
    this.is_quoted = false;
    this.name_and_title = "";
    this.quote_text = "";
    this.person_id = null;
    //this.location_of_name = "";
}

// Subject methods

SOURCENET.Subject.prototype.populate_from_form = function( form_element_IN )
{

    // declare variables
    var form_element = null;
    var my_subject_name = "";
    var my_is_quoted = false;
    var my_name_and_title = "";
    var my_quote_text = "";
    var my_person_id = null;
    var subject_name_input_element = null;

    // get form element
    form_element = form_element_IN
    
    // retrieve values from form inputs.
    
    // ! get input for subject_name - not sure best way to do this - reference form?  just go straight to the DOM?
    
    // must have a name
    my_name = this.subject_name;
    if ( ( my_name == null ) || ( my_name == "" ) )
    {
        // no name - invalid.
        is_valid_OUT = false;
    }
    
    alert( "is valid?" + is_valid_OUT )
    
    return is_valid_OUT;
    
} //-- END SOURCENET.Subject function validate() --//

SOURCENET.Subject.prototype.validate = function()
{

    // return reference
    var is_valid_OUT = true;

    // declare variables
    var my_name = "";
    
    // must have a name
    my_name = this.subject_name;
    if ( ( my_name == null ) || ( my_name == "" ) )
    {
        // no name - invalid.
        is_valid_OUT = false;
    }
    
    //alert( "is valid?" + is_valid_OUT )
    
    return is_valid_OUT;
    
} //-- END SOURCENET.Subject function validate() --//

//=====================//
// END Subject
//=====================//


//----------------------------------------------------------------------------//
// function definitions
//----------------------------------------------------------------------------//


SOURCENET.process_subject_coding = function()
{
    alert( "PROCESS SUBJECT CODING!!!" );
    
    // declare variables
    form_element = null;
    subject_instance = null;
    is_subject_valid = false;
    
    // get form element.
    form_element = $( '#subject-coding' );
    
    // create Subject instance.
    subject_instance = new SOURCENET.Subject();
    
    // populate it from the form.
    subject_instance.populate_from_form( form_element );
    
    // validate
    is_subject_valid = subject_instance.validate();
    
    alert( "made a subject instance... valid? " + is_subject_valid );
    
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
                $( '#source-name' ).val( selected_text );
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
                var source_name_and_title_element = null;
                var existing_text = "";
    
                // get selection
                selected_text = $.selection();
                //alert( "selected text : " + selected_text );
                
                // see if there is already something there.
                source_name_and_title_element = $( '#source-name-and-title' )
                existing_text = source_name_and_title_element.val()
                //alert( "Existing text: " + existing_text )
                
                // something already there?
                if ( existing_text != "" )
                {

                    // yes - append new to the end.
                    source_name_and_title_element.val( existing_text + " " + selected_text );
                    
                }
                else
                {
                    
                    // no - just overwrite.
                    source_name_and_title_element.val( selected_text );
                    
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
                source_text = $( '#source-name' ).val();
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