from __future__ import unicode_literals

'''
Copyright 2010-2016 Jonathan Morgan

This file is part of http://github.com/jonathanmorgan/sourcenet.

sourcenet is free software: you can redistribute it and/or modify it under the terms of the GNU Lesser General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.

sourcenet is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.

You should have received a copy of the GNU Lesser General Public License along with http://github.com/jonathanmorgan/sourcenet. If not, see http://www.gnu.org/licenses/.

Configuration properties for it are stored in django's admins, in the
   django_config application.  The properties for the article_code view are stored in Application
   "sourcenet-UI-article-code":
   - include_fix_person_name - boolean flag, if true outputs additional field to correct name text from article.
'''

#===============================================================================
# ! imports (in alphabetical order by package, then by name)
#===============================================================================

# import Python libraries for CSV output
#import csv
import datetime
import json
#from StringIO import StringIO
#import pickle
import sys

# six
import six

# HTML parsing
from bs4 import BeautifulSoup

# nameparser import
# http://pypi.python.org/pypi/nameparser
from nameparser import HumanName

# import django authentication code.
from django.contrib import auth
from django.contrib.auth.decorators import login_required
# include the django conf settings
#from django.conf import settings

# django core imports
from django.core.urlresolvers import reverse

# Import objects from the django.http library.
#from django.http import Http404
from django.http import HttpResponse
from django.http import HttpResponseRedirect

# django.shortcuts imports - remder() method
#from django.shortcuts import get_object_or_404
from django.shortcuts import render

# import django template code
#from django.template import Context
#from django.template import loader

# import django code for csrf security stuff.
from django.template.context_processors import csrf

# django config, for pulling in any configuration from database.

# import basic django configuration application.
from django_config.models import Config_Property

'''   
Example of getting properties from django_config:

# get settings from django_config.
email_smtp_server_host = Config_Property.get_property_value( Issue.CONFIG_APPLICATION, Issue.CONFIG_PROP_SMTP_HOST )
email_smtp_server_port = Config_Property.get_property_int_value( Issue.CONFIG_APPLICATION, Issue.CONFIG_PROP_SMTP_PORT, -1 )
email_smtp_server_username = Config_Property.get_property_value( Issue.CONFIG_APPLICATION, Issue.CONFIG_PROP_SMTP_USERNAME, "" )
email_smtp_server_password = Config_Property.get_property_value( Issue.CONFIG_APPLICATION, Issue.CONFIG_PROP_SMTP_PASSWORD, "" )
use_SSL = Config_Property.get_property_boolean_value( Issue.CONFIG_APPLICATION, Issue.CONFIG_PROP_SMTP_USE_SSL, False )
email_from_address = Config_Property.get_property_value( Issue.CONFIG_APPLICATION, Issue.CONFIG_PROP_FROM_EMAIL )

'''


# python_utilities
from python_utilities.dictionaries.dict_helper import DictHelper
from python_utilities.django_utils.django_view_helper import DjangoViewHelper
from python_utilities.exceptions.exception_helper import ExceptionHelper
from python_utilities.json.json_helper import JSONHelper
from python_utilities.logging.logging_helper import LoggingHelper
from python_utilities.strings.string_helper import StringHelper

# sourcenet
from sourcenet.shared.person_details import PersonDetails
from sourcenet.shared.sourcenet_base import SourcenetBase

# Import Form classes
from sourcenet.forms import Article_DataSelectForm
from sourcenet.forms import ArticleCodingArticleFilterForm
from sourcenet.forms import ArticleCodingForm
from sourcenet.forms import ArticleCodingListForm
from sourcenet.forms import ArticleCodingSubmitForm
from sourcenet.forms import ArticleLookupForm
from sourcenet.forms import ArticleOutputTypeSelectForm
from sourcenet.forms import ArticleSelectForm
from sourcenet.forms import Person_ProcessSelectedForm
from sourcenet.forms import PersonLookupTypeForm
from sourcenet.forms import PersonLookupByNameForm
from sourcenet.forms import PersonSelectForm
from sourcenet.forms import ProcessSelectedArticlesForm
from sourcenet.forms import NetworkOutputForm
from sourcenet.forms import RelationSelectForm

# import class that actually processes requests for outputting networks.
from sourcenet.export.network_output import NetworkOutput

# Import the classes for our SourceNet application
from sourcenet.models import Article
#from sourcenet.models import Article_Author
from sourcenet.models import Article_Data
#from sourcenet.models import Article_Subject
from sourcenet.models import Person
#from sourcenet.models import Topic

# import class that actually processes requests for outputting networks.
from sourcenet.article_coding.manual_coding.manual_article_coder import ManualArticleCoder


#================================================================================
# ! ==> Shared variables and functions
#================================================================================

# configuration properties
# article_code view
CONFIG_APPLICATION_ARTICLE_CODE = "sourcenet-UI-article-code"
    
# article_code config property names.
CONFIG_PROP_DO_OUTPUT_TABLE_HTML = "do_output_table_html"
CONFIG_PROP_INCLUDE_FIX_PERSON_NAME = "include_fix_person_name"
CONFIG_PROP_INCLUDE_TITLE_FIELD = "include_title_field"
CONFIG_PROP_INCLUDE_ORGANIZATION_FIELD = "include_organization_field"
CONFIG_PROP_INCLUDE_FIND_IN_ARTICLE_TEXT = "include_find_in_article_text"

# Form input names
INPUT_NAME_ARTICLE_ID = "article_id"
INPUT_NAME_SOURCE = "source"
INPUT_NAME_TAGS_IN_LIST = "tags_in_list"

NO_GRAF = "no_graf"

def create_graf_to_subject_map( article_data_qs_IN ):
    
    '''
    Accepts Article_Data QuerySet.  Loops over Article_Data instances, then over
        Article_Subjects.  Creates a Dictionary that maps paragraph location of
        first mention of full name to list of subjects found in that paragraph.
        Returns dictionary.
    '''
    
    # return reference
    map_OUT = {}
    
    # declare variables
    me = "create_graf_to_subject_map"
    article_data_qs = None
    article_data_instance = None
    article_subject_qs = None
    article_subject = None
    subject_name = ""
    subject_mention_qs = None
    subject_mention = None
    graf_number = -1
    graf_subject_list = None
    
    # create place in map for people who are missing paragraph.
    map_OUT[ NO_GRAF ] = []
    
    # got a QuerySet?
    article_data_qs = article_data_qs_IN
    if ( ( article_data_qs is not None ) and ( article_data_qs.count() > 0 ) ):
                    
        # make list of subjects broken out by paragraph number.
        for article_data_instance in article_data_qs:
        
            # retrieve all subjects
            article_subject_qs = article_data_instance.article_subject_set.all()
            
            # loop over subjects.
            for article_subject in article_subject_qs:
            
                # get name
                subject_name = article_subject.name
                
                # look for mentions of that name
                subject_mention_qs = article_subject.article_subject_mention_set.all()
                #subject_mention_qs = subject_mention_qs.filter( value__iexact = subject_name )
                subject_mention_qs = subject_mention_qs.order_by( "paragraph_number" )
                
                # got any?
                if ( subject_mention_qs.count() > 0 ):
                
                    # yes - get the first.
                    subject_mention = subject_mention_qs[ 0 ]
                    
                    # get paragraph number
                    graf_number = subject_mention.paragraph_number
                    
                    # got valid number?
                    if ( ( graf_number is not None ) and ( graf_number != "" ) and ( graf_number > 0 ) ):
                    
                        # yes - add to output map - graf number already in map?
                        if ( graf_number in map_OUT ):
                        
                            # yup.  Get List of subjects.
                            graf_subject_list = map_OUT.get( graf_number, [] )
                        
                        else:
                        
                            # no subjects from that graf just yet.  Make empty
                            #    list...
                            graf_subject_list = []
                            
                            # ...and store it in map.
                            map_OUT[ graf_number ] = graf_subject_list
                        
                        #-- END check to see if graf already in map --#
                        
                        # store article_subjet in list.
                        graf_subject_list.append( article_subject )
                    
                    else:
                    
                        # invalid paragraph number.  Add to "no_graf".
                        graf_subject_list = map_OUT.get( NO_GRAF, [] )
                        graf_subject_list.append( article_subject )
                    
                    #-- check to see if valid paragraph number --#
                
                else:
                
                    # no mentions recorded.  Add to "no_graf".
                    graf_subject_list = map_OUT.get( NO_GRAF, [] )
                    graf_subject_list.append( article_subject )
                
                #-- END check to see if any mentions of name. --#
            
            #-- END loop over Article_Subject instances --#
        
        #-- END loop over Article_Data instances --#
                    
    #-- END check to see if we have Article_Data. --#
    
    return map_OUT
    
#-- END function create_graf_to_subject_map() --#


def create_subject_table_html( subject_list_IN, include_header_row_IN = True ):

    '''
    Accepts list of Article_Subject instances and optional flag that tells
       whether we also want a header row.  Generates an HTML table with one row
       per subject with cells for coder info., subject info., and quote info.
       if quotation present.  Returns HTML string.
    '''

    # return reference
    html_OUT = ""
    
    # declare variables
    me = "create_subject_table_html"
    article_subject_instance = None
    article_data_instance = None
    article_data_coder = None
    article_data_coder_id = -1
    article_data_coder_username = ""
    article_data_coder_type = ""
    subject_name = ""
    subject_verbatim_name = ""
    subject_lookup_name = ""
    subject_title = ""
    subject_organization = ""
    quote_qs = None
    quote = None
    quote_value = ""
    quote_paragraph_number = -1
    
    # got a list?
    if ( ( subject_list_IN is not None ) and ( len( subject_list_IN ) > 0 ) ):

        # open <table>    
        html_OUT += "<table class=\"gridtable\">"

        # do we want a header?
        if ( include_header_row_IN == True ):
        
            # yes
            html_OUT += "<tr><th>coder</th><th>subject</th><th>quotation</th></tr>"
        
        #-- END check to see if we want a header. --#
    
        # got at least one - loop.
        for article_subject_instance in subject_list_IN:
    
            # render subject
            html_OUT += "<tr>"
    
            #------------------------------------------#
            # get coder information...
            html_OUT += "<td>"
            article_data_instance = article_subject_instance.article_data
            article_data_coder = article_data_instance.coder
            article_data_coder_id = article_data_coder.id
            article_data_coder_username = article_data_coder.username
            html_OUT += StringHelper.object_to_unicode_string( article_data_coder_id ) + " - " + article_data_coder_username

            # got a coder type?
            article_data_coder_type = article_data_instance.coder_type
            if ( ( article_data_coder_type is not None ) and ( article_data_coder_type != "" ) ):
            
                # yes.  Output.
                html_OUT += " (<em>" + article_data_coder_type + "</em>)"
            
            #-- END check to see if coder type. --#
            
            html_OUT += "</td>"
    
            #------------------------------------------#
            # and subject information
            html_OUT += "<td>"
            html_OUT += StringHelper.object_to_unicode_string( article_subject_instance )
    
            # got a name?
            subject_name = article_subject_instance.name
            if ( ( subject_name is not None ) and ( subject_name != "" ) ):
                html_OUT += "<br />==> name: " + subject_name
            #-- END check to see if name captured. --#
            
            # lookup name different from verbatim name?
            subject_verbatim_name = article_subject_instance.verbatim_name
            subject_lookup_name = article_subject_instance.lookup_name
            if ( ( subject_lookup_name is not None ) and ( subject_lookup_name != "" ) and ( subject_lookup_name != subject_verbatim_name ) ):
                html_OUT += "<br />====> verbatim name: " + subject_verbatim_name
                html_OUT += "<br />====> lookup name: " + subject_lookup_name
            #-- END check to see if name captured. --#
            
            subject_title = article_subject_instance.title
            if ( ( subject_title is not None ) and ( subject_title != "" ) ):
                html_OUT += "<br />==> title: " + subject_title
            #-- END check to see if name captured. --#
            
            # got an organization string?
            subject_organization = article_subject_instance.organization_string
            if ( ( subject_organization is not None ) and ( subject_organization != "" ) ):
                html_OUT += "<br />==> organization: " + subject_organization
            #-- END check to see if name captured. --#
            
            html_OUT += "</td>"                                    
        
            #------------------------------------------#
            # and quote information
            html_OUT += "<td>"
            
            # get first quote.
            quote_qs = article_subject_instance.article_subject_quotation_set.all()
            quote_qs = quote_qs.order_by( "paragraph_number" )
            
            # got one?
            if ( quote_qs.count() > 0 ):
                
                # yes - get value and output.
                quote = quote_qs[ 0 ]
                quote_value = quote.value
                quote_paragraph_number = quote.paragraph_number
                
                html_OUT += quote_value + " ( graf: " + StringHelper.object_to_unicode_string( quote_paragraph_number ) + " )"
    
            else:
                
                # no - output "None".
                html_OUT += "None."
                
            #-- END check to see if quote --#
    
            html_OUT += "</td>"

            html_OUT += "</tr>"
    
        #-- END loop over subjects. --#

        # close table.
        html_OUT += "</table>"
        
    #-- END check to see if we have a list --#

    return html_OUT

