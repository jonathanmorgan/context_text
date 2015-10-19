from __future__ import unicode_literals

'''
Copyright 2010-2015 Jonathan Morgan

This file is part of http://github.com/jonathanmorgan/sourcenet.

sourcenet is free software: you can redistribute it and/or modify it under the terms of the GNU Lesser General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.

sourcenet is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.

You should have received a copy of the GNU Lesser General Public License along with http://github.com/jonathanmorgan/sourcenet. If not, see http://www.gnu.org/licenses/.
'''

'''
This code file contains a class that implements functions for interacting with
   the Open Calais natural language processing API.  It includes methods for
   interacting with the Open Calais REST API and for processing the JSON response
   that the Open Calais REST API returns.

Configuration properties for it are stored in django's admins, in the
   django_config application.  The properties are stored in Application
   "OpenCalais_REST_API_v1":
   - open_calais_api_key - API key for accessing OpenCalais version 1 API.
   - submitter - submitter you want to report to the API.
'''

#================================================================================
# Imports
#================================================================================


# python standard libraries
import json
import sys

# mess with python 3 support
import six

# python utilities
from python_utilities.django_utils.django_string_helper import DjangoStringHelper
from python_utilities.json.json_helper import JSONHelper
from python_utilities.network.http_helper import Http_Helper
from python_utilities.sequences.sequence_helper import SequenceHelper

# sourcenet classes

# models
from sourcenet.models import Alternate_Subject_Match
from sourcenet.models import Article_Data
from sourcenet.models import Article_Data_Notes
from sourcenet.models import Article_Subject
from sourcenet.models import Article_Subject_Mention
from sourcenet.models import Article_Subject_Quotation
from sourcenet.models import Article_Text
from sourcenet.models import Person

# parent abstract class.
from sourcenet.article_coding.article_coder import ArticleCoder

# class to help with parsing and processing OpenCalaisApiResponse.
from sourcenet.article_coding.open_calais_v1.open_calais_api_response import OpenCalaisApiResponse

#================================================================================
# Package constants-ish
#================================================================================


#================================================================================
# OpenCalaisArticleCoder class
#================================================================================

