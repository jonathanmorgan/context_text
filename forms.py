from __future__ import unicode_literals

'''
Copyright 2010-2016 Jonathan Morgan

This file is part of http://github.com/jonathanmorgan/sourcenet.

sourcenet is free software: you can redistribute it and/or modify it under the terms of the GNU Lesser General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.

sourcenet is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.

You should have received a copy of the GNU Lesser General Public License along with http://github.com/jonathanmorgan/sourcenet. If not, see http://www.gnu.org/licenses/.
'''

'''
How to add a value to one of these sourcenet forms and then get that value
properly passed through to all the things that might use it:

- 1) If your form input will have a set of values from which the user will
    choose, figure out what those values will be and make variables to hold the
    specific values and to hold a dictionary that maps values to display names
    in the appropriate class in sourcenet.  For example:
    - add parameters related to network output to the class NetworkOutput in
        file /export/network_output.py (though if those parameters will also be
        used by NetworkDataOutput, you should declare them there, then just
        reference them in NetworkOutput).
    - add parameters related to automated coding of articles to the class
        ArticleCoding, in file /article_coding/article_coding.py.
        
    Example - adding person query type values to NetworkDataOutput:
    
        # Person Query Types
        PERSON_QUERY_TYPE_ALL = "all"
        PERSON_QUERY_TYPE_ARTICLES = "articles"
        PERSON_QUERY_TYPE_CUSTOM = "custom"
        
        PERSON_QUERY_TYPE_CHOICES_LIST = [ 
            ( PERSON_QUERY_TYPE_ALL, "All persons" ),
            ( PERSON_QUERY_TYPE_ARTICLES, "From selected articles" ),
            ( PERSON_QUERY_TYPE_CUSTOM, "Custom, defined below" ),
        ]

    And then referencing them from NetworkOutput:
    
        # Person Query Types
        PERSON_QUERY_TYPE_ALL = NetworkDataOutput.PERSON_QUERY_TYPE_ALL
        PERSON_QUERY_TYPE_ARTICLES = NetworkDataOutput.PERSON_QUERY_TYPE_ARTICLES
        PERSON_QUERY_TYPE_CUSTOM = NetworkDataOutput.PERSON_QUERY_TYPE_CUSTOM
    
        PERSON_QUERY_TYPE_CHOICES_LIST = NetworkDataOutput.PERSON_QUERY_TYPE_CHOICES_LIST    

- 2) Add a PARAM_* constant that contains the input name you'll use to reference
    the new field in the form, and then subsequently whenever the associated 
    value is needed throughout the application.  Example - adding a person query
    type to tell network outputter how to figure out which people to include in
    the network, first to NetworkDataOutput:
    
        PARAM_PERSON_QUERY_TYPE = "person_query_type"

    Then, referring to it in NetworkOutput:
    
        PARAM_PERSON_QUERY_TYPE = NetworkDataOutput.PARAM_PERSON_QUERY_TYPE
        
- 3) Add that parameter to PARAM_NAME_TO_TYPE_MAP in NetworkOutput or
    ArticleCoding, with the parameter name mapped to the appropriate type from
    the ParamContainer class in python_utilities.  Example, adding our string
    person query type to NetworkOutput's PARAM_NAME_TO_TYPE_MAP:
    
        PARAM_PERSON_QUERY_TYPE : ParamContainer.PARAM_TYPE_STRING,

- 4) Add the value to the appropriate form below, using the same name as was in
    your PARAM_* constant.  Example - adding a person query type select box to
    the person select form, referencing the choices list defined above:

        person_query_type = forms.ChoiceField( required = False, choices = NetworkOutput.PERSON_QUERY_TYPE_CHOICES_LIST )

- 5) Into what function or method do I then update processing to include the
    new field?:
    - For network output, method that creates QuerySets from form parameters is
        create_query_set(), in sourcenet/export/network_output.py,
        NetworkOutput.create_query_set().  This method is called by both
        create_person_query_set() and create_network_query_set().  If you add
        a parameter to the article select and the person select, make sure
        make the name of the person input the same as the article one, but
        preceded by "person_".  That will make the single method able to
        process values for either the article or person form.  For example, the
        coder_type_filter_type, from NetworkDataOutput class:

            PARAM_CODER_TYPE_FILTER_TYPE = "coder_type_filter_type"
            PARAM_PERSON_CODER_TYPE_FILTER_TYPE = "person_" + PARAM_CODER_TYPE_FILTER_TYPE

'''

