from __future__ import unicode_literals

'''
Copyright 2015 Jonathan Morgan

This file is part of http://github.com/jonathanmorgan/sourcenet.

sourcenet is free software: you can redistribute it and/or modify it under the terms of the GNU Lesser General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.

sourcenet is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.

You should have received a copy of the GNU Lesser General Public License along with http://github.com/jonathanmorgan/sourcenet. If not, see http://www.gnu.org/licenses/.
'''

#================================================================================
# Imports
#================================================================================


# python standard libraries
import json

# python utilities
from python_utilities.json.json_helper import JSONHelper
from python_utilities.logging.logging_helper import LoggingHelper


#================================================================================
# Package constants-ish
#================================================================================


#================================================================================
# OpenCalaisArticleCoder class
#================================================================================


# define OpenCalaisArticleCoder class.
class OpenCalaisApiResponse( LoggingHelper ):

    '''
    This class is a helper for coding articles using the OpenCalais REST API. It
       contains logic to deal with parsing and making the JSON response of an API
       call easier to use.
    Preconditions: In order for this to be useful, you'll need to send some text
       to the OpenCalais REST API and receive a JSON response.
    '''

    #============================================================================
    # META!!!
    #============================================================================

    
    #============================================================================
    # Constants-ish
    #============================================================================


    # Logging variables
    LOGGING_NAME = "sourcenet.article_coding.open_calais_api_response"

    # Known JSON object attribute names
    JSON_NAME_DOC = "doc"
    
    # Item property names
    JSON_NAME_ITEM_TYPE = "_type"
    JSON_NAME_ITEM_TYPE_GROUP = "_typeGroup"
    
    # Quotation property names
    JSON_NAME_QUOTE_PERSON_URI = "person"
    
    # Person property names
    JSON_NAME_PERSON_NAME = "name"
    
    # OpenCalais item types
    OC_ITEM_TYPE_QUOTATION = "Quotation"
    OC_ITEM_TYPE_PERSON = "Person"
    
    # debugging
    DEBUG_FLAG = True
    
    # status constants
    STATUS_SUCCESS = "Success!"    
    STATUS_ERROR_PREFIX = "Error: "    


    #============================================================================
    # Instance variables
    #============================================================================


    json_response_object = None
    doc_object = None
    type_group_to_items_dict = {}
    type_to_items_dict = {}


    #============================================================================
    # class methods
    #============================================================================


    @classmethod
    def print_calais_json( cls, json_IN ):
    
        '''
        Accepts OpenCalais API JSON object, prints selected parts of it to a
           string variable.  Returns that string.
        '''
    
        # return reference
        string_OUT = ""
        
        # declare variables
        properties_to_output_list = []
        current_property = ""
        
        # set properties we want to output
        properties_to_output_list = [ "_type", "_typeGroup", "commonname", "name", "person" ]
        
        # loop over the stuff in the response:
        item_counter = 0
        current_container = json_IN
        for item in current_container.keys():
        
            item_counter += 1
            string_OUT += "==> " + str( item_counter ) + ": " + item + "\n"
            
            # loop over properties that we care about.
            for current_property in properties_to_output_list:
                        
                # is property in the current JSON item we are looking at?
                if ( current_property in current_container[ item ] ):

                    # yes - output.
                    current_property_value = current_container[ item ][ current_property ]
                    string_OUT += "----> " + current_property + ": " + current_property_value  + "\n"

                    # is it a Quotation or a Person?
                    if ( ( current_property_value == "Quotation" ) or ( current_property_value == "Person" ) ):

                        string_OUT += str( current_container[ item ] ) + "\n"

                    #-- END check to see if type is "Quotation" --#

                #-- END current_property --#

            #-- END loop over list of properties we want to output. --#
            
        #-- END loop over items --#
        
        return string_OUT
        
    #-- END function print_calais_json --#


    #============================================================================
    # Instance methods
    #============================================================================


    #----------------------------------------------------------------------------
    # __init__() method
    #----------------------------------------------------------------------------


    def __init__( self ):

        # call parent's __init__()
        super( OpenCalaisApiResponse, self ).__init__()
        
        # declare variables
        
        # initialize variables
        self.response_object = None
        self.doc_object = None
        self.type_group_to_items_dict = {}
        self.type_to_entities_dict = {}
        
        # logging variables
        self.set_logger_name( self.LOGGING_NAME )

    #-- END method __init__() --#


    def add_item_to_type_dict( self, item_id_IN, item_IN ):
        
        '''
        Accepts item.  Gets type from inside the item.  Looks for type in
           type_to_items_dict.  If present, retrieves associated,
           dictionary (item ID to item map), adds item.  If not, makes dict,
           adds item to dict, adds dict to type dict mapped to type.
        If success, returns item type item was added to. On error, returns
           non-empty string describing it, preceded by self.STATUS_ERROR_PREFIX.
        '''
        
        # return reference
        status_OUT = ""
        
        # declare variables
        the_dict = None
        item_type = ""
        nested_dict = None
        
        # get dictionary
        the_dict = self.type_to_items_dict
        
        # get item's type_group
        item_type = JSONHelper.get_json_object_property( item_IN, self.JSON_NAME_ITEM_TYPE )
        
        # got one?
        if item_type is not None:
        
            # got a group.  Is it in the dict?
            if item_type in the_dict:
            
                # it is in the dict - get nested dictionary
                nested_dict = the_dict[ item_type ]
                
                # add the item to the nested dictionary.
                nested_dict[ item_id_IN ] = item_IN
            
            else:
            
                # not there yet.  create a dictionary.
                nested_dict = {}
                
                # add the item
                nested_dict[ item_id_IN ] = item_IN
                
                # nest the dictionary.
                the_dict[ item_type ] = nested_dict
            
            #-- END check to see if type group is in the dictionary --#
            
            # return type
            status_OUT = item_type
        
        else:
        
            # no group.
            status_OUT = self.STATUS_ERROR_PREFIX + "No type in element."
        
        #-- END check to see if we have a group --#
        
        return status_OUT
        
    #-- END method add_item_to_type_dict() --#
    

    def add_item_to_type_group_dict( self, item_id_IN, item_IN ):
        
        '''
        Accepts item.  Gets type group from inside the item.  Looks for group
           type in type_group_to_items_dict.  If present, retrieves associated,
           dictionary (item ID to item map), adds item.  If not, makes dict,
           adds item to dict, adds dict to type group dict mapped to group type.
        If success, returns item type group to which the item was added.  If
           error returns non-empty string describing it, preceded by
           self.STATUS_ERROR_PREFIX.
        '''
        
        # return reference
        status_OUT = ""
        
        # declare variables
        the_dict = None
        item_type_group = ""
        nested_dict = None
        
        # get dictionary
        the_dict = self.type_group_to_items_dict
        
        # get item's type_group
        item_type_group = JSONHelper.get_json_object_property( item_IN, self.JSON_NAME_ITEM_TYPE_GROUP )
        
        # got one?
        if item_type_group is not None:
        
            # got a group.  Is it in the dict?
            if item_type_group in the_dict:
            
                # it is in the dict - get nested dictionary
                nested_dict = the_dict[ item_type_group ]
                
                # add the item to the nested dictionary.
                nested_dict[ item_id_IN ] = item_IN
            
            else:
            
                # not there yet.  create a dictionary.
                nested_dict = {}
                
                # add the item
                nested_dict[ item_id_IN ] = item_IN
                
                # nest the dictionary.
                the_dict[ item_type_group ] = nested_dict
            
            #-- END check to see if type group is in the dictionary --#
            
            status_OUT = item_type_group
        
        else:
        
            # no group.
            status_OUT = self.STATUS_ERROR_PREFIX + "No type group in item."
        
        #-- END check to see if we have a type group --#
        
        return status_OUT
        
    #-- END method add_item_to_type_group_dict() --#
    

    def get_doc( self ):

        '''
        Retrieves JSON response "doc" object instance.
        '''
        
        # return reference
        instance_OUT = None

        # get JSON response "doc" object instance.
        instance_OUT = self.doc_object

        return instance_OUT

    #-- END get_doc() --#


    def get_item_from_response( self, name_IN ):

        '''
        Accepts name of OpenCalais entity (a URL string).  Retrieves the json
            object for that entity from the response.  If not found, returns
            None.
        '''
        
        # return reference
        json_OUT = None
        
        # declare variables
        json_response_root = None
        
        # get JSON response root.
        json_response_root = self.get_json_response_object()

        # get property, default to None if not present.
        json_OUT = JSONHelper.get_json_object_property( json_response_root, name_IN, None )
        
        return json_OUT

    #-- END get_item_from_response() --#


    def get_items_of_type( self, type_IN ):

        '''
        Accepts string name of an OpenCalais type.  Retrieves the dictionary
            object of items from the response with that type (maps item name -
            the OpenCalais URI) to each of the items of that type.  If not found,
            returns None.
        '''
        
        # return reference
        item_dict_OUT = None
        
        # declare variables
        my_types_to_items_dict = None
        
        # get type-to-items dictionary
        my_types_to_items_dict = self.type_to_items_dict

        # see if type passed in is in the dictionary.
        if type_IN in my_types_to_items_dict:
        
            # it is there, return it.
            item_dict_OUT = my_types_to_items_dict.get( type_IN, None )
            
        else:
        
            # no items.  Return None.
            item_dict_OUT = None
            
        #-- END check to see if type has items. --#
        
        return item_dict_OUT

    #-- END get_items_of_type() --#


    def get_json_response_object( self ):

        '''
        Retrieves JSON response "doc" object instance.
        '''
        
        # return reference
        instance_OUT = None

        # get JSON response object instance.
        instance_OUT = self.json_response_object

        return instance_OUT

    #-- END get_json_response_object() --#


    def summarize_json( self ):
    
        '''
        Using OpenCalais API JSON object in this instance, prints selected parts
           of it to a string variable.  Returns that string.
        '''
    
        # return reference
        string_OUT = ""
        
        # declare variables
        json_object = None
        
        # call class method.
        json_object = self.get_json_response_object()
        string_OUT = self.print_calais_json( json_object )
        
        return string_OUT
        
    #-- END function summarize_json --#


    def set_doc( self, json_object_IN ):
        
        '''
        Accepts JSON "doc" response object (name-value pairs) from call to
           OpenCalais REST API.  Stores separate reference to it internally,
           doesn't do anything else for now.  Eventually, can parse it and
           breaks out pieces so it is easier to work with if we care.
        '''
        
        # return reference
        value_OUT = None
        
        # declare variables
        me = "set_doc"
        my_logger = None
        
        # get logger
        #my_logger = self.get_logger()
        
        # store the doc object.
        self.doc_object = json_object_IN
        
        value_OUT = self.doc_object
        
        return value_OUT

    #-- END method set_doc() --#


    def set_json_response_object( self, json_object_IN ):
        
        '''
        Accepts JSON response object (name-value pairs) from call to OpenCalais
           REST API.  Stores it internally, then parses it and break out pieces
           so it is easier to work with.
        '''
        
        # return reference
        instance_OUT = None
        
        # declare variables
        me = "set_json_response_object"
        my_logger = None
        json_string = ""
        response_json_root = None
        item_counter = -1
        current_key = ""
        current_object = None
        current_type = ""
        current_type_group = ""
        doc_object = None
        current_status = ""
        
        # get logger
        my_logger = self.get_logger()
        
        # first, remind myself what the JSON looks like.
        #json_string = JSONHelper.pretty_print_json( json_object_IN )
        #my_logger.debug( "In " + me + ": outputting whole JSON document:" )
        #my_logger.debug( json_string )
        
        # store JSON response in "response_json_root" variable.
        response_json_root = json_object_IN
        
        # loop over the list of top-level things.  It should be a set of
        #    name-value pairs where the value is another structured JSON object.
        for item_counter, current_key in enumerate( response_json_root ):
        
            # grab JSON for the key.
            current_object = response_json_root[ current_key ]
            
            # get type group
            current_type_group = JSONHelper.get_json_object_property( current_object, self.JSON_NAME_ITEM_TYPE_GROUP )
            
            # get current entity type.
            current_type = JSONHelper.get_json_object_property( current_object, self.JSON_NAME_ITEM_TYPE )
            
            # log it.
            my_logger.debug( "In " + me + ": #" + str( item_counter ) + " (type group: " + str( current_type_group ) + "; type: " + str( current_type ) + ") = " + current_key )
            
            # if doc, store the doc off in separate reference for easy access.
            if ( current_key == self.JSON_NAME_DOC ):
            
                # store off the doc.
                self.set_doc( current_object )
                
                # output, just to make sure I have what I think I have.
                #json_string = JSONHelper.pretty_print_json( current_object )
                #my_logger.debug( "In " + me + ": outputting JSON \"doc\" object:" )
                #my_logger.debug( json_string )
            
            #-- END check to see if "doc" JSON --#
            
            # add to dict of type groups to items
            current_status = self.add_item_to_type_group_dict( current_key, current_object )
            
            my_logger.debug( "In " + me + ": added to type group map: " + current_status )
            
            # add to dict of types to items
            current_status = self.add_item_to_type_dict( current_key, current_object )
        
            my_logger.debug( "In " + me + ": added to type map: " + current_status )

        #-- END loop over top-level keys in JSON --#
        
        # store root in instance variable
        self.json_response_object = response_json_root
        instance_OUT = self.json_response_object
        
        # try retrieving doc entity directly from root element.
        doc_object = self.get_item_from_response( self.JSON_NAME_DOC )

        # output, just to make sure I have what I think I have.
        json_string = JSONHelper.pretty_print_json( doc_object )
        my_logger.debug( "In " + me + ": outputting JSON \"doc\" object from lookup:" )
        my_logger.debug( json_string )
        
        return instance_OUT

    #-- END method set_response_object() --#


#-- END class OpenCalaisApiResponse --#