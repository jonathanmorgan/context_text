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
from python_utilities.django_utils.django_model_helper import DjangoModelHelper
from python_utilities.logging.logging_helper import LoggingHelper
from python_utilities.objects.object_helper import ObjectHelper
from python_utilities.status.status_container import StatusContainer

# sourcenet models
from sourcenet.models import Article_Author
from sourcenet.models import Article_Subject
from sourcenet.models import Person


class PersonData( object ):


    #============================================================================
    # ! ==> constants-ish
    #============================================================================


    # DEBUG
    DEBUG_FLAG = False
    LOGGER_NAME = "sourcenet.data.person_data.PersonData"
    
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


    @classmethod
    def get_merge_function( cls, class_IN, *args, **kwargs ):
        
        '''
        Accepts a class.  Retrieves its name (__name__).  Looks up a merge
            function from CLASS_NAME_TO_MERGE_FUNCTION_MAP for the class name,
            returns a reference to the merge function.
        '''
        
        # return reference
        value_OUT = None
        
        # declare variables
        map_count = -1
        class_name = ""
        function_reference = None
        
        # got a class passed in?
        if ( class_IN is not None ):
        
            # first, see if there is anything in the map.
            map_count = len( cls.CLASS_NAME_TO_MERGE_FUNCTION_MAP )
            if ( map_count <= 0 ):
            
                # not initialized yet.  call init_merge_function_info()
                cls.init_merge_function_info()
                
            #-- END check to see if initialized. --#
            
            # get name of class.
            class_name = class_IN.__name__
            
            # to lower case
            class_name = class_name.lower()
            
            # retrieve function from map.
            function_reference = cls.CLASS_NAME_TO_MERGE_FUNCTION_MAP.get( class_name, None )
            
            value_OUT = function_reference
            
        #-- END check to see if class passed in. --#
        
        # if nothing, return default (mf_do_nothing()).
        if ( value_OUT is None ):
        
            # return default
            value_OUT = cls.DEFAULT_MERGE_FUNCTION
            
        #-- END check to see if nothing found --#
        
        return value_OUT
        
    #-- END class method get_merge_function() --#


    @classmethod
    def get_person_related_set_attribute_names( cls, *args, **kwargs ):
        
        # return reference
        name_list_OUT = []
        
        # declare variables
        person_attributes = None
        attribute_name = None
        attribute_value = None
        value_type = None
        type_name = ""
        type_qualname = ""
        
        # first, see if list already generated.
        name_list_OUT = cls.PERSON_RELATED_SET_ATTRIBUTE_NAMES
        
        if ( ( name_list_OUT is None )
            or ( isinstance( name_list_OUT, list ) == False )
            or ( len( name_list_OUT ) <= 0 ) ):
        
            # no list already, need to render.
            
            # to start, get non-boring attributes of Person
            person_attributes = ObjectHelper.get_user_attributes( Person )
            
            # loop over them to build a dictionary of names to classes of those that
            #     end in "*_set".
            for attribute_name, attribute_value in six.iteritems( person_attributes ):                                            
            
                # need to get the name of the class of attr_value.
                value_type = type( attribute_value )
                type_name = value_type.__name__
                type_qualname = value_type.__qualname__
                
                if ( type_name in DjangoModelHelper.REVERSE_LOOKUP_CLASS_NAMES ):
                
                    # add attribute name ("*_set") to name list.
                    name_list_OUT.append( attribute_name )
                    print( attribute_name + " = " + type_name )
                    
                #-- END check if type name is a Reverse Lookup class. --#
            
            #-- END loop over Person Attributes --#
            
            # store in static variable.
            cls.PERSON_RELATED_SET_ATTRIBUTE_NAMES = name_list_OUT
            
            name_list_OUT = cls.get_person_related_set_attribute_names()
            
        #-- END check to see if name list already built. --#
        
        return name_list_OUT
        
    #-- END class method get_person_related_set_attribute_names() --#


    @classmethod
    def init_merge_function_info( cls, *args, **kwargs ):
        
        '''
        Builds map of class names to merge functions for the following related
            tables, with reverse manager(s) listed below each table.  For models
            with more than one reverse manager, the merge function needs to be 
            able to differentiate between the different cases, or just needs to
            do nothing and return a warning explaining how to clean up.
            
            From Sourcenet:
            - Alternate_Author_Match:
                - alternate_author_match_set = ReverseManyToOneDescriptor
            - Alternate_Name
                - alternate_name_set = ReverseManyToOneDescriptor
            - Alternate_Subject_Match
                - alternate_subject_match_set = ReverseManyToOneDescriptor)
            - Article_Author
                - article_author_set = ReverseManyToOneDescriptor
                - sourcenet_article_author_original_person_set = ReverseManyToOneDescriptor
            - Article_Subject
                - article_subject_set = ReverseManyToOneDescriptor
                - sourcenet_article_subject_original_person_set = ReverseManyToOneDescriptor
            - Person_External_UUID 
                - person_external_uuid_set = ReverseManyToOneDescriptor
            - Person_Newspaper
                - person_newspaper_set = ReverseManyToOneDescriptor
            - Person_Organization
                - person_organization_set = ReverseManyToOneDescriptor

            From Sourcenet Analysis:
            - Reliabilty_Names
                - reliability_names_set = ReverseManyToOneDescriptor
            - Reliability_Ties
                - reliability_ties_to_set = ReverseManyToOneDescriptor
                - reliability_ties_from_set = ReverseManyToOneDescriptor
        '''
        
        # for each model name, refer to function that should be called.  Model
        #     names are in lower case here, and are converted to lower case
        #     before lookup in get_merge_function().

        # Sourcenet classes
        cls.CLASS_NAME_TO_MERGE_FUNCTION_MAP[ "alternate_author_match" ] = cls.mf_do_nothing
        cls.CLASS_NAME_TO_MERGE_FUNCTION_MAP[ "alternate_name" ] = cls.mf_do_nothing
        cls.CLASS_NAME_TO_MERGE_FUNCTION_MAP[ "alternate_subject_match" ] = cls.mf_do_nothing
        cls.CLASS_NAME_TO_MERGE_FUNCTION_MAP[ "article_author" ] = cls.mf_do_nothing
        cls.CLASS_NAME_TO_MERGE_FUNCTION_MAP[ "article_subject" ] = cls.mf_do_nothing
        cls.CLASS_NAME_TO_MERGE_FUNCTION_MAP[ "person_external_uuid" ] = cls.mf_do_nothing
        cls.CLASS_NAME_TO_MERGE_FUNCTION_MAP[ "person_newspaper" ] = cls.mf_do_nothing
        cls.CLASS_NAME_TO_MERGE_FUNCTION_MAP[ "person_organization" ] = cls.mf_do_nothing

        # Sourcenet Analysis classes
        cls.CLASS_NAME_TO_MERGE_FUNCTION_MAP[ "reliability_names" ] = cls.mf_do_nothing
        cls.CLASS_NAME_TO_MERGE_FUNCTION_MAP[ "reliability_ties" ] = cls.mf_do_nothing
        
        # AND, finally, set default merge function.
        cls.DEFAULT_MERGE_FUNCTION = cls.mf_do_nothing
        
    #-- END class method init_merge_function_info() --#


    @classmethod
    def mf_do_nothing( cls, record_instance_IN, merge_from_person_IN, merge_into_person_IN, logger_name_IN = None, *args, **kwargs ):
        
        '''
        merge function, does nothing.
        '''
        
        # return reference
        status_OUT = StatusContainer()
        
        # declare variables
        me = "mf_do_nothing"
        debug_message = ""
        my_logger_name = ""
        
        # set logger name.
        if ( ( logger_name_IN is not None ) and ( logger_name_IN != "" ) ):
        
            # got one - use it.
            my_logger_name = logger_name_IN
        
        else:
        
            # not set.  Use default.
            my_logger_name = cls.LOGGER_NAME
        
        #-- END check to see if loger name passed in. --#
        
        debug_message = "Doing nothing with record: " + str( record_instance_IN ) + "; merge from person = " + str( merge_from_person_IN ) + "; merge into person = " + str( merge_into_person_IN )
        LoggingHelper.output_debug( debug_message, method_IN = me, logger_name_IN = my_logger_name )
        
        # init status.
        status_OUT = status_OUT.set_status_code( StatusContainer.STATUS_CODE_SUCCESS )
        
        return status_OUT
        
    #-- END merge function mf_do_nothing() --#

    
    @classmethod
    def mf_just_delete( cls, record_instance_IN, merge_from_person_IN, merge_into_person_IN, logger_name_IN = None, *args, **kwargs ):
        
        '''
        merge function - just deletes the record passed in.
        '''

        # return reference
        status_OUT = StatusContainer()
        
        # declare variables
        me = "mf_just_delete"
        debug_message = ""
        my_logger_name = ""
        
        # set logger name.
        if ( ( logger_name_IN is not None ) and ( logger_name_IN != "" ) ):
        
            # got one - use it.
            my_logger_name = logger_name_IN
        
        else:
        
            # not set.  Use default.
            my_logger_name = cls.LOGGER_NAME
        
        #-- END check to see if loger name passed in. --#
        
        debug_message = "Just deleting record: " + str( record_instance_IN ) + "; merge from person = " + str( merge_from_person_IN ) + "; merge into person = " + str( merge_into_person_IN )
        LoggingHelper.output_debug( debug_message, method_IN = me, logger_name_IN = my_logger_name )

        # init status.
        status_OUT = status_OUT.set_status_code( StatusContainer.STATUS_CODE_SUCCESS )
        
        # delete.
        record_instance_IN.delete()
        
        return status_OUT        
        
    #-- END merge function mf_just_delete() --#

    
    @classmethod
    def merge_records( cls, record_qs_IN, merge_from_id_IN, merge_into_id_IN, do_delete_IN = False, logger_name_IN = None, *args, **kwargs ):
        
        '''
        accepts a QuerySet of related records of a specific type for the person
            we are merging INTO another person (the FROM user).  Loops over them
            to get a list of their IDs, so we can interact with them independent
            of the RelatedManager (not sure if this is necessary, but an
            overabundance of caution).  For the type, uses a dictionary that
            maps class name to function pointers to find and call a function to
            merge that class's rows.  Then, we loop over the rows once again
            to delete() each of them.

        preconditions: Deletes the merge_from person's data.  BE CAREFUL.
        postconditions: merges all the rows from the merge from person into the
            rows that belong to the merge into person, then deletes the rows for
            the merge_from person.  Again, deletes the merge_from person's data.
            BE CAREFUL.
        ''' 
        
        # return reference
        status_OUT = StatusContainer()
        
        # declare variables
        me = "delete_records"
        my_logger_name = ""
        debug_message = ""
        from_person = None
        into_person = None
        current_record = None
        related_class = None
        related_id = ""
        related_id_list = []
        merge_function = None
        related_qs = None
        related_record = None
        merge_status = None
        
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
                
                # load Person instances for the from and the into.
                from_person = Person.objects.get( pk = merge_from_id_IN )
                into_person = Person.objects.get( pk = merge_into_id_IN )                

                # loop over records in related set to get class and get IDs.
                #     Don't make changes here yet.  Wait so we aren't looping
                #     inside a related 
                for current_record in record_qs_IN:
                
                    debug_message = "Current record: " + str( current_record )
                    LoggingHelper.output_debug( debug_message, method_IN = me, indent_with_IN = "====> ", logger_name_IN = my_logger_name )
                
                    # is related class set?
                    if ( related_class is None ):
                    
                        related_class = type( current_record )
                        
                    #-- END check to see if we have related class --#
                    
                    # get ID and add it to list.
                    record_id = current_record.id
                    record_id_list.append( record_id )
                    
                #-- END loop over records to get ID list. --#
                
                # look up the record merge function for this class.
                merge_function = cls.get_merge_function( related_class )
                
                # now, use the class to get a result set of the same rows that
                #     is not related to one of the persons.
                related_qs = related_class.objects.filter( id__in = record_id_list )
                
                # in theory, we now have a QuerySet of the related records for
                #     the person we are merging from.  Loop and call the merge
                #     function on each.
                for related_record in related_qs:
                
                    # call the merge_function (just merge, don't delete).
                    merge_status = merge_function( related_record, from_person, into_person )
                    
                #-- END merge loop --#
                
                # do we delete?
                if ( do_delete_IN == True ):
                
                    # OK...
                    for related_record in related_qs:
                    
                        # delete()
                        related_record.delete()
                        
                        debug_message = "DELETED!!!"
                        LoggingHelper.output_debug( debug_message, method_IN = me, indent_with_IN = "========> ", logger_name_IN = my_logger_name )
                    
                    #-- END merge loop --#
                    
                #-- END check to see if we delete. --#
                
                # status is success.
                status_OUT.set_status_code( StatusContainer.STATUS_CODE_SUCCESS )

            else:
            
                debug_message = "QuerySet is EMPTY."
                LoggingHelper.output_debug( debug_message, method_IN = me, indent_with_IN = "====> ", logger_name_IN = my_logger_name )
            
            #-- END check to see if anything in list. --#
            
        else:
        
            debug_message = "record_qs_IN is not a QuerySet: " + str( record_qs_IN )
            LoggingHelper.output_debug( debug_message, method_IN = me, indent_with_IN = "====> ", logger_name_IN = my_logger_name )
            status_OUT.set_status_code( StatusContainer.STATUS_CODE_ERROR )
            status_OUT.add_message( debug_message )
            
        #-- END check to see if QuerySet instance passed in. --#
        
        return status_OUT
        
    #-- END class method merge_records() --#
        
    
    @classmethod
    def merge_persons( cls, from_person_id_list_IN, into_person_id_IN, do_updates_IN = True, delete_from_IN = False, logger_name_IN = None, *args, **kwargs ):

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
        from_person_id = -1
        from_person_instance = None
        reverse_lookup_attribute_names = None
        attribute_name = ""
        reverse_lookup_attribute = None
        reverse_lookup_qs = None
        record_merge_status = None
        persons_to_delete_list = []
        delete_person_id = -1
        delete_person = None
        
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
            if ( ( into_person_id_IN is not None )
                and ( isinstance( into_person_id_IN, six.integer_types ) == True )
                and ( into_person_id_IN > 0 ) ):
                
                # loop over person list.
                for from_person_id in from_person_id_list_IN:
                
                    # get person instance.
                    from_person_instance = Person.objects.get( pk = from_person_id )
                    
                    # get list of names of reverse lookup sets.
                    reverse_lookup_attribute_names = cls.get_person_related_set_attribute_names()
                    
                    # loop over attribute names.  For each, get QuerySet of
                    #     related records, then call merge_records().
                    for attribute_name in reverse_lookup_attribute_names:
                    
                        # get model reverse lookup set for FROM Person.
                        reverse_lookup_attribute = getattr( from_person_instance, attribute_name )
                        
                        # get QuerySet
                        reverse_lookup_qs = reverse_lookup_attribute.all()
                        
                        # call merge_records()
                        record_merge_status = cls.merge_records( reverse_lookup_qs, 
                                                                 from_person_id,
                                                                 into_person_id_IN,
                                                                 do_delete_IN = delete_from_IN,
                                                                 logger_name_IN = logger_name_IN )
                                                                 
                    #-- END loop over reverse lookup set names. --#
                    
                    # finally, do we delete the from person?
                    if ( delete_from_IN == True ):
                    
                        # yes.  Add ID to list.
                        persons_to_delete_list.append( from_person_instance )
                        
                    #-- END check to see if we delete. --#
                    
                #-- END loop over persons. --#
                
                # are we deleting?
                if ( delete_from_IN == True ):

                    # anything in the list of person IDs to delete?
                    if ( ( persons_to_delete_list is not None )
                        and ( isinstance( persons_to_delete_list, list ) == True )
                        and ( len( persons_to_delete_list ) > 0 ) ):
                        
                        # yup.  Delete them.
                        for delete_person in persons_to_delete_list:
                        
                            # delete.
                            status_OUT.add_message( "Deleting Person: " + str( delete_person ) )
                            delete_person.delete()
                            
                        #-- END loop over persons to delete. --#
                        
                    #-- END check to see if we delete anyone. --#
                
                #-- END check to see if we are deleting. --#

                # status is success.
                status_OUT.set_status_code( StatusContainer.STATUS_CODE_SUCCESS )

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
        status_message = "Switching associated person FROM: \"" + str( FROM_person ) + "\" --> TO: \"" + str( TO_person ) + "\""
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
    def undo_switch_persons_in_data( cls, from_person_id_IN, to_person_id_IN = -1, do_updates_IN = True, *args, **kwargs ):
        
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

        # return reference
        status_OUT = StatusContainer()

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

        # init status to success
        status_OUT.status_code = StatusContainer.STATUS_CODE_SUCCESS

        # first, set the IDs of the persons we will be switching from and to.
        FROM_person_id = from_person_id_IN
        TO_person_id = to_person_id_IN
        
        # Look up Person instances for each.
        FROM_person = Person.objects.get( id = FROM_person_id )
        
        # only get to person if one specified.
        if ( ( to_person_id_IN is not None )
            and ( isinstance( to_person_id_IN, six.integer_types ) == True )
            and ( to_person_id_IN > 0 ) ):

            # got a TO_person_id - get person.
            TO_person = Person.objects.get( id = TO_person_id )
            
        #-- END check to see if TO_person_id passed in. --#
        
        # make sure we at least have a FROM person.
        if ( FROM_person is not None ):
        
            # find all Article_Subject and Article_Author records that refer the the FROM
            #    person.
            article_author_qs = FROM_person.sourcenet_article_author_original_person_set.all()
            article_subject_qs = FROM_person.sourcenet_article_subject_original_person_set.all()
            
            # got a TO_person (so only undoing a switch to a particular person,
            #     not undoing all switches to any and all persons ever)?
            if ( TO_person is not None ):
            
                # yes.  Limit these lists to just those that refer to the
                #     TO_person.
                article_author_qs = article_author_qs.filter( person = TO_person )
                article_subject_qs = article_subject_qs.filter( person = TO_person )
                
            #-- end check to see if TO_person --#                
            
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
            status_message = "ERROR - don't have FROM person."
            status_OUT.add_message( status_message )
            
        #-- END check to see if we have FROM and TO persons. --#
        
        # Output summary
        status_message = "UNDO switching associated person FROM: \"" + str( FROM_person ) + "\""
        
        # is there a TO_person?
        if ( TO_person is not None ):
        
            status_message += " --> TO: \"" + str( TO_person ) + "\""
            
        #-- END check to see if there is a TO_person. --#
            
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