# import six for Python 2 and 3 compatibility.
import six

# import django form object.
from django import forms

# import django user authentication User object, for limiting to certain users.
from django.contrib.auth.models import User
from django.db.models.query import QuerySet

# import from AJAX selects, for looking up articles.
from ajax_select.fields import AutoCompleteSelectField
from ajax_select import make_ajax_field

# python_utilities - logging
from python_utilities.logging.logging_helper import LoggingHelper

# import stuff from sourcenet
#from mysite.sourcenet.export.network_output import NetworkOutput
from sourcenet.export.csv_article_output import CsvArticleOutput
from sourcenet.export.network_output import NetworkOutput
#from sourcenet.export.network_data_output import NetworkDataOutput
from sourcenet.models import Article
from sourcenet.models import Article_Data
from sourcenet.models import Article_Subject
from sourcenet.models import Newspaper
from sourcenet.models import Topic

class Article_DataLookupForm( forms.Form ):

    '''
    create a form to let a user lookup an article to view its Article_Data.
    '''

    # Article_Data ID
    article_data_id = forms.IntegerField( required = True, label = "Article Data ID" )
    # article_id = AutoCompleteSelectField( 'article', required = True, help_text = None, plugin_options = { 'autoFocus': True, 'minLength': 1 } )

#-- END ArticleLookupForm --#


class Article_DataSelectForm( forms.Form ):

    '''
    create a form to let a user select from Article_Data related to an article
       passed in to the form's __init__() method.
    '''

    def __init__( self, *args, **kwargs ):
    
        # declare variables
        article_IN = None
        article_data_qs = None
        article_data_count = -1
        article_data_choice_list = []
        article_data_instance = None
        ad_id = -1
        ad_coder = None
        ad_coder_type = ""
        ad_display_string = ""
        
        # retrieve article passed in.
        article_id_IN = kwargs.pop( 'article_id' )
        
        # call parent __init__() method.
        super( Article_DataSelectForm, self ).__init__(*args, **kwargs)
        
        # got an article?
        if ( ( article_id_IN is not None ) and ( article_id_IN > 0 ) ):
        
            # got any Article_Data instances?
            article_data_qs = Article_Data.objects.filter( article_id = article_id_IN )
            article_data_count = article_data_qs.count()
            
            if ( article_data_count > 0 ):
            
                # yes.  Loop, building a list of 2-tuples for each option,
                #   ( <actual_value>, <display_string> ).
                for article_data_instance in article_data_qs:
                
                    # get ID, coder, and coder type
                    ad_id = article_data_instance.id
                    ad_coder = article_data_instance.coder
                    ad_coder_type = article_data_instance.coder_type
            
                    # create display string
                    ad_display_string = str( ad_id ) + " - " + str( ad_coder ) + " ( " + str( ad_coder_type ) + " )"
                    
                    # add tuple to list
                    article_data_choice_list.append( ( ad_id, ad_display_string ) )
                    
                #-- END loop over choices. --#
        
                # add a form field to allow user to select Article_Data
                #    instances to display.
                self.fields[ 'article_data_id_select' ] = forms.MultipleChoiceField( required = False, choices = article_data_choice_list )
                
            #-- END - check to see how many Article_Data --#
            
        #-- END - check to see if article present. --#
    
    #-- END overridden/extended function __init__() --#

#-- END ArticleLookupForm --#


