'''
Copyright 2010-2015 Jonathan Morgan

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

'''

# import django form object.
from django import forms

# import django user authentication User object, for limiting to certain users.
from django.contrib.auth.models import User

# import from AJAX selects, for looking up articles.
from ajax_select.fields import AutoCompleteSelectField
from ajax_select import make_ajax_field

# import stuff from sourcenet
#from mysite.sourcenet.export.network_output import NetworkOutput
from sourcenet.export.csv_article_output import CsvArticleOutput
from sourcenet.export.network_output import NetworkOutput
#from sourcenet.export.network_data_output import NetworkDataOutput
from sourcenet.models import Article
from sourcenet.models import Article_Source
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

    # list of unique identifiers to limit to.
    coder_types_list = forms.CharField( required = False, label = "Coder Type List (comma-delimited)" )
    
    # topics to include
    topics = forms.ModelMultipleChoiceField( required = False, queryset = Topic.objects.all() )

    # list of unique identifiers to limit to.
    tags_list = forms.CharField( required = False, label = "Article Tag List (comma-delimited)" )
    
    # list of unique identifiers to limit to.
    unique_identifiers = forms.CharField( required = False, label = "Unique Identifier List (comma-delimited)" )
    
    # allow duplicate articles?
    allow_duplicate_articles = forms.ChoiceField( required = False, choices = NetworkOutput.CHOICES_YES_OR_NO_LIST )
    
#-- END ArticleSelectForm -----------------------------------------------------#


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
    person_coder_types_list = forms.CharField( required = False, label = "Coder Type List (comma-delimited)" )
    person_topics = forms.ModelMultipleChoiceField( required = False, queryset = Topic.objects.all() )
    person_tag_list = forms.CharField( required = False, label = "Article Tag List (comma-delimited)" )
    person_unique_identifiers = forms.CharField( required = False, label = "Unique Identifier List (comma-delimited)" )

    # allow duplicate articles?
    person_allow_duplicate_articles = forms.ChoiceField( required = False, choices = NetworkOutput.CHOICES_YES_OR_NO_LIST )

#-- end Form model PersonSelectForm -------------------------------------------


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
    for selected_item in Article_Source.SOURCE_CONTACT_TYPE_CHOICES:
    
        initial_selected_list.append( selected_item[ 0 ] )
        
    #-- END loop to populate initial selected items list --#
        
    include_source_contact_types = forms.MultipleChoiceField( required = False,
        choices = Article_Source.SOURCE_CONTACT_TYPE_CHOICES,
        widget = forms.widgets.CheckboxSelectMultiple,
        initial = ( initial_selected_list ),
        label = "relations - Include source contact types" )
    
    # include and exclude source capacities
    include_capacities = forms.MultipleChoiceField( required = False,
        choices = Article_Source.SOURCE_CAPACITY_CHOICES,
        label = "relations - Include source capacities" )

    exclude_capacities = forms.MultipleChoiceField( required = False,
        choices = Article_Source.SOURCE_CAPACITY_CHOICES,
        label = "relations - Exclude source capacities" )

#-- END RelationSelectForm -----------------------------------------------------#
