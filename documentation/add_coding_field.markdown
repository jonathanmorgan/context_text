# Adding a field to coding form.

- Add field to model where you want to store it.
- create migration, and update database.
- update form in context_text/templates/articles/article-code.html
- update context_text/static/context_text/js/article-coding/article-coding.js

    - add javascript event handlers for yanking selection, if needed, to context_text/static/context_text/js/article-coding/article-coding.js (near bottom), including CONTEXT_TEXT.* variables for any IDs or potentially re-usable strings.  Example:

            // !document.ready( #store-organization )
            // javascript to store selected text as organization.
            // Get selected text
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
                            //CONTEXT_TEXT.log_message( "selected text : " + selected_text );
                            
                            // see if there is already something there.
                            person_organization_element = $( '#' + CONTEXT_TEXT.INPUT_ID_ORGANIZATION )
                            existing_text = person_organization_element.val()
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

    - add field to Person object.
    - update Person.populate_from_form() to know about your new field.
    - update Person.populate_form() to know about your new field.
    - update Person.validate() if needed (for example, if new required field).
    - update CONTEXT_TEXT.clear_coding_form() so it knows about your new field.
    - start at CONTEXT_TEXT.process_person_coding() and work your way through, checking if you need to make changes.

        - CONTEXT_TEXT.DataStore.process_person()

            - CONTEXT_TEXT.DataStore.add_person()
            - CONTEXT_TEXT.DataStore.update_person()

    - update CONTEXT_TEXT.DataStore.load_from_json() so it knows about your new field.

- in context_text/article_coding/article_coder.py

    - add a PARAM_* constants-ish to ArticleCoder for your new field.

- in context_text/article_coding/manual_coding/manual_article_coder.py

    - add a DATA_STORE_PROP_* constants-ish to hold the name for your property from the Person JSON.  Set it to the PARAM_* you made in ArticleCoder.
    - update ManualArticleCoder.process_data_store_json() so it knows of the new field.  Includes:

        - make a variable to hold new value.
        - load value from JSON for person.

- in context_text/article_coding/article_coder.py

    - if property available for subject (added to model Article_Subject), update ArticleCoder.process_subject_name() to handle it, both the part where you INSERT and the part where you UPDATE existing.
    - if property available for author (added to Article_Author), update ArticleCoder.process_author_name() to handle it, both the part where you INSERT and the part where you UPDATE existing.
    - if added to Article_Person, update in both ArticleCoder.process_subject_name() and ArticleCoder.process_author_name().
    - if property has information you might also store in the Person, update ArticleCoder.lookup_person() and ArticleCoder.update_person()

- update unit tests.  Yes, all of them.  And maybe your test data, too.