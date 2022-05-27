from __future__ import unicode_literals
from __future__ import division

'''
Copyright 2010-2016 Jonathan Morgan

This file is part of http://github.com/jonathanmorgan/context_text.

context_text is free software: you can redistribute it and/or modify it under the terms of the GNU Lesser General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.

context_text is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.

You should have received a copy of the GNU Lesser General Public License along with http://github.com/jonathanmorgan/context_text. If not, see http://www.gnu.org/licenses/.
'''


#================================================================================
# Imports
#================================================================================

# python imports
from abc import ABCMeta, abstractmethod
import datetime
from decimal import Decimal
from decimal import getcontext
import gc
import hashlib
import logging
import pickle
#import re

# import six for Python 2 and 3 compatibility.
import six

# nameparser import
# http://pypi.python.org/pypi/nameparser
from nameparser import HumanName

# BeautifulSoup import
from bs4 import BeautifulSoup
from bs4 import NavigableString

# taggit tagging APIs
from taggit.managers import TaggableManager

# Django core imports
#import django
#django.setup()

#from django.core.exceptions import DoesNotExist
from django.core.exceptions import ObjectDoesNotExist
from django.core.exceptions import MultipleObjectsReturned

# Django imports
from django.contrib.auth.models import User
from django.db import models

# Django query object for OR-ing selection criteria together.
from django.db.models import Q

# Dajngo object for interacting directly with database.
from django.db import connection
import django.db

# django encoding imports (for supporting 2 and 3).
import django.utils.encoding
from django.utils.text import slugify

# python_utilities - text cleanup
from python_utilities.beautiful_soup.beautiful_soup_helper import BeautifulSoupHelper
from python_utilities.integers.integer_helper import IntegerHelper
from python_utilities.json.json_helper import JSONHelper
from python_utilities.lists.list_helper import ListHelper
from python_utilities.strings.html_helper import HTMLHelper
from python_utilities.strings.string_helper import StringHelper

# python_utilities - django
from python_utilities.django_utils.django_model_helper import DjangoModelHelper
from python_utilities.django_utils.queryset_helper import QuerySetHelper

# python_utilities - dictionaries
from python_utilities.dictionaries.dict_helper import DictHelper

# python_utilities - logging
from python_utilities.logging.logging_helper import LoggingHelper

# python_utilities - sequences
from python_utilities.sequences.sequence_helper import SequenceHelper

# context imports
from context.models import Abstract_Context_With_JSON
from context.models import Abstract_UUID
from context.models import Entity
from context.models import Entity_Identifier_Type
from context.models import Work_Log
from context.shared.entity_models import Abstract_Entity_Container
from context.shared.entity_models import Abstract_Location
from context.shared.entity_models import Abstract_Organization
from context.shared.entity_models import Abstract_Person_Parent
from context.shared.entity_models import Abstract_Person
from context.shared.entity_models import Abstract_Related_Content
from context.shared.entity_models import Abstract_Related_JSON_Content
from context.shared.entity_models import output_debug
from context.shared.entity_models import output_log_message
from context.shared.person_details import PersonDetails

# context_text imports
#from context_text.export.network_output import NetworkOutput
from context_text.shared.context_text_base import ContextTextBase

#================================================================================
# Shared variables and functions
#================================================================================

STATUS_SUCCESS = "Success!"
DEFAULT_DATE_FORMAT = "%Y-%m-%d"
BS_PARSER = "html5lib"

'''
Debugging code, shared across all models.
'''

DEBUG = False
DEFAULT_LOGGER_NAME = "context_text.models"

# now imported: context.shared.entity_models import output_log_message
# def output_log_message( message_IN, method_IN = "", indent_with_IN = "", logger_name_IN = DEFAULT_LOGGER_NAME, log_level_code_IN = logging.DEBUG, do_print_IN = False ):


# now imported: context.shared.entity_models import output_debug
#def output_debug( message_IN, method_IN = "", indent_with_IN = "", logger_name_IN = DEFAULT_LOGGER_NAME ):


def get_dict_value( dict_IN, name_IN, default_IN = None ):

    '''
    Convenience method for getting value for name of dictionary entry that might
       or might not exist in dictionary.
    '''

    # return reference
    value_OUT = default_IN

    # got a dict?
    if ( dict_IN ):

        # got a name?
        if ( name_IN ):

            # name in dictionary?
            if ( name_IN in dict_IN ):

                # yup.  Get it.
                value_OUT = dict_IN[ name_IN ]

            else:

                # no.  Return default.
                value_OUT = default_IN

            #-- END check to see if start date in arguments --#

        else:

            value_OUT = default_IN

        #-- END check to see if name passed in. --#

    else:

        value_OUT = default_IN

    #-- END check to see if dict passed in. --#

    return value_OUT

#-- END method get_dict_value() --#


'''
Models for context_text, including some that are specific to the Grand Rapids Press.
'''


# Locations
class Project( models.Model ):

    # Django model properties.
    name = models.CharField( max_length = 255 )
    description = models.TextField( blank = True, null = True )

    # Meta-data for this class.
    class Meta:
        ordering = [ 'name' ]

    #----------------------------------------------------------------------
    # methods
    #----------------------------------------------------------------------

    def __str__( self ):
        # return reference
        string_OUT = ''
        delimiter = ''

        string_OUT = str( self.id ) + ": " + self.name

        return string_OUT

    #-- END method __str__() --#

#= End Project Model ===========================================================


# Location model
class Location( Abstract_Location ):

    # inherit all from parent.
    #name = models.CharField( max_length = 255 )
    #description = models.TextField( blank = True )
    #location = models.ForeignKey( Location, on_delete = models.SET_NULL, blank = True, null = True )

    # Meta-data for this class.
    #class Meta:
    #    ordering = [ 'name', 'location' ]

    #----------------------------------------------------------------------
    # methods
    #----------------------------------------------------------------------

    def __init__( self, *args, **kwargs ):

        # call parent __init()__ first.
        super( Location, self ).__init__( *args, **kwargs )

    #-- END method __init__() --#


#= End Location Model ======================================================


# Topic model
class Topic( models.Model ):
    name = models.CharField( max_length = 255 )
    description = models.TextField( blank = True )
    last_modified = models.DateField( auto_now = True )

    # Meta-data for this class.
    class Meta:
        ordering = [ 'name' ]

    #----------------------------------------------------------------------
    # methods
    #----------------------------------------------------------------------

    def __str__( self ):
        string_OUT = self.name
        return string_OUT

#= End Topic Model =========================================================


# Organization model
class Organization( Abstract_Organization ):

    #----------------------------------------------------------------------------
    # ! ==> Constants-ish
    #----------------------------------------------------------------------------


    #===========================================================================
    # ! ----> Context

    # Entity name prefix
    ENTITY_NAME_PREFIX = "context_text-Organization-"

    # entity type
    ENTITY_TYPE_SLUG_ORGANIZATION = ContextTextBase.CONTEXT_ENTITY_TYPE_SLUG_ORGANIZATION

    # entity identifier types - organization
    ENTITY_ID_TYPE_ORGANIZATION_SOURCENET_ID = ContextTextBase.CONTEXT_ENTITY_ID_TYPE_ORGANIZATION_SOURCENET_ID

    # trait names
    TRAIT_NAME_DESCRIPTION = ContextTextBase.CONTEXT_TRAIT_NAME_DESCRIPTION
    TRAIT_NAME_NAME = ContextTextBase.CONTEXT_TRAIT_NAME_NAME
    TRAIT_NAME_LOCATION_ID = ContextTextBase.CONTEXT_TRAIT_NAME_SOURCENET_LOCATION_ID


    #----------------------------------------------------------------------
    # ! ==> model fields and meta
    #----------------------------------------------------------------------

    # inherit all from parent.
    #name = models.CharField( max_length = 255 )
    #description = models.TextField( blank = True )
    location = models.ForeignKey( Location, on_delete = models.SET_NULL, blank = True, null = True )
    #entity = models.ForeignKey( Entity, on_delete = models.SET_NULL, blank = True, null = True )

    # Meta-data for this class.
    #class Meta:
    #    ordering = [ 'name', 'location' ]


    #---------------------------------------------------------------------------
    # ! ==> overridden built-in methods
    #---------------------------------------------------------------------------


    def __init__( self, *args, **kwargs ):

        # call parent __init()__ first.
        super( Organization, self ).__init__( *args, **kwargs )

        # then, initialize variable.
        self.my_entity_name_prefix = self.ENTITY_NAME_PREFIX
        self.my_entity_type_slug = self.ENTITY_TYPE_SLUG_ORGANIZATION
        self.my_base_entity_id_type = self.ENTITY_ID_TYPE_ORGANIZATION_SOURCENET_ID

    #-- END method __init__() --#


    #----------------------------------------------------------------------
    # ! ==> instance methods
    #----------------------------------------------------------------------


    def update_entity( self ):

        '''
        Based on current instance, creates and populates an entity for the
            model based on the contents of the instance, returns the entity
            instance.

        If you just want to get a fully-populated ID loaded into this instance,
            call this method, not load_entity().  load_entity() will create a
            new instance if one doesn't exist, but it does not fill in all of
            the details - because this method does!
        '''

        # return reference
        entity_OUT = None

        # declare variables - create new.
        entity_instance = None
        entity_type = None
        trait_name = None
        trait_definition = None
        trait_instance = None
        trait_value = None
        trait_type = None
        identifier_type_name = None
        identifier_type = None
        identifier_instance = None
        identifier_uuid = None
        identifier_source = None

        # load entity for article.
        entity_instance = self.load_entity( do_create_if_none_IN = True )

        # got an entity?
        if ( entity_instance is not None ):

            # get entity type (won't duplicate if already added).
            entity_type = entity_instance.add_entity_type( self.my_entity_type_slug )

            # make sure we return it at this point, since it has been
            #    created and stored in database.
            entity_OUT = entity_instance

            #------------------------------------------------------------------#
            # ! ----> set entity traits

            # ! --------> name
            trait_name = self.TRAIT_NAME_NAME
            trait_value = self.name

            # initialize trait from predefined entity type trait "pub_date".
            trait_definition = entity_type.get_trait_spec( trait_name )

            # add trait
            entity_instance.set_entity_trait( trait_name,
                                              trait_value,
                                              entity_type_trait_IN = trait_definition )

            # ! --------> description
            trait_name = self.TRAIT_NAME_DESCRIPTION
            trait_value = self.description
            entity_instance.set_entity_trait( trait_name,
                                              trait_value,
                                              slug_IN = slugify( trait_name ) )

            # ! --------> location.id
            trait_instance = self.location
            trait_name = self.TRAIT_NAME_LOCATION_ID

            # is there an instance?
            if ( trait_instance is not None ):

                trait_value = trait_instance.id

            else:

                # no organization, set it to None.
                trait_value = None

            #-- END check to see if organization present. --#

            entity_instance.set_entity_trait( trait_name,
                                              trait_value,
                                              slug_IN = slugify( trait_name ) )

            #------------------------------------------------------------------#
            # ! ----> add identifiers

            # ! --------> for django ID in this system.
            identifier_type = Entity_Identifier_Type.get_type_for_name( self.my_base_entity_id_type )
            identifier_uuid = self.id
            entity_instance.set_identifier( identifier_uuid,
                                            name_IN = identifier_type.name,
                                            entity_identifier_type_IN = identifier_type )

        else:

            # no entity, can't add/update traits or identifiers
            print( "no entity, can't add/update traits or identifiers" )
            entity_OUT = None

        #-- END check to make sure we have an entity --#

        return entity_OUT

    #-- END method update_entity() --#


#= End Organization Model ======================================================


# Person model
class Person( Abstract_Person ):

    #----------------------------------------------------------------------------
    # ! ==> Constants-ish
    #----------------------------------------------------------------------------


    EXTERNAL_UUID_NAME_OPEN_CALAIS = "OpenCalais API URI (URL)"
    EXTERNAL_UUID_SOURCE_OPEN_CALAIS = "OpenCalais_REST_API"
    EXTERNAL_UUID_NAME_OPEN_CALAIS_V2 = "OpenCalais API V2 URI (URL)"
    EXTERNAL_UUID_SOURCE_OPEN_CALAIS_V2 = "OpenCalais_REST_API_v2"

    # list of Open Calais UUID names.
    EXTERNAL_UUID_NAME_OPEN_CALAIS_LIST = []
    EXTERNAL_UUID_NAME_OPEN_CALAIS_LIST.append( EXTERNAL_UUID_NAME_OPEN_CALAIS )
    EXTERNAL_UUID_NAME_OPEN_CALAIS_LIST.append( EXTERNAL_UUID_NAME_OPEN_CALAIS_V2 )


    #===========================================================================
    # ! ----> Context

    # Entity name prefix
    ENTITY_NAME_PREFIX = "context_text-Person-"

    # entity type
    ENTITY_TYPE_SLUG_PERSON = ContextTextBase.CONTEXT_ENTITY_TYPE_SLUG_PERSON

    # entity identifier types - organization
    ENTITY_ID_TYPE_PERSON_OPEN_CALAIS_UUID = ContextTextBase.CONTEXT_ENTITY_ID_TYPE_NAME_PERSON_OPEN_CALAIS_UUID
    ENTITY_ID_TYPE_PERSON_SOURCENET_ID = ContextTextBase.CONTEXT_ENTITY_ID_TYPE_NAME_PERSON_SOURCENET_ID

    # trait names
    TRAIT_NAME_FIRST_NAME = ContextTextBase.CONTEXT_TRAIT_NAME_FIRST_NAME
    TRAIT_NAME_FULL_NAME = ContextTextBase.CONTEXT_TRAIT_NAME_FULL_NAME
    TRAIT_NAME_GENDER = ContextTextBase.CONTEXT_TRAIT_NAME_GENDER
    TRAIT_NAME_LAST_NAME = ContextTextBase.CONTEXT_TRAIT_NAME_LAST_NAME
    TRAIT_NAME_MIDDLE_NAME = ContextTextBase.CONTEXT_TRAIT_NAME_MIDDLE_NAME
    TRAIT_NAME_NAME_PREFIX = ContextTextBase.CONTEXT_TRAIT_NAME_NAME_PREFIX
    TRAIT_NAME_NAME_SUFFIX = ContextTextBase.CONTEXT_TRAIT_NAME_NAME_SUFFIX
    TRAIT_NAME_ORGANIZATION_ID = ContextTextBase.CONTEXT_TRAIT_NAME_SOURCENET_ORGANIZATION_ID
    TRAIT_NAME_TITLE = ContextTextBase.CONTEXT_TRAIT_NAME_TITLE


    #----------------------------------------------------------------------
    # ! ==> model fields and meta
    #----------------------------------------------------------------------

    # Properties from Abstract_Person:
    '''
    GENDER_CHOICES = (
        ( 'na', 'Unknown' ),
        ( 'female', 'Female' ),
        ( 'male', 'Male' )
    )

    first_name = models.CharField( max_length = 255 )
    middle_name = models.CharField( max_length = 255, blank = True )
    last_name = models.CharField( max_length = 255 )
    name_prefix = models.CharField( max_length = 255, blank = True, null = True )
    name_suffix = models.CharField( max_length = 255, blank = True, null = True )
    full_name_string = models.CharField( max_length = 255, blank = True, null = True )
    gender = models.CharField( max_length = 6, choices = GENDER_CHOICES )
    title = models.CharField( max_length = 255, blank = True )
    nameparser_pickled = models.TextField( blank = True, null = True )
    is_ambiguous = models.BooleanField( default = False )
    notes = models.TextField( blank = True )
    '''
    organization = models.ForeignKey( Organization, on_delete = models.SET_NULL, blank = True, null = True )
    #entity = models.ForeignKey( Entity, on_delete = models.SET_NULL, blank = True, null = True )


    #---------------------------------------------------------------------------
    # ! ==> overridden built-in methods
    #---------------------------------------------------------------------------


    def __init__( self, *args, **kwargs ):

        # call parent __init()__ first.
        super( Person, self ).__init__( *args, **kwargs )

        # then, initialize variable.
        self.my_entity_name_prefix = self.ENTITY_NAME_PREFIX
        self.my_entity_type_slug = self.ENTITY_TYPE_SLUG_PERSON
        self.my_base_entity_id_type = self.ENTITY_ID_TYPE_PERSON_SOURCENET_ID

    #-- END method __init__() --#


    def __str__( self ):

        # return reference
        string_OUT = ''

        if ( self.id ):

            string_OUT = str( self.id ) + " - "

        #-- END check to see if ID --#

        string_OUT += str( self.last_name ) + ', ' + str( self.first_name )
        # middle name?
        if ( self.middle_name ):

            string_OUT += " " + self.middle_name

        #-- END middle name check --#

        if ( ( self.title ) or ( self.organization_string ) ):

            string_OUT += " ( "

            string_list = []

            if ( self.organization_string ):

                # add title to list
                string_list.append( self.organization_string )

            #-- END check for title --#

            if ( self.title ):

                # add title to list
                string_list.append( self.title )

            #-- END check for title --#

            string_OUT += "; ".join( string_list )

            string_OUT += " )"

        #-- END check to see if we have a title, organization, or capture_method. --#

        return string_OUT

    #-- END method __str__() --#


    #----------------------------------------------------------------------
    # ! ==> instance methods
    #----------------------------------------------------------------------


    def associate_newspaper( self, newspaper_IN, notes_IN = None ):

        '''
        Accepts newspaper instance of newspaper in which this person has either
           written or been quoted, plus optional notes to be stored with the
           association.  Checks to see if that newspaper is already associated
           with the person.  If no, creates association.  If yes, returns
           existing record.  If error, returns None.
        '''

        # return reference
        instance_OUT = None

        # declare variables
        me = "associate_newspaper"
        related_newspaper_qs = None
        related_newspaper_count = -1
        debug_message = ""

        # got a newspaper?
        if ( newspaper_IN is not None ):

            # see if Person_Newspaper for this newspaper.
            related_newspaper_qs = self.person_newspaper_set.filter( newspaper = newspaper_IN )

            # got a match?
            related_newspaper_count = related_newspaper_qs.count()
            if ( related_newspaper_count == 0 ):

                # No. Relate newspaper to person.
                instance_OUT = Person_Newspaper()

                # set values
                instance_OUT.person = self
                instance_OUT.newspaper = newspaper_IN

                if ( notes_IN is not None ):

                    instance_OUT.notes = notes_IN

                #-- END check to see if notes. --#

                # save.
                instance_OUT.save()

                debug_message = "In Person." + me + ": ----> created tie from " + str( self ) + " to newspaper " + str( newspaper_IN )
                output_debug( debug_message )

            else:

                # return reference.  Use get().  If more than one, error, so
                #    exception is fine.
                instance_OUT = related_newspaper_qs.get()

                debug_message = "In Person." + me + ": ----> tie exists from " + str( self ) + " to newspaper " + str( newspaper_IN )
                output_debug( debug_message )

            # -- END check to see if Person_Newspaper for current paper. --#

        #-- END check to see if newspaper passed in. --#

        return instance_OUT

    #-- END method associate_newspaper() --#


    def associate_external_uuid( self, uuid_IN, source_IN, name_IN = None, notes_IN = None ):

        '''
        Accepts UUID for the person from an external system (the source), plus
           optional name and notes on the UUID.  Checks to see if that UUID is
           already associated with the person.  If no, creates association.  If
           yes, returns existing record.  If error, returns None.
        '''

        # return reference
        instance_OUT = None

        # declare variables
        me = "associate_external_uuid"
        related_uuid_qs = None
        related_uuid_count = -1
        debug_message = ""

        # got a UUID value?
        if ( ( uuid_IN is not None ) and ( uuid_IN != "" ) ):

            # we do.  See if person is already associated with the UUID.
            related_uuid_qs = self.person_external_uuid_set.filter( uuid = uuid_IN )
            related_uuid_qs = related_uuid_qs.filter( source = source_IN )
            if ( name_IN is not None ):
                related_uuid_qs = related_uuid_qs.filter( name = name_IN )
            #-- END check to see if name present --#

            # got a match?
            related_uuid_count = related_uuid_qs.count()
            if ( related_uuid_count == 0 ):

                # not yet associated.  Make Person_External_UUID association.
                instance_OUT = Person_External_UUID()

                # set values
                instance_OUT.person = self
                instance_OUT.uuid = uuid_IN

                if ( source_IN is not None ):

                    instance_OUT.source = source_IN

                #-- END check to see if source of UUID passed in. --#

                if ( name_IN is not None ):

                    instance_OUT.name = name_IN

                #-- END check to see if name passed in. --#

                if ( notes_IN is not None ):

                    instance_OUT.notes = notes_IN

                #-- END check to see if notes passed in. --#

                # save.
                instance_OUT.save()

                debug_message = "In Person." + me + ": ----> created tie from {} to UUID {}" .format( self, instance_OUT )
                output_debug( debug_message )

            else:

                # return reference.  Use get().  If more than one, error, so
                #    exception is fine.
                instance_OUT = related_uuid_qs.get()

                debug_message = "In Person." + me + ": ----> tie exists from {} to UUID {}" .format( self, instance_OUT )
                output_debug( debug_message )

            #-- END check to see if UUID match. --#

        #-- END check to see if external UUID --#

        return instance_OUT

    #-- END method associate_external_uuid() --#


    def update_entity( self ):

        '''
        Based on current instance, creates and populates an entity for the
            model based on the contents of the instance, returns the entity
            instance.

        If you just want to get a fully-populated ID loaded into this instance,
            call this method, not load_entity().  load_entity() will create a
            new instance if one doesn't exist, but it does not fill in all of
            the details - because this method does!
        '''

        # return reference
        entity_OUT = None

        # declare variables - create new.
        me = "update_entity"
        debug_message = None
        entity_instance = None
        entity_type = None
        trait_name = None
        trait_definition = None
        trait_instance = None
        instance_has_entity = None
        trait_value = None
        trait_type = None
        identifier_type_name = None
        identifier_type = None
        identifier_instance = None
        identifier_uuid = None
        identifier_source = None
        identifier_qs = None

        # identifier information
        my_id_name = None
        my_id_uuid = None
        my_id_id_type = None
        my_id_source = None
        my_id_notes = None
        is_id_present = None
        is_uuid_in_use = None

        # load entity for article.
        entity_instance = self.load_entity( do_create_if_none_IN = True )

        # got an entity?
        if ( entity_instance is not None ):

            # get entity type (won't duplicate if already added).
            entity_type = entity_instance.add_entity_type( self.my_entity_type_slug )

            # make sure we return it at this point, since it has been
            #    created and stored in database.
            entity_OUT = entity_instance

            #------------------------------------------------------------------#
            # ! ----> set predefined entity traits

            # ! --------> first_name
            trait_name = self.TRAIT_NAME_FIRST_NAME
            trait_value = self.first_name

            # initialize trait from predefined entity type trait for name.
            trait_definition = entity_type.get_trait_spec( trait_name )

            # add trait
            entity_instance.set_entity_trait( trait_name,
                                              trait_value,
                                              entity_type_trait_IN = trait_definition )

            # ! --------> middle_name
            trait_name = self.TRAIT_NAME_MIDDLE_NAME
            trait_value = self.middle_name

            # initialize trait from predefined entity type trait for name.
            trait_definition = entity_type.get_trait_spec( trait_name )

            # add trait
            entity_instance.set_entity_trait( trait_name,
                                              trait_value,
                                              entity_type_trait_IN = trait_definition )

            # ! --------> last_name
            trait_name = self.TRAIT_NAME_LAST_NAME
            trait_value = self.last_name

            # initialize trait from predefined entity type trait for name.
            trait_definition = entity_type.get_trait_spec( trait_name )

            # add trait
            entity_instance.set_entity_trait( trait_name,
                                              trait_value,
                                              entity_type_trait_IN = trait_definition )

            #------------------------------------------------------------------#
            # ! ----> set free-form entity traits

            # ! --------> name_prefix
            trait_name = self.TRAIT_NAME_NAME_PREFIX
            trait_value = self.name_prefix
            entity_instance.set_entity_trait( trait_name,
                                              trait_value,
                                              slug_IN = slugify( trait_name ) )

            # ! --------> name_suffix
            trait_name = self.TRAIT_NAME_NAME_SUFFIX
            trait_value = self.name_suffix
            entity_instance.set_entity_trait( trait_name,
                                              trait_value,
                                              slug_IN = slugify( trait_name ) )

            # ! --------> full_name_string
            trait_name = self.TRAIT_NAME_FULL_NAME
            trait_value = self.full_name_string
            entity_instance.set_entity_trait( trait_name,
                                              trait_value,
                                              slug_IN = slugify( trait_name ) )

            # ! --------> gender
            trait_name = self.TRAIT_NAME_GENDER
            trait_value = self.gender
            entity_instance.set_entity_trait( trait_name,
                                              trait_value,
                                              slug_IN = slugify( trait_name ) )

            # ! --------> title
            trait_name = self.TRAIT_NAME_TITLE
            trait_value = self.title
            entity_instance.set_entity_trait( trait_name,
                                              trait_value,
                                              slug_IN = slugify( trait_name ) )

            # ! --------> organization_id
            trait_instance = self.organization
            trait_name = self.TRAIT_NAME_ORGANIZATION_ID

            # is there an organization?
            if ( trait_instance is not None ):

                trait_value = trait_instance.id

                # and check if instance has an entity.  If not, create one.
                instance_has_entity = trait_instance.has_entity()
                if ( instance_has_entity == False ):

                    # create one.
                    trait_instance.update_entity()

                #-- END check to see if instance has entity. --#

            else:

                # no organization, set it to None.
                trait_value = None

            #-- END check to see if organization present. --#

            entity_instance.set_entity_trait( trait_name,
                                              trait_value,
                                              slug_IN = slugify( trait_name ) )

            #------------------------------------------------------------------#
            # ! ----> add identifiers

            # ! --------> for django ID in this system.
            identifier_type = Entity_Identifier_Type.get_type_for_name( self.my_base_entity_id_type )
            identifier_uuid = self.id
            entity_instance.set_identifier( identifier_uuid,
                                            name_IN = identifier_type.name,
                                            entity_identifier_type_IN = identifier_type )

            # ! --------> external UUIDs

            # get QuerySet of external IDs.
            identifier_qs = self.person_external_uuid_set.all()

            # loop over identifiers.
            for identifier_instance in identifier_qs:

                # retrieve identifier information
                my_id_name = identifier_instance.name
                my_id_uuid = identifier_instance.uuid
                my_id_id_type = identifier_instance.id_type
                my_id_source = identifier_instance.source
                my_id_notes = identifier_instance.notes
                my_id_type_name = None

                # see if it is an OpenCalais ID.
                if ( my_id_name in self.EXTERNAL_UUID_NAME_OPEN_CALAIS_LIST ):

                    # it is.  retrieve pre-defined OpenCalais identifier type.
                    my_id_type_name = self.ENTITY_ID_TYPE_PERSON_OPEN_CALAIS_UUID

                else:

                    # it is not - try to retrieve type for value in id_type.
                    my_id_type_name = my_id_id_type

                #-- END check to see if known type. --#

                # try to load type, then set identifier.
                identifier_type = Entity_Identifier_Type.get_type_for_name( my_id_type_name )
                identifier_uuid = my_id_uuid

                # did we find an identifier_type?
                if ( identifier_type is not None ):

                    # also need to set name - when there is an ID type, the
                    #     type name overrides any name passed in.
                    my_id_name = identifier_type.name

                #-- END check to see if we found a type --#

                # is identifier with matching identity already present?
                #identifier_instance = entity_instance.get_identifier( my_id_name,
                #                                                      id_source_IN = my_id_source,
                #                                                      id_id_type_IN = my_id_id_type,
                #                                                      id_type_IN = None )

                # does identifier already exist?
                identifier_instance = entity_instance.get_identifier( my_id_name,
                                                                      id_source_IN = my_id_source,
                                                                      id_id_type_IN = my_id_id_type,
                                                                      id_type_IN = identifier_type,
                                                                      id_uuid_IN = identifier_uuid )

                # if UUID not in use, set identifier.
                if ( identifier_instance is None ):

                    # not in use.  Add it.
                    entity_instance.set_identifier( identifier_uuid,
                                                    name_IN = my_id_name,
                                                    id_type_IN = my_id_id_type,
                                                    source_IN = my_id_source,
                                                    notes_IN = my_id_notes,
                                                    entity_identifier_type_IN = identifier_type )

                else:

                    debug_message = "In Person." + me + ": ----> Entity Identifier created tie from {} to UUID {}" .format( self, entity_instance )
                    output_debug( debug_message )

                #-- END check to see if UUID already present. --#

            #-- END loop over identifiers. --#

        else:

            # no entity, can't add/update traits or identifiers
            print( "no entity, can't add/update traits or identifiers" )
            entity_OUT = None

        #-- END check to make sure we have an entity --#

        return entity_OUT

    #-- END method update_entity() --#


#== END Person Model ===========================================================#


# Alternate_Name model
class Alternate_Name( Abstract_Person ):

    '''
    Model that can be used to hold alternate names for a given person.
       For now, no way to tie to newspaper or external UUID.  And not used at the
       moment.  But, planning ahead...
    '''

    # Properties from Abstract_Person:
    '''
    GENDER_CHOICES = (
        ( 'na', 'Unknown' ),
        ( 'female', 'Female' ),
        ( 'male', 'Male' )
    )

    first_name = models.CharField( max_length = 255 )
    middle_name = models.CharField( max_length = 255, blank = True )
    last_name = models.CharField( max_length = 255 )
    name_prefix = models.CharField( max_length = 255, blank = True, null = True )
    name_suffix = models.CharField( max_length = 255, blank = True, null = True )
    full_name_string = models.CharField( max_length = 255, blank = True, null = True )
    gender = models.CharField( max_length = 6, choices = GENDER_CHOICES )
    title = models.CharField( max_length = 255, blank = True )
    nameparser_pickled = models.TextField( blank = True, null = True )
    is_ambiguous = models.BooleanField( default = False )
    notes = models.TextField( blank = True )
    '''

    person = models.ForeignKey( Person, on_delete = models.CASCADE )
    organization = models.ForeignKey( Organization, on_delete = models.SET_NULL, blank = True, null = True )

    #----------------------------------------------------------------------
    # instance methods
    #----------------------------------------------------------------------

    def __str__( self ):

        # return reference
        string_OUT = ''

        if ( self.id ):

            string_OUT = str( self.id ) + " - "

        #-- END check to see if ID --#

        string_OUT = self.last_name + ', ' + self.first_name

        # middle name?
        if ( self.middle_name ):

            string_OUT += " " + self.middle_name

        #-- END middle name check --#

        if ( self.title ):

            string_OUT = string_OUT + " ( " + self.title + " )"

        #-- END check to see if we have a title. --#

        return string_OUT

    #-- END method __str__() --#


#== END Alternate_Name Model ===========================================================#


# Person_Organization model
class Person_Organization( models.Model ):

    person = models.ForeignKey( Person, on_delete = models.CASCADE )
    organization = models.ForeignKey( Organization, on_delete = models.CASCADE, blank = True, null = True )
    title = models.CharField( max_length = 255, blank = True )

    #----------------------------------------------------------------------
    # methods
    #----------------------------------------------------------------------

    def __str__( self ):
        string_OUT = self.organization.name
        if ( self.title != '' ):
            string_OUT = string_OUT + " ( " + self.title + " )"
        return string_OUT

#= End Person_Organization Model ======================================================


# Document model
class Document( models.Model ):

    name = models.CharField( max_length = 255 )
    description = models.TextField( blank = True)
    organization = models.ForeignKey( Organization, on_delete = models.SET_NULL, blank = True, null = True )

    #----------------------------------------------------------------------
    # methods
    #----------------------------------------------------------------------

    def __str__( self ):
        string_OUT = self.name
        return string_OUT

#= End Document Model ======================================================


# Newspaper model
class Newspaper( Abstract_Entity_Container ):


    #----------------------------------------------------------------------------
    # ! ==> Constants-ish
    #----------------------------------------------------------------------------


    #===========================================================================
    # ! ----> Context

    # Entity name prefix
    ENTITY_NAME_PREFIX = "context_text-Newspaper-"

    # entity type
    ENTITY_TYPE_SLUG_NEWSPAPER = ContextTextBase.CONTEXT_ENTITY_TYPE_SLUG_NEWSPAPER

    # entity identifier types - general
    ENTITY_ID_TYPE_PERMALINK = ContextTextBase.CONTEXT_ENTITY_ID_TYPE_PERMALINK

    # entity identifier types - articles
    ENTITY_ID_TYPE_NEWSPAPER_SOURCENET_ID = ContextTextBase.CONTEXT_ENTITY_ID_TYPE_NEWSPAPER_SOURCENET_ID
    ENTITY_ID_TYPE_NEWSPAPER_NEWSBANK_CODE = ContextTextBase.CONTEXT_ENTITY_ID_TYPE_NEWSPAPER_NEWSBANK_CODE

    # trait names
    TRAIT_NAME_DESCRIPTION = ContextTextBase.CONTEXT_TRAIT_NAME_DESCRIPTION
    TRAIT_NAME_NAME = ContextTextBase.CONTEXT_TRAIT_NAME_NAME
    TRAIT_NAME_ORGANIZATION_ID = ContextTextBase.CONTEXT_TRAIT_NAME_SOURCENET_ORGANIZATION_ID
    TRAIT_NAME_SECTIONS_LOCAL_NEWS = ContextTextBase.CONTEXT_TRAIT_NAME_SECTIONS_LOCAL_NEWS
    TRAIT_NAME_SECTIONS_SPORTS = ContextTextBase.CONTEXT_TRAIT_NAME_SECTIONS_SPORTS


    #----------------------------------------------------------------------
    # ! ==> model fields and meta
    #----------------------------------------------------------------------


    name = models.CharField( max_length = 255 )
    description = models.TextField( blank = True )
    organization = models.ForeignKey( Organization, on_delete = models.SET_NULL, null = True, blank = True )
    newsbank_code = models.CharField( max_length = 255, null = True, blank = True )
    sections_local_news = models.TextField( blank = True, null = True )
    sections_sports = models.TextField( blank = True, null = True )

    #location = models.ForeignKey( Location, on_delete = models.SET_NULL, null = True, blank = True )
    #entity = models.ForeignKey( Entity, on_delete = models.SET_NULL, blank = True, null = True )

    #----------------------------------------------------------------------
    # ! ==> Meta
    #----------------------------------------------------------------------


    # Meta-data for this class.
    class Meta:

        ordering = [ 'name' ]

    #-- END Meta class --#


    #---------------------------------------------------------------------------
    # ! ==> overridden built-in methods
    #---------------------------------------------------------------------------


    def __init__( self, *args, **kwargs ):

        # call parent __init()__ first.
        super( Newspaper, self ).__init__( *args, **kwargs )

        # then, initialize variable.
        self.my_entity_name_prefix = self.ENTITY_NAME_PREFIX
        self.my_entity_type_slug = self.ENTITY_TYPE_SLUG_NEWSPAPER
        self.my_base_entity_id_type = self.ENTITY_ID_TYPE_NEWSPAPER_SOURCENET_ID

    #-- END method __init__() --#


    def __str__( self ):

        # return reference
        string_OUT = ""

        # got an ID?
        if ( self.id ):

            # output ID
            string_OUT += str( self.id ) + " - "

        #-- END check to see if ID. --#

        string_OUT += self.name

        # got a newsbank code?
        current_value = self.newsbank_code
        if ( ( current_value is not None ) and ( current_value != "" ) ):

            # yes.  Append it.
            string_OUT += " ( " + current_value + " )"

        #-- END check to see if newsbank_code --#

        return string_OUT

    #-- END method __str__() --#


    #----------------------------------------------------------------------
    # ! ==> instance methods
    #----------------------------------------------------------------------


    def update_entity( self ):

        '''
        Based on current instance, creates and populates an entity for the
            model based on the contents of the instance, returns the entity
            instance.

        If you just want to get a fully-populated ID loaded into this instance,
            call this method, not load_entity().  load_entity() will create a
            new instance if one doesn't exist, but it does not fill in all of
            the details - because this method does!
        '''

        # return reference
        entity_OUT = None

        # declare variables - create new.
        entity_instance = None
        entity_type = None
        trait_name = None
        trait_definition = None
        trait_instance = None
        instance_has_entity = None
        trait_value = None
        trait_type = None
        identifier_type_name = None
        identifier_type = None
        identifier_instance = None
        identifier_uuid = None
        identifier_source = None

        # load entity for article.
        entity_instance = self.load_entity( do_create_if_none_IN = True )

        # got an entity?
        if ( entity_instance is not None ):

            # get entity type (won't duplicate if already added).
            entity_type = entity_instance.add_entity_type( self.my_entity_type_slug )

            # make sure we return it at this point, since it has been
            #    created and stored in database.
            entity_OUT = entity_instance

            #------------------------------------------------------------------#
            # ! ----> set entity traits

            # ! --------> name
            trait_name = self.TRAIT_NAME_NAME
            trait_value = self.name

            # initialize trait from predefined entity type trait for name.
            trait_definition = entity_type.get_trait_spec( trait_name )

            # add trait
            entity_instance.set_entity_trait( trait_name,
                                              trait_value,
                                              entity_type_trait_IN = trait_definition )

            # ! --------> description
            trait_name = self.TRAIT_NAME_DESCRIPTION
            trait_value = self.description
            entity_instance.set_entity_trait( trait_name,
                                              trait_value,
                                              slug_IN = slugify( trait_name ) )

            # ! --------> organization_id
            trait_instance = self.organization
            trait_name = self.TRAIT_NAME_ORGANIZATION_ID

            # is there an organization?
            if ( trait_instance is not None ):

                trait_value = trait_instance.id

                # and check if instance has an entity.  If not, create one.
                instance_has_entity = trait_instance.has_entity()
                if ( instance_has_entity == False ):

                    # create one.
                    trait_instance.update_entity()

                #-- END check to see if instance has entity. --#

            else:

                # no organization, set it to None.
                trait_value = None

            #-- END check to see if organization present. --#

            entity_instance.set_entity_trait( trait_name,
                                              trait_value,
                                              slug_IN = slugify( trait_name ) )

            # ! --------> sections_local_news
            trait_name = self.TRAIT_NAME_SECTIONS_LOCAL_NEWS
            trait_value = self.sections_local_news
            entity_instance.set_entity_trait( trait_name,
                                              trait_value,
                                              slug_IN = slugify( trait_name ) )

            # ! --------> sections_sports
            trait_name = self.TRAIT_NAME_SECTIONS_SPORTS
            trait_value = self.sections_sports
            entity_instance.set_entity_trait( trait_name,
                                              trait_value,
                                              slug_IN = slugify( trait_name ) )

            #------------------------------------------------------------------#
            # ! ----> add identifiers

            # ! --------> for django ID in this system.
            identifier_type = Entity_Identifier_Type.get_type_for_name( self.my_base_entity_id_type )
            identifier_uuid = self.id
            entity_instance.set_identifier( identifier_uuid,
                                            name_IN = identifier_type.name,
                                            entity_identifier_type_IN = identifier_type )

            # ! --------> for newsbank code.
            identifier_type = Entity_Identifier_Type.get_type_for_name( self.ENTITY_ID_TYPE_NEWSPAPER_NEWSBANK_CODE )
            identifier_uuid = self.newsbank_code
            entity_instance.set_identifier( identifier_uuid,
                                            name_IN = identifier_type.name,
                                            entity_identifier_type_IN = identifier_type )

        else:

            # no entity, can't add/update traits or identifiers
            print( "no entity, can't add/update traits or identifiers" )
            entity_OUT = None

        #-- END check to make sure we have an entity --#

        return entity_OUT

    #-- END method update_entity() --#


#= End Newspaper Model ======================================================


# Article_Topic model
##class Article_Topic( models.Model ):

    #topic = models.ForeignKey( Topic, on_delete = models.CASCADE )
    #rank = models.IntegerField()

    #----------------------------------------------------------------------
    # methods
    #----------------------------------------------------------------------

    #def __str__( self ):

    #    string_OUT = '%d - %s' % ( self.rank, self.topic.name )
    #    return string_OUT

    #-- END __str__() method --#

#= End Article_Topic Model ======================================================


# Person_External_UUID model
class Person_External_UUID( Abstract_UUID ):

    person = models.ForeignKey( Person, on_delete = models.CASCADE )
    #name = models.CharField( max_length = 255, null = True, blank = True )
    #uuid = models.TextField( blank = True, null = True )
    #id_type = models.CharField( max_length = 255, null = True, blank = True )
    #source = models.CharField( max_length = 255, null = True, blank = True )
    #notes = models.TextField( blank = True, null = True )

    #----------------------------------------------------------------------
    # methods
    #----------------------------------------------------------------------

    def __init__( self, *args, **kwargs ):

        # call parent __init()__ first.
        super( Person_External_UUID, self ).__init__( *args, **kwargs )

        # then, initialize variable.
        self.bs_helper = None

    #-- END method __init__() --#

    # just use the parent stuff.

#= End Person_External_UUID Model ======================================================


# Person_Newspaper model
class Person_Newspaper( models.Model ):

    person = models.ForeignKey( Person, on_delete = models.CASCADE )
    newspaper = models.ForeignKey( Newspaper, on_delete = models.CASCADE, blank = True, null = True )
    notes = models.TextField( blank = True, null = True )

    #----------------------------------------------------------------------
    # methods
    #----------------------------------------------------------------------


    def __str__( self ):

        # return reference
        string_OUT = ""

        # declare variables
        prefix_string = ""

        if ( self.id ):

            # yes. output.
            string_OUT += str( self.id )
            prefix_string = " - "

        #-- END check to see if ID --#

        if ( self.newspaper ):

            string_OUT += prefix_string + self.newspaper.name
            prefix_string = " - "

        #-- END check to see if newspaper. --#

        if ( self.person ):

            string_OUT += prefix_string + str( self.person.id )
            prefix_string = " - "

        #-- END check to see if newspaper. --#

        return string_OUT

    #-- END method __str__() --#


#= End Person_Newspaper Model ======================================================


# Article model
class Article( Abstract_Entity_Container ):

    #----------------------------------------------------------------------------
    # ! ==> Constants-ish
    #----------------------------------------------------------------------------


    # status values
    STATUS_NEW = "new"
    STATUS_ERROR = "error"
    STATUS_DEFAULT = STATUS_NEW

    # cleanup_status values
    CLEANUP_STATUS_NEW = "new"
    CLEANUP_STATUS_AUTHOR_FIXED = "author_fixed"
    CLEANUP_STATUS_AUTHOR_ERROR = "author_error"
    CLEANUP_STATUS_TEXT_FIXED = "text_fixed"
    CLEANUP_STATUS_TEXT_ERROR = "text_error"
    CLEANUP_STATUS_AUTHOR_AND_TEXT_FIXED = "author_and_text_fixed"
    CLEANUP_STATUS_COMPLETE = "complete"
    CLEANUP_STATUS_ERROR = "error"
    CLEANUP_STATUS_DEFAULT = CLEANUP_STATUS_NEW

    CLEANUP_STATUS_CHOICES = (
        ( CLEANUP_STATUS_NEW, "new" ),
        ( CLEANUP_STATUS_AUTHOR_FIXED, "author fixed" ),
        ( CLEANUP_STATUS_AUTHOR_ERROR, "author error" ),
        ( CLEANUP_STATUS_TEXT_FIXED, "text fixed" ),
        ( CLEANUP_STATUS_TEXT_ERROR , "text error" ),
        ( CLEANUP_STATUS_AUTHOR_AND_TEXT_FIXED, "author & text fixed" ),
        ( CLEANUP_STATUS_COMPLETE, "complete" ),
        ( CLEANUP_STATUS_ERROR, "error" )
    )

    # parameters that can be passed in to class methods
    PARAM_AUTOPROC_ALL = "autoproc_all"
    PARAM_AUTOPROC_AUTHORS = "autoproc_authors"

    # author_string
    AUTHOR_STRING_DIVIDER = "/"

    #===========================================================================
    # ! ----> filter (LOOKUP) parameters

    # newspaper filter (expects instance of Newspaper model)
    PARAM_NEWSPAPER_ID = ContextTextBase.PARAM_NEWSPAPER_ID
    PARAM_NEWSPAPER_NEWSBANK_CODE = ContextTextBase.PARAM_NEWSPAPER_NEWSBANK_CODE
    PARAM_NEWSPAPER_INSTANCE = ContextTextBase.PARAM_NEWSPAPER_INSTANCE
    PARAM_NEWSPAPER_ID_IN_LIST = ContextTextBase.PARAM_NEWSPAPER_ID_IN_LIST
    PARAM_PUBLICATION_LIST = ContextTextBase.PARAM_PUBLICATION_LIST  # same as newspaper id in list, for compatibility.

    # date range filter parameters, for article lookup.
    PARAM_START_DATE = ContextTextBase.PARAM_START_DATE
    PARAM_END_DATE = ContextTextBase.PARAM_END_DATE
    PARAM_SINGLE_DATE = ContextTextBase.PARAM_SINGLE_DATE
    PARAM_DATE_RANGE = ContextTextBase.PARAM_DATE_RANGE
    DEFAULT_DATE_FORMAT = ContextTextBase.DEFAULT_DATE_FORMAT

    # section selection parameters.
    PARAM_SECTION_NAME = ContextTextBase.PARAM_SECTION_NAME
    PARAM_SECTION_NAME_LIST = ContextTextBase.PARAM_SECTION_NAME_LIST
    PARAM_SECTION_NAME_IN_LIST = PARAM_SECTION_NAME_LIST
    PARAM_SECTION_LIST = ContextTextBase.PARAM_SECTION_LIST
    PARAM_CUSTOM_SECTION_Q = "custom_section_q"
    PARAM_JUST_PROCESS_ALL = "just_process_all" # set to True if just want sum of all sections, not records for each individual section.  If False, processes each section individually, then generates the "all" record.

    # filter on tags.
    PARAM_TAGS_IN_LIST = ContextTextBase.PARAM_TAGS_IN_LIST
    PARAM_TAG_LIST = ContextTextBase.PARAM_TAG_LIST
    PARAM_TAGS_NOT_IN_LIST = ContextTextBase.PARAM_TAGS_NOT_IN_LIST

    # other article parameters.
    PARAM_UNIQUE_ID_IN_LIST = ContextTextBase.PARAM_UNIQUE_ID_LIST   # list of unique identifiers of articles whose data you want included.
    PARAM_ARTICLE_ID_IN_LIST = ContextTextBase.PARAM_ARTICLE_ID_LIST   # list of ids of articles whose data you want included.
    PARAM_CUSTOM_ARTICLE_Q = ContextTextBase.PARAM_CUSTOM_ARTICLE_Q
    PARAM_GET_DISTINCT_RECORDS = ContextTextBase.PARAM_GET_DISTINCT_RECORDS

    #===========================================================================
    # ! ----> Django queryset parameters

    # variables for building nuanced queries in django.
    # Will be specific to each paper, so using Grand Rapids Press as example.

    # Grand Rapids Press
    GRP_LOCAL_SECTION_NAME_LIST = [ "Business", "City and Region", "Front Page", "Lakeshore", "Religion", "Special", "Sports", "State" ]
    GRP_NEWS_SECTION_NAME_LIST = [ "Business", "City and Region", "Front Page", "Lakeshore", "Religion", "Special", "State" ]
    Q_GRP_IN_HOUSE_AUTHOR = Q( author_varchar__iregex = r'.* */ *THE GRAND RAPIDS PRESS$' ) | Q( author_varchar__iregex = r'.* */ *PRESS .* EDITOR$' ) | Q( author_varchar__iregex = r'.* */ *GRAND RAPIDS PRESS .* BUREAU$' ) | Q( author_varchar__iregex = r'.* */ *SPECIAL TO THE PRESS$' )


    #===========================================================================
    # ! ----> Context

    # Entity name prefix
    ENTITY_NAME_PREFIX = "context_text-Article-"

    # entity type
    ENTITY_TYPE_SLUG_ARTICLE = ContextTextBase.CONTEXT_ENTITY_TYPE_SLUG_ARTICLE

    # entity identifier types - general
    ENTITY_ID_TYPE_PERMALINK = ContextTextBase.CONTEXT_ENTITY_ID_TYPE_PERMALINK

    # entity identifier types - articles
    ENTITY_ID_TYPE_ARTICLE_ARCHIVE_IDENTIFIER = ContextTextBase.CONTEXT_ENTITY_ID_TYPE_ARTICLE_ARCHIVE_IDENTIFIER
    ENTITY_ID_TYPE_ARTICLE_SOURCENET_ID = ContextTextBase.CONTEXT_ENTITY_ID_TYPE_ARTICLE_SOURCENET_ID
    ENTITY_ID_TYPE_ARTICLE_NEWSBANK_ID = ContextTextBase.CONTEXT_ENTITY_ID_TYPE_ARTICLE_NEWSBANK_ID

    # entity identifier types - default
    UNIQUE_ID_TYPE_DEFAULT = ENTITY_ID_TYPE_PERMALINK

    # choices for unique_identifier_type
    UNIQUE_ID_TYPE_CHOICES = (
        ( ENTITY_ID_TYPE_PERMALINK, ENTITY_ID_TYPE_PERMALINK ),
        ( ENTITY_ID_TYPE_ARTICLE_NEWSBANK_ID, ENTITY_ID_TYPE_ARTICLE_NEWSBANK_ID )
    )

    # trait names
    CONTEXT_TRAIT_NAME_PUB_DATE = ContextTextBase.CONTEXT_TRAIT_NAME_PUB_DATE
    CONTEXT_TRAIT_NAME_NEWSPAPER_ID = ContextTextBase.CONTEXT_TRAIT_NAME_SOURCENET_NEWSPAPER_ID


    #---------------------------------------------------------------------------
    # ! ==> Model fields (persisted in database)
    #---------------------------------------------------------------------------

    # ! TODO - need to figure out a way to actually make a unique identifier.
    unique_identifier = models.CharField( max_length = 255, blank = True )
    unique_identifier_type = models.CharField( max_length = 255, blank = True, null = True, choices = UNIQUE_ID_TYPE_CHOICES, default = None )
    source_string = models.CharField( max_length = 255, blank = True, null = True )
    newspaper = models.ForeignKey( Newspaper, on_delete = models.SET_NULL, blank = True, null = True )
    pub_date = models.DateField()
    section = models.CharField( max_length = 255, blank = True )
    #page = models.IntegerField( blank = True )
    page = models.CharField( max_length = 255, blank = True, null = True )
    author_string = models.TextField( blank = True, null = True )
    author_varchar = models.CharField( max_length = 255, blank = True, null = True )
    author_name = models.CharField( max_length = 255, blank = True, null = True )
    author_affiliation = models.CharField( max_length = 255, blank = True, null = True )
    headline = models.CharField( max_length = 255 )
    # What is this? - author = models.CharField( max_length = 255, blank = True, null = True )

    # text = models.TextField( blank = True ) - moved to related Article_Text instance.
    # - to retrieve Article_Text instance for this Article: self.article_text_set.get()

    corrections = models.TextField( blank = True, null = True )
    edition = models.CharField( max_length = 255, blank = True, null = True )
    index_terms = models.TextField( blank = True, null = True )
    archive_source = models.CharField( max_length = 255, blank = True, null = True )
    archive_id = models.CharField( max_length = 255, blank = True, null = True )
    permalink = models.TextField( blank = True, null = True )
    copyright = models.TextField( blank = True, null = True )
    file_path = models.CharField( max_length = 255, blank = True, null = True )

    # notes = models.TextField( blank = True, null = True ) - moved to related Article_Notes instance.
    # - to retrieve Article_Notes instance for this Article: self.article_notes_set.get()

    # raw_html = models.TextField( blank = True, null = True ) - moved to related Article_RawData instance.
    # - to retrieve Article_RawData instance for this Article: self.article_rawdata_set.get()

    status = models.CharField( max_length = 255, blank = True, null = True, default = STATUS_DEFAULT )
    cleanup_status = models.CharField( max_length = 255, blank = True, null = True, choices = CLEANUP_STATUS_CHOICES, default = CLEANUP_STATUS_DEFAULT )
    is_local_news = models.BooleanField( default = 0 )
    is_sports = models.BooleanField( default = 0 )
    is_local_author = models.BooleanField( default = 0 )

    # moved to Abstract_Entity_Container
    # tags!
    #tags = TaggableManager( blank = True )
    #create_date = models.DateTimeField( auto_now_add = True )
    #last_modified = models.DateTimeField( auto_now = True )
    #entity = models.ForeignKey( Entity, on_delete = models.SET_NULL, blank = True, null = True )

    # we have the option of adding these relations here, at an article level,
    #    but for now assuming they are to be coded in Article_Data, not here, so
    #    we can track agreement, compare coding from different coders.
    #topics = models.ManyToManyField( Article_Topic )
    #authors = models.ManyToManyField( Article_Author )
    #subjects = models.ManyToManyField( Article_Subject )
    #locations = models.ManyToManyField( Article_Location, blank = True )

    #----------------------------------------------------------------------------
    # ! ==> Meta class
    #----------------------------------------------------------------------------

    # Meta-data for this class.
    class Meta:
        ordering = [ 'pub_date', 'section', 'page' ]

    #----------------------------------------------------------------------------
    # ! ==> class methods
    #----------------------------------------------------------------------------


    @classmethod
    def add_section_filter_to_article_qs( cls, section_list_IN = [], qs_IN = None, *args, **kwargs ):

        '''
        Accepts section name and query string.  If "all", adds a filter to
           QuerySet where section just has to be one of those in the list of
           locals.  If not all, adds a filter to limit the section to the name.
        Preconditions: instance must have a name set.
        Postconditions: returns the QuerySet passed in with an additional filter
           for section name.  If no QuerySet passed in, creates new Article
           QuerySet, returns it with filter added.
        '''

        # return reference
        qs_OUT = None

        # declare variables
        me = "add_section_filter_to_article_qs"
        my_section_list = ""

        # got a query set?
        if ( qs_IN ):

            # use the one passed in.
            qs_OUT = qs_IN

            #output_debug( "QuerySet passed in, using it.", me, "*** " )

        else:

            # No.  Make one.
            qs_OUT = cls.objects.all()

            #output_debug( "No QuerySet passed in, using fresh one.", me, "*** " )

        #-- END check to see if query set passed in --#

        # get section name.
        my_section_list = section_list_IN

        # got a list?
        if ( ( my_section_list is not None )
            and ( isinstance( my_section_list, list ) == True )
            and ( len( my_section_list ) > 0 ) ):

            # add filter for name being in the list
            qs_OUT = qs_OUT.filter( section__in = my_section_list )

        #-- END check to see if list was populated. --#

        return qs_OUT

    #-- END method add_section_filter_to_article_qs() --#


    @classmethod
    def create_q_article_date_range( cls, start_date_IN = "", end_date_IN = "", *args, **kwargs ):

        '''
        Accepts string start and end dates (YYYY-MM-DD format). in the keyword
           arguments.  Creates a Q() instance that filters dates based on start
           and end date passed in. If both are missing, does nothing.  If one or
           other passed in, filters accordingly.
        Preconditions: Dates must be strings in YYYY-MM-DD format.
        Postconditions: Returns the Q() instance - to use it, you must pass it
           to a QuerySet's filter method.  If neither start nor end dates are
           passed in, returns None.
        '''

        # return reference
        q_OUT = None

        # declare variables
        start_date = ""
        end_date = ""

        # retrieve dates
        # start date
        start_date = start_date_IN
        if ( ( start_date is None ) or ( start_date == "" ) ):

            # no start date passed in. Check in the kwargs.
            if ( cls.PARAM_START_DATE in kwargs ):

                # yup.  Use it.
                start_date = kwargs[ cls.PARAM_START_DATE ]

            #-- END check to see if start date in arguments --#

        #-- END check to see if start date passed in. --#

        # end date
        end_date = end_date_IN
        if( ( end_date is None ) or ( end_date == "" ) ):

            # no end date passed in.  Check in kwargs.
            if ( cls.PARAM_END_DATE in kwargs ):

                # yup.  Use it.
                end_date = kwargs[ cls.PARAM_END_DATE ]

            #-- END check to see if end date in arguments --#

        #-- END check to see if end date passed in.

        if ( ( ( start_date is not None ) and ( start_date != "" ) )
            and ( ( end_date is not None ) and ( end_date != "" ) ) ):

            # both start and end.
            q_OUT = Q( pub_date__gte = datetime.datetime.strptime( start_date, cls.DEFAULT_DATE_FORMAT ) )
            q_OUT = q_OUT & Q( pub_date__lte = datetime.datetime.strptime( end_date, cls.DEFAULT_DATE_FORMAT ) )

        elif( ( start_date is not None ) and ( start_date != "" ) ):

            # just start date
            q_OUT = Q( pub_date__gte = datetime.datetime.strptime( start_date, cls.DEFAULT_DATE_FORMAT ) )

        elif( ( end_date is not None ) and ( end_date != "" ) ):

            # just end date
            q_OUT = Q( pub_date__lte = datetime.datetime.strptime( end_date, cls.DEFAULT_DATE_FORMAT ) )

        #-- END conditional to see what we got. --#

        return q_OUT

    #-- END method create_q_article_date_range() --#


    @classmethod
    def create_q_multiple_date_range( cls, date_range_IN = "", *args, **kwargs ):

        '''
        Accepts string start and end dates (YYYY-MM-DD format). in the keyword
           arguments.  Creates a Q() instance that filters dates based on start
           and end date passed in. If both are missing, does nothing.  If one or
           other passed in, filters accordingly.
        Preconditions: Dates must be strings in YYYY-MM-DD format.
        Postconditions: Returns the Q() instance - to use it, you must pass it
           to a QuerySet's filter method.  If neither start nor end dates are
           passed in, returns None.
        '''

        # return reference
        q_OUT = None

        # declare variables
        date_range = ""
        date_range_list = None
        date_range_q_list = None
        date_range_pair = None
        range_start_date = None
        range_end_date = None
        date_range_q = None
        current_query = None

        # retrieve date range string
        date_range = date_range_IN
        if ( ( date_range is None ) or ( date_range == "" ) ):

            # no date range passed in. Check in the kwargs.
            if ( cls.PARAM_DATE_RANGE in kwargs ):

                # yup.  Use it.
                date_range = kwargs[ cls.PARAM_DATE_RANGE ]

            #-- END check to see if date range in arguments --#

        #-- END check to see if date range passed in. --#

        # got a date range string?
        if ( date_range != '' ):

            # first, break up the string into a list of start and end dates.
            date_range_list = ContextTextBase.parse_multiple_date_range_string( date_range )
            date_range_q_list = []

            # loop over the date ranges, create a Q for each, and then store
            #    that Q in our Q list.
            for date_range_pair in date_range_list:

                # get start and end datetime.date instances.
                range_start_date = date_range_pair[ 0 ]
                range_end_date = date_range_pair[ 1 ]

                # make Q
                date_range_q = Q( pub_date__gte = range_start_date ) & Q( pub_date__lte = range_end_date )

                # add Q to Q list.
                date_range_q_list.append( date_range_q )

            #-- END loop over date range items. --#

            # see if there is anything in date_range_q_list.
            if ( len( date_range_q_list ) > 0 ):

                # There is something.  Convert it to one big ORed together
                #    Q and add that to the list.
                q_OUT = reduce( operator.__or__, date_range_q_list )

            #-- END check to see if we have any valid date ranges.

        #-- END processing of date range --#

        return q_OUT

    #-- END method create_q_multiple_date_range() --#


    @classmethod
    def filter_articles( cls, qs_IN = None, params_IN = None, *args, **kwargs ):

        '''
        Accepts parameters in kwargs.  Uses arguments to filter a QuerySet of
            articles, which it subsequently returns.  Currently, you can pass
            this method a section name list and date range start and end dates.
            You can also pass in an optional QuerySet instance.  If QuerySet
            passed in, this method appends filters to it.  If not, starts with
            a new QuerySet.  Specifically, accepts:
            - cls.PARAM_NEWSPAPER_ID ("newspaper_id") - ID of newspapers whose articles we want to limit to.
            - cls.PARAM_NEWSPAPER_NEWSBANK_CODE ("newspaper_newsbank_code") - newsbank code of newspaper whose articles we want.
            - cls.PARAM_NEWSPAPER_INSTANCE ("newspaper") - instance of newspaper whose articles we want.
            - cls.PARAM_NEWSPAPER_ID_IN_LIST ("newspaper_id_in_list") - list of IDs of newspapers whose articles we want included in our filtered set.
            - cls.PARAM_START_DATE ("start_date") - date string in "YYYY-MM-DD" format of date on which and after we want articles published.
            - cls.PARAM_END_DATE ("end_date") - date string in "YYYY-MM-DD" format of date up to and including which we want articles published.
            - cls.PARAM_DATE_RANGE ("date_range") - For date range fields, enter any number of paired date ranges, where dates are in the format YYYY-MM-DD, dates are separated by the string " to ", and each pair of dates is separated by two pipes ("||").  Example: 2009-12-01 to 2009-12-31||2010-02-01 to 2010-02-28
            - cls.PARAM_SECTION_NAME_IN_LIST ("section_name_list") - list of section names an article can have in our filtered article set.
            - cls.PARAM_TAGS_IN_LIST ("tags_in_list_IN") - tags articles in our set should have.
            - cls.PARAM_TAGS_NOT_IN_LIST ("tags_not_in_list_IN") - tags articles in our set should not have.
            - cls.PARAM_UNIQUE_ID_IN_LIST = ContextTextBase.PARAM_UNIQUE_ID_LIST   # list of unique identifiers of articles whose data you want included.
            - cls.PARAM_ARTICLE_ID_IN_LIST = ContextTextBase.PARAM_ARTICLE_ID_LIST   # list of ids of articles whose data you want included.
            - cls.PARAM_CUSTOM_ARTICLE_Q = ContextTextBase.PARAM_CUSTOM_ARTICLE_Q - Django django.db.models.Q instance to apply to filtered QuerySet.
            - cls.PARAM_GET_DISTINCT_RECORDS = ContextTextBase.PARAM_GET_DISTINCT_RECORDS   # For whatever model is being queried or filtered, only get one instance of a record that has a given ID.


        Preconditions: None.
        Postconditions: returns the QuerySet passed in with filters added as
            specified by arguments.  If no QuerySet passed in, creates new
            Article QuerySet, returns it with filters added.
        '''

        # return reference
        qs_OUT = None

        # declare variables
        me = "filter_articles"
        my_logger_name = "context_text.models.Article"
        my_logger = None
        is_queryset_evaluated = False

        # declare variables - input parameters
        my_params = None
        my_dict_helper = None
        newspaper_instance_IN = None
        newspaper_ID_IN = None
        newspaper_newsbank_code_IN = None
        newspaper_id_in_list_IN = None
        start_date_IN = None
        end_date_IN = None
        date_range_IN = None
        section_name_list_IN = None
        tags_in_list_IN = None
        tags_not_in_list_IN = None
        unique_id_in_list_IN = None
        article_id_in_list_IN = None
        custom_q_IN = None
        get_distinct_records_IN = False

        # declare variables - processing variables
        current_query = None
        query_list = None
        newspaper_instance = None
        paper_id_in_list = None
        q_date_range = None
        tags_in_list = None
        tags_not_in_list = None
        unique_id_in_list = None
        article_id_in_list = None
        query_item = None

        # do DISTINCT?
        distinct_work_qs = None
        article_id_list = None
        duplicate_count = -1
        current_article = None
        current_article_id = -1

        #-----------------------------------------------------------------------
        # ! ----> init
        #-----------------------------------------------------------------------

        # init - get logger
        my_logger = LoggingHelper.get_a_logger( logger_name_IN = my_logger_name )

        # init - query list
        query_list = []

        # init - store kwargs in params_IN, and in DictHelper instance.
        if ( params_IN is not None ):

            # got params passed in - use them.
            my_params = params_IN

            # and append kwargs, just in case.
            my_params.update( kwargs )

        else:

            # use kwargs
            my_params = kwargs

        #-- END check to see if params other than kwargs passed in.

        my_dict_helper = DictHelper()
        my_dict_helper.set_dictionary( my_params )

        # got a query set?
        if ( qs_IN ):

            # use the one passed in.
            qs_OUT = qs_IN

            #output_debug( "QuerySet passed in, using it.", me, "*** " )

        else:

            # No.  Make one.
            qs_OUT = cls.objects.all()

            #output_debug( "No QuerySet passed in, using fresh one.", me, "*** " )

        #-- END check to see if query set passed in --#

        #-----------------------------------------------------------------------
        # ! ----> retrieve parameters
        #-----------------------------------------------------------------------

        newspaper_instance_IN = my_dict_helper.get_value( cls.PARAM_NEWSPAPER_INSTANCE, default_IN = None )
        newspaper_ID_IN = my_dict_helper.get_value_as_int( cls.PARAM_NEWSPAPER_ID, default_IN = -1 )
        newspaper_newsbank_code_IN = my_dict_helper.get_value_as_str( cls.PARAM_NEWSPAPER_NEWSBANK_CODE, default_IN = None )

        # multiple options for paper ID list
        newspaper_id_in_list_IN = my_dict_helper.get_value_as_list( cls.PARAM_NEWSPAPER_ID_IN_LIST, default_IN = None )

        # got anything for cls.PARAM_NEWSPAPER_ID_IN_LIST?
        if ( newspaper_id_in_list_IN is None ):

            # no.  Try cls.PARAM_PUBLICATION_LIST...
            newspaper_id_in_list_IN = my_dict_helper.get_value_as_list( cls.PARAM_PUBLICATION_LIST, default_IN = None )

        #-- END check to see if cls.PARAM_NEWSPAPER_ID_IN_LIST present --#

        start_date_IN = my_dict_helper.get_value_as_str( cls.PARAM_START_DATE, default_IN = None )
        end_date_IN = my_dict_helper.get_value_as_str( cls.PARAM_END_DATE, default_IN = None )
        date_range_IN = my_dict_helper.get_value_as_str( cls.PARAM_DATE_RANGE, default_IN = None )

        # multiple options for section name list
        section_name_list_IN = my_dict_helper.get_value_as_list( cls.PARAM_SECTION_NAME_IN_LIST, default_IN = None )

        # got anything for cls.PARAM_SECTION_NAME_IN_LIST?
        if ( section_name_list_IN is None ):

            # no.  Try cls.PARAM_SECTION_LIST...
            section_name_list_IN = my_dict_helper.get_value_as_list( cls.PARAM_SECTION_LIST, default_IN = None )

        #-- END check to see if cls.PARAM_SECTION_NAME_IN_LIST present --#

        # multiple options for tag in list
        tags_in_list_IN = my_dict_helper.get_value_as_list( cls.PARAM_TAGS_IN_LIST, default_IN = None )

        # got anything for cls.PARAM_TAGS_IN_LIST?
        if ( tags_in_list_IN is None ):

            # no.  Try cls.PARAM_TAG_LIST...
            tags_in_list_IN = my_dict_helper.get_value_as_list( cls.PARAM_TAG_LIST, default_IN = None )

        #-- END check to see if cls.PARAM_TAGS_IN_LIST present --#

        tags_not_in_list_IN = my_dict_helper.get_value_as_list( cls.PARAM_TAGS_NOT_IN_LIST, default_IN = None )
        unique_id_in_list_IN = my_dict_helper.get_value_as_list( cls.PARAM_UNIQUE_ID_IN_LIST, default_IN = None )
        article_id_in_list_IN = my_dict_helper.get_value_as_list( cls.PARAM_ARTICLE_ID_IN_LIST, default_IN = None )
        custom_q_IN = my_dict_helper.get_value( cls.PARAM_CUSTOM_ARTICLE_Q, default_IN = None )
        get_distinct_records_IN = my_dict_helper.get_value_as_boolean( cls.PARAM_GET_DISTINCT_RECORDS, default_IN = True )

        # got anything?
        if get_distinct_records_IN is not None:

            do_distinct = get_distinct_records_IN

        #-- END check to see if flag passed in. --#

        #-----------------
        # ! ----> newspaper
        #-----------------

        newspaper_instance = None

        my_logger.debug( "In " + me + "(): newspaper_instance_IN = " + str( newspaper_instance_IN ) )

        # selected newspaper instance passed in?
        if ( newspaper_instance_IN is not None ):

            # yup.  Use it.
            newspaper_instance = newspaper_instance_IN

        #-- END check to see if newspaper instance in arguments --#

        my_logger.debug( "In " + me + "(): newspaper_ID_IN = " + str( newspaper_ID_IN ) )

        # selected newspaper ID passed in?
        if ( ( newspaper_instance is None )
            and ( newspaper_ID_IN is not None )
            and ( int( newspaper_ID_IN ) > 0 ) ):

            # Make sure it isn't empty.
            if ( ( newspaper_ID_IN is not None )
                and ( newspaper_ID_IN != "" )
                and ( isinstance( newspaper_ID_IN, int ) == True )
                and ( int( newspaper_ID_IN ) > 0 ) ):

                # not empty - look up newspaper by ID
                newspaper_instance = Newspaper.objects.get( pk = newspaper_ID_IN )

            #-- END check to see if newspaper ID populated. --#

        #-- END check to see if newspaper instance in arguments --#

        my_logger.debug( "In " + me + "(): newspaper_newsbank_code_IN = " + str( newspaper_newsbank_code_IN ) )

        # selected newspaper code passed in?
        if ( ( newspaper_instance is None ) and ( newspaper_newsbank_code_IN is not None ) ):

            # Make sure it isn't empty.
            if ( ( newspaper_newsbank_code_IN is not None )
                and ( newspaper_newsbank_code_IN != "" ) ):

                # not empty - look up newspaper by code.
                newspaper_instance = Newspaper.objects.get( newsbank_code = newspaper_newsbank_code_IN )

            #-- END check to see if newspaper code was empty. --#

        #-- END check to see if newspaper instance in arguments --#

        # got a newspaper instance?
        if ( newspaper_instance is not None ):

            # Yes.  Filter.
            current_query = Q( newspaper = newspaper_instance )
            query_list.append( current_query )

        #-- END check to see if newspaper instance found.

        my_logger.debug( "In " + me + "(): newspaper_id_in_list_IN = " + str( newspaper_id_in_list_IN ) )

        # got a newspaper ID IN list?
        if ( newspaper_id_in_list_IN is not None ):

            # get list
            paper_id_in_list = ListHelper.get_value_as_list( newspaper_id_in_list_IN )

            # filter?
            if ( ( paper_id_in_list is not None ) and ( len( paper_id_in_list ) > 0 ) ):

                # something in list - filter.
                current_query = Q( newspaper__id__in = paper_id_in_list )
                query_list.append( current_query )

            #-- END check to see if anything in list. --#

        #-- END check to see if newspaper ID IN list is in arguments --#



        #-------------------------------
        # ! ----> start_date and end_date
        #-------------------------------

        my_logger.debug( "In " + me + "(): start_date_IN = " + str( start_date_IN ) + "; end_date_IN = " + str( end_date_IN ) )

        # try to get Q() for start and end dates.
        q_date_range = cls.create_q_article_date_range( start_date_IN, end_date_IN, *args, **kwargs )

        # got a Q()?
        if ( q_date_range is not None ):

            # Yes.  Add it to query list.
            current_query = q_date_range
            query_list.append( current_query )

        #-- END check to see if date range present.


        #-------------------------------
        # ! ----> date_range
        #-------------------------------

        my_logger.debug( "In " + me + "(): date_range_IN = " + str( date_range_IN ) )

        # got a date_range value?
        if ( date_range_IN is not None ):

            # try to get Q() for start and end dates.
            q_date_range = cls.create_q_multiple_date_range( date_range_IN, *args, **kwargs )

            # got a Q()?
            if ( q_date_range is not None ):

                # Yes.  Add it to query set.
                current_query = q_date_range
                query_list.append( current_query )

            #-- END check to see if anything returned. --#

        #-- END check to see if date range present.

        #----------------
        # ! ----> sections
        #----------------

        my_logger.debug( "In " + me + "(): section_name_list_IN = " + str( section_name_list_IN ) )

        # try to update QuerySet for selected sections.
        if ( section_name_list_IN is not None ):

            # got a list?
            if ( ( section_name_list_IN is not None )
                and ( isinstance( section_name_list_IN, list ) == True )
                and ( len( section_name_list_IN ) > 0 ) ):

                # add filter for name being in the list
                current_query = Q( section__in = section_name_list_IN )
                query_list.append( current_query )

            #-- END check to see if list was populated. --#

        #-- END check to see if start date in arguments --#

        #--------------------
        # ! ----> tags IN list
        #--------------------

        my_logger.debug( "In " + me + "(): tags_in_list_IN = " + str( tags_in_list_IN ) )

        # Update QuerySet to only include articles with tags in list?
        if ( tags_in_list_IN is not None ):

            # get the value as a list, whether it is a delimited string or list.
            tags_in_list = ListHelper.get_value_as_list( tags_in_list_IN )

            # filter?
            if ( ( tags_in_list is not None ) and ( len( tags_in_list ) > 0 ) ):

                # something in list - filter.
                current_query = Q( tags__name__in = tags_in_list )
                query_list.append( current_query )

                # And, need to do DISTINCT on id.
                do_distinct = True

            #-- END check to see if anything in list. --#

        #-- END check to see if tags IN list is in arguments --#

        #------------------------
        # ! ----> tags NOT IN list
        #------------------------

        my_logger.debug( "In " + me + "(): tags_not_in_list_IN = " + str( tags_not_in_list_IN ) )

        # Update QuerySet to exclude articles with tags in list?
        if ( tags_not_in_list_IN is not None ):

            # get the value as a list, whether it is a delimited string or list.
            tags_not_in_list = ListHelper.get_value_as_list( tags_not_in_list_IN )

            # filter?
            if ( ( tags_not_in_list is not None ) and ( len( tags_not_in_list ) > 0 ) ):

                # something in list - filter.
                current_query = ~Q( tags__name__in = tags_not_in_list )
                query_list.append( current_query )

            #-- END check to see if anything in list. --#

        #-- END check to see if tags IN list is in arguments --#

        #-------------------------
        # ! ----> unique ID IN list
        #-------------------------

        my_logger.debug( "In " + me + "(): unique_id_in_list_IN = " + str( unique_id_in_list_IN ) )

        # Update QuerySet to only include articles with tags in list?
        if ( unique_id_in_list_IN is not None ):

            # get the value as a list, whether it is a delimited string or list.
            unique_id_in_list = ListHelper.get_value_as_list( unique_id_in_list_IN )

            # filter?
            if ( ( unique_id_in_list is not None ) and ( len( unique_id_in_list ) > 0 ) ):

                # set up query instance to look for articles with
                #    unique_identifier in the list of values passed in.  Not
                #    quoting, since django should do that.
                current_query = Q( unique_identifier__in = unique_id_in_list )

                # add it to list of queries
                query_list.append( current_query )

            #-- END check to see if anything in list. --#

        #-- END check to see if tags IN list is in arguments --#

        #--------------------------
        # ! ----> article ID IN list
        #--------------------------

        my_logger.debug( "In " + me + "(): article_id_in_list_IN = " + str( article_id_in_list_IN ) )

        # Update QuerySet to only include articles with tags in list?
        if ( article_id_in_list_IN is not None ):

            # get the value as a list, whether it is a delimited string or list.
            article_id_in_list = ListHelper.get_value_as_list( article_id_in_list_IN )

            # filter?
            if ( ( article_id_in_list is not None ) and ( len( article_id_in_list ) > 0 ) ):

                # set up query instance to look for articles with
                #    ID in the list of values passed in.  Not
                #    quoting, since django should do that.
                current_query = Q( id__in = article_id_in_list )

                # add it to list of queries
                query_list.append( current_query )

            #-- END check to see if anything in list. --#

        #-- END check to see if tags IN list is in arguments --#

        #-------------------------------
        # ! ----> custom-built Q() object
        #-------------------------------

        # try to update QuerySet for selected sections.
        if ( custom_q_IN is not None ):

            # got something in the parameter?
            if ( ( custom_q_IN is not None )
                and ( isinstance( custom_q_IN, Q ) == True ) ):

                # yes.  Add to q queue.
                current_query = custom_q_IN
                query_list.append( current_query )

            #-- END check to see if custom Q() present. --#

        #-- END check to see if Custom Q argument present --#

        #-----------------------------------------------------------------------
        # ! ----> filter with Q() list
        #-----------------------------------------------------------------------

        my_logger.debug( "In {}(): article_id_in_list_IN = {}".format( me, article_id_in_list_IN ) )

        # evaluated?
        is_queryset_evaluated = QuerySetHelper.is_queryset_evaluated( qs_OUT )
        my_logger.debug( "----> In " + me + "(): before applying list of Q() objects, is QS evaluated?: {}".format( is_queryset_evaluated ) )

        # now, add them all to the QuerySet - try a loop
        for query_item in query_list:

            # append each filter to query set.
            qs_OUT = qs_OUT.filter( query_item )

        #-- END loop over query set items --#

        # evaluated?
        is_queryset_evaluated = QuerySetHelper.is_queryset_evaluated( qs_OUT )
        my_logger.debug( "----> In " + me + "(): after applying list of Q() objects, is QS evaluated?: {}".format( is_queryset_evaluated ) )

        #-----------------------------------------------------------------------
        # ! ----> do DISTINCT?
        #-----------------------------------------------------------------------

        # do DISTINCT on ID?
        if ( do_distinct == True ):

            # do DISTINCT
            # qs_OUT.distinct() - doesn't work.

            distinct_work_qs = qs_OUT.order_by( "id" )

            # init ID set.
            article_id_list = []
            duplicate_count = 0

            # loop over results:
            for current_article in distinct_work_qs:

                # get ID
                current_article_id = current_article.id

                # already in list?
                if ( current_article_id not in article_id_list ):

                    # add it to list.
                    article_id_list.append( current_article_id )

                else:

                    # alread in the list.
                    duplicate_count += 1

                #-- END check to see if ID already in list. --#

            #-- END loop over articles --#

            my_logger.debug( "In " + me + "(): do_distinct = " + str( do_distinct ) + "; duplicate count = " + str( duplicate_count ) + "; Article IDs = " + str( article_id_list ) )

            # anything in list?
            if ( len( article_id_list ) > 0 ):

                # yes - were there any duplicates?
                if ( duplicate_count > 0 ):

                    # yes.  Make a query that just limits to current matches.
                    qs_OUT = Article.objects.filter( id__in = article_id_list )

                    my_logger.debug( "In " + me + "(): filtered out duplicate Articles." )

                #-- END check to see if any duplicates. --#

            #-- END check to see if anything in ID list --#

        #-- END check to see if we do DISTINCT --#

        # evaluated?
        is_queryset_evaluated = QuerySetHelper.is_queryset_evaluated( qs_OUT )
        my_logger.debug( "----> In " + me + "(): after potential DISTINCT check, is QS evaluated?: {}".format( is_queryset_evaluated ) )

        return qs_OUT

    #-- END method filter_articles() --#


    #---------------------------------------------------------------------------
    # ! ==> overridden built-in methods
    #---------------------------------------------------------------------------


    def __init__( self, *args, **kwargs ):

        # call parent __init()__ first.
        super( Article, self ).__init__( *args, **kwargs )

        # then, initialize variable.
        self.my_entity_name_prefix = self.ENTITY_NAME_PREFIX
        self.my_entity_type_slug = self.ENTITY_TYPE_SLUG_ARTICLE
        self.my_base_entity_id_type = self.ENTITY_ID_TYPE_ARTICLE_SOURCENET_ID

    #-- END method __init__() --#


    def __str__( self ):

        # start with stuff we should always have.
        string_OUT = str( self.id ) + " - " + self.pub_date.strftime( "%b %d, %Y" )

        # Got a section?
        if ( self.section ):

            # add section
            string_OUT += ", " + self.section

        #-- END check to see if section present.

        # Got a page?
        if ( self.page ):

            # add page.
            string_OUT += " ( " + str( self.page ) + " )"

        #-- END check to see if page. --#

        # Unique Identifier?
        if ( self.unique_identifier ):

            # Add UID
            string_OUT += ", UID: " + self.unique_identifier

        #-- END check for unique identifier

        # headline
        string_OUT += " - " + self.headline

        # got a related newspaper?
        if ( self.newspaper ):

            # Yes.  Append it.
            string_OUT += " ( " + self.newspaper.name + " )"

        elif ( self.source_string ):

            # Well, we have a source string.
            string_OUT += " ( " + self.source_string + " )"

        #-- END check to see if newspaper present. --#

        return string_OUT

    #-- END method __str__() --#


    #----------------------------------------------------------------------------
    # ! ==> instance methods
    #----------------------------------------------------------------------------


    def create_notes( self, text_IN = "", content_type_IN = "text", do_save_IN = True, *args, **kwargs ):

        '''
        Accepts a piece of text.  Adds it as a related Article_Notes instance.
        Preconditions: Probably should do this after you've saved the article,
           so there is an ID in it, so this child class will know what article
           it is related to.
        Postconditions: Article_Notes instance is returned, saved if save flag
           is true.
        '''

        # return reference
        instance_OUT = None

        # declare variables
        me = "create_notes"

        # Nothing.  Make new one.
        instance_OUT = Article_Notes()
        instance_OUT.article = self
        instance_OUT.content_type = content_type_IN

        # set the text in the instance.
        instance_OUT.set_content( text_IN )

        # save?
        if ( do_save_IN == True ):

            # yes.
            instance_OUT.save()

        #-- END check to see if we save. --#

        return instance_OUT

    #-- END method create_notes() --#


    def get_article_data_for_coder( self, coder_IN = None, coder_type_IN = "", *args, **kwargs ):

        '''
        Checks to see if there is a nested article_data instance for the coder
           whose User instance is passed in.  If so, returns it.  If not, creates
           one, places minimum required for save inside, saves, then returns it.
        preconditions: Assumes that you are looking for a single coding record
           for a given user, and that the user won't have multiple.  If the user
           might have more than one coding record, just invoke:

           self.article_data_set.filter( coder = <user_instance> )

           to get a QuerySet, and see if it returns anything.  If not, call this
           method to create a new one for that user.
        postconditions: If user passed in doesn't have a article_data record,
           this will create one for him or her, save it, and then return it.
        '''

        # return reference
        instance_OUT = None

        # declare variables
        me = "get_article_data_for_coder"
        article_data_qs = None
        article_data_count = -1

        # Do we have a coder passed in?
        if ( coder_IN ):

            # first, see if we have an associated article_data instance already.
            article_data_qs = self.article_data_set.filter( coder = coder_IN )

            # got a coder type?
            if ( ( coder_type_IN is not None ) and ( coder_type_IN != "" ) ):

                # yes.  filter on it, as well.
                article_data_qs = article_data_qs.filter( coder_type = coder_type_IN )

            #-- END check to see if coder type present. --#

            # what we got back?
            article_data_count = article_data_qs.count()

            # if 0, create new, populate, and save.
            if ( article_data_count == 0 ):

                # create instance
                instance_OUT = Article_Data()

                # populate
                instance_OUT.article = self
                instance_OUT.coder = coder_IN

                # got a coder type?
                if ( ( coder_type_IN is not None ) and ( coder_type_IN != "" ) ):

                    # yes.  save it.
                    instance_OUT.coder_type = coder_type_IN

                #-- END check to see if coder type present. --#

                # save article_data instance.
                instance_OUT.save()

                output_debug( "Created article_data for " + str( coder_IN ) + ".", me )

            elif ( article_data_count == 1 ):

                # one found.  Get and return it.
                instance_OUT = article_data_qs.get()

                output_debug( "Found existing article_data for " + str( coder_IN ) + ".", me )

            elif ( article_data_count > 1 ):

                # found more than one.  Log error, suggest just pulling QuerySet.
                output_debug( "Found multiple article_data records for " + str( coder_IN ) + ".  Returning None.  If this is expected, try self.article_data_set.filter( coder = <user_instance> ) instead.", me )

            #-- END processing based on counts --#

        else:

            output_debug( "No coder passed in, returning None.", me )

        #-- END check to see if we have a coder --#

        return instance_OUT

    #-- END method get_article_data_for_coder() --#


    def rebuild_author_string( self, *args, **kwargs ):

        '''
        author_string and author_varchar should just follow pattern:

            <author_name(s)> / <author_affiliation>

        If no author_name, just use author_affiliation.

        Stores the rebuilt author string value in the instance, but does not
            save, so to persist the new value to the database, the instance will
            need to be saved.

        Returns the rebuilt author string.
        '''

        # return reference
        value_OUT = ""

        # declare variables
        me = "rebuild_author_string"
        my_author_name = ""
        my_author_affiliation = ""

        # get author name and affiliation.
        my_author_name = self.author_name
        my_author_affiliation = self.author_affiliation

        # got an author name?
        if ( ( my_author_name is not None ) and ( my_author_name != "" ) ):

            # we have an author name.  start with it.
            value_OUT = my_author_name

            # got an affiliation?
            if ( ( my_author_affiliation is not None ) and ( my_author_affiliation != "" ) ):

                # we do.  add it on.
                value_OUT += " " + self.AUTHOR_STRING_DIVIDER + " " + my_author_affiliation

            #-- END check to see if also have affiliation --#

        else:

            # no author name.  Just have affiliation?
            if ( ( my_author_affiliation is not None ) and ( my_author_affiliation != "" ) ):

                # just affiliation.  Use that.
                value_OUT = my_author_affiliation

            #-- END check to see if just affiliation --#

        #-- END check to see if author_name. --#

        # place the contents of value_OUT in author_string and author_varchar.
        self.author_string = value_OUT
        self.author_varchar = value_OUT

        return value_OUT

    #-- END method rebuild_author_string() --#


    def set_author_affiliation( self, value_IN, do_rebuild_IN = True, *args, **kwargs ):

        '''
        Accepts a value to be placed in author_affiliation.  Places that value
            in the "author_name" instance variable, then if do_rebuild_IN ==
            True, calls rebuild_author_string().
        Preconditions: None at this time.
        Postconditions: Article instance is updated, but not saved.  Current
            author_affiliation is returned.
        '''

        # return reference
        value_OUT = None

        # declare variables
        me = "set_author_affiliation"

        # set author_affiliation
        self.author_affiliation = value_IN

        # do we rebuild?
        if ( do_rebuild_IN == True ):

            # yes.  Do.
            self.rebuild_author_string()

        #-- END check to see if we rebuild. --#

        return value_OUT

    #-- END method set_author_affiliation() --#


    def set_author_name( self, value_IN, do_rebuild_IN = True, *args, **kwargs ):

        '''
        Accepts a value to be placed in author_name.  Places that value in
            the "author_name" instance variable, then if do_rebuild_IN == True,
            calls rebuild_author_string().
        Preconditions: None at this time.
        Postconditions: Article instance is updated, but not saved.  Current
            author_name is returned.
        '''

        # return reference
        value_OUT = None

        # declare variables
        me = "set_author_name"

        # set author_name
        self.author_name = value_IN

        # do we rebuild?
        if ( do_rebuild_IN == True ):

            # yes.  Do.
            self.rebuild_author_string()

        #-- END check to see if we rebuild. --#

        return value_OUT

    #-- END method set_author_name() --#


    def set_notes( self, text_IN = "", do_save_IN = True, do_append_to_content_IN = True, *args, **kwargs ):

        '''
        Accepts a piece of text.  Adds it as a related Article_Notes instance.
           If there is already an Article_Notes instance, we can either replace
           that instance's content with the text passed in, or append text to
           note.  Defaults to appending.  If no existing note, we make one.
           If you have multiple Article_Notes, this won't work.  Just create
           another Article_Note.
        Preconditions: Probably should do this after you've saved the article,
           so there is an ID in it, so this child class will know what article
           it is related to.
        Postconditions: Article_Notes instance is returned, saved if save flag
           is true.
        '''

        # return reference
        instance_OUT = None

        # declare variables
        me = "set_notes"
        current_qs = None
        current_count = -1
        updated_content = ""

        # get current text QuerySet
        current_qs = self.article_notes_set

        # how many do we have?
        current_count = current_qs.count()
        if ( current_count == 1 ):

            # One.  Get it.
            instance_OUT = current_qs.get()

        elif ( current_count == 0 ):

            # Nothing.  Make new one.
            instance_OUT = Article_Notes()
            instance_OUT.article = self
            instance_OUT.content_type = "text"

        else:

            # Either error or more than one (so error).
            output_debug( "Found more than one related Article_Notes.  Doing nothing.", me )

        #-- END check to see if have one or not. --#

        if ( instance_OUT ):

            # append?
            if ( do_append_to_content_IN == True ):

                # get current content
                updated_content = instance_OUT.get_content()

                # append the new text, separated by a newline.
                updated_content += "\n" + text_IN

            else:

                # just use what is there.
                updated_content = text_IN

            #-- END check to see if we append --#

            # store the updated content
            instance_OUT.set_content( updated_content )

            # save?
            if ( do_save_IN == True ):

                # yes.
                instance_OUT.save()

            #-- END check to see if we save. --#

        #-- END check to see if instance. --#

        return instance_OUT

    #-- END method set_notes() --#


    def set_raw_html( self, text_IN = "", do_save_IN = True, *args, **kwargs ):

        '''
        Accepts a piece of text.  Adds it as a related Article_RawData instance.
           If there is already an Article_RawData instance, we just replace that
           instance's content with the text passed in.  If not, we make one.
        Preconditions: Probably should do this after you've saved the article,
           so there is an ID in it, so this child class will know what article
           it is related to.
        Postconditions: Article_RawData instance is returned, saved if save flag
           is true.
        '''

        # return reference
        instance_OUT = None

        # declare variables
        me = "set_raw_html"
        current_qs = None
        current_count = -1
        current_content = None

        # get current text QuerySet
        current_qs = self.article_rawdata_set

        # how many do we have?
        current_count = current_qs.count()
        if ( current_count == 1 ):

            # One.  Get it.
            instance_OUT = current_qs.get()

        elif ( current_count == 0 ):

            # Nothing.  Make new one.
            instance_OUT = Article_RawData()
            instance_OUT.article = self
            instance_OUT.content_type = "html"

        else:

            # Either error or more than one (so error).
            output_debug( "Found more than one related Article_RawData.  Doing nothing.", me )

        #-- END check to see if have one or not. --#

        if ( instance_OUT ):

            # set the text in the instance.
            instance_OUT.set_content( text_IN )

            # save?
            if ( do_save_IN == True ):

                # yes.
                instance_OUT.save()

            #-- END check to see if we save. --#

        #-- END check to see if instance. --#

        return instance_OUT

    #-- END method set_raw_html() --#


    def set_text( self, text_IN = "", do_save_IN = True, clean_text_IN = True, *args, **kwargs ):

        '''
        Accepts a piece of text.  Adds it as a related Article_Text instance.
           If there is already an Article_Text instance, we just replace that
           instance's content with the text passed in.  If not, we make one.
        Preconditions: Probably should do this after you've saved the article,
           so there is an ID in it, so this child class will know what article
           it is related to.
        Postconditions: Article_Text instance is returned, saved if save flag
           is true.
        '''

        # return reference
        instance_OUT = None

        # declare variables
        me = "set_text"
        current_qs = None
        current_count = -1
        current_content = None
        cleaned_text = ""

        # get current text QuerySet
        current_qs = self.article_text_set

        # how many do we have?
        current_count = current_qs.count()
        if ( current_count == 1 ):

            # One.  Get it.
            instance_OUT = current_qs.get()

        elif ( current_count == 0 ):

            # Nothing.  Make new one.
            instance_OUT = Article_Text()
            instance_OUT.article = self
            instance_OUT.content_type = "canonical"

        else:

            # Either error or more than one (so error).
            output_debug( "Found more than one related text.  Doing nothing.", me )

        #-- END check to see if have one or not. --#

        if ( instance_OUT ):

            # set the text in the instance.
            instance_OUT.set_text( text_IN, clean_text_IN )

            # save?
            if ( do_save_IN == True ):

                # yes.
                instance_OUT.save()

            #-- END check to see if we save. --#

        #-- END check to see if instance. --#

        return instance_OUT

    #-- END method set_text() --#


    def update_entity( self ):

        '''
        Based on current instance, creates and populates an entity for the
            model based on the contents of the instance, returns the entity
            instance.

        If you just want to get a fully-populated ID loaded into this instance,
            call this method, not load_entity().  load_entity() will create a
            new instance if one doesn't exist, but it does not fill in all of
            the details - because this method does!
        '''

        # return reference
        entity_OUT = None

        # declare variables - create new.
        me = "update_entity"
        entity_instance = None
        entity_type = None
        trait_name = None
        trait_definition = None
        trait_instance = None
        instance_has_entity = None
        trait_value = None
        trait_type = None
        identifier_type_name = None
        identifier_type = None
        identifier_instance = None
        identifier_uuid = None
        identifier_source = None

        # load entity for article.
        entity_instance = self.load_entity( do_create_if_none_IN = True )

        # got an entity?
        if ( entity_instance is not None ):

            # get entity type (won't duplicate if already added).
            entity_type = entity_instance.add_entity_type( self.my_entity_type_slug )

            # make sure we return it at this point, since it has been
            #    created and stored in database.
            entity_OUT = entity_instance

            #------------------------------------------------------------------#
            # ! ----> set entity traits

            # ! --------> publication date
            trait_name = self.CONTEXT_TRAIT_NAME_PUB_DATE
            trait_value = self.pub_date
            trait_value = trait_value.strftime( "%Y-%m-%d" )

            # initialize trait from predefined entity type trait "pub_date".
            trait_definition = entity_type.get_trait_spec( trait_name )

            # add trait
            entity_instance.set_entity_trait( trait_name,
                                              trait_value,
                                              entity_type_trait_IN = trait_definition )

            # ! --------> newspaper ID
            trait_name = self.CONTEXT_TRAIT_NAME_NEWSPAPER_ID

            # do we have a newspaper?
            if ( self.newspaper is not None ):

                # there is a related instance.  It's ID is value.
                trait_instance = self.newspaper
                trait_value = trait_instance.id

                # and check if instance has an entity.  If not, create one.
                instance_has_entity = trait_instance.has_entity()
                if ( instance_has_entity == False ):

                    # create one.
                    trait_instance.update_entity()

                #-- END check to see if instance has entity. --#

            else:

                # No newspaper, set trait to None.
                trait_value = None

            #-- END check to see if Newspaper. --#

            # store
            entity_instance.set_entity_trait( trait_name,
                                              trait_value,
                                              slug_IN = slugify( trait_name ) )

            # ! TODO - figure out other traits to add.

            #------------------------------------------------------------------#
            # ! ----> add identifiers

            # ! --------> for django ID in this system.
            identifier_type = Entity_Identifier_Type.get_type_for_name( self.ENTITY_ID_TYPE_ARTICLE_SOURCENET_ID )
            identifier_uuid = self.id
            entity_instance.set_identifier( identifier_uuid,
                                            name_IN = identifier_type.name,
                                            entity_identifier_type_IN = identifier_type )

            # ! --------> for unique identifier.
            identifier_type_name = self.unique_identifier_type
            identifier_type = Entity_Identifier_Type.get_type_for_name( identifier_type_name )
            identifier_uuid = self.unique_identifier
            entity_instance.set_identifier( identifier_uuid,
                                            name_IN = identifier_type.name,
                                            entity_identifier_type_IN = identifier_type )

            # ! --------> generic archive id
            # is there an archive_id and archive_source?
            identifier_type = None
            identifier_uuid = self.archive_id
            identifier_source = self.archive_source
            if (
                (
                    ( identifier_uuid is not None )
                    and ( identifier_uuid != "" )
                )
                and
                (
                    ( identifier_source is not None )
                    and ( identifier_source != "" )
                )
            ):

                # log archive identifier information
                log_message = "NOTE - Archive identifier: {}; source: {}".format( identifier_uuid, identifier_source )
                output_log_message( log_message, log_level_code_IN = logging.DEBUG, do_print_IN = DEBUG )

                # archive ID and source present.  Create identifier.
                identifier_type = Entity_Identifier_Type.get_type_for_name( self.ENTITY_ID_TYPE_ARTICLE_ARCHIVE_IDENTIFIER )
                entity_instance.set_identifier( identifier_uuid,
                                                name_IN = identifier_type.name,
                                                source_IN = identifier_source,
                                                entity_identifier_type_IN = identifier_type )

            else:

                # No archive identifier.
                log_message = "NOTE - No archive identifier or source."
                output_log_message( log_message, log_level_code_IN = logging.DEBUG, do_print_IN = DEBUG )

            #-- END check to see if generic archive ID. --#

            # ----> generic permalink
            # permalink set?
            identifier_uuid = self.permalink
            if ( ( identifier_uuid is not None ) and ( identifier_uuid != "" ) ):

                # permalink present.  Create identifier.
                identifier_type = Entity_Identifier_Type.get_type_for_name( self.ENTITY_ID_TYPE_PERMALINK )
                entity_instance.set_identifier( identifier_uuid,
                                                name_IN = identifier_type.name,
                                                entity_identifier_type_IN = identifier_type )

            #-- END check to see if permalink present. --#

        else:

            # no entity, can't add/update traits or identifiers
            print( "no entity, can't add/update traits or identifiers" )
            entity_OUT = None

        #-- END check to make sure we have an entity --#

        return entity_OUT

    #-- END method update_entity() --#


#= End Article Model ============================================================


# Article_Content model
class Article_Content( Abstract_Related_JSON_Content ):

    #----------------------------------------------------------------------
    # model fields and meta
    #----------------------------------------------------------------------

    # allow more than one related piece of "Article_Content" per article.
    article = models.ForeignKey( Article, on_delete = models.CASCADE )

    # meta class so we know this is an abstract class.
    class Meta:
        abstract = True
        ordering = [ 'article', 'last_modified', 'create_date' ]

    #----------------------------------------------------------------------------
    # instance methods
    #----------------------------------------------------------------------------


    def __init__( self, *args, **kwargs ):

        # call parent __init()__ first.
        super( Article_Content, self ).__init__( *args, **kwargs )

    #-- END method __init__() --#


    def to_string( self ):

        # return reference
        string_OUT = ""

        if ( self.id ):

            string_OUT += str( self.id ) + " - "

        #-- END check to see if ID --#

        if ( self.content_description ):

            string_OUT += self.content_description

        #-- END check to see if content_description --#

        if ( self.content_type ):

            string_OUT += " of type \"" + self.content_type + "\""

        #-- END check to see if there is a type --#

        string_OUT += " for article: " + str( self.article )

        return string_OUT

    #-- END method to_string() --#


    def __str__( self ):

        # return reference
        string_OUT = ""

        string_OUT = self.to_string()

        return string_OUT

    #-- END method __str__() --#


#-- END abstract Article_Content model --#


# Unique_Article_Content model
class Unique_Article_Content( Abstract_Related_Content ):

    #----------------------------------------------------------------------
    # model fields and meta
    #----------------------------------------------------------------------

    # only allow one related piece of "Unique_Article_Content" per article.
    article = models.ForeignKey( Article, on_delete = models.CASCADE, unique = True )

    # meta class so we know this is an abstract class.
    class Meta:
        abstract = True
        ordering = [ 'article', 'last_modified', 'create_date' ]

    #----------------------------------------------------------------------------
    # instance methods
    #----------------------------------------------------------------------------


    def __init__( self, *args, **kwargs ):

        # call parent __init()__ first.
        super( Unique_Article_Content, self ).__init__( *args, **kwargs )

    #-- END method __init__() --#


    def to_string( self ):

        # return reference
        string_OUT = ""

        if ( self.id ):

            string_OUT += str( self.id ) + " - "

        #-- END check to see if ID --#

        if ( self.content_description ):

            string_OUT += self.content_description

        #-- END check to see if content_description --#

        if ( self.content_type ):

            string_OUT += " of type \"" + self.content_type + "\""

        #-- END check to see if there is a type --#

        string_OUT += " for article: " + str( self.article )

        return string_OUT

    #-- END method to_string() --#


    def __str__( self ):

        # return reference
        string_OUT = ""

        string_OUT = self.to_string()

        return string_OUT

    #-- END method __str__() --#


#-- END abstract Unique_Article_Content model --#


# Article_Notes model
class Article_Notes( Article_Content ):

    def __init__( self, *args, **kwargs ):

        # call parent __init()__ first.
        super( Article_Notes, self ).__init__( *args, **kwargs )

    #-- END method __init__() --#


    def __str__( self ):

        # return reference
        string_OUT = ""

        # set content description
        self.content_description = "notes"

        # call string method.
        string_OUT = super( Article_Notes, self ).to_string()

        return string_OUT

    #-- END method __str__() --#

#-- END Article_Notes model --#


# Article_RawData model
class Article_RawData( Unique_Article_Content ):

    def __init__( self, *args, **kwargs ):

        # call parent __init()__ first.
        super( Article_RawData, self ).__init__( *args, **kwargs )

    #-- END method __init__() --#


    def __str__( self ):

        # return reference
        string_OUT = ""

        # set content description
        self.content_description = "raw data"

        # call string method.
        string_OUT = super( Article_RawData, self ).to_string()

        return string_OUT

    #-- END method __str__() --#

#-- END Article_RawData model --#


# Article_Text model
class Article_Text( Unique_Article_Content ):

    #----------------------------------------------------------------------------
    # Constants-ish
    #----------------------------------------------------------------------------

    STATUS_SUCCESS = "Success!"

    # Body Text Cleanup
    #==================

    BODY_TEXT_ALLOWED_TAGS = [ 'p', ]
    BODY_TEXT_ALLOWED_ATTRS = {
        'p' : [ 'id', ],
    }

    # Names for dictionary of results of find_in_text() (FIT) method.
    FIT_CANONICAL_INDEX_LIST = "canonical_index_list"
    FIT_TEXT_INDEX_LIST = "index_list"
    FIT_FIRST_WORD_NUMBER_LIST = "first_word_number_list"
    FIT_LAST_WORD_NUMBER_LIST = "last_word_number_list"
    FIT_PARAGRAPH_NUMBER_LIST = "paragraph_number_list"


    #----------------------------------------------------------------------
    # ! ==> model fields
    #----------------------------------------------------------------------


    do_clean_on_save = models.BooleanField( default = True )


    #----------------------------------------------------------------------------
    # class methods
    #----------------------------------------------------------------------------


    @classmethod
    def clean_body_text( cls, body_text_IN = "", *args, **kwargs ):

        '''
        Accepts body text string.  Removes extra white space, then removes HTML
           other than <p> tags.  Returns cleaned string.
        '''

        # return reference
        body_text_OUT = ""

        # declare variables
        allowed_tags = None
        allowed_attrs = None

        # start with text passed in.
        body_text_OUT = body_text_IN

        # use bleach to strip out HTML.
        allowed_tags = cls.BODY_TEXT_ALLOWED_TAGS
        allowed_attrs = cls.BODY_TEXT_ALLOWED_ATTRS
        body_text_OUT = HTMLHelper.remove_html( body_text_OUT, allowed_tags, allowed_attrs )

        # compact white space
        body_text_OUT = StringHelper.replace_white_space( body_text_OUT, ' ' )

        return body_text_OUT

    #-- END class method clean_body_text() --#


    @classmethod
    def convert_string_to_word_list( cls,
                                     string_IN,
                                     remove_html_IN = False,
                                     remove_punctuation_IN = False,
                                     clean_white_space_IN = True,
                                     *args,
                                     **kwargs ):

        '''
        Accepts a string, for now, just calls ".split()" on it to split it on
           white space.  Eventually, might make it fancier (deal better with
           punctuation, for example, at least optionally).
        Returns list of words if no errors, None if error.
        '''

        # return reference
        word_list_OUT = []

        # declare variables
        work_string = ""

        # got a string?
        if ( ( string_IN is not None ) and ( string_IN != "" ) ):

            work_string = string_IN

            # remove HTML?
            if ( remove_html_IN == True ):

                # get the content with no HTML.
                work_string = HTMLHelper.remove_html( work_string, bs_parser_IN = BS_PARSER )

            #-- END check to see if remove HTML --#

            # clean out punctuation, as well?
            if ( remove_punctuation_IN == True ):

                # clean out punctuation
                work_string = StringHelper.remove_punctuation( work_string )

            #-- END check to see if we remove punctuation. --#

            # clean up white space?
            if ( clean_white_space_IN == True ):

                work_string = StringHelper.replace_white_space( work_string )

            #-- END check to see if we clean extra white space --#

            # split the string.
            word_list_OUT = work_string.split()

        else:

            # no string.  Return None.
            word_list_OUT = None

        #-- END check to see if string. --#

        return word_list_OUT

    #-- END class method convert_string_to_word_list() --#


    @classmethod
    def process_paragraph_contents( cls, paragraph_element_list_IN, bs_helper_IN = None, *args, **kwargs ):

        '''
        Accepts a list of the contents of a paragraph.  Loops over them and
           pulls them all together into one string.  Returns the string.

        Params:
        - paragraph_element_list_IN - list of BeautifulSoup4 elements that from an article paragraph.
        '''

        # return reference
        string_OUT = ""

        # declare variables
        paragraph_text_list = []
        current_paragraph_text = ""
        my_bs_helper = ""

        # initialize BeautifulSoup helper
        if ( bs_helper_IN != None ):

            # BSHelper passed in.
            my_bs_helper = bs_helper_IN

        else:

            # no helper passed in.  Create one.
            my_bs_helper = BeautifulSoupHelper()

        #-- END BeautifulSoupHelper init. --#

        # got anything in list?
        if ( len( paragraph_element_list_IN ) > 0 ):

            # yes - process elements of paragraph, add to paragraph list.
            paragraph_text_list = []
            for paragraph_element in paragraph_element_list_IN:

                # convert current element to just text.  Is it NavigableString?
                if ( isinstance( paragraph_element, NavigableString ) ):

                    # it is NavigableString - convert it to string.
                    current_paragraph_text = StringHelper.object_to_unicode_string( paragraph_element )

                else:

                    # not text - just grab all the text out of it.
                    #current_paragraph_text = ' '.join( paragraph_element.findAll( text = True ) )
                    #current_paragraph_text = paragraph_element.get_text( " ", strip = True )
                    current_paragraph_text = HTMLHelper.remove_html( str( paragraph_element ) )

                #-- END check to see if current element is text. --#

                # clean up - convert HTML entities
                current_paragraph_text = my_bs_helper.convert_html_entities( current_paragraph_text )

                # strip out extra white space
                current_paragraph_text = StringHelper.replace_white_space( current_paragraph_text )

                # got any paragraph text?
                current_paragraph_text = current_paragraph_text.strip()
                if ( ( current_paragraph_text != None ) and ( current_paragraph_text != "" ) ):

                    # yes.  Add to paragraph text.
                    paragraph_text_list.append( current_paragraph_text )

                #-- END check to see if any text. --#

            #-- END loop over paragraph elements. --#

            # convert paragraph list to string
            paragraph_text = ' '.join( paragraph_text_list )

            # return paragraph text
            string_OUT = paragraph_text

        #-- END check to see if anything in list. --#

        return string_OUT

    #-- END method process_paragraph_contents() --#


    @classmethod
    def validate_FIT_results( cls, FIT_values_IN ):

        '''
        Accepts a dictionary of results from a Article_Text.find_in_text() call.
           Looks for problems (counts of nested lists not being 1, not being all
           the same).  If it finds problems, returns list of string messages
           describing problems.  If no problems, returns empty list.
        '''

        # return reference
        status_list_OUT = []

        # declare variables
        me = "validate_FIT_results"
        status_OUT = ""
        canonical_index_list = []
        plain_text_index_list = []
        paragraph_list = []
        first_word_list = []
        last_word_list = []
        canonical_index_count = -1
        plain_text_index_count = -1
        paragraph_count = -1
        first_word_count = -1
        last_word_count = -1
        count_list = []
        unique_count_list = []
        unique_count = -1
        match_count = -1

        # Unpack results - for each value, could be 0, 1, or more.
        # - If 0, no match - ERROR.
        # - If 1, use value.
        # - If more than one, multiple matches - WARNING.
        # - All lists should have same count.  If any are different - WARNING (can be because of complications relating to punctuation - "'s" or "." after name, etc.).

        # get result lists.
        canonical_index_list = FIT_values_IN.get( cls.FIT_CANONICAL_INDEX_LIST, [] )
        plain_text_index_list = FIT_values_IN.get( cls.FIT_TEXT_INDEX_LIST, [] )
        paragraph_list = FIT_values_IN.get( cls.FIT_PARAGRAPH_NUMBER_LIST, [] )
        first_word_list = FIT_values_IN.get( cls.FIT_FIRST_WORD_NUMBER_LIST, [] )
        last_word_list = FIT_values_IN.get( cls.FIT_LAST_WORD_NUMBER_LIST, [] )

        # get counts and add them to list.
        canonical_index_count = len( canonical_index_list )
        count_list.append( canonical_index_count )

        plain_text_index_count = len( plain_text_index_list )
        count_list.append( plain_text_index_count )

        paragraph_count = len( paragraph_list )
        count_list.append( paragraph_count )

        first_word_count = len( first_word_list )
        count_list.append( first_word_count )

        last_word_count = len( last_word_list )
        count_list.append( last_word_count )

        # counts all the same?
        unique_count_list = SequenceHelper.list_unique_values( count_list )

        # first, see how many unique values (should be 1).
        unique_count = len( unique_count_list )
        if ( unique_count == 1 ):

            # all have same count.  What is it?
            match_count = unique_count_list[ 0 ]
            if ( match_count == 1 ):

                # this is the normal case.  Return empty list.
                status_list_OUT = []

            elif ( match_count == 0 ):

                # error - no matches returned for quotation.  What to do?
                status_OUT = "In " + me + ": ERROR - search for string in text yielded no matches."
                status_list_OUT.append( status_OUT )
                output_debug( status_OUT )

            elif ( match_count > 1 ):

                # warning - multiple matches returned for quotation.  What to do?
                status_OUT = "In " + me + ": WARNING - search for string in text yielded " + str( match_count ) + " matches."
                status_list_OUT.append( status_OUT )
                output_debug( status_OUT )

            else:

                # error - matches returned something other than 0, 1, or
                #    > 1.  What to do?
                status_OUT = "In " + me + ": ERROR - search for string in text yielded invalid count: " + str( match_count )
                status_list_OUT.append( status_OUT )
                output_debug( status_OUT )

            #-- END check to see how many matches were found. --#

        else:

            # warning - unique_count_list does not have only one thing in it.
            status_OUT = "In " + me + ": WARNING - search for string in text yielded different numbers of results for different ways of searching: " + str( unique_count_list )
            status_list_OUT.append( status_OUT )
            output_debug( status_OUT )

        #-- END check to make sure all searches returned same count of matches. --#

        return status_list_OUT

    #-- END class method validate_FIT_results() --#


    #----------------------------------------------------------------------------
    # instance methods
    #----------------------------------------------------------------------------


    def __init__( self, *args, **kwargs ):

        # call parent __init()__ first.
        super( Article_Text, self ).__init__( *args, **kwargs )

    #-- END method __init__() --#


    def __str__( self ):

        # return reference
        string_OUT = ""

        # set content description
        self.content_description = "text"

        # call string method.
        string_OUT = super( Article_Text, self ).to_string()

        return string_OUT

    #-- END method __str__() --#


    def find_in_canonical_text( self, string_IN, do_multi_graph_check_IN = True ):

        '''
        Accepts a string that we want to locate in the nested article text.
        If found, returns a list of the indices of positions in the string where
           the string was found (could be more than one).  If not found, returns
           empty list.  If error, returns None.
        '''

        # return reference.
        list_OUT = []

        # declare variables
        me = "find_in_canonical_text"
        index_OUT = -1
        my_text = ""
        match_count = -1
        loop_count = -1
        keep_looping = False
        plain_text_index_list = []
        plain_text_count = -1
        remaining_word_list = []
        current_word_list = []
        match_count = -1
        matching_index_list = []
        current_index = -1

        # declare variables - multi-graf check - start removing wrods from
        #    beginning to test for case where start of string is end of
        #    paragraph.
        original_word_list = None
        reduced_word_list = None
        removed_word_list = None
        reduced_word_count = -1
        reduced_string = ""
        multi_graph_match_list = []
        multi_graph_match_count = -1
        continue_reducing = True
        reduced_match_index = -1
        first_word = ""
        first_word_index = -1
        removed_word = ""
        removed_word_index = -1
        removed_word_count = -1
        removed_word_match_counter = -1

        # got a string?
        if ( ( string_IN is not None ) and ( string_IN != "" ) ):

            # get text
            my_text = self.get_content()

            # first step is to try to find the string, as-is.
            list_OUT = StringHelper.find_substring_match_list( my_text, string_IN )

            # sanity check in case string spans multiple paragraphs.

            # sanity check.  Got anything?
            match_count = len( list_OUT )
            if ( match_count < 1 ):

                # no.  See if the string is in the plain text.
                plain_text_index_list = self.find_in_plain_text( string_IN )
                plain_text_count = len( plain_text_index_list )
                if ( plain_text_count > 0 ):

                    output_debug( "In " + me + ": WARNING - string being searched for is in text, likely spans paragraphs." )

                    # it is in the text.  So, start to build up string word by
                    #    word, looking for indexes where it matches the string.
                    #    Keep looping until number that match are 0 or 1.

                    # split string into words.
                    remaining_word_list = self.convert_string_to_word_list( string_IN )
                    current_word_list = []

                    # loop until 0 or 1 matches.
                    keep_looping = True
                    loop_count = 0
                    while keep_looping == True:

                        # increment loop count
                        loop_count = loop_count + 1

                        # empty matching_index_list
                        matching_index_list = []

                        # add word to current list.
                        current_word_list.append( remaining_word_list[ 0 ] )

                        # strip off the first item from remaining_word_list
                        del( remaining_word_list[ 0 ] )

                        # make string from current_word_list.
                        current_string = " ".join( current_word_list )

                        output_debug( "--> In " + me + ": loop #" + str( loop_count ) + " - looking for: " + current_string )

                        # loop over the paragraph list.
                        for current_index in StringHelper.find_substring_iter( my_text, current_string ):

                            # add match index to list.
                            matching_index_list.append( current_index )

                        #-- END loop over paragraph list. --#

                        # get count of matches.
                        match_count = len( matching_index_list )

                        # short circuit in case of looking for something that is
                        #    duplicated exactly in two places in the text.
                        remaining_word_count = len( remaining_word_list )
                        if ( remaining_word_count == 0 ):

                            # At this point, there are no more words to add, so
                            #    the current state is final.  Fall out of loop.
                            keep_looping = False

                        else:

                            # more words to add... Do we have a match?
                            if ( match_count > 1 ):

                                # still multiple matches - keep looking.
                                keep_looping = True

                            else:

                                # only 1 or 0 matches.  At this point we fall
                                #    out and see what happened.
                                keep_looping = False

                            #-- END check to see if match yet or not --#

                        #-- END check to see if no more words left. --#

                    #-- END loop to find starting paragraph. --#

                    # !find_in_canonical_text() - spans paragraphs?
                    # check if spans paragraphs.  In case of first word
                    #    in one paragraph, rest of string in another, start
                    #    removing words from the front and recursive-ish-ly
                    #    calling this method, to see if we can at least get
                    #    an idea of where it is.
                    if ( ( match_count == 0 ) and ( do_multi_graph_check_IN == True ) ):

                        # convert original string to word list.
                        original_word_list = self.convert_string_to_word_list( string_IN )

                        # start reduced_word_list at original_word_list.
                        reduced_word_list = list( original_word_list )

                        # start removed_word_list as an empty list.
                        removed_word_list = []

                        # initialize loop variables.
                        multi_graph_match_list = []
                        multi_graph_match_count = -1
                        continue_reducing = True

                        # loop, removing one word from beginning of reduced list
                        #    each time, then calling this method, with the flag
                        #    to do_multi_graph_check_IN set to False.
                        while continue_reducing == True:

                            # take first word in reduced_word_list, add it to
                            #    removed_word_list, then remove it from
                            #    reduced_word_list.
                            removed_word_list.append( reduced_word_list[ 0 ] )
                            del( reduced_word_list[ 0 ] )

                            # first, check if we are out of words.
                            reduced_word_count = len( reduced_word_list )
                            if ( reduced_word_count > 0 ):

                                # call this method with reduced string
                                reduced_string = " ".join( reduced_word_list )
                                multi_graph_match_list = self.find_in_canonical_text( reduced_string, False )

                                # what we got?
                                if ( multi_graph_match_list is not None ):

                                    # got a list back.  Matches?
                                    multi_graph_match_count = len( multi_graph_match_list )
                                    if ( multi_graph_match_count == 0 ):

                                        # no match.  Keep looping.
                                        continue_reducing = True

                                    elif ( multi_graph_match_count >= 1 ):

                                        # one or more matches.  Once you get
                                        #    matches, stop.  string is only
                                        #    getting shorter.  Will have to deal
                                        #    with multiples outside of loop.
                                        continue_reducing = False

                                    else:

                                        # error - should never get here.  Stop
                                        #    looping.
                                        continue_reducing = False
                                        output_debug( "In " + me + ": ERROR - error in child call to " + me + "() - length of list returned is not >= 0.  Falling out." )

                                    #-- END check to see how many matches. --#

                                else:

                                    # error in child call.  Stop looping.
                                    continue_reducing = False
                                    output_debug( "In " + me + ": ERROR - error in child call to " + me + "() - None returned rather than a list.  Falling out." )

                                #-- END check to see if list is None --#

                            else:

                                # reduced word count is 0. End of line.
                                continue_reducing = False

                            #-- END check to see if any words left in reduced word list. --#

                        #-- END loop to reduce and search for string. --#

                        # OK.  See if we have a match list.
                        if ( multi_graph_match_list is not None ):

                            # got more than 0?
                            multi_graph_match_count = len( multi_graph_match_list )
                            if ( multi_graph_match_count > 0 ):

                                # got something.  for each match, then, need to
                                #    loop over the removed words and look for
                                #    each in the overall string, from the right,
                                #    starting with the match index, until one of
                                #    the matches is not between the first word
                                #    and the match index (fail) or you run out
                                #    of words (match).
                                for reduced_match_index in multi_graph_match_list:

                                    # look for first word.
                                    first_word = original_word_list[ 0 ]
                                    first_word_index = my_text.rfind( first_word, 0, reduced_match_index )
                                    most_recent_index = first_word_index - 1

                                    # first word found?
                                    if ( first_word_index >= 0 ):

                                        # loop over the removed words.
                                        removed_word_count = len( removed_word_list )
                                        removed_word_match_counter = 0
                                        for removed_word in removed_word_list:

                                            # get index for removed word.
                                            removed_word_index = my_text.rfind( removed_word, 0, reduced_match_index )

                                            # make sure it is greater than
                                            #    most_recent_index.
                                            if ( removed_word_index > most_recent_index ):

                                                # removed word is in correct
                                                #    range - increment counter.
                                                removed_word_match_counter += 1
                                                output_debug( "In " + me + ": in sanity check - for reduced match index = " + str( reduced_match_index ) + ", word ( \"" + removed_word + "\" ) is at index " + str( removed_word_index ) + " which is between previous index ( " + str( most_recent_index ) + " ) and start of reduced match ( " + str( reduced_match_index ) + " ).  OK so far..." )

                                            else:

                                                # not in range.  Don't increment
                                                #    counter, no match.
                                                output_debug( "In " + me + ": in sanity check - for reduced match index = " + str( reduced_match_index ) + ", word ( \"" + removed_word + "\" ) is at index " + str( removed_word_index ) + " which is not between previous index ( " + str( most_recent_index ) + " ) and start of reduced match ( " + str( reduced_match_index ) + " ).  No match." )

                                            #-- END check to see if removed word is in right place. --#

                                            # set most_recent_index to
                                            #    removed_word_index
                                            most_recent_index = removed_word_index

                                        #-- END loop over removed words. --#

                                        # is removed_word_match_counter equal to
                                        #    removed_word_count?
                                        if ( removed_word_match_counter == removed_word_count ):

                                            # yes.  This is a match.
                                            matching_index_list.append( first_word_index )

                                        #-- END check to see if removed words indicate match --#

                                    #-- END check to see if first word found. --#

                                #-- END loop over multi-graph match list --#

                            else:

                                # nothing in list.  Leave match_count and
                                #    matching_index_list as-is.
                                pass

                            #-- END check to see if matches. --#

                        #-- END check to see if multi-graph match list --#

                    #-- END check to see if no matches at this point. --#

                    # so, got one match, or none.
                    match_count = len( matching_index_list )
                    if ( match_count >= 1 ):

                        # found one or more indexes - add each to output list.
                        for current_index in matching_index_list:

                            list_OUT.append( current_index )

                        #-- END loop over index matches. --#

                    elif ( match_count == 0 ):

                        # no match - return empty list.
                        list_OUT = []

                    else:

                        # not 0 or >= 1 - error.
                        output_debug( "In " + me + ": found " + str( next_count ) + " matches for string.  Returning None." )
                        list_OUT = None

                    #-- END check to see if we found match. --#

                #-- END check to see if string is in the text --#

            #-- END sanity check to see if got anything --#

        else:

            # no string.  Return None.
            list_OUT = None

        #-- END check to see if string. --#

        return list_OUT

    #-- END method find_in_canonical_text() --#


    def find_in_paragraph_list( self, string_IN, do_multi_graph_check_IN = True, depth_IN = 0 ):

        '''
        Accepts a string we want to locate in one of the paragraphs inside this
           article text.
        If found, returns a list of the numbers of paragraphs that contains the
           string passed in, where paragraphs are numbered starting with 1.  If
           not found, returns empty list.  If error, returns None.
        '''

        # return reference.
        list_OUT = []

        # declare variables
        me = "find_in_paragraph_list"
        index_OUT = -1
        my_paragraph_list = []
        paragraph_counter = -1
        current_paragraph = ""
        match_count = -1
        plain_text_index_list = []
        plain_text_count = -1
        plain_text_match_start_index = -1
        string_length = -1
        plain_text_match_end_index = -1
        current_paragraph_list = []
        next_paragraph_list = []
        next_count = -1
        loop_count = -1
        keep_looping = False
        remaining_word_list = []
        current_word_list = []
        current_string = ""
        current_string_index_list = None
        current_string_match_index = -1
        remaining_word_count = -1
        matching_paragraph_list = []
        match_count = -1
        current_paragraph_text = ""

        # declare variables - multi-graf check - start removing wrods from
        #    beginning to test for case where start of string is end of
        #    paragraph.
        original_word_list = None
        reduced_word_list = None
        removed_word_list = None
        multi_graph_match_list = []
        multi_graph_match_count = -1
        continue_reducing = True
        reduced_word_count = -1
        reduced_string = ""
        removed_string = ""
        removed_string_match_list = []
        preceding_paragraph_number = -1
        preceding_paragraph_index = -1
        preceding_paragraph_text = ""

        output_debug( "====> Top of " + me + ": searching for \"" + string_IN + "\"; depth = " + str( depth_IN ) )

        # got a string?
        if ( ( string_IN is not None ) and ( string_IN != "" ) ):

            # get paragraph list
            my_paragraph_list = self.get_paragraph_list()

            # loop over paragraphs
            paragraph_counter = 0
            for current_paragraph in my_paragraph_list:

                # increment counter
                paragraph_counter = paragraph_counter + 1

                # first step is to try to find the string, as-is.
                if string_IN in current_paragraph:

                    # found it.  this is the paragraph.
                    list_OUT.append( paragraph_counter )

                #-- END check to see if found in current paragraph. --#

            #-- END loop over paragraphs --#

            # sanity check in case string spans multiple paragraphs.

            # Got anything?
            match_count = len( list_OUT )
            if ( match_count < 1 ):

                # no.  See if the string is in the plain text.
                plain_text_index_list = self.find_in_plain_text( string_IN )
                plain_text_count = len( plain_text_index_list )

                if ( plain_text_count > 0 ):

                    # if just one match, get index.
                    if ( plain_text_count == 1 ):

                        # just one matching index - store it.
                        plain_text_match_start_index = plain_text_index_list[ 0 ]
                        string_length = len( string_IN )
                        plain_text_match_end_index = plain_text_match_start_index + ( string_length - 1 )

                        output_debug( "In " + me + ": WARNING - string being searched for ( " + string_IN + " ) is in text ( match index = " + str( plain_text_index_list ) + " ), likely spans paragraphs." )

                    else:

                        # multiple matches (eek!)
                        plain_text_match_start_index = -1
                        string_length = -1
                        plain_text_match_end_index = -1

                        output_debug( "In " + me + ": WARNING - string being searched for ( " + string_IN + " ) is in text multiple times ( match index = " + str( plain_text_index_list ) + " ), likely spans paragraphs, but multiple matches means no way to get single paragraph where the text occurs." )

                    #-- END check to see if one match, for sanity check --#

                    # split string into words.
                    remaining_word_list = self.convert_string_to_word_list( string_IN )
                    current_word_list = []

                    # it is in the text.  So, start to build up string word by
                    #    word, looking for paragraphs that match as we go.  Keep
                    #    looping until number that match are 0 or 1.
                    current_paragraph_list = my_paragraph_list
                    next_count = len( current_paragraph_list )
                    keep_looping = True
                    loop_count = 0
                    while keep_looping == True:

                        # increment loop count
                        loop_count = loop_count + 1

                        # empty next_paragraph_list
                        next_paragraph_list = []

                        # add word to current list.
                        current_word_list.append( remaining_word_list[ 0 ] )

                        # strip off the first item from remaining_word_list
                        del( remaining_word_list[ 0 ] )

                        # make string from current_word_list.
                        current_string = " ".join( current_word_list )

                        output_debug( "--> In " + me + ": loop #" + str( loop_count ) + " - looking for: " + current_string )

                        # loop over the paragraph list.
                        for current_paragraph in current_paragraph_list:

                            # is string in paragraph?
                            if current_string in current_paragraph:

                                # yes - add paragraph to next list.
                                next_paragraph_list.append( current_paragraph )

                            #-- END check to see if string is in paragraph --#

                        #-- END loop over paragraph list. --#

                        # switch next_paragraph_list to my_paragraph_list.
                        current_paragraph_list = next_paragraph_list
                        next_count = len( current_paragraph_list )

                        # Keep looping?

                        # short circuit in case of looking for something that is
                        #    duplicated exactly in two places in the text.
                        remaining_word_count = len( remaining_word_list )
                        if ( remaining_word_count == 0 ):

                            # At this point, there are no more words to add, so
                            #    the current state is final.  Fall out of loop.
                            keep_looping = False

                        else:

                            # more words to add... Do we have a match?
                            if ( next_count > 1 ):

                                # still multiple matches - keep looking.
                                keep_looping = True

                            else:

                                # ! sanity check - if there was a single match
                                #     for the entire string above, is the
                                #     position of the current string greater
                                #     than or equal to the position of the
                                #     entire string (if not, no match, keep
                                #     looping)?
                                if ( plain_text_match_start_index > 0 ):

                                    # got an original index.  Where does this
                                    #     latest string fall in the document?
                                    current_string_index_list = self.find_in_plain_text( current_string )
                                    current_string_match_index = current_string_index_list[ 0 ]

                                    # is current index in bounds of indices for
                                    #     the whole string match?
                                    if ( ( current_string_match_index >= plain_text_match_start_index )
                                        and ( current_string_match_index <= plain_text_match_end_index ) ) :

                                        # Looks like we've got it.
                                        keep_looping = False
                                        output_debug( "++++ In " + me + ": loop #" + str( loop_count ) + " - current match index ( " + str( current_string_match_index ) + " ) within overall match ( " + str( plain_text_match_start_index ) + " - " + str( plain_text_match_end_index ) + " ), looks like we found it." )

                                    else:

                                        # current match isn't within the actual
                                        #     original string.  Keep looping.
                                        keep_looping = True

                                        output_debug( "++++ In " + me + ": loop #" + str( loop_count ) + " - current match index ( " + str( current_string_match_index ) + " ) NOT WITHIN overall match ( " + str( plain_text_match_start_index ) + " - " + str( plain_text_match_end_index ) + " ).  Keep looking..." )

                                    #-- END check to see if

                                else:

                                    # only 1 or 0 matches.  At this point we fall
                                    #    out and see what happened.
                                    keep_looping = False

                                #-- END check to see if match found for string. --#

                            #-- END check to see if match yet or not --#

                        #-- END check to see if no more words left. --#

                    #-- END loop to find starting paragraph. --#

                    # put list of remaining paragraphs in
                    #    matching_paragraph_list and get count of matches.
                    matching_paragraph_list = list( current_paragraph_list )
                    match_count = len( matching_paragraph_list )

                    # !find_in_paragraph_list() - spans paragraphs?
                    # check if spans paragraphs.  In case of first word
                    #    in one paragraph, rest of string in another, start
                    #    removing words from the front and recursive-ish-ly
                    #    calling this method, to see if we can at least get
                    #    an idea of where it is.
                    if ( ( match_count == 0 ) and ( do_multi_graph_check_IN == True ) ):

                        # convert original string to word list.
                        original_word_list = self.convert_string_to_word_list( string_IN )

                        # start reduced_word_list at original_word_list.
                        reduced_word_list = list( original_word_list )

                        # start removed_word_list as an empty list.
                        removed_word_list = []

                        # initialize loop variables.
                        multi_graph_match_list = []
                        multi_graph_match_count = -1
                        continue_reducing = True

                        # loop, removing one word from beginning of reduced list
                        #    each time, then calling this method, with the flag
                        #    to do_multi_graph_check_IN set to False.
                        while continue_reducing == True:

                            # take first word in reduced_word_list, add it to
                            #    removed_word_list, then remove it from
                            #    reduced_word_list.
                            removed_word_list.append( reduced_word_list[ 0 ] )
                            del( reduced_word_list[ 0 ] )

                            # first, check if we are out of words.
                            reduced_word_count = len( reduced_word_list )
                            if ( reduced_word_count > 0 ):

                                # call this method with reduced string
                                reduced_string = " ".join( reduced_word_list )
                                multi_graph_match_list = self.find_in_paragraph_list( reduced_string, False, depth_IN = depth_IN + 1 )

                                # what we got?
                                if ( multi_graph_match_list is not None ):

                                    # got a list back.  Matches?
                                    multi_graph_match_count = len( multi_graph_match_list )
                                    if ( multi_graph_match_count == 0 ):

                                        # no match.  Keep looping.
                                        continue_reducing = True

                                    elif ( multi_graph_match_count >= 1 ):

                                        # one or more matches.  Once you get
                                        #    matches, stop.  string is only
                                        #    getting shorter.  Will have to deal
                                        #    with multiples outside of loop.
                                        continue_reducing = False

                                    else:

                                        # error - should never get here.  Stop
                                        #    looping.
                                        continue_reducing = False
                                        output_debug( "In " + me + ": ERROR - error in child call to " + me + "() - length of list returned is not >= 0.  Falling out." )

                                    #-- END check to see how many matches. --#

                                else:

                                    # error in child call.  Stop looping.
                                    continue_reducing = False
                                    output_debug( "In " + me + ": ERROR - error in child call to " + me + "() - None returned rather than a list.  Falling out." )

                                #-- END check to see if list is None --#

                            else:

                                # reduced word count is 0. End of line.
                                continue_reducing = False

                            #-- END check to see if any words left in reduced word list. --#

                        #-- END loop to reduce and search for string. --#

                        # OK.  See if we have a match list.
                        if ( multi_graph_match_list is not None ):

                            # got more than 0?
                            multi_graph_match_count = len( multi_graph_match_list )
                            if ( multi_graph_match_count > 0 ):

                                # got something.  for each match, then, need to
                                #    look for string of removed words in list of
                                #    paragraphs.  If removed word string is in
                                #    the paragraph before the current match (at
                                #    least in the list of matches, if not the
                                #    only one), then match!  If not, no match.
                                for reduced_match_index in multi_graph_match_list:

                                    # just look for the string made up of the
                                    #    removed words.
                                    removed_string = " ".join( removed_word_list )

                                    # call this method, telling it not to do any
                                    #    multi-paragraph checking.
                                    removed_string_match_list = self.find_in_paragraph_list( removed_string, False, depth_IN = depth_IN + 1 )

                                    # is reduced_match_index - 1 (paragraph
                                    #    before match) in list?
                                    preceding_paragraph_number = reduced_match_index - 1
                                    if ( preceding_paragraph_number in removed_string_match_list ):

                                        # got a match.  Get paragraph text for
                                        #    that preceding paragraph.

                                        # get index of preceding paragraph.
                                        preceding_paragraph_index = preceding_paragraph_number - 1

                                        # get text for that paragraph.
                                        preceding_paragraph_text = my_paragraph_list[ preceding_paragraph_index ]

                                        # add text to matching_paragraph_list
                                        matching_paragraph_list.append( preceding_paragraph_text )
                                        output_debug( "In " + me + ": in sanity check - for reduced match paragraph # = " + str( reduced_match_index ) + ", removed words ( \"" + removed_string + "\" ) are in graph(s): " + str( removed_string_match_list ) + ", which includes the previous graph ( " + str( preceding_paragraph_number ) + " ) - this is a match." )

                                    else:

                                        # not a match.
                                        output_debug( "In " + me + ": in sanity check - for reduced match paragraph # = " + str( reduced_match_index ) + ", removed words ( \"" + removed_string + "\" ) are in graphs: " + str( removed_string_match_list ) + ", none of which is the previous graph ( " + str( preceding_paragraph_number ) + " ) - this is not a match." )

                                    #-- END check to see if match for removed text is in previous paragraph. --#

                                #-- END loop over multi-graph match list --#

                            else:

                                # nothing in list.  Leave match_count and
                                #    matching_index_list as-is.
                                pass

                            #-- END check to see if matches. --#

                        #-- END check to see if multi-graph match list --#

                    #-- END check to see if no matches at this point. --#

                    # so, loop is done.  How many matches?
                    match_count = len( matching_paragraph_list )
                    if ( match_count >= 1 ):

                        # found one or more paragraphs - look up index of each
                        #    in my_paragraph_list, add that plus 1 to the list.
                        for current_paragraph_text in matching_paragraph_list:

                            index_OUT = my_paragraph_list.index( current_paragraph_text )
                            index_OUT = index_OUT + 1

                            # add to output list.
                            list_OUT.append( index_OUT )

                        #-- END loop over paragraph list. --#

                    elif ( match_count == 0 ):

                        # no match - return empty list.
                        list_OUT = []

                    else:

                        # not 0 or >= 1 - what to do?
                        output_debug( "In " + me + ": found " + str( match_count ) + " matches for string.  Returning None." )
                        list_OUT = None

                    #-- END check to see if we found paragraph. --#

                #-- END check to see if string is in the text --#

            #-- END sanity check to see if got anything --#

        else:

            # no string.  Return None.
            list_OUT = None

        #-- END check to see if string. --#

        output_debug( "====> Bottom of " + me + ": searching for \"" + string_IN + "\"; depth = " + str( depth_IN ) + "; list_OUT = " + str( list_OUT ) )

        return list_OUT

    #-- END method find_in_paragraph_list() --#


    def find_in_plain_text( self, string_IN, ignore_case_IN = False ):

        '''
        Accepts a string that we want to locate in the nested article text with
           all HTML and markup removed ("plain text").
        If found, returns the index of the start of the string inside the
           plain text for this article.  If not found, returns -1.  If error,
           returns None.
        '''

        # return reference.
        list_OUT = []

        # declare variables.
        my_text = ""

        # got a string?
        if ( ( string_IN is not None ) and ( string_IN != "" ) ):

            # get text
            my_text = self.get_content_sans_html()

            # first step is to try to find the string, as-is.
            list_OUT = StringHelper.find_substring_match_list( my_text, string_IN, ignore_case_IN = ignore_case_IN )

        else:

            # no string.  Return None.
            list_OUT = None

        #-- END check to see if string. --#

        return list_OUT

    #-- END method find_in_plain_text() --#


    def find_in_text( self, string_IN, requested_items_IN = None, ignore_case_IN = False, *args, **kwargs ):

        '''
        Accepts a string that we want to locate in the nested article text.
            If error, returns None (for now, just no string passed in to find).
            If not found, returns empty dictionary. If found, returns dictionary
            with the following values:
            - FIT_CANONICAL_INDEX_LIST = "canonical_index_list" - list of
                index(ices) of start of the string passed in in the canonical
                text for this article.
            - FIT_TEXT_INDEX_LIST = "index_list" - index(ices) of the start of
                the string passed in in the plain text for this article.
            - FIT_FIRST_WORD_NUMBER_LIST = "first_word_number_list" - the
                number(s) of the word in this article, when converted to a word
                list, of the first word in the string passed in.  Number, not
                index (so index + 1).
            - FIT_LAST_WORD_NUMBER_LIST = "last_word_number_list" - number(s)
                of the word in this article, when converted to a word list, of
                the last word in the string passed in.  Number, not index
                (so index + 1).
            - FIT_PARAGRAPH_NUMBER_LIST = "paragraph_number_list" - list of the
                number (s) of the paragraph in this article that contains the
                string (or, if it spans multiple paragraphs, the start of this
                string).
        '''

        # return reference
        dict_OUT = {}

        # declare variables
        me = "find_in_text"
        items_to_process = []
        temp_dictionary = {}
        current_value = None

        # do we have a string?
        if ( ( string_IN is not None ) and ( string_IN != "" ) ):

            # got any requested items?
            if ( ( requested_items_IN is not None ) and ( len( requested_items_IN ) > 0 ) ):

                # yes.  use this as list of items to process.
                items_to_process = requested_items_IN

            else:

                # no - process all items.
                items_to_process = []
                items_to_process.append( self.FIT_CANONICAL_INDEX_LIST )
                items_to_process.append( self.FIT_TEXT_INDEX_LIST )
                items_to_process.append( self.FIT_FIRST_WORD_NUMBER_LIST )
                items_to_process.append( self.FIT_LAST_WORD_NUMBER_LIST )
                items_to_process.append( self.FIT_PARAGRAPH_NUMBER_LIST )

            #-- END check to see which items we process. --#

            # go item by item.

            # FIT_CANONICAL_INDEX_LIST
            if ( self.FIT_CANONICAL_INDEX_LIST in items_to_process ):

                # find the index of the start of the string in the canonical
                #    text for this article (paragraphs preserved as <p> tags).
                current_value = self.find_in_canonical_text( string_IN )
                dict_OUT[ self.FIT_CANONICAL_INDEX_LIST ] = current_value

            #-- END FIT_CANONICAL_INDEX_LIST --#

            # FIT_TEXT_INDEX_LIST
            if ( self.FIT_TEXT_INDEX_LIST in items_to_process ):

                # find the index of the start of the string in the plain text
                #    for this article.
                current_value = self.find_in_plain_text( string_IN, ignore_case_IN = ignore_case_IN )
                dict_OUT[ self.FIT_TEXT_INDEX_LIST ] = current_value

            #-- END FIT_TEXT_INDEX_LIST --#

            # FIT_FIRST_WORD_NUMBER_LIST and/or FIT_LAST_WORD_NUMBER_LIST
            if ( ( self.FIT_FIRST_WORD_NUMBER_LIST in items_to_process ) or ( self.FIT_LAST_WORD_NUMBER_LIST in items_to_process ) ):

                # find the position in the list of words in this article for the
                #    first and last words in the string passed in (also can
                #    approximate word count from this, as well).
                temp_dictionary = self.find_in_word_list( string_IN )

                # will return a dictionary with first and last number.
                if ( self.FIT_FIRST_WORD_NUMBER_LIST in items_to_process ):

                    # get value and store it in output dictionary.
                    current_value = temp_dictionary[ self.FIT_FIRST_WORD_NUMBER_LIST ]
                    dict_OUT[ self.FIT_FIRST_WORD_NUMBER_LIST ] = current_value

                #-- END check to see if we return number of first word in word list. --#

                # will return a dictionary with first and last number.
                if ( self.FIT_LAST_WORD_NUMBER_LIST in items_to_process ):

                    # get value and store it in output dictionary.
                    current_value = temp_dictionary[ self.FIT_LAST_WORD_NUMBER_LIST ]
                    dict_OUT[ self.FIT_LAST_WORD_NUMBER_LIST ] = current_value

                #-- END check to see if we return number of first word in word list. --#

            #-- FIT_FIRST_WORD_NUMBER_LIST and/or FIT_LAST_WORD_NUMBER_LIST --#

            # FIT_PARAGRAPH_NUMBER_LIST
            if ( self.FIT_PARAGRAPH_NUMBER_LIST in items_to_process ):

                # find the number of the paragraph in this article that contains
                #    the string passed in.  If through some error or insanity
                #    the string starts in one paragraph and ends in another,
                #    will find the paragraph in which it starts.
                current_value = self.find_in_paragraph_list( string_IN )
                dict_OUT[ self.FIT_PARAGRAPH_NUMBER_LIST ] = current_value

            #-- END FIT_PARAGRAPH_NUMBER_LIST --#

        else:

            # no string passed in, return None.
            dict_OUT = None

        #-- END check to see if string passed in. --#

        return dict_OUT

    #-- END method find_in_text() --#


    def find_in_word_list( self, string_IN, remove_punctuation_IN = False ):

        '''
        Accepts a string we want to locate in the word list based on this
           article text.
        Returns a dictionary that contains two name-value pairs:
           - FIT_FIRST_WORD_NUMBER_LIST = "first_word_number_list" - the
              number(s) of the word in this article, when converted to a word
              list, of the first word in the string passed in.  Number, not
              index (so index + 1).
           - FIT_LAST_WORD_NUMBER_LIST = "last_word_number_list" - the number(s)
              of the word in this article, when converted to a word list, of the
              last word in the string passed in.  Number, not index
              (so index + 1).
        If not found, each will contain an empty list.  If error, returns None.
        '''

        # return reference.
        dict_OUT = {}
        first_word_list_OUT = []
        last_word_list_OUT = []
        first_word_OUT = -1
        last_word_OUT = -1
        my_word_list = []
        string_word_list = []
        match_list = []
        match_index = -1
        string_word_count = -1
        recurse_results_dict = None

        # got a string?
        if ( ( string_IN is not None ) and ( string_IN != "" ) ):

            # get paragraph list
            my_word_list = self.get_word_list( remove_punctuation_IN = remove_punctuation_IN )

            #output_debug( "article word list: " + str( my_word_list ) )

            # convert string into a word list.
            string_word_list = self.convert_string_to_word_list( string_IN,
                                                                 remove_html_IN = True,
                                                                 remove_punctuation_IN = remove_punctuation_IN,
                                                                 clean_white_space_IN = True )

            #output_debug( "search word list: " + str( string_word_list ) )

            # try the KnuthMorrisPratt algorithm from Python Cookbook 2nd Ed.
            for match_index in SequenceHelper.KnuthMorrisPratt( my_word_list, string_word_list ):

                # append match to list.
                match_list.append( match_index )

            #-- END loop over matches. --#

            # got anything?
            if ( len( match_list ) > 0 ):

                # yes - loop over matches.
                for match_index in match_list:

                    # add 1 - want word number, not word index.
                    first_word_OUT = match_index + 1

                    # get word count
                    string_word_count = len( string_word_list )

                    # for last word, set it to match_index + word count
                    last_word_OUT = match_index + string_word_count

                    # add to lists.
                    first_word_list_OUT.append( first_word_OUT )
                    last_word_list_OUT.append( last_word_OUT )

                #-- END loop over matches. --#

            else:

                # no matches.  Try removing punctuation?

                # If haven't already, try removing punctuation and looking.
                if ( remove_punctuation_IN == False ):

                    # we did not remove punctuation.  Try calling again, but
                    #    removing punctuation.
                    recurse_results_dict = self.find_in_word_list( string_IN, remove_punctuation_IN = True )

                    # got anything back?
                    if ( recurse_results_dict is not None ):

                        # return the results of this call.
                        first_word_list_OUT = recurse_results_dict[ self.FIT_FIRST_WORD_NUMBER_LIST ]
                        last_word_list_OUT = recurse_results_dict[ self.FIT_LAST_WORD_NUMBER_LIST ]

                    else:

                        first_word_list_OUT = []
                        last_word_list_OUT = []

                    #-- END check to see if got anything back. --#

                else:

                    # punctuation is removed.  Hope is dead.  Return empty lists.
                    first_word_list_OUT = []
                    last_word_list_OUT = []

                #-- END check to see if we've tried removing punctuation. --#

            #-- END check to see if match. --#

            # build return dictionary.
            dict_OUT = {}
            dict_OUT[ self.FIT_FIRST_WORD_NUMBER_LIST ] = first_word_list_OUT
            dict_OUT[ self.FIT_LAST_WORD_NUMBER_LIST ] = last_word_list_OUT

        else:

            # no string.  Return None.
            dict_OUT = None

        #-- END check to see if string. --#

        return dict_OUT

    #-- END method find_in_word_list() --#


    def get_content_sans_html( self, *args, **kwargs ):

        '''
        Returns content nested in this instance but with ALL HTML removed.
        Preconditions: None
        Postconditions: None

        Returns the content exactly as it is stored in the instance.
        '''

        # return reference
        content_OUT = None

        # declare variables
        me = "get_content_sans_html"

        # get the content.
        content_OUT = self.content

        # strip all HTML
        content_OUT = HTMLHelper.remove_html( content_OUT, bs_parser_IN = BS_PARSER )

        return content_OUT

    #-- END method get_content_sans_html() --#


    def get_paragraph_list( self, *args, **kwargs ):

        '''
        Looks in nested content for paragraph tags.  Returns a list of the text
           in paragraph tags, in the same order as they appeared in the content,
           with no nested HTML.  If no <p> tags, returns a list with a single item - all of the text.
        Preconditions: None
        Postconditions: None

        Returns a list of the paragraphs in the content.
        '''

        # return reference
        list_OUT = []

        # declare variables
        me = "get_paragraph_list"
        my_content = ""
        content_bs = None
        p_tag_list = []
        p_tag_count = -1
        current_p_tag = None
        current_p_tag_id = ""
        current_p_tag_contents = ""

        # get the content.
        my_content = self.content

        # create a BeautifulSoup instance that contains it.
        content_bs = BeautifulSoup( my_content, BS_PARSER )

        # get all the <p> tags.
        p_tag_list = content_bs.find_all( 'p' )

        # how many?
        p_tag_count = len( p_tag_list )

        # got any at all?
        if ( p_tag_count > 0 ):

            # yes - prepopulate list, so we can assign positions based on "id"
            #    attribute values.
            list_OUT = [ None ] * p_tag_count

            # loop!
            for current_p_tag in p_tag_list:

                # get id attribute value and contents.
                current_p_tag_id = int( current_p_tag[ "id" ] )
                current_p_tag_contents = self.make_paragraph_string( current_p_tag.contents )

                # add contents to output list at position of "id".
                list_OUT[ current_p_tag_id - 1 ] = current_p_tag_contents

            #-- END loop over p-tags. --#

        else:

            # none at all.  Just return content in first item of list.
            list_OUT.append( my_content )

        #-- END check to see if any p-tags

        return list_OUT

    #-- END method get_paragraph_list() --#


    def get_word_list( self, remove_punctuation_IN = False, *args, **kwargs ):

        '''
        Creates list of words contained in nested content.  Returns a list of
           the words in the Article_Text, with each word added as an item in the
           list, in the same order as they appeared in the content, with no
           nested HTML.
        Preconditions: None
        Postconditions: None

        Returns a list of the words in the content.
        '''

        # return reference
        list_OUT = []

        # declare variables
        me = "get_paragraph_list"
        my_content = ""
        cleaned_content = ""
        word_list = []
        word_count = -1
        word_counter = -1
        current_word = ""

        # get the content.
        my_content = self.content

        # split the string on white space.
        word_list = self.convert_string_to_word_list( my_content,
                                                      remove_html_IN = True,
                                                      remove_punctuation_IN = remove_punctuation_IN,
                                                      clean_white_space_IN = True )

        # how many we got?
        word_count = len( word_list )

        # check to see that we have some words.
        if ( word_count > 0 ):

            # yes - prepopulate list, so we can assign positions based on "id"
            #    attribute values.
            list_OUT = [ None ] * word_count

            # loop!
            word_counter = 0
            for current_word in word_list:

                # add word to list
                list_OUT[ word_counter ] = current_word

                # increment word counter
                word_counter = word_counter + 1

            #-- END loop over words. --#

        else:

            # none at all.  Just return content in first item of list.
            list_OUT.append( my_content )

        #-- END check to see if any words

        return list_OUT

    #-- END method get_word_list() --#


    def make_paragraph_string( self, paragraph_element_list_IN, *args, **kwargs ):

        '''
        Accepts a list of the contents of a paragraph.  Loops over them and
           pulls them all together into one string.  Returns the string.

        Params:
        - paragraph_element_list_IN - list of BeautifulSoup4 elements that from an article paragraph.
        '''

        # return reference
        string_OUT = ""

        # declare variables
        my_bs_helper = ""

        # initialize BeautifulSoup helper
        my_bs_helper = self.get_bs_helper()

        # call class method
        string_OUT = self.process_paragraph_contents( paragraph_element_list_IN, my_bs_helper )

        return string_OUT

    #-- END method make_paragraph_string() --#


    def remove_paragraphs( self, paragraph_id_list_IN, *args, **kwargs ):

        '''
        Accepts a list of ids of paragraphs we want to remove (based on the id
            attributes in <p> tags in canonical text).

        Retrieves the desired canonical text, parses it using BeautifulSoup,
            removes the paragraphs one-by-one, decrementing the IDs of any
            paragraphs with ids higher than the one currently being removed.
            After processing, converts the text back to a string and stores it,
            then returns status string - "Success!" if no problems, delimited
            list of error messages separated by " || " if problems arose.

        Postconditions: The canonical text inside this instance is updated after
            calling this routine, but you still need to save() to persist the
            updates to the database.
        '''

        # return reference
        status_OUT = self.STATUS_SUCCESS

        # declare variables.
        me = "remove_paragraphs"
        status_message = ""
        status_message_list = []
        canonical_text = ""
        canonical_text_bs = None
        sorted_desc_id_list = []
        p_list_bs = None
        p_to_delete_bs = None
        p_to_delete_counter = -1
        removed_p_bs = None
        removed_p_list = []
        current_p_bs = None
        current_id = ""
        current_id_int = ""
        current_p_string = ""
        p_text_list = []

        # is list populated?
        if ( ( paragraph_id_list_IN is not None )
            and ( isinstance( paragraph_id_list_IN, list ) == True )
            and ( len( paragraph_id_list_IN ) > 0 ) ):

            # it is.  Sort list in descending order.
            sorted_desc_id_list = list( paragraph_id_list_IN )
            sorted_desc_id_list.sort( reverse = True )

            # get canonical text
            canonical_text = self.content

            # parse with beautiful soup
            canonical_text_bs = BeautifulSoup( canonical_text )

            # loop over IDs.
            for id_to_remove in sorted_desc_id_list:

                # find paragraph with this ID and remove it.
                p_list_bs = canonical_text_bs.find_all( "p", id = str( id_to_remove ) )

                # loop - should be only 1.
                p_to_delete_counter = 0
                for p_to_delete_bs in p_list_bs:

                    # increment counter
                    p_to_delete_counter += 1

                    # remove the <p> from the document.
                    removed_p_bs = p_to_delete_bs.extract()

                    # add it to removed list
                    removed_p_list.append( removed_p_bs )

                #-- END loop over p tags that match ID. --#

                # check count - should be 1.
                if ( p_to_delete_counter > 1 ):

                    # error.
                    status_message = "In " + me + "(): multiple <p> tags ( " + str( p_to_delete_counter ) + " ) with id of " + str( id_to_remove ) + " - they are all gone...  Should only have been one."
                    status_message_list.append( status_message )

                #-- END sanity check for multiple <p> with same id -->

                # get all <p> tags and for those with id greater than that we
                #     deleted, decrement their IDs by 1.
                p_list_bs = canonical_text_bs.find_all( "p" )
                for current_p_bs in p_list_bs:

                    # get id
                    current_id = current_p_bs[ 'id' ]

                    # convert to integer
                    current_id_int = int( current_id )

                    # is it greater than the ID of the <p> we deleted?
                    if ( current_id_int > id_to_remove ):

                        # it is.  Decrement value by 1...
                        current_id_int = current_id_int - 1

                        # ...and store back in p tag.
                        current_p_bs[ 'id' ] = str( current_id_int )

                    #-- END check if id is greater than that of deleted <p>. --#

                #-- END loop over <p> tags. --#

            #-- END loop over IDs of <p> tags to remove --#

            # after all that, convert BeautifulSoup instance back to text. --#
            p_text_list = []
            p_list_bs = canonical_text_bs.find_all( "p" )
            for current_p_bs in p_list_bs:

                # convert to string
                current_p_string = StringHelper.object_to_unicode_string( current_p_bs )

                # add to list
                p_text_list.append( current_p_string )

            #-- END loop over <p> tags. --#

            # join list to create new canonical text.
            canonical_text = "".join( p_text_list )

            # store back in content
            self.content = canonical_text

        else:

            status_message = "In " + me + "(): ERROR - nothing in list of IDs to delete, so not updating text."
            status_message_list.append( status_message )

        #-- END Check to see if any IDs in list. --#

        # got statuses?
        if ( ( status_message_list is not None ) and ( len( status_message_list ) > 0 ) ):

            # convert to string
            status_OUT = " || ".join( status_message_list )

        else:

            # nothing - return empty string.
            status_OUT = self.STATUS_SUCCESS

        #-- END check to see if status messages. --#

        return status_OUT

    #-- END method remove_paragraphs() --#


    def save(self, *args, **kwargs):

        '''
        Overriding save() method so that we always clean self.content before
           storing it in database.
        '''

        # declare variables
        my_content = ""

        # get content
        my_content = self.get_content()

        # clean that content
        self.set_text( my_content, self.do_clean_on_save )

        # call parent save() method
        super( Article_Text, self).save( *args, **kwargs )

    #-- END overriden save() method --#


    def set_text( self, text_IN = "", clean_text_IN = True, *args, **kwargs ):

        '''
        Accepts a piece of text.  If asked, we clean the text, then we store
           it in this instance's content variable.
        Preconditions: None
        Postconditions: None

        Returns the text as it is stored in the instance.
        '''

        # return reference
        text_OUT = None

        # declare variables
        me = "set_content"
        text_value = ""

        # clean text?
        if ( clean_text_IN == True ):

            # yes.
            text_value = self.clean_body_text( text_IN )

        else:

            # no just use what was passed in.
            text_value = text_IN

        #-- END check to see if we clean... --#

        # set the text in the instance and return the content.
        text_OUT = self.set_content( text_value )

        return text_OUT

    #-- END method set_text() --#


#-- END Article_Text model --#


# Article_Data model
class Article_Data( models.Model ):

    # declaring a few "constants"
    DEBUG = True

    ARTICLE_TYPE_NEWS_TO_ID_MAP = {
        'news' : 1,
        'sports' : 2,
        'feature' : 3,
        'opinion' : 4,
        'other' : 99
    }

    ARTICLE_TYPE_CHOICES = (
        ( "news", "News" ),
        ( "sports", "Sports" ),
        ( "feature", "Feature" ),
        ( "opinion", "Opinion" ),
        ( "other", "Other" )
    )

    STATUS_NEW = "new"
    STATUS_COMPLETE = "complete"
    STATUS_SERVICE_ERROR = "service_error"
    STATUS_UNKNOWN_ERROR = "unknown_error"
    STATUS_DEFAULT = STATUS_NEW

    # filter_records() parameters
    PARAM_CODERS = ContextTextBase.PARAM_CODERS
    PARAM_CODER_TYPE_FILTER_TYPE = ContextTextBase.PARAM_CODER_TYPE_FILTER_TYPE
    PARAM_CODER_TYPES_LIST = ContextTextBase.PARAM_CODER_TYPES_LIST
    PARAM_TAGS_IN_LIST = ContextTextBase.PARAM_TAGS_IN_LIST
    PARAM_TAG_LIST = ContextTextBase.PARAM_TAG_LIST
    PARAM_ARTICLE_ID_IN_LIST = ContextTextBase.PARAM_ARTICLE_ID_LIST

    # Filtering Article_Data on coder_type.
    CODER_TYPE_FILTER_TYPE_NONE = ContextTextBase.CODER_TYPE_FILTER_TYPE_NONE
    CODER_TYPE_FILTER_TYPE_AUTOMATED = ContextTextBase.CODER_TYPE_FILTER_TYPE_AUTOMATED
    CODER_TYPE_FILTER_TYPE_ALL = ContextTextBase.CODER_TYPE_FILTER_TYPE_ALL
    CODER_TYPE_FILTER_TYPE_DEFAULT = ContextTextBase.CODER_TYPE_FILTER_TYPE_DEFAULT


    #----------------------------------------------------------------------
    # ! ==> model fields
    #----------------------------------------------------------------------

    article = models.ForeignKey( Article, on_delete = models.CASCADE )
    coder = models.ForeignKey( User, on_delete = models.CASCADE )
    coder_type = models.CharField( max_length = 255, blank = True, null = True )
    topics = models.ManyToManyField( Topic, blank = True )
    locations = models.ManyToManyField( Location, blank = True )
    article_type = models.CharField( max_length = 255, choices = ARTICLE_TYPE_CHOICES, blank = True, default = 'news' )
    is_sourced = models.BooleanField( default = True )
    can_code = models.BooleanField( default = True )
    status = models.CharField( max_length = 255, blank = True, null = True, default = STATUS_DEFAULT )
    status_messages = models.TextField( blank = True, null = True )
    create_date = models.DateTimeField( auto_now_add = True )
    last_modified = models.DateTimeField( auto_now = True )

    # Was saving topics and location per article, not referencing shared topic
    #    or location tables.  No longer (see topics and locations above).
    #topics = models.ManyToManyField( Article_Topic, blank = True, null = True )
    #locations = models.ManyToManyField( Article_Location, blank = True, null = True )

    # Changed to having a separate join table, not ManyToMany auto-generated one.
    #authors = models.ManyToManyField( Article_Author )
    #subjects = models.ManyToManyField( Article_Subject )

    # field to store how source was captured.
    capture_method = models.CharField( max_length = 255, blank = True, null = True )

    # related projects:
    projects = models.ManyToManyField( Project, blank = True )
    work_log = models.ForeignKey( Work_Log, on_delete = models.SET_NULL, blank = True, null = True )

    # Meta-data for this class.
    class Meta:
        ordering = [ 'article', 'last_modified', 'create_date' ]


    #----------------------------------------------------------------------
    # ! ==> class methods
    #----------------------------------------------------------------------

    @classmethod
    def create_q_filter_automated_by_coder_type( cls, coder_type_in_list_IN = None, include_non_automated_coders_IN = True ):

        '''
        Accepts list of coder types we want included in Article_Data instances
           that were coded by an automated coder.  Returns Q() object that can
           be applied to an Article_Data QuerySet to filter any rows that were
           coded by the automated coder to only include those with coder_type
           in the list passed in.

        postconditions: Does not actually filter anything.  Returns a Q()
           instance that you can use to filter.
        '''

        # return reference
        q_OUT = None

        # declare variables
        me = "create_q_filter_automated_by_coder_type"
        log_message = None
        automated_coder_user = None
        current_query = None

        # got a list?
        if ( ( coder_type_in_list_IN is not None ) and ( len( coder_type_in_list_IN ) > 0 ) ):

            # get automated coder.
            automated_coder_user = ContextTextBase.get_automated_coding_user()

            if cls.DEBUG == True:
                log_message = "automated coder user: {} - {}".format( automated_coder_user.id, automated_coder_user )
                output_log_message( log_message, me, do_print_IN = True )
            #-- END DEBUG --#

            # filter - either:

            # ( coder = automated_coder AND coder_type = automated_coder_type )
            current_query = Q( coder = automated_coder_user ) & Q( coder_type__in = coder_type_in_list_IN )

            # just filtering automated, but not excluding non-automated?
            #    Said another way, include non-automated coder, as well?
            if ( include_non_automated_coders_IN == True ):

                # OR coder != automated_coder
                current_query = ~Q( coder = automated_coder_user ) | current_query

            #-- END check to see if we include non-automated coder, as well --#

            # return the query
            q_OUT = current_query

        #-- END check to see if list passed in. --#

        return q_OUT

    #-- END class method create_q_filter_automated_by_coder_type() --#


    @classmethod
    def create_q_only_automated( cls, coder_type_in_list_IN = None ):

        '''
        Accepts list of coder types we want included in Article_Data instances
           that were coded by an automated coder.  Returns Q() object that can
           be applied to an Article_Data QuerySet to limit to Article_Data coded
           by the automated coder, and then optionally filter any rows that were
           coded by the automated coder to only include those with coder_type
           in the list passed in.

        postconditions: Does not actually filter anything.  Returns a Q()
           instance that you can use to filter.
        '''

        # return reference
        q_OUT = None

        # declare variables
        automated_coder_user = None
        current_query = None

        # get automated coder.
        automated_coder_user = ContextTextBase.get_automated_coding_user()

        # just include those coded by automated coder.
        q_OUT = Q( coder = automated_coder_user )

        # got a list?
        if ( ( coder_type_in_list_IN is not None ) and ( len( coder_type_in_list_IN ) > 0 ) ):

            # yes - filter to only those with coder_type in list passed in.
            current_query = cls.create_q_filter_automated_by_coder_type( coder_type_in_list_IN, include_non_automated_coders_IN = False )

            # add the filter to the Q() we will return.
            q_OUT = q_OUT & current_query

        #-- END check to see if list passed in. --#

        return q_OUT

    #-- END class method create_q_only_automated() --#


    @classmethod
    def filter_article_persons(
        cls,
        qs_IN,
        exclude_persons_with_tags_list_IN = None,
        include_persons_with_single_name_IN = None
    ):

        '''
        Accepts Article_Person child class QuerySet and parameters for how it
            should be filtered. Returns QuerySet with any requested filtering
            completed.

        Parameters:
        - exclude_persons_with_tags_list_IN - if tag names list provided,
            excludes any person with any one of those tags assigned.
        - include_persons_with_single_name_IN - if "yes" or empty, does nothing.
            If "no", filters to only records with a space (" ") in verbatim_name
            (so a multi-word name).

        postconditions: Returns new QuerySet filtered as described above. If no
            parameters passed in, returns QuerySet passed in, unchanged.
        '''

        # return reference
        qs_OUT = None

        # declare variables

        # init
        qs_OUT = qs_IN

        # exclude persons with tags in tag name list?
        if (
            ( exclude_persons_with_tags_list_IN is not None )
            and ( len( exclude_persons_with_tags_list_IN ) > 0 )
        ):

            # exclude persons with tags in tag name list
            qs_OUT = qs_OUT.exclude( tags__name__in = exclude_persons_with_tags_list_IN )

        #-- END check if exclude persons with tags in tag name list --#

        # include persons with single-word verbatim_name?
        if (
            ( include_persons_with_single_name_IN is not None )
            and ( include_persons_with_single_name_IN == ContextTextBase.CHOICE_NO )
        ):

            # do not include single-word verbatim_name (must be a space in there)
            qs_OUT = qs_OUT.filter( verbatim_name__contains = " " )

        #-- END check if include persons with single word verbatim_name. --#

        return qs_OUT

    #-- END class method filter_article_persons() --#


    @classmethod
    def filter_automated_by_coder_type( cls, qs_IN, coder_type_in_list_IN = None ):

        '''
        Accepts Article_Data QuerySet and list of coder types we want included
           in Article_Data instances that were coded by an automated coder in
           the QuerySet passed in.  Returns QuerySet object filtered so that any
           Article_Data coded by the automated coder has one of the coder_type
           values in the list passed in.

        postconditions: Returns new QuerySet filtered as described above.  If no
           list specified, return same QuerySet as was passed in.
        '''

        # return reference
        qs_OUT = None

        # declare variables
        filter_q = None

        # got a list?
        if ( ( coder_type_in_list_IN is not None ) and ( len( coder_type_in_list_IN ) > 0 ) ):

            # get Q() for list.
            filter_q = cls.create_q_filter_automated_by_coder_type( coder_type_in_list_IN )

            # return newly filtered QuerySet
            qs_OUT = qs_IN.filter( filter_q )

        else:

            # no list - return what was passed in.
            qs_OUT = qs_IN

        #-- END check to see if list passed in. --#

        return qs_OUT

    #-- END class method filter_automated_by_coder_type() --#


    @classmethod
    def filter_only_automated( cls, qs_IN, coder_type_in_list_IN = None ):

        '''
        Accepts Article_Data QuerySet and optional list of coder types we want
           included in Article_Data instances that were coded by an automated
           coder.  Returns QuerySet with any coders other than automated
           removed, and then if coder type list is present, filters to only
           include rows with coder_type in the list passed in.

        postconditions: Returns new QuerySet filtered as described above.  If no
           list specified, return same QuerySet with only automated coded
           Article_Data instances, with any coder_type.
        '''

        # return reference
        qs_OUT = None

        # declare variables
        filter_q = None

        # get Q().
        filter_q = cls.create_q_only_automated( coder_type_in_list_IN )

        # return newly filtered QuerySet
        qs_OUT = qs_IN.filter( filter_q )

        return qs_OUT

    #-- END class method filter_only_automated() --#


    @classmethod
    def filter_records( cls, qs_IN = None, params_IN = None, *args, **kwargs ):

        '''
        Accepts parameters in kwargs.  Uses arguments to filter a QuerySet of
            articles, which it subsequently returns.  If QuerySet
            passed in, this method appends filters to it.  If not, starts with
            a new QuerySet.  Specifically, accepts:
            - Article_Data.PARAM_CODERS ("coder_list_IN") - list of coder Users we want work for.
            - Article_Data.PARAM_CODER_TYPE_FILTER_TYPE ("coder_type_filter_type_IN") -
            - Article_Data.PARAM_CODER_TYPES_LIST ("coder_types_list_IN") -
            - Article_Data.PARAM_TAGS_IN_LIST ("tags_in_list_IN") - Looks at the tags for the article associated with each Article_Data
            - Article_Data.PARAM_ARTICLE_ID_IN_LIST ("article_id_list_IN") - Looks for Article_Data for articles whose ID is in this parameter.

        Preconditions: None.
        Postconditions: returns the QuerySet passed in with filters added as
            specified by arguments.  If no QuerySet passed in, creates new
            Article_Data QuerySet, returns it with filters added.
        '''

        # return reference
        qs_OUT = None

        # declare variables
        me = "filter_records"
        my_logger_name = "context_text.models.Article_Data"
        my_logger = None

        # declare variables - input parameters
        my_params = None
        my_dict_helper = None
        coder_in_list_IN = None
        coder_type_filter_type_IN = None
        coder_types_list_IN = None
        tags_in_list_IN = None
        article_id_in_list_IN = None
        custom_q_IN = None
        get_distinct_records_IN = None

        # declare variables - processing variables
        current_query = None
        query_list = None
        newspaper_instance = None
        paper_id_in_list = None
        q_date_range = None
        coder_in_list = None
        tags_in_list = None
        article_id_in_list = None
        query_item = None

        # do DISTINCT?
        do_distinct = False
        article_data_id_list = None
        duplicate_count = -1
        current_article_data = None
        current_id = -1

        #-----------------------------------------------------------------------
        # ! ==> init
        #-----------------------------------------------------------------------

        # init - get logger
        my_logger = LoggingHelper.get_a_logger( logger_name_IN = my_logger_name )

        # init - query list
        query_list = []

        # init - store kwargs in params_IN, and in DictHelper instance.
        if ( params_IN is not None ):

            # got params passed in - use them.
            my_params = params_IN

            # and append kwargs, just in case.
            my_params.update( kwargs )

        else:

            # use kwargs
            my_params = kwargs

        #-- END check to see if params other than kwargs passed in.

        my_dict_helper = DictHelper()
        my_dict_helper.set_dictionary( my_params )

        # got a query set?
        if ( qs_IN ):

            # use the one passed in.
            qs_OUT = qs_IN

            #output_debug( "QuerySet passed in, using it.", me, "*** " )

        else:

            # No.  Make one.
            qs_OUT = cls.objects.all()

            #output_debug( "No QuerySet passed in, using fresh one.", me, "*** " )

        #-- END check to see if query set passed in --#

        #-----------------------------------------------------------------------
        # ! ==> retrieve parameters
        #-----------------------------------------------------------------------

        # coder_in_list
        coder_in_list_IN = my_dict_helper.get_value_as_list( cls.PARAM_CODERS, default_IN = None )


        # Coder type
        coder_type_filter_type_IN = my_params.get( cls.PARAM_CODER_TYPE_FILTER_TYPE, None )
        coder_types_list_IN = my_dict_helper.get_value_as_list( cls.PARAM_CODER_TYPES_LIST, default_IN = None )

        # multiple options for tag in list
        tags_in_list_IN = my_dict_helper.get_value_as_list( cls.PARAM_TAGS_IN_LIST, default_IN = None )

        # got anything for cls.PARAM_TAGS_IN_LIST?
        if ( tags_in_list_IN is None ):

            # no.  Try cls.PARAM_TAG_LIST...
            tags_in_list_IN = my_dict_helper.get_value_as_list( cls.PARAM_TAG_LIST, default_IN = None )

        #-- END check to see if cls.PARAM_TAGS_IN_LIST present --#

        article_id_in_list_IN = my_dict_helper.get_value_as_list( cls.PARAM_ARTICLE_ID_IN_LIST, default_IN = None )

        # custom Q parameter, just in case.
        custom_q_IN = my_params.get( cls.PARAM_CODER_TYPE_FILTER_TYPE, None )

        #---------------------
        # ! ==> coder IN list
        #---------------------

        my_logger.debug( "In " + me + "(): coder_in_list_IN = " + str( coder_in_list_IN ) )

        # Update QuerySet to only include articles with tags in list?
        if ( coder_in_list_IN is not None ):

            # get the value as a list, whether it is a delimited string or list.
            coder_in_list = ListHelper.get_value_as_list( coder_in_list_IN )

            # filter?
            if ( ( coder_in_list is not None ) and ( len( coder_in_list ) > 0 ) ):

                # something in list - filter.
                current_query = Q( coder__in = coder_in_list )
                query_list.append( current_query )

                # And, need to do DISTINCT on id.
                do_distinct = True

            #-- END check to see if anything in list. --#

        #-- END check to see if tags IN list is in arguments --#

        #---------------------
        # ! ==> coder type
        #---------------------

        my_logger.debug( "In " + me + "(): coder_type_filter_type_IN = " + str( coder_type_filter_type_IN ) )
        my_logger.debug( "In " + me + "(): coder_types_list_IN = " + str( coder_types_list_IN ) )

        # anything in automated coder type include list?
        if ( ( coder_types_list_IN is not None ) and ( isinstance( coder_types_list_IN, list ) == True ) and ( len( coder_types_list_IN ) > 0 ) ):

            # What is our filter type?
            if ( coder_type_filter_type_IN == cls.CODER_TYPE_FILTER_TYPE_AUTOMATED ):

                # Just filter automated records, not all records.
                qs_OUT = Article_Data.filter_automated_by_coder_type( qs_OUT, coder_types_list_IN )

            elif( coder_type_filter_type_IN == cls.CODER_TYPE_FILTER_TYPE_ALL ):

                # all records.
                qs_OUT = qs_OUT.filter( coder_type__in = coder_types_list_IN )

            else:

                # unknown, or specifically requested to not filter on coder
                #    type.
                pass

            #-- END check to see what filter type --#

        #-- END check to see if anything in coder_type_list.

        #--------------------
        # ! ==> tags IN list
        #--------------------

        my_logger.debug( "In " + me + "(): tags_in_list_IN = " + str( tags_in_list_IN ) )

        # Update QuerySet to only include articles with tags in list?
        if ( tags_in_list_IN is not None ):

            # get the value as a list, whether it is a delimited string or list.
            tags_in_list = ListHelper.get_value_as_list( tags_in_list_IN )

            # filter?
            if ( ( tags_in_list is not None ) and ( len( tags_in_list ) > 0 ) ):

                # something in list - filter.
                current_query = Q( article__tags__name__in = tags_in_list )
                query_list.append( current_query )

                # And, need to do DISTINCT on id.
                do_distinct = True

            #-- END check to see if anything in list. --#

        #-- END check to see if tags IN list is in arguments --#

        #--------------------------
        # ! ==> article ID IN list
        #--------------------------

        my_logger.debug( "In " + me + "(): article_id_in_list_IN = " + str( article_id_in_list_IN ) )

        # Update QuerySet to only include articles with tags in list?
        if ( article_id_in_list_IN is not None ):

            # get the value as a list, whether it is a delimited string or list.
            article_id_in_list = ListHelper.get_value_as_list( article_id_in_list_IN )

            # filter?
            if ( ( article_id_in_list is not None ) and ( len( article_id_in_list ) > 0 ) ):

                # set up query instance to look for articles with
                #    ID in the list of values passed in.  Not
                #    quoting, since django should do that.
                current_query = Q( article__id__in = article_id_in_list )

                # add it to list of queries
                query_list.append( current_query )

            #-- END check to see if anything in list. --#

        #-- END check to see if tags IN list is in arguments --#

        #-------------------------------
        # ! ==> custom-built Q() object
        #-------------------------------

        my_logger.debug( "In " + me + "(): custom_q_IN = " + str( custom_q_IN ) )

        # try to update QuerySet for selected sections.
        if ( custom_q_IN is not None ):

            # got something in the parameter?
            if ( ( custom_q_IN is not None )
                and ( isinstance( custom_q_IN, Q ) == True ) ):

                # yes.  Add to q queue.
                current_query = custom_q_IN
                query_list.append( current_query )

            #-- END check to see if custom Q() present. --#

        #-- END check to see if Custom Q argument present --#

        #-----------------------------------------------------------------------
        # ! ==> filter with Q() list
        #-----------------------------------------------------------------------

        # now, add them all to the QuerySet - try a loop
        for query_item in query_list:

            # append each filter to query set.
            qs_OUT = qs_OUT.filter( query_item )

        #-- END loop over query set items --#

        #-----------------------------------------------------------------------
        # ! ==> do DISTINCT?
        #-----------------------------------------------------------------------

        # do DISTINCT on ID?
        if ( do_distinct == True ):

            # do DISTINCT
            # qs_OUT.distinct() - doesn't work.

            # init ID set.
            article_data_id_list = []
            duplicate_count = 0

            # loop over results:
            for current_article_data in qs_OUT:

                # get ID
                current_id = current_article_data.id

                # already in list?
                if ( current_id not in article_data_id_list ):

                    # add it to list.
                    article_data_id_list.append( current_id )

                else:

                    # already in the list.
                    duplicate_count += 1

                #-- END check to see if ID already in list. --#

            #-- END loop over articles --#

            my_logger.debug( "In " + me + "(): do_distinct = " + str( do_distinct ) + "; duplicate count = " + str( duplicate_count ) + "; Article_Data IDs = " + str( article_data_id_list ) )

            # anything in list?
            if ( len( article_data_id_list ) > 0 ):

                # yes - were there any duplicates?
                if ( duplicate_count > 0 ):

                    # yes.  Make a query that just limits to current matches.
                    qs_OUT = Article_Data.objects.filter( id__in = article_id_list )

                    my_logger.debug( "In " + me + "(): filtered out " + str( duplicate_count ) + " duplicate Article_Data." )

                #-- END check to see if any duplicates. --#

            #-- END check to see if anything in ID list --#

        #-- END check to see if we do DISTINCT --#

        return qs_OUT

    #-- END class method filter_records() --#


    @classmethod
    def make_deep_copy( cls, id_to_copy_IN, new_coder_user_id_IN = None, *args, **kwargs ):

        '''
        Accepts ID of Article_Data instance we want to make a deep copy of and
            the optional ID of a User we want to set as coder in the copy.
            First, loads record with ID passed in and makes a copy (by setting
            pk and id to None, then saving).  Then, goes through all the related
            sets and ManyToMany relations and manually makes copies of all the
            related records, pointing them at the appropriate places in the new
            copied tree.

        - Article_Data deep copy
            - look at all relations that will need to be duplicated and
                re-referenced...
            - ManyToMany:
                - topics
                - locations
                - projects
            - Article_Data_Notes
            - Article_Person
                - Article_Author
                    - Alternate_Author_Match
                - Article_Subject
                    - ManyToMany:
                        - topics
                    - Alternate_Subject_Match
                    - Article_Subject_Mention
                    - Article_Subject_Quotation
                    - Subject_Organization
        '''

        # return reference
        instance_OUT = None

        # declare variables
        me = "make_deep_copy"
        debug_message = ""
        my_logger_name = "context_text.models.Article_Data"
        is_id_valid = -1
        copy_from_article_data = None
        copy_to_article_data = None

        # declare variables - ManyToMany
        copy_m2m_from = None
        copy_m2m_to = None
        m2m_qs = None
        m2m_instance = None

        # declare variables - related Article_Data_Notes
        copy_me_article_data_notes_qs = None
        copy_me_article_data_notes_count = None
        article_data_notes = None

        # declare variables - related Article_Author
        copy_me_article_author_qs = None
        copy_me_article_author_count = None
        article_author = None
        copy_me_id = -1
        new_article_author = None

        # declare variables - related Article_Subject
        copy_me_article_subject_qs = None
        copy_me_article_subject_count = None
        article_subject = None
        new_article_subject = None

        # declare variables - new coder user
        new_coder_user_instance = None

        # got an ID?
        is_id_valid = IntegerHelper.is_valid_integer( id_to_copy_IN, must_be_greater_than_IN = 0 )
        if ( is_id_valid ):

            # DEBUG
            debug_message = "deep copying Article_Data record with ID = " + str( id_to_copy_IN )
            output_debug( debug_message, me, logger_name_IN = my_logger_name )

            # make and save copy.
            copy_from_article_data = Article_Data.objects.get( pk = id_to_copy_IN )
            copy_to_article_data = copy_from_article_data
            copy_to_article_data.id = None
            copy_to_article_data.pk = None
            copy_to_article_data.save()

            # reload copy_me.
            copy_from_article_data = Article_Data.objects.get( pk = id_to_copy_IN )

            debug_message = "--> deep copying FROM Article_Data record with ID = " + str( id_to_copy_IN ) + " INTO Article_Data ID = " + str( copy_to_article_data.id )
            output_debug( debug_message, me, logger_name_IN = my_logger_name )

            '''
            - Article_Data deep copy
                - look at all relations that will need to be duplicated and re-referenced...
                - Article_Data_Notes
                - Article_Person
                    - Article_Author
                        - Alternate_Author_Match
                    - Article_Subject
                        - Alternate_Subject_Match
                        - Article_Subject_Mention
                        - Article_Subject_Quotation
                        - Subject_Organization
            '''

            # ! ----> ManyToMany - topics
            DjangoModelHelper.copy_m2m_values( "topics", copy_from_article_data, copy_to_article_data )

            # ! ----> ManyToMany - locations
            DjangoModelHelper.copy_m2m_values( "locations", copy_from_article_data, copy_to_article_data )

            # ! ----> ManyToMany - projects
            DjangoModelHelper.copy_m2m_values( "projects", copy_from_article_data, copy_to_article_data )

            # ! ----> Article_Data_Notes

            # get QuerySet and count()
            copy_me_article_data_notes_qs = copy_from_article_data.article_data_notes_set.all()
            copy_me_article_data_notes_count = copy_me_article_data_notes_qs.count()

            debug_message = "found " + str( copy_me_article_data_notes_count ) + " Article_Data_Notes instances."
            output_debug( debug_message, me, logger_name_IN = my_logger_name )

            # got anything?
            if ( copy_me_article_data_notes_count > 0 ):

                # yes.  loop.
                for article_data_notes in copy_me_article_data_notes_qs:

                    debug_message = "----> deep copying FROM Article_Data_Notes record with ID = " + str( article_data_notes.id )
                    output_debug( debug_message, me, logger_name_IN = my_logger_name )

                    # None out id and pk.
                    article_data_notes.id = None
                    article_data_notes.pk = None

                    # change reference to Article_Data from copy_me to copy_to.
                    article_data_notes.article_data = copy_to_article_data

                    # save.
                    article_data_notes.save()

                    debug_message = "----> INTO Article_Data_Notes ID = " + str( article_data_notes.id )
                    output_debug( debug_message, me, logger_name_IN = my_logger_name )

                #-- END loop over Article_Data_Notes --#

            #-- END check to see if any Article_Data_Notes --#

            # ! ----> Article_Author

            # get QuerySet and count()
            copy_me_article_author_qs = copy_from_article_data.article_author_set.all()
            copy_me_article_author_count = copy_me_article_author_qs.count()

            debug_message = "found " + str( copy_me_article_author_count ) + " Article_Author instances."
            output_debug( debug_message, me, logger_name_IN = my_logger_name )

            # got anything?
            if ( copy_me_article_author_count > 0 ):

                # yes.  loop.
                for article_author in copy_me_article_author_qs:

                    # get original ID
                    copy_me_id = article_author.id

                    # call the deep copy method in it.
                    new_article_author = Article_Author.make_deep_copy( id_to_copy_IN = copy_me_id )

                    # change reference to Article_Data from copy_me to copy_to.
                    new_article_author.article_data = copy_to_article_data

                    # save.
                    new_article_author.save()

                    debug_message = "----> deep copying FROM Article_Author record with ID = " + str( copy_me_id ) + " INTO Article_Author ID = " + str( new_article_author.id )
                    output_debug( debug_message, me, logger_name_IN = my_logger_name )

                #-- END loop over Article_Author --#

            #-- END check to see if any Article_Author --#

            # ! ----> Article_Subject

            # get QuerySet and count()
            copy_me_article_subject_qs = copy_from_article_data.article_subject_set.all()
            copy_me_article_subject_count = copy_me_article_subject_qs.count()

            debug_message = "found " + str( copy_me_article_subject_count ) + " Article_Subject instances."
            output_debug( debug_message, me, logger_name_IN = my_logger_name )

            # got anything?
            if ( copy_me_article_subject_count > 0 ):

                # yes.  loop.
                for article_subject in copy_me_article_subject_qs:

                    # get original ID
                    copy_me_id = article_subject.id

                    # call the deep copy method in it.
                    new_article_subject = Article_Subject.make_deep_copy( id_to_copy_IN = copy_me_id )

                    # change reference to Article_Data from copy_me to copy_to.
                    new_article_subject.article_data = copy_to_article_data

                    # save.
                    new_article_subject.save()

                    debug_message = "----> deep copying FROM Article_Subject record with ID = " + str( copy_me_id ) + " INTO Article_Subject ID = " + str( new_article_subject.id )
                    output_debug( debug_message, me, logger_name_IN = my_logger_name )

                #-- END loop over Article_Subject --#

            #-- END check to see if any Article_Subject --#

        #-- END check to see if id passed in is valid --#

        # do we have a User to set as the coder in the copy?
        if ( ( new_coder_user_id_IN is not None )
            and ( isinstance( new_coder_user_id_IN, six.integer_types ) == True )
            and ( new_coder_user_id_IN > 0 ) ):

            # put get() in try so we don't blow up if error, since the copy is
            #     already made and saved.
            try:

                # we do.  Get the user...
                new_coder_user_instance = User.objects.get( pk = new_coder_user_id_IN )

                # ...store it in the copy...
                copy_to_article_data.coder = new_coder_user_instance

                # ...and save.
                copy_to_article_data.save()

            except:

                # problem looking up new user - log a message, but don't blow up
                #     since the copy is already completely done other than the
                #     user.
                debug_message = "----> deep copying FROM Article_Subject record with ID = " + str( copy_me_id ) + " INTO Article_Subject ID = " + str( new_article_subject.id ) + " - attempt to lookup user ID " + str( new_coder_user_id_IN ) + " failed."
                output_debug( debug_message, me, logger_name_IN = my_logger_name )

            #-- END try...except around User.objects.get() --#

        #-- END check to see if ID of user to set as coder --#

        instance_OUT = copy_to_article_data

        return instance_OUT

    #-- END class method make_deep_copy() --#


    #----------------------------------------------------------------------------
    # ! ==> instance methods
    #----------------------------------------------------------------------------

    def __str__( self ):

        # return reference
        string_OUT = ""

        # got an ID?
        if ( self.id ):

            string_OUT = str( self.id )

        #-- END check to see if there is an ID. --#

        # got a coder?
        if ( self.coder ):

            string_OUT += " - " + str( self.coder )

        else:

            string_OUT += " - no coder"

        #-- END - got coder type? --#

        # got a coder_type?
        if ( self.coder_type ):

            string_OUT += " ( ADCT: " + str( self.coder_type ) + " ) "

        else:

            string_OUT += " - no coder_type"

        #-- END - got coder type? --#

        string_OUT += " -- Article: " + str( self.article )

        return string_OUT

    #-- END method __str__() --#


    def get_article_authors_qs(
        self,
        exclude_persons_with_tags_list_IN = None,
        include_persons_with_single_name_IN = None
    ):

        '''
        Retrieves a QuerySet that contains related Article_Author instances,
            optionally filtered so people with specified tags are excluded, and
            persons with single word names are included.
        '''

        # return reference
        qs_OUT = None

        # declare variables

        # get all article authors
        qs_OUT = self.article_author_set.all()

        # do standard Article_Person and children filtering.
        qs_OUT = self.filter_article_persons(
            qs_OUT,
            exclude_persons_with_tags_list_IN = exclude_persons_with_tags_list_IN,
            include_persons_with_single_name_IN = include_persons_with_single_name_IN
        )

        return qs_OUT

    #-- END method get_article_authors_qs() --#


    def get_quoted_article_sources_qs(
        self,
        exclude_persons_with_tags_list_IN = None,
        include_persons_with_single_name_IN = None
    ):

        '''
        Retrieves a QuerySet that contains related Article_Subject instances
            that are of subject_type "quoted".
        '''

        # return reference
        qs_OUT = None

        # declare variables

        # get all article sources
        qs_OUT = self.article_subject_set.all()

        # filter to just those with subject type of "quoted"
        #    (Article_Subject.SUBJECT_TYPE_QUOTED).
        qs_OUT = qs_OUT.filter( subject_type = Article_Subject.SUBJECT_TYPE_QUOTED )

        # do standard Article_Person and children filtering.
        qs_OUT = self.filter_article_persons(
            qs_OUT,
            exclude_persons_with_tags_list_IN = exclude_persons_with_tags_list_IN,
            include_persons_with_single_name_IN = include_persons_with_single_name_IN
        )

        return qs_OUT

    #-- END method get_quoted_article_sources_qs() --#


    def get_source_counts_by_type( self ):

        '''
            Method: get_source_counts_by_type
            Retrieves all sources, loops over them and creates a dictionary that maps
               source types to the count of that type of source in this article.
            preconditions: the instance needs to have an article loaded in it.
            postconditions: returns dictionary that maps each source type to the count
               of sources of that type in this article.

            Returns:
               - dictionary - dictionary that maps each source type to the count of sources of that type in this article.
        '''

        # return reference
        counts_OUT = {}

        # declare variables
        types_dictionary = None
        current_type = ''
        #current_type_id = ''
        article_sources = None
        current_source = None
        current_source_type = ''
        current_type_count = -1

        # grab types from Article_Subject
        types_dictionary = Article_Subject.SOURCE_TYPE_TO_ID_MAP

        # populate output dictionary with types
        for current_type in types_dictionary.iterkeys():

            counts_OUT[ current_type ] = 0

        #-- END loop over source types --#

        # now get sources, loop over them, and for each, get source type, add
        #    one to the value in the hash for that type.
        article_sources = self.get_quoted_article_sources_qs()

        for current_source in article_sources:

            # get type for source
            current_source_type = current_source.source_type

            # retrieve value for that source from the dictionary
            if current_source_type in counts_OUT:

                # source type is in the dictionary.  Retrieve value.
                current_type_count = counts_OUT[ current_source_type ]

                # increment
                current_type_count += 1

                # store new value.
                counts_OUT[ current_source_type ] = current_type_count

            else:

                # source type not in dictionary.  Hmmm.  Set its entry to 1.
                counts_OUT[ current_source_type ] = 1

            #-- END conditional to increment count for current type.

        #-- END loop over sources --#

        return counts_OUT

    #-- END method get_source_counts_by_type() --#


    def my_article_id( self ):

        # return reference
        value_OUT = ""

        if ( ( self.article is not None ) and ( self.article ) ):

            value_OUT = self.article.id

        else:

            value_OUT = None

        #-- END check to see if we have an article. --#

        return value_OUT

    #-- END method my_article_id() --#


    def set_status( self, status_IN, status_message_IN = None ):

        '''
        Accepts status value and status message.  Stores status in "status"
           field.  Appends status_message to "status_messages" field, preceded
           by a newline if field is not empty.  Returns status.
        '''

        # return reference
        status_OUT = ""

        # got a status?
        if ( status_IN is not None ):

            # yes.  store it.
            self.status = status_IN

        #-- END check to see if status. --#

        # got message?
        if ( ( status_message_IN is not None ) and ( status_message_IN != "" ) ):

            # yes.  Anything currently in message?
            if ( ( self.status_messages is not None ) and ( self.status_messages != "" ) ):

                self.status_messages += "\n" + status_message_IN

            else:

                self.status_messages = status_message_IN

            #-- END check to see if we need a newline. --#

        #-- END check to see if message. --#

        status_OUT = self.status

        return status_OUT

    #-- END method set_status() --#


    def short_str( self ):

        # return reference
        string_OUT = ""

        # got an ID?
        if ( self.id ):

            string_OUT = str( self.id )

        #-- END check to see if there is an ID. --#

        string_OUT += " -- Article: " + str( self.article.id )

        return string_OUT

    #-- END method short_str() --#


#= End Article_Data Model =======================================================


# Article_Content model
class Article_Data_Notes( Abstract_Related_JSON_Content ):

    #----------------------------------------------------------------------
    # model fields and meta
    #----------------------------------------------------------------------

    # allow more than one related piece of "Article_Content" per article.
    article_data = models.ForeignKey( Article_Data, on_delete = models.CASCADE )

    # meta class with ordering.
    class Meta:

        ordering = [ 'article_data', 'last_modified', 'create_date' ]

    #-- END nested Meta class --#

    #----------------------------------------------------------------------------
    # instance methods
    #----------------------------------------------------------------------------


    def __init__( self, *args, **kwargs ):

        # call parent __init()__ first.
        super( Article_Data_Notes, self ).__init__( *args, **kwargs )

    #-- END method __init__() --#


    def to_string( self ):

        # return reference
        string_OUT = ""

        if ( self.id ):

            string_OUT += str( self.id ) + " - "

        #-- END check to see if ID --#

        if ( self.content_description ):

            string_OUT += self.content_description

        #-- END check to see if content_description --#

        if ( self.content_type ):

            string_OUT += " of type \"" + self.content_type + "\""

        #-- END check to see if there is a type --#

        string_OUT += " for article_data: " + str( self.article_data )

        return string_OUT

    #-- END method to_string() --#


    def __str__( self ):

        # return reference
        string_OUT = ""

        string_OUT = self.to_string()

        return string_OUT

    #-- END method __str__() --#


#-- END abstract Article_Data_Notes model --#


# Article_Person model
class Article_Person( Abstract_Person_Parent ):


    #----------------------------------------------------------------------
    # constants-ish
    #----------------------------------------------------------------------

    #RELATION_TYPE_CHOICES = (
    #    ( "author", "Article Author" ),
    #    ( "subject", "Article Subject " )
    #)

    TAG_SINGLE_NAME_PART = ContextTextBase.TAG_SINGLE_NAME_PART
    TAG_SINGLE_NAME_MISMATCH_WITH_PERSON = ContextTextBase.TAG_SINGLE_NAME_MISMATCH_WITH_PERSON
    TAG_ME_SINGLE_NAME_PERSON_MULTI = ContextTextBase.TAG_ME_SINGLE_NAME_PERSON_MULTI

    #----------------------------------------------------------------------------
    # model fields and meta
    #----------------------------------------------------------------------------

    article_data = models.ForeignKey( Article_Data, on_delete = models.CASCADE )
    organization = models.ForeignKey( Organization, on_delete = models.SET_NULL, blank = True, null = True )
    person = models.ForeignKey( Person, on_delete = models.CASCADE, blank = True, null = True )
    original_person = models.ForeignKey( Person, on_delete = models.SET_NULL, blank = True, null = True, related_name="%(app_label)s_%(class)s_original_person_set")
    #relation_type = models.CharField( max_length = 255, choices = RELATION_TYPE_CHOICES )
    name = models.CharField( max_length = 255, blank = True, null = True )
    verbatim_name = models.CharField( max_length = 255, blank = True, null = True )
    lookup_name = models.CharField( max_length = 255, blank = True, null = True )

    # details on automated matching, if attempted.
    # capture match confidence - start with 1 or 0, but leave room for
    #    decimal values.
    match_confidence_level = models.DecimalField( max_digits = 11, decimal_places = 10, blank = True, null = True, default = 0.0 )
    match_status = models.TextField( blank = True, null = True )

    # field to store how person was captured. - moved to Abstract_Person_Parent.
    #capture_method = models.CharField( max_length = 255, blank = True, null = True )

    # moved up to Abstract_Person_Parent
    #title = models.CharField( max_length = 255, blank = True, null = True )
    #more_title = models.TextField( blank = True, null = True )
    #organization_string = models.CharField( max_length = 255, blank = True, null = True )
    #more_organization = models.TextField( blank = True, null = True )

    # time stamps.
    create_date = models.DateTimeField( auto_now_add = True )
    last_modified = models.DateTimeField( auto_now = True )

    # meta class so we know this is an abstract class.
    class Meta:

        abstract = True

    #----------------------------------------------------------------------------
    # NOT Instance variables
    # Class variables - overriden by __init__() per instance if same names, but
    #    if not set there, shared!
    #----------------------------------------------------------------------------


    # variable to hold list of multiple potentially matching persons, if more
    #    than one found when lookup is attempted by Article_Coder.
    #person_match_list = []


    #----------------------------------------------------------------------------
    # instance methods
    #----------------------------------------------------------------------------


    def __init__( self, *args, **kwargs ):

        # call parent __init()__ first.
        super( Article_Person, self ).__init__( *args, **kwargs )

        # then, initialize variable.
        self.person_match_list = []  # expects a list of person instances.

    #-- END method __init__() --#


    def __str__( self ):

        # return reference
        string_OUT = ""

        if ( self.id ):

            string_OUT += str( self.id ) + " - "

        #-- END check to see if id --#

        if ( self.person is not None ):

            string_OUT += self.person.last_name + ", " + self.person.first_name

        else:

            string_OUT += 'empty Article_Person instance'

        #-- END check to see if person. --#

        return string_OUT

    #-- END method __str__() --#


    def get_article_info( self ):

        '''
        Returns information on the article associated with this person.
        '''

        # return reference
        string_OUT = ''

        # declare variables
        article_instance = None

        # get article instance
        article_instance = self.article_data.article

        string_OUT = str( article_instance )

        return string_OUT

    #-- END method get_article_info() --#


    def get_alternate_person_id_list( self, append_to_list_IN = None, *args, **kwargs ):

        '''
        If there are any related Alternate person Match records, makes a list of
            IDs of the Persons associated with each, then returns that
            list.  If none, returns an empty list.  If error, returns None.
        '''

        # return reference
        list_OUT = None

        # declare variables
        me = "get_alternate_person_id_list"
        alternate_person_list = None
        person_instance = None
        person_ID = -1

        # initialize output list
        if ( ( append_to_list_IN is not None )
            and ( isinstance( append_to_list_IN, list ) == True ) ):

            list_OUT = append_to_list_IN

        else:

            # Nothing passed in.  Make a new list.
            list_OUT = []

        #-- END check to see if output list passed in. --#

        # try to get list of alternate persons.
        alternate_person_list = self.get_alternate_person_list()

        # got something?
        if ( ( alternate_person_list is not None )
            and ( isinstance( alternate_person_list, list ) == True )
            and ( len( alternate_person_list ) > 0 ) ):

            # yes.  Loop, grabbing the ID of each person and placing it in our
            #     output list.
            for person_instance in alternate_person_list:

                # get ID.
                person_ID = person_instance.id

                # add to list.
                list_OUT.append( person_ID )

            #-- END loop over person instances.

        #-- END check to see if any alternate persons. --#

        return list_OUT

    #-- END function get_alternate_person_id_list() --#


    def get_alternate_person_list( self, *args, **kwargs ):

        '''
        If there are any related Alternate_Author_Match records, makes a list of
            Person instances of Persons associated with each, then returns that
            list.  If none, returns an empty list.  If error, returns None.
        '''

        # return reference
        person_list_OUT = None

        # declare variables
        me = "get_alternate_person_list"
        alternate_person_qs = None
        alternate_person_count = -1
        alternate_person = None
        person_instance = None

        # initialize output list
        person_list_OUT = []

        # see if there is anything in article_author_match_set.
        alternate_person_qs = self.get_alternate_person_match_qs()
        alternate_person_count = alternate_person_qs.count()

        if ( alternate_person_count > 0 ):

            # loop, adding each person to the list.
            for alternate_person in alternate_person_qs:

                # get Person instance.
                person_instance = alternate_person.person

                # add to output list.
                person_list_OUT.append( person_instance )

            #-- END loop over associated alternate persons --#

        #-- END check to see if any alternate matches --#

        return person_list_OUT

    #-- END function get_alternate_person_list() --#


    @abstractmethod
    def get_alternate_person_match_qs( self ):

        '''
        If there are any alternate matches for this person, returns a list of
            Match instances for each (each contains a reference to a "person"
            along with other information).  If none found, returns empty list.
            If error returns None.  This method is abstract, so the child
            classes can each define how they deal with multiple matches and
            ambiguity.
        '''

        print( "++++++++ In Article_Person.get_alternate_person_match_qs() ++++++++" )

        pass

    #-- END function get_alternate_person_match_qs() --#


    def get_associated_person_id_list( self ):

        '''
        If there is a related Person or any related Alternate person Match
            records, makes a list of IDs of the Persons associated with each,
            then returns that list.  If none, returns an empty list.  If error,
            returns None.
        '''

        # return reference
        list_OUT = None

        # declare variables
        me = "get_associated_person_id_list"
        my_person = None
        alternate_person_list = None
        person_instance = None
        person_ID = -1

        # initialize output list
        list_OUT = []

        # first, is there a nested person?
        my_person = self.person
        if ( my_person is not None ):

            # there is.  Get ID and add it to the list.
            person_ID = my_person.id
            list_OUT.append( person_ID )

        #-- END check to se if nested person --#

        # get alternate person ID list.
        alternate_person_id_list = self.get_alternate_person_id_list()

        # got something?
        if ( ( alternate_person_id_list is not None )
            and ( isinstance( alternate_person_id_list, list ) == True )
            and ( len( alternate_person_id_list ) > 0 ) ):

            # yes.  Add items in the list to our output list.
            list_OUT.extend( alternate_person_id_list )

        #-- END check to see if any alternate persons. --#

        return list_OUT

    #-- END function get_associated_person_id_list() --#


    def get_person_id( self ):

        '''
        Returns ID of person associated with this record.
        '''

        # return reference
        id_OUT = ''

        # declare variables
        my_person = None

        # get current person.
        my_person = self.person

        # see if there is a person
        if ( my_person is not None ):

            # are we also loading the person?
            id_OUT = my_person.id

        #-- END check to make sure there is an associated person.

        return id_OUT

    #-- END method get_person_id() --#


    def get_verbatim_name_part_count( self ):

        '''
        Retrieves name part list from `get_name_part_list()`. Returns count.
        '''

        # return reference
        value_OUT = None

        # declare variables
        name_part_list = None
        name_part_count = None

        # get name part list
        name_part_list = self.get_verbatim_name_part_list()

        # got anything back?
        if ( name_part_list is not None ):

            # get and return count.
            name_part_count = len( name_part_list )
            value_OUT = name_part_count

        else:

            # error. return None
            value_OUT = None

        #-- END check for returned name part list. --#

        return value_OUT

    #-- END class method get_verbatim_name_part_count() --#


    def get_verbatim_name_part_list( self, split_string_IN = None ):

        '''
        Retrieves list of tokens from split()-ing the verbatim_name field.
        '''

        # return reference
        list_OUT = None

        # declare variables
        me = "get_verbatim_name_token_list"
        status_message = None
        my_verbatim_name = None
        my_verbatim_name_part_list = None
        name_part_count = None

        # get count.
        my_verbatim_name = self.verbatim_name
        my_verbatim_name_part_list = self.get_name_part_list_from_name( my_verbatim_name )
        name_part_count = len( my_verbatim_name_part_list )

        list_OUT = my_verbatim_name_part_list

        return list_OUT

    #-- END class method get_verbatim_name_token_list() --#


    def get_verbatim_name_token_count( self ):

        '''
        Retrieves name part list from `get_name_part_list()`. Returns count.
        '''

        # return reference
        value_OUT = None

        # declare variables
        name_part_list = None
        name_part_count = None

        # get name part list
        name_part_list = self.get_verbatim_name_token_list()

        # got anything back?
        if ( name_part_list is not None ):

            # get and return count.
            name_part_count = len( name_part_list )
            value_OUT = name_part_count

        else:

            # error. return None
            value_OUT = None

        #-- END check for returned name part list. --#

        return value_OUT

    #-- END class method get_verbatim_name_token_count() --#


    def get_verbatim_name_token_list( self, split_string_IN = None ):

        '''
        Retrieves list of tokens from split()-ing the verbatim_name field.
        '''

        # return reference
        list_OUT = None

        # declare variables
        me = "get_verbatim_name_token_list"
        status_message = None
        my_verbatim_name = None
        my_verbatim_name_token_list = None
        name_part_count = None

        # get count.
        my_verbatim_name = self.verbatim_name
        my_verbatim_name_token_list = my_verbatim_name.split()
        name_part_count = len( my_verbatim_name_token_list )

        list_OUT = my_verbatim_name_token_list

        return list_OUT

    #-- END class method get_verbatim_name_token_list() --#


    def is_single_verbatim_name( self ):

        '''
        Retrieves count of name parts from `get_name_part_count_from_name()`.
            Returns True if 1, False if > 1, and raises ContextException
            otherwise.
        '''

        # return reference
        is_single_name_OUT = False

        # declare variables
        me = "is_single_verbatim_name"
        status_message = None
        my_verbatim_name = None
        name_part_count = None

        # get count.
        my_verbatim_name = self.verbatim_name
        name_part_count = self.get_name_part_count_from_name( my_verbatim_name )

        # how many?
        if ( name_part_count == 1 ):

            # single name part.
            is_single_name_OUT = True

        elif ( name_part_count > 1 ):

            # more than one name part.
            is_single_name_OUT = False

        else:

            # not 1 or > 1. Error.
            is_single_name_OUT = None
            status_message = "In Abstract_Person.{me}(): name_count = {name_count}, not 1 or greater than 1, unexpected at this point.".format(
                me = me,
                name_count = name_part_count
            )
            raise ContextError( "status_message" )

        #-- END how many name parts found? --#

        return is_single_name_OUT

    #-- END class method is_single_verbatim_name() --#


    def is_single_verbatim_name_token( self ):

        '''
        Retrieves count of name part tokens by split()-ing the verbatim_name
            field. Returns True if 1, False if > 1, and raises ContextException
            otherwise.
        '''

        # return reference
        is_single_name_OUT = False

        # declare variables
        me = "is_single_name"
        status_message = None
        my_verbatim_name = None
        my_verbatim_name_part_list = None
        name_part_count = None

        # get count.
        my_verbatim_name = self.verbatim_name
        my_verbatim_name_part_list = self.get_verbatim_name_token_list( my_verbatim_name )
        name_part_count = len( my_verbatim_name_part_list )

        # how many?
        if ( name_part_count == 1 ):

            # single name part.
            is_single_name_OUT = True

        elif ( name_part_count > 1 ):

            # more than one name part.
            is_single_name_OUT = False

        else:

            # not 1 or > 1. Error.
            is_single_name_OUT = None
            status_message = "In Abstract_Person.{me}(): name_count = {name_count}, not 1 or greater than 1, unexpected at this point.".format(
                me = me,
                name_count = name_part_count
            )
            raise ContextError( "status_message" )

        #-- END how many name parts found? --#

        return is_single_name_OUT

    #-- END class method is_single_verbatim_name_token() --#


    def is_connected( self, param_dict_IN = None ):

        """
            Method: is_connected()

            Purpose: accepts a parameter dictionary for specifying more rigorous
               ways of including or ommitting connections.  Returns true if
               there is a person reference.

            Inheritance: In Article_Person, and in child Article_Author, just
               always returns true if there is a person reference.  In
               Article_Subject, examines the categorization of the source to
               determine if the source is eligible to be classified as
               "connected" to the authors of the story.  If "connected", returns
               True.  If not, returns False.  By default, "Connected" = source
               of type "individual" with contact type of "direct" or "event".
               Eventually we can make this more nuanced, allow filtering here
               based on input parameters, and allow different types of
               connections to be requested.  For now, just need it to work.

            Params:
            - param_dict_IN - contains person whose connectedness we need to check.

            Returns:
            - boolean - If "connected", returns True.  If not, returns False.
        """

        # return reference
        is_connected_OUT = True

        # declare variables
        current_person_id = ''

        # does the source have a person ID?
        current_person_id = self.get_person_id()
        if ( not ( current_person_id ) ):

            # no person ID, so can't make a relation
            is_connected_OUT = False

        #-- END check to see if there is an associated person --#

        return is_connected_OUT

    #-- END method is_connected() --#


    @abstractmethod
    def process_alternate_matches( self ):

        '''
        If there are matches in the variable person_match_list, loops over them
           and deals with each appropriately.  person_match_list is a list of
           Person instances of people who might be a match for a given name
           string.  This method is abstract, so the child classes can each
           define how they deal with multiple matches.
        '''

        print( "++++++++ In Article_Person process_alternate_matches() ++++++++" )

        pass

    #-- END function process_alternate_matches() --#


    def save( self, *args, **kwargs ):

        '''
        Overridden save() method that calls process_alternate_matches() after
           django's save() method.

        Note: looks like child classes don't have to override save method.
        '''

        #print( "++++++++ In Article_Person save() ++++++++" )

        # declare variables.

        # call parent save() method.
        super( Article_Person, self ).save( *args, **kwargs )

        # call process_alternate_matches
        self.process_alternate_matches()

    #-- END method save() --#


    def update_from_person_details( self, person_details_IN, do_save_IN = True, *args, **kwargs ):

        '''
        Accepts PersonDetails instance and an optional boolean flag that tells
            whether we want to save at the end or not.  For PersonDetails that
            are present in this abstract class (title and organization),
            retrieves values from person_details, then processes them
            appropriately.  End result is that this instance is updated, and if
            the do_save_IN flag is set, the updated values are persisted to the
            database, as well.

        Preconditions: Must pass a PersonDetails instance, even if it is empty.

        Postconditions: Instance is updated, and if do_save_IN is True, any
            changes are saved to the database.

        Returns the title.
        '''

        # return reference
        status_OUT = "Success!"

        # declare variables
        me = "update_from_person_details"
        parent_status = None
        my_person_details = None
        my_id = -1
        is_insert = False
        existing_article_data = ""
        existing_person_instance = None
        existing_name = ""
        existing_verbatim_name = ""
        existing_lookup_name = ""
        existing_match_confidence_level = -1
        existing_match_status = ""
        existing_capture_method = ""
        article_data_IN = ""
        person_instance_IN = None
        name_IN = ""
        verbatim_name_IN = ""
        lookup_name_IN = ""
        match_confidence_level_IN = -1
        match_status_IN = ""
        capture_method_IN = ""
        is_updated = False

        # declare variables - person instance
        existing_person_id = -1
        new_person_id = -1

        # call parent method.
        parent_status = super( Article_Person, self ).update_from_person_details( person_details_IN, do_save_IN = do_save_IN, *args, **kwargs )
        if ( parent_status is None ):

            # status of None = success.  Carry on.

            # get values of interest from this instance.
            existing_article_data_instance = self.article_data
            existing_person_instance = self.person
            existing_name = self.name
            existing_verbatim_name = self.verbatim_name
            existing_lookup_name = self.lookup_name
            existing_match_confidence_level = self.match_confidence_level
            existing_match_status = self.match_status
            existing_capture_method = self.capture_method

            # got person_details?
            my_person_details = PersonDetails.get_instance( person_details_IN )
            if ( my_person_details is not None ):

                # we have PersonDetails.  Get values of interest.
                article_data_instance_IN = my_person_details.get( PersonDetails.PROP_NAME_ARTICLE_DATA_INSTANCE, None )
                person_instance_IN = my_person_details.get( PersonDetails.PROP_NAME_PERSON_INSTANCE, None )
                name_IN = my_person_details.get( PersonDetails.PROP_NAME_PERSON_NAME, None )
                verbatim_name_IN = my_person_details.get_verbatim_name()
                lookup_name_IN = my_person_details.get_lookup_name()
                match_confidence_level_IN = my_person_details.get( PersonDetails.PROP_MAME_MATCH_CONFIDENCE_LEVEL, None )
                match_status_IN = my_person_details.get( PersonDetails.PROP_NAME_MATCH_STATUS, None )
                capture_method_IN = my_person_details.get( PersonDetails.PROP_NAME_CAPTURE_METHOD, None )

                # got an ID (check to see if update or insert)?
                my_id = self.id
                if ( ( my_id is not None ) and ( int( my_id ) > 0 ) ):

                    # no ID.  Insert.
                    is_insert = True

                else:

                    # there is an id.  Not an insert.
                    is_insert = False

                #-- END check to see if insert or update --#

                #------------------------------------------------------#
                # ==> article_data instance

                # value passed in?
                if ( article_data_instance_IN is not None ):

                    # store it.
                    self.article_data = article_data_instance_IN

                    # we need to save.
                    is_updated = True

                #-- END check to see if article_data instance passed in --#

                #------------------------------------------------------#
                # ==> person instance

                # instance passed in?
                if ( person_instance_IN ):

                    # sanity - was there an existing person?
                    if ( existing_person_instance is not None ):

                        # yes.  Compare IDs.
                        existing_person_id = existing_person_instance.id
                        new_person_id = person_instance_IN.id

                        # same IDs?
                        if ( existing_person_id != new_person_id ):

                            # not the same.  Store new person.
                            self.person = person_instance_IN

                            # we need to save.
                            is_updated = True

                        #-- END check to see if IDs are the same --#

                    else:

                        # no existing person...  This is not right,
                        #     but we're here and we have a person,
                        #     so save it.
                        self.person = person_instance_IN

                        # we need to save.
                        is_updated = True

                    #-- END check to see if existing person --#

                #-- END check to see if person instance passed in. --#

                #------------------------------------------------------#
                # ==> name

                # value passed in?
                if ( name_IN is not None ):

                    # has name string changed?
                    if ( name_IN != existing_name ):

                        # they are different.  Replace.
                        self.name = name_IN

                        # we need to save.
                        is_updated = True

                    #-- END check to see if updated name. --#

                #-- END check to see if name string changed. --#

                #------------------------------------------------------#
                # ==> verbatim_name

                # value passed in?
                if ( verbatim_name_IN is not None ):

                    # has verbatim name string changed?
                    if ( verbatim_name_IN != existing_verbatim_name ):

                        # they are different.  Replace.
                        self.verbatim_name = verbatim_name_IN

                        # we need to save.
                        is_updated = True

                    #-- END check to see if updated verbatim_name. --#

                #-- END check to see if verbatim name passed in. --#

                #------------------------------------------------------#
                # ==> lookup_name

                # value passed in?
                if ( lookup_name_IN is not None ):

                    # has lookup name string changed?
                    if ( lookup_name_IN != existing_lookup_name ):

                        # they are different.  Replace.
                        self.lookup_name = lookup_name_IN

                        # we need to save.
                        is_updated = True

                    #-- END check to see if updated lookup_name. --#

                #-- END check to see if lookup name passed in. --#

                #------------------------------------------------------#
                # ==> match_confidence_level

                # value passed in?
                if ( match_confidence_level_IN is not None ):

                    # store it.
                    self.match_confidence_level = match_confidence_level_IN

                    # we need to save.
                    is_updated = True

                #-- END check to see if match_confidence_level passed in --#

                #------------------------------------------------------#
                # ==> match_status

                # value passed in?
                if ( match_status_IN is not None ):

                    # store it.
                    self.match_status = match_status_IN

                    # we need to save.
                    is_updated = True

                #-- END check to see if match_status passed in --#

                #------------------------------------------------------#
                # ==> capture_method - moved up into update_from_person_details
                #     method in parent.

                # updated?
                if ( is_updated == True ):

                    # yes.  Do we save?
                    if ( do_save_IN == True ):

                        # yes.  Save.
                        self.save()

                    #-- END check to see if we save or not. --#

                #-- END check to see if changes made --#

            #-- END check to see if PersonDetails passed in. --#

        else:

            # errors in parent method.  Oh no.
            status_OUT = "In Article_Person." + me + "(): errors in call to parent method: " + status_OUT

        #-- END check to see if parent method executed OK --#

        return status_OUT

    #-- END method update_from_person_details() --#

#= END Article_Person Abstract Model ======================================================


# Article_Author model
class Article_Author( Article_Person ):

    AUTHOR_TYPE_TO_ID_MAP = {
        "staff" : 1,
        "editorial" : 2,
        "government" : 3,
        "business" : 4,
        "organization" : 5,
        "public" : 6,
        "other" : 7
    }

    AUTHOR_TYPE_CHOICES = (
        ( "staff", "News Staff" ),
        ( "editorial", "Editorial Staff" ),
        ( "government", "Government Official" ),
        ( "business", "Business Representative" ),
        ( "organization", "Other Organization Representative" ),
        ( "public", "Member of the Public" ),
        ( "other", "Other" )
    )

    author_type = models.CharField( max_length = 255, choices = AUTHOR_TYPE_CHOICES, default = "staff", blank = True, null = True )


    #----------------------------------------------------------------------
    # ! ==> class methods
    #----------------------------------------------------------------------


    @classmethod
    def make_deep_copy( cls, id_to_copy_IN, *args, **kwargs ):

        '''
        Accepts ID of Article_Author instance we want to make a deep copy of.
            First, loads record with ID passed in and makes a copy (by setting
            pk and id to None, then saving).  Then, goes through all the related
            sets and manually makes copies of all the related records, pointing
            them at the appropriate places in the new copied tree.

        - Article_Author deep copy
            - look at all relations that will need to be duplicated and re-referenced...
            - Article_Author
                - Alternate_Author_Match
        '''

        # return reference
        instance_OUT = None

        # declare variables
        me = "make_deep_copy"
        debug_message = ""
        my_logger_name = "context_text.models.Article_Author"
        is_id_valid = -1
        copy_from_article_author = None
        copy_to_article_author = None

        # declare variables - related Article_Author --> Alternate_Author_Match
        copy_me_alternate_author_match_qs = None
        copy_me_alternate_author_match_count = None
        alternate_author_match = None

        # got an ID?
        is_id_valid = IntegerHelper.is_valid_integer( id_to_copy_IN, must_be_greater_than_IN = 0 )
        if ( is_id_valid ):

            # DEBUG
            debug_message = "deep copying Article_Author record with ID = " + str( id_to_copy_IN )
            output_debug( debug_message, me, logger_name_IN = my_logger_name )

            # make and save copy.
            copy_from_article_author = Article_Author.objects.get( pk = id_to_copy_IN )
            copy_to_article_author = copy_from_article_author
            copy_to_article_author.id = None
            copy_to_article_author.pk = None
            copy_to_article_author.save()

            # reload copy_from_...
            copy_from_article_author = Article_Author.objects.get( pk = id_to_copy_IN )

            debug_message = "--> deep copying FROM Article_Author record with ID = " + str( id_to_copy_IN ) + " INTO Article_Author ID = " + str( copy_to_article_author.id )
            output_debug( debug_message, me, logger_name_IN = my_logger_name )

            '''
            - Article_Author deep copy
                - look at all relations that will need to be duplicated and re-referenced...
                - Alternate_Author_Match
            '''

            # Now, process children

            # ! ----> Alternate_Author_Match

            # get QuerySet and count()
            copy_me_alternate_author_match_qs = copy_from_article_author.alternate_author_match_set.all()
            copy_me_alternate_author_match_count = copy_me_alternate_author_match_qs.count()

            debug_message = "found " + str( copy_me_alternate_author_match_count ) + " Alternate_Author_Match instances."
            output_debug( debug_message, me, logger_name_IN = my_logger_name )

            # got anything?
            if ( copy_me_alternate_author_match_count > 0 ):

                # yes.  loop.
                for alternate_author_match in copy_me_alternate_author_match_qs:

                    debug_message = "----> deep copying FROM Alternate_Author_Match record with ID = " + str( alternate_author_match.id )
                    output_debug( debug_message, me, logger_name_IN = my_logger_name )

                    # None out id and pk.
                    alternate_author_match.id = None
                    alternate_author_match.pk = None

                    # change reference to Article_Data from copy_me to copy_to.
                    alternate_author_match.article_author = copy_to_article_author

                    # save.
                    alternate_author_match.save()

                    debug_message = "----> INTO Alternate_Author_Match ID = " + str( alternate_author_match.id )
                    output_debug( debug_message, me, logger_name_IN = my_logger_name )

                #-- END loop over Alternate_Author_Match --#

            #-- END check to see if any Alternate_Author_Match --#

        #-- END check to see if id passed in is valid --#

        instance_OUT = copy_to_article_author

        return instance_OUT

    #-- END class method make_deep_copy() --#


    #----------------------------------------------------------------------
    # ! ==> instance methods
    #----------------------------------------------------------------------


    def __str__( self ):

        # return reference
        string_OUT = ""

        if ( self.id ):

            string_OUT += str( self.id ) + " (AA) - "

        #-- END check to see if id --#

        if ( self.person is not None ):

            string_OUT += str( self.person.last_name ) + ", " + str( self.person.first_name ) + " ( id = " + str( self.person.id ) + "; type = " + str( self.author_type ) + "; capture_method = " + str( self.person.capture_method ) + " )"

        else:

            string_OUT += self.author_type

        #-- END check to see if we have a person. --#

        return string_OUT

    #-- END __str__() method --#


    def get_alternate_person_match_qs( self ):

        '''
        If there are any alternate matches for this person, returns a list of
            Match instances for each (each contains a reference to a "person"
            along with other information).  If none found, returns empty
            QuerySet.  If error returns None.  This method is abstract, so the child
            classes can each define how they deal with multiple matches and
            ambiguity.
        '''

        # return reference
        qs_OUT = None

        # retrieve QuerySet
        qs_OUT = self.alternate_author_match_set.all()

        # return the list
        return qs_OUT

    #-- END function get_alternate_person_match_qs() --#


    def process_alternate_matches( self ):

        '''
        If there are matches in the variable person_match_list, loops over them
           and deals with each appropriately.  person_match_list is a list of
           Person instances of people who might be a match for a given name
           string.  For each, this method:
           - checks to see if there is an Alternate_Author_Match present for
              that person.
           - if so, moves on.
           - if not, makes one.
        '''

        #print( "@@@@@@@@ In Article_Author process_alternate_matches() @@@@@@@@" )

        #define variables
        me = "Article_Author.process_alternate_matches"
        person_list = None
        person_count = -1
        current_person = ""
        alt_match_qs = None
        alt_match_count = -1
        alt_author_match = None
        exception_message = ""

        # get person list
        person_list = self.person_match_list

        # got anything?
        if ( person_list is not None ):

            # get count
            person_count = len( person_list )
            if ( person_count > 0 ):

                # loop
                for current_person in person_list:

                    # see if there is already an Alternate_Author_Match for the
                    #    Person.
                    alt_match_qs = self.alternate_author_match_set.filter( person = current_person )

                    # got one?
                    alt_match_count = alt_match_qs.count()
                    if ( alt_match_count == 0 ):

                        # no.  Make one.
                        alt_author_match = Alternate_Author_Match()
                        alt_author_match.article_author = self
                        alt_author_match.person = current_person
                        alt_author_match.save()

                    # got more than one (an error)?
                    elif ( alt_match_count > 1 ):

                        # more than one alternate subjects found for person.
                        exception_message = "In " + me + ": Multiple records found looking for alternate match record for person " + str( alternate_person ) + ", Article_Author: " + str( self ) + ".  Should never be more than one per person."
                        output_debug( "\n ! in " + me + " - ERROR - " + exception_message )
                        output_debug( "\n ! Article_Data:\n" + str( self.article_data ) )

                    #-- END check to see if match present. --#

                #-- END loop over persons --#

            #-- END check to see if anything in the list. --#

        #-- END check to see if list is present. --#

    #-- END function process_alternate_matches() --#


#= End Article_Author Model ======================================================


class Abstract_Alternate_Person_Match( models.Model ):

    #----------------------------------------------------------------------------
    # model fields and meta
    #----------------------------------------------------------------------------


    person = models.ForeignKey( Person, on_delete = models.CASCADE, blank = True, null = True )

    # time stamps.
    create_date = models.DateTimeField( auto_now_add = True, blank = True, null = True )
    last_modified = models.DateTimeField( auto_now = True, blank = True, null = True )


    # meta class so we know this is an abstract class.
    class Meta:

        abstract = True

    #-- END Meta class --#


    #----------------------------------------------------------------------
    # instance methods
    #----------------------------------------------------------------------


    def __str__( self ):

        # return reference
        string_OUT = ""

        # declare variables
        got_last_name = False

        # got id?
        if ( self.id ):

            string_OUT = str( self.id ) + " - "

        #-- END check for ID. --#

        # got associated person?  We'd better...
        if ( self.person ):

            string_OUT += " alternate = "

            # got ID?
            if ( self.person.id ):

                # yup.  Output it.
                string_OUT += "person " + str( self.person.id ) + " - "

            #-- END check to see if ID --#

            # got a last name?
            if ( ( self.person.last_name is not None ) and ( self.person.last_name != "" ) ):

                string_OUT += self.person.last_name
                got_last_name = True

            #-- END check to see if last name. --#

            # got a first name?
            if ( ( self.person.first_name is not None ) and ( self.person.first_name != "" ) ):

                if ( got_last_name == True ):

                    string_OUT += ", "

                #-- END check to see if last name preceded first name --#

                string_OUT += self.person.first_name

            #-- END check to see if first name. --#

        #-- END check to see if we have a person. --#

        return string_OUT

    #-- END __str__() method --#


#= End Abstract_Alternate_Person_Match Model ======================================================


# Alternate_Author_Match model
class Alternate_Author_Match( Abstract_Alternate_Person_Match ):

    #----------------------------------------------------------------------------
    # model fields and meta
    #----------------------------------------------------------------------------


    article_author = models.ForeignKey( Article_Author, on_delete = models.CASCADE, blank = True, null = True )

    '''
    # now in parent class.
    person = models.ForeignKey( Person, blank = True, null = True )

    # time stamps.
    create_date = models.DateTimeField( auto_now_add = True, blank = True, null = True )
    last_modified = models.DateTimeField( auto_now = True, blank = True, null = True )
    '''

    #----------------------------------------------------------------------
    # instance methods
    #----------------------------------------------------------------------


    def __str__( self ):

        # return reference
        string_OUT = ""

        # got id?
        if ( self.id ):

            string_OUT = str( self.id ) + " - "

        #-- END check for ID. --#

        if ( self.article_author ):

            string_OUT += str( aelf.article_author ) + " alternate = "

        #-- END check to see if article_author. --#

        # got associated person?  We'd better...
        if ( self.person ):

            string_OUT += self.person.last_name + ", " + self.person.first_name

        #-- END check to see if we have a person. --#

        return string_OUT

    #-- END __str__() method --#


#= End Alternate_Author_Match Model ======================================================


# Article_Subject model
class Article_Subject( Article_Person ):

    PARAM_SOURCE_CAPACITY_INCLUDE_LIST = 'include_capacities'
    PARAM_SOURCE_CAPACITY_EXCLUDE_LIST = 'exclude_capacities'
    PARAM_SOURCE_CONTACT_TYPE_INCLUDE_LIST = 'include_source_contact_types'

    # subjet types
    SUBJECT_TYPE_MENTIONED = PersonDetails.SUBJECT_TYPE_MENTIONED
    SUBJECT_TYPE_QUOTED = PersonDetails.SUBJECT_TYPE_QUOTED

    SUBJECT_TYPE_CHOICES = (
        ( SUBJECT_TYPE_MENTIONED, "Subject Mentioned" ),
        ( SUBJECT_TYPE_QUOTED, "Source Quoted" ),
    )

    # Source type stuff
    SOURCE_TYPE_ANONYMOUS = 'anonymous'
    SOURCE_TYPE_INDIVIDUAL = 'individual'
    SOURCE_TYPE_ORGANIZATION = 'organization'
    SOURCE_TYPE_DOCUMENT = 'document'
    SOURCE_TYPE_OTHER = 'other'

    SOURCE_TYPE_TO_ID_MAP = {
        SOURCE_TYPE_ANONYMOUS : 1,
        SOURCE_TYPE_INDIVIDUAL : 2,
        SOURCE_TYPE_ORGANIZATION : 3,
        SOURCE_TYPE_DOCUMENT : 4,
        SOURCE_TYPE_OTHER : 5
    }

    SOURCE_TYPE_CHOICES = (
        ( SOURCE_TYPE_ANONYMOUS, "Anonymous/Unnamed" ),
        ( SOURCE_TYPE_INDIVIDUAL, "Individual Person" ),
        ( SOURCE_TYPE_ORGANIZATION, "Organization" ),
        ( SOURCE_TYPE_DOCUMENT, "Document" ),
        ( SOURCE_TYPE_OTHER, "Other" )
    )

    # Source contact type stuff
    SOURCE_CONTACT_TYPE_DIRECT = 'direct'
    SOURCE_CONTACT_TYPE_EVENT = 'event'
    SOURCE_CONTACT_TYPE_PAST_QUOTES = 'past_quotes'
    SOURCE_CONTACT_TYPE_DOCUMENT = 'document'
    SOURCE_CONTACT_TYPE_OTHER = 'other'

    SOURCE_CONTACT_TYPE_TO_ID_MAP = {
        SOURCE_CONTACT_TYPE_DIRECT : 1,
        SOURCE_CONTACT_TYPE_EVENT : 2,
        SOURCE_CONTACT_TYPE_PAST_QUOTES : 3,
        SOURCE_CONTACT_TYPE_DOCUMENT : 4,
        SOURCE_CONTACT_TYPE_OTHER : 5
    }

    SOURCE_CONTACT_TYPE_CHOICES = (
        ( SOURCE_CONTACT_TYPE_DIRECT, "Direct contact" ),
        ( SOURCE_CONTACT_TYPE_EVENT, "Press conference/event" ),
        ( SOURCE_CONTACT_TYPE_PAST_QUOTES, "Past quotes/statements" ),
        ( SOURCE_CONTACT_TYPE_DOCUMENT, "Press release/document" ),
        ( SOURCE_CONTACT_TYPE_OTHER, "Other" )
    )

    # Source capacity stuff
    SOURCE_CAPACITY_TO_ID_MAP = {
        "government" : 1,
        "police" : 2,
        #"legal" : "?",
        "business" : 3,
        "labor" : 4,
        "education" : 5,
        "organization" : 6,
        "expert" : 7,
        "individual" : 8,
        "other" : 9
    }

    SOURCE_CAPACITY_CHOICES = (
        ( "government", "Government Source" ),
        ( "police", "Police Source" ),
        #( "legal", "Legal Source" ),
        ( "business", "Business Source" ),
        ( "labor", "Labor Source" ),
        ( "education", "Education Source" ),
        ( "organization", "Other Organization Source" ),
        ( "expert", "Expert Opinion" ),
        ( "individual", "Personal Opinion" ),
        ( "other", "Other" )
    )

    # localness stuff
    LOCALNESS_TO_ID_MAP = {
        "none" : 1,
        "local" : 2,
        #"regional" : "?",
        "state" : 3,
        "national" : 4,
        "international" : 5,
        "other" : 6
    }

    LOCALNESS_CHOICES = (
        ( "none", "None" ),
        ( "local", "Local" ),
        #( "regional", "Regional" ),
        ( "state", "State" ),
        ( "national", "National" ),
        ( "international", "International" ),
        ( "other", "Other" )
    )

    source_type = models.CharField( max_length = 255, choices = SOURCE_TYPE_CHOICES, blank = True, null = True )
    subject_type = models.CharField( max_length = 255, choices = SUBJECT_TYPE_CHOICES, blank = True, null = True )
    # moved up to Article_Person (so also over to Article_Author).
    #title = models.CharField( max_length = 255, blank = True, null = True )
    #more_title = models.TextField( blank = True, null = True )
    document = models.ForeignKey( Document, on_delete = models.SET_NULL, blank = True, null = True )
    topics = models.ManyToManyField( Topic, blank = True )
    source_contact_type = models.CharField( max_length = 255, choices = SOURCE_CONTACT_TYPE_CHOICES, blank = True, null = True )
    source_capacity = models.CharField( max_length = 255, choices = SOURCE_CAPACITY_CHOICES, blank = True, null = True )
    #count_direct_quote = models.IntegerField( "Count direct quotes", default = 0 )
    #count_indirect_quote = models.IntegerField( "Count indirect quotes", default = 0 )
    #count_from_press_release = models.IntegerField( "Count quotes from press release", default = 0 )
    #count_spoke_at_event = models.IntegerField( "Count quotes from public appearances", default = 0 )
    #count_other_use_of_source = models.IntegerField( "Count other uses of source", default = 0 )
    localness = models.CharField( max_length = 255, choices = LOCALNESS_CHOICES, blank = True, null = True )

    # moved up to parent
    #notes = models.TextField( blank = True, null = True )

    # fields to track locations of data this coding was based on within
    #    article.  References are based on results of ParsedArticle.parse().
    #attribution_verb_word_index = models.IntegerField( blank = True, null = True, default = 0 )
    #attribution_verb_word_number = models.IntegerField( blank = True, null = True, default = 0 )
    #attribution_paragraph_number = models.IntegerField( blank = True, null = True, default = 0 )
    #attribution_speaker_name_string = models.TextField( blank = True, null = True )
    #is_speaker_name_pronoun = models.BooleanField( default = False )
    #attribution_speaker_name_index_range = models.CharField( max_length = 255, blank = True, null = True )
    #attribution_speaker_name_word_range = models.CharField( max_length = 255, blank = True, null = True )

    # field to store how source was captured. - parent
    #capture_method = models.CharField( max_length = 255, blank = True, null = True )


    #----------------------------------------------------------------------
    # ! ==> class methods
    #----------------------------------------------------------------------


    @classmethod
    def make_deep_copy( cls, id_to_copy_IN, *args, **kwargs ):

        '''
        Accepts ID of Article_Author instance we want to make a deep copy of.
            First, loads record with ID passed in and makes a copy (by setting
            pk and id to None, then saving).  Then, goes through all the related
            sets and manually makes copies of all the related records, pointing
            them at the appropriate places in the new copied tree.

        - Article_Subject deep copy
            - look at all relations that will need to be duplicated and re-referenced...
            - Article_Subject
                - Alternate_Subject_Match
                - Article_Subject_Mention
                - Article_Subject_Quotation
                - Subject_Organization
        '''

        # return reference
        instance_OUT = None

        # declare variables
        me = "make_deep_copy"
        debug_message = ""
        my_logger_name = "context_text.models.Article_Subject"
        is_id_valid = -1
        copy_from_article_subject = None
        copy_to_article_subject = None

        # declare variables - related Alternate_Subject_Match
        copy_me_alternate_subject_match_qs = None
        copy_me_alternate_subject_match_count = None
        alternate_subject_match = None

        # declare variables - related Article_Subject_Mention
        copy_me_article_subject_mention_qs = None
        copy_me_article_subject_mention_count = None
        article_subject_mention = None

        # declare variables - related Article_Subject_Quotation
        copy_me_article_subject_quotation_qs = None
        copy_me_article_subject_quotation_count = None
        article_subject_quotation = None

        # declare variables - related Subject_Organization
        copy_me_subject_organization_qs = None
        copy_me_subject_organization_count = None
        subject_organization = None

        # got an ID?
        is_id_valid = IntegerHelper.is_valid_integer( id_to_copy_IN, must_be_greater_than_IN = 0 )
        if ( is_id_valid ):

            # DEBUG
            debug_message = "deep copying Article_Subject record with ID = " + str( id_to_copy_IN )
            output_debug( debug_message, me, logger_name_IN = my_logger_name )

            # make and save copy.
            copy_from_article_subject = Article_Subject.objects.get( pk = id_to_copy_IN )
            copy_to_article_subject = copy_from_article_subject
            copy_to_article_subject.id = None
            copy_to_article_subject.pk = None
            copy_to_article_subject.save()

            # reload copy_me.
            copy_from_article_subject = Article_Subject.objects.get( pk = id_to_copy_IN )

            debug_message = "--> deep copying FROM Article_Subject record with ID = " + str( id_to_copy_IN ) + " INTO Article_Subject ID = " + str( copy_to_article_subject.id )
            output_debug( debug_message, me, logger_name_IN = my_logger_name )

            '''
            - Article_Subject deep copy
                - look at all relations that will need to be duplicated and re-referenced...
                - Article_Subject
                    - Alternate_Subject_Match
                    - Article_Subject_Mention
                    - Article_Subject_Quotation
                    - Subject_Organization
            '''

            # Now, process children

            # ! ----> ManyToMany - topics
            DjangoModelHelper.copy_m2m_values( "topics", copy_from_article_subject, copy_to_article_subject )

            # ! ----> Alternate_Subject_Match

            # get QuerySet and count()
            copy_me_alternate_subject_match_qs = copy_from_article_subject.alternate_subject_match_set.all()
            copy_me_alternate_subject_match_count = copy_me_alternate_subject_match_qs.count()

            debug_message = "found " + str( copy_me_alternate_subject_match_count ) + " Alternate_Subject_Match instances."
            output_debug( debug_message, me, logger_name_IN = my_logger_name )

            # got anything?
            if ( copy_me_alternate_subject_match_count > 0 ):

                # yes.  loop.
                for alternate_subject_match in copy_me_alternate_subject_match_qs:

                    debug_message = "----> deep copying FROM Alternate_Subject_Match record with ID = " + str( alternate_subject_match.id )
                    output_debug( debug_message, me, logger_name_IN = my_logger_name )

                    # None out id and pk.
                    alternate_subject_match.id = None
                    alternate_subject_match.pk = None

                    # change reference to Article_Data from copy_me to copy_to.
                    alternate_subject_match.article_subject = copy_to_article_subject

                    # save.
                    alternate_subject_match.save()

                    debug_message = "----> INTO Alternate_Subject_Match ID = " + str( alternate_subject_match.id )
                    output_debug( debug_message, me, logger_name_IN = my_logger_name )

                #-- END loop over Alternate_Subject_Match --#

            #-- END check to see if any Alternate_Subject_Match --#


            # ! ----> Article_Subject_Mention

            # get QuerySet and count()
            copy_me_article_subject_mention_qs = copy_from_article_subject.article_subject_mention_set.all()
            copy_me_article_subject_mention_count = copy_me_article_subject_mention_qs.count()

            debug_message = "found " + str( copy_me_article_subject_mention_count ) + " Article_Subject_Mention instances."
            output_debug( debug_message, me, logger_name_IN = my_logger_name )

            # got anything?
            if ( copy_me_article_subject_mention_count > 0 ):

                # yes.  loop.
                for article_subject_mention in copy_me_article_subject_mention_qs:

                    debug_message = "----> deep copying FROM Article_Subject_Mention record with ID = " + str( article_subject_mention.id )
                    output_debug( debug_message, me, logger_name_IN = my_logger_name )

                    # None out id and pk.
                    article_subject_mention.id = None
                    article_subject_mention.pk = None

                    # change reference to Article_Data from copy_me to copy_to.
                    article_subject_mention.article_subject = copy_to_article_subject

                    # save.
                    article_subject_mention.save()

                    debug_message = "----> INTO Article_Subject_Mention ID = " + str( article_subject_mention.id )
                    output_debug( debug_message, me, logger_name_IN = my_logger_name )

                #-- END loop over Article_Subject_Mention --#

            #-- END check to see if any Article_Subject_Mention --#


            # ! ----> Article_Subject_Quotation

            # get QuerySet and count()
            copy_me_article_subject_quotation_qs = copy_from_article_subject.article_subject_quotation_set.all()
            copy_me_article_subject_quotation_count = copy_me_article_subject_quotation_qs.count()

            debug_message = "found " + str( copy_me_article_subject_quotation_count ) + " Article_Subject_Quotation instances."
            output_debug( debug_message, me, logger_name_IN = my_logger_name )

            # got anything?
            if ( copy_me_article_subject_quotation_count > 0 ):

                # yes.  loop.
                for article_subject_quotation in copy_me_article_subject_quotation_qs:

                    debug_message = "----> deep copying FROM Article_Subject_Quotation record with ID = " + str( article_subject_quotation.id )
                    output_debug( debug_message, me, logger_name_IN = my_logger_name )

                    # None out id and pk.
                    article_subject_quotation.id = None
                    article_subject_quotation.pk = None

                    # change reference to Article_Data from copy_me to copy_to.
                    article_subject_quotation.article_subject = copy_to_article_subject

                    # save.
                    article_subject_quotation.save()

                    debug_message = "----> INTO Article_Subject_Quotation ID = " + str( article_subject_quotation.id )
                    output_debug( debug_message, me, logger_name_IN = my_logger_name )

                #-- END loop over Article_Subject_Quotation --#

            #-- END check to see if any Article_Subject_Quotation --#

            # ! ----> Subject_Organization

            # get QuerySet and count()
            copy_me_subject_organization_qs = copy_from_article_subject.subject_organization_set.all()
            copy_me_subject_organization_count = copy_me_subject_organization_qs.count()

            debug_message = "found " + str( copy_me_subject_organization_count ) + " Subject_Organization instances."
            output_debug( debug_message, me, logger_name_IN = my_logger_name )

            # got anything?
            if ( copy_me_subject_organization_count > 0 ):

                # yes.  loop.
                for subject_organization in copy_me_subject_organization_qs:

                    debug_message = "----> deep copying FROM Subject_Organization record with ID = " + str( subject_organization.id )
                    output_debug( debug_message, me, logger_name_IN = my_logger_name )

                    # None out id and pk.
                    subject_organization.id = None
                    subject_organization.pk = None

                    # change reference to Article_Data from copy_me to copy_to.
                    subject_organization.article_subject = copy_to_article_subject

                    # save.
                    subject_organization.save()

                    debug_message = "----> INTO Subject_Organization ID = " + str( subject_organization.id )
                    output_debug( debug_message, me, logger_name_IN = my_logger_name )

                #-- END loop over Subject_Organization --#

            #-- END check to see if any Subject_Organization --#

        #-- END check to see if id passed in is valid --#

        instance_OUT = copy_to_article_subject

        return instance_OUT

    #-- END class method make_deep_copy() --#


    #----------------------------------------------------------------------
    # ! ==> instance methods
    #----------------------------------------------------------------------

    def __str__( self ):

        # return reference
        string_OUT = ''

        # declare variables
        temp_string = ""
        separator = ""

        if ( self.id ):

            string_OUT += str( self.id ) + " (AS) - "

        #-- END check to see if ID --#

        if ( self.source_type == "individual" ):

            if ( self.person is not None ):

                # last name
                temp_string = self.person.last_name
                if ( ( temp_string is not None ) and ( temp_string != "" ) ):

                    string_OUT += temp_string
                    separator = ", "

                #-- END last name --#

                # first name
                temp_string = self.person.first_name
                if ( ( temp_string is not None ) and ( temp_string != "" ) ):

                    string_OUT += separator + temp_string
                    separator = ", "

                #-- END first name --#

                # there will be an ID, and fine to just output "None" if no
                #    capture_method.
                string_OUT += " ( id = " + str( self.person.id ) + "; capture_method = " + str( self.person.capture_method ) + " )"

            else:

                if ( self.title != '' ):

                    string_OUT += self.title

                else:

                    string_OUT += "individual"

                #-- END check to see if title --#

            #-- END check to see if person --#

        elif ( self.source_type == "organization" ):

            if ( self.organization is not None ):

                string_OUT += self.organization.name

            else:

                string_OUT += self.title

            #-- END check to see if organization --#

        elif ( self.source_type == "document" ):

            if ( self.document is not None ):

                string_OUT += self.document.name

            else:

                string_OUT += self.notes

            #-- END check to see if Document --#

        #elif ( self.source_type == "anonymous" ):
        #    string_OUT =

        #-- END check to see what type of source --#

        string_OUT = string_OUT + " (" + str( self.subject_type ) + "; " + str( self.source_type ) + ")"

        return string_OUT

    #-- END method __str__() --#


    def get_alternate_person_match_qs( self ):

        '''
        If there are any alternate matches for this person, returns a list of
            Match instances for each (each contains a reference to a "person"
            along with other information).  If none found, returns empty
            QuerySet.  If error returns None.  This method is abstract, so the child
            classes can each define how they deal with multiple matches and
            ambiguity.
        '''

        # return reference
        qs_OUT = None

        # retrieve QuerySet
        qs_OUT = self.alternate_subject_match_set.all()

        # return the list
        return qs_OUT

    #-- END function get_alternate_person_match_qs() --#


    def is_connected( self, param_dict_IN = None ):

        """
            Method: is_connected()

            Purpose: accepts a parameter dictionary, examines its categorization
               to determine if the source is eligible to be classified as
               "connected" to the authors of the story.  If "connected", returns
               True.  If not, returns False.  By default, "Connected" = source
               of type "individual" with contact type of "direct" or "event".
               The parameter dictionary allows one to extend the filtering
               options here without changing the method signature.  First
               add-ons are include and exclude lists for source capacity.
               Eventually we should move everything that is in this method into
               params, so defaults aren't set in code.  For now, just need it to
               work.

            Params:
            - self - source whose connectedness we need to check.
            - contact_type_in_list_IN - list of contact types that are OK to be considered "connected".  If not specified, all are OK.
            - capacity_in_list_IN
            - capacity_not_in_list_IN

            Returns:
            - boolean - If "connected", returns True.  If not, returns False.
        """

        # return reference
        is_connected_OUT = True

        # declare variables
        current_source_type = ''
        current_source_contact_type = ''
        current_source_capacity = ''
        contact_type_in_list_IN = None
        capacity_in_list_IN = None
        capacity_not_in_list_IN = None

        # first, call parent method (takes care of checking to see if there is a
        #    person in the person reference).
        is_connected_OUT = super( Article_Subject, self ).is_connected( param_dict_IN )

        # Now, check the source type.
        current_source_type = self.source_type

        # correct source type?
        if ( current_source_type != Article_Subject.SOURCE_TYPE_INDIVIDUAL ):

            # no.  Set output flag to false.
            is_connected_OUT = False

        #-- END check of source type --#

        # Got a param dict?
        if ( param_dict_IN is not None ):

            # we have a parameter dictionary - anything in it related to us?

            # Do we have a list of source contact types that we are to allow?
            if Article_Subject.PARAM_SOURCE_CONTACT_TYPE_INCLUDE_LIST in param_dict_IN:

                # first, retrieve the value for the key
                contact_type_in_list_IN = param_dict_IN.get( Article_Subject.PARAM_SOURCE_CONTACT_TYPE_INCLUDE_LIST, None )

                # is it populated and does it contain at least one thing?
                if ( ( contact_type_in_list_IN is not None ) and ( len( contact_type_in_list_IN ) > 0 ) ):

                    # it is populated.  Is the current source contact type in
                    #    the list?
                    current_source_contact_type = self.source_contact_type
                    if current_source_contact_type not in contact_type_in_list_IN:

                        # not in include list, so not connected.
                        is_connected_OUT = False

                    #-- END check to see if contact type is in our list. --#

                else:

                    # nothing in list.  Fall back to default - Any is fine!
                    pass

                    # old default: Only acceptable contact types were:
                    # - Article_Subject.SOURCE_CONTACT_TYPE_DIRECT
                    # - Article_Subject.SOURCE_CONTACT_TYPE_EVENT
                    # if other than those, not connected.

                #-- END check to see if list is populated.

            #-- END check to see if source contact types include list --#

            # Do we have list of source capacities to either
            #    include or exclude?
            if Article_Subject.PARAM_SOURCE_CAPACITY_INCLUDE_LIST in param_dict_IN:

                # get include list.
                capacity_in_list_IN = param_dict_IN[ Article_Subject.PARAM_SOURCE_CAPACITY_INCLUDE_LIST ]

                # see if our capacity is in the include list.
                current_source_capacity = self.source_capacity

                if current_source_capacity not in capacity_in_list_IN:

                    # not in include list, so not connected.
                    is_connected_OUT = False

                #-- END check to see if we fail the test. --#

            #-- END check to see if we have an include list. --#

            if Article_Subject.PARAM_SOURCE_CAPACITY_EXCLUDE_LIST in param_dict_IN:

                # get include list.
                capacity_not_in_list_IN = param_dict_IN[ Article_Subject.PARAM_SOURCE_CAPACITY_EXCLUDE_LIST ]

                # see if our capacity is in the include list.
                current_source_capacity = self.source_capacity

                if current_source_capacity in capacity_not_in_list_IN:

                    # capacity is in the exclude list, so not connected.
                    is_connected_OUT = False

                #-- END check to see if we fail the test. --#

            #-- END check to see if we have an exclude list. --#

        #-- END check to see if we have params passed in. --#

        return is_connected_OUT

    #-- END method is_connected() --#


    def process_alternate_matches( self ):

        '''
        If there are matches in the variable person_match_list, loops over them
           and deals with each appropriately.  person_match_list is a list of
           Person instances of people who might be a match for a given name
           string.  For each, this method:
           - checks to see if there is an Alternate_Subject_Match present for
              that person.
           - if so, moves on.
           - if not, makes one.
        '''

        #output_debug( "&&&&&&&& In Article_Subject process_alternate_matches() &&&&&&&&" )

        # define variables
        me = "Article_Subject.process_alternate_matches"
        person_list = None
        person_count = -1
        current_person = ""
        alt_match_qs = None
        alt_match_count = -1
        alt_subject_match = None
        exception_message = ""

        # get person list
        person_list = self.person_match_list

        # got anything?
        if ( person_list is not None ):

            # get count
            person_count = len( person_list )
            if ( person_count > 0 ):

                # loop
                for current_person in person_list:

                    # see if there is already an Alternate_Subject_Match for the
                    #    Person.
                    alt_match_qs = self.alternate_subject_match_set.filter( person = current_person )

                    # got one?
                    alt_match_count = alt_match_qs.count()
                    if ( alt_match_count == 0 ):

                        # no.  Make one.
                        alt_subject_match = Alternate_Subject_Match()
                        alt_subject_match.article_subject = self
                        alt_subject_match.person = current_person
                        alt_subject_match.save()

                    # got more than one (an error)?
                    elif ( alt_match_count > 1 ):

                        # more than one alternate subjects found for person.
                        exception_message = "In " + me + ": Multiple records found looking for alternate match record for person " + str( alternate_person ) + ", Article_Subject: " + str( self ) + ".  Should never be more than one per person."
                        output_debug( "\n ! in " + me + " - ERROR - " + exception_message )
                        output_debug( "\n ! Article_Data:\n" + str( self.article_data ) )

                    #-- END check to see if match present. --#

                #-- END loop over persons --#

            #-- END check to see if anything in the list. --#

        #-- END check to see if list is present. --#

    #-- END function process_alternate_matches() --#


#= End Article_Subject Model ======================================================


# Alternate_Subject_Match model
class Alternate_Subject_Match( Abstract_Alternate_Person_Match ):

    #----------------------------------------------------------------------------
    # model fields and meta
    #----------------------------------------------------------------------------


    article_subject = models.ForeignKey( Article_Subject, on_delete = models.CASCADE, blank = True, null = True )

    '''
    # in parent class now.
    person = models.ForeignKey( Person, blank = True, null = True )

    # time stamps.
    create_date = models.DateTimeField( auto_now_add = True, blank = True, null = True )
    last_modified = models.DateTimeField( auto_now = True, blank = True, null = True )
    '''


    #----------------------------------------------------------------------
    # instance methods
    #----------------------------------------------------------------------


    def __str__( self ):

        # return reference
        string_OUT = ""

        # declare variables
        got_last_name = False

        # got id?
        if ( self.id ):

            string_OUT = str( self.id ) + " - "

        #-- END check for ID. --#

        if ( self.article_subject ):

            string_OUT += str( self.article_subject )

        #-- END check to see if article_subject. --#

        # got associated person?  We'd better...
        if ( self.person ):

            string_OUT += " alternate = "

            # got ID?
            if ( self.person.id ):

                # yup.  Output it.
                string_OUT += "person " + str( self.person.id ) + " - "

            #-- END check to see if ID --#

            # got a last name?
            if ( ( self.person.last_name is not None ) and ( self.person.last_name != "" ) ):

                string_OUT += self.person.last_name
                got_last_name = True

            #-- END check to see if last name. --#

            # got a first name?
            if ( ( self.person.first_name is not None ) and ( self.person.first_name != "" ) ):

                if ( got_last_name == True ):

                    string_OUT += ", "

                #-- END check to see if last name preceded first name --#

                string_OUT += self.person.first_name

            #-- END check to see if first name. --#

        #-- END check to see if we have a person. --#

        return string_OUT

    #-- END __str__() method --#


#= End Alternate_Subject_Match Model ======================================================


# Abstract_Selected_Text model
class Abstract_Selected_Text( models.Model ):

    '''
    This abstract class is used to store text that has been selected from inside
       a larger text document.  It holds details on the text found, the text
       around it, and the method used to single out the text.  Can be extended to
       reference a Foreign Key of the container in which this text was found.
    '''


    #----------------------------------------------------------------------------
    # static/CONSTANTS-ish
    #----------------------------------------------------------------------------


    HAS_ERROR_FIELD_NAME_TO_ERROR_VALUE_MAP = {}
    HAS_ERROR_FIELD_NAME_TO_ERROR_VALUE_MAP[ "value_index" ] = ( -1, None )
    HAS_ERROR_FIELD_NAME_TO_ERROR_VALUE_MAP[ "canonical_index" ] = ( -1, None )
    HAS_ERROR_FIELD_NAME_TO_ERROR_VALUE_MAP[ "value_word_number_start" ] = ( -1, None )
    HAS_ERROR_FIELD_NAME_TO_ERROR_VALUE_MAP[ "value_word_number_end" ] = ( -1, None )
    HAS_ERROR_FIELD_NAME_TO_ERROR_VALUE_MAP[ "paragraph_number" ] = ( -1, None )


    #----------------------------------------------------------------------------
    # model fields and meta
    #----------------------------------------------------------------------------


    # basics - value, text before and after the value, length and index of value.
    value = models.TextField( blank = True, null = True )
    value_in_context = models.TextField( blank = True, null = True )
    value_index = models.IntegerField( blank = True, null = True, default = 0 )
    value_length = models.IntegerField( blank = True, null = True, default = 0 )
    canonical_index = models.IntegerField( blank = True, null = True, default = 0 )
    value_word_number_start = models.IntegerField( blank = True, null = True, default = 0 )
    value_word_number_end = models.IntegerField( blank = True, null = True, default = 0 )
    paragraph_number = models.IntegerField( blank = True, null = True, default = 0 )
    context_before = models.TextField( blank = True, null = True )
    context_after = models.TextField( blank = True, null = True )

    # field to store how source was captured.
    capture_method = models.CharField( max_length = 255, blank = True, null = True )

    # additional identifying information
    uuid = models.TextField( blank = True, null = True )
    uuid_name = models.CharField( max_length = 255, null = True, blank = True )

    # other notes.
    notes = models.TextField( blank = True, null = True )

    # time stamps.
    create_date = models.DateTimeField( auto_now_add = True )
    last_modified = models.DateTimeField( auto_now = True )

    # meta class so we know this is an abstract class.
    class Meta:

        abstract = True
        ordering = [ 'paragraph_number', 'last_modified', 'create_date' ]

    #-- END inner class Meta --#


    #----------------------------------------------------------------------
    # instance methods
    #----------------------------------------------------------------------


    def __init__( self, *args, **kwargs ):

        # call parent __init()__ first.
        super( Abstract_Selected_Text, self ).__init__( *args, **kwargs )

    #-- END method __init__() --#


    def __str__( self ):

        # return reference
        string_OUT = ""

        # got id?
        if ( self.id ):

            string_OUT = str( self.id ) + " - "

        #-- END check for ID. --#

        if ( self.value_offset ):

            string_OUT += " ( index: " + str( self.value_offset ) + " ) : "

        #-- END check to see if value_offset. --#

        # got associated text?...
        if ( self.value ):

            string_OUT += self.value

        #-- END check to see if we have a value. --#

        return string_OUT

    #-- END __str__() method --#


    def build_details_list( self ):

        '''
        Pulls together details on this selected text, one item to a list
           element.  If present in instance, includes:
           - graf - paragraph_number
           - from word - starting word number
           - to word - ending word number
           - index - start character index in plain-text.
        '''

        # return reference
        list_OUT = []

        if ( self.paragraph_number ):

            list_OUT.append( "graf: " + str( self.paragraph_number ) )

        #-- END check to see if paragraph_number --#

        if ( self.value_word_number_start ):

            list_OUT.append( "from word: " + str( self.value_word_number_start ) )

        #-- END check to see if value_word_number_start --#

        if ( self.value_word_number_end ):

            list_OUT.append( "to word: " + str( self.value_word_number_end ) )

        #-- END check to see if value_word_number_end --#

        if ( self.value_index ):

            list_OUT.append( "index: " + str( self.value_index ) )

        #-- END check to see if value_index --#

        return list_OUT

    #-- END method build_details_list --#


    def get_error_list( self ):

        '''
        Checks fields within where a certain value is an error (specified in
            self.HAS_ERROR_FIELD_NAME_TO_ERROR_VALUE_MAP).  For each field,
            checks the value in the current instance.  If that value is equal
            to the error condition, adds the field name to the error list.
            Returns the error list.
        '''

        # return reference
        error_list_OUT = []

        # declare variables
        current_field_name = None
        current_error_value_list = None
        current_value = None

        # loop over HAS_ERROR_FIELD_NAME_LIST
        for current_field_name in six.iterkeys( self.HAS_ERROR_FIELD_NAME_TO_ERROR_VALUE_MAP ):

            # get error value
            current_error_value_list = self.HAS_ERROR_FIELD_NAME_TO_ERROR_VALUE_MAP.get( current_field_name, [] )

            # get value.
            current_value = getattr( self, current_field_name, None )

            # got a value?
            if ( current_value in current_error_value_list ):

                # value is in error value list - add field to error list.
                error_list_OUT.append( current_field_name )

            #-- END check to see if value is in error list. --#

        #-- END end loop over fields that can has_error. --#

        return error_list_OUT

    #-- END method get_error_list() --#


    def has_error( self ):

        '''
        Checks fields within where a certain value is an error (specified in
            self.HAS_ERROR_FIELD_NAME_TO_ERROR_VALUE_MAP).  For each field,
            checks the value in the current instance.  If that value is equal
            to the error condition, adds the field name to the error list.
            Returns the error list.
        '''

        # return reference
        has_error_OUT = False

        # declare variables
        me = "has_error"
        error_list = []

        # call get_error_list()
        error_list = self.get_error_list()

        # got any errors?
        if( error_list is not None ):

            # anything in it?
            if ( len( error_list ) > 0 ):

                # yes.  we has_error.
                has_error_OUT = True

            else:

                # no - we do not has_error.
                has_error_OUT = False

        else:

            # error list is None - an error getting errors...  Do we has_error?

            # ...yes...?
            has_error_OUT = True
            print( "ERROR in " + me + "(): get_error_list() returned None.  Should have been at least an empty list." )

        #-- END check to see if list returned. --#

        return has_error_OUT

    #-- END method has_error() --#


#-- END abstract class Abstract_Selected_Text --#


# AbstractArticleText model
class AbstractSelectedArticleText( Abstract_Selected_Text ):

    #----------------------------------------------------------------------------
    # model fields and meta
    #----------------------------------------------------------------------------

    # associated article
    article = models.ForeignKey( Article, on_delete = models.CASCADE, blank = True, null = True )

    # optional - who captured this at the article level?
    article_data = models.ForeignKey( Article_Data, on_delete = models.CASCADE, blank = True, null = True )

    # work log reference.
    work_log = models.ForeignKey( Work_Log, on_delete = models.SET_NULL, blank = True, null = True )

    # tags!
    tags = TaggableManager( blank = True )

    # Meta-data for this class.
    class Meta:

        abstract = True

    #-- END class Meta --#


    #----------------------------------------------------------------------
    # instance methods
    #----------------------------------------------------------------------


    def __init__( self, *args, **kwargs ):

        # call parent __init()__ first.
        super( AbstractSelectedArticleText, self ).__init__( *args, **kwargs )

    #-- END method __init__() --#


    def __str__( self ):

        # return reference
        string_OUT = ""

        # declare variables
        details_list = []

        # got id?
        if ( self.id ):

            string_OUT = str( self.id )

        #-- END check for ID. --#

        if ( self.publication ):

            string_OUT += " - Pub. ID: {}" + str( self.publication.id )

        #-- END check to see if publication. --#

        # got associated text?...
        if ( self.value ):

            string_OUT += ": {}".format( self.value )

        #-- END check to see if we have text. --#

        return string_OUT

    #-- END __str__() method --#

#= End AbstractSelectedArticleText Model ======================================================


# Article_Subject_Mention model
class Article_Subject_Mention( Abstract_Selected_Text ):

    #----------------------------------------------------------------------------
    # model fields and meta
    #----------------------------------------------------------------------------


    # subject in a given article whom this quote belongs to.
    article_subject = models.ForeignKey( Article_Subject, on_delete = models.CASCADE, blank = True, null = True )

    # is name a pronoun?
    is_speaker_name_pronoun = models.BooleanField( default = False )


    #----------------------------------------------------------------------
    # instance methods
    #----------------------------------------------------------------------


    def __str__( self ):

        # return reference
        string_OUT = ""

        # declare variables
        details_list = []

        # got id?
        if ( self.id ):

            string_OUT = str( self.id ) + " - "

        #-- END check for ID. --#

        details_list = self.build_details_list()

        # got anything in list?
        if ( len( details_list ) > 0 ):

            string_OUT += " ( " + "; ".join( details_list ) + " ) - "

        #-- END check to see if got anything in list --#

        if ( self.article_subject ):

            string_OUT += str( self.article_subject ) + " : "

        #-- END check to see if article_subject. --#

        # got associated text?...
        if ( self.value_in_context ):

            string_OUT += self.value_in_context

        elif ( self.value ):

            string_OUT += self.value

        #-- END check to see if we have a quotation. --#

        return string_OUT

    #-- END __str__() method --#

#= End Article_Subject_Mention Model ======================================================


# Article_Subject_Quotation model
class Article_Subject_Quotation( Abstract_Selected_Text ):

    #----------------------------------------------------------------------------
    # model fields and meta
    #----------------------------------------------------------------------------


    # subject in a given article whom this quote belongs to.
    article_subject = models.ForeignKey( Article_Subject, on_delete = models.CASCADE, blank = True, null = True )

    # value_with_attribution
    value_with_attribution = models.TextField( blank = True, null = True )

    # fields to track locations of data this coding was based on within
    #    article.  References are based on results of ParsedArticle.parse().
    attribution_verb_word_index = models.IntegerField( blank = True, null = True, default = 0 )
    attribution_verb_word_number = models.IntegerField( blank = True, null = True, default = 0 )
    attribution_paragraph_number = models.IntegerField( blank = True, null = True, default = 0 )
    attribution_speaker_name_string = models.TextField( blank = True, null = True )
    is_speaker_name_pronoun = models.BooleanField( default = False )
    attribution_speaker_name_index_range = models.CharField( max_length = 255, blank = True, null = True )
    attribution_speaker_name_word_range = models.CharField( max_length = 255, blank = True, null = True )

    # meta-data about quotation
    quotation_type = models.CharField( max_length = 255, blank = True, null = True )

    #----------------------------------------------------------------------
    # instance methods
    #----------------------------------------------------------------------


    def __str__( self ):

        # return reference
        string_OUT = ""

        # declare variables
        details_list = []

        # got id?
        if ( self.id ):

            string_OUT = str( self.id ) + " - "

        #-- END check for ID. --#

        details_list = self.build_details_list()

        # got anything in list?
        if ( len( details_list ) > 0 ):

            string_OUT += " ( " + "; ".join( details_list ) + " ) - "

        #-- END check to see if got anything in list --#

        if ( self.article_subject ):

            string_OUT += str( self.article_subject ) + " : "

        #-- END check to see if article_subject. --#

        # got associated quotation?...
        if ( self.value ):

            string_OUT += self.value

        #-- END check to see if we have a quotation. --#

        return string_OUT

    #-- END __str__() method --#

#= End Article_Subject_Quotation Model ======================================================


# Subject_Organization model
class Subject_Organization( models.Model ):

    article_subject = models.ForeignKey( Article_Subject, on_delete = models.CASCADE )
    organization = models.ForeignKey( Organization, on_delete = models.CASCADE, blank = True, null = True )
    title = models.CharField( max_length = 255, blank = True )

    # time stamps.
    create_date = models.DateTimeField( auto_now_add = True )
    last_modified = models.DateTimeField( auto_now = True )

    #----------------------------------------------------------------------
    # instance methods
    #----------------------------------------------------------------------

    def __str__( self ):
        # return reference
        string_OUT = ''

        # got an organization?
        if ( self.organization is not None ):
            string_OUT = self.organization.name

        # got a title?
        if ( self.title != '' ):
            string_OUT = string_OUT + " ( " + self.title + " )"
        return string_OUT

#= End Subject_Organization Model ======================================================


# Subject_Organization model
#class Subject_Organization( models.Model ):

#    article_subject = models.ForeignKey( Article_Subject, on_delete = models.CASCADE, blank = True, null = True )
#    organization = models.ForeignKey( Organization, on_delete = models.CASCADE, blank = True, null = True )
#    title = models.CharField( max_length = 255, blank = True )

    #----------------------------------------------------------------------
    # methods
    #----------------------------------------------------------------------

#    def __str__( self ):

        # return reference
#        string_OUT = ''

        # declare variables
#        delimiter = ''

        # figure out how to present
#        if ( self.organization is not None ):
#            string_OUT = string_OUT + self.organization.name
#            delimiter = ' - '
#        if ( self.title != '' ):
#            string_OUT = string_OUT + delimiter + self.title

#        return string_OUT

#= End Subject_Organization Model ======================================================


# Article_Location model
#class Article_Location( models.Model ):

#    article = models.ForeignKey( Article, on_delete = models.CASCADE )
#    location = models.ForeignKey( Location, on_delete = models.CASCADE )
#    rank = models.IntegerField()

    #----------------------------------------------------------------------
    # methods
    #----------------------------------------------------------------------

#    def __str__( self ):
        #string_OUT = self.rank + " - " + self.location.name
#        string_OUT = '%d - %s' % ( self.rank, self.location.name )
#        return string_OUT

#= End Article_Location Model ======================================================


#==============================================================================#
# !Import and migration models
#==============================================================================#


# Import_Error model
class Import_Error( models.Model ):

    unique_identifier = models.CharField( max_length = 255, blank = True )
    archive_source = models.CharField( max_length = 255, blank = True, null = True )
    item = models.TextField( blank = True, null = True )
    message = models.TextField( blank = True, null = True )
    exception = models.TextField( blank = True, null = True )
    stack_trace = models.TextField( blank = True, null = True )
    batch_identifier = models.CharField( max_length = 255, blank = True )
    item_date = models.DateTimeField( blank = True, null = True )
    status = models.CharField( max_length = 255, blank = True, null = True, default = "new" )
    create_date = models.DateTimeField( auto_now_add = True )
    last_modified = models.DateTimeField( auto_now = True )

    #----------------------------------------------------------------------
    # methods
    #----------------------------------------------------------------------

    def __str__( self ):
        #string_OUT = self.rank + " - " + self.location.name
        string_OUT = '%d - %s (%s): %s' % ( self.id, self.unique_identifier, self.item, self.message )
        return string_OUT

#= End Import_Error Model ======================================================


# Temp_Section model
class Temp_Section( models.Model ):

    #----------------------------------------------------------------------
    # constants-ish
    #----------------------------------------------------------------------

    # Section Name constants.
    NEWS_SECTION_NAME_LIST = [ "Business", "City and Region", "Front Page", "Lakeshore", "Religion", "Special", "Sports", "State" ]
    SECTION_NAME_ALL = "all"

    # variables for building nuanced queries in django.
    # query for bylines of in-house authors.
    Q_IN_HOUSE_AUTHOR = Q( author_varchar__iregex = r'.* */ *THE GRAND RAPIDS PRESS$' ) | Q( author_varchar__iregex = r'.* */ *PRESS .* EDITOR$' ) | Q( author_varchar__iregex = r'.* */ *GRAND RAPIDS PRESS .* BUREAU$' ) | Q( author_varchar__iregex = r'.* */ *SPECIAL TO THE PRESS$' )

    # date range params
    PARAM_START_DATE = "start_date"
    PARAM_END_DATE = "end_date"
    DEFAULT_DATE_FORMAT = "%Y-%m-%d"

    # other article parameters.
    PARAM_CUSTOM_ARTICLE_Q = "custom_article_q"

    # section selection parameters.
    PARAM_SECTION_NAME = "section_name"
    PARAM_CUSTOM_SECTION_Q = "custom_section_q"
    PARAM_JUST_PROCESS_ALL = "just_process_all" # set to True if just want sum of all sections, not records for each individual section.  If False, processes each section individually, then generates the "all" record.

    # property names for dictionaries of output information.
    OUTPUT_DAY_COUNT = "day_count"
    OUTPUT_ARTICLE_COUNT = "article_count"
    OUTPUT_PAGE_COUNT = "page_count"
    OUTPUT_ARTICLES_PER_DAY = "articles_per_day"
    OUTPUT_PAGES_PER_DAY = "pages_per_day"

    #----------------------------------------------------------------------
    # model fields
    #----------------------------------------------------------------------

    name = models.CharField( max_length = 255, blank = True, null = True )
    total_days = models.IntegerField( blank = True, null = True, default = 0 )
    total_articles = models.IntegerField( blank = True, null = True, default = 0 )
    in_house_articles = models.IntegerField( blank = True, null = True, default = 0 )
    external_articles = models.IntegerField( blank = True, null = True, default = 0 )
    external_booth = models.IntegerField( blank = True, null = True, default = 0 )
    total_pages = models.IntegerField( blank = True, null = True, default = 0 )
    in_house_pages = models.IntegerField( blank = True, null = True, default = 0 )
    in_house_authors = models.IntegerField( blank = True, null = True, default = 0 )
    percent_in_house = models.DecimalField( max_digits = 21, decimal_places = 20, blank = True, null = True, default = Decimal( '0' ) )
    percent_external = models.DecimalField( max_digits = 21, decimal_places = 20, blank = True, null = True, default = Decimal( '0' ) )
    average_articles_per_day = models.DecimalField( max_digits = 25, decimal_places = 20, blank = True, null = True, default = Decimal( '0' ) )
    average_pages_per_day = models.DecimalField( max_digits = 25, decimal_places = 20, blank = True, null = True, default = Decimal( '0' ) )
    average_in_house_articles_per_day = models.DecimalField( max_digits = 25, decimal_places = 20, blank = True, null = True, default = Decimal( '0' ) )
    average_in_house_pages_per_day = models.DecimalField( max_digits = 25, decimal_places = 20, blank = True, null = True, default = Decimal( '0' ) )
    start_date = models.DateTimeField( blank = True, null = True )
    end_date = models.DateTimeField( blank = True, null = True )

    create_date = models.DateTimeField( auto_now_add = True )
    last_modified = models.DateTimeField( auto_now = True )

    #----------------------------------------------------------------------
    # instance methods
    #----------------------------------------------------------------------

    def __str__( self ):

        # build the whole string except the id prefix.  Let DEBUG dictate level
        #    of detail.
        if ( DEBUG == True ):

            # high detail.
            string_OUT = '%s: tot_day = %d; tot_art = %d; in_art = %d; ext_art= %d; ext_booth = %d; tot_page = %d; in_page = %d; in_auth = %d; avg_art = %f; avg_page = %f; avg_ih_art = %f; avg_ih_page = %f; per_in = %f; per_ext = %f; start = %s; end = %s' % ( self.name + ": ", self.total_days, self.total_articles, self.in_house_articles, self.external_articles, self.external_booth, self.total_pages, self.in_house_pages, self.in_house_authors, self.average_articles_per_day, self.average_pages_per_day, self.average_in_house_articles_per_day, self.average_in_house_pages_per_day, self.percent_in_house, self.percent_external, str( self.start_date ), str( self.end_date ) )

        else:

            # less detail.
            string_OUT = '%s: tot_art = %d; in_art = %d; ext_art= %d; ext_booth = %d; in_auth = %d; per_in = %f; per_ext = %f; start = %s; end = %s' % ( self.name, self.total_articles, self.in_house_articles, self.external_articles, self.external_booth, self.in_house_authors, self.percent_in_house, self.percent_external, str( self.start_date ), str( self.end_date ) )

        #-- Decide what level of detail based on debug or not --#

        # add on ID if one present.
        if ( self.id ):

            string_OUT = str( self.id ) + " - " + string_OUT

        #-- END check to see if there is an ID. --#

        return string_OUT

    #-- END method __str__() --#


    def add_section_name_filter_to_article_qs( self, qs_IN = None, *args, **kwargs ):

        '''
        Checks section name in this instance.  If "all", adds a filter to
           QuerySet where section just has to be one of those in the list of
           locals.  If not all, adds a filter to limit the section to the name.
        Preconditions: instance must have a name set.
        Postconditions: returns the QuerySet passed in with an additional filter
           for section name.  If no QuerySet passed in, creates new Article
           QuerySet, returns it with filter added.
        '''

        # return reference
        qs_OUT = None

        # declare variables
        me = "add_section_name_filter_to_article_qs"
        my_section_name = ""

        # got a query set?
        if ( qs_IN ):

            # use the one passed in.
            qs_OUT = qs_IN

            #output_debug( "QuerySet passed in, using it.", me, "*** " )

        else:

            # No.  Make one.
            qs_OUT = Article.objects.all()

            #output_debug( "No QuerySet passed in, using fresh one.", me, "*** " )

        #-- END check to see if query set passed in --#

        # get section name.
        my_section_name = self.name

        # see if section name is "all".
        if ( my_section_name == Temp_Section.SECTION_NAME_ALL ):

            # add filter for name being in the list
            qs_OUT = qs_OUT.filter( section__in = Temp_Section.NEWS_SECTION_NAME_LIST )

        else:

            # just limit to the name.
            qs_OUT = qs_OUT.filter( section = self.name )

        #-- END check to see if section name is "all" --#

        return qs_OUT

    #-- END method add_section_name_filter_to_article_qs() --#


    def append_shared_article_qs_params( self, query_set_IN = None, *args, **kwargs ):

        # return reference
        qs_OUT = None

        # declare variables
        me = "append_shared_article_qs_params"
        date_range_q = None
        custom_q_IN = None

        # got a query set?
        if ( query_set_IN ):

            # use the one passed in.
            qs_OUT = query_set_IN

            #output_debug( "QuerySet passed in, using it.", me, "*** " )

        else:

            # No.  Make one.
            qs_OUT = Article.objects.all()

            #output_debug( "No QuerySet passed in, using fresh one.", me, "*** " )

        #-- END check to see if query set passed in --#

        # date range
        date_range_q = self.create_q_article_date_range( *args, **kwargs )

        if ( date_range_q ):

            # yup. add it to query.
            qs_OUT = qs_OUT.filter( date_range_q )

        # end date range check.

        # got a custom Q passed in?
        if ( self.PARAM_CUSTOM_ARTICLE_Q in kwargs ):

            # yup.  Get it.
            custom_q_IN = kwargs[ self.PARAM_CUSTOM_ARTICLE_Q ]

            # anything there?
            if ( custom_q_IN ):

                # add it to the output QuerySet
                qs_OUT = qs_OUT.filter( custom_q_IN )

            #-- END check to see if custom Q() populated --#

        #-- END check to see if start date in arguments --#

        # try deferring the text and raw_html fields.
        #qs_OUT.defer( 'text', 'raw_html' )

        return qs_OUT

    #-- END method append_shared_article_qs_params() --#


    def calculate_average_pages_articles_per_day( self, query_set_IN, *args, **kwargs ):

        '''
        Retrieves pages in current section that have local writers on them for
           each day, then averages the counts over the number of days. Returns
           the average.
        Preconditions: Must have a start and end date.  If not, returns -1.
        '''

        # return reference
        values_OUT = {}

        # Declare variables
        me = "calculate_average_pages_articles_per_day"
        daily_article_qs = None
        start_date_IN = None
        end_date_IN = None
        start_date = None
        end_date = None
        qs_article_count = -1
        current_date = None
        current_timedelta = None
        page_dict = None
        day_page_count_list = None
        day_article_count_list = None
        current_page = ""
        current_page_count = -1
        daily_page_count = -1
        daily_article_count = -1
        overall_time_delta = None
        day_count = -1
        current_count = -1
        total_page_count = -1
        total_article_count = -1

        # get start and end date.
        start_date_IN = get_dict_value( kwargs, Temp_Section.PARAM_START_DATE, None )
        end_date_IN = get_dict_value( kwargs, Temp_Section.PARAM_END_DATE, None )

        # do we have dates?
        if ( ( start_date_IN ) and ( end_date_IN ) ):

            # we do.  Convert them to datetime.
            start_date = datetime.datetime.strptime( start_date_IN, self.DEFAULT_DATE_FORMAT )
            end_date = datetime.datetime.strptime( end_date_IN, self.DEFAULT_DATE_FORMAT )

            # initialize list of counts.
            day_page_count_list = []
            day_article_count_list = []

            # then, loop one day at a time.
            current_date = start_date
            current_timedelta = end_date - current_date

            # loop over dates as long as difference between current and end is 0
            #    or greater.
            while ( current_timedelta.days > -1 ):

                # today's page map
                page_dict = {}
                daily_page_count = 0
                daily_article_count = 0
                output_debug( "Processing " + str( current_date ), me )

                # get articles for current date.add current date to list.
                article_qs = query_set_IN.filter( pub_date = current_date )

                # check if we have anything in the QuerySet
                qs_article_count = article_qs.count()
                output_debug( "Article count: " + str( qs_article_count ), me, "--- " )

                # only process if there is something in the QuerySet
                if ( qs_article_count > 0 ):

                    for article in article_qs.iterator():

                        # get the page for the current article.
                        current_page = article.page

                        # get current page article, increment, and store.
                        current_page_article_count = get_dict_value( page_dict, current_page, 0 )
                        current_page_article_count += 1
                        page_dict[ current_page ] = current_page_article_count

                    #-- END loop over articles for current day. --#

                    # Now, loop over the pages (not the same as number of
                    #    articles - likely will be fewer, with multiple
                    #    articles per page), adding them up and outputting counts
                    #    for each page.
                    output_debug( "Page count: " + str( len( page_dict ) ), me, "--- " )
                    for current_page, current_page_article_count in page_dict.items():

                        # add 1 to page count
                        daily_page_count += 1
                        daily_article_count += current_page_article_count

                        # output page and count.
                        output_debug( current_page + ", " + str( current_page_article_count ), me, "--- " )

                    #-- END loop over pages for a day.

                    # Output average articles per page if page count is not 0.
                    if ( daily_page_count > 0 ):

                        output_debug( "Average articles per page: " + str( daily_article_count / daily_page_count ), me )

                    #-- END check to make sure we don't divide by 0. --#

                #-- END check to see if there are any articles. --#

                # Always add a count for each day to the lists, even if it is 0.
                day_page_count_list.append( daily_page_count )
                day_article_count_list.append( daily_article_count )

                # increment the date and re-calculate timedelta.
                current_date = current_date + datetime.timedelta( days = 1 )
                current_timedelta = end_date - current_date

            #-- END loop over days --#

            # initialize count holders
            total_page_count = 0
            total_article_count = 0

            # get day count
            # day_count = len( day_page_count_list )
            if ( start_date_IN == end_date_IN ):

                day_count = 1

            else:

                overall_time_delta = end_date - start_date
                day_count = overall_time_delta.days + 1

            #-- END try to get number of days set correctly. --#

            output_debug( "Day Count: " + str( day_count ), me, "--- " )

            # loop to get totals for page and article counts.
            for current_count in day_article_count_list:

                # add current count to total_page_count
                total_article_count += current_count

            #-- END loop over page counts --#

            # loop to get totals for page and article counts.
            for current_count in day_page_count_list:

                # add current count to total_page_count
                total_page_count += current_count

            #-- END loop over page counts --#

            # Populate output values.
            values_OUT[ Temp_Section.OUTPUT_DAY_COUNT ] = day_count
            values_OUT[ Temp_Section.OUTPUT_ARTICLE_COUNT ] = total_article_count
            values_OUT[ Temp_Section.OUTPUT_ARTICLES_PER_DAY ] = Decimal( total_article_count ) / Decimal( day_count )
            values_OUT[ Temp_Section.OUTPUT_PAGE_COUNT ] = total_page_count
            values_OUT[ Temp_Section.OUTPUT_PAGES_PER_DAY ] = Decimal( total_page_count ) / Decimal( day_count )

        #-- END check to see if we have required variables. --#

        #output_debug( "Query: " + str( article_qs.query ), me, "---===>" )

        return values_OUT

    #-- END method calculate_average_pages_articles_per_day() --#


    def create_q_article_date_range( self, *args, **kwargs ):

        '''
        Accepts a start and end date in the keyword arguments.  Creates a Q()
           instance that filters dates based on start and end date passed in. If
           both are missing, does nothing.  If on or other passed in, filters
           accordingly.
        Preconditions: Dates must be in YYYY-MM-DD format.
        Postconditions: None.
        '''

        # return reference
        q_OUT = None

        # declare variables
        start_date_IN = ""
        end_date_IN = ""

        # retrieve dates
        # start date
        if ( self.PARAM_START_DATE in kwargs ):

            # yup.  Get it.
            start_date_IN = kwargs[ self.PARAM_START_DATE ]

        #-- END check to see if start date in arguments --#

        # end date
        if ( self.PARAM_END_DATE in kwargs ):

            # yup.  Get it.
            end_date_IN = kwargs[ self.PARAM_END_DATE ]

        #-- END check to see if end date in arguments --#

        if ( ( start_date_IN ) and ( end_date_IN ) ):

            # both start and end.
            q_OUT = Q( pub_date__gte = datetime.datetime.strptime( start_date_IN, self.DEFAULT_DATE_FORMAT ) )
            q_OUT = q_OUT & Q( pub_date__lte = datetime.datetime.strptime( end_date_IN, self.DEFAULT_DATE_FORMAT ) )

        elif( start_date_IN ):

            # just start date
            q_OUT = Q( pub_date__gte = datetime.datetime.strptime( start_date_IN, self.DEFAULT_DATE_FORMAT ) )

        elif( end_date_IN ):

            # just end date
            q_OUT = Q( pub_date__lte = datetime.datetime.strptime( end_date_IN, self.DEFAULT_DATE_FORMAT ) )

        #-- END conditional to see what we got. --#

        return q_OUT

    #-- END method create_q_article_date_range() --#


    def get_daily_averages( self, *args, **kwargs ):

        '''
        Retrieves pages in current section then averages the counts of pages and
           articles over the number of days. Returns
           the average.
        Preconditions: Must have a start and end date.  If not, returns -1.
        Postconditions: Returns a dictionary with two values in it, average
           articles per day and average pages per day.  Also stores the values
           in the current instance, so the calling method need not deal that.
        '''

        # return reference
        values_OUT = -1

        # Declare variables
        me = "get_daily_averages"
        base_article_qs = None
        daily_article_qs = None
        start_date_IN = None
        end_date_IN = None
        averages_dict = None
        day_count = None
        page_count = None
        pages_per_day = None
        articles_per_day = None

        # get start and end date.
        start_date_IN = get_dict_value( kwargs, Temp_Section.PARAM_START_DATE, None )
        end_date_IN = get_dict_value( kwargs, Temp_Section.PARAM_END_DATE, None )

        output_debug( "Getting daily averages for " + start_date_IN + " to " + end_date_IN, me, ">>> " )

        output_debug( "State of object entering method: " + str( self ), me, ">>> " )

        # do we have dates?
        if ( ( start_date_IN ) and ( end_date_IN ) ):

            # add shared filter parameters - for now, just date range.
            base_article_qs = self.append_shared_article_qs_params( *args, **kwargs )

            # get current section articles.
            #base_article_qs = base_article_qs.filter( section = self.name )
            base_article_qs = self.add_section_name_filter_to_article_qs( base_article_qs, *args, **kwargs )

            # call method to calculate averages.
            averages_dict = self.calculate_average_pages_articles_per_day( base_article_qs, *args, **kwargs )

            output_debug( "Averages returned: " + str( averages_dict ), me, ">>> " )

            # bust out the values.
            values_OUT = averages_dict
            day_count = averages_dict.get( Temp_Section.OUTPUT_DAY_COUNT, Decimal( "0" ) )
            page_count = averages_dict.get( Temp_Section.OUTPUT_PAGE_COUNT, Decimal( "0" ) )
            articles_per_day = averages_dict.get( Temp_Section.OUTPUT_ARTICLES_PER_DAY, Decimal( "0" ) )
            pages_per_day = averages_dict.get( Temp_Section.OUTPUT_PAGES_PER_DAY, Decimal( "0" ) )

            # Store values in this instance.
            self.total_days = day_count
            self.total_pages = page_count
            self.average_articles_per_day = articles_per_day
            self.average_pages_per_day = pages_per_day

        #-- END conditional to make sure we have start and end dates --#

        output_debug( "State of object before leaving method: " + str( self ), me, ">>> " )

        return values_OUT

    #-- END method get_daily_averages() --#


    def get_daily_in_house_averages( self, *args, **kwargs ):

        '''
        Retrieves pages in current section that have local writers on them for
           each day, then averages the counts over the number of days. Returns
           the average.
        Preconditions: Must have a start and end date.  If not, returns -1.
        Postconditions: Returns a dictionary with two values in it, average
           articles per day and average pages per day.  Also stores the values
           in the current instance, so the calling method need not deal that.
        '''

        # return reference
        values_OUT = -1

        # Declare variables
        me = "get_daily_in_house_averages"
        base_article_qs = None
        daily_article_qs = None
        start_date_IN = None
        end_date_IN = None
        averages_dict = None
        day_count = None
        page_count = None
        pages_per_day = None
        articles_per_day = None

        # get start and end date.
        start_date_IN = get_dict_value( kwargs, Temp_Section.PARAM_START_DATE, None )
        end_date_IN = get_dict_value( kwargs, Temp_Section.PARAM_END_DATE, None )

        output_debug( "Getting daily IN-HOUSE averages for " + start_date_IN + " to " + end_date_IN, me, ">>> " )

        output_debug( "State of object entering method: " + str( self ), me, ">>> " )

        # do we have dates?
        if ( ( start_date_IN ) and ( end_date_IN ) ):

            # add shared filter parameters - for now, just date range.
            base_article_qs = self.append_shared_article_qs_params( *args, **kwargs )

            # get in-house articles in current section articles.
            base_article_qs = self.add_section_name_filter_to_article_qs( base_article_qs, *args, **kwargs )
            base_article_qs = base_article_qs.filter( Temp_Section.Q_IN_HOUSE_AUTHOR )

            # call method to calculate averages.
            averages_dict = self.calculate_average_pages_articles_per_day( base_article_qs, *args, **kwargs )

            output_debug( "Averages returned: " + str( averages_dict ), me, ">>> " )

            # bust out the values.
            values_OUT = averages_dict
            day_count = averages_dict.get( Temp_Section.OUTPUT_DAY_COUNT, Decimal( "0" ) )
            page_count = averages_dict.get( Temp_Section.OUTPUT_PAGE_COUNT, Decimal( "0" ) )
            articles_per_day = averages_dict.get( Temp_Section.OUTPUT_ARTICLES_PER_DAY, Decimal( "0" ) )
            pages_per_day = averages_dict.get( Temp_Section.OUTPUT_PAGES_PER_DAY, Decimal( "0" ) )

            # Store values in this instance.
            self.total_days = day_count
            self.in_house_pages = page_count
            self.average_in_house_articles_per_day = articles_per_day
            self.average_in_house_pages_per_day = pages_per_day


        #-- END conditional to make sure we have start and end dates --#

        output_debug( "State of object before leaving method: " + str( self ), me, ">>> " )

        return values_OUT

    #-- END method get_daily_in_house_averages() --#


    def get_external_article_count( self, *args, **kwargs ):

        '''
        Retrieves count of articles in the current section whose "author_varchar"
           column indicate that the articles were not written by the Grand
           Rapids Press newsroom.
        '''

        # return reference
        value_OUT = -1

        # Declare variables
        me = "get_external_article_count"
        article_qs = None
        position = ""

        # add shared filter parameters - for now, just date range.
        article_qs = self.append_shared_article_qs_params( article_qs, *args, **kwargs )

        # exclude bylines of local authors.
        article_qs = article_qs.exclude( Temp_Section.Q_IN_HOUSE_AUTHOR )

        # include just this section.
        article_qs = self.add_section_name_filter_to_article_qs( article_qs, *args, **kwargs )

        #output_debug( "Query: " + str( article_qs.query ), me, "---===>" )

        # get count.
        value_OUT = article_qs.count()

        return value_OUT

    #-- END method get_external_article_count --#


    def get_external_booth_count( self, *args, **kwargs ):

        '''
        Retrieves count of articles in the current section whose "author_varchar"
           column indicate that the articles were not written by the Grand
           Rapids Press newsroom, but were implemented in another Booth company
           newsroom.
        '''

        # return reference
        value_OUT = -1

        # Declare variables
        me = "get_external_booth_count"
        article_qs = None
        author_q = None

        # add shared filter parameters - for now, just date range.
        article_qs = self.append_shared_article_qs_params( article_qs, *args, **kwargs )

        # only get articles by news service.
        author_q = Q( author_varchar__iregex = r'.* */ *GRAND RAPIDS PRESS NEWS SERVICE$' )
        article_qs = article_qs.filter( author_q )

        # limit to current section.
        article_qs = self.add_section_name_filter_to_article_qs( article_qs, *args, **kwargs )

        #output_debug( "Query: " + str( article_qs.query ), me, "---===>" )

        # get count.
        value_OUT = article_qs.count()

        return value_OUT

    #-- END method get_external_booth_count --#


    def get_in_house_article_count( self, *args, **kwargs ):

        '''
        Retrieves count of articles in the current section whose "author_varchar"
           column indicate that the articles were written by the actual Grand
           Rapids Press newsroom.
        '''

        # return reference
        value_OUT = -1

        # Declare variables
        me = "get_in_house_article_count"
        article_qs = None

        # get articles.
        #article_qs = Article.objects.filter( Q( section = self.name ), Temp_Section.Q_IN_HOUSE_AUTHOR )
        article_qs = self.add_section_name_filter_to_article_qs( *args, **kwargs )
        article_qs = article_qs.filter( Temp_Section.Q_IN_HOUSE_AUTHOR )

        # add shared filter parameters - for now, just date range.
        article_qs = self.append_shared_article_qs_params( article_qs, *args, **kwargs )
        #output_debug( "Query: " + str( article_qs.query ), me, "---===>" )

        # get count.
        value_OUT = article_qs.count()

        return value_OUT

    #-- END method get_in_house_article_count --#


    def get_in_house_author_count( self, *args, **kwargs ):

        '''
        Retrieves count of distinct author strings (including joint bylines
           separate from either individual's name, and including misspellings)
           of articles in the current section whose "author_varchar" column
           indicate that the articles were implemented by the actual Grand
           Rapids Press newsroom.
        '''

        # return reference
        value_OUT = -1

        # Declare variables
        my_cursor = None
        query_string = ""
        name_list_string = ""
        my_row = None
        start_date_IN = ""
        end_date_IN = ""

        # get database cursor
        my_cursor = connection.cursor()

        # create SQL query string
        query_string = "SELECT COUNT( DISTINCT CONVERT( LEFT( author_varchar, LOCATE( ' / ', author_varchar ) ), CHAR ) ) as name_count"
        query_string += " FROM context_text_article"

        # add in ability to either look for "all" or a single section name.
        if ( self.name == Temp_Section.SECTION_NAME_ALL ):

            # start IN statement.
            query_string += " WHERE section IN ( "

            # make list of section names.
            name_list_string = "', '".join( Temp_Section.NEWS_SECTION_NAME_LIST )

            # check if there is anything in that list.
            if ( name_list_string ):

                # there is.  add quotes to beginning and end.
                name_list_string = "'" + name_list_string + "'"

            #-- END check to see if we have anything in list. --#

            # add list to IN, then close out IN statement.
            query_string += name_list_string + " )"

        else:

            # not all, so just limit to current name.
            query_string += " WHERE section = '" + self.name + "'"

        #-- END check to see if "all" --#

        query_string += "     AND"
        query_string += "     ("
        query_string += "         ( UPPER( author_varchar ) REGEXP '.* */ *THE GRAND RAPIDS PRESS$' )"
        query_string += "         OR ( UPPER( author_varchar ) REGEXP '.* */ *PRESS .* EDITOR$' )"
        query_string += "         OR ( UPPER( author_varchar ) REGEXP '.* */ *GRAND RAPIDS PRESS .* BUREAU$' )"
        query_string += "         OR ( UPPER( author_varchar ) REGEXP '.* */ *SPECIAL TO THE PRESS$' )"
        query_string += "     )"

        # retrieve dates
        # start date
        if ( self.PARAM_START_DATE in kwargs ):

            # yup.  Get it.
            start_date_IN = kwargs[ self.PARAM_START_DATE ]

        #-- END check to see if start date in arguments --#

        # end date
        if ( self.PARAM_END_DATE in kwargs ):

            # yup.  Get it.
            end_date_IN = kwargs[ self.PARAM_END_DATE ]

        #-- END check to see if end date in arguments --#

        if ( ( start_date_IN ) and ( end_date_IN ) ):

            # both start and end.
            query_string += "     AND ( ( pub_date >= '" + start_date_IN + "' ) AND ( pub_date <= '" + end_date_IN + "' ) )"

        elif( start_date_IN ):

            # just start date
            query_string += "     AND ( pub_date >= '" + start_date_IN + "' )"

        elif( end_date_IN ):

            # just end date
            query_string += "     AND ( pub_date <= '" + end_date_IN + "' )"

        #-- END conditional to see what we got. --#

        # execute query.
        my_cursor.execute( query_string )

        # get the row that is returned.
        my_row = my_cursor.fetchone()

        # get count.
        value_OUT = my_row[ 0 ]

        return value_OUT

    #-- END method get_in_house_author_count --#


    def get_total_article_count( self, *args, **kwargs ):

        '''
        Retrieves count of articles whose "section" column contain the current
           section instance's name.
        '''

        # return reference
        value_OUT = -1

        # Declare variables
        article_qs = None

        # get articles.
        #article_qs = Article.objects.filter( section = self.name )
        article_qs = self.add_section_name_filter_to_article_qs( *args, **kwargs )

        # add shared filter parameters - for now, just date range.
        article_qs = self.append_shared_article_qs_params( article_qs, *args, **kwargs )

        # get count.
        value_OUT = article_qs.count()

        return value_OUT

    #-- END method get_total_article_count --#


    def process_column_values( self, do_save_IN = False, *args, **kwargs ):

        '''
        Generates values for all columns for section name passed in.
        '''

        # return reference
        status_OUT = STATUS_SUCCESS

        # Declare variables
        me = "process_column_values"
        my_total_articles = -1
        my_in_house_articles = -1
        my_external_articles = -1
        my_external_booth = -1
        my_in_house_authors = -1
        my_percent_in_house = -1
        my_percent_external = -1
        my_averages = None
        my_in_house_averages = None
        debug_string = ""

        # start and end date?
        start_date_IN = None
        end_date_IN = None

        # retrieve dates
        # start date
        if ( self.PARAM_START_DATE in kwargs ):

            # yup.  Get it.
            start_date_IN = kwargs[ self.PARAM_START_DATE ]
            start_date_IN = datetime.datetime.strptime( start_date_IN, self.DEFAULT_DATE_FORMAT )
            output_debug( "*** Start date = " + str( start_date_IN ) + "\n", me )

        else:

            # No start date.
            output_debug( "No start date!", me, "*** " )

        #-- END check to see if start date in arguments --#

        # end date
        if ( self.PARAM_END_DATE in kwargs ):

            # yup.  Get it.
            end_date_IN = kwargs[ self.PARAM_END_DATE ]
            end_date_IN = datetime.datetime.strptime( end_date_IN, self.DEFAULT_DATE_FORMAT )
            output_debug( "*** End date = " + str( end_date_IN ) + "\n", me )

        else:

            # No end date.
            output_debug( "No end date!", me, "*** " )

        #-- END check to see if end date in arguments --#

        # initialize Decimal Math
        getcontext().prec = 20

        # get values.
        my_total_articles = self.get_total_article_count( *args, **kwargs )
        my_in_house_articles = self.get_in_house_article_count( *args, **kwargs )
        my_external_articles = self.get_external_article_count( *args, **kwargs )
        my_external_booth = self.get_external_booth_count( *args, **kwargs )
        my_in_house_authors = self.get_in_house_author_count( *args, **kwargs )
        my_averages = self.get_daily_averages( *args, **kwargs )
        my_in_house_averages = self.get_daily_in_house_averages( *args, **kwargs )

        # derive additional values

        # percent of articles that are in-house
        if ( ( my_in_house_articles >= 0 ) and ( my_total_articles > 0 ) ):

            # divide in-house by total
            my_percent_in_house = Decimal( my_in_house_articles ) / Decimal( my_total_articles )

        else:

            # either no in-house or total is 0.  Set to 0.
            my_percent_in_house = Decimal( "0.0" )

        #-- END check to make sure values are OK for calculating percent --#

        # percent of articles that are external
        if ( ( my_external_articles >= 0 ) and ( my_total_articles > 0 ) ):

            # divide external by total
            my_percent_external = Decimal( my_external_articles ) / Decimal( my_total_articles )

        else:

            # either no external or total is 0.  Set to 0.
            my_percent_external = Decimal( "0.0" )

        #-- END check to make sure values are OK for calculating percent --#

        # set values
        self.total_articles = my_total_articles
        self.in_house_articles = my_in_house_articles
        self.external_articles = my_external_articles
        self.external_booth = my_external_booth
        self.in_house_authors = my_in_house_authors

        if ( my_percent_in_house ):
            self.percent_in_house = my_percent_in_house
        #-- END check if we have in-house percent --#

        if ( my_percent_external ):
            self.percent_external = my_percent_external
        #-- END check to see if we have percent external --#

        self.start_date = start_date_IN
        self.end_date = end_date_IN

        # save?
        if ( do_save_IN == True ):

            # output contents.
            debug_string = '%s: tot_day = %d; tot_art = %d; in_art = %d; ext_art= %d; ext_booth = %d; tot_page = %d; in_page = %d; in_auth = %d; avg_art = %f; avg_page = %f; avg_ih_art = %f; avg_ih_page = %f; per_in = %f; per_ext = %f; start = %s; end = %s' % ( "Before save, contents of variables for " + self.name + ": ", self.total_days, my_total_articles, my_in_house_articles, my_external_articles, my_external_booth, self.total_pages, self.in_house_pages, my_in_house_authors, self.average_articles_per_day, self.average_pages_per_day, self.average_in_house_articles_per_day, self.average_in_house_pages_per_day, my_percent_in_house, my_percent_external, str( start_date_IN ), str( end_date_IN ) )
            output_debug( debug_string, me, "===>" )
            output_debug( "Contents of instance: " + str( self ), me, "===>" )

            # save
            save_result = self.save()

            output_debug( "save() result: " + str( save_result ), me, "*** " )

        #-- END check to see if we save or not. --#

        return status_OUT

    #-- END method process_column_values --#


    #----------------------------------------------------------------------
    # class methods
    #----------------------------------------------------------------------

    @classmethod
    def find_instance( self, *args, **kwargs ):

        '''
        Generates values for all columns for section name passed in.
        '''

        # return reference
        instance_OUT = None

        # Declare variables
        me = "get_instance_for_name"
        result_qs = None
        result_count = -1

        # incoming parameters
        section_name_IN = ""
        start_date_IN = None
        end_date_IN = None
        custom_q_IN = None

        # start with Empty QuerySet
        result_qs = self.objects.all()

        # retrieve parameters
        # section name
        if ( self.PARAM_SECTION_NAME in kwargs ):

            # yup.  Get it.
            section_name_IN = kwargs[ self.PARAM_SECTION_NAME ]
            result_qs = result_qs.filter( name = section_name_IN )
            output_debug( "Requested section name = " + str( section_name_IN ), me, "*** " )

        else:

            # No start date.
            output_debug( "No section name!", me, "*** " )

        #-- END check to see if start date in arguments --#

        # start date
        if ( self.PARAM_START_DATE in kwargs ):

            # yup.  Get it.
            start_date_IN = kwargs[ self.PARAM_START_DATE ]
            start_date_IN = datetime.datetime.strptime( start_date_IN, self.DEFAULT_DATE_FORMAT )
            result_qs = result_qs.filter( start_date = start_date_IN )
            output_debug( "Start date = " + str( start_date_IN ), me, "*** " )

        else:

            # No start date.
            output_debug( "No start date!\n", me, "*** " )

        #-- END check to see if start date in arguments --#

        # end date
        if ( self.PARAM_END_DATE in kwargs ):

            # yup.  Get it.
            end_date_IN = kwargs[ self.PARAM_END_DATE ]
            end_date_IN = datetime.datetime.strptime( end_date_IN, self.DEFAULT_DATE_FORMAT )
            result_qs = result_qs.filter( end_date = end_date_IN )
            output_debug( "End date = " + str( end_date_IN ), me, "*** " )

        else:

            # No end date.
            output_debug( "No end date!\n", me, "*** " )

        #-- END check to see if end date in arguments --#

        # got a custom Q passed in?
        if ( self.PARAM_CUSTOM_SECTION_Q in kwargs ):

            # yup.  Get it.
            custom_q_IN = kwargs[ self.PARAM_CUSTOM_SECTION_Q ]

            # anything there?
            if ( custom_q_IN ):

                # add it to the output QuerySet
                result_qs = result_qs.filter( custom_q_IN )

            #-- END check to see if custom Q() populated --#

        #-- END check to see if custom Q() in arguments --#

        # try to get Temp_Section instance
        try:

            instance_OUT = result_qs.get()

        except MultipleObjectsReturned:

            # error!
            output_debug( "ERROR - more than one match for name \"" + name_IN + "\" when there should only be one.  Returning nothing.", me )

        except ObjectDoesNotExist:

            # either nothing or negative count (either implies no match).
            #    Return new instance.
            instance_OUT = Temp_Section()
            instance_OUT.name = section_name_IN

            # got a start date?
            if ( start_date_IN ):

                instance_OUT.start_date = start_date_IN

            #-- END check to see if we have a start date. --#

            # got an end date?
            if ( end_date_IN ):

                instance_OUT.end_date = end_date_IN

            #-- END check to see if we have an end date. --#

        #-- END try to retrieve instance for name passed in. --#

        return instance_OUT

    #-- END class method find_instance --#


    @classmethod
    def process_section_date_range( cls, *args, **kwargs ):

        # declare variables
        me = "process_section_date_range"
        start_date_IN = ""
        end_date_IN = ""
        skip_individual_sections_IN = False
        save_stats = True
        section_params = {}
        current_section_name = ""
        current_instance = None

        # Get start and end dates
        start_date_IN = get_dict_value( kwargs, cls.PARAM_START_DATE, None )
        end_date_IN = get_dict_value( kwargs, cls.PARAM_END_DATE, None )

        # check if we only want to create "all" records, so skip individual
        #    sections.
        skip_individual_sections_IN = get_dict_value( kwargs, cls.PARAM_JUST_PROCESS_ALL, False )

        # got dates?
        if ( ( start_date_IN ) and ( end_date_IN ) ):

            # store in params.
            section_params[ cls.PARAM_START_DATE ] = start_date_IN
            section_params[ cls.PARAM_END_DATE ] = end_date_IN

            # process records for individual sections?
            if( skip_individual_sections_IN == False ):

                # loop over list of section names that are local news or sports.
                for current_section_name in cls.NEWS_SECTION_NAME_LIST:

                    # set section name
                    section_params[ cls.PARAM_SECTION_NAME ] = current_section_name

                    # get instance
                    current_instance = cls.find_instance( **section_params )

                    # process values and save
                    current_instance.process_column_values( save_stats, **section_params )

                    # output current instance.
                    output_debug( "Finished processing section " + current_section_name + " - " + str( current_instance ) + "\n\n", me, "\n\n=== " )

                    # memory management.
                    gc.collect()
                    django.db.reset_queries()

                #-- END loop over sections. --#

            #-- END check to see if just want to update "all" rows. --#

            # Then, do the "all"
            # set section name
            section_params[ cls.PARAM_SECTION_NAME ] = Temp_Section.SECTION_NAME_ALL

            # get instance
            current_instance = cls.find_instance( **section_params )

            # process values and save
            current_instance.process_column_values( save_stats, **section_params )

            # output current instance.
            output_debug( "Finished processing section " + current_section_name + " - " + str( current_instance ) + "\n\n", me, "\n\n=== " )

            # memory management.
            gc.collect()
            django.db.reset_queries()

        #-- END check to make sure we have dates. --#

    #-- END method process_section_date_range() --#


    @classmethod
    def process_section_date_range_day_by_day( cls, *args, **kwargs ):

        # declare variables
        me = "process_section_date_range_day_by_day"
        start_date_IN = ""
        end_date_IN = ""
        skip_individual_sections_IN = False
        start_date = None
        end_date = None
        save_stats = True
        daily_params = {}
        current_section_name = ""
        current_date = None
        current_timedelta = None
        current_instance = None


        # Get start and end dates
        start_date_IN = get_dict_value( kwargs, cls.PARAM_START_DATE, None )
        end_date_IN = get_dict_value( kwargs, cls.PARAM_END_DATE, None )

        # check if we only want to create "all" records, so skip individual
        #    sections.
        skip_individual_sections_IN = get_dict_value( kwargs, cls.PARAM_JUST_PROCESS_ALL, False )

        # got dates?
        if ( ( start_date_IN ) and ( end_date_IN ) ):

            # Convert start and end dates to datetime.
            start_date = datetime.datetime.strptime( start_date_IN, cls.DEFAULT_DATE_FORMAT )
            end_date = datetime.datetime.strptime( end_date_IN, cls.DEFAULT_DATE_FORMAT )

            # then, loop one day at a time.
            current_date = start_date
            current_timedelta = end_date - current_date

            # loop over dates as long as difference between current and end is 0
            #    or greater.
            while ( current_timedelta.days > -1 ):

                # current date
                output_debug( "Processing " + str( current_date ), me )

                # set start and end date in kwargs to current_date
                daily_params[ cls.PARAM_START_DATE ] = current_date.strftime( cls.DEFAULT_DATE_FORMAT )
                daily_params[ cls.PARAM_END_DATE ] = current_date.strftime( cls.DEFAULT_DATE_FORMAT )

                # process records for individual sections?
                if( skip_individual_sections_IN == False ):

                    # yes - loop over list of section names that are local news or sports.
                    for current_section_name in cls.NEWS_SECTION_NAME_LIST:

                        # set section name
                        daily_params[ cls.PARAM_SECTION_NAME ] = current_section_name

                        # get an instance
                        current_instance = cls.find_instance( **daily_params )

                        # process values and save
                        current_instance.process_column_values( save_stats, **daily_params )

                        # output current instance.
                        output_debug( "Finished processing section " + current_section_name + "\n\n", me, "\n\n=== " )

                    #-- END loop over sections. --#

                #-- END check to see if just want to update "all" rows. --#

                # process "all"
                # set section name
                daily_params[ cls.PARAM_SECTION_NAME ] = cls.SECTION_NAME_ALL

                # get an instance
                current_instance = cls.find_instance( **daily_params )

                # process values and save
                current_instance.process_column_values( save_stats, **daily_params )

                # output current instance.
                output_debug( "Finished processing section " + current_section_name + "\n\n", me, "\n\n=== " )

                # Done with this date.  Moving on.
                output_debug( "Finished processing date " + str( current_date ) + " - " + str( current_instance ) + "\n\n", me, "\n\n=== " )

                # increment the date and re-calculate timedelta.
                current_date = current_date + datetime.timedelta( days = 1 )
                current_timedelta = end_date - current_date

                # memory management.
                gc.collect()
                django.db.reset_queries()

            #-- END loop over dates in date range --#

        #-- END check to make sure we have start and end date. --#

    #-- END method process_section_date_range_day_by_day() --#


#= End Temp_Section Model ======================================================#


class Articles_To_Migrate( models.Model ):

    ARTICLE_TYPE_CHOICES = (
        ( "news", "News" ),
        ( "sports", "Sports" ),
        ( "feature", "Feature" ),
        ( "opinion", "Opinion" ),
        ( "other", "Other" )
    )

    article = models.ForeignKey( Article, on_delete = models.CASCADE, blank = True, null = True )
    unique_identifier = models.CharField( max_length = 255, blank = True )
    coder = models.ForeignKey( User, on_delete = models.SET_NULL, blank = True, null = True )
    newspaper = models.ForeignKey( Newspaper, on_delete = models.SET_NULL, blank = True, null = True )
    pub_date = models.DateField()
    section = models.CharField( max_length = 255, blank = True )
    page = models.IntegerField( blank = True )
    headline = models.CharField( max_length = 255 )
    text = models.TextField( blank = True )
    is_sourced = models.BooleanField( default = True )
    can_code = models.BooleanField( default = True )
    article_type = models.CharField( max_length = 255, choices = ARTICLE_TYPE_CHOICES, blank = True, default = 'news' )

    #----------------------------------------------------------------------------
    # Meta class
    #----------------------------------------------------------------------------

    # Meta-data for this class.
    class Meta:
        ordering = [ 'pub_date', 'section', 'page' ]


    #----------------------------------------------------------------------------
    # instance methods
    #----------------------------------------------------------------------------


    def __str__( self ):

        # start with stuff we should always have.
        string_OUT = str( self.id ) + " - " + self.pub_date.strftime( "%b %d, %Y" )

        # Got a section?
        if ( self.section ):

            # add section
            string_OUT += ", " + self.section

        #-- END check to see if section present.

        # Got a page?
        if ( self.page ):

            # add page.
            string_OUT += " ( " + str( self.page ) + " )"

        #-- END check to see if page. --#

        # Unique Identifier?
        if ( self.unique_identifier ):

            # Add UID
            string_OUT += ", UID: " + self.unique_identifier

        #-- END check for unique identifier

        # headline
        string_OUT += " - " + self.headline

        # got a related newspaper?
        if ( self.newspaper ):

            # Yes.  Append it.
            string_OUT += " ( " + self.newspaper.name + " )"

        elif ( self.source_string ):

            # Well, we have a source string.
            string_OUT += " ( " + self.source_string + " )"

        #-- END check to see if newspaper present. --#

        return string_OUT

    #-- END method __str__() --#


#= END Articles_To_Migrate model ===============================================#


#==============================================================================#
# ! Export Network Data models
#==============================================================================#


# NetworkDataOutputLog model
class NetworkDataOutputLog( models.Model ):

    # Sources:
    REQUEST_TYPE_HTTP_REQUEST = "http_request"
    REQUEST_TYPE_JSON = "json"
    REQUEST_TYPE_DEFAULT = REQUEST_TYPE_JSON

    REQUEST_TYPE_CHOICES_LIST = (
        ( REQUEST_TYPE_JSON, "JSON" ),
        ( REQUEST_TYPE_HTTP_REQUEST, "HTTP request" )
    )

    # Content types:
    CONTENT_TYPE_CANONICAL = 'canonical'
    CONTENT_TYPE_TEXT = 'text'
    CONTENT_TYPE_HTML = 'html'
    CONTENT_TYPE_JSON = 'json'
    CONTENT_TYPE_XML = 'xml'
    CONTENT_TYPE_OTHER = 'other'
    CONTENT_TYPE_NONE = 'none'
    CONTENT_TYPE_DEFAULT = CONTENT_TYPE_TEXT

    CONTENT_TYPE_CHOICES = (
        ( CONTENT_TYPE_CANONICAL, "Canonical" ),
        ( CONTENT_TYPE_TEXT, "Text" ),
        ( CONTENT_TYPE_HTML, "HTML" ),
        ( CONTENT_TYPE_JSON, "JSON" ),
        ( CONTENT_TYPE_XML, "XML" ),
        ( CONTENT_TYPE_OTHER, "Other" ),
        ( CONTENT_TYPE_NONE, "None" )
    )

    PARAM_NAME_OUTPUT_TYPE = "output_type"

    #----------------------------------------------------------------------
    # model fields and meta
    #----------------------------------------------------------------------

    data_spec_json = models.JSONField()
    data_spec_json_hash = models.CharField( max_length = 255, blank = True, null = True )
    description = models.TextField( blank = True, null = True )
    label = models.CharField( max_length = 255, blank = True, null = True )
    network_data = models.TextField()
    network_data_content_type = models.CharField( max_length = 255, choices = CONTENT_TYPE_CHOICES, blank = True, null = True, default = CONTENT_TYPE_DEFAULT )
    network_data_format = models.CharField( max_length = 255, choices = ContextTextBase.NETWORK_DATA_FORMAT_CHOICES_LIST, blank = True, null = True )
    network_data_hash = models.CharField( max_length = 255, blank = True, null = True )
    notes = models.TextField( blank = True, null = True )
    request_type = models.CharField( max_length = 255, choices = REQUEST_TYPE_CHOICES_LIST, blank = True, null = True, default = REQUEST_TYPE_DEFAULT )
    status = models.CharField( max_length = 255, blank = True, null = True )
    status_message = models.TextField( blank = True, null = True )

    # timestamps
    create_date = models.DateTimeField( auto_now_add = True )
    last_modified = models.DateTimeField( auto_now = True )

    # tags!
    tags = TaggableManager( blank = True )

    # meta class so we know this is an abstract class.
    class Meta:
        ordering = [ 'last_modified', 'create_date' ]

    #----------------------------------------------------------------------
    # NOT instance variables
    # Class variables - overriden by __init__() per instance if same names, but
    #    if not set there, shared!
    #----------------------------------------------------------------------


    #bs_helper = None


    #----------------------------------------------------------------------------
    # class methods
    #----------------------------------------------------------------------------


    @classmethod
    def make_standard_json_string_hash( cls, json_IN ):

        # return reference
        value_OUT = None

        # declare variables
        me = "make_standard_json_string_hash"
        json_object = None
        my_json_hash_hexdigest = None

        # value_IN is json_object
        json_object = json_IN

        # Is JSON not None?
        if ( json_object is not None ):

            # not None - create hash of standardized JSON string and store.
            my_json_hash_hexdigest = JSONHelper.create_standard_json_hash( json_object )
            value_OUT = my_json_hash_hexdigest

        #-- END check to see if JSON is not None. --#

        return value_OUT

    #-- END class method make_standard_json_string_hash() --#


    @classmethod
    def make_string_hash( cls, value_IN, hash_function_IN = hashlib.sha256 ):

        # return reference
        value_OUT = None

        # declare variables
        me = "make_string_hash"

        # call StringHelper method.
        value_OUT = StringHelper.make_string_hash( value_IN, hash_function_IN = hash_function_IN )

        return value_OUT

    #-- END class method make_string_hash() --#


    #----------------------------------------------------------------------------
    # instance methods
    #----------------------------------------------------------------------------


    def __init__( self, *args, **kwargs ):

        # call parent __init()__ first.
        super().__init__( *args, **kwargs )

        # then, initialize variable.
        self.bs_helper = None

    #-- END method __init__() --#


    def get_bs_helper( self ):

        # return reference
        instance_OUT = None

        # get instance.
        instance_OUT = self.bs_helper

        # got one?
        if ( not( instance_OUT ) ):

            # no.  Create and store.
            self.bs_helper = BeautifulSoupHelper()

            # try again.  If nothing this time, nothing we can do.  Return it.
            instance_OUT = self.bs_helper

        #-- END check to see if regex is stored in instance --#

        return instance_OUT

    #-- END method get_bs_helper() --#


    def get_data_spec_json( self, *args, **kwargs ):

        '''
        Returns request JSON nested in this instance.
        Preconditions: None
        Postconditions: None

        Returns the request JSON exactly as it is stored in the instance.
        '''

        # return reference
        value_OUT = None

        # declare variables
        me = "get_data_spec_json"

        # return the content.
        value_OUT = self.data_spec_json

        return value_OUT

    #-- END method get_data_spec_json() --#


    def get_data_spec_json_hash( self, *args, **kwargs ):

        '''
        Returns data_spec_json_hash nested in this instance.
        Preconditions: None
        Postconditions: None

        Returns the data_spec_json_hash exactly as it is stored in the instance.
        '''

        # return reference
        value_OUT = None

        # declare variables
        me = "get_data_spec_json_hash"

        # return the content.
        value_OUT = self.data_spec_json_hash

        return value_OUT

    #-- END method get_data_spec_json_hash() --#


    def get_label( self, *args, **kwargs ):

        '''
        Returns label stored in this instance.
        Preconditions: None
        Postconditions: None

        Returns the label exactly as it is stored in the instance.
        '''

        # return reference
        value_OUT = None

        # declare variables
        me = "get_label"

        # return the content.
        value_OUT = self.label

        return value_OUT

    #-- END method get_label() --#


    def get_network_data( self, *args, **kwargs ):

        '''
        Returns network_data nested in this instance.
        Preconditions: None
        Postconditions: None

        Returns the network_data exactly as it is stored in the instance.
        '''

        # return reference
        value_OUT = None

        # declare variables
        me = "get_network_data"

        # return the content.
        value_OUT = self.network_data

        return value_OUT

    #-- END method get_network_data() --#


    def get_network_data_format( self, *args, **kwargs ):

        '''
        Returns network_data nested in this instance.
        Preconditions: None
        Postconditions: None

        Returns the network_data exactly as it is stored in the instance.
        '''

        # return reference
        value_OUT = None

        # declare variables
        me = "get_network_data_format"

        # return the content.
        value_OUT = self.network_data_format

        return value_OUT

    #-- END method get_network_data_format() --#


    def get_network_data_hash( self, *args, **kwargs ):

        '''
        Returns network_data_hash nested in this instance.
        Preconditions: None
        Postconditions: None

        Returns the network_data_hash exactly as it is stored in the instance.
        '''

        # return reference
        value_OUT = None

        # declare variables
        me = "get_network_data_hash"

        # return the content.
        value_OUT = self.network_data_hash

        return value_OUT

    #-- END method get_network_data_hash() --#


    def get_request_type( self, *args, **kwargs ):

        '''
        Returns value nested in this instance.
        Preconditions: None
        Postconditions: None
        '''

        # return reference
        value_OUT = None

        # declare variables
        me = "get_request_type"

        # return the content.
        value_OUT = self.request_type

        return value_OUT

    #-- END method get_request_type() --#


    def set_data_spec_json( self, value_IN = "", *args, **kwargs ):

        '''
        Accepts a JSON object (dictionary).  Stores it in this instance's
            data_spec_json variable.
        Preconditions: None
        Postconditions: Also creates a sha256 hash of the standardized string
            representation of the JSON passed in and stores it in
            data_spec_json_hash.

        Returns data_spec_json as it is stored in the instance.
        '''

        # return reference
        value_OUT = None

        # declare variables
        me = "set_data_spec_json"
        json_object = None
        my_json_hash_hexdigest = None
        my_output_type = None

        # value_IN is json_object
        json_object = value_IN

        # set the JSON in the instance.
        self.data_spec_json = json_object

        # Is JSON not None?
        if ( json_object is not None ):

            # not None - create hash of standardized JSON string and store.
            my_json_hash_hexdigest = self.make_standard_json_string_hash( json_object )
            self.set_data_spec_json_hash( my_json_hash_hexdigest )

            # retrieve output_type and store it in network_data_format
            my_output_type = json_object.get( ContextTextBase.PARAM_NAME_OUTPUT_TYPE, None )

            # got output type?
            if (
                ( my_output_type is not None )
                and ( my_output_type != "" )
                and ( my_output_type in ContextTextBase.NETWORK_DATA_FORMAT_CHOICES_LIST )
            ):

                # yes - store it in network_data_format
                self.network_data_format = my_output_type

            #-- END check if there is an output type. --#

        #-- END check to see if JSON is not None. --#

        # return the content.
        value_OUT = self.get_data_spec_json()

        return value_OUT

    #-- END method set_data_spec_json() --#


    def set_data_spec_json_hash( self, value_IN = "", *args, **kwargs ):

        '''
        Accepts a hash of a JSON object's standardized string representation.
            Stores it in this instance's data_spec_json_hash variable.
        Preconditions: None
        Postconditions: Also creates a sha256 hash of the standardized string
            representation of the JSON passed in and stores it in
            data_spec_json_hash.

        Returns data_spec_json_hash as it is stored in the instance.
        '''

        # return reference
        value_OUT = None

        # declare variables
        me = "set_data_spec_json_hash"

        # set the value in the instance.
        self.data_spec_json_hash = value_IN

        # return the request.
        value_OUT = self.get_data_spec_json_hash()

        return value_OUT

    #-- END method set_data_spec_json_hash() --#


    def set_label( self, value_IN = "", *args, **kwargs ):

        '''
        Accepts value and stores it in current instance variable.
        Preconditions: None

        Returns value as it is stored in the instance.
        '''

        # return reference
        value_OUT = None

        # declare variables
        me = "set_label"

        # set the value in the instance.
        self.label = value_IN

        # return the value set in the instance.
        value_OUT = self.get_label()

        return value_OUT

    #-- END method set_label() --#


    def set_network_data( self, value_IN = "", hash_function_IN = hashlib.sha256, *args, **kwargs ):

        '''
        Accepts a piece of text.  Stores it in this instance's network_data variable.
        Preconditions: None
        Postconditions: None

        Returns the network_data as it is stored in the instance.
        '''

        # return reference
        value_OUT = None

        # declare variables
        me = "set_network_data"
        my_value_bytes = None
        my_value_hash = None
        my_value_hash_hexdigest = None

        # set the text in the instance.
        self.network_data = value_IN

        # Is value not None and not empty?
        if ( ( value_IN is not None ) and ( value_IN != "" ) ):

            # get hex digest of hash
            my_value_hash_hexdigest = self.make_string_hash( value_IN )

            # store it.
            self.set_network_data_hash( my_value_hash_hexdigest )

        #-- END check to see if value is not None. --#

        # return the content.
        value_OUT = self.get_network_data()

        return value_OUT

    #-- END method set_network_data() --#


    def set_network_data_format( self, value_IN = "", *args, **kwargs ):

        '''
        Accepts value, stores it in this instance's variable.
        Preconditions: None
        Postconditions: None

        Returns the value as it is stored in the instance.
        '''

        # return reference
        value_OUT = None

        # declare variables
        me = "set_network_data_format"

        # set the value in the instance.
        self.network_data_format = value_IN

        # return the value.
        value_OUT = self.get_network_data_format()

        return value_OUT

    #-- END method set_network_data_format() --#


    def set_network_data_hash( self, value_IN = "", *args, **kwargs ):

        '''
        Accepts the hash of the data in "network_data". Stores it in this instance's
            network_data_hash variable.
        Preconditions: None
        Postconditions: None

        Returns the network_data_hash as it is stored in the instance.
        '''

        # return reference
        value_OUT = None

        # declare variables
        me = "set_network_data_hash"

        # set the text in the instance.
        self.network_data_hash = value_IN

        # return the content_hash.
        value_OUT = self.get_network_data_hash()

        return value_OUT

    #-- END method set_network_data_hash() --#


    def set_request_type( self, value_IN = "", *args, **kwargs ):

        '''
        Accepts value and stores it in current instance variable.
        Preconditions: None

        Returns value as it is stored in the instance.
        '''

        # return reference
        value_OUT = None

        # declare variables
        me = "set_request_type"

        # set the value in the instance.
        self.request_type = value_IN

        # return the value set in the instance.
        value_OUT = self.get_request_type()

        return value_OUT

    #-- END method set_request_type() --#


    def to_string( self ):

        # return reference
        string_OUT = ""

        if ( self.id ):

            string_OUT += str( self.id ) + " - "

        #-- END check to see if ID --#

        if ( self.label ):

            string_OUT += self.label

        #-- END check to see if label --#

        if ( self.network_data_format ):

            string_OUT += " ( type \"" + self.network_data_format + "\" )"

        #-- END check to see if there is a network_data_format --#

        return string_OUT

    #-- END method to_string() --#


    def __str__( self ):

        # return reference
        string_OUT = ""

        string_OUT = self.to_string()

        return string_OUT

    #-- END method __str__() --#


#-- END abstract NetworkDataOutputLog model --#