#-- END function create_subject_table() --#


def get_request_data( request_IN ):
    
    '''
    Accepts django request.  Based on method, grabs the container for incoming
        parameters and returns it:
        - for method "POST", returns request_IN.POST
        - for method "GET", returns request_IN.GET
    '''
    
    # return reference
    request_data_OUT = None

    # call method in DjangoViewHelper
    request_data_OUT = DjangoViewHelper.get_request_data( request_IN )
    
    return request_data_OUT
    
#-- END function get_request_data() --#



'''
debugging code, shared across all models.
'''

DEBUG = False
LOGGER_NAME = "sourcenet.views"

def output_debug( message_IN, method_IN = "", indent_with_IN = "", logger_name_IN = "" ):
    
    '''
    Accepts message string.  If debug is on, logs it.  If not,
       does nothing for now.
    '''
    
    # declare variables
    my_logger_name = ""
    
    # got a logger name?
    my_logger_name = LOGGER_NAME
    if ( ( logger_name_IN is not None ) and ( logger_name_IN != "" ) ):
    
        # use logger name passed in.
        my_logger_name = logger_name_IN
        
    #-- END check to see if logger name --#

    # call DjangoViewHelper method.
    DjangoViewHelper.output_debug( message_IN,
                                   method_IN = method_IN,
                                   indent_with_IN = indent_with_IN,
                                   logger_name_IN = my_logger_name,
                                   debug_flag_IN = DEBUG )

#-- END method output_debug() --#


#===============================================================================
# ! ==> view action methods (in alphabetical order)
#===============================================================================


#def detail( request_IN, poll_id_IN ):

    #return HttpResponse( "You're looking at poll %s." % poll_id_IN )

    # declare variables
#    poll_instance = None

    # shortcut for grabbing an instance, raising 404 error if not found.
    #try:
    #    poll_instance = Poll.objects.get( pk = poll_id_IN )
    #except Poll.DoesNotExist:
    #    raise Http404
#    poll_instance = get_object_or_404( Poll, pk = poll_id_IN )

#    return render( request_IN, 'polls/detail.html', { 'poll' : poll_instance } )

#-- end method detail() --#


#def index( request_IN ):

    # return reference
#    response_OUT = None

    # declare variables
#    param_dictionary = {}

    #return HttpResponse( "Hello, world.  You're at the poll index." )
#    latest_poll_list = Poll.objects.all().order_by('-pub_date')[:5]

    # set up the rendering dictionary
#    param_dictionary.update( {'latest_poll_list': latest_poll_list} )

    # this has a django.shortcuts method, render(), used below.
    #t = loader.get_template('polls/index.html')
    #c = Context({
    #    'latest_poll_list': latest_poll_list,
    #})
    #return HttpResponse(t.render(c))
    #response_OUT = render( request_IN, 'polls/index.html', {'latest_poll_list': latest_poll_list} )
#    response_OUT = render( request_IN, 'polls/index.html', param_dictionary )

#    return response_OUT

#-- end method index() --#


#def results( request_IN, poll_id_IN ):
    # return HttpResponse( "You're looking at the results of poll %s." % poll_id_IN )

    #return reference
#    response_OUT = None

    # declare variables
#    poll_instance = None

    # get poll instance
#    poll_instance = get_object_or_404( Poll, pk = poll_id_IN )

#    response_OUT = render( request_IN, 'polls/results.html', { 'poll': poll_instance } )

#    return response_OUT

#-- end view method results() --#


