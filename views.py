from __future__ import unicode_literals

'''
Copyright 2010-2013 Jonathan Morgan

This file is part of http://github.com/jonathanmorgan/sourcenet.

sourcenet is free software: you can redistribute it and/or modify it under the terms of the GNU Lesser General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.

sourcenet is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.

You should have received a copy of the GNU Lesser General Public License along with http://github.com/jonathanmorgan/sourcenet. If not, see http://www.gnu.org/licenses/.
'''

#===============================================================================
# imports (in alphabetical order by package, then by name)
#===============================================================================

# import Python libraries for CSV output
#import csv
import datetime
import json
#from StringIO import StringIO
#import pickle

# HTML parsing
from bs4 import BeautifulSoup

# import django authentication code.
from django.contrib import auth
from django.contrib.auth.decorators import login_required

# include the django conf settings
#from django.conf import settings

# django core imports

# import django code for csrf security stuff.
from django.template.context_processors import csrf

#from django.core.urlresolvers import reverse

# Import objects from the django.http library.
#from django.http import Http404
from django.http import HttpResponse
from django.http import HttpResponseRedirect

# import the render_to_response() method from django.shortcuts
#from django.shortcuts import get_object_or_404
from django.shortcuts import render_to_response

# import django template code
#from django.template import Context
#from django.template import loader
from django.template import RequestContext

# python_utilities - logging
from python_utilities.logging.logging_helper import LoggingHelper

# python_utilities - string helper
from python_utilities.strings.string_helper import StringHelper

# Import the form classes for network output
from sourcenet.forms import Article_DataSelectForm
from sourcenet.forms import ArticleCodingForm
from sourcenet.forms import ArticleCodingSubmitForm
from sourcenet.forms import ArticleLookupForm
from sourcenet.forms import ArticleOutputTypeSelectForm
from sourcenet.forms import ArticleSelectForm
from sourcenet.forms import PersonSelectForm
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
# Shared variables and functions
#================================================================================

'''
Gross debugging code, shared across all models.
'''

DEBUG = True


def output_debug( message_IN, method_IN = "", indent_with_IN = "", logger_name_IN = "" ):
    
    '''
    Accepts message string.  If debug is on, logs it.  If not,
       does nothing for now.
    '''
    
    # declare variables
    my_message = ""
    my_logger = None
    my_logger_name = ""

    # got a message?
    if ( message_IN ):
    
        # only print if debug is on.
        if ( DEBUG == True ):
        
            my_message = message_IN
        
            # got a method?
            if ( method_IN ):
            
                # We do - append to front of message.
                my_message = "In " + method_IN + ": " + my_message
                
            #-- END check to see if method passed in --#
            
            # indent?
            if ( indent_with_IN ):
                
                my_message = indent_with_IN + my_message
                
            #-- END check to see if we indent. --#
        
            # debug is on.  Start logging rather than using print().
            #print( my_message )
            
            # got a logger name?
            my_logger_name = "sourcenet.views"
            if ( ( logger_name_IN is not None ) and ( logger_name_IN != "" ) ):
            
                # use logger name passed in.
                my_logger_name = logger_name_IN
                
            #-- END check to see if logger name --#
                
            # get logger
            my_logger = LoggingHelper.get_a_logger( my_logger_name )
            
            # log debug.
            my_logger.debug( my_message )
        
        #-- END check to see if debug is on --#
    
    #-- END check to see if message. --#

#-- END method output_debug() --#


#===============================================================================
# view action methods (in alphabetical order)
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

#    return render_to_response( 'polls/detail.html', { 'poll' : poll_instance }, context_instance = RequestContext( request_IN ) )

#-- end method detail() --#


#def index( request_IN ):

    # return reference
#    response_OUT = None

    # declare variables
#    param_dictionary = {}
#    context = None

    #return HttpResponse( "Hello, world.  You're at the poll index." )
#    latest_poll_list = Poll.objects.all().order_by('-pub_date')[:5]

    # set up the rendering dictionary
