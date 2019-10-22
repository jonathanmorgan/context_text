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
    ENTITY_ID_TYPE_PERMALINK = ContextTextBase.CONTEXT_ENTITY_ID_TYPE_PERMALINK
    
    # entity identifier types - articles
    ENTITY_ID_TYPE_ARTICLE_ARCHIVE_IDENTIFIER = ContextTextBase.CONTEXT_ENTITY_ID_TYPE_ARTICLE_ARCHIVE_IDENTIFIER
    ENTITY_ID_TYPE_ARTICLE_SOURCENET_ID = ContextTextBase.CONTEXT_ENTITY_ID_TYPE_ARTICLE_SOURCENET_ID
    ENTITY_ID_TYPE_ARTICLE_NEWSBANK_ID = ContextTextBase.CONTEXT_ENTITY_ID_TYPE_ARTICLE_NEWSBANK_ID
    ENTITY_ID_TYPE_PERSON_OPEN_CALAIS_UUID = ContextTextBase.CONTEXT_ENTITY_ID_TYPE_NAME_PERSON_OPEN_CALAIS_UUID
    ENTITY_ID_TYPE_PERSON_SOURCENET_ID = ContextTextBase.CONTEXT_ENTITY_ID_TYPE_NAME_PERSON_SOURCENET_ID
    
    # entity identifier types - default
    ENTITY_ID_TYPE_DEFAULT = ContextTextBase.CONTEXT_ENTITY_ID_TYPE_PERMALINK
    
    # entity types
    ENTITY_TYPE_SLUG_ARTICLE = ContextTextBase.CONTEXT_ENTITY_TYPE_SLUG_ARTICLE
    ENTITY_TYPE_SLUG_NEWSPAPER = ContextTextBase.CONTEXT_ENTITY_TYPE_SLUG_NEWSPAPER
    ENTITY_TYPE_SLUG_PERSON = ContextTextBase.CONTEXT_ENTITY_TYPE_SLUG_PERSON
    
    # trait names
    TRAIT_NAME_PUB_DATE = ContextTextBase.CONTEXT_TRAIT_NAME_PUB_DATE
    TRAIT_NAME_SOURCENET_NEWSPAPER_ID = ContextTextBase.CONTEXT_TRAIT_NAME_SOURCENET_NEWSPAPER_ID
    

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
        Accepts an Article instance, creates and populates an entity for the
            Article based on the contents of the instance, returns the entity
            instance.
        '''
        
        # return reference
        entity_OUT = None
        
        # declare variables
        article_instance = None
        
        # declare variables - create new.
        entity_instance = None
        
        # make sure an article was passed in.
        article_instance = instance_IN
        if ( article_instance is not None ):

            # ask the article to make its entity.
            entity_instance = article_instance.update_entity()
            entity_OUT = entity_instance
        
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