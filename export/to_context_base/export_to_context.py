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
from context.models import Entity_Relation
from context.models import Entity_Relation_Type

# context_text imports
from context_text.article_coding.article_coding import ArticleCoder
from context_text.article_coding.article_coding import ArticleCoding
from context_text.article_coding.open_calais_v2.open_calais_v2_article_coder import OpenCalaisV2ArticleCoder
from context_text.collectors.newsbank.newspapers.GRPB import GRPB
from context_text.collectors.newsbank.newspapers.DTNB import DTNB
from context_text.models import Article
from context_text.models import Article_Author
from context_text.models import Article_Data
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


    @classmethod
    def create_article_entity( cls, instance_IN ):
        
        '''
        Accepts an Article instance, creates and populates an entity for the
            Article based on the contents of the instance, returns the entity
            instance.
        '''
        
        # return reference
        entity_OUT = None
        
        # call the standard method
        entity_OUT = cls.create_entity_container_entity( instance_IN )
        
        return entity_OUT
        
    #-- END method create_article_entity() --#


    @classmethod
    def create_entity_container_entity( cls, entity_container_IN ):
        
        '''
        Accepts an AbstractEntityContainer child instance, creates and populates
            an entity based on the contents of the instance, returns the entity
            instance.
        '''
        
        # return reference
        entity_OUT = None
        
        # declare variables
        entity_container = None
        
        # declare variables - create new.
        entity_instance = None
        
        # make sure an isntance was passed in.
        entity_container = entity_container_IN
        if ( entity_container is not None ):

            # ask the instance to make its entity.
            entity_instance = entity_container.update_entity()
            entity_OUT = entity_instance
        
        else:
        
            # instance passed in is None.  return None.
            entity_OUT = None    
        
        #-- END check to see if instance is None --#
        
        return entity_OUT
        
    #-- END method create_entity_container_entity() --#


    @classmethod
    def create_person_entity( cls, instance_IN ):
        
        '''
        Accepts a Person instance, creates and populates an entity for the
            Person based on the contents of the instance, returns the entity
            instance.
        '''
        
        # return reference
        entity_OUT = None
        
        # call the standard method
        entity_OUT = cls.create_entity_container_entity( instance_IN )
        
        return entity_OUT
                
    #-- END method create_person_entity() --#


    @classmethod
    def make_author_entity_list( cls, article_data_IN ):
        
        # return reference
        list_OUT = None
        
        # declare variables
        me = "make_author_entity_list"
        status_message = None
        author_entity_list = None
        article_data_instance = None
        author_qs = None
        article_author = None
        current_person = None
        person_entity = None
        
        # check to make sure we have Article_Data.
        if ( article_data_IN is not None ):
        
            # init
            article_data_instance = article_data_IN
            author_entity_list = []
            
            # get QuerySet of Article_Author instances and loop.    
            author_qs = article_data_instance.article_author_set.all()
            for article_author in author_qs:
            
                # get nested person.
                current_person = article_author.person

                # create their entity.
                person_entity = cls.create_person_entity( current_person )
                
                # store entity for making relations.
                author_entity_list.append( person_entity )

            #-- END loop over authors --#
        
            # return the list
            list_OUT = author_entity_list
        
        else:
        
            # No Article_Data passed in.  Return None.
            list_OUT = None
            status_message = "In {}(): no Article_Data passed in, can't create author entity list".format( me )
            cls.output_debug( status_message, method_IN = me, do_print_IN = True )
            
        #-- END check to see if Article_Data. --#
        
        return list_OUT
        
    #-- END class method make_author_entity_list() --#
    

    @classmethod
    def make_relation_trait_dict( cls, article_entity_IN = None, article_data_IN = None ):
        
        # return reference
        dict_OUT = None
        
        # declare variables
        trait_dict = None
        trait_name = None
        entity_trait = None
        trait_value = None
        coder = None
        coder_id = None
        coder_username = None
        coder_type = None
        
        # init
        trait_dict = {}
        
        # got article entity?
        if ( article_entity_IN is not None ):

            # pub_date
            trait_name = ContextTextBase.CONTEXT_TRAIT_NAME_PUB_DATE
            entity_trait = article_entity_IN.get_trait( ContextTextBase.CONTEXT_TRAIT_NAME_PUB_DATE )
            trait_value = entity_trait.get_trait_value()
            trait_dict[ trait_name ] = trait_value
            #relation_trait_filter_dict[ trait_name ] = trait_value
            
            # pull in identifier with sourcenet django ID
            identifier_name = Article.ENTITY_ID_TYPE_ARTICLE_SOURCENET_ID
            identifier_type = Entity_Identifier_Type.get_type_for_name( identifier_name )
            entity_identifier = article_entity_IN.get_identifier( identifier_name, id_type_IN = identifier_type )
            identifier_uuid = entity_identifier.uuid
            trait_dict[ identifier_name ] = identifier_uuid
            #relation_trait_filter_dict[ identifier_name ] = identifier_uuid
            
        #-- END check to see if we have an article entity for traits. --#

        # do we have Article_Data?
        if ( article_data_IN is not None ):
        
            # we do.  Retrieve the coder and coder type.
            coder = article_data_IN.coder
            coder_type = article_data_IN.coder_type
            
            # is there a coder?
            if ( coder is not None ):
            
                # yes - get ID and username.
                coder_id = coder.id
                coder_username = coder.username
                
                # add them to the dictionary.
                
                # coder_id
                trait_name = ContextTextBase.CONTEXT_TRAIT_NAME_CODER_ID
                trait_value = coder_id
                trait_dict[ trait_name ] = trait_value
                # ? relation_trait_filter_dict[ trait_name ] = trait_value

                # coder_username                    
                trait_name = ContextTextBase.CONTEXT_TRAIT_NAME_CODER_USERNAME
                trait_value = coder_username
                trait_dict[ trait_name ] = trait_value
                # ? relation_trait_filter_dict[ trait_name ] = trait_value
            
            #-- END check to see if coder --#
        
            # got a coder_type?
            if ( ( coder_type is not None ) and ( coder_type != "" ) ):
            
                # yes.  Add it as a trait.
                trait_name = ContextTextBase.CONTEXT_TRAIT_NAME_CODER_TYPE
                trait_value = coder_type
                trait_dict[ trait_name ] = trait_value
                # ? relation_trait_filter_dict[ trait_name ] = trait_value

            #-- END check to see if coder_type. --#                    

        #-- END check to see if Article_Data --#

        # return the dictionary.
        dict_OUT = trait_dict
        
        return dict_OUT
        
    #-- END class method make_relation_trait_dict() --#
    

    @classmethod
    def make_subject_entity_list( cls, article_data_IN, limit_to_sources_IN = False, include_sources_in_subjects_IN = True ):
        
        # return reference
        list_OUT = None
        
        # declare variables
        me = "make_subject_entity_list"
        status_message = None
        subject_entity_list = None
        source_entity_list = None
        article_data_instance = None
        subject_qs = None
        article_subject = None
        current_person = None
        person_entity = None
        
        # check to make sure we have Article_Data.
        if ( article_data_IN is not None ):
        
            # init
            article_data_instance = article_data_IN
            subject_entity_list = []
            source_entity_list = []
            subject_qs = article_data_instance.article_subject_set.all()
            for article_subject in subject_qs:
            
                # get nested person.
                current_person = article_subject.person
                subject_type = article_subject.subject_type

                # create their entity.
                person_entity = cls.create_person_entity( current_person )
                
                # store based on subject_type so we can make relations.
                if ( subject_type == Article_Subject.SUBJECT_TYPE_MENTIONED ):
                
                    # simple subject, not quoted
                    subject_entity_list.append( person_entity )
                    
                elif ( subject_type == Article_Subject.SUBJECT_TYPE_QUOTED ):
                
                    # source
                    source_entity_list.append( person_entity )
                    
                    # and subject? (Default is yes - source is also a subject).
                    if ( include_sources_in_subjects_IN == True ):
                    
                        # yes - add it.
                        subject_entity_list.append( person_entity )
                        
                    #-- END check to see if we consider a source also a subject --#
                    
                else:
                
                    # unknown or empty subject type.  Assume simple subject.
                    subject_entity_list.append( person_entity )
                    
                #-- END check subject_type --#
                
            #-- END loop over subjects. --#

            # return a list
            if ( limit_to_sources_IN == False ):

                # return subject list
                list_OUT = subject_entity_list
                
            elif ( limit_to_sources_IN == True ):
            
                # just return source list
                list_OUT = source_entity_list
                
            else:
            
                # huh? just subjects.
                list_OUT = subject_entity_list
                
            #-- END check to see what we return. --#
        
        else:
        
            # No Article_Data passed in.  Return None.
            list_OUT = None
            status_message = "In {}(): no Article_Data passed in, can't create subject entity list".format( me )
            cls.output_debug( status_message, method_IN = me, do_print_IN = True )
            
        #-- END check to see if Article_Data. --#
        
        return list_OUT
        
    #-- END class method make_subject_entity_list() --#


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


    def create_article_relations( self,
                                  article_entity_IN,
                                  author_entity_list_IN = None,
                                  subject_entity_list_IN = None,
                                  source_entity_list_IN = None,
                                  article_data_IN = None ):
                                      
        '''
        If Article_Data passed in, assuming all are based on this single
            Article_Data instance, so adding metadata traits on the coder and 
            coder type to provide information on how the relations were
            captured.
        '''
                          
        # return reference
        status_OUT = None
        
        # declare variables
        me = "create_article_relations"
        status_message = None
        status_code = None
        result_status = None
        result_status_is_error = None
        relation_type = None
        trait_dict = None
        entity_trait = None
        trait_value = None
        trait_name = None
        entity_identifier = None
        identifier_type = None
        identifier_name = None
        identifier_uuid = None
        relation = None
        relation_trait_filter_dict = None
        coder = None
        coder_id = None
        coder_username = None
        coder_type = None

        # declare variables - looping over people to make relations.
        relation_type_slug = None
        from_entity_list = None
        from_entity = None
        from_entity_id = None
        to_entity_list = None
        to_entity = None
        to_entity_id = None
        through_entity = None
        
        # init status container
        status_OUT = StatusContainer()
        status_OUT.set_status_code( StatusContainer.STATUS_CODE_SUCCESS )
        
        # first, see if article entity passed in.
        if ( article_entity_IN is not None ):
        
            # traits to filter relations on.
            # - include traits for pub_date and django/sourcenet ID of article.
            relation_trait_filter_dict = self.make_relation_trait_dict( article_entity_IN = article_entity_IN )
            
            # traits for actual relations, both article info and coder
            #     information from Article_Data.
            trait_dict = self.make_relation_trait_dict( article_entity_IN = article_entity_IN,
                                                        article_data_IN = article_data_IN )            
                    
            #------------------------------------------------------------------#
            # ! ----> Entity_Relation_Type slugs - FROM ARTICLE
            from_entity = article_entity_IN

            # ! --------> CONTEXT_RELATION_TYPE_SLUG_AUTHOR = "author"    # FROM article TO reporter.
            relation_type_slug = ContextTextBase.CONTEXT_RELATION_TYPE_SLUG_AUTHOR
            relation_type = Entity_Relation_Type.objects.get( slug = relation_type_slug )
            to_entity_list = author_entity_list_IN

            # got entities in list?
            if ( ( to_entity_list is not None ) and ( len( to_entity_list ) > 0 ) ):
            
                # yes, there are entities.  Loop.
                for to_entity in to_entity_list:
                
                    # create relation if no match of FROM, TO, type, and pub_date.
                    relation = Entity_Relation.create_entity_relation( from_IN = from_entity,
                                                                       to_IN = to_entity,
                                                                       type_IN = relation_type,
                                                                       trait_name_to_value_map_IN = trait_dict,
                                                                       match_trait_dict_IN = relation_trait_filter_dict )
                
                #-- END loop over TO entities --#
            
            #-- END check to see if entities in list. --#

            # ! --------> CONTEXT_RELATION_TYPE_SLUG_SOURCE = "source"    # FROM article TO source person.
            relation_type_slug = ContextTextBase.CONTEXT_RELATION_TYPE_SLUG_SOURCE
            relation_type = Entity_Relation_Type.objects.get( slug = relation_type_slug )
            to_entity_list = source_entity_list_IN

            # got entities in list?
            if ( ( to_entity_list is not None ) and ( len( to_entity_list ) > 0 ) ):
            
                # yes, there are entities.  Loop.
                for to_entity in to_entity_list:
                
                    # create relation if no match of FROM, TO, type, and pub_date.
                    relation = Entity_Relation.create_entity_relation( from_IN = from_entity,
                                                                       to_IN = to_entity,
                                                                       type_IN = relation_type,
                                                                       trait_name_to_value_map_IN = trait_dict,
                                                                       match_trait_dict_IN = relation_trait_filter_dict )
                
                #-- END loop over TO entities --#
            
            #-- END check to see if entities in list. --#


            # ! --------> CONTEXT_RELATION_TYPE_SLUG_SUBJECT = "subject"  # FROM article TO subject person.
            relation_type_slug = ContextTextBase.CONTEXT_RELATION_TYPE_SLUG_SUBJECT
            relation_type = Entity_Relation_Type.objects.get( slug = relation_type_slug )
            to_entity_list = subject_entity_list_IN

            # got entities in list?
            if ( ( to_entity_list is not None ) and ( len( to_entity_list ) > 0 ) ):
            
                # yes, there are entities.  Loop.
                for to_entity in to_entity_list:
                
                    # create relation if no match of FROM, TO, type, and pub_date.
                    relation = Entity_Relation.create_entity_relation( from_IN = from_entity,
                                                                       to_IN = to_entity,
                                                                       type_IN = relation_type,
                                                                       trait_name_to_value_map_IN = trait_dict,
                                                                       match_trait_dict_IN = relation_trait_filter_dict )
                
                #-- END loop over TO entities --#
            
            #-- END check to see if entities in list. --#
    
            #------------------------------------------------------------------#
            # ! ----> Entity_Relation_Type slugs - FROM reporter/author
            through_entity = article_entity_IN
            from_entity_list = author_entity_list_IN
            
            # got from entities?
            if ( ( from_entity_list is not None ) and ( len( from_entity_list ) > 0 ) ):
            
                # loop over entities for FROM
                for from_entity in from_entity_list:
                
                    # get ID
                    from_entity_id = from_entity.id
            
                    # ! --------> CONTEXT_RELATION_TYPE_SLUG_MENTIONED = "mentioned"  # FROM reporter/author TO subject THROUGH article (includes subjects and sources).
                    relation_type_slug = ContextTextBase.CONTEXT_RELATION_TYPE_SLUG_MENTIONED
                    relation_type = Entity_Relation_Type.objects.get( slug = relation_type_slug )
                    to_entity_list = subject_entity_list_IN
        
                    # got entities in TO list?
                    if ( ( to_entity_list is not None ) and ( len( to_entity_list ) > 0 ) ):
                    
                        # yes, there are people.  Loop.
                        for to_entity in to_entity_list:
                        
                            # create relation if no match of FROM, TO, THROUGH, type, and pub_date.
                            relation = Entity_Relation.create_entity_relation( from_IN = from_entity,
                                                                               to_IN = to_entity,
                                                                               through_IN = through_entity,
                                                                               type_IN = relation_type,
                                                                               trait_name_to_value_map_IN = trait_dict,
                                                                               match_trait_dict_IN = relation_trait_filter_dict )
                        
                        #-- END loop over TO entities --#
                    
                    #-- END author-to-subject check to see if TO entities in list. --#

                    # ! --------> CONTEXT_RELATION_TYPE_SLUG_QUOTED = "quoted"  # FROM reporter TO source THROUGH article.
                    relation_type_slug = ContextTextBase.CONTEXT_RELATION_TYPE_SLUG_QUOTED
                    relation_type = Entity_Relation_Type.objects.get( slug = relation_type_slug )
                    to_entity_list = source_entity_list_IN
        
                    # got entities in TO list?
                    if ( ( to_entity_list is not None ) and ( len( to_entity_list ) > 0 ) ):
                    
                        # yes, there are people.  Loop.
                        for to_entity in to_entity_list:
                        
                            # create relation if no match of FROM, TO, THROUGH, type, and pub_date.
                            relation = Entity_Relation.create_entity_relation( from_IN = from_entity,
                                                                               to_IN = to_entity,
                                                                               through_IN = through_entity,
                                                                               type_IN = relation_type,
                                                                               trait_name_to_value_map_IN = trait_dict,
                                                                               match_trait_dict_IN = relation_trait_filter_dict )
                        
                        #-- END loop over TO entities --#
                    
                    #-- END author-to-subject check to see if TO entities in list. --#

                    # ! --------> CONTEXT_RELATION_TYPE_SLUG_SHARED_BYLINE = "shared_byline"  # FROM author TO author THROUGH article.
                    relation_type_slug = ContextTextBase.CONTEXT_RELATION_TYPE_SLUG_SHARED_BYLINE
                    relation_type = Entity_Relation_Type.objects.get( slug = relation_type_slug )
                    to_entity_list = author_entity_list_IN
        
                    # got people in list?
                    if ( ( to_entity_list is not None ) and ( len( to_entity_list ) > 0 ) ):
                    
                        # yes, there are people.  Loop.
                        for to_entity in to_entity_list:
                        
                            # get ID
                            to_entity_id = to_entity.id
                            
                            # only create tie if FROM entity != TO entity
                            if ( from_entity_id != to_entity_id ):
                        
                                # create relation if no match of FROM, TO, THROUGH, type, and pub_date.
                                relation = Entity_Relation.create_entity_relation( from_IN = from_entity,
                                                                                   to_IN = to_entity,
                                                                                   through_IN = through_entity,
                                                                                   type_IN = relation_type,
                                                                                   trait_name_to_value_map_IN = trait_dict,
                                                                                   match_trait_dict_IN = relation_trait_filter_dict )
                                                                                   
                            #-- END check to make sure we don't make self-ties --#
                        
                        #-- END loop over people --#
                    
                    #-- END author-to-author check to see if person entities in list. --#

                #-- END loop over author list

            #-- END check to see if author list? --#

            #------------------------------------------------------------------#
            # ! ----> Entity_Relation_Type slugs - FROM source
            through_entity = article_entity_IN
            from_entity_list = source_entity_list_IN

            # got a FROM list?
            if ( ( from_entity_list is not None ) and ( len( from_entity_list ) > 0 ) ):
            
                # loop over entities for FROM
                for from_entity in from_entity_list:
                
                    # get id
                    from_entity_id = from_entity.id
            
                    # ! --------> CONTEXT_RELATION_TYPE_SLUG_SAME_ARTICLE_SOURCES = "same_article_sources"    # FROM source person TO source person THROUGH article.
                    relation_type_slug = ContextTextBase.CONTEXT_RELATION_TYPE_SLUG_SAME_ARTICLE_SOURCES
                    relation_type = Entity_Relation_Type.objects.get( slug = relation_type_slug )
                    to_entity_list = source_entity_list_IN
        
                    # got people in list?
                    if ( ( to_entity_list is not None ) and ( len( to_entity_list ) > 0 ) ):
                    
                        # yes, there are people.  Loop.
                        for to_entity in to_entity_list:
                        
                            # get ID
                            to_entity_id = to_entity.id
                            
                            # only create tie if FROM entity != TO entity
                            if ( from_entity_id != to_entity_id ):
                        
                                # create relation if no match of FROM, TO, THROUGH, type, and pub_date.
                                relation = Entity_Relation.create_entity_relation( from_IN = from_entity,
                                                                                   to_IN = to_entity,
                                                                                   through_IN = through_entity,
                                                                                   type_IN = relation_type,
                                                                                   trait_name_to_value_map_IN = trait_dict,
                                                                                   match_trait_dict_IN = relation_trait_filter_dict )
                                                                                   
                            #-- END check to make sure we don't make self-ties --#
                        
                        #-- END loop over TO entities --#
                    
                    #-- END check to see if TO entities in list. --#

                #-- END loop over FROM list

            #-- END check to see if FROM list --#

            #------------------------------------------------------------------#
            # ! ----> Entity_Relation_Type slugs - FROM subject
            through_entity = article_entity_IN
            from_entity_list = subject_entity_list_IN

            # got a from list?
            if ( ( from_entity_list is not None ) and ( len( from_entity_list ) > 0 ) ):
            
                # loop over subject entities for FROM
                for from_entity in from_entity_list:
                
                    # get id
                    from_entity_id = from_entity.id
            
                    # ! --------> CONTEXT_RELATION_TYPE_SLUG_SAME_ARTICLE_SUBJECTS = "same_article_subjects"  # FROM subject person TO subject person THROUGH article (includes subjects and sources).
                    relation_type_slug = ContextTextBase.CONTEXT_RELATION_TYPE_SLUG_SAME_ARTICLE_SUBJECTS
                    relation_type = Entity_Relation_Type.objects.get( slug = relation_type_slug )
                    to_entity_list = subject_entity_list_IN
        
                    # got people in list?
                    if ( ( to_entity_list is not None ) and ( len( to_entity_list ) > 0 ) ):
                    
                        # yes, there are people.  Loop.
                        for to_entity in to_entity_list:
                        
                            # get ID
                            to_entity_id = to_entity.id
                            
                            # only create tie if FROM entity != TO entity
                            if ( from_entity_id != to_entity_id ):
                        
                                # create relation if no match of FROM, TO, THROUGH, type, and pub_date.
                                relation = Entity_Relation.create_entity_relation( from_IN = from_entity,
                                                                                   to_IN = to_entity,
                                                                                   through_IN = through_entity,
                                                                                   type_IN = relation_type,
                                                                                   trait_name_to_value_map_IN = trait_dict,
                                                                                   match_trait_dict_IN = relation_trait_filter_dict )
                                                                                   
                            #-- END check to make sure we don't make self-ties --#
                        
                        #-- END loop over TO entities --#
                    
                    #-- END check to see if TO entities in list. --#

                #-- END loop over FROM list

            #-- END check to see if FROM list --#
                
        else:
        
            # ERROR - no article entity passed in.
            status_message = "In {}: ERROR - no article entity in, so no relations to create.".format( me )
            self.output_message( status_message, do_print_IN = True, log_level_code_IN = logging.ERROR )
            status_code = StatusContainer.STATUS_CODE_ERROR
            status_OUT.set_status_code( status_code )
            status_OUT.add_message( status_message )
        
        #-- END check to see if article entity passed in. --#
        
        return status_OUT                  

    #-- END method create_article_relations() --#


    def create_newspaper_relations( self,
                                    newspaper_entity_IN,
                                    article_entity_IN,
                                    author_entity_list_IN = None,
                                    subject_entity_list_IN = None,
                                    source_entity_list_IN = None,
                                    article_data_IN = None ):
                          
        # return reference
        status_OUT = None
        
        # declare variables
        me = "create_newspaper_relations"
        status_message = None
        status_code = None
        result_status = None
        result_status_is_error = None
        relation_type = None
        trait_dict = None
        entity_trait = None
        trait_value = None
        trait_name = None
        entity_identifier = None
        identifier_type = None
        identifier_name = None
        identifier_uuid = None
        relation = None
        relation_trait_filter_dict = None
        person_entity = None
        
        # init status container
        status_OUT = StatusContainer()
        status_OUT.set_status_code( StatusContainer.STATUS_CODE_SUCCESS )
        
        # first, see if newspaper entity passed in.
        if ( newspaper_entity_IN is not None ):
        
            # shared traits for these relations, also used to filter.
            # - includes article's pub_date and sourcenet article ID.
            trait_dict = self.make_relation_trait_dict( article_entity_IN = article_entity_IN )
            relation_trait_filter_dict = trait_dict
                        
            # ! ----> "newspaper_article"    # FROM newspaper TO article.
        
            # got article entity?
            if ( article_entity_IN is not None ):

                # get type
                relation_type = Entity_Relation_Type.objects.get( slug = ContextTextBase.CONTEXT_RELATION_TYPE_SLUG_NEWSPAPER_ARTICLE )
                
                # create relation if no match of FROM, TO, type, pub_date, and article ID.
                relation = Entity_Relation.create_entity_relation( from_IN = newspaper_entity_IN,
                                                                   to_IN = article_entity_IN,
                                                                   type_IN = relation_type,
                                                                   trait_name_to_value_map_IN = trait_dict,
                                                                   match_trait_dict_IN = relation_trait_filter_dict )                
            
            #-- END check to see if article entity. --#
            
            # ! ----> "newspaper_reporter"  # FROM newspaper TO person (reporter) THROUGH article.
            relation_type_slug = ContextTextBase.CONTEXT_RELATION_TYPE_SLUG_NEWSPAPER_REPORTER
            relation_type = Entity_Relation_Type.objects.get( slug = relation_type_slug )
            person_entity_list = author_entity_list_IN

            # got people in list?
            if ( ( person_entity_list is not None ) and ( len( person_entity_list ) > 0 ) ):
            
                # yes, there are people.  Loop.
                for person_entity in person_entity_list:
                
                    # create relation if no match of FROM, TO, type, and pub_date.
                    relation = Entity_Relation.create_entity_relation( from_IN = newspaper_entity_IN,
                                                                       to_IN = person_entity,
                                                                       through_IN = article_entity_IN,
                                                                       type_IN = relation_type,
                                                                       trait_name_to_value_map_IN = trait_dict,
                                                                       match_trait_dict_IN = relation_trait_filter_dict )
                
                #-- END loop over people --#
            
            #-- END check to see if person entities in list. --#
                
            # ! ----> "newspaper_subject"    # FROM newspaper TO person (subject, including sources) THROUGH article.
            relation_type_slug = ContextTextBase.CONTEXT_RELATION_TYPE_SLUG_NEWSPAPER_SUBJECT
            relation_type = Entity_Relation_Type.objects.get( slug = relation_type_slug )
            person_entity_list = subject_entity_list_IN

            # got people in list?
            if ( ( person_entity_list is not None ) and ( len( person_entity_list ) > 0 ) ):
            
                # yes, there are people.  Loop.
                for person_entity in person_entity_list:
                
                    # create relation if no match of FROM, TO, type, and pub_date.
                    relation = Entity_Relation.create_entity_relation( from_IN = newspaper_entity_IN,
                                                                       to_IN = person_entity,
                                                                       through_IN = article_entity_IN,
                                                                       type_IN = relation_type,
                                                                       trait_name_to_value_map_IN = trait_dict,
                                                                       match_trait_dict_IN = relation_trait_filter_dict )
                
                #-- END loop over people --#
            
            #-- END check to see if person entities in list. --#
                
            # ! ----> "newspaper_source"      # FROM newspaper TO person (source) THROUGH article.
            relation_type_slug = ContextTextBase.CONTEXT_RELATION_TYPE_SLUG_NEWSPAPER_SOURCE
            relation_type = Entity_Relation_Type.objects.get( slug = relation_type_slug )
            person_entity_list = source_entity_list_IN

            # got people in list?
            if ( ( person_entity_list is not None ) and ( len( person_entity_list ) > 0 ) ):
            
                # yes, there are people.  Loop.
                for person_entity in person_entity_list:
                
                    # create relation if no match of FROM, TO, type, and pub_date.
                    relation = Entity_Relation.create_entity_relation( from_IN = newspaper_entity_IN,
                                                                       to_IN = person_entity,
                                                                       through_IN = article_entity_IN,
                                                                       type_IN = relation_type,
                                                                       trait_name_to_value_map_IN = trait_dict,
                                                                       match_trait_dict_IN = relation_trait_filter_dict )
                
                #-- END loop over people --#
            
            #-- END check to see if person entities in list. --#
                
        else:
        
            # ERROR - no newspaper entity passed in.
            status_message = "ERROR - no newspaper entity in, so no relations to create."
            self.output_message( status_message, do_print_IN = True, log_level_code_IN = logging.ERROR )
            status_code = StatusContainer.STATUS_CODE_ERROR
            status_OUT.set_status_code( status_code )
            status_OUT.add_message( status_message )
        
        #-- END check to see if newspaper entity passed in. --#
        
        return status_OUT                  
                          
    #-- END method create_newspaper_relations() --#


    def create_relations( self,
                          article_data_IN,
                          author_entity_list_IN = None,
                          subject_entity_list_IN = None,
                          source_entity_list_IN = None ):
                          
        # return reference
        status_OUT = None
        
        # declare variables
        me = "create_relations"
        status_message = None
        status_code = None
        article_instance = None
        article_entity = None
        newspaper_instance = None
        newspaper_entity = None
        result_status = None
        result_status_is_error = None
        
        # init status container
        status_OUT = StatusContainer()
        status_OUT.set_status_code( StatusContainer.STATUS_CODE_SUCCESS )
        
        # first, see if Article_Data passed in.
        if ( article_data_IN is not None ):
        
            # first, get article entity.
            article_instance = article_data_IN.article
            article_entity = article_instance.get_entity()
            if ( article_entity is not None ):
            
                # next, get newspaper entity.
                newspaper_instance = article_instance.newspaper
                if ( newspaper_instance is not None ):
                
                    # got a newspaper - try to retrieve entity.
                    newspaper_entity = newspaper_instance.get_entity()
                    
                else:
                
                    # no newspaper, so no newspaper entity.
                    status_message = "no newspaper for article {}, so no newspaper relations.".format( article_instance )
                    self.output_message( status_message, do_print_IN = True, log_level_code_IN = logging.INFO )
                    status_OUT.add_message( status_message )
                    
                #-- END check to see if associated newspaper. --#
                
                # now we start creating relations.
                
                # ! ----> create newspaper-based relations.
                
                # if newspaper entity, we create a set of newspaper relations.
                if ( newspaper_entity is not None ):
                
                    # create newspaper relations
                    result_status = self.create_newspaper_relations( newspaper_entity,
                                                                     article_entity,
                                                                     author_entity_list_IN = author_entity_list_IN,
                                                                     subject_entity_list_IN = subject_entity_list_IN,
                                                                     source_entity_list_IN = source_entity_list_IN,
                                                                     article_data_IN = article_data_IN )
                    result_status_is_error = result_status.is_error()
                    
                    # errors?
                    if ( result_status_is_error == True ):
                    
                        # set status to error, add a message, then nest the
                        #     StatusContainer instance.
                        status_message = "ERROR - errors processing newspaper relations.  See nested StatusContainer for more details."
                        self.output_message( status_message, do_print_IN = True, log_level_code_IN = logging.ERROR )
                        status_code = StatusContainer.STATUS_CODE_ERROR
                        status_OUT.set_status_code( status_code )
                        status_OUT.add_message( status_message )
                        status_OUT.add_status_container( result_status )
                    
                    #-- END check to see if errors. --#
                    
                else:
                
                    # no newspaper entity, so no newspaper relations.
                    status_message = "no newspaper entity, so no newspaper relations.".format( article_instance )
                    self.output_message( status_message, do_print_IN = True, log_level_code_IN = logging.INFO )
                    status_OUT.add_message( status_message )

                #-- END check to see if newspaper entity. --#
                
                # ! ----> create article-based relations.
                result_status = self.create_article_relations( article_entity,
                                                               author_entity_list_IN = author_entity_list_IN,
                                                               subject_entity_list_IN = subject_entity_list_IN,
                                                               source_entity_list_IN = source_entity_list_IN,
                                                               article_data_IN = article_data_IN )                
                result_status_is_error = result_status.is_error()
                
                # errors?
                if ( result_status_is_error == True ):
                
                    # set status to error, add a message, then nest the
                    #     StatusContainer instance.
                    status_message = "ERROR - errors processing article-based relations.  See nested StatusContainer for more details."
                    self.output_message( status_message, do_print_IN = True, log_level_code_IN = logging.ERROR )
                    status_code = StatusContainer.STATUS_CODE_ERROR
                    status_OUT.set_status_code( status_code )
                    status_OUT.add_message( status_message )
                    status_OUT.add_status_container( result_status )
                
                #-- END check to see if errors. --#
                    
            else:
            
                # ERROR - no article entity.
                status_message = "ERROR - no article entity for article {}, so no relations to create.".format( article_instance )
                self.output_message( status_message, do_print_IN = True, log_level_code_IN = logging.ERROR )
                status_code = StatusContainer.STATUS_CODE_ERROR
                status_OUT.set_status_code( status_code )
                status_OUT.add_message( status_message )            
            
            #-- END check to see if article entity present --#
        
        else:
        
            # ERROR - no article passed in.
            status_message = "ERROR - no Article_Data passed in, so no relations to create."
            self.output_message( status_message, do_print_IN = True, log_level_code_IN = logging.ERROR )
            status_code = StatusContainer.STATUS_CODE_ERROR
            status_OUT.set_status_code( status_code )
            status_OUT.add_message( status_message )
        
        #-- END check to see if Article_Data passed in. --#
        
        return status_OUT                  
                          
    #-- END method create_relations() --#


    def process_articles( self, article_qs_IN ):
        
        # declare variables
        me = "process_articles"
        article_qs = None
        current_article = None
        current_article_id = None
        coder_type_list = None
        article_data_q = None
        article_data_qs = None
        article_data_count = None
        article_data_instance = None
        article_entity = None
        current_newspaper = None
        newspaper_entity = None
        author_qs = None
        article_author = None
        subject_qs = None
        article_subject = None
        current_person = None
        subject_type = None
        person_entity = None
        
        # declare variables - relations
        author_entity_list = None
        subject_entity_list = None
        source_entity_list = None
        
        # declare variables - auditing
        good_counter = None
        more_than_one_counter = None
        zero_counter = None
        unexpected_counter = None
        
        # initialization
        article_qs = article_qs_IN
        automated_coder_user = ArticleCoder.get_automated_coding_user()

        # initialization - retrieve a Q to filter Article_Data on automated
        #     coder with type for OpenCalais V2.
        coder_type_list = []
        coder_type_list.append( OpenCalaisV2ArticleCoder.CONFIG_APPLICATION )
        article_data_q = Article_Data.create_q_only_automated( coder_type_list )
        
        # loop over articles
        good_counter = 0
        more_than_one_counter = 0
        zero_counter = 0
        unexpected_counter = 0
        for current_article in article_qs:
            
            current_article_id = current_article.id
            
            # create article entity?  For now, no, only those with coding.
            # article_entity = self.create_article_entity( current_article )
            
            # ! ----> Article_Data

            # retrieve Article_Data by automated coder, type OpenCalais V2.
            article_data_qs = current_article.article_data_set.filter( article_data_q )
        
            # article_data_count
            article_data_count = article_data_qs.count()
            
            # got 1?
            if ( article_data_count == 1 ):
                
                # got one.  Process.
                good_counter += 1
                article_data_instance = article_data_qs.get()
                
                # ! ----> Entities
                
                # ! --------> Article and Newspaper
                # create article entity.
                article_entity = self.create_article_entity( current_article )
                
                # lookup the associated newspaper's entity
                current_newspaper = current_article.newspaper
                newspaper_entity = current_newspaper.entity
                
                # retrieve the people who are referenced in the Article_Data.
                
                # ! --------> Authors (Person)
                # start with authors
                author_entity_list = self.make_author_entity_list( article_data_instance )

                # ! --------> Subjects (Person)
                # subjects
                subject_entity_list = self.make_subject_entity_list( article_data_instance, limit_to_sources_IN = False )
                
                # ! --------> Sources (Person)
                # sources
                source_entity_list = self.make_subject_entity_list( article_data_instance, limit_to_sources_IN = True )
                
                # ! ----> create relations
                
                # now we have entities for article, newspaper, authors,
                #     subjects, and sources.  Time to make relations.
                self.create_relations( article_data_instance,
                                       author_entity_list,
                                       subject_entity_list,
                                       source_entity_list )
                
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