class ArticleCodingArticleFilterForm( forms.Form ):
    
    # constants-ish
    IAMEMPTY = "IAMEMPTY"
    
    '''
    create a form to let a user specify the criteria used to limit the articles
       that are used to create output.
    '''
    
    # what fields do I want?

    # start date
    start_date = forms.DateField( required = False, label = "Start Date (YYYY-MM-DD)" )

    # end date
    end_date = forms.DateField( required = False, label = "End Date (YYYY-MM-DD)" )

    # date range - text date range field that can parse out date ranges -
    #    double-pipe delimited, " to " between dates that bound a range, could
    #    add more later.
    # Ex.: "YYY1-M1-D1 to YYY2-M2-D2||YYY3-M3-D3 to YYY4-M4-D4", etc.
    date_range = forms.CharField( required = False, label = "* Fancy date range" )

    # publication
    publications = forms.ModelMultipleChoiceField( required = False, queryset = Newspaper.objects.all() )

    # list of unique identifiers to limit to.
    tags_list = forms.CharField( required = False, label = "Article Tag List (comma-delimited)" )
    
    # list of unique identifiers to limit to.
    unique_identifiers = forms.CharField( required = False, label = "Unique Identifier List (comma-delimited)" )
    
    # list of unique identifiers to limit to.
    article_id_list = forms.CharField( required = False, label = "Article ID IN List (comma-delimited)" )

    # list of unique identifiers to limit to.
    section_list = forms.CharField( required = False, label = "String Section Name IN List (comma-delimited)" )
    
    #--------------------------------------------------------------------------#
    # methods
    #--------------------------------------------------------------------------#
    
    
    def am_i_empty( self, *args, **kwargs ):
        
        '''
        Goes through the fields in the form and checks to see if any has been
            populated.  If not, returns True (it is empty!).  If there is a
            value in any of them, returns False (not empty).
        '''
        
        # return reference
        is_empty_OUT = True
        
        # declare variables
        me = "am_i_empty"
        my_logger_name = "sourcenet.forms.ArticleCodingArticleFilterForm"
        debug_message = ""
        my_cleaned_data = None
        input_counter = -1
        current_key = None
        current_value = None
        
        # get cleaned data.
        my_cleaned_data = self.cleaned_data
        
        # loop over keys
        input_counter = 0
        for current_key in six.iterkeys( my_cleaned_data ):
        
            # increment counter
            input_counter += 1

            # get value.
            current_value = my_cleaned_data.get( current_key, self.IAMEMPTY )
            
            debug_message = "input " + str( input_counter ) + ": key = " + str( current_key ) + "; value = \"" + str( current_value ) + "\" ( class = \"" + str( current_value.__class__ ) + "\" )"
            LoggingHelper.output_debug( debug_message, method_IN = me, logger_name_IN = my_logger_name )
            
            # empty?
            if ( current_value is not None ):
                
                # got a QuerySet?
                if ( isinstance( current_value, QuerySet ) == True ):
                    
                    # yes.  anything in it?
                    if ( current_value.count() > 0 ):
                    
                        is_empty_OUT = False
                        
                        debug_message = "QuerySet in key \"" + str( current_key ) + "\" IS NOT empty."
                        LoggingHelper.output_debug( debug_message, method_IN = me, indent_with_IN = "====> ", logger_name_IN = my_logger_name )
                
                    else:
                    
                        debug_message = "QuerySet in key \"" + str( current_key ) + "\" is EMPTY."
                        LoggingHelper.output_debug( debug_message, method_IN = me, indent_with_IN = "====> ", logger_name_IN = my_logger_name )
                    
                    #-- END check to see if anything in list. --#

                elif ( isinstance( current_value, list ) == True ):
                    
                    # yes.  Is there anything in list?
                    if ( len( current_value ) > 0 ):
                            
                        is_empty_OUT = False
                            
                        debug_message = "LIST in key \"" + str( current_key ) + "\" IS NOT empty."
                        LoggingHelper.output_debug( debug_message, method_IN = me, indent_with_IN = "====> ", logger_name_IN = my_logger_name )
    
                    else:
                            
                        debug_message = "LIST in key \"" + str( current_key ) + "\" is EMPTY."
                        LoggingHelper.output_debug( debug_message, method_IN = me, indent_with_IN = "====> ", logger_name_IN = my_logger_name )
                            
                    #-- END check to see if anything in list. --#
                        
                else:
                    
                    # not list - probably a string.
                    if ( ( current_value != "" ) and ( current_value != self.IAMEMPTY ) ):
                        
                        # not an empty string.
                        is_empty_OUT = False
                        
                        debug_message = "STRING in key \"" + str( current_key ) + "\" IS NOT empty."
                        LoggingHelper.output_debug( debug_message, method_IN = me, indent_with_IN = "====> ", logger_name_IN = my_logger_name )

                    else:
                        
                        debug_message = "STRING in key \"" + str( current_key ) + "\" is EMPTY."
                        LoggingHelper.output_debug( debug_message, method_IN = me, indent_with_IN = "====> ", logger_name_IN = my_logger_name )
                        
                    #-- END check to see if empty string, or set to self.IAMEMPTY --#
                    
                #-- END check to see if list. --#
            
            else:
            
                # empty.
                debug_message = "key \"" + str( current_key ) + "\" is None, and so EMPTY."
                LoggingHelper.output_debug( debug_message, method_IN = me, indent_with_IN = "====> ", logger_name_IN = my_logger_name )
            
            #-- END check to see if empty. --#

        #-- END loop over keys in data dictionary --#

        return is_empty_OUT
        
    #-- END method am_i_empty() --#

    