#    param_dictionary.update( {'latest_poll_list': latest_poll_list} )

    # get the context
#    context = RequestContext( request_IN )

    # this has a django.shortcuts method, render_to_response, used below.
    #t = loader.get_template('polls/index.html')
    #c = Context({
    #    'latest_poll_list': latest_poll_list,
    #})
    #return HttpResponse(t.render(c))
    #response_OUT = render_to_response('polls/index.html', {'latest_poll_list': latest_poll_list})
#    response_OUT = render_to_response('polls/index.html', param_dictionary, context_instance = context )

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

#    response_OUT = render_to_response( 'polls/results.html', { 'poll': poll_instance }, context_instance = RequestContext( request_IN ) )

#    return response_OUT

#-- end view method results() --#


def logout( request_IN ):

    # log out the user.
    auth.logout( request_IN )

    # Redirect to server home page for now.
    return HttpResponseRedirect( "/" )
    
#-- END view method logout() --#


@login_required
def article_view( request_IN ):

    #return reference
    response_OUT = None

    # declare variables
    me = "article_view"
    my_context_instance = None
    response_dictionary = {}
    default_template = ''
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

    # configure context instance
    my_context_instance = RequestContext( request_IN )
    
    # initialize response dictionary
    response_dictionary = {}
    response_dictionary.update( csrf( request_IN ) )
    response_dictionary[ 'article_instance' ] = None
    response_dictionary[ 'article_text' ] = None

    # set my default rendering template
    default_template = 'articles/article-view.html'

    # variables for building, populating person array that is used to control
    #    building of network data matrices.

    # do we have output parameters?
    if ( request_IN.method == 'POST' ):

        article_lookup_form = ArticleLookupForm( request_IN.POST )
        article_id = request_IN.POST.get( "article_id", -1 )
        is_form_ready = True
        
    elif ( request_IN.method == 'GET' ):
    
        article_lookup_form = ArticleLookupForm( request_IN.GET )
        article_id = request_IN.GET.get( "article_id", -1 )
        is_form_ready = True
        
    #-- END check to see request type so we initialize form correctly. --#
    
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
                            rendered_article_html += "\n        <tr><td>" + unicode( paragraph_number ) + "</td><td>" + p_tag_html + "</td></tr>"
                        
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
    response_OUT = render_to_response( default_template, response_dictionary, context_instance = my_context_instance )

    return response_OUT

#-- END view method article_view() --#


@login_required
def article_view_article_data( request_IN ):

    #return reference
    response_OUT = None

    # declare variables
    me = "article_view_coding"
    my_context_instance = None
    response_dictionary = {}
    default_template = ''
    request_inputs = None
    article_lookup_form = None
    is_form_ready = False
    article_id = -1
    article_data_qs = None
    article_data_count = -1
    article_data_instance = None
    article_data_list = []
    
    # devlare variables - for selecting specific article_data to output.
    article_data_select_form = None
    article_data_id_list = []

    # configure context instance
    my_context_instance = RequestContext( request_IN )
    
    # initialize response dictionary
    response_dictionary = {}
    response_dictionary.update( csrf( request_IN ) )
    response_dictionary[ 'article_instance' ] = None
    response_dictionary[ 'article_text' ] = None

    # set my default rendering template
    default_template = 'articles/article-view-article-data.html'

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
            
            # Article ID retrieved above
            # get article ID.
            #article_id = request_IN.POST.get( "article_id", -1 )

            # retrieve QuerySet of Article_Data related to article.
            article_data_qs = Article_Data.objects.filter( article_id = article_id )

            # get count of queryset return items
            if ( ( article_data_qs != None ) and ( article_data_qs != "" ) ):

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
    response_OUT = render_to_response( default_template, response_dictionary, context_instance = my_context_instance )

    return response_OUT

#-- END view method article_view_coding() --#