@login_required
def article_code( request_IN ):

    '''
    View for coding a single article.  Form accepts article ID.  If article ID
        present, looks up coding for that article for current user.  If found,
        loads it, if not, initializes to empty.  Loads article, loads coding
        form, then if existing coding, pre-populates coding form.
    '''

    # return reference
    response_OUT = None

    # declare variables
    me = "article_code"
    logger_name = ""
    debug_message = ""
    
    # declare variables - config properties
    config_do_output_table_html = False
    config_include_fix_person_name = False
    config_include_title_field = False
    config_include_organization_field = False
    config_include_find_in_article_text = False
    
    # declare variables - exception handling
    exception_message = ""
    is_exception = False
    do_cleanup_post_exception = False
    
    # declare variables - processing request
    response_dictionary = {}
    default_template = ''
    article_lookup_form = None
    is_form_ready = False
    request_data = None
    source = None
    tags_in_list = None
    article_id = -1
    article_qs = None
    article_count = -1
    article_instance = None
    article_paragraph_list = None
    
    # declare variables - coding submission.
    data_store_json_string = ""
    current_user = None
    has_existing_article_data = False
    article_data_qs = None
    article_data_count = -1
    article_data_instance = None
    article_data_id = -1
    article_data_id_list = []
    is_ok_to_process_coding = True
    manual_article_coder = None
    result_article_data = None
    coding_status = ""
    new_data_store_json = None
    new_data_store_json_string = ""
    page_status_message = ""
    page_status_message_list = []
    
    # declare variables - interacting with article text
    article_content = ""
    article_content_bs = None
    p_tag_list = []
    p_tag_count = -1
    rendered_article_html = ""
    paragraph_index = -1
    paragraph_number = -1
    p_tag_bs = None
    p_tag_html = ""

    # declare variables - article coding
    person_lookup_form = None
    
    # declare variables - submit coding back to server
    coding_submit_form = None

    # set logger_name
    logger_name = "sourcenet.views." + me
    
    # ! load configuration
    config_do_output_table_html = Config_Property.get_property_boolean_value( CONFIG_APPLICATION_ARTICLE_CODE, CONFIG_PROP_DO_OUTPUT_TABLE_HTML, False )
    config_include_fix_person_name = Config_Property.get_property_boolean_value( CONFIG_APPLICATION_ARTICLE_CODE, CONFIG_PROP_INCLUDE_FIX_PERSON_NAME, False )
    config_include_title_field = Config_Property.get_property_boolean_value( CONFIG_APPLICATION_ARTICLE_CODE, CONFIG_PROP_INCLUDE_TITLE_FIELD, False )
    config_include_organization_field = Config_Property.get_property_boolean_value( CONFIG_APPLICATION_ARTICLE_CODE, CONFIG_PROP_INCLUDE_ORGANIZATION_FIELD, True )
    config_include_find_in_article_text = Config_Property.get_property_boolean_value( CONFIG_APPLICATION_ARTICLE_CODE, CONFIG_PROP_INCLUDE_FIND_IN_ARTICLE_TEXT, False )

    # initialize response dictionary
    response_dictionary = {}
    response_dictionary.update( csrf( request_IN ) )
    response_dictionary[ 'manual_article_coder' ] = None
    response_dictionary[ 'article_instance' ] = None
    response_dictionary[ 'article_text' ] = None
    response_dictionary[ 'base_simple_navigation' ] = True
    response_dictionary[ 'base_post_login_redirect' ] = reverse( article_code )
    # just passing reference to ManualArticleCoder now.
    # response_dictionary[ 'person_type_subject' ] = ManualArticleCoder.PERSON_TYPE_SUBJECT
    # response_dictionary[ 'person_type_source' ] = ManualArticleCoder.PERSON_TYPE_SOURCE
    # response_dictionary[ 'person_type_author' ] = ManualArticleCoder.PERSON_TYPE_AUTHOR
    response_dictionary[ 'existing_data_store_json' ] = ""
    response_dictionary[ 'page_status_message_list' ] = page_status_message_list
    
    # create article coder and place in response so we can access constants-ish.
    manual_article_coder = ManualArticleCoder()
    response_dictionary[ 'manual_article_coder' ] = manual_article_coder

    # set my default rendering template
    default_template = 'sourcenet/articles/article-code.html'

    # init coding status variables
    # start with it being OK to process coding.
    is_ok_to_process_coding = True
    
    # do we have input parameters?
    request_data = get_request_data( request_IN )
    if ( request_data is not None ):

        # get information needed from request, add to response dictionary.

        # ==> source (passed by article_code_list).
        source = request_data.get( INPUT_NAME_SOURCE, "" )
        response_dictionary[ INPUT_NAME_SOURCE ] = source
        
        # ==> tags_in_list (passed by article_code_list).
        tags_in_list = request_data.get( INPUT_NAME_TAGS_IN_LIST, [] )
        response_dictionary[ INPUT_NAME_TAGS_IN_LIST ] = tags_in_list

        # OK to process.
        is_form_ready = True
        
    #-- END check to see if we have request data. --#
    
    # set up form objects.

    # make instance of person_lookup_form.
    person_lookup_form = ArticleCodingForm()
    
    # make instance of article coding submission form.
    coding_submit_form = ArticleCodingSubmitForm( request_data )

    # make instance of ArticleLookupForm
    article_lookup_form = ArticleLookupForm( request_data )

    # store the article ID if passed in.
    article_id = request_data.get( INPUT_NAME_ARTICLE_ID, -1 )

    # check to see if ""
    if ( article_id == "" ):
    
        article_id = -1
        
    #-- END check to see if article_id = "" --#

    # retrieve QuerySet that contains that article.
    article_qs = Article.objects.filter( pk = article_id )

    # get count of articles
    article_count = article_qs.count()

    # should only be one.
    if ( article_count == 1 ):
    
        # get article instance
        article_instance = article_qs.get()

    #-- END check if single article. --#

    # get current user.
    current_user = request_IN.user

    # ! Article_Data

    # for now, not accepting an Article_Data ID from page, looking for
    #    Article_Data that matches current user and current article
    #    instead.
    #article_data_id = request_data.get( "article_data_id", -1 )

    # see if existing Article_Data for user and article
    article_data_qs = Article_Data.objects.filter( coder = current_user )
    article_data_qs = article_data_qs.filter( article = article_instance )
    
    # how many matches?
    article_data_count = article_data_qs.count()
    if ( article_data_count == 1 ):

        # found one.  Get ID so we can update it.
        article_data_instance = article_data_qs.get()
        article_data_id = article_data_instance.id
        has_existing_article_data = True

    else:

        # either 0 or > 1.  See if > 1.
        if ( article_data_count > 1 ):

            # error - don't want to allow multiple for now.
            is_ok_to_process_coding = False

            # output log message, output status message on screen,
            #    reload coding into page from JSON.
            page_status_message = "Multiple Article_Data instances found (IDs: "

            # loop to make list of IDs
            for article_data_instance in article_data_qs:

                # add ID to status message
                article_data_id_list.append( str( article_data_instance.id ) )

            #-- END loop over Article_Data instances --#
            
            # add Article_Data ids to message
            page_status_message += ", ".join( article_data_id_list )

            # and finish message
            page_status_message += ") for user " + str( current_user ) + " and article " + str( article_instance ) + ".  There should be only one.  Did not store coding."

            # log the message.
            output_debug( page_status_message, me, indent_with_IN = "====> ", logger_name_IN = logger_name )

            # place in status message variable.
            page_status_message_list.append( page_status_message )
            
            has_existing_article_data = True

        else:

            # not greater than 1, so 0 or negative (!).  OK to process.
            #is_ok_to_process_coding = True
            has_existing_article_data = False

        #-- END check to see if greater than 1. --#

    #-- END dealing with either 0 or > 1 Article_Data --#

    # form ready?
    if ( is_form_ready == True ):
    
        # ! process coding submission
        if ( coding_submit_form.is_valid() == True ):

            # it is valid - retrieve data_store_json and article_data_id
            data_store_json_string = request_data.get( "data_store_json", "" )

            # got any JSON?
            data_store_json_string = data_store_json_string.strip()
            if ( ( data_store_json_string is None ) or ( data_store_json_string == "" ) ):

                # no JSON - no need to process coding.
                is_ok_to_process_coding = False

            #-- END check to see if we have any JSON --#
                        
            # OK to process coding?
            if ( is_ok_to_process_coding == True ):

                # Wrap this all in a try-except, so we can return decent error
                #    messages.
                try:

                    # process JSON with instance of ManualArticleCoder
                    #manual_article_coder = ManualArticleCoder()
                    
                    # need to get call set up for new parameters.
                    article_data_instance = manual_article_coder.process_data_store_json( article_instance,
                                                                                          current_user,
                                                                                          data_store_json_string,
                                                                                          article_data_id,
                                                                                          request_IN,
                                                                                          response_dictionary )
    
                    # got anything back?
                    coding_status = ""
                    if ( article_data_instance is not None ):
    
                        # get status from article data instance
                        coding_status = article_data_instance.status_messages
    
                    #-- END check to see if we have an Article_Data instance --#
    
                    # got a status?
                    if ( ( coding_status is not None ) and ( coding_status != "" ) ):
    
                        # short circuit article lookup (use empty copy of form) if success.
                        if ( coding_status == ManualArticleCoder.STATUS_SUCCESS ):
    
                            # no longer emptying things out - load existing
                            #    coding, so you can edit.

                            # Add status message that just says that Coding was saved.
                            page_status_message_list.append( "Article data successfully saved!" )
    
                        elif ( coding_status != "" ):
    
                            # got an error status.  Log and output it.
                            page_status_message = "There was an error processing your coding: " + coding_status
    
                            # log it...
                            output_debug( page_status_message, me, indent_with_IN = "====> ", logger_name_IN = logger_name )
    
                            # ...and output it.
                            page_status_message_list.append( page_status_message )
    
                        #-- END check to see what status message is --#
    
                    #-- END check to see if status message returned at all --#
                    
                except Exception as e:
                
                    # set exception flag
                    is_exception = True
                
                    # Capture exception message.
                    my_exception_helper = ExceptionHelper()

                    # log exception, no email or anything.
                    exception_message = "Exception caught for user " + str( current_user.username ) + ", article " + str( article_id )
                    my_exception_helper.process_exception( e, exception_message )
                    
                    output_debug( exception_message, me, indent_with_IN = "======> ", logger_name_IN = logger_name )
                    
                    # and, create status message from Exception message.
                    page_status_message = "There was an unexpected exception caught while processing your coding: " + str( e )

                    # log it...
                    output_debug( page_status_message, me, indent_with_IN = "====> ", logger_name_IN = logger_name )

                    # ...and output it.
                    page_status_message_list.append( page_status_message )    

                #-- END try/except around article data processing. --#

            #-- END check to see if OK to process coding. --#
            
        #-- END check to see if coding form is valid. --#

        # !figure out if and which data store JSON we return

        # check to see if exception.
        if ( is_exception == True ):
        
            # yes, exception.  In "existing_data_store_json", override to pass
            #    back what was passed in.
            if ( ( data_store_json_string is not None ) and ( data_store_json_string != "" ) ):
            
                #output_debug( "\n\ndata_store_json_string : \n\n" + data_store_json_string, me )
                
                '''
                # got JSON that was passed in.  After escaping nested quotes,
                #    return it.
                new_data_store_json = json.loads( data_store_json_string )
                
                # escape string values
                new_data_store_json = JSONHelper.escape_all_string_json_values( new_data_store_json, do_double_escape_quotes_IN = True )
                
                # convert to string
                new_data_store_json_string = json.dumps( new_data_store_json )
                '''
                
                new_data_store_json_string = data_store_json_string.replace( "\\\"", "\\\\\\\"" )
                
                # output_debug( "\n\nnew_data_store_json_string : \n\n" + new_data_store_json_string, me )

                # store in response dictionary.
                response_dictionary[ 'existing_data_store_json' ] = new_data_store_json_string

            #-- END check to see if existing JSON. --#

            # got Article_Data that we created new?
            if ( ( has_existing_article_data == False ) and ( article_data_instance is not None ) ):
            
                # we created an Article_Data, then had an exception.  Delete?
                if ( do_cleanup_post_exception == True ):
                
                    # delete Article_Data and all child records.
                    article_data_instance.delete()
                    article_data_instance = None
                    
                #-- END check to see if we are to clean up after an exception. --#
                
            #-- END check to see if we have a new Article_Data instance --#

        else:
        
            # got article_data?
            if ( article_data_instance is not None ):
    
                # convert to JSON and store in response dictionary
                new_data_store_json = ManualArticleCoder.convert_article_data_to_data_store_json( article_data_instance )
                new_data_store_json_string = json.dumps( new_data_store_json )
                #output_debug( "\n\nnew_data_store_json_string : \n\n" + new_data_store_json_string, me )
                response_dictionary[ 'existing_data_store_json' ] = new_data_store_json_string
    
                # output a message that we've done this.
                page_status_message = "Loaded article " + str( article_instance.id ) + " coding for user " + str( current_user )
                page_status_message_list.append( page_status_message )
    
            #-- END check to see if we have an Article_Data instance --#
                
        #-- END check to see if exception --#
        

        # process article lookup?
        if ( article_lookup_form.is_valid() == True ):

            # retrieve article specified by the input parameter, then create
            #   HTML output of article plus Article_Text.
            
            # get article ID.
            # already populated above.
            #article_id = request_IN.POST.get( "article_id", -1 )

            # retrieve QuerySet that contains that article.
            article_qs = Article.objects.filter( pk = article_id )

            # get count of queryset return items
            if ( ( article_qs != None ) and ( article_qs != "" ) ):

                # get count of articles
                article_count = article_qs.count()
    
                # should only be one.
                if ( article_count == 1 ):
                
                    # get article instance
                    article_instance = article_qs.get()
                    
                    # retrieve article text.
                    article_text = article_instance.article_text_set.get()
                    
                    # get content
                    article_content = article_text.get_content()
                    
                    # parse with beautifulsoup
                    article_content_bs = BeautifulSoup( article_content, "html5lib" )
                    
                    # get paragraph tag list
                    p_tag_list = article_content_bs.find_all( 'p' )
                    p_tag_count = len( p_tag_list )
                    
                    # got p-tags?
                    if ( p_tag_count > 0 ):
                    
                        # yes.  create a table with two columns per row:
                        # - paragraph number
                        # - paragraph text
                        rendered_article_html = '''
                            <table class="gridtable">
                                <tr>
                                    <th>graf#</th>
                                    <th>text</th>
                                </tr>
                        '''
                    
                        # for each paragraph, grab that <p> and place it in a table
                        #    cell.
                        for paragraph_index in range( p_tag_count ):
                        
                            # paragraph number is index + 1
                            paragraph_number = paragraph_index + 1
                            
                            # get <p> tag with ID of paragraph_number
                            p_tag_bs = article_content_bs.find( id = str( paragraph_number ) )
                            
                            # render row
                            p_tag_html = p_tag_bs.prettify()
                            #p_tag_html = StringHelper.encode_string( p_tag_html, output_encoding_IN = StringHelper.ENCODING_UTF8 )
                            debug_message = "p_tag_html type = " + str( type( p_tag_html ) )
                            output_debug( debug_message, me, indent_with_IN = "====> ", logger_name_IN = logger_name )

                            # calling str() on any part of a string being
                            #    concatenated causes all parts of the string to
                            #    try to encode to default encoding ('ascii').
                            #    This breaks if there are non-ascii characters.
                            rendered_article_html += "\n        <tr><td>" + StringHelper.object_to_unicode_string( paragraph_number ) + "</td><td>" + p_tag_html + "</td></tr>"
                        
                        #-- END loop over <p> ids. --#
                        
                        rendered_article_html += "</table>"
                    
                    else:
                    
                        # no p-tags - just use article_text.
                        rendered_article_html = article_content
                        
                    #-- END check to see if paragraph tags. --#
                    
                    # seed response dictionary.
                    response_dictionary[ 'article_instance' ] = article_instance
                    response_dictionary[ 'article_text' ] = article_text
                    response_dictionary[ 'article_content' ] = rendered_article_html
                    response_dictionary[ 'article_lookup_form' ] = article_lookup_form
                    response_dictionary[ 'person_lookup_form' ] = person_lookup_form
                    response_dictionary[ 'coding_submit_form' ] = coding_submit_form
                    response_dictionary[ 'base_include_django_ajax_selects' ] = True
                    
                    # loaded from config
                    response_dictionary[ 'do_output_table_html' ] = config_do_output_table_html
                    response_dictionary[ 'include_fix_person_name' ] = config_include_fix_person_name
                    response_dictionary[ 'include_title_field' ] = config_include_title_field
                    response_dictionary[ 'include_organization_field' ] = config_include_organization_field
                    response_dictionary[ 'include_find_in_article_text' ] = config_include_find_in_article_text

                    # get paragraph list
                    #article_paragraph_list = article_text.get_paragraph_list()
                    
                elif ( article_count > 1 ):

                    # error - multiple articles found for ID. --#

                    # create error message.
                    page_status_message = "ERROR - lookup for article ID " + str( article_id ) + " returned " + str( article_count ) + " records.  Oh my..."
                    
                    # log it...
                    output_debug( page_status_message, me, indent_with_IN = "====> ", logger_name_IN = logger_name )

                    # ...and output it.
                    page_status_message_list.append( page_status_message )

                    # and pass on the form.
                    response_dictionary[ 'article_lookup_form' ] = article_lookup_form

                elif ( article_count == 0 ):

                    # error - multiple articles found for ID. --#

                    # create error message.
                    page_status_message = "No article found for article ID " + str( article_id ) + "."

                    # log it...
                    output_debug( page_status_message, me, indent_with_IN = "====> ", logger_name_IN = logger_name )

                    # ...and output it.
                    page_status_message_list.append( page_status_message )

                    # and pass on the form.
                    response_dictionary[ 'article_lookup_form' ] = article_lookup_form

                else:
                
                    # unknown error. --#

                    # create error message.
                    page_status_message = "Unknown error encountered looking up article ID " + str( article_id ) + "."

                    # log it...
                    output_debug( page_status_message, me, indent_with_IN = "====> ", logger_name_IN = logger_name )

                    # ...and output it.
                    page_status_message_list.append( page_status_message )

                    # and pass on the form.
                    response_dictionary[ 'article_lookup_form' ] = article_lookup_form
                    
                #-- END check to see if there is one or other than one. --#

            else:
            
                # ERROR - nothing returned from attempt to get queryset (would expect empty query set)

                    # create error message.
                    page_status_message = "ERROR - no QuerySet returned from call to filter().  This is odd."

                    # log it...
                    output_debug( page_status_message, me, indent_with_IN = "====> ", logger_name_IN = logger_name )

                    # ...and output it.
                    page_status_message_list.append( page_status_message )

                    # and pass on the form.
                    response_dictionary[ 'article_lookup_form' ] = article_lookup_form

            #-- END check to see if query set is None --#

        else:

            # not valid - render the form again
            response_dictionary[ 'article_lookup_form' ] = article_lookup_form

        #-- END check to see whether or not form is valid. --#

    else:
    
        # new request, make an empty instance of network output form.
        article_lookup_form = ArticleLookupForm()
        response_dictionary[ 'article_lookup_form' ] = article_lookup_form

    #-- END check to see if new request or POST --#
    
    # add on the "me" property.
    response_dictionary[ 'current_view' ] = me        

    # render response
    response_OUT = render( request_IN, default_template, response_dictionary )

    return response_OUT

