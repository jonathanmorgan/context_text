from __future__ import unicode_literals

'''
Copyright 2010-present (2016) Jonathan Morgan

This file is part of http://github.com/jonathanmorgan/context_text.

context_text is free software: you can redistribute it and/or modify it under the terms of the GNU Lesser General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.

context_text is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.

You should have received a copy of the GNU Lesser General Public License along with http://github.com/jonathanmorgan/context_text. If not, see http://www.gnu.org/licenses/.
'''

#===============================================================================
# imports (in alphabetical order by package, then by name)
#===============================================================================

# six - python 2 + 3
import six

# nameparser import
# http://pypi.python.org/pypi/nameparser
from nameparser import HumanName

# python_utilities imports
from python_utilities.django_utils.django_form_helper import DjangoFormHelper

# context_text imports
#from context_text.models import Article_Subject

#================================================================================
# Shared variables and functions
#================================================================================


#===============================================================================
# classes (in alphabetical order by name)
#===============================================================================

class PersonDetails( dict ):

    #---------------------------------------------------------------------------
    # CONSTANTS-ish
    #---------------------------------------------------------------------------

    # property names
    PROP_NAME_PERSON_ID = "person_id"
    PROP_NAME_PERSON_NAME = "person_name"
    PROP_NAME_FIXED_PERSON_NAME = "fixed_person_name"
    PROP_NAME_PERSON_TYPE = "person_type"
    PROP_NAME_ORIGINAL_PERSON_TYPE = "original_person_type"
    PROP_NAME_ARTICLE_PERSON_ID = "article_person_id"
    PROP_NAME_TITLE = "title"
    PROP_NAME_PERSON_ORGANIZATION = "person_organization"
    PROP_NAME_QUOTE_TEXT = "quote_text"
    
    # Properties that map to Article_Person fields
    PROP_NAME_ARTICLE_DATA_INSTANCE = "article_data_instance"
    PROP_NAME_PERSON_INSTANCE = "person_instance"
    PROP_NAME_VERBATIM_NAME = "verbatim_name"
    PROP_NAME_LOOKUP_NAME = "lookup_name"
    PROP_NAME_ORGANIZATION_INSTANCE = "organization_instance"
    PROP_NAME_NEWSPAPER_INSTANCE = "newspaper_instance"
    PROP_NAME_NEWSPAPER_NOTES = "newspaper_notes"
    PROP_NAME_EXTERNAL_UUID_NAME = "external_uuid_name"
    PROP_NAME_EXTERNAL_UUID = "external_uuid"
    PROP_NAME_EXTERNAL_UUID_SOURCE = "external_uuid_source"
    PROP_NAME_EXTERNAL_UUID_NOTES = "external_uuid_notes"
    PROP_NAME_CAPTURE_METHOD = "capture_method"
    PROP_NAME_SUBJECT_TYPE = "subject_type"
    PROP_NAME_MATCH_STATUS = "match_status"
    PROP_MAME_MATCH_CONFIDENCE_LEVEL = "match_confidence_level"
    PROP_NAME_CODER_TYPE = "coder_type"
    PROP_NAME_NOTES = "notes"
    
    # Properties that map to Person fields
    PROP_NAME_FULL_NAME_STRING = "full_name_string"
    PROP_NAME_FIRST_NAME = "first_name"
    PROP_NAME_MIDDLE_NAME = "middle_name"
    PROP_NAME_LAST_NAME = "last_name"
    PROP_NAME_NAME_PREFIX = "name_prefix"
    PROP_NAME_NAME_SUFFIX = "name_suffix"
    PROP_NAME_NICKNAME = "nickname"
    
    PROP_LIST_NAME_PARTS = [ PROP_NAME_FIRST_NAME, PROP_NAME_MIDDLE_NAME, PROP_NAME_LAST_NAME, PROP_NAME_NAME_PREFIX, PROP_NAME_NAME_SUFFIX, PROP_NAME_NICKNAME ]

    # constants-ish
    IAMEMPTY = "IAMEMPTY"
    
    # person types
    PERSON_TYPE_SUBJECT = "subject"
    PERSON_TYPE_SOURCE = "source"
    PERSON_TYPE_AUTHOR = "author"
    
    # subject types
    SUBJECT_TYPE_MENTIONED = 'mentioned'
    SUBJECT_TYPE_QUOTED = 'quoted'

    # subject_type to person type dictionary
    SUBJECT_TYPE_TO_PERSON_TYPE_MAP = {}
    SUBJECT_TYPE_TO_PERSON_TYPE_MAP[ SUBJECT_TYPE_MENTIONED ] = PERSON_TYPE_SUBJECT
    SUBJECT_TYPE_TO_PERSON_TYPE_MAP[ SUBJECT_TYPE_QUOTED ] = PERSON_TYPE_SOURCE    

    #---------------------------------------------------------------------------
    # ! ==> class methods, in alphabetical order
    #---------------------------------------------------------------------------


    @classmethod
    def get_instance( cls, instance_IN = None, *args, **kwargs ):
        
        '''
        Accepts an instance that is either a dictionary or a PersonDetails
            instance.
            - Checks to see if it is None.
                - If so, returns an empty PersonDetails instance.
                - If not None, checks to see if it is a PersonDetails instance.
                    - If yes, just returns what was passed in.
                    - If not, checks to see if it is a dictionary.
                        - If dictionary, creates new PersonDetails, copies
                            contents of dictionary into PersonDetails, then
                            returns new instance.
                        - If not dictionary, error - returns None.
        '''
        
        # return reference
        instance_OUT = None
        
        # declare variables
        is_person_details = False
        is_dict = False
        
        # check to see if instance passed in is populated at all.
        if ( instance_IN is not None ):
        
            # got something.  Is it a PersonDetails instance?
            is_person_details = isinstance( instance_IN, PersonDetails )
            if ( is_person_details == False ):
            
                # not PersonDetails.  Is it a dict?
                is_dict = isinstance( instance_IN, dict )
                if ( is_dict == True ):
                
                    # yes - copy values to a new PersonDetails instance.
                    instance_OUT = PersonDetails()
                    
                    # init from dictionary
                    instance_OUT.init_from_dict( instance_IN )
                
                else:
                
                    # not a dictionary.  For now, this is an error.  Return
                    #     None.
                    instance_OUT = None
                
                #-- END check to see if is dictionary --#
                
            else:
            
                # Already a PersonDetails instance...  For now, just return it.
                instance_OUT = instance_IN
            
            #-- END check to see if already a PersonDetails instance --#
        
        else:
        
            # nothing passed in.  Return empty instance.
            instance_OUT = PersonDetails()
        
        #-- END check to see if we just want an empty instance. --#
        
        return instance_OUT
        
    #-- END class method get_instance() --#
    

    #---------------------------------------------------------------------------
    # ! ==> __init__() and __str__() methods
    #---------------------------------------------------------------------------


    def __init__( self, *args, **kwargs ):
        
        super( PersonDetails, self ).__init__( *args, **kwargs )
        
        # declare variables
        self.do_lookup_id_before_name = False

    #-- END overridden __init__() that calls parent __init__(). --#
    

    def __str__( self ):
        
        # return reference
        string_OUT = ''

        string_OUT = super( PersonDetails, self ).__str__()

        return string_OUT
        
    #-- END method __str__() --#


    #---------------------------------------------------------------------------
    # ! ==> instance methods, in alphabetical order
    #---------------------------------------------------------------------------


    def get_corrected_person_name( self, *args, **kwargs ):
        
        '''
        Looks to see if there is a property named "fixed_person_name".  If so,
            and if it is not empty or None, returns that.  If not, returns
            whatever is in "person_name".
        '''
        
        # return reference
        value_OUT = ""
        
        # declare variables
        current_name_value = ""
        
        # try to retrieve "fixed_person_name"
        current_name_value = self.get( self.PROP_NAME_FIXED_PERSON_NAME, None )
        
        # got anything?
        if ( ( current_name_value is None ) or ( current_name_value == "" ) ):
        
            # no.  Grab value in person_name
            current_name_value = self.get( self.PROP_NAME_PERSON_NAME, None )
            
        #-- END check to see if fixed_person_name --#
        
        # return whatever is in current_name_value.
        value_OUT = current_name_value
        
        return value_OUT
        
    #-- END method get_corrected_person_name() --#
    

    def get_lookup_name( self, *args, **kwargs ):
        
        '''
        Looks to see if there is a property named "fixed_person_name".  If so,
            and if it is not empty or None, returns that.  If not, returns
            whatever is in "person_name".  Actual implementation is to call
            get_corrected_person_name().
        '''
        
        # return reference
        value_OUT = ""
        
        # declare variables
        temp_value = ""
        
        # is there a lookup_name explicitly set?
        temp_value = self.get( self.PROP_NAME_LOOKUP_NAME, None )
        if ( temp_value is None ):
        
            # no.  call get_corrected_person_name()
            value_OUT = self.get_corrected_person_name()
            
        else:
        
            # yes.  Use it.
            value_OUT = temp_value
            
        #-- END check to see if lookup name is set. --#
        
        return value_OUT
        
    #-- END method get_lookup_name() --#
    

    def get_verbatim_name( self, *args, **kwargs ):
        
        '''
        To start, always returns person_name.
        '''
        
        # return reference
        value_OUT = ""
        
        # declare variables
        temp_value = ""
        
        # is there a verbatim_name explicitly set?
        temp_value = self.get( self.PROP_NAME_VERBATIM_NAME, None )
        if ( temp_value is None ):
        
            # no.  Just use person name.
            value_OUT = self.get( self.PROP_NAME_PERSON_NAME, None )
            
        else:
        
            # yes.  Use it.
            value_OUT = temp_value
            
        #-- END check to see if verbatim name is set. --#
        
        return value_OUT
        
    #-- END method get_verbatim_name() --#
    

    def got_name_parts( self, *args, **kwargs ):
        
        '''
        Loops over the property names in PROP_LIST_NAME_PARTS.
        '''
        
        # return reference
        value_OUT = False
        
        # declare variables
        me = "got_name_parts"
        is_empty = False
        got_name_parts = False
        name_part_prop_name_list = []
        current_prop_name = ""
        current_prop_value = ""
        
        # get reference to name part property nanme list.
        name_part_prop_name_list = self.PROP_LIST_NAME_PARTS
        
        # loop!
        for current_prop_name in name_part_prop_name_list:
        
            # is there a value for this property name?
            current_prop_value = self.get( current_prop_name, None )
            
            # empty?
            is_empty = DjangoFormHelper.is_value_empty( current_prop_value )
            if ( is_empty == False ):

                # not empty - return True.
                got_name_parts = True
                
            #-- END check to see if current value is empty. --#
            
        #-- END loop over property names. --#
        
        # return got_name_parts
        value_OUT = got_name_parts
        
        return value_OUT
        
    #-- END method got_name_parts() --#
    

    def init_from_dict( self, dict_IN = None, *args, **kwargs ):
        
        '''
        Accepts a reference to a dictionary.  If None, does nothing.  If dict,
            uses the update() method to pull values from dict into PersonDetails
            instance.  If not dict, does nothing.
        '''
        
        # declare variables
        is_dict = False
        
        # got anything passed in?
        if ( dict_IN is not None ):
        
            # is it a dict(ionary)?
            is_dict = isinstance( dict_IN, dict )
            if ( is_dict == True ):
            
                # yes.  Use update() to pull in data.
                self.update( dict_IN )
                
            #-- END check to see if dict(ionary) --#
            
        #-- END check to see if dictionary populated at all --#
        
    #-- END method init_from_dict() --#
    

    def to_HumanName( self ):
        
        '''
        This method creates a nameparser HumanName() object instance for the
            Person name property values in this instance.  Returns the HumanName
            instance.
           
        preconditions: None.
        postconditions: None.
        '''
        
        # return reference
        instance_OUT = None
        
        # declare variables
        me = "to_HumanName"
        my_name_prefix = ""
        my_first_name = ""
        my_middle_name = ""
        my_last_name = ""
        my_name_suffix = ""
        my_nickname = ""
        my_full_name_string = ""
        my_lookup_name = ""
        got_name_parts = False
        
        # retrieve values from this instance
        my_name_prefix = self.get( self.PROP_NAME_NAME_PREFIX, None )
        my_first_name = self.get( self.PROP_NAME_FIRST_NAME, None )
        my_middle_name = self.get( self.PROP_NAME_MIDDLE_NAME, None )
        my_last_name = self.get( self.PROP_NAME_LAST_NAME, None )
        my_name_suffix = self.get( self.PROP_NAME_NAME_SUFFIX, None )
        my_nickname = self.get( self.PROP_NAME_NICKNAME, None )
        my_full_name_string = self.get( self.PROP_NAME_FULL_NAME_STRING, None )
        my_lookup_name = self.get_lookup_name()
        
        # got name parts?
        got_name_parts = self.got_name_parts()
        if ( got_name_parts == True ):
        
            # build human name from name parts.
            instance_OUT = HumanName()
    
            # Use nested values to populate HumanName.
            if ( my_name_prefix ):
        
                instance_OUT.title = my_name_prefix
                
            #-- END check to see if name_prefix. --#
            
            if ( my_first_name ):
        
                instance_OUT.first = my_first_name
                
            #-- END check to see if first_name. --#
            
            if ( my_middle_name ):
        
                instance_OUT.middle = my_middle_name
                
            #-- END check to see if middle_name. --#
            
            if ( my_last_name ):
        
                instance_OUT.last = my_last_name
                
            #-- END check to see if last_name. --#
            
            if ( my_name_suffix ):
        
                instance_OUT.suffix = my_name_suffix
                
            #-- END check to see if name_suffix. --#
            
            if ( my_nickname ):
        
                instance_OUT.nickname = my_nickname
                
            #-- END check to see if nickname. --#
            
        # got full name string?
        elif ( ( my_full_name_string is not None ) and ( my_full_name_string != "" ) ):
        
            # yes.  Pass it to HumanName
            instance_OUT = HumanName( my_full_name_string )
        
        # how about lookup name?
        elif ( ( my_lookup_name is not None ) and ( my_lookup_name != "" ) ):
        
            # yes.  Pass it to HumanName
            instance_OUT = HumanName( my_lookup_name )
        
        else:
        
            # no names present at all.  Return None.
            instance_OUT = None
            
        #-- END check to see what name information we have --#
                
        return instance_OUT
        
    #-- END method to_HumanName() --#


#-- END class PersonDetails --#