@login_required
def article_code( request_IN ):

    # return reference
    response_OUT = None

    # declare variables
    me = "article_code"
    logger_name = ""
    debug_message = ""
    my_context_instance = None
    response_dictionary = {}
    default_template = ''
    article_lookup_form = None
    is_form_ready = False
    request_data = None
    article_id = -1
    article_qs = None
    article_count = -1
    article_instance = None
    article_paragraph_list = None
    
    # declare variables - coding submission.
    person_store_json_string = ""
    coder_user = None
    article_data_qs = None
    article_data_count = -1
    article_data_instance = None
    article_data_id = -1
    article_data_id_list = []
    is_ok_to_process_coding = True
    manual_article_coder = None
    result_article_data = None
    coding_status = ""
    new_person_store_json = None
    new_person_store_json_string = ""
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

    # configure context instance
    my_context_instance = RequestContext( request_IN )
    
    # initialize response dictionary
    response_dictionary = {}
    response_dictionary.update( csrf( request_IN ) )
    response_dictionary[ 'article_instance' ] = None
    response_dictionary[ 'article_text' ] = None
    response_dictionary[ 'base_hide_navigation' ] = True
    response_dictionary[ 'person_type_subject' ] = ManualArticleCoder.PERSON_TYPE_SUBJECT
    response_dictionary[ 'person_type_source' ] = ManualArticleCoder.PERSON_TYPE_SOURCE
    response_dictionary[ 'person_type_author' ] = ManualArticleCoder.PERSON_TYPE_AUTHOR
    response_dictionary[ 'existing_person_store_json' ] = ""
    response_dictionary[ 'page_status_message_list' ] = page_status_message_list

    # set my default rendering template
    default_template = 'articles/article-code.html'

    # init coding status variables
    # start with it being OK to process coding.
    is_ok_to_process_coding = True
    
    # do we have input parameters?
    if ( request_IN.method == 'POST' ):

        request_data = request_IN.POST
        is_form_ready = True
        
    elif ( request_IN.method == 'GET' ):
    
        request_data = request_IN.GET
        is_form_ready = True
        
    #-- END check to see request type so we initialize form correctly. --#
    
    # set up form objects.

    # make instance of person_lookup_form.
    person_lookup_form = ArticleCodingForm()
    
    # make instance of article coding submission form.
    coding_submit_form = ArticleCodingSubmitForm( request_data )

    # make instance of ArticleLookupForm
    article_lookup_form = ArticleLookupForm( request_data )

    # store the article ID if passed in.
    article_id = request_data.get( "article_id", -1 )

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

        else:

            # not greater than 1, so 0 or negative (!).  OK to process.
            #is_ok_to_process_coding = True
            pass

        #-- END check to see if greater than 1. --#

    #-- END dealing with either 0 or > 1 Article_Data --#

    # form ready?
    if ( is_form_ready == True ):
    
        # !TODO - process coding submission
        if ( coding_submit_form.is_valid() == True ):

            # it is valid - retrieve person_store_json and article_data_id
            person_store_json_string = request_data.get( "person_store_json", "" )

            # got any JSON?
            person_store_json_string = person_store_json_string.strip()
            if ( ( person_store_json_string is None ) or ( person_store_json_string == "" ) ):

                # no JSON - no need to process coding.
                is_ok_to_process_coding = False

            #-- END check to see if we have any JSON --#
                        
            # OK to process coding?
            if ( is_ok_to_process_coding == True ):

                # process JSON with instance of ManualArticleCoder
                manual_article_coder = ManualArticleCoder()
                
                # need to get call set up for new parameters.
                article_data_instance = manual_article_coder.process_person_store_json( article_instance,
                                                                                        current_user,
                                                                                        person_store_json_string,
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

                        # !TODO - success - short circuit article lookup - use empty
                        #    copy of form - after successful posting of data, place
                        #    empty ArticleLookupForm() in article_lookup_form so you
                        #    don't reload the same article automatically (want to keep
                        #    people from coding twice).
                        #article_lookup_form = ArticleLookupForm()

                        # also empty out article_data_instance, so no JSON output.
                        #article_data_instance = None

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

            #-- END check to see if OK to process coding. --#
            
        #-- END check to see if coding form is valid. --#

        # got article_data?
        if ( article_data_instance is not None ):

            # convert to JSON and store in response dictionary
            new_person_store_json = ManualArticleCoder.convert_article_data_to_person_store_json( article_data_instance )
            new_person_store_json_string = json.dumps( new_person_store_json )
            response_dictionary[ 'existing_person_store_json' ] = new_person_store_json_string

        #-- END check to see if we have an Article_Data instance --#

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
                            rendered_article_html += "\n        <tr><td>" + unicode( paragraph_number ) + "</td><td>" + p_tag_html + "</td></tr>"
                        
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
    response_OUT = render_to_response( default_template, response_dictionary, context_instance = my_context_instance )

    return response_OUT

#-- END view method article_code() --#


@login_required
def output_articles( request_IN ):

    #return reference
    response_OUT = None

    # declare variables
    me = "output_articles"
    my_context_instance = None
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
    
    # configure context instance
    my_context_instance = RequestContext( request_IN )
    
    # initialize response dictionary
    response_dictionary = {}
    response_dictionary.update( csrf( request_IN ) )

    # set my default rendering template
    default_template = 'sourcenet_output_articles.html'

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
                response_OUT = render_to_response( default_template, response_dictionary, context_instance = my_context_instance )
                
            else:
            
                # is None.  error.
                response_dictionary[ 'output_string' ] = "ERROR - network query set is None."
                response_dictionary[ 'article_select_form' ] = article_select_form
                response_dictionary[ 'output_type_form' ] = output_type_form
                response_OUT = render_to_response( default_template, response_dictionary, context_instance = my_context_instance )
            
            #-- END check to see if query set is None --#
            '''
            # is None.  error.
            response_dictionary[ 'output_string' ] = "debug - " + str( type( network_query_set ) ) + " - " + str( network_query_set )
            response_dictionary[ 'article_select_form' ] = article_select_form
            response_dictionary[ 'output_type_form' ] = output_type_form
            response_OUT = render_to_response( default_template, response_dictionary, context_instance = my_context_instance )
            '''
            
        else:

            # not valid - render the form again
            response_dictionary[ 'article_select_form' ] = article_select_form
            response_dictionary[ 'output_type_form' ] = output_type_form
            response_OUT = render_to_response( default_template, response_dictionary, context_instance = my_context_instance )

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
        response_OUT = render_to_response( default_template, response_dictionary, context_instance = my_context_instance )

    #-- END check to see if new request or POST --#


    return response_OUT

#-- END view method output_articles() --#


@login_required
def output_network( request_IN ):

    #return reference
    response_OUT = None

    # declare variables
    me = "output_network"
    my_context_instance = None
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

    # configure context instance
    my_context_instance = RequestContext( request_IN )
    
    # initialize response dictionary
    response_dictionary = {}
    response_dictionary.update( csrf( request_IN ) )

    # set my template
    default_template = 'sourcenet_output_network.html'
    
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
                response_OUT = render_to_response( default_template, response_dictionary, context_instance = my_context_instance )
                
            #-- END check to see if we return result as a file --#

        else:

            # not valid - render the form again
            response_dictionary[ 'output_string' ] = "Invalid Form"
            response_dictionary[ 'article_select_form' ] = article_select_form
            response_dictionary[ 'network_output_form' ] = network_output_form
            response_dictionary[ 'person_select_form' ] = person_select_form
            response_dictionary[ 'relation_select_form' ] = relation_select_form
            response_OUT = render_to_response( default_template, response_dictionary, context_instance = my_context_instance )

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
        response_OUT = render_to_response( default_template, response_dictionary, context_instance = my_context_instance )

    #-- END check to see if new request or POST --#


    return response_OUT

#-- END view method output_network() --#
