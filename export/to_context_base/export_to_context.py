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

# object --> LoggingHelper --> ExceptionHelper --> BasicRateLimited --> ContextBase --> ContextTextBase --> ExportToContext
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
    
    # entity identifier types

    # entity identifier types - general
    ENTITY_ID_TYPE_PERMALINK = "permalink"
    
    # entity identifier types - articles
    ENTITY_ID_TYPE_ARTICLE_ARCHIVE_IDENTIFIER = "article_archive_identifier"
    ENTITY_ID_TYPE_ARTICLE_SOURCENET_ID = "article_sourcenet_id"
    ENTITY_ID_TYPE_ARTICLE_NEWSBANK_ID = "article_newsbank_id"
    
    # entity identifier types - default
    ENTITY_ID_TYPE_DEFAULT = ENTITY_ID_TYPE_PERMALINK
    
    

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
        
        # article export customization
        self.article_uuid_id_type_name = None
        self.article_uuid_id_type = None

    #-- END method __init__() --#


    #---------------------------------------------------------------------------
    # ! ==> instance methods, in alphabetical order
    #---------------------------------------------------------------------------


    def get_article_uuid_id_type( self, default_name_IN = ENTITY_ID_TYPE_DEFAULT, update_on_default_IN = True ):
        
        # return reference
        uuid_id_type_OUT = None
        
        # declare variables
        me = "get_article_uuid_id_type"
        log_message = None
        id_type_name = None
        id_type_instance = None
        
        # get instance
        id_type_instance = self.article_uuid_id_type
        
        # got anything?
        if ( id_type_instance is not None ):
        
            # instance was already loaded.  Return it.
            uuid_id_type_OUT = id_type_instance
        
        else:
        
            # no.  Try to retrieve type for nested name.
            id_type_name = self.article_uuid_id_type_name
            
            # got a name?
            if ( ( id_type_name is not None ) and ( id_type_name != "" ) ):
            
                # yes.  Use it to lookup.
                id_type_instance = Entity_Identifier_Type.get_type_for_name( id_type_name )
                
            #-- END check to see if name set in instance. --#
            
            # got instance?
            if ( id_type_instance is not None ):
            
                # not None - store it and return it.
                uuid_id_type_OUT = self.set_article_uuid_id_type( id_type_instance )
            
            else:
            
                # no.  Hmmm.  So, we have a default name passed in.  Try to use
                #     that.
                id_type_name = default_name_IN

                # got a name?
                if ( ( id_type_name is not None ) and ( id_type_name != "" ) ):
                
                    # yes.  Use it to lookup.
                    id_type_instance = Entity_Identifier_Type.get_type_for_name( id_type_name )
                    
                #-- END check to see if name set in instance. --#
            
                # got an instance now?
                if ( id_type_instance is not None ):
                
                    # yes.  return it.
                    uuid_id_type_OUT = id_type_instance
                    
                    # do we store it and update the internal name and instance?
                    if ( update_on_default_IN == True ):
                    
                        # we do.  update.
                        self.set_article_uuid_id_type_name( id_type_name, False )
                        uuid_id_type_OUT = self.set_article_uuid_id_type( id_type_instance )
                    
                    #-- END check to see if we update when we fall back to default --#
                
                else:
                
                    # no.  Hmmm.  At this point, log message, give up and return None.
                    log_message = "ERROR - Could not find valid Entity_Identifier_Type instance ( self: {}; default: {} ).  Returning None.".format( self.article_uuid_id_type_name, id_type_name )
                    self.output_message( log_message, do_print_IN = True, log_level_code_IN = logging.INFO )        
                    uuid_id_type_OUT = None
                    
                #-- END check to see if default name returned a type. --#
            
            #-- END check to see if we found instance for name --#
        
        #-- END check to see if type stored in instance. --#
        
        return uuid_id_type_OUT
        
    #-- END method get_article_uuid_id_type() --#
    

    def create_article_entity( self, instance_IN ):
        
        '''
        Accepts an Article instance, creates and populates an entity for the
            Article based on the contents of the instance, returns the entity
            instance.
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
        identifier_source = None
        
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
    
                # make sure we return it at this point, since it has been
                #    created and stored in database.
                entity_OUT = entity_instance
    
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
                                                  
                # ! TODO - figure out other traits to add.
    
                # ==> add identifiers
    
                # ----> for django ID in this system.
                identifier_type = Entity_Identifier_Type.get_type_for_name( self.ENTITY_ID_TYPE_ARTICLE_SOURCENET_ID )
                identifier_uuid = article_instance.id
                entity_instance.set_identifier( identifier_uuid,
                                                name_IN = identifier_type.name,
                                                entity_identifier_type_IN = identifier_type )
                
                # ----> for unique identifier.
                identifier_type = self.get_article_uuid_id_type( default_name_IN = self.ENTITY_ID_TYPE_ARTICLE_NEWSBANK_ID )
                identifier_uuid = article_instance.unique_identifier
                entity_instance.set_identifier( identifier_uuid,
                                                name_IN = identifier_type.name,
                                                entity_identifier_type_IN = identifier_type )
                                                
                # ----> generic archive id
                # is there an archive_id and archive_source?
                identifier_uuid = article_instance.archive_id
                identifier_source = article_instance.archive_source
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
                
                    # archive ID and source present.  Create identifier.
                    identifier_type = Entity_Identifier_Type.get_type_for_name( self.ENTITY_ID_TYPE_ARTICLE_ARCHIVE_IDENTIFIER )
                    entity_instance.set_identifier( identifier_uuid,
                                                    name_IN = identifier_type.name,
                                                    source_IN = identifier_source,
                                                    entity_identifier_type_IN = identifier_type )
                                                
                #-- END check to see if generic archive ID. --#
                
                # ----> generic permalink
                # permalink set?
                identifier_uuid = article_instance.permalink
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
        
        else:
        
            # Article instance passed in is None.  return None.
            entity_OUT = None    
        
        #-- END check to see if instance is None --#
        
        return entity_OUT
        
    #-- END method create_article_entity() --#


    def process_articles( self, article_qs_IN ):
        
        # declare variables
        me = "process_articles"
        article_qs = None
        current_article = None
        current_article_id = None
        article_data_qs = None
        article_data_count = None
        article_data_instance = None
        article_entity = None
        
        # declare variables - auditing
        good_counter = None
        more_than_one_counter = None
        zero_counter = None
        unexpected_counter = None
        
        # initialization
        article_qs = article_qs_IN
        automated_coder_user = ArticleCoder.get_automated_coding_user()
        
        # loop over articles
        good_counter = 0
        more_than_one_counter = 0
        zero_counter = 0
        unexpected_counter = 0
        for current_article in article_qs:
            
            current_article_id = current_article.id
            
            # create article entity?  For now, no, only those with coding.
            # article_entity = self.create_article_entity( current_article )
            
            # retrieve Article_Data created by automated coder...
            article_data_qs = current_article.article_data_set.filter( coder = automated_coder_user )
        
            # ...and specifically coded using OpenCalais V2...
            article_data_qs = article_data_qs.filter( coder_type = OpenCalaisV2ArticleCoder.CONFIG_APPLICATION )
            
            # article_data_count
            article_data_count = article_data_qs.count()
            
            # got 1?
            if ( article_data_count == 1 ):
                
                # got one.  Process.
                good_counter += 1
                article_data_instance = article_data_qs.get()
                
                # create article entity.
                article_entity = self.create_article_entity( current_article )
                
            elif ( article_data_count > 1 ):
                
                # more than one.  Hmmm.
                more_than_one_counter += 1
                log_message = "ERROR - Article: {} - More than one Article_Data instance found ( {} ).  Moving to next article.".format( current_article_id, article_data_count )
                self.output_message( log_message, do_print_IN = True, log_level_code_IN = logging.INFO )        
        
                
            elif ( article_data_count == 0 ):
                
                # none.  ERROR.  move on.
                zero_counter += 1
                log_message = "ERROR - Article: {} - No Article_Data instances found ( {} ).  Moving to next article.".format( current_article_id, article_data_count )
                self.output_message( log_message, do_print_IN = True, log_level_code_IN = logging.INFO )        
        
            else:
            
                # unexpected.  ERROR.
                unexpected_counter += 1
                log_message = "ERROR - Article: {} - Article_Data count ( {} ) wasn't 1, > 1, or 0 - Unexpected...".format( current_article_id, article_data_count )
                self.output_message( log_message, do_print_IN = True, log_level_code_IN = logging.INFO )        
                
            #-- END check to see how many Article_Data. --#
            
        #-- END loop over articles --#
        
        log_message = "\nSummary:"
        self.output_message( log_message, do_print_IN = True, log_level_code_IN = logging.INFO )        
        log_message = "- good count: {}".format( good_counter )
        self.output_message( log_message, do_print_IN = True, log_level_code_IN = logging.INFO )        
        log_message = "- > 1 count: {}".format( more_than_one_counter )
        self.output_message( log_message, do_print_IN = True, log_level_code_IN = logging.INFO )        
        log_message = "- 0 count: {}".format( zero_counter )
        self.output_message( log_message, do_print_IN = True, log_level_code_IN = logging.INFO )        
        log_message = "- unexpected count: {}".format( unexpected_counter )
        self.output_message( log_message, do_print_IN = True, log_level_code_IN = logging.INFO )
    
    #-- END method process_articles() --#


    def set_article_uuid_id_type( self, value_IN ):
        
        # return reference
        uuid_id_type_OUT = None
        
        # declare variables
        me = "set_article_uuid_id_type"
        id_type_instance = None
        
        # got an instance.
        id_type_instance = value_IN
        
        # store it
        self.article_uuid_id_type = id_type_instance
        
        # return it.
        uuid_id_type_OUT = self.article_uuid_id_type

        return uuid_id_type_OUT
        
    #-- END method set_article_uuid_id_type() --#
    

    def set_article_uuid_id_type_name( self, value_IN, do_get_instance_IN = True ):
        
        # return reference
        uuid_id_type_OUT = None
        
        # declare variables
        me = "set_article_uuid_id_type_name"
        id_type_name = None
        id_type_instance = None
        
        # get name
        if ( ( value_IN is not None ) and ( value_IN != "" ) ):
        
            # got a value.
            id_type_name = value_IN
            
            # store it
            self.article_uuid_id_type_name = id_type_name
            
            # get instance?
            if ( do_get_instance_IN ):
            
                # yes - will return None if not found.
                id_type_instance = Entity_Identifier_Type.get_type_for_name( id_type_name )
                uuid_id_type_OUT = self.set_article_uuid_id_type( id_type_instance )
                
            #-- END check to see if we are to retrieve and store instance --#
        
        #-- END check to see if value --#
        
        return uuid_id_type_OUT
        
    #-- END method set_article_uuid_id_type_name() --#
    

#-- END class ExportToContext --#