#-- END view method article_code() --#


@login_required
def article_coding_list( request_IN ):

    '''
    This view allows a user to look up a set of articles (first by entering a
        tag to use to filter articles), and then see which have been coded.
        Regardless, for each article provides a link to code.  If coded, the
        link is details on the Article_Data record for that article.  If not, it
        is just a link to the coding page for that article.
    '''

    #return reference
    response_OUT = None

    # declare variables
    me = "article_coding_list"
    current_user = None
    response_dictionary = {}
    default_template = ''
    request_inputs = None
    article_coding_list_form = None
    tags_in_list = []
    is_form_ready = False
    article_qs = None
    article_counter = -1
    article_data_qs = None
    article_details_list = []
    article_details = {}
    article_instance = ""
    article_data = None
    article_status = ""
    
    # initialize response dictionary
    response_dictionary = {}
    response_dictionary.update( csrf( request_IN ) )
    response_dictionary[ 'base_simple_navigation' ] = True
    response_dictionary[ 'base_post_login_redirect' ] = reverse( article_coding_list )

    # set my default rendering template
    default_template = 'sourcenet/articles/article-code-list.html'
    
    # get current user
    current_user = request_IN.user

    # variables for building, populating person array that is used to control
    #    building of network data matrices.

    # do we have input parameters?
    request_inputs = get_request_data( request_IN )
    
    # got inputs?
    if ( request_inputs is not None ):
        
        # create ArticleCodingListForm
        article_coding_list_form = ArticleCodingListForm( request_inputs )

        # get information we need from request.
        tags_in_list = request_inputs.get( INPUT_NAME_TAGS_IN_LIST, [] )

        is_form_ready = True
    
    else:
    
        # no inputs - create empty form
        article_coding_list_form = ArticleCodingListForm()

        is_form_ready = False
    
    #-- END check to see if inputs. --#

    # store form in response
    response_dictionary[ 'article_coding_list_form' ] = article_coding_list_form

    # store tags in list value in response dictionary.
    response_dictionary[ 'tags_in_list' ] = tags_in_list
    
    # form ready?
    if ( is_form_ready == True ):

        if ( article_coding_list_form.is_valid() == True ):

            # retrieve articles specified by the input parameters, ordered by
            #     Article ID, then create HTML output of list of articles.  For
            #     each, output:
            #     - article string
            #     - link to code article.  If no existing coding, make it a
            #         generic link.  If existing coding, make the Article_Data
            #         string the link.
            
            # retrieve QuerySet that contains articles with requested tag(s).
            article_qs = Article.filter_articles( tags_in_list_IN = tags_in_list )
            article_qs = article_qs.order_by( "id" )

            # get count of queryset return items
            if ( ( article_qs != None ) and ( article_qs != "" ) ):

                # get count of articles
                article_count = article_qs.count()
    
                # got one or more?
                if ( article_count >= 1 ):
                
                    # yes - initialize list of article_details
                    article_details_list = []
                
                    # loop over articles
                    article_counter = 0
                    for article_instance in article_qs:
                    
                        # increment article_counter
                        article_counter += 1
                    
                        # new article_details
                        article_details = {}
                        
                        # store index and article
                        article_details[ "index" ] = article_counter
                        article_details[ "article_instance" ] = article_instance
                        
                        # see if there is an Article_Data for current user.
                        try:
                        
                            #look up Article_Data
                            article_data_qs = article_instance.article_data_set
                            article_data = article_data_qs.get( coder = current_user )
                            article_status = "coded"
                            
                        except Article_Data.MultipleObjectsReturned as amore:
                        
                            # multiple returned.
                            article_data = None
                            article_status = "multiple"

                        except Article_Data.DoesNotExist as adne:
                        
                            # None returned.
                            article_data = None
                            article_status = "new"

                        except Exception as e:
                        
                            # multiple returned.
                            article_data = None
                            article_status = "error" + str( e )
                            
                        #-- END attempt to get Article_Data for current user. --#
                        
                        # place article_data in article_details
                        article_details[ "article_data" ] = article_data
                        article_details[ "article_status" ] = article_status
                        
                        # add details to list.
                        article_details_list.append( article_details )

                    #-- END loop over articles --#
                    
                    # seed response dictionary.
                    response_dictionary[ 'article_details_list' ] = article_details_list
                    
                else:
                
                    # error - none or multiple articles found for ID. --#
                    print( "No article returned for ID passed in." )
                    response_dictionary[ 'output_string' ] = "ERROR - nothing in QuerySet returned from call to Article.filter_articles() ( tags_in_list_IN = " + str( tags_in_list ) + " )."
                    response_dictionary[ 'article_coding_list_form' ] = article_coding_list_form
                    
                #-- END check to see if there is one or other than one. --#

            else:
            
                # ERROR - nothing returned from attempt to get queryset (would expect empty query set)
                response_dictionary[ 'output_string' ] = "ERROR - no QuerySet returned from call to Article.filter_articles().  This is odd."
                
            
            #-- END check to see if query set is None --#

        else:

            # not valid - render the form again
            response_dictionary[ 'output_string' ] = "ArticleCodingListForm is not valid."

        #-- END check to see whether or not form is valid. --#

    else:
    
        # new request, just use empty instance of form created and stored above.
        pass

    #-- END check to see if new request or POST --#
    
    # add on the "me" property.
    response_dictionary[ 'current_view' ] = me        

    # render response
    response_OUT = render( request_IN, default_template, response_dictionary )

    return response_OUT

#-- END view function article_coding_list() --#

    
@login_required
def article_view( request_IN ):

    #return reference
    response_OUT = None

    # declare variables
    me = "article_view"
    response_dictionary = {}
    default_template = ''
    request_inputs = None
    article_lookup_form = None
    is_form_ready = False
    article_id = -1
    article_qs = None
    article_count = -1
    article_instance = None
    article_paragraph_list = None
    
    # declare variables - interacting with article text
    article_content = ""
    article_content_bs = None
    p_tag_list = []
    p_tag_count = -1
    rendered_article_html = ""
    paragraph_index = -1
    paragraph_number = -1
    p_tag_bs = None
    p_tag_html = ""

    # initialize response dictionary
    response_dictionary = {}
    response_dictionary.update( csrf( request_IN ) )
    response_dictionary[ 'article_instance' ] = None
    response_dictionary[ 'article_text' ] = None

    # set my default rendering template
    default_template = 'sourcenet/articles/article-view.html'

    # variables for building, populating person array that is used to control
    #    building of network data matrices.

    # do we have output parameters?
    if ( request_IN.method == 'POST' ):

        # use request_IN.POST as request_inputs.
        request_inputs = request_IN.POST
        
    elif ( request_IN.method == 'GET' ):
    
        # use request_IN.GET as request_inputs.
        request_inputs = request_IN.GET
        
    #-- END check of request method to set request_inputs --#
    
    # got inputs?
    if ( request_inputs is not None ):
        
        # create ArticleLookupForm
        article_lookup_form = ArticleLookupForm( request_inputs )

        # get information we need from request.
        article_id = request_inputs.get( "article_id", -1 )

        is_form_ready = True
    
    #-- END check to see if inputs. --#
    
    # form ready?
    if ( is_form_ready == True ):

        if ( article_lookup_form.is_valid() == True ):

            # retrieve article specified by the input parameter, then create
            #   HTML output of article plus Article_Text.
            
            # get article ID.
            # already populated above.
            #article_id = request_IN.POST.get( "article_id", -1 )

            # retrieve QuerySet that contains that article.
            article_qs = Article.objects.filter( pk = article_id )

            # get count of queryset return items
            if ( ( article_qs != None ) and ( article_qs != "" ) ):

                # get count of articles
                article_count = article_qs.count()
    
                # should only be one.
                if ( article_count == 1 ):
                
                    # get article instance
                    article_instance = article_qs.get()
                    
                    # retrieve article text.
                    article_text = article_instance.article_text_set.get()
                    
                    # get content
                    article_content = article_text.get_content()
                    
                    # parse with beautifulsoup
                    article_content_bs = BeautifulSoup( article_content, "html5lib" )
                    
                    # get paragraph tag list
                    p_tag_list = article_content_bs.find_all( 'p' )
                    p_tag_count = len( p_tag_list )
                    
                    # got p-tags?
                    if ( p_tag_count > 0 ):
                    
                        # yes.  create a table with two columns per row:
                        # - paragraph number
                        # - paragraph text
                        rendered_article_html = '''
                            <table class="gridtable">
                                <tr>
                                    <th>graf#</th>
                                    <th>text</th>
                                </tr>
                        '''
                    
                        # for each paragraph, grab that <p> and place it in a table
                        #    cell.
                        for paragraph_index in range( p_tag_count ):
                        
                            # paragraph number is index + 1
                            paragraph_number = paragraph_index + 1
                            
                            # get <p> tag with ID of paragraph_number
                            p_tag_bs = article_content_bs.find( id = str( paragraph_number ) )
                            
                            # render row
                            p_tag_html = p_tag_bs.prettify()
                            #p_tag_html = StringHelper.encode_string( p_tag_html, output_encoding_IN = StringHelper.ENCODING_UTF8 )
                            output_debug( "In " + me + ": p_tag_html type = " + str( type( p_tag_html ) ) )

                            # calling str() on any part of a string being
                            #    concatenated causes all parts of the string to
                            #    try to encode to default encoding ('ascii').
                            #    This breaks if there are non-ascii characters.
                            rendered_article_html += "\n        <tr><td>" + StringHelper.object_to_unicode_string( paragraph_number ) + "</td><td>" + p_tag_html + "</td></tr>"
                        
                        #-- END loop over <p> ids. --#
                        
                        rendered_article_html += "</table>"
                    
                    else:
                    
                        # no p-tags - just use article_text.
                        rendered_article_html = article_content
                        
                    #-- END check to see if paragraph tags. --#
                    
                    # seed response dictionary.
                    response_dictionary[ 'article_instance' ] = article_instance
                    response_dictionary[ 'article_text' ] = article_text
                    response_dictionary[ 'article_content' ] = rendered_article_html
                    response_dictionary[ 'article_lookup_form' ] = article_lookup_form

                    # get paragraph list
                    #article_paragraph_list = article_text.get_paragraph_list()
                    
                else:
                
                    # error - none or multiple articles found for ID. --#
                    print( "No article returned for ID passed in." )
                    response_dictionary[ 'output_string' ] = "ERROR - nothing in QuerySet returned from call to filter()."
                    response_dictionary[ 'article_lookup_form' ] = article_lookup_form
                    
                #-- END check to see if there is one or other than one. --#

            else:
            
                # ERROR - nothing returned from attempt to get queryset (would expect empty query set)
                response_dictionary[ 'output_string' ] = "ERROR - no QuerySet returned from call to filter().  This is odd."
                response_dictionary[ 'article_lookup_form' ] = article_lookup_form
            
            #-- END check to see if query set is None --#

        else:

            # not valid - render the form again
            response_dictionary[ 'article_lookup_form' ] = article_lookup_form

        #-- END check to see whether or not form is valid. --#

    else:
    
        # new request, make an empty instance of network output form.
        article_lookup_form = ArticleLookupForm()
        response_dictionary[ 'article_lookup_form' ] = article_lookup_form

    #-- END check to see if new request or POST --#
    
    # add on the "me" property.
    response_dictionary[ 'current_view' ] = me        

    # render response
    response_OUT = render( request_IN, default_template, response_dictionary )

    return response_OUT

