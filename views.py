#===============================================================================
# imports (in alphabetical order by package, then by name)
#===============================================================================

# import Python libraries for CSV output
#import csv
#import StringIO
#import pickle

# include the django conf settings
#from django.conf import settings

# django core imports
#from django.core.urlresolvers import reverse

# Import objects from the django.http library.
#from django.http import Http404
#from django.http import HttpResponse
#from django.http import HttpResponseRedirect

# import the render_to_response() method from django.shortcuts
#from django.shortcuts import get_object_or_404
from django.shortcuts import render_to_response

# import django template code
#from django.template import Context
#from django.template import loader
from django.template import RequestContext

# Import the form class for network output
from research.sourcenet.forms import ArticleSelectForm
from research.sourcenet.forms import ArticleOutputTypeSelectForm
from research.sourcenet.forms import PersonSelectForm
from research.sourcenet.forms import NetworkOutputForm

# import class that actually processes requests for outputting networks.
from research.sourcenet.export.network_output import NetworkOutput

# Import the classes for our SourceNet application
#from mysite.sourcenet.models import Article
#from mysite.sourcenet.models import Article_Author
#from mysite.sourcenet.models import Article_Source
#from mysite.sourcenet.models import Person
#from mysite.sourcenet.models import Topic


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

#-- end method detail() --------------------------------------------------------


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

#-- end method index() ---------------------------------------------------------


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

#-- end method results() -------------------------------------------------------


def output_articles( request_IN ):

    #return reference
    response_OUT = None

    # declare variables
    default_template = ''
    article_select_form = None
    output_type_form = None
    response_dictionary = {}
    output_string = ''
    network_outputter = None
    current_item = None
    network_query_set = None
    article_count = ''
    query_counter = ''

    # set my default rendering template
    default_template = 'sourcenet/output.html'

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
            article_count = network_query_set.count()

            output_string += "\n\nTotal articles returned: " + str( article_count ) + "\n\n\n"

            # loop over the query set.
            query_counter = 0
            for current_item in network_query_set:
                query_counter += 1
                output_string += "- ( " + str( query_counter ) + " ) " + current_item.headline + "\n"

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
            response_OUT = render_to_response( default_template, response_dictionary, context_instance = RequestContext( request_IN ) )

        else:

            # not valid - render the form again
            response_dictionary[ 'article_select_form' ] = article_select_form
            response_dictionary[ 'output_type_form' ] = output_type_form
            response_OUT = render_to_response( default_template, response_dictionary, context_instance = RequestContext( request_IN ) )

        #-- END check to see whether or not form is valid. --#

    else:
    
        # new request, make an empty instance of network output form.
        article_select_form = ArticleSelectForm()
        output_type_form = ArticleOutputTypeSelectForm()
        response_dictionary[ 'article_select_form' ] = article_select_form
        response_dictionary[ 'output_type_form' ] = output_type_form

        # declare variables
        response_OUT = render_to_response( default_template, response_dictionary, context_instance = RequestContext( request_IN ) )

    #-- END check to see if new request or POST --#


    return response_OUT

#-- END method output_articles() -------------------------------------------------------


def output_network( request_IN ):

    #return reference
    response_OUT = None

    # declare variables
    default_template = ''
    article_select_form = None
    network_output_form = None
    person_select_form = None
    response_dictionary = {}
    output_string = ''
    network_outputter = None
    current_item = None
    network_query_set = None
    article_count = ''
    query_counter = ''

    # set my teplate
    default_template = 'sourcenet/output_network.html'

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

            # initialize the NetworkOutput instance.
            network_outputter = NetworkOutput()
            network_outputter.set_request( request_IN )

            # For now, output plain string
            output_string = network_outputter.debug_parameters()

            #-------------------------------------------------------------------
            # summary info.
            #-------------------------------------------------------------------

            # retrieve article QuerySet based on parameters passed in.
            network_query_set = network_outputter.create_network_query_set()

            # get count of queryset return items
            article_count = network_query_set.count()

            output_string += "\n\nTotal articles returned: " + str( article_count ) + "\n\n\n"

            # loop over the query set.
            query_counter = 0
            for current_item in network_query_set:

                query_counter += 1
                output_string += "- ( " + str( query_counter ) + " ) " + current_item.headline + "\n"

            #-- END loop over articles to list out headlines. --#

            # render and output networkd data.
            output_string += "\n\n"
            output_string += "=======================\n"
            output_string += "network data output:\n"
            output_string += "=======================\n"
            output_string += network_outputter.render_network_data( network_query_set )
            output_string += "=======================\n"
            output_string += "END network data output\n"
            output_string += "=======================\n"

            # Prepare parameters for view.
            response_dictionary[ 'output_string' ] = output_string
            response_dictionary[ 'article_select_form' ] = article_select_form
            response_dictionary[ 'network_output_form' ] = network_output_form
            response_dictionary[ 'person_select_form' ] = person_select_form
            response_OUT = render_to_response( default_template, response_dictionary, context_instance = RequestContext( request_IN ) )

        else:

            # not valid - render the form again
            response_dictionary[ 'article_select_form' ] = article_select_form
            response_dictionary[ 'network_output_form' ] = network_output_form
            response_dictionary[ 'person_select_form' ] = person_select_form
            response_OUT = render_to_response( default_template, response_dictionary, context_instance = RequestContext( request_IN ) )

        #-- END check to see whether or not form is valid. --#

    else:

        # new request, make an empty instance of network output form.
        article_select_form = ArticleSelectForm()
        network_output_form = NetworkOutputForm()
        person_select_form = PersonSelectForm()
        response_dictionary[ 'article_select_form' ] = article_select_form
        response_dictionary[ 'network_output_form' ] = network_output_form
        response_dictionary[ 'person_select_form' ] = person_select_form

        # declare variables
        response_OUT = render_to_response( default_template, response_dictionary, context_instance = RequestContext( request_IN ) )

    #-- END check to see if new request or POST --#


    return response_OUT

#-- END method output_network() -------------------------------------------------------