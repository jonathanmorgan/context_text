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
#from StringIO import StringIO
#import pickle

# import django authentication code.
from django.contrib import auth
from django.contrib.auth.decorators import login_required

# include the django conf settings
#from django.conf import settings

# django core imports

# import django code for csrf security stuff.
from django.core.context_processors import csrf

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

# Import the form class for network output
from sourcenet.forms import ArticleLookupForm
from sourcenet.forms import ArticleOutputTypeSelectForm
from sourcenet.forms import ArticleSelectForm
from sourcenet.forms import PersonSelectForm
from sourcenet.forms import NetworkOutputForm

# import class that actually processes requests for outputting networks.
from sourcenet.export.network_output import NetworkOutput

# Import the classes for our SourceNet application
from sourcenet.models import Article
#from sourcenet.models import Article_Author
#from sourcenet.models import Article_Source
#from sourcenet.models import Person
#from sourcenet.models import Topic


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
            article_id = request_IN.POST.get( "article_id", -1 )

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
                    
                    # seed response dictionary.
                    response_dictionary[ 'article_instance' ] = article_instance
                    response_dictionary[ 'article_text' ] = article_text
                    response_dictionary[ 'article_lookup_form' ] = article_lookup_form
                    
                else:
                
                    # error - none or multiple articles found for ID. --#
                    print( "No article returned for ID passed in." )
                    response_dictionary[ 'output_string' ] = "ERROR - no QuerySet returned from call to filter().  This is odd."
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
def article_code( request_IN ):

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
    
    # configure context instance
    my_context_instance = RequestContext( request_IN )
    
    # initialize response dictionary
    response_dictionary = {}
    response_dictionary.update( csrf( request_IN ) )
    response_dictionary[ 'article_instance' ] = None
    response_dictionary[ 'article_text' ] = None

    # set my default rendering template
    default_template = 'articles/article-code.html'

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
            article_id = request_IN.POST.get( "article_id", -1 )

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
                    
                    # seed response dictionary.
                    response_dictionary[ 'article_instance' ] = article_instance
                    response_dictionary[ 'article_text' ] = article_text
                    response_dictionary[ 'article_lookup_form' ] = article_lookup_form
                    
                else:
                
                    # error - none or multiple articles found for ID. --#
                    print( "No article returned for ID passed in." )
                    response_dictionary[ 'output_string' ] = "ERROR - no QuerySet returned from call to filter().  This is odd."
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
    article_select_form = None
    network_output_form = None
    person_select_form = None
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

        # is all our form data OK?
        if ( ( article_select_form.is_valid() == True ) and ( network_output_form.is_valid() == True ) and ( person_select_form.is_valid() == True ) ):

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

            # get count of queryset return items
            if ( network_query_set is not None ):
            
                article_data_count = network_query_set.count()
                
            else:
            
                article_data_count = -1
                
            #-- END check to see if None --#

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
            
            # render the actual network data.
            output_string += network_outputter.render_network_data( network_query_set )

            # include render details?
            if ( include_render_details == True ):

                output_string += "=======================\n"
                output_string += "END network data output\n"
                output_string += "=======================\n"
    
            #-- END check to see if we output render details --#

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
                response_OUT = render_to_response( default_template, response_dictionary, context_instance = my_context_instance )
                
            #-- END check to see if we return result as a file --#

        else:

            # not valid - render the form again
            response_dictionary[ 'output_string' ] = "Invalid Form"
            response_dictionary[ 'article_select_form' ] = article_select_form
            response_dictionary[ 'network_output_form' ] = network_output_form
            response_dictionary[ 'person_select_form' ] = person_select_form
            response_OUT = render_to_response( default_template, response_dictionary, context_instance = my_context_instance )

        #-- END check to see whether or not form is valid. --#

    else:

        # new request, make an empty instance of network output form.
        article_select_form = ArticleSelectForm()
        network_output_form = NetworkOutputForm()
        person_select_form = PersonSelectForm()
        response_dictionary[ 'article_select_form' ] = article_select_form
        response_dictionary[ 'network_output_form' ] = network_output_form
        response_dictionary[ 'person_select_form' ] = person_select_form
        
        # add on the "me" property.
        response_dictionary[ 'current_view' ] = me        

        # declare variables
        response_OUT = render_to_response( default_template, response_dictionary, context_instance = my_context_instance )

    #-- END check to see if new request or POST --#


    return response_OUT

#-- END view method output_network() --#