#-- END view method article_view() --#


@login_required
def article_view_article_data( request_IN ):

    #return reference
    response_OUT = None

    # declare variables
    me = "article_view_article_data"
    response_dictionary = {}
    default_template = ''
    request_inputs = None
    article_lookup_form = None
    is_form_ready = False
    article_id = -1
    article_data_qs = None
    article_data_count = -1
    article_data_list = []
    
    # declare variables - for selecting specific article_data to output.
    article_data_select_form = None
    article_data_id_list = []

    # initialize response dictionary
    response_dictionary = {}
    response_dictionary.update( csrf( request_IN ) )
    response_dictionary[ 'article_instance' ] = None
    response_dictionary[ 'article_text' ] = None

    # set my default rendering template
    default_template = 'sourcenet/articles/article-view-article-data.html'

    # do we have output parameters?
    if ( request_IN.method == 'POST' ):

        # use request_IN.POST as request_inputs.
        request_inputs = request_IN.POST
        
    elif ( request_IN.method == 'GET' ):
    
        # use request_IN.GET as request_inputs.
        request_inputs = request_IN.GET
        
    #-- END check of request method to set request_inputs --#
    
    # got inputs?
    if ( request_inputs is not None ):
        
        # create ArticleLookupForm
        article_lookup_form = ArticleLookupForm( request_inputs )

        # get information we need from request.
        article_id = request_inputs.get( "article_id", -1 )
        article_id = int( article_id )

        # need to also get Article_DataSelectForm?
        if ( article_id > 0 ):

            # yes - make one, pass it the article id.
            article_data_select_form = Article_DataSelectForm( request_inputs, article_id = article_id )

        #-- END check to see if article_id is populated. --#

        is_form_ready = True
    
    #-- END check to see if inputs. --#
    
    # form ready?
    if ( is_form_ready == True ):

        if ( article_lookup_form.is_valid() == True ):

            # retrieve QuerySet of Article_Data related to article.
            article_data_qs = Article_Data.objects.filter( article_id = article_id )

            # get count of queryset return items
            if ( ( article_data_qs is not None ) and ( article_data_qs != "" ) ):

                # do we need to further filter the list?
                if ( ( article_data_select_form is not None ) and ( article_data_select_form.is_valid() == True ) ):
                
                    # yes.  Get list of IDs.
                    article_data_id_list = request_inputs.getlist( "article_data_id_select" )
                    
                    # got any?  If not, just display all.
                    if ( len( article_data_id_list ) > 0 ):
                    
                        # filter to just Article_Data whose IDs were selected.
                        article_data_qs = article_data_qs.filter( id__in = article_data_id_list )
                        
                    #-- END check to see if any IDs selected --#
                
                #-- END check to see if we need to further filter Article_Data list --#
    
                # get count of articles
                article_data_count = article_data_qs.count()
                
                # to start, just make a list out of the article data and pass it
                #    to the template.
                article_data_list = list( article_data_qs )

                # seed response dictionary.
                response_dictionary[ 'article_id' ] = article_id
                response_dictionary[ 'article_data_list' ] = article_data_list
                response_dictionary[ 'article_lookup_form' ] = article_lookup_form
                response_dictionary[ 'article_data_select_form' ] = article_data_select_form

            else:
            
                # ERROR - nothing returned from attempt to get queryset (would expect empty query set)
                response_dictionary[ 'output_string' ] = "ERROR - no QuerySet returned from call to filter().  This is odd."
                response_dictionary[ 'article_lookup_form' ] = article_lookup_form
            
            #-- END check to see if query set is None --#

        else:

            # not valid - render the form again
            response_dictionary[ 'article_lookup_form' ] = article_lookup_form

        #-- END check to see whether or not form is valid. --#

    else:
    
        # new request, make an empty instance of network output form.
        article_lookup_form = ArticleLookupForm()
        response_dictionary[ 'article_lookup_form' ] = article_lookup_form

    #-- END check to see if new request or POST --#
    
    # add on the "me" property.
    response_dictionary[ 'current_view' ] = me        

    # render response
    response_OUT = render( request_IN, default_template, response_dictionary )

    return response_OUT

#-- END view method article_view_article_data() --#


@login_required
def article_view_article_data_with_text( request_IN ):

    #return reference
    response_OUT = None

    # declare variables
    me = "article_view_article_data_with_text"
    response_dictionary = {}
    default_template = ''
    request_inputs = None
    article_lookup_form = None
    is_form_ready = False
    article_id = -1
    article_qs = None
    article_count = -1
    article_instance = None
    article_paragraph_list = None
    
    # declare variables - selecting and filtering Article_Data
    article_data_qs = None
    article_data_count = -1
    article_data_instance = None
    graf_to_subject_map = {}
    id_to_author_list_map = {}

    # declare variables - for selecting specific article_data to output.
    article_data_select_form = None
    article_data_coder = None
    article_data_coder_id = -1
    article_data_coder_username = ""
    rendered_author_html = ""
    author_qs = None
    author_organization = ""
    
    # declare variables - for unassociated subjects
    subject_list = None
    rendered_subject_html = ""
    
    # declare variables - interacting with article text
    p_tag_id_to_subject_map = {}
    current_graf_subjects_list = []
    subject = None
    article_content = ""
    article_content_bs = None
    p_tag_list = []
    p_tag_count = -1
    rendered_article_html = ""
    paragraph_index = -1
    paragraph_number = -1
    p_tag_bs = None
    p_tag_html = ""

    # initialize response dictionary
    response_dictionary = {}
    response_dictionary.update( csrf( request_IN ) )
    response_dictionary[ 'article_instance' ] = None
    response_dictionary[ 'article_text' ] = None

    # set my default rendering template
    default_template = 'sourcenet/articles/article-view-article-data-with-text.html'

    # do we have output parameters?
    if ( request_IN.method == 'POST' ):

        # use request_IN.POST as request_inputs.
        request_inputs = request_IN.POST
        
    elif ( request_IN.method == 'GET' ):
    
        # use request_IN.GET as request_inputs.
        request_inputs = request_IN.GET
        
    #-- END check of request method to set request_inputs --#
    
    # got inputs?
    if ( request_inputs is not None ):
        
        # create ArticleLookupForm
        article_lookup_form = ArticleLookupForm( request_inputs )

        # get information we need from request.
        article_id = request_inputs.get( "article_id", -1 )
        article_id = int( article_id )

        # need to also get Article_DataSelectForm?
        if ( article_id > 0 ):

            # yes - make one, pass it the article id.
            article_data_select_form = Article_DataSelectForm( request_inputs, article_id = article_id )

        #-- END check to see if article_id is populated. --#

        is_form_ready = True
    
    #-- END check to see if inputs. --#
    
    # form ready?
    if ( is_form_ready == True ):

        if ( article_lookup_form.is_valid() == True ):

            # retrieve article specified by the input parameter, then create
            #   HTML output of article plus Article_Text.
            
            # retrieve QuerySet that contains that article.
            article_qs = Article.objects.filter( pk = article_id )

            # get count of queryset return items
            if ( ( article_qs != None ) and ( article_qs != "" ) ):

                # get count of articles
                article_count = article_qs.count()
    
                # should only be one.
                if ( article_count == 1 ):
                
                    # retrieve QuerySet of Article_Data related to article.
                    article_data_qs = Article_Data.objects.filter( article_id = article_id )
        
                    # do we need to further filter the list?
                    if ( ( article_data_select_form is not None ) and ( article_data_select_form.is_valid() == True ) ):
                    
                        # yes.  Get list of IDs.
                        article_data_id_list = request_inputs.getlist( "article_data_id_select" )
                        
                        # got any?  If not, just display all.
                        if ( len( article_data_id_list ) > 0 ):
                        
                            # filter to just Article_Data whose IDs were selected.
                            article_data_qs = article_data_qs.filter( id__in = article_data_id_list )
                            
                        #-- END check to see if any IDs selected --#
                    
                    #-- END check to see if we need to further filter Article_Data list --#
                    
                    article_data_qs = article_data_qs.order_by( "coder__id" )
                    
                    # ! authors
                    
                    # got any Article_Data?
                    if ( article_data_qs.count() > 0 ):
                    
                        rendered_author_html = '''
                            <table class="gridtable">
                                <tr>
                                    <th>coder</th>
                                    <th>author</th>
                                </tr>
                        '''

                        # make table of authors broken out by coder, then person
                        #    ID.
                        for article_data_instance in article_data_qs:
                        
                            # get coder information
                            article_data_coder = article_data_instance.coder
                            article_data_coder_id = article_data_coder.id
                            article_data_coder_username = article_data_coder.username
                        
                            # retrieve all authors
                            author_qs = article_data_instance.article_author_set.all()
                            author_qs = author_qs.order_by( "person__last_name", "person__first_name" )
                            
                            # loop over authors.
                            for author in author_qs:
                            
                                # build HTML
                                # calling str() on any part of a string being
                                #    concatenated causes all parts of the string to
                                #    try to encode to default encoding ('ascii').
                                #    This breaks if there are non-ascii characters.
                                rendered_author_html += "\n        <tr><td>" + StringHelper.object_to_unicode_string( article_data_coder_id ) + " - " + article_data_coder_username + "</td><td>" + StringHelper.object_to_unicode_string( author )
                                
                                # got an organization string?
                                author_organization = author.organization_string
                                if ( ( author_organization is not None ) and ( author_organization != "" ) ):
                                    rendered_author_html += "<br />==> organization: " + author_organization
                                #-- END check to see if name captured. --#

                                rendered_author_html += "</td></tr>"
                            
                            #-- END loop over authors. --#
                        
                        #-- END loop over Article_Data instances --#
                    
                        rendered_author_html += "</table>"

                    #-- END check to see if we have any Article_Data --#
                    
                    # get map of subjects to <p> tags.
                    p_tag_id_to_subject_map = create_graf_to_subject_map( article_data_qs )
                
                    # ! subjects with no mentions (so no associated graf)
                    
                    # got any unassociated subjects?
                    subject_list = p_tag_id_to_subject_map.get( NO_GRAF, [] )
                    if ( len ( subject_list ) > 0 ):
                    
                        # we do.  Make a table for them.
                        rendered_subject_html = create_subject_table_html( subject_list, include_header_row_IN = True )

                    #-- END check to see if unassociated subjects --#
                    
                    # ! text and subjects
                    
                    # get article instance
                    article_instance = article_qs.get()
                    
                    # retrieve article text.
                    article_text = article_instance.article_text_set.get()
                    
                    # get content
                    article_content = article_text.get_content()
                    
                    # parse with beautifulsoup
                    article_content_bs = BeautifulSoup( article_content, "html5lib" )
                    
                    # get paragraph tag list
                    p_tag_list = article_content_bs.find_all( 'p' )
                    p_tag_count = len( p_tag_list )
                    
                    # got p-tags?
                    if ( p_tag_count > 0 ):
                    
                        # yes.  create a table with three columns per row:
                        # - paragraph number
                        # - paragraph text
                        # - subjects detected in that paragraph
                        rendered_article_html = '''
                            <table class="gridtable">
                                <tr>
                                    <th>graf#</th>
                                    <th>text</th>
                                    <th>subjects coded</th>
                                </tr>
                        '''
                    
                        # for each paragraph, grab that <p> and place it in a table
                        #    cell.
                        for paragraph_index in range( p_tag_count ):
                        
                            # paragraph number is index + 1
                            paragraph_number = paragraph_index + 1
                            
                            # get <p> tag with ID of paragraph_number
                            p_tag_bs = article_content_bs.find( id = str( paragraph_number ) )
                            
                            # render row
                            p_tag_html = p_tag_bs.prettify()
                            #p_tag_html = StringHelper.encode_string( p_tag_html, output_encoding_IN = StringHelper.ENCODING_UTF8 )
                            output_debug( "In " + me + ": p_tag_html type = " + str( type( p_tag_html ) ) )

                            # calling str() on any part of a string being
                            #    concatenated causes all parts of the string to
                            #    try to encode to default encoding ('ascii').
                            #    This breaks if there are non-ascii characters.
                            rendered_article_html += "\n        <tr><td>" + StringHelper.object_to_unicode_string( paragraph_number ) + "</td><td>" + p_tag_html + "</td>"
                            
                            # check if any Article_Subjects for this paragraph.
                            current_graf_subjects_list = p_tag_id_to_subject_map.get( paragraph_number, [] )
                            if ( len( current_graf_subjects_list ) > 0 ):
                            
                                # open cell for subject table.
                                rendered_article_html += "<td>"
                                
                                # generate HTML for subject table.
                                rendered_article_html += create_subject_table_html( current_graf_subjects_list, include_header_row_IN = True )

                                # close table cell
                                rendered_article_html += "</td>"

                            else:
                            
                                # none.
                                rendered_article_html += "<td>None</td>"
                            
                            #-- END check to see if Article_Subjects for graf --#
                            
                            # close off the row.
                            rendered_article_html += "\n</tr>"
                        
                        #-- END loop over <p> ids. --#
                        
                        rendered_article_html += "</table>"
                    
                    else:
                    
                        # no p-tags - just use article_text.
                        rendered_article_html = article_content
                        
                    #-- END check to see if paragraph tags. --#
                    
                    # seed response dictionary.
                    response_dictionary[ 'article_instance' ] = article_instance
                    response_dictionary[ 'article_text' ] = article_text
                    response_dictionary[ 'author_info' ] = rendered_author_html
                    response_dictionary[ 'subject_info' ] = rendered_subject_html
                    response_dictionary[ 'article_content' ] = rendered_article_html
                    response_dictionary[ 'article_lookup_form' ] = article_lookup_form
                    response_dictionary[ 'article_data_select_form' ] = article_data_select_form

                    # get paragraph list
                    #article_paragraph_list = article_text.get_paragraph_list()
                    
                else:
                
                    # error - none or multiple articles found for ID. --#
                    print( "No article returned for ID passed in." )
                    response_dictionary[ 'output_string' ] = "ERROR - nothing in QuerySet returned from call to filter()."
                    response_dictionary[ 'article_lookup_form' ] = article_lookup_form
                    
                #-- END check to see if there is one or other than one. --#

            else:
            
                # ERROR - nothing returned from attempt to get queryset (would expect empty query set)
                response_dictionary[ 'output_string' ] = "ERROR - no QuerySet returned from call to filter().  This is odd."
                response_dictionary[ 'article_lookup_form' ] = article_lookup_form
            
            #-- END check to see if query set is None --#

        else:

            # not valid - render the form again
            response_dictionary[ 'article_lookup_form' ] = article_lookup_form

        #-- END check to see whether or not form is valid. --#

    else:
    
        # new request, make an empty instance of network output form.
        article_lookup_form = ArticleLookupForm()
        response_dictionary[ 'article_lookup_form' ] = article_lookup_form

    #-- END check to see if new request or POST --#
    
    # add on the "me" property.
    response_dictionary[ 'current_view' ] = me        

    # render response
    response_OUT = render( request_IN, default_template, response_dictionary )

    return response_OUT