#-- END ArticleCodingArticleFilterForm ----------------------------------------#


class ArticleCodingForm( forms.ModelForm ):

    '''
    Create a form to let a user look up the source.
    '''

    class Meta:
        model = Article_Subject
        exclude = [ 'article_data', 'original_person', 'match_confidence_level', 'match_status', 'capture_method', 'create_date', 'last_modified', 'source_type', 'subject_type', 'name', 'verbatim_name', 'lookup_name', 'title', 'more_title', 'organization', 'document', 'topics', 'source_contact_type', 'source_capacity', 'localness', 'notes', 'organization_string', 'more_organization' ]

    # AJAX lookup for person.
    person  = make_ajax_field( Article_Subject, 'person', 'coding_person', help_text = "" )

#-- END ArticleCodingForm --#


class ArticleCodingListForm( forms.Form ):

    '''
    form to hold lookup criteria for articles that need to be coded.  To start,
        just includes list of tags.
    '''

    # list of unique tags to limit to.
    tags_in_list = forms.CharField( required = True, label = "Article Tag List (comma-delimited)" )

#-- END ArticleLookupForm --#


class ArticleCodingSubmitForm( forms.Form ):

    '''
    form to hold coding details for a given article.
    '''

    # PersonStore JSON
    data_store_json = forms.CharField( required = False, widget = forms.HiddenInput() )
    article_data_id = forms.IntegerField( required = False, widget = forms.HiddenInput() )

#-- END ArticleLookupForm --#


class ArticleLookupForm( forms.Form ):

    '''
    create a form to let a user lookup an article to view its contents.
    '''

    # Article ID
    article_id = forms.IntegerField( required = True, label = "Article ID" )
    # article_id = AutoCompleteSelectField( 'article', required = True, help_text = None, plugin_options = { 'autoFocus': True, 'minLength': 1 } )

#-- END ArticleLookupForm --#


class ArticleOutputTypeSelectForm( forms.Form ):

    '''
    form inputs to let a user specify the criteria used to limit the articles
       that are used to create output.
    '''

    # just contains the output type field for outputting network data.
    output_type = forms.ChoiceField( label = "Output Type", choices = CsvArticleOutput.OUTPUT_TYPE_CHOICES_LIST )

    # and a place to specify the text you want pre-pended to each column header.
    header_prefix = forms.CharField( required = False, label = "Column Header Prefix" )

#-- END ArticleOutputTypeSelectForm -------------------------------------------#


