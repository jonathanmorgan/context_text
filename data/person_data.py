from __future__ import unicode_literals

'''
Copyright 2016-present (2016) Jonathan Morgan

This file is part of http://github.com/jonathanmorgan/sourcenet.

sourcenet is free software: you can redistribute it and/or modify it under the terms of the GNU Lesser General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.

sourcenet is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.

You should have received a copy of the GNU Lesser General Public License along with http://github.com/jonathanmorgan/sourcenet. If not, see http://www.gnu.org/licenses/.

Configuration properties for it are stored in django's admins, in the
   django_config application.  The properties for the article_code view are stored in Application
   "sourcenet-UI-article-code":
   - include_fix_person_name - boolean flag, if true outputs additional field to correct name text from article.
'''

# imports

# six - python 2 + 3
import six

# django imports
from django.db.models.query import QuerySet

# python utilities
from python_utilities.logging.logging_helper import LoggingHelper
from python_utilities.status.status_container import StatusContainer

# sourcenet models
from sourcenet.models import Article_Author
from sourcenet.models import Article_Subject
from sourcenet.models import Person


class PersonData( object ):


    #============================================================================
    # constants-ish
    #============================================================================


    # DEBUG
    DEBUG_FLAG = False
    LOGGER_NAME = "sourcenet.data.person_data.PersonData"
    
    # names of reverse lookup classes.
    CLASS_NAME_REVERSE_1_TO_1_OLD = "SingleRelatedObjectDescriptor"
    CLASS_NAME_REVERSE_1_TO_1_NEW = "ReverseOneToOneDescriptor"
    CLASS_NAME_REVERSE_M_TO_1_OLD = "ForeignRelatedObjectsDescriptor"
    CLASS_NAME_REVERSE_M_TO_1_NEW = "ReverseManyToOneDescriptor"
    CLASS_NAME_REVERSE_GENERIC_M_TO_1_OLD = "ReverseGenericRelatedObjectsDescriptor"
    CLASS_NAME_REVERSE_GENERIC_M_TO_1_NEW = "ReverseGenericManyToOneDescriptor"
    CLASS_NAME_M_TO_M_OLD = "ManyRelatedObjectsDescriptor"
    CLASS_NAME_M_TO_M_NEW = "ManyToManyDescriptor"
    
    REVERSE_LOOKUP_CLASS_NAMES = [ CLASS_NAME_REVERSE_1_TO_1_OLD,
                                   CLASS_NAME_REVERSE_1_TO_1_NEW,
                                   CLASS_NAME_REVERSE_M_TO_1_OLD,
                                   CLASS_NAME_REVERSE_M_TO_1_NEW,
                                   CLASS_NAME_REVERSE_GENERIC_M_TO_1_OLD,
                                   CLASS_NAME_REVERSE_GENERIC_M_TO_1_NEW,
                                   CLASS_NAME_M_TO_M_OLD,
                                   CLASS_NAME_M_TO_M_NEW ]
                                   
    
    

    #============================================================================
    # static methods
    #============================================================================


    #============================================================================
    # ! class methods
    #============================================================================

    @classmethod
    def delete_records( cls, record_qs_IN, merge_to_id_IN, do_delete_IN = False, logger_name_IN = None, *args, **kwargs ):
        
        '''
        accepts a QuerySet of records.  calls delete() on each record in the
            QuerySet.  Be careful!

        preconditions: Seriously, BE CAREFUL!!!
        postconditions: deletes everything in the QuerySet.
        '''
        
        # return reference
        status_OUT = StatusContainer()
        
        # declare variables
        me = "delete_records"
        my_logger_name = ""
        debug_message = ""
        current_record = None
        
        # set logger name.
        if ( ( logger_name_IN is not None ) and ( logger_name_IN != "" ) ):
        
            # got one - use it.
            my_logger_name = logger_name_IN
        
        else:
        
            # not set.  Use default.
            my_logger_name = cls.LOGGER_NAME
        
        #-- END check to see if loger name passed in. --#
        
        # got a QuerySet?
        if ( isinstance( record_qs_IN, QuerySet ) == True ):
            
            # yes.  anything in it?
            if ( record_qs_IN.count() > 0 ):
            
                debug_message = "QuerySet IS NOT empty."
                LoggingHelper.output_debug( debug_message, method_IN = me, logger_name_IN = my_logger_name )

                # loop over records.
                for current_record in record_qs_IN:
                
                    debug_message = "Current record: " + str( current_record )
                    LoggingHelper.output_debug( debug_message, method_IN = me, indent_with_IN = "====> ", logger_name_IN = my_logger_name )
                
                    # do we delete?
                    if ( do_delete_IN == True ):
                    
                        # OK...
                        current_record.delete()
                        
                        debug_message = "DELETED!!!"
                        LoggingHelper.output_debug( debug_message, method_IN = me, indent_with_IN = "========> ", logger_name_IN = my_logger_name )
                    
                    #-- END check to see if we delete. --#
                
                #-- END loop over records. --#
        
            else:
            
                debug_message = "QuerySet is EMPTY."
                LoggingHelper.output_debug( debug_message, method_IN = me, indent_with_IN = "====> ", logger_name_IN = my_logger_name )
            
            #-- END check to see if anything in list. --#
            
        else:
        
        #-- END check to see if QuerySet instance passed in. --#
        
        return status_OUT
        
    #-- END class method delete_related_records. --#
        
    
    @classmethod
    def get_function_for_attr_name( cls, record_qs_IN, merge_to_id_IN, do_delete_IN = False, logger_name_IN = None, *args, **kwargs ):
        
        '''
        accepts a QuerySet of records.  calls delete() on each record in the
        '''
        
        pass



    @classmethod
    def get_person_set_names( cls, *args, **kwargs ):
        
        # return reference
        name_list_OUT = []
        
        # declare variables
        attr_list = None
        
        # get all non-standard attributes of Person class.
        attr_list = ObjectHelper.get_user_attributes( Person )
        
        # get list of person "*_set" attributes
        for name, value in six.iteritems( attr_list ):
        
            # check to see if it ends in "_set"
   ...:     if ( name.endswith( "_set" ) == True ):
   ...:         print( name )


    


    @classmethod
    def merge_persons( cls, from_person_id_list_IN, to_person_id_IN, do_updates_IN = True, logger_name_IN = None, *args, **kwargs ):

        '''
        Have to account for references:
        - reliability_names_set
        - article_author_set
        - person_organization_set
        - sourcenet_article_author_original_person_set
        - person_newspaper_set
        - alternate_author_match_set
        - sourcenet_article_subject_original_person_set
        - person_external_uuid_set
        - alternate_name_set
        - reliability_ties_to_set
        - reliability_ties_from_set
        - alternate_subject_match_set
        - article_subject_set
        '''

        # return reference
        status_OUT = StatusContainer()
                
        # declare variables
        me = "switch_persons_in_data"
        debug_message = ""
        my_logger_name = ""
        status_message = ""
        person_id = -1
        person_instance = None
        
        # set logger name.
        if ( ( logger_name_IN is not None ) and ( logger_name_IN != "" ) ):
        
            # got one - use it.
            my_logger_name = logger_name_IN
        
        else:
        
            # not set.  Use default.
            my_logger_name = cls.LOGGER_NAME
        
        #-- END check to see if loger name passed in. --#
        
        # init status container
        status_OUT.set_status_code( StatusContainer.STATUS_CODE_SUCCESS )
        
        # get list of person "*_set"s.
                
        # got a list passed in?
        if ( ( from_person_id_list_IN is not None )
            and ( isinstance( from_person_id_list_IN, list ) == True )
            and ( len( from_person_id_list_IN ) > 0 ) ):
        
            # make sure there is a person to merge to...
            if ( ( to_person_id_IN is not None )
                and ( isinstance( to_person_id_IN, six.integer_types ) == True )
                and ( to_person_id_IN > 0 ) ):
                
                # loop over person list.
                for person_id in from_person_id_list_IN:
                
                    # get person instance.
                    person_instance = Person.objects.get( pk = person_id )
                    
                    #
                    
                #-- END loop over persons. --#

            else:
            
                # no person ID to merge into - nothing to merge.
                status_OUT.set_status_code( StatusContainer.STATUS_CODE_ERROR )
                status_message = "No person ID to merge into, so nothing to merge."
                status_OUT.add_message( status_message )
                
            #-- END check to see if ID to merge into. --#
        
            
        else:
        
            # no list of from person IDs - nothing to merge.
            status_OUT.set_status_code( StatusContainer.STATUS_CODE_ERROR )
            status_message = "No person IDs in list of persons to merge passed in, so nothing to merge."
            status_OUT.add_message( status_message )
            
        #-- END check to see if list of person to merge. --#

        return status_OUT
        
    #-- END class method merge_persons() --#

    @classmethod
    def switch_persons_in_data( cls, from_person_id_IN, to_person_id_IN, do_updates_IN = True, *args, **kwargs ):
        
        '''
        Accepts a FROM person ID, a TO person ID, and an optional flag that
            controls whether or not we actually update, or just generate status
            info.  Pulls in Article_Author and Article_Subject records for the
            FROM user, then if we are updating, for each moves the FROM user to
            the "original_person" field and replaces that user with the TO user
            in the "person" field.
            
        Returns a status container that contains a list of messages detailing
            processing steps that occurred, plus status information.  If errors,
            the status_code will be StatusContainer.STATUS_CODE_ERROR.  If
            success, it will be StatusContainer.STATUS_CODE_SUCCESS.
        '''

        # return reference
        status_OUT = StatusContainer()
                
        # declare variables
        me = "switch_persons_in_data"
        my_logger = None
        status_message = ""
        FROM_person_id = None
        TO_person_id = None
        FROM_person = None
        TO_person = None
        article_author_id_list = []
        article_author_qs = None
        article_author = None
        article_author_id = -1
        article_author_count = -1
        article_subject_id_list = []
        article_subject_qs = None
        article_subject = None
        article_subject_id = -1
        article_subject_count = -1

        # init status to success
        status_OUT.status_code = StatusContainer.STATUS_CODE_SUCCESS

        # first, set the IDs of the persons we will be switching from and to.
        FROM_person_id = from_person_id_IN
        TO_person_id = to_person_id_IN
        
        # Look up Person instances for each.
        FROM_person = Person.objects.get( id = FROM_person_id )
        TO_person = Person.objects.get( id = TO_person_id )
        
        # make sure we found one for each.
        if ( ( FROM_person is not None ) and ( TO_person is not None ) ):
        
            # find all Article_Subject and Article_Author records that refer the the FROM
            #    person.
            article_author_qs = FROM_person.article_author_set.all()
            article_subject_qs = FROM_person.article_subject_set.all()
            
            # loop over author records
            for article_author in article_author_qs:
            
                # get ID, add to list.
                article_author_id = article_author.id
                article_author_id_list.append( article_author_id )
                
                # do updates?
                if ( do_updates_IN == True ):
                
                    # yes - move article_author.person to article_author.original_person
                    article_author.original_person = article_author.person
                    
                    # then set article_author.person to TO_person.
                    article_author.person = TO_person
                    
                    # save
                    article_author.save()
                
                #-- END check to see if we update. --#
            
            #-- END loop over authors --#
        
            # loop over source records
            for article_subject in article_subject_qs:
            
                # get ID, add to list.
                article_subject_id = article_subject.id
                article_subject_id_list.append( article_subject_id )
                
                # do updates?
                if ( do_updates_IN == True ):
                
                    # yes - move article_subject.person to article_subject.original_person
                    article_subject.original_person = article_subject.person
                    
                    # then set article_subject.person to TO_person.
                    article_subject.person = TO_person
                    
                    # save
                    article_subject.save()
                
                #-- END check to see if we update. --#
            
            #-- END loop over sources --#
        
        else:
        
            status_OUT.status_code = StatusContainer.STATUS_CODE_ERROR
            status_message = "ERROR - don't have both FROM and TO persons."
            status_OUT.add_message( status_message )
            
        #-- END check to see if we have FROM and TO persons. --#
        
        # Output summary
        status_message = "Switching associated person FROM: " + str( FROM_person ) + " TO: " + str( TO_person )
        status_OUT.add_message( status_message )
        
        # do updates?
        if ( do_updates_IN == True ):
        
            status_message = "do_updates_IN = True, UPDATED THE FOLLOWING:"
        
        else:
        
            status_message = "do_updates_IN = False, NO CHANGES MADE!"
        
        #-- END check to see if we made updates or not --#article_author_count = len( article_author_id_list )
        status_OUT.add_message( status_message )
        
        article_author_count = len( article_author_id_list )
        article_subject_count = len( article_subject_id_list )
        
        status_message = "Updating " + str( article_author_count ) + " Article_Author instances: " + str( article_author_id_list )
        status_OUT.add_message( status_message )
        
        status_message = "Updating " + str( article_subject_count ) + " Article_Subject instances: " + str( article_subject_id_list )
        status_OUT.add_message( status_message )
        
        return status_OUT
        
    #-- END class method switch_persons_in_data() --#
    

    @classmethod
    def undo_switch_persons_in_data( cls, from_person_id_IN, to_person_id_IN, do_updates_IN = True, *args, **kwargs ):
        
        '''
        Accepts a FROM person ID, a TO person ID, and an optional flag that
            controls whether or not we actually update, or just generate status
            info.  Pulls in Article_Author and Article_Subject records where the
            FROM person is "original_person", then if we are updating, for each 
            moves that user from the "original_person" field to the "person"
            field and then empties the "original_person" field.
            
        Returns a status container that contains a list of messages detailing
            processing steps that occurred, plus status information.  If errors,
            the status_code will be StatusContainer.STATUS_CODE_ERROR.  If
            success, it will be StatusContainer.STATUS_CODE_SUCCESS.
        '''

        # declare variables
        FROM_person_id = None
        TO_person_id = None
        FROM_person = None
        TO_person = None
        article_author_id_list = []
        article_author_qs = None
        article_author = None
        article_author_id = -1
        article_author_count = -1
        article_subject_id_list = []
        article_subject_qs = None
        article_subject = None
        article_subject_id = -1
        article_subject_count = -1

        # first, set the IDs of the persons we will be switching from and to.
        FROM_person_id = from_person_id_IN
        TO_person_id = to_person_id_IN
        
        # Look up Person instances for each.
        FROM_person = Person.objects.get( id = FROM_person_id )
        TO_person = Person.objects.get( id = TO_person_id )
        
        # make sure we found one for each.
        if ( ( FROM_person is not None ) and ( TO_person is not None ) ):
        
            # find all Article_Subject and Article_Author records that refer the the FROM
            #    person.
            article_author_qs = FROM_person.sourcenet_article_author_original_person_set.all()
            article_subject_qs = FROM_person.sourcenet_article_subject_original_person_set.all()
            
            # loop over author records
            for article_author in article_author_qs:
            
                # get ID, add to list.
                article_author_id = article_author.id
                article_author_id_list.append( article_author_id )
                
                # do updates?
                if ( do_updates_IN == True ):
                            
                    # yes.
                    
                    # then set article_author.person to article_author.original_person.
                    article_author.person = article_author.original_person
                    
                    # empty out article_author.original_person.
                    article_author.original_person = None
        
                    # save
                    article_author.save()
                
                #-- END check to see if we update. --#
            
            #-- END loop over authors --#
        
            # loop over subject records
            for article_subject in article_subject_qs:
            
                # get ID, add to list.
                article_subject_id = article_subject.id
                article_subject_id_list.append( article_subject_id )
                
                # do updates?
                if ( do_updates_IN == True ):
                
                    # yes.
                    
                    # then set article_subject.person to article_subject.original_person.
                    article_subject.person = article_subject.original_person
                    
                    # empty out article_subject.original_person.
                    article_subject.original_person = None
        
                    # save
                    article_subject.save()
                
                #-- END check to see if we update. --#
            
            #-- END loop over subjects --#
        
        else:
        
            status_OUT.status_code = StatusContainer.STATUS_CODE_ERROR
            status_message = "ERROR - don't have both FROM and TO persons."
            status_OUT.add_message( status_message )
            
        #-- END check to see if we have FROM and TO persons. --#
        
        # Output summary
        status_message = "UNDO switching associated person FROM: " + str( FROM_person ) + " TO: " + str( TO_person )
        status_OUT.add_message( status_message )
        
        # do updates?
        if ( do_updates_IN == True ):
        
            status_message = "do_updates_IN = True, UPDATED THE FOLLOWING:"
        
        else:
        
            status_message = "do_updates_IN = False, NO CHANGES MADE!"
        
        #-- END check to see if we made updates or not --#article_author_count = len( article_author_id_list )
        status_OUT.add_message( status_message )
        
        article_author_count = len( article_author_id_list )
        article_subject_count = len( article_subject_id_list )
        
        status_message = "Updating " + str( article_author_count ) + " Article_Author instances: " + str( article_author_id_list )
        status_OUT.add_message( status_message )
        
        status_message = "Updating " + str( article_subject_count ) + " Article_Subject instances: " + str( article_subject_id_list )
        status_OUT.add_message( status_message )
        
        return status_OUT

    #-- END class method undo_switch_persons_in_data() --#


#-- END class PersonData --#