#-- END view method article_view_article_data_with_text() --#


@login_required
def filter_articles( request_IN ):

    '''
    This view allows a user to look up a set of articles (first by entering a
        tag to use to filter articles), and then add tag values to their list of
        tags.
    '''

    #return reference
    response_OUT = None

    # declare variables
    me = "filter_articles"
    current_user = None
    response_dictionary = {}
    default_template = ''
    request_inputs = None
    process_selected_articles_form = None
    article_coding_article_filter_form = None
    ready_to_act = False
    is_article_filter_form_empty = True
    
    # declare variables - filter articles
    article_qs = None
    start_date_IN = ""
    end_date_IN = ""
    date_range_IN = ""
    publication_list_IN = []
    tag_list_IN = ""
    unique_id_list_IN = ""
    article_id_list_IN = ""
    section_list_IN = ""
    filter_articles_params = {}
    article_count = -1
    article_filter_summary = ""
    article_details_list = []
    article_counter = -1
    article_instance = None
    article_details = {}
    
    # declare variables - article processing
    action_IN = ""
    action_summary = ""
    action_detail_list = []
    apply_tags_list_IN = []
    apply_tags_count = -1
    
    # initialize response dictionary
    response_dictionary = {}
    response_dictionary.update( csrf( request_IN ) )

    # set my default rendering template
    default_template = 'sourcenet/articles/article-filter.html'
    
    # get current user
    current_user = request_IN.user

    # do we have input parameters?
    request_inputs = get_request_data( request_IN )
    
    # got inputs?
    if ( request_inputs is not None ):
        
        # create forms
        article_coding_article_filter_form = ArticleCodingArticleFilterForm( request_inputs )
        process_selected_articles_form = ProcessSelectedArticlesForm( request_inputs )
        
        # we can try an action
        ready_to_act = True

    else:
    
        # no inputs - create empty forms
        article_coding_article_filter_form = ArticleCodingArticleFilterForm()
        process_selected_articles_form = ProcessSelectedArticlesForm()
        
        # no action without some inputs
        ready_to_act = False

    #-- END check to see if inputs. --#

    # store forms in response
    response_dictionary[ 'article_coding_article_filter_form' ] = article_coding_article_filter_form
    response_dictionary[ 'process_selected_articles_form' ] = process_selected_articles_form

    # form ready?
    if ( ready_to_act == True ):

        if ( article_coding_article_filter_form.is_valid() == True ):

            # is the form empty?  If so, do nothing.
            is_article_filter_form_empty = article_coding_article_filter_form.am_i_empty()
            if ( is_article_filter_form_empty == False ):

                # retrieve articles specified by the input parameters, ordered by
                #     Article ID, then create HTML output of list of articles.  For
                #     each, output:
                #     - article string
                #     - link to code article.  If no existing coding, make it a
                #         generic link.  If existing coding, make the Article_Data
                #         string the link.
                
                # retrieve the incoming parameters
                start_date_IN = request_inputs.get( SourcenetBase.PARAM_START_DATE, None )
                end_date_IN = request_inputs.get( SourcenetBase.PARAM_END_DATE, None )
                date_range_IN = request_inputs.get( SourcenetBase.PARAM_DATE_RANGE, None )
                publication_list_IN = request_inputs.getlist( SourcenetBase.PARAM_PUBLICATION_LIST, None )
                tag_list_IN = DictHelper.get_dict_value_as_list( request_inputs, SourcenetBase.PARAM_TAG_LIST, None )
                unique_id_list_IN = DictHelper.get_dict_value_as_list( request_inputs, SourcenetBase.PARAM_UNIQUE_ID_LIST, None )
                article_id_list_IN = DictHelper.get_dict_value_as_list( request_inputs, SourcenetBase.PARAM_ARTICLE_ID_LIST, None )
                section_list_IN = DictHelper.get_dict_value_as_list( request_inputs, SourcenetBase.PARAM_SECTION_LIST, None )
            
                # get all articles to start
                article_qs = Article.objects.all()
                
                # set up dictionary for call to Article.filter_articles()
                filter_articles_params = {}
                filter_articles_params[ Article.PARAM_START_DATE ] = start_date_IN
                filter_articles_params[ Article.PARAM_END_DATE ] = end_date_IN
                filter_articles_params[ Article.PARAM_DATE_RANGE ] = date_range_IN
                filter_articles_params[ Article.PARAM_NEWSPAPER_ID_IN_LIST ] = publication_list_IN
                filter_articles_params[ Article.PARAM_TAGS_IN_LIST ] = tag_list_IN
                filter_articles_params[ Article.PARAM_UNIQUE_ID_IN_LIST ] = unique_id_list_IN
                filter_articles_params[ Article.PARAM_ARTICLE_ID_IN_LIST ] = article_id_list_IN
                filter_articles_params[ Article.PARAM_SECTION_NAME_IN_LIST ] = section_list_IN
                
                # call Article.filter_articles() retrieve QuerySet that contains
                #     articles that match filter criteria.
                article_qs = Article.filter_articles( qs_IN = article_qs, params_IN = filter_articles_params )
                
                # Order by ID.
                article_qs = article_qs.order_by( "id" )
    
                # get count of queryset return items
                if ( ( article_qs != None ) and ( article_qs != "" ) ):
    
                    # get count of articles
                    article_count = article_qs.count()
        
                    # got one or more?
                    if ( article_count >= 1 ):
                    
                        # always create and store a summary of articles.
                        article_filter_summary = "Found " + str( article_count ) + " articles that match your selected filter criteria: " + str( filter_articles_params )
                        response_dictionary[ 'article_filter_summary' ] = article_filter_summary
                        
                        # ! TODO - use process_selected_articles_form to see
                        #     what we do now...
                        
                        # is form valid?
                        if ( process_selected_articles_form.is_valid() == True ):
                        
                            # yes - do we have an action?
                            action_IN = request_inputs.get( "action", None )
                            if ( action_IN is not None ):
                                
                                # add to response.
                                response_dictionary[ 'action' ] = action_IN
                            
                                # is it "view_matches"?
                                if ( action_IN == "view_matches" ):

                                    # yes - initialize list of article_details
                                    article_details_list = []
                                
                                    # loop over articles
                                    article_counter = 0
                                    for article_instance in article_qs:
                                    
                                        # increment article_counter
                                        article_counter += 1
                                    
                                        # new article_details
                                        article_details = {}
                                        
                                        # store index and article
                                        article_details[ "index" ] = article_counter
                                        article_details[ "article_instance" ] = article_instance
                                        
                                        # add details to list.
                                        article_details_list.append( article_details )
                
                                    #-- END loop over articles --#
                                    
                                    # seed response dictionary.
                                    response_dictionary[ 'article_details_list' ] = article_details_list
            
                                elif ( action_IN == "apply_tags" ):
                                
                                    # retrieve list of tags to apply.
                                    apply_tags_list_IN = DictHelper.get_dict_value_as_list( request_inputs, SourcenetBase.PARAM_APPLY_TAGS_LIST, None )
                                    if ( apply_tags_list_IN is not None ):
                                        
                                        apply_tags_count = len( apply_tags_list_IN )
                                
                                        # Check count of articles retrieved.
                                        action_summary = "Got " + str( article_count ) + " articles to tag with tags \"" + str( apply_tags_list_IN ) + "\"."
                                        response_dictionary[ "action_summary" ] = action_summary
                                        
                                        # loop over tags
                                        for current_tag in apply_tags_list_IN:
                                        
                                            # output the tags.
                                            action_detail_list.append( "Adding tag \"" + current_tag + "\" to articles:" )

                                            # loop over articles.
                                            for current_article in article_qs:
                                            
                                                # add tag.
                                                current_article.tags.add( current_tag )
                                                
                                                # output the tags.
                                                action_detail_list.append( "----> Tags for article " + str( current_article.id ) + " : " + str( current_article.tags.all() ) )
                                                
                                            #-- END loop over articles --#
                                            
                                        #-- END loop over tags to apply to selected articles. --#
                                        
                                        # add variables to response
                                        response_dictionary[ "action_detail_list" ] = action_detail_list
                                        
                                    else:
                                        
                                        # no tags to apply.  Output message.
                                        action_summary = "Got " + str( article_count ) + " articles to tag, but no tags to apply were entered.  Please enter the tags you want to apply to the selected articles."
                                        response_dictionary[ "action_summary" ] = action_summary
                                        
                                    #-- END check to see if any tags specified to be applied. --#
                                
                                #-- END check to see what action. --#

                            #-- END check to see if action present. --#
                            
                        #-- END check to see if article processing form is valid --#
                                            
                    else:
                    
                        # error - none or multiple articles found for ID. --#
                        print( "No article returned for ID passed in." )
                        response_dictionary[ 'output_string' ] = "No matches for filter criteria."
                        
                    #-- END check to see if there is one or other than one. --#
    
                else:
                
                    # ERROR - nothing returned from attempt to get queryset (would expect empty query set)
                    response_dictionary[ 'output_string' ] = "ERROR - no QuerySet returned from call to Article.filter_articles().  This is odd."
                    
                
                #-- END check to see if query set is None --#
                
            else:
            
                # form is empty.
                response_dictionary[ 'output_string' ] = "Please enter at least one filter criteria."
            
            #-- END check to see if form is empty --#

        else:

            # not valid - render the form again
            response_dictionary[ 'output_string' ] = "ArticleCodingArticleFilterForm is not valid."

        #-- END check to see whether or not form is valid. --#

    else:
    
        # new request, just use empty instance of form created and stored above.
        pass

    #-- END check to see if new request or POST --#
    
    # add on the "me" property.
    response_dictionary[ 'current_view' ] = me        

    # render response
    response_OUT = render( request_IN, default_template, response_dictionary )

    return response_OUT