class ArticleSelectForm( forms.Form ):
    
    '''
    create a form to let a user specify the criteria used to limit the articles
       that are used to create output.
    '''
    
    # what fields do I want?

    # start date
    start_date = forms.DateField( required = False, label = "Start Date (YYYY-MM-DD)" )

    # end date
    end_date = forms.DateField( required = False, label = "End Date (YYYY-MM-DD)" )

    # date range - text date range field that can parse out date ranges -
    #    double-pipe delimited, " to " between dates that bound a range, could
    #    add more later.
    # Ex.: "YYY1-M1-D1 to YYY2-M2-D2||YYY3-M3-D3 to YYY4-M4-D4", etc.
    date_range = forms.CharField( required = False, label = "* Fancy date range" )

    # publication
    publications = forms.ModelMultipleChoiceField( required = False, queryset = Newspaper.objects.all() )

    # coders to include
    coders = forms.ModelMultipleChoiceField( required = False, queryset = User.objects.all() )

    # type of filtering on Article_Data coder_type identifiers we want to do.
    coder_type_filter_type = forms.ChoiceField( required = False,
        choices = NetworkOutput.CODER_TYPE_FILTER_TYPE_CHOICES_LIST,
        initial = NetworkOutput.CODER_TYPE_FILTER_TYPE_DEFAULT,
        label = "Article_Data coder_type Filter Type" )
    
    # list of Article_Data coder_type identifiers to limit to.
    coder_types_list = forms.CharField( required = False, label = "coder_type 'Value In' List (comma-delimited)" )
    
    # topics to include
    topics = forms.ModelMultipleChoiceField( required = False, queryset = Topic.objects.all() )

    # list of unique identifiers to limit to.
    tags_list = forms.CharField( required = False, label = "Article Tag List (comma-delimited)" )
    
    # list of unique identifiers to limit to.
    unique_identifiers = forms.CharField( required = False, label = "Unique Identifier List (comma-delimited)" )
    
    # allow duplicate articles?
    allow_duplicate_articles = forms.ChoiceField( required = False, choices = NetworkOutput.CHOICES_YES_OR_NO_LIST )
    
#-- END ArticleSelectForm -----------------------------------------------------#


class NetworkOutputForm( forms.Form ):

    '''
    NetworkOutputForm lets user specify details about the format and structure
       of the output that will capture network data - can specify file format,
       for example, whether to include render details/debug, and other details
       of the data that will result from examining Article_Data.
    '''

    # do we want to download result as file?
    network_download_as_file = forms.ChoiceField( required = False, label = "Download As File?", choices = NetworkOutput.CHOICES_YES_OR_NO_LIST )

    # include render details? 
    network_include_render_details = forms.ChoiceField( required = False, label = "Include Render Details?", choices = NetworkOutput.CHOICES_YES_OR_NO_LIST )

    # just contains the format you want the network data outputted as.
    output_type = forms.ChoiceField( label = "Data Format", choices = NetworkOutput.NETWORK_OUTPUT_TYPE_CHOICES_LIST, initial = NetworkOutput.NETWORK_OUTPUT_TYPE_DEFAULT )

    # data to output - either just network, just node attributes, both with attributes in columns, or both with attributes in rows.
    network_data_output_type = forms.ChoiceField( label = "Data Output Type", choices = NetworkOutput.NETWORK_DATA_OUTPUT_TYPE_CHOICES_LIST, initial = NetworkOutput.NETWORK_DATA_OUTPUT_TYPE_DEFAULT )

    # do we want a label at the top of the network file?
    network_label = forms.CharField( required = False, label = "Network Label" )

    # do we want to output row and column headers?
    network_include_headers = forms.ChoiceField( required = False, label = "Include headers?", choices = NetworkOutput.CHOICES_YES_OR_NO_LIST )

#-- END NetworkOutputForm -------------------------------------------#


