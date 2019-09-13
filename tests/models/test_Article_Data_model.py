"""
This file contains tests of the context_text Article_Data model.

Functions tested:
- @classmethod Article_Data.make_deep_copy()
"""

from __future__ import unicode_literals

# imports
from context_text.models import Article_Data
from context_text.models import Article_Author
from context_text.models import Article_Subject
from context_text.shared.context_text_base import ContextTextBase
from context_text.tests.test_helper import TestHelper

# Django imports
from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Q
import django.test

# six
import six

#===============================================================================
# ! ==> declare testing work class
#===============================================================================

class Article_Data_Copy_Tester( object ):
    

    #----------------------------------------------------------------------------
    # ! ==> class methods, in alphabetical order
    #----------------------------------------------------------------------------

    
    @classmethod
    def compare_attributes( cls,
                            orig_instance_IN,
                            copy_instance_IN,
                            message_prefix_IN = None,
                            equal_attr_names_list_IN = None,
                            not_equal_attr_names_list_IN = None,
                            *args,
                            **kwargs ):
                                
        # return reference
        message_list_OUT = []
    
        # declare variables
        me = "compare_attributes"
        local_debug_flag = False
        error_count = -1
        error_message = ""
        error_message_list = None
        orig_id = -1
        copy_id = -1
        message_prefix = ""
        attribute_name = ""
        orig_value = None
        orig_type = None
        orig_class_name = ""
        copy_value = None
        copy_type = None
        copy_class_name = ""
        
        # declare variables - ManyToMany (m2m)
        m2m_orig_all = None
        m2m_orig_count = -1
        m2m_orig_instance = None
        m2m_copy_all = None
        m2m_copy_count = -1
        m2m_copy_instance = None
        
        # initialize message list and count
        error_count = 0
        error_message_list = []
    
        # got a prefix?
        if ( ( message_prefix_IN is not None ) and ( message_prefix_IN != "" ) ):
        
            # yes.  Use it.
            message_prefix = message_prefix_IN
        
        else:
        
            # no.  Empty.
            message_prefix = ""
        
        #-- END check to see if message prefix --#
        
        # get IDs of instances
        orig_id = orig_instance_IN.id
        copy_id = copy_instance_IN.id
    
        # Check attribute values.
        for attribute_name in equal_attr_names_list_IN:
        
            # get values
            orig_value = getattr( orig_instance_IN, attribute_name )
            copy_value = getattr( copy_instance_IN, attribute_name )
    
            # and type and class name of those values
            orig_type = type( orig_value )
            orig_class_name = orig_type.__name__
            copy_type = type( copy_value )
            copy_class_name = copy_type.__name__
            
            if ( local_debug_flag == True ):
            
                # print type of each value
                print( "orig_value: type = " + str( orig_type ) + "; class = " + orig_type.__name__ + "; value = " + str( orig_value ) )
                print( "copy_value: type = " + str( copy_type ) + "; class = " + copy_type.__name__ + "; value = " + str( copy_value ) )
            
            #-- END DEBUG --#
            
            # compare
            
            # ManyToMany field?
            if ( orig_class_name == "ManyRelatedManager" ):
            
                # get .all() then count() for each and compare.
                
                # orig
                m2m_orig_all = orig_value.all()
                m2m_orig_count = m2m_orig_all.count()
                
                # copy
                m2m_copy_all = copy_value.all()
                m2m_copy_count = m2m_copy_all.count()
                
                # same count?
                if ( m2m_orig_count == m2m_copy_count ):
    
                    # loop over orig, look for item in copy.  If any missing, error.
                    for m2m_orig_instance in m2m_orig_all:
                    
                        # use try and call to .get() to look for each.
                        try:
                        
                            m2m_copy_instance = m2m_copy_all.filter( id = m2m_orig_instance.id )
                            
                        except ObjectDoesNotExist as odne:
                        
                            # copy is missing an instance in original.
                            error_count += 1
                            error_message = message_prefix + attribute_name + " ManyToMany field value " + str( m2m_orig_instance ) + " not present in copy."
                            error_message_list.append( error_message )                                        
    
                        except:
                    
                            # unexpected exception.
                            error_count += 1
                            error_message = message_prefix + attribute_name + " - unexpected exception trying to validate values in ManyToMany field."
                            error_message_list.append( error_message )                
    
                        #-- END try-except for comparing values in M2M --#
    
                    #-- END loop over instances in orig --#
                
                else:
                
                    # counts are different - error.
                    error_count += 1
                    error_message = message_prefix + attribute_name + " ManyToMany field counts of objects are different - m2m_orig_count = " + str( m2m_orig_count ) + "; m2m_copy_count = " + str( m2m_copy_count )
                    error_message_list.append( error_message )                
                
                #-- END check to see if same number of items. --#
            
            else:
            
                # not both None...
                if ( orig_value != copy_value ):
                
                    # not a match.  Error.
                    error_count += 1
                    error_message = message_prefix + attribute_name + " values should be EQUAL - orig_value ( ID: " + str( orig_id ) + " ) = " + str( orig_value ) + "; copy_value ( ID: " + str( copy_id ) + " ) = " + str( copy_value )
                    error_message_list.append( error_message )
                    
                else:
        
                    # it is a match.  Move on.
                    pass
                
                #-- END check to see if test values are equal --#
                
            #-- END check to see if both None --#
    
        #-- END loop over test attribute equal names --#
        
        # Check attribute values.
        for attribute_name in not_equal_attr_names_list_IN:
        
            # get values
            orig_value = getattr( orig_instance_IN, attribute_name )
            copy_value = getattr( copy_instance_IN, attribute_name )
            
            # compare
            if ( ( ( orig_value is None ) and ( copy_value is None ) )
                or ( orig_value == copy_value ) ):
            
                # a match.  Error.
                error_count += 1
                error_message = message_prefix + attribute_name + " should NOT be EQUAL - orig_value = " + str( orig_value ) + "; copy_value = " + str( copy_value )
                error_message_list.append( error_message )
                
            else:
    
                # it is a match.  Move on.
                pass
            
            #-- END check to see if test values are equal --#
    
            #-- END check to see if both None --#
    
        #-- END loop over test attribute not equal names --#
        
        message_list_OUT = error_message_list
        
        return message_list_OUT
    
    #-- END function compare_attributes() --#
    
    
    @classmethod
    def validate_copy( cls,
                       orig_instance_IN,
                       copy_instance_qs_IN,
                       message_prefix_IN = None,
                       equal_attr_names_list_IN = None,
                       not_equal_attr_names_list_IN = None,
                       *args,
                       **kwargs ):
                           
        '''
        Accepts original instance, queryset that contains the copy we want to
            compare it to, and then optional parameters:
            - message_prefix_IN - prefix you want added to the left of error messages.
            - equal_attr_names_list_IN - list of attribute names you'd expect to be equal between the copy and the original.
            - not_equal_attr_names_list_IN - list of attributes you'd expect to not be equal between the copy and the original (time stamps, for example).
            
        Compares the copy to the original.  If there are discrepancies, makes
            and returns a list.  If list that is returned is empty, then no
            problems. 
        '''
                           
        # return reference
        message_list_OUT = []
        
        # declare variables
        error_count = -1
        error_message_list = []
        copy_instance_count = -1
        copy_instance = None
        copy_instance_id = -1
        error_message_prefix = ""
        error_id_list = []
        error_instance = None
        
        # got a query set?
        if ( copy_instance_qs_IN is not None ):
    
            # how many?
            copy_instance_count = copy_instance_qs_IN.count()
            if ( copy_instance_count == 1 ):
            
                # a single match.  Get instance and ID.
                copy_instance = copy_instance_qs_IN.get()
                copy_instance_id = copy_instance.id
                
                # Check attribute values.
                current_error_list = cls.compare_attributes( orig_instance_IN,
                                                             copy_instance,
                                                             message_prefix_IN = message_prefix_IN,
                                                             equal_attr_names_list_IN = equal_attr_names_list_IN,
                                                             not_equal_attr_names_list_IN = not_equal_attr_names_list_IN )
                                        
                # update error_count and error_message_list.
                error_count += len( current_error_list )
                error_message_list.extend( current_error_list )
                
            elif ( copy_instance_count > 1 ):
            
                # ERROR - multiple matches found for record in original.
                error_count += 1
                
                # get IDs of multiple matches
                error_id_list = []
                for error_instance in copy_instance_qs_IN:
                
                    error_id_list.append( str( error_instance.id ) )
                    
                #-- END loop to create list of error IDs. --#
                
                error_message_list.append( message_prefix_IN + " - multiple matches for ID " + str( orig_instance_IN.id ) + ": " + ", ".join( error_id_list ) )
                
            elif ( copy_instance_count < 1 ):
            
                # ERROR - no match found for record in original.
                error_count += 1
                error_message_list.append( message_prefix_IN + " - no match for ID " + str( orig_instance_IN.id ) )
            
            #-- END check to see how many. --#
    
        else:
            
            # ERROR - no match found for record in original.
            error_count += 1
            error_message_list.append( message_prefix_IN + " - QuerySet is None.  No copy found...?" )
            
        #-- END check to see if QuerySet passed in. --# 
        
        message_list_OUT = error_message_list
        
        return message_list_OUT
        
    #-- END function validate_copy() --#


    @classmethod
    def validate_article_data_deep_copy( cls,
                                         original_article_data_id_IN = None,
                                         copy_article_data_id_IN = None,
                                         copy_coder_user_id_IN = None ):

        '''
        Accepts ID of original Article_Data, optional ID of copy you want to
            validate.  If no copy ID passed in, makes a copy, optionally setting
            the code in that copy to the coder represented by the person who's
            id is in copy_coder_user_id_IN.
        
        Returns list of messages.  If message list is empty, valid!  If messages
            returned, they are error messages.
        '''
        
        # return reference
        message_list_OUT = []

        # ! ==> declare variables
        
        # declare variables - set up IDs of records
        article_data_id = -1
        copy_article_data_id = -1
        new_coder_id = -1
        
        # declare variables
        instance = None
        instance_id = -1
        my_article_data = None
        copy_article_data = None
        my_ad_notes_qs = None
        my_ad_notes_count = -1
        my_author_qs = None
        my_author_count = -1
        author_id = -1
        my_subject_qs = None
        my_subject_count = -1
        subject_id = -1
        current_child_model_name = ""
        child_qs = None
        child_count = -1
        child_instance = None
        copy_child_qs = None
        copy_child_instance_qs = None
        
        # declare variables - test quality of copy
        current_model_name = ""
        error_count = -1
        error_message = ""
        error_message_list = None
        standard_error_message_prefix = ""
        error_message_prefix = ""
        
        # declare variables - find matching instance in copy.
        copy_instance_qs = None
        
        # declare variables - test attributes
        test_attribute_names_equal_list = []
        test_attribute_names_not_equal_list = []
        test_attribute_name = ""
        child_equal_list = []
        child_not_equal_list = []
        
        #===============================================================================
        # ! ==> configuration
        #===============================================================================
        
        article_data_id = original_article_data_id_IN
        copy_article_data_id = copy_article_data_id_IN
        new_coder_id = copy_coder_user_id_IN
        
        #===============================================================================
        # ! ==> do stuff
        #===============================================================================
        
        # load existing Article_Data
        my_article_data = Article_Data.objects.get( id = article_data_id )
        
        # make a copy?
        if ( ( copy_article_data_id is None ) or ( copy_article_data_id <= 0 ) ):
        
            # make a copy
            copy_article_data = Article_Data.make_deep_copy( article_data_id, new_coder_user_id_IN = new_coder_id )
            copy_article_data_id = copy_article_data.id
            
        else:
        
            # look up copy
            copy_article_data = Article_Data.objects.get( id = copy_article_data_id )
        
        #-- END check if we make a copy or test existing copy --#
        
        # set standard message prefix:
        standard_error_message_prefix = " - orig ID = " + str( article_data_id ) + "; copy ID = " + str( copy_article_data_id ) + " - "
        print( "Original Article_Data ID = " + str( article_data_id ) + "; Copy Article_Data ID = " + str( copy_article_data_id ) )
        
        # check quality of copy
        error_count = 0
        error_message_list = []
        current_error_list = None
        
        # ! ----> Article_Data_Notes
        current_model_name = "Article_Data_Notes"
        my_ad_notes_qs = my_article_data.article_data_notes_set.all()
        my_ad_notes_count = my_ad_notes_qs.count()
        print( "\n\n" + current_model_name + " ( count = " + str( my_ad_notes_count ) + " ):" )
        
        # set up test attributes
        test_attribute_names_equal_list = [ "content_type", "content", "status", "source", "content_description" ]
        test_attribute_names_not_equal_list = [ "create_date", "last_modified", "article_data_id" ]
        
        for instance in my_ad_notes_qs:
        
            print( "- " + str( instance ) )
            
            # look for a match in copy with same content
            copy_instance_qs = copy_article_data.article_data_notes_set.filter( content = instance.content )
            
            # validate the copy
            error_message_prefix = current_model_name + standard_error_message_prefix
            current_error_list = cls.validate_copy( instance,
                                                    copy_instance_qs,
                                                    message_prefix_IN = error_message_prefix,
                                                    equal_attr_names_list_IN = test_attribute_names_equal_list,
                                                    not_equal_attr_names_list_IN = test_attribute_names_not_equal_list )
        
            # update error_count and error_message_list.
            error_count += len( current_error_list )
            error_message_list.extend( current_error_list )        
            
        #-- END loop over Article_Data_Notes --#
        
        # ! ----> Article_Author
        current_model_name = "Article_Author"
        my_author_qs = my_article_data.article_author_set.all()
        my_author_count = my_author_qs.count()
        print( "\n" + current_model_name + " ( count = " + str( my_author_count ) + " ):" )
        
        # set up test attributes
        test_attribute_names_equal_list = [ "person", "original_person", "name", "verbatim_name", "lookup_name", "match_confidence_level", "match_status", "author_type" ]
        test_attribute_names_not_equal_list = [ "create_date", "last_modified", "article_data_id" ]
        
        for instance in my_author_qs:
        
            print( "\n- " + str( instance ) )
            
            # look for a match in copy with same content
            copy_instance_qs = copy_article_data.article_author_set.filter( person = instance.person )
            
            # validate the copy
            error_message_prefix = current_model_name + standard_error_message_prefix
            current_error_list = cls.validate_copy( instance,
                                                    copy_instance_qs,
                                                    message_prefix_IN = error_message_prefix,
                                                    equal_attr_names_list_IN = test_attribute_names_equal_list,
                                                    not_equal_attr_names_list_IN = test_attribute_names_not_equal_list )
        
            # update error_count and error_message_list.
            error_count += len( current_error_list )
            error_message_list.extend( current_error_list )        
        
            # get ID
            instance_id = instance.id
            
            # get copy instance.
            copy_instance = copy_instance_qs.get()
        
            # ! --------> Alternate_Author_Match
            current_child_model_name = "Alternate_Author_Match"
            child_equal_list = [ "person" ]
            child_not_equal_list = [ "article_author", "create_date", "last_modified" ]
            
            # get child  and copy child QuerySets.
            child_qs = instance.alternate_author_match_set.all()
            child_count = child_qs.count()
            copy_child_qs = copy_instance.alternate_author_match_set.all()

            print( "\n----> " + current_child_model_name + " ( count = " + str( child_count ) + " ):" )
            
            # loop over child instances
            for child_instance in child_qs:
                
                print( "----> - " + str( child_instance ) )
            
                # look for match in copy.
                copy_child_instance_qs = copy_instance.alternate_author_match_set.filter( person = child_instance.person )
        
                # validate the copy instance
                error_message_prefix = current_model_name + "-->" + current_child_model_name + standard_error_message_prefix
                current_error_list = cls.validate_copy( child_instance,
                                                        copy_child_instance_qs,
                                                        message_prefix_IN = error_message_prefix,
                                                        equal_attr_names_list_IN = child_equal_list,
                                                        not_equal_attr_names_list_IN = child_not_equal_list )
        
                # update error_count and error_message_list.
                error_count += len( current_error_list )
                error_message_list.extend( current_error_list )
        
            #-- END loop over Alternate_Author_Match --#
        
        #-- END loop over Article_Author --#
        
        # ! ----> Article_Subject 
        current_model_name = "Article_Subject"
        my_subject_qs = my_article_data.article_subject_set.all()
        my_subject_count = my_subject_qs.count()
        print( "\n" + current_model_name + " ( count = " + str( my_subject_count ) + " ):" )
        
        # set up test attributes
        test_attribute_names_equal_list = [ "person", "original_person", "name", "verbatim_name", "lookup_name", "match_confidence_level", "match_status", "source_type", "subject_type", "document", "topics", "source_contact_type", "source_capacity", "localness" ]
        test_attribute_names_not_equal_list = [ "create_date", "last_modified", "article_data_id" ]
        
        for instance in my_subject_qs:
        
            print( "\n- " + str( instance ) )
            
            # get ID
            instance_id = instance.id
            
            # look for a match in copy with same content
            copy_instance_qs = copy_article_data.article_subject_set.filter( person = instance.person )
            
            # validate the copy
            error_message_prefix = current_model_name + " - orig ID = " + str( article_data_id ) + "; copy ID = " + str( copy_article_data_id ) + " - "
            current_error_list = cls.validate_copy( instance,
                                                    copy_instance_qs,
                                                    message_prefix_IN = error_message_prefix,
                                                    equal_attr_names_list_IN = test_attribute_names_equal_list,
                                                    not_equal_attr_names_list_IN = test_attribute_names_not_equal_list )
        
            # update error_count and error_message_list.
            error_count += len( current_error_list )
            error_message_list.extend( current_error_list )        
        
            # get ID
            instance_id = instance.id
            
            # get copy instance.
            copy_instance = copy_instance_qs.get()
        
            # ! --------> Alternate_Subject_Match
            current_child_model_name = "Alternate_Subject_Match"
            child_equal_list = [ "person" ]
            child_not_equal_list = [ "article_subject", "create_date", "last_modified" ]
            
            # get child  and copy child QuerySets.
            child_qs = instance.alternate_subject_match_set.all()
            child_count = child_qs.count()
            copy_child_qs = copy_instance.alternate_subject_match_set.all()
            
            print( "\n----> " + current_child_model_name + " ( count = " + str( child_count ) + " ):" )
            
            # loop over child instances
            for child_instance in child_qs:
                
                print( "----> - " + str( child_instance ) )
            
                # look for match in copy.
                copy_child_instance_qs = copy_instance.alternate_subject_match_set.filter( person = child_instance.person )
        
                # validate the copy instance
                error_message_prefix = current_model_name + "-->" + current_child_model_name + standard_error_message_prefix
                current_error_list = cls.validate_copy( child_instance,
                                                        copy_child_instance_qs,
                                                        message_prefix_IN = error_message_prefix,
                                                        equal_attr_names_list_IN = child_equal_list,
                                                        not_equal_attr_names_list_IN = child_not_equal_list )
        
                # update error_count and error_message_list.
                error_count += len( current_error_list )
                error_message_list.extend( current_error_list )
        
            #-- END loop over Alternate_Subject_Match --#
        
            # ! --------> Article_Subject_Mention
            current_child_model_name = "Article_Subject_Mention"
            child_equal_list = [ "value", "value_in_context", "value_index", "value_length", "canonical_index", "value_word_number_start", "value_word_number_end", "paragraph_number", "context_before", "context_after", "capture_method", "uuid", "uuid_name", "notes", "is_speaker_name_pronoun" ]
            child_not_equal_list = [ "article_subject", "create_date", "last_modified" ]
            
            # get child  and copy child QuerySets.
            child_qs = instance.article_subject_mention_set.all()
            child_count = child_qs.count()
            copy_child_qs = copy_instance.article_subject_mention_set.all()
            
            print( "\n----> " + current_child_model_name + " ( count = " + str( child_count ) + " ):" )
            
            # loop over child instances
            for child_instance in child_qs:
                
                print( "----> - " + str( child_instance ) )
            
                # look for match in copy.
                copy_child_instance_qs = copy_instance.article_subject_mention_set.filter( value = child_instance.value, value_in_context = child_instance.value_in_context, value_index = child_instance.value_index )
        
                # validate the copy instance
                error_message_prefix = current_model_name + "-->" + current_child_model_name + standard_error_message_prefix
                current_error_list = cls.validate_copy( child_instance,
                                                        copy_child_instance_qs,
                                                        message_prefix_IN = error_message_prefix,
                                                        equal_attr_names_list_IN = child_equal_list,
                                                        not_equal_attr_names_list_IN = child_not_equal_list )
        
                # update error_count and error_message_list.
                error_count += len( current_error_list )
                error_message_list.extend( current_error_list )
        
            #-- END loop over Article_Subject_Mention --#
        
            # ! --------> Article_Subject_Quotation
            current_child_model_name = "Article_Subject_Quotation"
            child_equal_list = [ "value", "value_in_context", "value_index", "value_length", "canonical_index", "value_word_number_start", "value_word_number_end", "paragraph_number", "context_before", "context_after", "capture_method", "uuid", "uuid_name", "notes", "is_speaker_name_pronoun", "value_with_attribution", "attribution_verb_word_index", "attribution_verb_word_number", "attribution_paragraph_number", "attribution_speaker_name_string", "is_speaker_name_pronoun", "attribution_speaker_name_index_range", "attribution_speaker_name_word_range", "quotation_type" ]
            child_not_equal_list = [ "article_subject", "create_date", "last_modified" ]
            
            # get child  and copy child QuerySets.
            child_qs = instance.article_subject_quotation_set.all()
            child_count = child_qs.count()
            copy_child_qs = copy_instance.article_subject_quotation_set.all()
            
            print( "\n----> " + current_child_model_name + " ( count = " + str( child_count ) + " ):" )
            
            # loop over child instances
            for child_instance in child_qs:
                
                print( "----> - " + str( child_instance ) )
            
                # look for match in copy.
                copy_child_instance_qs = copy_instance.article_subject_quotation_set.filter( value = child_instance.value, value_in_context = child_instance.value_in_context, value_index = child_instance.value_index )
        
                # validate the copy instance
                error_message_prefix = current_model_name + "-->" + current_child_model_name + standard_error_message_prefix
                current_error_list = cls.validate_copy( child_instance,
                                                        copy_child_instance_qs,
                                                        message_prefix_IN = error_message_prefix,
                                                        equal_attr_names_list_IN = child_equal_list,
                                                        not_equal_attr_names_list_IN = child_not_equal_list )
        
                # update error_count and error_message_list.
                error_count += len( current_error_list )
                error_message_list.extend( current_error_list )
        
            #-- END loop over Article_Subject_Quotation --#
        
            # ! --------> Subject_Organization
            current_child_model_name = "Subject_Organization"
            child_equal_list = [ "organization", "title" ]
            child_not_equal_list = [ "article_subject", "create_date", "last_modified" ]
            
            # get child  and copy child QuerySets.
            child_qs = instance.subject_organization_set.all()
            child_count = child_qs.count()
            copy_child_qs = copy_instance.subject_organization_set.all()
            
            print( "\n----> " + current_child_model_name + " ( count = " + str( child_count ) + " ):" )
            
            # loop over child instances
            for child_instance in child_qs:
                
                print( "----> - " + str( child_instance ) )
            
                # look for match in copy.
                copy_child_instance_qs = copy_instance.subject_organization_set.filter( organization = child_instance.organization )
        
                # validate the copy instance
                error_message_prefix = current_model_name + "-->" + current_child_model_name + standard_error_message_prefix
                current_error_list = cls.validate_copy( child_instance,
                                                        copy_child_instance_qs,
                                                        message_prefix_IN = error_message_prefix,
                                                        equal_attr_names_list_IN = child_equal_list,
                                                        not_equal_attr_names_list_IN = child_not_equal_list )
        
                # update error_count and error_message_list.
                error_count += len( current_error_list )
                error_message_list.extend( current_error_list )
        
            #-- END loop over Subject_Organization --#
        
        #-- END loop over Article_Subject --#
        
        print( "\n\n====================" )
        print( "Results:" )
        print( "====================" )
        print( "\n" )
        
        # error count?
        if ( error_count > 0 ):
        
            # errors.
            print( str( error_count ) + " errors:" )
            
            # print out error messages
            for error_message in error_message_list:
            
                print( "- " + error_message )
                
            #-- END loop over error messages. --#
        
        else:
        
            # no errors!
            print( "NO ERRORS!" )
            
        #-- END check to see if errors. --#
        
        # return the error_message_list
        message_list_OUT = error_message_list
        
        return message_list_OUT
        
    #-- END class method validate_article_data_deep_copy() --#
    

    #----------------------------------------------------------------------------
    # ! ==> __init__() method
    #----------------------------------------------------------------------------


    def __init__( self ):

        # call parent's __init__()
        super( Article_Data_Copy_Tester, self ).__init__()
        
    #-- END method __init__() --#

    