#-- END view function filter_articles() --#

    
@login_required
def index( request_IN ):
    
    # return reference
    me = "index"
    response_OUT = None
    response_dictionary = {}
    default_template = ''

    # initialize response dictionary
    response_dictionary = {}
    response_dictionary.update( csrf( request_IN ) )

    # set my default rendering template
    default_template = 'sourcenet/index.html'

    # add on the "me" property.
    response_dictionary[ 'current_view' ] = me        

    # render response
    response_OUT = render( request_IN, default_template, response_dictionary )

    return response_OUT

#-- END view method index() --#


def logout( request_IN ):

    # declare variables
    me = "sourcenet.views.logout"
    request_data = None
    redirect_path = ""
    
    # initialize redirect_path
    redirect_path = "/"
    
    # do we have input parameters?
    request_data = get_request_data( request_IN )
    if ( request_data is not None ):
    
        # we do.  See if we have redirect.
        redirect_path = request_data.get( "post_logout_redirect", "/" )

    #-- END check to see if we have request data. --#

    # log out the user.
    auth.logout( request_IN )

    # Redirect to server home page for now.
    return HttpResponseRedirect( redirect_path )
    
#-- END view method logout() --#


@login_required
def output_articles( request_IN ):

    #return reference
    response_OUT = None

    # declare variables
    me = "output_articles"
    response_dictionary = {}
    default_template = ''
    article_select_form = None
    output_type_form = None
    output_string = ''
    network_outputter = None
    current_item = None
    network_query_set = None
    article_data_count = ''
    query_counter = ''
    
    # initialize response dictionary
    response_dictionary = {}
    response_dictionary.update( csrf( request_IN ) )

    # set my default rendering template
    default_template = 'sourcenet/sourcenet_output_articles.html'

    # variables for building, populating person array that is used to control
    #    building of network data matrices.

    # do we have output parameters?
    if request_IN.method == 'POST':

        article_select_form = ArticleSelectForm( request_IN.POST )
        output_type_form = ArticleOutputTypeSelectForm( request_IN.POST )

        if ( ( article_select_form.is_valid() == True ) and ( output_type_form.is_valid() == True ) ):

            # retrieve articles specified by the input parameters, then create
            #   string output, then pass it and form on to the output form.

            # initialize the NetworkOutput instance.
            network_outputter = NetworkOutput()
            network_outputter.set_request( request_IN )

            # For now, output plain string
            output_string = network_outputter.debug_parameters()

            #-------------------------------------------------------------------
            # summary info.
            #-------------------------------------------------------------------

            # retrieve QuerySet based on parameters passed in.
            network_query_set = network_outputter.create_network_query_set()

            # get count of queryset return items
            if ( ( network_query_set != None ) and ( network_query_set != "" ) ):

                # get count of articles
                article_data_count = network_query_set.count()
    
                output_string += "\n\nTotal articles returned: " + str( article_data_count ) + "\n\n\n"
    
                # loop over the query set.
                query_counter = 0
                for current_item in network_query_set:
                    query_counter += 1
                    output_string += "- ( " + str( query_counter ) + " ) " + current_item.article.headline + "\n"
    
                # first, build the CSV list of articles, so we can use it for
                #    reliability, basic statistics.
                output_string += "\n\n"
                output_string += "====================\n"
                output_string += "CSV output:\n"
                output_string += "====================\n"
                output_string += network_outputter.render_csv_article_data( network_query_set )
                output_string += "====================\n"
                output_string += "END CSV output\n"
                output_string += "====================\n"
    
                # Prepare parameters for view.
                response_dictionary[ 'output_string' ] = output_string
                response_dictionary[ 'article_select_form' ] = article_select_form
                response_dictionary[ 'output_type_form' ] = output_type_form
                response_OUT = render( request_IN, default_template, response_dictionary )
                
            else:
            
                # is None.  error.
                response_dictionary[ 'output_string' ] = "ERROR - network query set is None."
                response_dictionary[ 'article_select_form' ] = article_select_form
                response_dictionary[ 'output_type_form' ] = output_type_form
                response_OUT = render( request_IN, default_template, response_dictionary )
            
            #-- END check to see if query set is None --#
            '''
            # is None.  error.
            response_dictionary[ 'output_string' ] = "debug - " + str( type( network_query_set ) ) + " - " + str( network_query_set )
            response_dictionary[ 'article_select_form' ] = article_select_form
            response_dictionary[ 'output_type_form' ] = output_type_form
            response_OUT = render( request_IN, default_template, response_dictionary )
            '''
            
        else:

            # not valid - render the form again
            response_dictionary[ 'article_select_form' ] = article_select_form
            response_dictionary[ 'output_type_form' ] = output_type_form
            response_OUT = render( request_IN, default_template, response_dictionary )

        #-- END check to see whether or not form is valid. --#

    else:
    
        # new request, make an empty instance of network output form.
        article_select_form = ArticleSelectForm()
        output_type_form = ArticleOutputTypeSelectForm()
        response_dictionary[ 'article_select_form' ] = article_select_form
        response_dictionary[ 'output_type_form' ] = output_type_form

        # add on the "me" property.
        response_dictionary[ 'current_view' ] = me        

        # render
        response_OUT = render( request_IN, default_template, response_dictionary )

    #-- END check to see if new request or POST --#


    return response_OUT

#-- END view method output_articles() --#


@login_required
def output_network( request_IN ):

    #return reference
    response_OUT = None

    # declare variables
    me = "output_network"
    response_dictionary = {}
    default_template = ''
    
    # declare variables - forms
    article_select_form = None
    network_output_form = None
    person_select_form = None
    relation_select_form = None
    
    # declare variables - rendering
    include_render_details_IN = ''
    include_render_details = False
    download_as_file_IN = ""
    download_as_file = False
    output_string = ''
    network_outputter = None
    current_item = None
    network_query_set = None
    article_count = ''
    query_counter = ''
    my_content_type = ""
    my_file_extension = ""
    current_date_time = ""

    # initialize response dictionary
    response_dictionary = {}
    response_dictionary.update( csrf( request_IN ) )

    # set my template
    default_template = 'sourcenet/sourcenet_output_network.html'
    
    # output parameters
 
    # does user want to download the result as a file?
    download_as_file_IN = request_IN.POST.get( NetworkOutput.PARAM_NETWORK_DOWNLOAD_AS_FILE, NetworkOutput.CHOICE_NO )

    # convert download_as_file_IN to boolean
    if ( download_as_file_IN == NetworkOutput.CHOICE_YES ):
    
        # yes - True
        download_as_file = True

    else:
    
        # not yes, so False.
        download_as_file = False
    
    #-- END check to see whether user wants to download the results as a file --#

    # variables for building, populating person array that is used to control
    #    building of network data matrices.

    # do we have output parameters?
    if request_IN.method == 'POST':

        article_select_form = ArticleSelectForm( request_IN.POST )
        network_output_form = NetworkOutputForm( request_IN.POST )
        person_select_form = PersonSelectForm( request_IN.POST )
        relation_select_form = RelationSelectForm( request_IN.POST )

        # is all our form data OK?
        if ( ( article_select_form.is_valid() == True )
            and ( network_output_form.is_valid() == True )
            and ( person_select_form.is_valid() == True )
            and ( relation_select_form.is_valid() == True ) ):

            # retrieve articles specified by the input parameters, then create
            #   string output, then pass it and form on to the output form.
            
            # do we include details?
            include_render_details_IN = request_IN.POST.get( NetworkOutput.PARAM_NETWORK_INCLUDE_RENDER_DETAILS, NetworkOutput.CHOICE_NO )

            # convert include_render_details_IN to boolean
            if ( include_render_details_IN == NetworkOutput.CHOICE_YES ):
            
                # yes - True
                include_render_details = True
    
            else:
            
                # not yes, so False.
                include_render_details = False
            
            #-- END check to see whether we include render details --#

            # initialize the NetworkOutput instance.
            network_outputter = NetworkOutput()
            network_outputter.set_request( request_IN )
            
            # prepare data
            
            # retrieve Article_Data QuerySet based on parameters passed in.
            network_query_set = network_outputter.create_network_query_set()
            
            output_debug( "In " + me + ": type of network_query_set = " + str( type( network_query_set ) ) )

            # get count of queryset return items
            if ( network_query_set is not None ):
            
                article_data_count = network_query_set.count()
                
            else:
            
                article_data_count = -1
                
            #-- END check to see if None --#

            output_debug( "In " + me + ": before parameter and article details." )

            # include render details?
            if ( include_render_details == True ):

                # For now, output plain string
                output_string += "=======================\n"
                output_string += "parameter overview:\n"
                output_string += "=======================\n"
                output_string += "\n"
                output_string += network_outputter.debug_parameters()
                output_string += "\n"
                output_string += "\n"
                my_param_container = network_outputter.get_param_container()
                output_string += my_param_container.debug_parameters()
    
                #-------------------------------------------------------------------
                # summary info.
                #-------------------------------------------------------------------
    
                output_string += "\n\n\n"
                output_string += "=======================\n"
                output_string += "article overview:\n"
                output_string += "=======================\n"
                output_string += "\nTotal article data rows returned: " + str( article_data_count ) + "\n\n"
    
                # loop over the query set.
                query_counter = 0
                
                if ( network_query_set is not None ):

                    for current_item in network_query_set:
        
                        query_counter += 1
                        output_string += "- " + str( query_counter ) + " ( id: " + str( current_item.article.id ) + " ) - " + current_item.article.headline + "\n"
        
                    #-- END loop over articles to list out headlines. --#
                    
                #-- END check to see if network_query_set is None --#
    
                # render and output networkd data.
                output_string += "\n\n"
                output_string += "=======================\n"
                output_string += "network data output:\n"
                output_string += "=======================\n"
                
            #-- END check to see if we include render details. --#
            
            output_debug( "In " + me + ": after parameter and article details, before rendering network." )

            # render the actual network data.
            output_string += network_outputter.render_network_data( network_query_set )

            # include render details?
            if ( include_render_details == True ):

                output_string += "=======================\n"
                output_string += "END network data output\n"
                output_string += "=======================\n"
    
            #-- END check to see if we output render details --#

            output_debug( "In " + me + ": download file, or render view?" )

            # download as file, or render view?
            if ( download_as_file == True ):
            
                # figure out the content type and content disposition.
                my_content_type = network_outputter.mime_type
                my_file_extension = network_outputter.file_extension
                
                # time stamp to append to file name
                current_date_time = datetime.datetime.now().strftime( '%Y%m%d-%H%M%S' )
                
                # Create the HttpResponse object with the appropriate content
                #    type and disposition.
                response_OUT = HttpResponse( content = output_string, content_type = my_content_type )
                response_OUT[ 'Content-Disposition' ] = 'attachment; filename="sourcenet_data-' + current_date_time + '.' + my_file_extension + '"'
            
            else:

                # Prepare parameters for view.
                response_dictionary[ 'output_string' ] = output_string
                response_dictionary[ 'article_select_form' ] = article_select_form
                response_dictionary[ 'network_output_form' ] = network_output_form
                response_dictionary[ 'person_select_form' ] = person_select_form
                response_dictionary[ 'relation_select_form' ] = relation_select_form
                response_OUT = render( request_IN, default_template, response_dictionary )
                
            #-- END check to see if we return result as a file --#

        else:

            # not valid - render the form again
            response_dictionary[ 'output_string' ] = "Invalid Form"
            response_dictionary[ 'article_select_form' ] = article_select_form
            response_dictionary[ 'network_output_form' ] = network_output_form
            response_dictionary[ 'person_select_form' ] = person_select_form
            response_dictionary[ 'relation_select_form' ] = relation_select_form
            response_OUT = render( request_IN, default_template, response_dictionary )

        #-- END check to see whether or not form is valid. --#

    else:

        # new request, make an empty instance of network output form.
        article_select_form = ArticleSelectForm()
        network_output_form = NetworkOutputForm()
        person_select_form = PersonSelectForm()
        relation_select_form = RelationSelectForm()
        response_dictionary[ 'article_select_form' ] = article_select_form
        response_dictionary[ 'network_output_form' ] = network_output_form
        response_dictionary[ 'person_select_form' ] = person_select_form
        response_dictionary[ 'relation_select_form' ] = relation_select_form
        
        # add on the "me" property.
        response_dictionary[ 'current_view' ] = me        

        # declare variables
        response_OUT = render( request_IN, default_template, response_dictionary )

    #-- END check to see if new request or POST --#


    return response_OUT

