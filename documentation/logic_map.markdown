# Sourcenet Logic Map

<!-- TOC -->

# Output Attention Network

- When configured per README.md, accessed via [http://<your_server>/sourcenet/sourcenet/output/network](http://<your_server>/sourcenet/sourcenet/output/network).

## Files:

- sourcenet/views.py - output_network()
- sourcenet/export/network_output.py - class NetworkOutput
- sourcenet/export/network_data_output.py - abstract class NetworkDataOutput
- sourcenet/export/ndo_*.py - concrete NetworkDataOutput child classes:

    - sourcenet/export/ndo_simple_matrix.py - first format, for UCINet, not compatible with anything else.
    - sourcenet/export/ndo_csv_matrix.py - CSV table, symmetric tie matrix where first row is IDs of people, then each subsequent row is the ties from that person to the people represented by each of the columns.
    - sourcenet/export/ndo_tab_delimited_matrix.py - tab-delimited table, symmetric tie matrix where first row is IDs of people, then each subsequent row is the ties from that person to the people represented by each of the columns.    

- sourcenet/models.py - class Article_Source

## Logic Map

- request handler = sourcenet/views.py - output_network()

    - NetworkOutput.set_request()
    - NetworkOutput.create_network_query_set()
    
        - NetworkOutput.create_query_set()
        
    - NetworkOutput.debug_parameters() a couple of times.
    - NetworkOutput.render_network_data()
    
        - NetworkOutput.create_person_dict()
        
            - NetworkOutput.create_person_query_set()
            - NetworkOutput.add_people_to_dict() - called on lists of authors and sources for each Article_Data in person queryset.
        
        - NetworkOutput.get_NDO_instance()
        - NetworkDataOutput.set_query_set( query_set_IN ) - QuerySet made by NetworkOutput.create_network_query_set() above.
        - NetworkDataOutput.set_person_dictionary( person_dictionary )
        - NetworkDataOutput.get_param_container() - in SourcenetBase parent class
        - NetworkDataOutput.initialize_from_params( my_params )
        - NetworkDataOutput.render()

            - create ties:
            
                - NetworkDataOutput.process_author_relations()
                
                    - NetworkDataOutput.add_reciprocal_relation()
                    - NetworkDataOutput.update_person_type()
                    - NetworkDataOutput.process_source_relations()
                    
                        - NetworkDataOutput.is_source_connected()
                        
                            - Article_Source.is_connected()
                        
                        - NetworkDataOutput.add_reciprocal_relation()
                    
                    - _refactor note - this is where you'd need to figure out how to fit in relations between sources from being in same article._
                    
                        - might rename `process_source_relations()` to `process_author_source_relations()`, then have `process_source_relations()` be the method for source-to-source based on same article.
                
                - NetworkDataOutput.update_source_person_types()
                
            - NetworkDataOutput.generate_master_person_list()
            
                - based on person_dictionary.
            
            - abstract NetworkDataOutput.render_network_data()
            
                - implemented by one of the outputters in the sourcenet/export/ndo_*.py files