# define OpenCalaisArticleCoder class.
class ManualArticleCoder( ArticleCoder ):

    '''
    This class is a helper for coding articles manually.
    '''

    #============================================================================
    # Constants-ish
    #============================================================================
    

    # status constants - in parent (ArticleCoder) now:
    # STATUS_SUCCESS = "Success!"
    # STATUS_ERROR_PREFIX = "Error: "
    
    # config application
    CONFIG_APPLICATION = "Manual_Coding"
    

    #============================================================================
    # NOT Instance variables
    # Class variables - overriden by __init__() per instance if same names, but
    #    if not set there, shared!
    #============================================================================

    
    # declare variables
    #http_helper = None
    #content_type = ""
    #output_format = ""


    #============================================================================
    # Constructor
    #============================================================================


    def __init__( self ):

        # call parent's __init__() - I think...
        super( ManualArticleCoder, self ).__init__()
        
        # declare variables
        
        # set application string (for LoggingHelper parent class: (LoggingHelper -->
        #    BasicRateLimited --> ArticleCoder --> OpenCalaisArticleCoder).
        self.set_logger_name( "sourcenet.article_coding.manual_coding.manual_article_coder" )
        
        # items for processing a given JSON response - should be updated with
        #    every new article coded.
        
        # coder type (defaults to self.CONFIG_APPLICATION).
        self.coder_type = self.CONFIG_APPLICATION
        
    #-- END method __init__() --#


    #============================================================================
    # Instance methods
    #============================================================================


    def init_config_properties( self, *args, **kwargs ):

        '''
        purpose: Called as part of the base __init__() method, so that loading
           config properties can also be included in the parent __init__()
           method.  The application for django_config and any properties that
           need to be loaded should be set here.  To set a property use
           add_config_property( name_IN ).  To set application, use
           set_config_application( app_name_IN ).
           
        inheritance: This method overrides the abstract method of the same name in
           the ArticleCoder parent class.

        preconditions: None.

        postconditions: This instance should be ready to have
           load_config_properties() called on it after this method is invoked.
        '''

        self.set_config_application( self.CONFIG_APPLICATION )

    #-- END abstract method init_config_properties() --#
    

    def initialize_from_params( self, params_IN, *args, **kwargs ):

        '''
        purpose: Accepts a dictionary of run-time parameters, uses them to
           initialize this instance.

        inheritance: This method overrides the abstract method of the same name in
           the ArticleCoder parent class.

        preconditions: None.

        postconditions: None.
        '''

        # declare variables
        me = "initialize_from_params"
        
        # update config properties with params passed in.
        self.update_config_properties( params_IN )
        
    #-- END abstract method initialize_from_params() --#
    

    def process_article( self, article_IN, coding_user_IN = None, *args, **kwargs ):

        '''
        purpose: After the ArticleCoder is initialized, this method accepts one
           article instance and codes it for sourcing.  In regards to articles,
           this class is stateless, so you can process many articles with a
           single instance of this object without having to reconfigure each
           time.
           
        inheritance: This method overrides the abstract method of the same name in
           the ArticleCoder parent class.

        preconditions: load_config_properties() should have been invoked before
           running this method.

        postconditions: article passed in is coded, which means an Article_Data
           instance is created for it and populated to the extent the child
           class is capable of coding the article.
        '''

        # return reference
        status_OUT = self.STATUS_SUCCESS
        
        # declare variables
        me = "process_article"
        my_logger = None
        my_exception_helper = None
        automated_coding_user = None
        article_data = None
        
        # get logger
        my_logger = self.get_logger()
        
        # get exception_helper
        my_exception_helper = self.get_exception_helper()
        
        # get automated_coding_user
        automated_coding_user = coding_user_IN
        
        # got a user?
        if ( automated_coding_user is not None ):

            # got an article?
            if ( article_IN is not None ):
    
                # get Article_Data instance for user and coder_type.  Grab it
                #    first so we can store error information in it if problem
                #    on OpenCalais side.
                article_data = article_IN.get_article_data_for_coder( automated_coding_user, self.coder_type )
                
                # got article data?
                if ( article_data is not None ):
                
                    self.output_debug( "\n\nIn " + me + ": Article_Data instance id = " + str( article_data.id ) )
                
                else:
                
                    status_OUT = self.STATUS_ERROR_PREFIX + "Could not retrieve Article_Data instance.  Very odd.  Might mean we have multiple data records for coder \"" + automated_coding_user + "\" and coder_type \"" + self.coder_type + "\""
                    
                #-- END check to see if we found article data into which we'll code.
    
            #-- END check to see if article. --#
            
        else:
        
            status_OUT = self.STATUS_ERROR_PREFIX + "Could not find user with name \"automated\".  Can't code articles without a user."
            
        #-- END check to make sure we have an automated coding user. --#
        
        return status_OUT

    #-- END method process_article() --#
    

    def process_json_mention( self, article_IN, article_subject_IN, mention_JSON_IN ):
    
        '''
        Accepts Article, Article_Subject instance, and JSON of a
           mention of the subject.  Retrieves data from JSON.  Looks for mention
           that has same length, offset, and value.  If present, does nothing.
           If not, makes an Article_Subject_Mention instance for the mention,
           populates it, saves it, then returns it.  If error, returns None.
           
        Preconditions:  Assumes all input variables will be populated
           appropriately.  If any are missing or set to None, will break,
           throwing exceptions.
           
        Postconditions:  If mention wasn't already stored, it will be after
           this call.
           
        Example JSON:
        {
            "detection": "[ Fiat (SpA) that we have and we need to examine,\" ]Fred Diaz[, head of the Ram brand, said in an interview]",
            "exact": "Fred Diaz",
            "length": 9,
            "offset": 382,
            "prefix": " Fiat (SpA) that we have and we need to examine,\" ",
            "suffix": ", head of the Ram brand, said in an interview"
        }

        '''
        
        # return reference
        instance_OUT = None
        
        # declare variables
        me = "process_json_mention"
        mention_qs = None
        mention_count = -1
        current_mention = None
        
        # declare variables - Information from OpenCalais JSON
        mention_instances_list = None
        mention_detection = ""
        mention_exact = ""
        mention_length = ""
        mention_offset = ""
        mention_prefix = ""
        mention_suffix = ""
        
        # declare variables - get values from article text.
        article_text = None
        find_string = ""
        mention_FIT_values = {}
        FIT_status_list = []
        FIT_status_count = -1
        canonical_index_list = []
        plain_text_index_list = []
        paragraph_list = []
        first_word_list = []
        last_word_list = []
        
        # declare variables - values we'll place in instance at the end.
        canonical_index = -1
        plain_text_index = -1
        paragraph_number = -1
        first_word_number = -1
        last_word_number = -1
        is_ok_to_update = False
        current_value = None
        notes_list = []
        notes_count = -1
        notes_string = ""
        found_list = []
        found_list_count = -1
        sanity_check_index = -1
        found_dict = {}
        mention_prefix_length = -1
        mention_prefix_word_list = []
        mention_prefix_word_count = -1
        
        # declare variables - troubleshooting
        current_match = -1
        full_string_index = -1
        mention_prefix_length = -1
        calculated_match_index = -1
        
        # output JSON.
        self.output_debug( "++++++++ In " + me + " - Mention JSON:\n\n\n" + JSONHelper.pretty_print_json( mention_JSON_IN )  )

        # first, retrieve values from JSON, so we can use them to see if already
        #    added.
        
        # "detection" is the "exact" (mention), with "prefix" and "suffix"
        #    before and after, each enclosed in square brackets.
        #    - Example: [<"prefix">]<"exact">[<"suffix">]
        mention_detection = mention_JSON_IN.get( OpenCalaisApiResponse.JSON_NAME_DETECTION, None )
        
        # "exact" is the mention itself.
        #    - Examples: "he" or "Jim Morrison"
        mention_exact = mention_JSON_IN.get( OpenCalaisApiResponse.JSON_NAME_EXACT, None )
        
        # "length" is the length of the mention string.
        mention_length = mention_JSON_IN.get( OpenCalaisApiResponse.JSON_NAME_LENGTH, None )
        
        # "offset" is the index of the start of the mention string in the
        #    article text passed to OpenCalais (plain text).
        mention_offset = mention_JSON_IN.get( OpenCalaisApiResponse.JSON_NAME_OFFSET, None )
        
        # "prefix" is the text directly before the mention, for context.
        mention_prefix = mention_JSON_IN.get( OpenCalaisApiResponse.JSON_NAME_PREFIX, None )

        # "suffix" is the text directly after the mention, for context.
        mention_suffix = mention_JSON_IN.get( OpenCalaisApiResponse.JSON_NAME_SUFFIX, None )

        # is this mention already stored?
        
        # Filter on exact, offset, length, prefix, and suffix.
        mention_qs = article_subject_IN.article_subject_mention_set.filter( value = mention_exact )
        mention_qs = mention_qs.filter( value_index = mention_offset )
        mention_qs = mention_qs.filter( value_length = mention_length )
        mention_qs = mention_qs.filter( context_before = mention_prefix )
        mention_qs = mention_qs.filter( context_after = mention_suffix )
                        
        # got one?
        mention_count = mention_qs.count()
        if ( mention_count == 0 ):
                        
            # no.  Create one.
            current_mention = Article_Subject_Mention()
            
            # store the Article_Subject in it.
            current_mention.article_subject = article_subject_IN
            
            # store information from OpenCalais
            current_mention.value = mention_exact
            current_mention.value_in_context = mention_detection
            current_mention.value_index = mention_offset
            current_mention.value_length = mention_length
            current_mention.context_before = mention_prefix
            current_mention.context_after = mention_suffix
            
            # derive a few more details based on finding the mention in the text
            #    of the article.
            
            # get article text for article.
            article_text = article_IN.article_text_set.get()
            
            # then, call find_in_text (FIT) method on mention plus suffix (to
            #    make sure we get the right "he", for example).
            find_string = mention_exact + mention_suffix
            mention_FIT_values = article_text.find_in_text( find_string )
            
            # Validate results.
            FIT_status_list = self.validate_FIT_results( mention_FIT_values )
            
            # any error statuses passed back?
            FIT_status_count = len( FIT_status_list )
            if ( FIT_status_count == 0 ):
            
                # None - success!  Load items into variables.
                
                # get result lists.
                canonical_index_list = mention_FIT_values.get( Article_Text.FIT_CANONICAL_INDEX_LIST, [] )
                plain_text_index_list = mention_FIT_values.get( Article_Text.FIT_TEXT_INDEX_LIST, [] )
                paragraph_list = mention_FIT_values.get( Article_Text.FIT_PARAGRAPH_NUMBER_LIST, [] )
                first_word_list = mention_FIT_values.get( Article_Text.FIT_FIRST_WORD_NUMBER_LIST, [] )
                last_word_list = mention_FIT_values.get( Article_Text.FIT_LAST_WORD_NUMBER_LIST, [] )

                # load values from lists.
                plain_text_index = plain_text_index_list[ 0 ]
                
                if ( mention_offset != plain_text_index ):
                
                    # not the same.  output debug.
                    notes_string = "In " + me + ": ERROR - mention index from OpenCalais ( " + str( mention_offset ) + " ) doesn't match what we found ( " + str( plain_text_index ) + " ). Using local match index instead."
                    notes_list.append( notes_string )
                    self.output_debug( notes_string )
                    
                    # AND use what we calculated, not what OpenCalais returned.
                    plain_text_index = current_value

                #-- END check to see if index from OpenCalais matches --#

                canonical_index = canonical_index_list[ 0 ]
                paragraph_number = paragraph_list[ 0 ]
                first_word_number = first_word_list[ 0 ]

                # add the count of words in the actual mention minus
                #    1 (to account for the first word already being
                #    counted) to the first word value to get the last
                #    word number.
                mention_word_list = mention_exact.split()
                mention_word_count = len( mention_word_list )
                last_word_number = first_word_number + mention_word_count - 1

                # flag that it is OK to update.
                is_ok_to_update = True

            else:
            
                # add FIT_status_list to notes_list.
                notes_list = notes_list + FIT_status_list

                # try one-by-one.  Start with is_ok_to_update = True, then set
                #    to False if anything goes wrong.
                is_ok_to_update = True

                # to start, make sure the text is in the article.
                find_full_string = mention_prefix + mention_exact + mention_suffix
                found_list = article_text.find_in_plain_text( find_full_string )
                found_list_count = len( found_list )
                if ( found_list_count == 1 ):
                
                    # we know we have one match, so we can dig in and try to get
                    #    all the things.
                    sanity_check_index = found_list[ 0 ]
                    full_string_index = sanity_check_index
                    
                    #-----------------------------------------------------------
                    # plain text index
                    #-----------------------------------------------------------

                    # get actual plain text index (no prefix)
                    find_string = mention_exact + mention_suffix
                    found_list = article_text.find_in_plain_text( find_string )
                    found_list_count = len( found_list )
                    if ( found_list_count == 1 ):
                    
                        # load value.
                        plain_text_index = found_list[ 0 ]
                        
                        # see if it agrees with OpenCalais
                        if ( mention_offset != plain_text_index ):
                        
                            # not the same.  output debug.
                            notes_string = "In " + me + ": ERROR - mention index from OpenCalais ( " + str( mention_offset ) + " ) doesn't match what we found ( " + str( plain_text_index ) + " ). Using local match index instead."
                            notes_list.append( notes_string )
                            self.output_debug( notes_string )
                            
                            # AND use what we calculated, not what OpenCalais returned.
                            plain_text_index = current_value
        
                        #-- END check to see if index from OpenCalais matches --#
                        
                    elif ( found_list_count > 1 ):
                    
                        # multiple matches.  If at end of entire article, could
                        #    be because suffix is one or two words, there are
                        #    other matches in the article.
                        # Match = full_string_index + mention_prefix_length
                        mention_prefix_length = len( mention_prefix )
                        calculated_match_index = full_string_index + mention_prefix_length
                        if calculated_match_index in found_list:
                        
                            # the calculated match index is in list.  That is
                            #    the match.  Use it.
                            plain_text_index = calculated_match_index
                            
                        #-- END check to see which match is the right one.
                    
                    else:
                    
                        # ERROR.
                        notes_string = "In " + me + ": ERROR - plain text index - `mention + suffix` match count = " + str( found_list_count ) + ", `prefix + mention + suffix` was at index " + str( sanity_check_index )
                        notes_list.append( notes_string )
                        self.output_debug( notes_string )
                        
                        #is_ok_to_update = False
                        # might as well update, so we can see what else for
                        #    debugging. just set the plain text index to -1.
                        plain_text_index = -1
                    
                    #-- END check to see if found mention + suffix
                    
                    #-----------------------------------------------------------
                    # canonical index
                    #-----------------------------------------------------------

                    # canonical text seems to be a troublesome one.  Start out
                    #    looking for the full string.
                    found_list = article_text.find_in_canonical_text( find_full_string )
                    found_list_count = len( found_list )
                    if ( found_list_count == 1 ):
                    
                        # found it.  load value from list.
                        canonical_index = found_list[ 0 ]
                        
                        # then, add the length of the prefix to the value, to
                        #    get to the actual value.
                        mention_prefix_length = len( mention_prefix )
                        canonical_index = canonical_index + mention_prefix_length
                        
                    else:
                    
                        # ERROR.
                        notes_string = "In " + me + ": ERROR - canonical index - prefix + mention + suffix ( \"" + find_full_string + "\" ) either returned 0 or multiple matches: " + str( found_list )
                        notes_list.append( notes_string )
                        self.output_debug( notes_string )

                        # OK to update...  Just broken.
                        # is_ok_to_update = False
                    
                    #-- END check to see if found mention + suffix
                    
                    #-----------------------------------------------------------
                    # word first and last numbers
                    #-----------------------------------------------------------

                    # Start out looking for the full string.
                    found_dict = article_text.find_in_word_list( find_full_string )
                    first_word_list = found_dict.get( Article_Text.FIT_FIRST_WORD_NUMBER_LIST, [] )
                    last_word_list = found_dict.get( Article_Text.FIT_LAST_WORD_NUMBER_LIST, [] )
                    found_list_count = len( first_word_list )
                    if ( found_list_count == 1 ):
                    
                        # found it.  load values from lists.
                        first_word_number = first_word_list[ 0 ]
                        last_word_number = last_word_list[ 0 ]
                        
                        # then, add the number of words of the prefix to the
                        #    first word value, to get to the actual value.
                        mention_prefix_word_list = mention_prefix.split()
                        mention_prefix_word_count = len( mention_prefix_word_list )
                        first_word_number = first_word_number + mention_prefix_word_count
                        
                        # and add the count of words in the actual mention minus
                        #    1 (to account for the first word already being
                        #    counted) to the first word value to get the last
                        #    word number.
                        mention_word_list = mention_exact.split()
                        mention_word_count = len( mention_word_list )
                        last_word_number = first_word_number + mention_word_count - 1
                        
                    else:
                    
                        # ERROR.
                        notes_string = "In " + me + ": ERROR - word first and last numbers - prefix + mention + suffix ( \"" + find_full_string + "\" ) either returned 0 or multiple matches: " + str( found_list )
                        notes_list.append( notes_string )
                        self.output_debug( notes_string )

                        # OK to update...  Just broken.
                        # is_ok_to_update = False
                    
                    #-- END check to see if found mention + suffix
                    
                    #-----------------------------------------------------------
                    # paragraph number
                    #-----------------------------------------------------------

                    # Start out looking for the full string.
                    found_list = article_text.find_in_paragraph_list( find_full_string )
                    found_list_count = len( found_list )
                    if ( found_list_count == 1 ):
                    
                        # found it.  load value from list.
                        paragraph_number = found_list[ 0 ]
                        
                    else:
                    
                        # ERROR.
                        notes_string = "In " + me + ": ERROR - paragraph number - prefix + mention + suffix ( \"" + find_full_string + "\" ) either returned 0 or multiple matches: " + str( found_list )
                        notes_list.append( notes_string )
                        self.output_debug( notes_string )

                        # OK to update...  Just broken.
                        # is_ok_to_update = False
                    
                    #-- END check to see if found mention + suffix
                                        
                else:
                
                    # Either no match or multiple.
                    notes_string = "In " + me + ": ERROR - plain text index - prefix + mention + suffix ( \"" + find_full_string + "\" ) either returned 0 or multiple matches: " + str( found_list )
                    notes_list.append( notes_string )
                    self.output_debug( notes_string )
                    is_ok_to_update = False
                
                #-- END check to see if match for prefix + mention + suffix --#
                
            #-- END check to make sure all searches returned same count of matches. --#
            
            # OK to update the stuff from FIT?
            if ( is_ok_to_update == True ):

                # Yes.  Update them.
                current_mention.value_index = plain_text_index
                current_mention.canonical_index = canonical_index
                current_mention.value_word_number_start = first_word_number
                current_mention.value_word_number_end = last_word_number
                current_mention.paragraph_number = paragraph_number
            
            #-- END check to see if OK to update with info from FIT. --#

            # and store a few more details.
            current_mention.capture_method = self.coder_type

            # no UUID for a mention.
            #current_mention.uuid = quotation_URI_IN
            #current_mention.uuid_name = self.OPEN_CALAIS_UUID_NAME
            
            # notes?
            notes_count = len( notes_list )
            if ( notes_count > 0 ):
            
                # yes - join with newline, add to notes.
                notes_string = "\n".join( notes_list )
                current_mention.notes = notes_string
                
            #-- END check to see if notes. --#
                        
            # save the quotation instance.
            current_mention.save()
            
            # and return it.
            instance_OUT = current_mention
            
        elif ( mention_count == 1 ):
        
            # already got one.  Return it.
            instance_OUT = mention_qs.get()
        
        elif ( mention_count > 1 ):
        
            # trouble - more than one quotation for the UUID.
            self.output_debug( "++++++++ In " + me + " - ERROR - more than one mention matches.  Something is off..." )
            instance_OUT = None

        else:
        
            # trouble - count is invalid.
            self.output_debug( "++++++++ In " + me + " - ERROR - count of mention matches is neither 0, 1, or greater than 1.  Something is off..." )
            instance_OUT = None

        #-- END check to see if mention already stored. --#
        
        return instance_OUT
        
    #-- END method process_json_mention() --#

        
    def process_json_person( self, article_IN, article_data_IN, person_URI_IN, person_JSON_IN = None ):
        
        '''
        Accepts Article, Article_Data instance of article we are processing, and
           the JSON for the person who is the subject of the article that we are
           currently processing.  For each person:
           - look up the person.
              - If ambiguity, make a new person, but also keep track of other
                 potential matches (will need to add this to the database).
              - will probably need to refine the person lookup, too.  Right now, 
           - add person to Article_Data as Article_Subject instance.
           - add mentions to person's Article_Subject as Article_Subject_Mention
               instances.
           - check to see if quotations.  If yes:
              - change subject_type to "quoted".
              - add quotations to Article_Subject as Article_Subject_Quotation
                 instances.
           - save the Article_Subject and Article_Data.
           
        Returns Article_Subject instance for this person.
        
        Preconditions: Must have properly set up the following variables in the
           instance:
           - self.request_helper - instance of OpenCalaisApiResponse instance
              initialized with response JSON.
           - self.coder_type - should always be self.CONFIG_APPLICATION.
           - self.person_to_quotes_dict - dictionary of Person URIs to their
              quotations, created by method create_person_to_quotation_dict().
           
        Postconditions: If successful, a new Article_Subject for this person
           will have been created and saved to database on method completion.
           This Article_Subject instance will be returned.  If None returned,
           then there was an error and nothing was saved to the database.  See
           log file for more details on error.
        '''
        
        # return reference
        article_subject_OUT = None
        
        # declare variables
        me = "process_json_person"
        my_logger = None
        person_URI = ""
        person_json = None
        person_json_string = ""
        my_coder_type = ""
        
        # declare variables - person lookup
        person_name = ""
        article_subject = None
        person_details_dict = {}
        subject_person = None
        subject_match_list = None
        article_subject_set = None
        article_subject_qs = None
        article_subject_count = -1
        
        # alternate match processing
        alternate_person = None
        alternate_match_qs = None
        alternate_match = None

        # mention processing variables.
        mention_list = []
        mention_counter = -1
        current_mention = None
        
        # quotation processing variables
        person_to_quotes_map = {}
        uri_to_quotation_dictionary = {}
        person_quote_list = None
        quote_counter = -1
        current_quotation_URI = ""
        quotation_JSON = None
        quotation_qs = None
        current_quotation = None
        status_string = ""

        # get logger
        my_logger = self.get_logger()
        
        # get response helper
        my_response_helper = self.response_helper
        
        # initialize person variables from input arguments, instance variables.
        my_coder_type = self.coder_type
        person_URI = person_URI_IN
        
        # got URI?
        if ( ( person_URI is not None ) and ( person_URI != "" ) ):
        
            # yes - good.  Got JSON?
            if ( ( person_JSON_IN is not None ) and ( person_JSON_IN != "" ) ):
            
                # yes - use it.
                person_json = person_JSON_IN
                
            else:
            
                # no - look it up using URI.
                person_json = my_response_helper.get_item_from_response( person_URI )
                
            #-- END check to see if we have person JSON --#
            
            # convert JSON to string, for debugging and check to see if populated.
            person_json_string = JSONHelper.pretty_print_json( person_json )
                        
            self.output_debug( "+++++ Person JSON for URI: \"" + person_URI + "\"\n\n\n" + person_json_string )
                        
            # Do we have JSON?
            if ( ( person_json is not None ) and ( person_json_string.strip() != "null" ) ):
                        
                # yes - get and output name.
                person_name = JSONHelper.get_json_object_property( person_json, OpenCalaisApiResponse.JSON_NAME_PERSON_NAME )
                
                my_logger.debug( "In " + me + ": person name = " + person_name )
                
                # try looking up source just like we look up authors.
    
                # make empty article subject to work with, for now.
                article_subject = Article_Subject()
                article_subject.subject_type = Article_Subject.SUBJECT_TYPE_MENTIONED
                
                # prepare person details.
                person_details_dict = {}
                person_details_dict[ self.PARAM_NEWSPAPER_INSTANCE ] = article_IN.newspaper
                person_details_dict[ self.PARAM_EXTERNAL_UUID_NAME ] = self.OPEN_CALAIS_UUID_NAME
                person_details_dict[ self.PARAM_EXTERNAL_UUID ] = person_URI
                person_details_dict[ self.PARAM_EXTERNAL_UUID_SOURCE ] = my_coder_type
                person_details_dict[ self.PARAM_CAPTURE_METHOD ] = my_coder_type                        
    
                # lookup person - returns person and confidence score inside
                #    Article_Subject instance.
                article_subject = self.lookup_person( article_subject, 
                                                      person_name,
                                                      create_if_no_match_IN = True,
                                                      update_person_IN = True,
                                                      person_details_IN = person_details_dict )

                # get results from article_subject
                subject_person = article_subject.person
                subject_person_match_list = article_subject.person_match_list  # list of Person instances
                                        
                # got a person?
                if ( subject_person is not None ):
    
                    # One Article_Subject per person, and then have a new thing to
                    #    hold mentions and quotations that hangs off that.
                    
                    # Now, we need to deal with Article_Subject instance.  First, see
                    #    if there already is one for this name.  If so, do nothing.
                    #    If not, make one.
    
                    # get sources
                    article_subject_set = article_data_IN.article_subject_set.all()
                    article_subject_qs = article_subject_set.filter( person = subject_person )
                    article_subject_count = article_subject_qs.count()
                                
                    # got anything?
                    if ( article_subject_count == 0 ):
                                                 
                        # no - add - more stuff to set.  Need to see what we can get.
                        
                        # use the source Article_Subject created for call to
                        #    lookup_person().
                        #article_source = Article_Subject()
                    
                        article_subject.article_data = article_data_IN
                        article_subject.person = subject_person
                        
                        # confidence level set in lookup_person() method.
                        #article_subject.match_confidence_level = 1.0
        
                        article_subject.source_type = Article_Subject.SOURCE_TYPE_INDIVIDUAL
                        article_subject.title = ""
                        article_subject.more_title = ""
                        article_subject.organization = None # models.ForeignKey( Organization, blank = True, null = True )
                        #article_subject.document = None
                        article_subject.source_contact_type = Article_Subject.SOURCE_CONTACT_TYPE_OTHER
                        #article_subject.source_capacity = None
                        #article_subject.localness = None
                        article_subject.notes = ""
        
                        # field to store how source was captured.
                        article_subject.capture_method = self.coder_type
                    
                        # save, and as part of save, record alternate matches.
                        article_subject.save()
                        
                        # !TODO - topics?
                        # if we want to set topics, first save article_source, then
                        #    we can parse them out of the JSON, make sure they exist
                        #    in topics table, then add relation.  Probably want to
                        #    make Person_Topic also.  So, if we do this, it will be
                        #    a separate method.
                        #article_source.topics = None # models.ManyToManyField( Topic, blank = True, null = True )
    
                        my_logger.debug( "In " + me + ": adding Article_Subject instance for " + str( subject_person ) + "." )
        
                    elif ( article_subject_count == 1 ):
                    
                        my_logger.debug( "In " + me + ": Article_Subject instance already exists for " + str( subject_person ) + "." )
                        
                        # retrieve article source from query set.
                        article_subject = article_subject_qs.get()
                        
                        # !UPDATE existing Article_Subject
                        # !UPDATE alternate matches

                        # Were there alternate matches?
                        if ( len( subject_person_match_list ) > 0 ):
                        
                            # yes - store the list of alternate matches in the
                            #    Article_Subject instance variable
                            #    "person_match_list".
                            article_subject.person_match_list = subject_person_match_list
                            
                            # call method to process alternate matches.
                            my_logger.debug( "In " + me + ": @@@@@@@@ Existing Article_Subject found for person, calling process_alternate_matches." )
                            article_subject.process_alternate_matches()
                            
                        #-- END check to see if there were alternate matches --#
                        
                    else:
                    
                        # neither 0 or 1 sources - either invalid or multiple,
                        #    either is not right.
                        my_logger.debug( "In " + me + ": Article_Subject count for " + str( subject_person ) + " = " + str( article_subject_count ) + ".  What to do?" )
                        
                        # make sure we don't go any further.
                        article_subject = None
                                            
                    #-- END check if need new Article_Subject instance --#
                                
                    # make sure we have an article_subject
                    if ( ( article_subject is not None ) and ( article_subject.id ) ):
    
                        # !deal with mentions.
                        
                        # get list of mentions from Person's "instances"
                        mention_list = JSONHelper.get_json_object_property( person_json, OpenCalaisApiResponse.JSON_NAME_INSTANCES )
        
                        # loop
                        mention_counter = 0
                        for current_mention in mention_list:
                        
                            # incremenet counter
                            mention_counter = mention_counter + 1
                        
                            self.output_debug( "Mention " + str( mention_counter ) )
                            
                            # call method to process mention.
                            self.process_json_mention( article_IN, article_subject, current_mention )
        
                        #-- END loop over mentions --#
        
                        # !deal with quotes.
                        # to start, loop over the quotes associated with the current
                        #    person and see what is in them.
                        
                        # get map of URIs to JSON for "Quotation" item type.
                        uri_to_quotation_dictionary = my_response_helper.get_items_of_type( OpenCalaisApiResponse.OC_ITEM_TYPE_QUOTATION )
                        
                        # get map of people to quotes, quote list for
                        #    current person.
                        person_to_quotes_map = self.person_to_quotes_dict
                        person_quote_list = person_to_quotes_map.get( person_URI, [] )
                        
                        # loop
                        quote_counter = 0
                        for current_quotation_URI in person_quote_list:
        
                            # increment counter
                            quote_counter = quote_counter + 1
        
                            self.output_debug( "Quotation " + str( quote_counter ) + " URI: " + current_quotation_URI )
                            
                            # get JSON from URI_to_quotation_dictionary.
                            quotation_JSON = uri_to_quotation_dictionary.get( current_quotation_URI, None )
        
                            # got one?
                            if ( quotation_JSON is not None ):
        
                                self.process_json_quotation( article_IN, article_subject, current_quotation_URI, quotation_JSON )
                                
                            #-- END check to see if Quotation JSON --#
                            
                        #-- END loop over quotations --#
                        
                        # How many quotes?
                        if ( quote_counter > 0 ):
                        
                            # at least one - set subject-type to quoted.
                            article_subject.subject_type = Article_Subject.SUBJECT_TYPE_QUOTED
                            article_subject.save()
                            
                        #-- END check to see if quotes present. --#
                        
                        # return reference to article_subject.
                        article_subject_OUT = article_subject
                        
                    #-- END check to make sure we have an Article_Subject --#
                
                else:
                
                    # error - no person found for name.
                    my_logger.debug( "In " + me + ": ERROR - no matching person found - must have been a problem looking up name \"" + person_name + "\"" )
                    article_subject_OUT = None
    
                #-- END check to see if person found. --#
                
            else:
            
                # When JSON is not present for a person URI, is a problem with OpenCalais.
                status_string = "In OpenCalaisArticleCoder." + me + ": ERROR - No Person JSON for URI: \"" + person_URI + "\".  When OpenCalais includes URIs that don't have matches in the JSON, that usually means an error occurred.  Probably should reprocess this article.  JSON contents: " + person_json_string.strip()
                article_data_IN.set_status( Article_Data.STATUS_SERVICE_ERROR, status_string  )
                article_subject_OUT = None
            
                # log it.
                my_logger.debug( status_string )
                
            #-- END check to see if JSON present for person URI --#
            
        else:
        
            # No URI, nothing we can do.  Who is it?
            my_logger.debug( "In " + me + ": ERROR - no URI passed in for person.  Can not continue." )
            article_subject_OUT = None
        
        #-- END check to make sure we have a URI --#
        
        return article_subject_OUT
    
    #-- END function process_json_person() --#


    def process_json_quotation( self, article_IN, article_subject_IN, quotation_URI_IN, quotation_JSON_IN ):
    
        '''
        Accepts Article, Article_Subject of a source, OpenCalais URI of a
           quotation, and JSON of a quotation attributed to the source.  Uses
           URI to check if the quotation has already been attributed to the
           source.  If so, returns the instance.  If not, creates an instance
           and saves it, then returns it.  If error, returns None.
           
        Preconditions:  Assumes all input variables will be populated
           appropriately.  If any are missing or set to None, will break,
           throwing exceptions.
           
        Postconditions:  If quotation wasn't already stored, it will be after
           this call.
           
        Example JSON (bonus - can you find the OpenCalais parsing error?):
        {
            "_type": "Quotation",
            "_typeGroup": "relations",
            "_typeReference": "http://s.opencalais.com/1/type/em/r/Quotation",
            "instances": [
                {
                    "detection": "[went on sale in 2005 to limited success. ]Sales through November are less than 15,000, down 54 percent, according to Autodata Corp. Toyota Motor Corp. showed the A-BAT concept, a small hybrid unibody pickup, at the 2008 Detroit auto show but has no immediate plans to put it into production, said spokesman John McCandless.[ \"A lot of people have tried the idea of creating]",
                    "exact": "Sales through November are less than 15,000, down 54 percent, according to Autodata Corp. Toyota Motor Corp. showed the A-BAT concept, a small hybrid unibody pickup, at the 2008 Detroit auto show but has no immediate plans to put it into production, said spokesman John McCandless.",
                    "length": 281,
                    "offset": 2110,
                    "prefix": "went on sale in 2005 to limited success. ",
                    "suffix": " \"A lot of people have tried the idea of creating"
                }
            ],
            "person": "http://d.opencalais.com/pershash-1/52f81716-30d1-3b2b-bc98-16e50eb06782",
            "persondescription": "spokesman",
            "quote": "Sales through November are less than 15,000, down 54 percent, according to Autodata Corp. Toyota Motor Corp. showed the A-BAT concept, a small hybrid unibody pickup, at the 2008 Detroit auto show but has no immediate plans to put it into production"
        }
        '''
        
        # return reference
        instance_OUT = None
        
        # declare variables
        me = "process_json_quotation"
        quotation_qs = None
        quotation_count = -1
        
        # declare variables - Information from OpenCalais JSON
        quotation_string = ""
        quotation_person_title = ""
        quotation_instances_list = None
        current_quotation = None
        quotation_detection = ""
        quotation_exact = ""
        quotation_length = ""
        quotation_offset = ""
        quotation_prefix = ""
        quotation_suffix = ""
        
        # declare variables - get values from article text.
        article_text = None
        quotation_FIT_values = {}
        FIT_status_list = []
        FIT_status_count = -1
        canonical_index_list = []
        plain_text_index_list = []
        paragraph_list = []
        first_word_list = []
        last_word_list = []
        
        # declare variables - values we'll place in instance at the end.
        canonical_index = -1
        plain_text_index = -1
        paragraph_number = -1
        first_word_number = -1
        last_word_number = -1
        is_ok_to_update = False
        current_value = None
        notes_list = []
        notes_count = -1
        notes_string = ""
        
        # output JSON.
        self.output_debug( "++++++++ In " + me + " - Quotation JSON:\n\n\n" + JSONHelper.pretty_print_json( quotation_JSON_IN )  )

        # need to see if this quotation has already been stored.

        # Filter on UUID from Quotation JSON object.
        quotation_qs = article_subject_IN.article_subject_quotation_set.filter( uuid = quotation_URI_IN )
                        
        # got one?
        quotation_count = quotation_qs.count()
        if ( quotation_count == 0 ):
                        
            # no.  Create one.
            current_quotation = Article_Subject_Quotation()
            
            # store the Article_Subject in it.
            current_quotation.article_subject = article_subject_IN
            
            # get actual quotation information from JSON
            
            # "quote" is the quotation without an attribution string.
            quotation_string = quotation_JSON_IN.get( OpenCalaisApiResponse.JSON_NAME_QUOTE, None )
            
            self.output_debug( "In " + me + ": quotation_string = \"" + quotation_string + "\"" )

            # "persondescription" is the description of the person that
            #    accompanied attribution for the quote.
            #    - Example: would be "spokesman" for atttribution string
            #       ", said spokesman John McCandless."
            quotation_person_title = quotation_JSON_IN.get( OpenCalaisApiResponse.JSON_NAME_PERSON_DESCRIPTION, None )

            # more details are stored in JSON object referred to as "instances".
            quotation_instances_list = quotation_JSON_IN.get( OpenCalaisApiResponse.JSON_NAME_INSTANCES, None )
            current_instance = quotation_instances_list[ 0 ]
            
            # get values from OpenCalais instance
            
            # "detection" is the "exact" (quote plus attribution), with "prefix"
            #    and "suffix" before and after, each enclosed in square
            #    brackets.
            #    - Example: [<"prefix">]<"exact">[<"suffix">]
            quotation_detection = current_instance.get( OpenCalaisApiResponse.JSON_NAME_DETECTION, None )
            
            # "exact" is the quotation plus the attribution string.
            #    - Example: "quote", said Jim.
            quotation_exact = current_instance.get( OpenCalaisApiResponse.JSON_NAME_EXACT, None )
            
            # "length" is the length of the quotation string.
            quotation_length = current_instance.get( OpenCalaisApiResponse.JSON_NAME_LENGTH, None )
            
            # "offset" is the index of the start of the quotation string in the
            #    article text passed to OpenCalais (plain text).
            quotation_offset = current_instance.get( OpenCalaisApiResponse.JSON_NAME_OFFSET, None )
            
            # "prefix" is the text directly before the quotation, included for
            #    context.
            quotation_prefix = current_instance.get( OpenCalaisApiResponse.JSON_NAME_PREFIX, None )

            # "suffix" is the text directly after the quotation, included for
            #    context.
            quotation_suffix = current_instance.get( OpenCalaisApiResponse.JSON_NAME_SUFFIX, None )

            # store information from OpenCalais
            current_quotation.value = quotation_string
            current_quotation.value_with_attribution = quotation_exact
            current_quotation.value_in_context = quotation_detection
            current_quotation.value_index = quotation_offset
            current_quotation.value_length = quotation_length
            current_quotation.context_before = quotation_prefix
            current_quotation.context_after = quotation_suffix
            
            # derive a few more details based on finding the quote in the text
            #    of the article.
            
            # get article text for article.
            article_text = article_IN.article_text_set.get()
            
            # then, call find_in_text (FIT) method.  When we deal with words, we
            #    split on spaces.  Because of this, "words" must include the
            #    punctuation around them for them to match.  The quotation_string
            #    doesn't include punctuation, so we can't use it.  Instead, we
            #    need to use the "exact" string, since it includes punctuation.
            quotation_FIT_values = article_text.find_in_text( quotation_exact )
            
            # Validate results.
            FIT_status_list = self.validate_FIT_results( quotation_FIT_values )

            # any error statuses passed back?
            FIT_status_count = len( FIT_status_list )
            if ( FIT_status_count == 0 ):
            
                # None - success!
                
                self.output_debug( "In " + me + ": FIT status was good - single match for each element we are looking for." )

                # get result lists.
                canonical_index_list = quotation_FIT_values.get( Article_Text.FIT_CANONICAL_INDEX_LIST, [] )
                plain_text_index_list = quotation_FIT_values.get( Article_Text.FIT_TEXT_INDEX_LIST, [] )
                paragraph_list = quotation_FIT_values.get( Article_Text.FIT_PARAGRAPH_NUMBER_LIST, [] )
                first_word_list = quotation_FIT_values.get( Article_Text.FIT_FIRST_WORD_NUMBER_LIST, [] )
                last_word_list = quotation_FIT_values.get( Article_Text.FIT_LAST_WORD_NUMBER_LIST, [] )

                # this is the normal case.  Save the values into our current
                #    quotation instance.
                
                # make sure that the plain text index matches the one from
                #    OpenCalais.
                plain_text_index = plain_text_index_list[ 0 ]
                if ( quotation_offset != plain_text_index ):
                
                    # not the same.  output debug.
                    notes_string = "In " + me + ": ERROR - quotation index from OpenCalais ( " + str( quotation_offset ) + " ) doesn't match what we found ( " + str( plain_text_index ) + " ).  Using local match index instead."
                    notes_list.append( notes_string )
                    self.output_debug( notes_string )
                    
                    # AND use what we calculated, not what OpenCalais returned.
                    current_quotation.value_index = plain_text_index

                #-- END check to see if index from OpenCalais matches --#
                
                # canonical index
                canonical_index = canonical_index_list[ 0 ]
                
                # value_word_number_start
                first_word_number = first_word_list[ 0 ]
                
                # value_word_number_end
                last_word_number = last_word_list[ 0 ]

                # paragraph_number
                paragraph_number = paragraph_list[ 0 ]
                
                # flag that it is OK to update.
                is_ok_to_update = True

            else:

                # add FIT_status_list to notes_list.
                notes_list = notes_list + FIT_status_list

                self.output_debug( "In " + me + ": FIT status was bad - see if the string is actually in the article." )

                # try one-by-one.  Start with is_ok_to_update = True, then set
                #    to False if anything goes wrong.
                is_ok_to_update = True

                # to start, make sure the text is in the article.
                found_list = article_text.find_in_plain_text( quotation_exact )
                found_list_count = len( found_list )
                if ( found_list_count == 1 ):
                
                    # we know we have one match, so we can dig in and try to get
                    #    all the things.
                    
                    #-----------------------------------------------------------
                    # plain text index
                    #-----------------------------------------------------------

                    # store the plain text index from check above.
                    plain_text_index = found_list[ 0 ]
                    
                    # see if it agrees with OpenCalais
                    if ( quotation_offset != plain_text_index ):
                    
                        # not the same.  output debug.
                        notes_string = "In " + me + ": ERROR - quotation index from OpenCalais ( " + str( quotation_offset ) + " ) doesn't match what we found ( " + str( plain_text_index ) + " ).  Using local match index instead."
                        notes_list.append( notes_string )
                        self.output_debug( notes_string )
                        
                        # AND use what we calculated, not what OpenCalais returned.
                        plain_text_index = plain_text_index
    
                    #-- END check to see if index from OpenCalais matches --#
                        
                    #-----------------------------------------------------------
                    # canonical index
                    #-----------------------------------------------------------

                    # canonical text seems to be a troublesome one.  Start out
                    #    looking for the full string.
                    found_list = article_text.find_in_canonical_text( quotation_exact )
                    found_list_count = len( found_list )
                    if ( found_list_count == 1 ):
                    
                        # found it.  load value from list.
                        canonical_index = found_list[ 0 ]
                        
                    else:
                    
                        # ERROR.
                        notes_string = "In " + me + ": ERROR - canonical index - search for quotation ( \"" + quotation_string + "\" ) either returned 0 or multiple matches: " + str( found_list )
                        notes_list.append( notes_string )
                        self.output_debug( notes_string )
                        
                        # set canonical_index to -1.
                        canonical_index = -1

                        # OK to update...  Just broken.
                        # is_ok_to_update = False
                    
                    #-- END check to see if found mention + suffix
                    
                    #-----------------------------------------------------------
                    # word first and last numbers
                    #-----------------------------------------------------------

                    # Start out looking for the full string.
                    found_dict = article_text.find_in_word_list( quotation_exact )
                    
                    self.output_debug( "In " + me + ": results of looking for string in word list: " + str( found_dict ) )
                    
                    first_word_list = found_dict.get( Article_Text.FIT_FIRST_WORD_NUMBER_LIST, [] )
                    last_word_list = found_dict.get( Article_Text.FIT_LAST_WORD_NUMBER_LIST, [] )
                    found_list_count = len( first_word_list )
                    if ( found_list_count == 1 ):
                    
                        # found it.  load values from lists.
                        first_word_number = first_word_list[ 0 ]
                        last_word_number = last_word_list[ 0 ]
                        
                    else:
                    
                        # ERROR.
                        notes_string = "In " + me + ": ERROR - word first and last numbers - search for quotation ( \"" + quotation_string + "\" ) either returned 0 or multiple matches: " + str( first_word_list )
                        notes_list.append( notes_string )
                        self.output_debug( notes_string )

                        # OK to update...  Just broken.
                        # is_ok_to_update = False
                    
                    #-- END check to see if found mention + suffix
                    
                    #-----------------------------------------------------------
                    # paragraph number
                    #-----------------------------------------------------------

                    # Start out looking for the full string.
                    found_list = article_text.find_in_paragraph_list( quotation_exact )
                    found_list_count = len( found_list )
                    if ( found_list_count == 1 ):
                    
                        # found it.  load value from list.
                        paragraph_number = found_list[ 0 ]
                        
                    else:
                    
                        # ERROR.
                        notes_string = "In " + me + ": ERROR - paragraph number - search for quotation ( \"" + quotation_string + "\" ) either returned 0 or multiple matches: " + str( found_list )
                        notes_list.append( notes_string )
                        self.output_debug( notes_string )

                        # OK to update...  Just broken.
                        # is_ok_to_update = False
                    
                    #-- END check to see if found mention + suffix
                    
                #-- END check to see if quotation is in plain text string --#
                                        
            #-- END check to make sure all searches returned same count of matches. --#

            # OK to update the stuff from FIT?
            if ( is_ok_to_update == True ):

                # Yes.  Update them.
                current_quotation.value_index = plain_text_index
                current_quotation.canonical_index = canonical_index
                current_quotation.value_word_number_start = first_word_number
                current_quotation.value_word_number_end = last_word_number
                current_quotation.paragraph_number = paragraph_number
            
            #-- END check to see if OK to update with info from FIT. --#

            # and store a few more details.
            current_quotation.capture_method = self.coder_type
            current_quotation.uuid = quotation_URI_IN
            current_quotation.uuid_name = self.OPEN_CALAIS_UUID_NAME
            
            # notes?
            if ( len( notes_list ) > 0 ):
            
                # yes - join with newline, add to notes.
                notes_string = "\n".join( notes_list )
                current_quotation.notes = notes_string
                
            #-- END check to see if notes. --#
                        
            # Deferring handling of attribution information for now.
            # fields to track locations of data this coding was based on within
            #    article.  References are based on results of ParsedArticle.parse().
            #article_subject.attribution_verb_word_index = -1
            #article_subject.attribution_verb_word_number = -1
            #article_subject.attribution_paragraph_number = -1
            #article_subject.attribution_speaker_name_string = -1
            #article_subject.is_speaker_name_pronoun = False
            #article_subject.attribution_speaker_name_index_range = ""
            #article_subject.attribution_speaker_name_word_range = ""
            
            # save the quotation instance.
            current_quotation.save()
            
            # and return it.
            instance_OUT = current_quotation
            
        elif ( quotation_count == 1 ):
        
            # already got one.  Return it.
            instance_OUT = quotation_qs.get()
        
        elif ( quotation_count > 1 ):
        
            # trouble more than one quotation for the UUID.
            self.output_debug( "++++++++ In " + me + " - ERROR - more than one quotation matches URI \"" + quotation_URI_IN + "\".  Something is off..." )
            instance_OUT = None

        else:
        
            # trouble - count is invalid.
            self.output_debug( "++++++++ In " + me + " - ERROR - count of matches to URI \"" + quotation_URI_IN + "\" is neither 0, 1, or greater than 1.  Something is off..." )
            instance_OUT = None

        #-- END check to see if quote already stored. --#
        
        return instance_OUT
        
    #-- END method process_json_quotation() --#

    
    def process_person_store_json( self, request_IN, article_id_IN, person_store_json_string_IN, article_data_id_IN, response_dictionary_IN ):
    
        # return reference
        article_data_OUT = None
    
        # declare variables
        me = "article_code_process_json"
        
        # declare variables - coding submission.
        coder_user = None
        person_store_json_string = ""
        person_store_json = None
        article_data_id = -1
        person_list = []
        person_count = -1
        coder_user = None
        person_type = ""
        person_name = ""
        name_and_title = ""
        quote_text = ""
        person_id = -1
        current_article_data = None
        current_article = None
        current_person = None
    
        # got an article ID?
        if ( ( article_id_IN is not None ) and ( article_id_IN != "" ) and ( article_id_IN > 0 ) ):
        
            # yes, we have an article ID.  Got a coder user?
            coder_user = request_IN.user
            if ( coder_user is not None ):
            
                # Got a JSON string?
                person_store_json_string = person_store_json_string_IN
                if ( ( person_store_json_string is not None ) and ( person_store_json_string != "" ) ):
                
                    # got a JSON string, convert to Python objects.
                    person_store_json = json.loads( person_store_json_string )
                    
                    # get list of people.
                    person_list = person_store_json[ "person_array" ]
                    
                    # get count of persons
                    person_count = len( person_list )
                    
                    # got one or more people?
                    if ( person_count > 0 ):
                    
                        # yes.  Got an Article_Data ID?
                        if ( ( article_data_id_IN is not None ) and ( article_data_id_IN != "" ) and ( article_data_id_IN > 0 ) ):
                        
                            # we have an Article_Data ID.  look up.
                            try:
        
                                # use exception handling to see if record already exists.
                                
                                # filter on ID
                                current_article_data = Article_Data.objects.filter( pk = article_data_id_IN )
                                
                                # then ues get() to make sure this ID belongs to the current user.
                                current_article_data = current_article_data.get( coder = coder_user )
                        
                            except Exception as e:
                            
                                # not found.  Set current_article_data tp None.
                                current_article_data = None
                        
                            #-- END check to see if we can find existing article data. --#
                            
                        #-- END check to see if article data already exists. --#
                        
                        # got article data?
                        if ( current_article_data is None ):
                        
                            # no Article_Data.  Create a new record.
                            current_article_data = Article_Data()
                            
                            # get article for ID, store in Article_Data.
                            current_article = Article.objects.get( pk = article_id_IN )
                            current_article_data.article = current_article
                            current_article_data.coder = coder_user
                        
                        #-- END check to see if Article_Data instance. --#
                    
                        # loop over persons
                        for current_person in person_array:
                        
                            # retrieve person information.
                            person_type = current_person.get( "person_type" )
                            person_name =  current_person.get( "person_name" )
                            name_and_title =  current_person.get( "name_and_title" )
                            quote_text =  current_person.get( "quote_text" )
                            person_id =  current_person.get( "person_id" )
                            
                            # got a person ID?
                            if ( ( person_id is not None ) and ( person_id > 0 ) ):
                            
                                # We have a person ID.  Lookup Person.
                                current_person = Person.objects.get( pk = person_id )
                            
                            else:
                            
                                # no person ID.  Create person based on name.
                                pass
                                
                                # !TODO - need ManualCoder, extension of ArticleCoder.
                                
                            # check person type to see what we are adding.
                            
                            # Article_Source
                            
                            # Article_Author
                            
                            # either way, if already a record for person ID, move on
                            #    for now, we can always make an update routine
                            #    later.
                        
                        #-- END loop over persons --#
                        
                    #-- END check to see if there are any persons. --#
                    
                    # store JSON string in response dictionary
                    response_dictionary_IN[ 'person_store_json' ] = person_store_json_string    
    
                else:
                
                    # no JSON - can't process.
                    self.output_debug( "ERROR - No JSON passed in - must have data in JSON to process that data...", me, "====> " )
                    article_data_OUT = None
                
                #-- END check to see if JSON string passed in.
                
            else:
            
                # no coder user?  That is an odd error.
                self.output_debug( "ERROR - No coder user passed in - must have a coder user...", me, "====> " )
                article_data_OUT = None
            
        else:
        
            # no article ID - can't process.
            self.output_debug( "ERROR - No article ID passed in - must have an article ID to code an article...", me, "====> " )
            article_data_OUT = None
        
        #-- END check to see if article ID passed in.
    
        return article_data_OUT
    
    #-- END function process_person_store_json() --#


    def validate_FIT_results( self, FIT_values_IN ):

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
        # - If more than one, multiple matches - ERROR.
        # - All lists should have same count.  If any are different - ERROR.

        # get result lists.
        canonical_index_list = FIT_values_IN.get( Article_Text.FIT_CANONICAL_INDEX_LIST, [] )
        plain_text_index_list = FIT_values_IN.get( Article_Text.FIT_TEXT_INDEX_LIST, [] )
        paragraph_list = FIT_values_IN.get( Article_Text.FIT_PARAGRAPH_NUMBER_LIST, [] )
        first_word_list = FIT_values_IN.get( Article_Text.FIT_FIRST_WORD_NUMBER_LIST, [] )
        last_word_list = FIT_values_IN.get( Article_Text.FIT_LAST_WORD_NUMBER_LIST, [] )

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
                self.output_debug( status_OUT )
                
            elif ( match_count > 1 ):
            
                # error - multiple matches returned for quotation.  What to do?
                status_OUT = "In " + me + ": ERROR - search for string in text yielded " + str( match_count ) + " matches."
                status_list_OUT.append( status_OUT )
                self.output_debug( status_OUT )
                
            else:
            
                # error - matches returned something other than 0, 1, or
                #    > 1.  What to do?
                status_OUT = "In " + me + ": ERROR - search for string in text yielded invalid count: " + str( match_count )
                status_list_OUT.append( status_OUT )
                self.output_debug( status_OUT )
                
            #-- END check to see how many matches were found. --#
            
        else:

            # error - unique_count_list does not have only one thing in it.
            status_OUT = "In " + me + ": ERROR - search for string in text yielded different numbers of results for different ways of searching: " + str( unique_count_list )
            status_list_OUT.append( status_OUT )
            self.output_debug( status_OUT )
            
        #-- END check to make sure all searches returned same count of matches. --#
        
        return status_list_OUT        
        
    #-- END method validate_FIT_results() --#


#-- END class ManualArticleCoder --#