#-- END view method output_network() --#


@login_required
def person_filter_and_process( request_IN ):

    '''
    This view allows a user to look up a set of Persons who have similar names
        and merge any that are duplicates.
    '''

    #return reference
    response_OUT = None

    # declare variables
    me = "person_fix_duplicates"
    my_logger_name = "sourcenet.views.person_filter_and_process"
    debug_message = ""
    current_user = None
    response_dictionary = {}
    default_template = ''
    request_inputs = None
    person_lookup_by_name_form = None
    person_lookup_type_form = None
    person_process_selected_form = None
    ready_to_act = False
    is_lookup_form_empty = True
    
    # declare variables - filter Person records
    person_qs = None
    person_count = -1
    full_name_string_IN = ""
    first_name_IN = ""
    middle_name_IN = ""
    last_name_IN = ""
    name_prefix_IN = ""
    name_suffix_IN = ""
    name_nickname_IN = ""
    my_person_details = None
    human_name = None
    name_string = ""
    lookup_type = ""
    do_strict_match = False
    do_partial_match = False
    
    # declare variables - person processing
    action_IN = ""
    action_summary = ""
    action_detail_list = []
    person_details_list = []
    person_details_dict = {}
    person_counter = -1
    person_instance = None
    
    # initialize response dictionary
    response_dictionary = {}
    response_dictionary.update( csrf( request_IN ) )

    # set my default rendering template
    default_template = 'sourcenet/person/person-filter-process.html'
    
    # get current user
    current_user = request_IN.user

    # do we have input parameters?
    request_inputs = get_request_data( request_IN )
    
    # got inputs?
    if ( request_inputs is not None ):
        
        # create forms
        person_lookup_by_name_form = PersonLookupByNameForm( request_inputs )
        person_lookup_type_form = PersonLookupTypeForm( request_inputs )
        person_process_selected_form = Person_ProcessSelectedForm( request_inputs )
        
        # we can try an action
        ready_to_act = True

    else:
    
        # no inputs - create empty forms
        person_lookup_by_name_form = PersonLookupByNameForm()
        person_lookup_type_form = PersonLookupTypeForm()
        person_process_selected_form = Person_ProcessSelectedForm()
        
        # no action without some inputs
        ready_to_act = False

    #-- END check to see if inputs. --#

    # store forms in response
    response_dictionary[ "person_lookup_by_name_form" ] = person_lookup_by_name_form
    response_dictionary[ "person_lookup_type_form" ] = person_lookup_type_form
    response_dictionary[ "person_process_selected_form" ] = person_process_selected_form

    # form ready?
    if ( ready_to_act == True ):

        if ( person_lookup_by_name_form.is_valid() == True ):

            # is the form empty?  If so, do nothing.
            is_lookup_form_empty = person_lookup_by_name_form.am_i_empty()
            if ( is_lookup_form_empty == False ):

                # retrieve Person records specified by the input parameters,
                #     ordered by Last Name, then First Name.  Then, create HTML
                #     output of list of articles.  For each, output (to start):
                #     - Person string
                
                # populate PersonDetails from request_inputs:
                my_person_details = PersonDetails.get_instance( request_inputs )
                
                # get name fields from person_details
                full_name_string_IN = my_person_details.get( PersonDetails.PROP_NAME_FULL_NAME_STRING, None )
                first_name_IN = my_person_details.get( PersonDetails.PROP_NAME_FIRST_NAME, None )
                middle_name_IN = my_person_details.get( PersonDetails.PROP_NAME_MIDDLE_NAME, None )
                last_name_IN = my_person_details.get( PersonDetails.PROP_NAME_LAST_NAME, None )
                name_prefix_IN = my_person_details.get( PersonDetails.PROP_NAME_NAME_PREFIX, None )
                name_suffix_IN = my_person_details.get( PersonDetails.PROP_NAME_NAME_SUFFIX, None )
                name_nickname_IN = my_person_details.get( PersonDetails.PROP_NAME_NICKNAME, None )
                
                # get HumanName instance...
                human_name = my_person_details.to_HumanName()
                name_string = str( human_name )
                
                # figure out type of lookup.
                lookup_type = None
                if ( person_lookup_type_form.is_valid() == True ):
                
                    # form is valid, use type from form.
                    lookup_type = request_inputs.get( "lookup_type", PersonLookupTypeForm.PERSON_LOOKUP_TYPE_GENERAL_QUERY )
                
                else:
                
                    # form is not valid.  Default to general lookup
                    lookup_type = PersonLookupTypeForm.PERSON_LOOKUP_TYPE_GENERAL_QUERY
                
                #-- END Check to see if lookup type passed in --#
                
                debug_message = "lookup_type = " + str( lookup_type )
                LoggingHelper.output_debug( debug_message, method_IN = me, logger_name_IN = my_logger_name )

                # do lookup based on lookup_type
                if ( lookup_type == PersonLookupTypeForm.PERSON_LOOKUP_TYPE_GENERAL_QUERY ):
                
                    debug_message = "performing general query"
                    LoggingHelper.output_debug( debug_message, method_IN = me, logger_name_IN = my_logger_name )
                
                    # not strict
                    do_strict_match = False
                    do_partial_match = True
                    person_qs = Person.look_up_person_from_name( name_IN = name_string,
                                                                 parsed_name_IN = human_name,
                                                                 do_strict_match_IN = do_strict_match,
                                                                 do_partial_match_IN = do_partial_match )
                
                elif ( lookup_type == PersonLookupTypeForm.PERSON_LOOKUP_TYPE_EXACT_QUERY ):
                
                    debug_message = "performing exact query"
                    LoggingHelper.output_debug( debug_message, method_IN = me, logger_name_IN = my_logger_name )

                    # strict
                    do_strict_match = True
                    do_partial_match = False
                    person_qs = Person.look_up_person_from_name( name_IN = name_string,
                                                                 parsed_name_IN = human_name,
                                                                 do_strict_match_IN = do_strict_match,
                                                                 do_partial_match_IN = do_partial_match )

                else:
                
                    debug_message = "no lookup_type, so doing general query"
                    LoggingHelper.output_debug( debug_message, method_IN = me, logger_name_IN = my_logger_name )

                    # default to not strict
                    do_strict_match = False
                    do_partial_match = True
                    person_qs = Person.look_up_person_from_name( name_IN = name_string,
                                                                 parsed_name_IN = human_name,
                                                                 do_strict_match_IN = do_strict_match,
                                                                 do_partial_match_IN = do_partial_match )
                
                #-- END decide how to lookup based on lookup_type --#
                                    
                # get count of queryset return items
                if ( ( person_qs != None ) and ( person_qs != "" ) ):
    
                    # get count of records
                    person_count = person_qs.count()
        
                    # got one or more?
                    if ( person_count >= 1 ):
                    
                        # always create and store a summary of Person records.
                        person_filter_summary = "Found " + str( person_count ) + " Person records that match your selected filter criteria: " + str( human_name )
                        response_dictionary[ 'person_filter_summary' ] = person_filter_summary
                        
                        # ! use person_process_selected_form to see what we do now...
                        
                        # is form valid?
                        if ( person_process_selected_form.is_valid() == True ):
                        
                            # yes - do we have an action?
                            action_IN = request_inputs.get( "action", None )
                            if ( action_IN is not None ):
                                
                                # add to response.
                                response_dictionary[ 'action' ] = action_IN
                            
                                # is it "view_matches"?
                                if ( action_IN == "view_matches" ):

                                    # yes - initialize list of person_details
                                    person_details_list = []
                                
                                    # loop over articles
                                    person_counter = 0
                                    for person_instance in person_qs:
                                    
                                        # increment counter
                                        person_counter += 1
                                    
                                        # new details dictionary
                                        person_details_dict = {}
                                        
                                        # store index and person instance
                                        person_details_dict[ "index" ] = person_counter
                                        person_details_dict[ "instance" ] = person_instance
                                        
                                        # add details to list.
                                        person_details_list.append( person_details_dict )
                
                                    #-- END loop over records --#
                                    
                                    # seed response dictionary.
                                    response_dictionary[ 'person_details_list' ] = person_details_list
            
                                elif ( action_IN == "merge" ):
                                
                                    # ! TODO - merge.
                                    pass
                                
                                #-- END check to see what action. --#

                            #-- END check to see if action present. --#
                            
                        #-- END check to see if article processing form is valid --#
                                            
                    else:
                    
                        # error - none or multiple articles found for ID. --#
                        print( "No Person records returned for ID passed in." )
                        response_dictionary[ 'output_string' ] = "No matches for filter criteria."
                        
                    #-- END check to see if there is one or other than one. --#
    
                else:
                
                    # ERROR - nothing returned from attempt to get queryset (would expect empty query set)
                    response_dictionary[ 'output_string' ] = "ERROR - no QuerySet returned from call to Person.look_up_person_from_name().  This is odd.  HumanName = " + str( human_name ) + "; lookup_type = " + str( lookup_type ) + "."
                
                #-- END check to see if query set is None --#
                
            else:
            
                # form is empty.
                response_dictionary[ 'output_string' ] = "Please enter at least one filter criteria."
            
            #-- END check to see if form is empty --#

        else:

            # not valid - render the form again
            response_dictionary[ 'output_string' ] = "ArticleCodingArticleFilterForm is not valid."

        #-- END check to see whether or not form is valid. --#

    else:
    
        # new request, just use empty instance of form created and stored above.
        pass

    #-- END check to see if new request or POST --#
    
    # add on the "me" property.
    response_dictionary[ 'current_view' ] = me        

    # render response
    response_OUT = render( request_IN, default_template, response_dictionary )

    return response_OUT

#-- END view function person_filter_and_process() --#
