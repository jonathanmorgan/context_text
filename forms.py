'''
Copyright 2010-2013 Jonathan Morgan

This file is part of http://github.com/jonathanmorgan/sourcenet.

sourcenet is free software: you can redistribute it and/or modify it under the terms of the GNU Lesser General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.

sourcenet is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.

You should have received a copy of the GNU Lesser General Public License along with http://github.com/jonathanmorgan/sourcenet. If not, see http://www.gnu.org/licenses/.
'''

# import django form object.
from django import forms

# import django user authentication User object, for limiting to certain users.
from django.contrib.auth.models import User

# import stuff from sourcenet
#from mysite.sourcenet.export.network_output import NetworkOutput
from sourcenet.export.csv_article_output import CsvArticleOutput
from sourcenet.export.network_output import NetworkOutput
#from sourcenet.export.network_data_output import NetworkDataOutput
from sourcenet.models import Article_Source
from sourcenet.models import Newspaper
from sourcenet.models import Topic

# create a form to let a user specify the criteria used to limit the articles
#    that are used to create output.
class ArticleSelectForm( forms.Form ):
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

    # topics to include
    topics = forms.ModelMultipleChoiceField( required = False, queryset = Topic.objects.all() )

    # list of unique identifiers to limit to.
    unique_identifiers = forms.CharField( required = False, label = "Unique Identifier List (comma-delimited)" )

    # allow duplicate articles?
    allow_duplicate_articles = forms.ChoiceField( required = False, choices = NetworkOutput.CHOICES_YES_OR_NO_LIST )
    
#-- END ArticleSelectForm -----------------------------------------------------#


# create a form to let a user specify the criteria used to limit the articles
#    that are used to create output.
class ArticleOutputTypeSelectForm( forms.Form ):

    # just contains the output type field for outputting network data.
    output_type = forms.ChoiceField( label = "Output Type", choices = CsvArticleOutput.OUTPUT_TYPE_CHOICES_LIST )

    # and a place to specify the text you want pre-pended to each column header.
    header_prefix = forms.CharField( required = False, label = "Column Header Prefix" )

#-- END ArticleOutputTypeSelectForm -------------------------------------------#


# create a form to let a user specify the criteria used to limit the output form
class PersonSelectForm( forms.Form ):
    # reporters to include?

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
    person_topics = forms.ModelMultipleChoiceField( required = False, queryset = Topic.objects.all() )
    person_unique_identifiers = forms.CharField( required = False, label = "Unique Identifier List (comma-delimited)" )

    # allow duplicate articles?
    person_allow_duplicate_articles = forms.ChoiceField( required = False, choices = NetworkOutput.CHOICES_YES_OR_NO_LIST )

#-- end Form model PersonSelectForm -------------------------------------------


# create a form to let a user specify the criteria used to limit the articles
#    that are used to create output.
class NetworkOutputForm( forms.Form ):

    # just contains the output type field for outputting network data.
    output_type = forms.ChoiceField( label = "Output Type", choices = NetworkOutput.NETWORK_OUTPUT_TYPE_CHOICES_LIST )

    # do we want a label at the top of the network file?
    network_label = forms.CharField( required = False, label = "Network Label" )

    # do we want to output row and column headers?
    network_include_headers = forms.ChoiceField( required = False, label = "Include headers", choices = NetworkOutput.CHOICES_YES_OR_NO_LIST )

    # include and exclude source capacities
    include_capacities = forms.MultipleChoiceField( required = False, choices = Article_Source.SOURCE_CAPACITY_CHOICES )
    exclude_capacities = forms.MultipleChoiceField( required = False, choices = Article_Source.SOURCE_CAPACITY_CHOICES )

#-- END ArticleOutputTypeSelectForm -------------------------------------------#