#-- END class Article_Data_Copy_Tester --#

class Article_DataModelTest( django.test.TestCase ):
    
    #----------------------------------------------------------------------------
    # Constants-ish
    #----------------------------------------------------------------------------


    #----------------------------------------------------------------------------
    # instance methods
    #----------------------------------------------------------------------------


    def setUp( self ):
        
        """
        setup tasks.  Call function that we'll re-use.
        """

        # call TestHelper.standardSetUp()
        TestHelper.standardSetUp( self, fixture_list_IN = TestHelper.FIXTURE_LIST )

    #-- END function setUp() --#
        

    def test_setup( self ):

        """
        Tests whether there were errors in setup.
        """
        
        # declare variables
        error_count = -1
        error_message = ""
        
        # get setup error count
        setup_error_count = self.setup_error_count
        
        # should be 0
        error_message = ";".join( self.setup_error_list )
        self.assertEqual( setup_error_count, 0, msg = error_message )
        
    #-- END test method test_django_config_installed() --#


    def test_article_data_deep_copy( self ):
        
        # declare variables
        me = "test_article_data_deep_copy"
        original_article_data_id = -1
        copy_to_coder_user = None
        copy_to_coder_user_id = -1
        article_data_copy = None
        new_article_data_id = -1
        error_message_list = None
                
        # pick an Article_Data to copy.
        original_article_data_id = 74
        
        # get user to copy to:
        copy_to_coder_user = ContextTextBase.get_ground_truth_coding_user()
        copy_to_coder_user_id = copy_to_coder_user.id

        # make a copy.
        article_data_copy = Article_Data.make_deep_copy( original_article_data_id,
                                                         new_coder_user_id_IN = copy_to_coder_user_id )
                                                         
        new_article_data_id = article_data_copy.id
        
        # and validate
        error_message_list = Article_Data_Copy_Tester.validate_article_data_deep_copy( original_article_data_id, new_article_data_id, copy_to_coder_user_id )
        
        error_message_count = len( error_message_list )
        should_be = 0
        error_string = "Copy of Article_Data ID " + str( original_article_data_id ) + " into ID " + str( new_article_data_id ) + " had " + str( error_message_count ) + " errors, should be = " + str( should_be )
        error_string += "\n error messages:"
        error_string += str( error_message_list )
        self.assertEqual( error_message_count, should_be, msg = error_string )
        
    #-- END test method test_article_data_deep_copy() --# 

#-- END class Article_DataModelTest --#