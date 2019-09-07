from __future__ import unicode_literals

'''
Copyright 2019-present (2019) Jonathan Morgan

This file is part of http://github.com/jonathanmorgan/context_text.

context_text is free software: you can redistribute it and/or modify it under the terms of the GNU Lesser General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.

context_text is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.

You should have received a copy of the GNU Lesser General Public License along with http://github.com/jonathanmorgan/context_text. If not, see http://www.gnu.org/licenses/.
'''

# imports
import datetime
import logging

# six - python 2 + 3
import six

# django imports
from django.db.models import Avg, Max, Min
from django.db.models.query import QuerySet
from django.utils.text import slugify

# python utilities
from python_utilities.django_utils.django_model_helper import DjangoModelHelper
from python_utilities.logging.logging_helper import LoggingHelper
from python_utilities.objects.object_helper import ObjectHelper
from python_utilities.status.status_container import StatusContainer

# context imports
from context.models import Entity
from context.models import Entity_Identifier_Type
from context.models import Entity_Identifier

# context_text imports
from context_text.article_coding.article_coding import ArticleCoder
from context_text.article_coding.article_coding import ArticleCoding
from context_text.article_coding.open_calais_v2.open_calais_v2_article_coder import OpenCalaisV2ArticleCoder
from context_text.collectors.newsbank.newspapers.GRPB import GRPB
from context_text.collectors.newsbank.newspapers.DTNB import DTNB
from context_text.models import Article
from context_text.models import Article_Subject
from context_text.models import Newspaper
from context_text.shared.context_text_base import ContextTextBase

class ExportToContext( ContextTextBase ):


    #============================================================================
    # ! ==> constants-ish
    #============================================================================


    # DEBUG
    DEBUG_FLAG = False
    LOGGER_NAME = "context_text.export.to_context_base.export_to_context.ExportToContext"
    ME = LOGGER_NAME
    
    # Person related set attributes
    PERSON_RELATED_SET_ATTRIBUTE_NAMES = []
    
    # merge functions
    CLASS_NAME_TO_MERGE_FUNCTION_MAP = {}
    DEFAULT_MERGE_FUNCTION = None
    

    #============================================================================
    # static methods
    #============================================================================


    #============================================================================
    # ! ==> class methods
    #============================================================================


    #---------------------------------------------------------------------------
    # ! ==> __init__() method
    #---------------------------------------------------------------------------


    def __init__( self ):

        # call parent's __init__()
        super( ExportToContext, self ).__init__()

        # declare variables
        self.current_working_folder = "/home/jonathanmorgan/work/django/research/work/phd_work/analysis"
        self.current_datetime = datetime.datetime.now()
        self.current_date_string = self.current_datetime.strftime( "%Y-%m-%d-%H-%M-%S" )

        # set logger name (for LoggingHelper parent class: (LoggingHelper --> BasicRateLimited --> ContextTextBase).
        self.set_logger_name( self.LOGGER_NAME )
        
        # initialize variables - log output
        #self.logging_level = self.LOGGING_DEFAULT_LEVEL
        #self.logging_format = self.LOGGING_DEFAULT_FORMAT
        #self.logging_filename = self.LOGGING_DEFAULT_FILENAME
        #self.logging_filemode = self.LOGGING_DEFAULT_FILEMODE

    #-- END method __init__() --#


    #---------------------------------------------------------------------------
    # ! ==> instance methods, in alphabetical order
    #---------------------------------------------------------------------------


    def create_article_entity( self, instance_IN ):
        
        '''
        Accepts an Article instance, creates and populates an entity for the Article based on the contents of the instance.
        '''
        
        # return reference
        entity_OUT = None
        
        # declare variables
        article_instance = None
        
        # declare variables - find existing.
        article_id = None
        identifier_type_name = None
        entity_identifier_type = None
        existing_entity_qs = None
        existing_entity_count = -1
        
        # declare variables - create new.
        entity_instance = None
        entity_type = None
        trait_name = None
        trait_definition = None
        trait_instance = None
        trait_value = None
        trait_type = None
        identifier_type = None
        identifier_instance = None
        identifier_uuid = None
        
        # init
        identifier_type_name = "article_sourcenet_id"
        
        # make sure an article was passed in.
        article_instance = instance_IN
        if ( article_instance is not None ):
            
            # check to see if already an article entity with this ID.
            article_id = article_instance.id
            
            # filter on identifier with type "article_sourcenet_id"...
            entity_identifier_type = Entity_Identifier_Type.objects.get( name = identifier_type_name )
            existing_entity_qs = Entity.objects.filter( entity_identifier__entity_identifier_type = entity_identifier_type )
    
            # ...and the ID of the article.
            existing_entity_qs = existing_entity_qs.filter( entity_identifier__uuid = article_id )
    
            # what have we got?
            existing_entity_count = existing_entity_qs.count()
            if existing_entity_count == 0:
            
                # got an instance.  Create entity instance.
                entity_instance = Entity()
                entity_instance.name = "context_text-Article-{}".format( article_instance.id )
                entity_instance.notes = "{}".format( article_instance )
                entity_instance.save()
    
                # set type
                entity_type = entity_instance.add_entity_type( "article" )
    
            elif existing_entity_count == 1:
                
                # already exists. return it.
                entity_instance = existing_entity_qs.get()
    
                # set type
                entity_type = entity_instance.my_entity_types.get()
                
            else:
                
                # more than one existing match.  Error.
                print( "ERROR - more than one entity ( {} ) with identifier of type {}, uuid = {}".format( existing_entity_count, identifier_type_name, article_id ) )
    
            #-- END check for existing entity. --#
            
            # got an entity?
            if ( entity_instance is not None ):
    
                # ==> set entity traits
    
                # ----> publication date
                trait_name = "pub_date"
                trait_value = article_instance.pub_date
                trait_value = trait_value.strftime( "%Y-%m-%d" )
    
                # initialize trait from predefined entity type trait "pub_date".
                trait_definition = entity_type.get_trait_spec( trait_name )
    
                # add trait
                entity_instance.set_entity_trait( trait_name,
                                                  trait_value,
                                                  entity_type_trait_IN = trait_definition )
    
                # ----> newspaper ID
                trait_name = "sourcenet-Newspaper-ID"
                trait_value = article_instance.newspaper.id
                entity_instance.set_entity_trait( trait_name,
                                                  trait_value,
                                                  slug_IN = slugify( trait_name ) )
    
                # ==> add identifiers
    
                # ----> for django ID in this system.
                identifier_type = Entity_Identifier_Type.get_type_for_name( "article_sourcenet_id" )
                identifier_uuid = article_instance.id
                entity_instance.set_identifier( identifier_uuid,
                                                name_IN = identifier_type.name,
                                                entity_identifier_type_IN = identifier_type )
                
                # ----> for Newsbank ID
                identifier_type = Entity_Identifier_Type.get_type_for_name( "article_newsbank_id" )
                identifier_uuid = article_instance.unique_identifier
                entity_instance.set_identifier( identifier_uuid,
                                                name_IN = identifier_type.name,
                                                entity_identifier_type_IN = identifier_type )
    
            else:
                
                # no entity, can't add/update traits or identifiers
                print( "no entity, can't add/update traits or identifiers" )
                
            #-- END check to make sure we have an entity --#
            
        #-- END check to see if instance is None --#
        
        return entity_OUT
        
    #-- END method create_article_entity() --#


#-- END class ExportToContext --#