# create a form to let a user specify the criteria used to limit the output form
class PersonSelectForm( forms.Form ):

    '''
    PersonSelectForm lets user specify additional filter criteria for selecting
       the people who will be included in a given network.  This should be used
       to broaden the set of people included in a given network so that networks
       over time will include the same set of people, even if some aren't
       present in a given time slice.
    '''

    # people to include?
    
    # first, have a field that lets the user choose the overall strategy for
    #    choosing the people who will make up the rows and columns of the
    #    resulting attribution network.  Three choices:
    # - all - just gets all the people in the database.
    # - articles - limits to people found in selected articles.
    # - custom - pulls in people based on the filter criteria below.
    person_query_type = forms.ChoiceField( required = False, choices = NetworkOutput.PERSON_QUERY_TYPE_CHOICES_LIST, initial = NetworkOutput.PERSON_QUERY_TYPE_DEFAULT )

    # criteria for pulling in people, so we can include a broader set of people
    #    in a given network, so it can be compared to other networks with
    #    criteria that might make them more broad.  Across invocations, a list
    #    of the same sources will sort the same, so networks that include a set
    #    of people are comparable even if the network data is generated at
    #    different times.
    person_start_date = forms.DateField( required = False, label = "People from (YYYY-MM-DD)" )
    person_end_date = forms.DateField( required = False, label = "People to (YYYY-MM-DD)" )

    # date range - text date range field that can parse out date ranges -
    #    double-pipe delimited, " to " between dates that bound a range, could
    #    add more later.
    # Ex.: "YYY1-M1-D1 to YYY2-M2-D2||YYY3-M3-D3 to YYY4-M4-D4", etc.
    person_date_range = forms.CharField( required = False, label = "* Fancy person date range" )

    person_publications = forms.ModelMultipleChoiceField( required = False, queryset = Newspaper.objects.all() )
    person_coders = forms.ModelMultipleChoiceField( required = False, queryset = User.objects.all() )

    # filtering on Article_Data coder_type identifiers...  filter type:
    person_coder_type_filter_type = forms.ChoiceField( required = False,
        choices = NetworkOutput.CODER_TYPE_FILTER_TYPE_CHOICES_LIST,
        initial = NetworkOutput.CODER_TYPE_FILTER_TYPE_DEFAULT,
        label = "Article_Data coder_type Filter Type" )
        
    # and values on which to filter.
    person_coder_types_list = forms.CharField( required = False, label = "coder_type 'Value In' List (comma-delimited)" )

    person_topics = forms.ModelMultipleChoiceField( required = False, queryset = Topic.objects.all() )
    person_tag_list = forms.CharField( required = False, label = "Article Tag List (comma-delimited)" )
    person_unique_identifiers = forms.CharField( required = False, label = "Unique Identifier List (comma-delimited)" )

    # allow duplicate articles?
    person_allow_duplicate_articles = forms.ChoiceField( required = False, choices = NetworkOutput.CHOICES_YES_OR_NO_LIST )

#-- end Form model PersonSelectForm -------------------------------------------


class ProcessSelectedArticlesForm( forms.Form ):
    
    '''
    allows user to specify list of tags they would like to be applied to
        some taggable entity.
    '''
    
    # action choices
    ACTION_CHOICES = (
        ( "match_summary", "Match Summary" ),
        ( "view_matches", "View Matches" ),
        ( "apply_tags", "Apply Tags" ),
    )
    action = forms.ChoiceField( required = True, choices = ACTION_CHOICES )

    # apply_tags_list (comma-delimited)
    apply_tags_list = forms.CharField( required = False, label = "If 'Apply Tags', list of tags to apply (comma-delimited)" )
    
#-- END Form class ProcessSelectedArticlesForm --#
    

class RelationSelectForm( forms.Form ):
    
    '''
    RelationSelectForm contains form inputs that allow one to specify what types
       of relations you want included in a network.  To start, just includes the
       source contact type.
    ''' 

    # source contact types

    # to have them all selected, need to make a list of the values in choices
    #    to place in "initial".
    initial_selected_list = []
    for selected_item in Article_Subject.SOURCE_CONTACT_TYPE_CHOICES:
    
        initial_selected_list.append( selected_item[ 0 ] )
        
    #-- END loop to populate initial selected items list --#
        
    include_source_contact_types = forms.MultipleChoiceField( required = False,
        choices = Article_Subject.SOURCE_CONTACT_TYPE_CHOICES,
        widget = forms.widgets.CheckboxSelectMultiple,
        initial = ( initial_selected_list ),
        label = "relations - Include source contact types" )
    
    # include and exclude source capacities
    include_capacities = forms.MultipleChoiceField( required = False,
        choices = Article_Subject.SOURCE_CAPACITY_CHOICES,
        label = "relations - Include source capacities" )

    exclude_capacities = forms.MultipleChoiceField( required = False,
        choices = Article_Subject.SOURCE_CAPACITY_CHOICES,
        label = "relations - Exclude source capacities" )

#-- END RelationSelectForm -----------------------------------------------------#
