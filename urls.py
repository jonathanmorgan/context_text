'''
Copyright 2010-2013 Jonathan Morgan

This file is part of http://github.com/jonathanmorgan/sourcenet.

sourcenet is free software: you can redistribute it and/or modify it under the terms of the GNU Lesser General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.

sourcenet is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.

You should have received a copy of the GNU Lesser General Public License along with http://github.com/jonathanmorgan/sourcenet. If not, see http://www.gnu.org/licenses/.
'''

# import djanfgo.conf.urls.defaults stuff.
#from django.conf.urls.defaults import *
from django.conf.urls.defaults import patterns
from django.conf.urls.defaults import url

# import polls from mysite
from sourcenet.models import Article

# polls-specific URL settings, intended to be included in master urls.py file.
#urlpatterns = patterns( 'mysite.polls.views',
urlpatterns = patterns( '',
    # Example:
    # (r'^mysite/', include('mysite.foo.urls')),

    # migrated from master urls.py, so left in old lines to show how I changed
    #    it, just commented them out.
    # And now, abstracting out to generic views, so commenting and changing
    #    again.

    #( r'^polls/$', 'mysite.polls.views.index' ),
    #( r'^$', 'index' ),
    #( r'^$', 'django.views.generic.list_detail.object_list', info_dict ),

    #( r'^polls/(?P<poll_id_IN>\d+)/$', 'mysite.polls.views.detail' ),
    #( r'^(?P<poll_id_IN>\d+)/$', 'detail' ),
    #( r'^(?P<object_id>\d+)/$', 'django.views.generic.list_detail.object_detail', info_dict ),

    #( r'^polls/(?P<poll_id_IN>\d+)/results/$', 'mysite.polls.views.results' ),
    #( r'^(?P<poll_id_IN>\d+)/results/$', 'results' ),
    #url( r'^(?P<object_id>\d+)/results/$', 'django.views.generic.list_detail.object_detail', dict( info_dict, template_name='polls/results.html' ), 'poll_results'),

    #( r'^polls/(?P<poll_id_IN>\d+)/vote/$', 'mysite.polls.views.vote' ),
    #( r'^(?P<poll_id_IN>\d+)/vote/$', 'vote' ),
    #( r'^(?P<poll_id_IN>\d+)/vote/$', 'mysite.polls.views.vote'),

    # Uncomment the admin/doc line below and add 'django.contrib.admindocs'
    # to INSTALLED_APPS to enable admin documentation:
    # (r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    #(r'^admin/', include(admin.site.urls)),

    # left in all the stuff above as a sample.  Making an output view, to let a
    #    user specify what they want in output, and then an output/display view
    #    to display the results of the rendering.
    ( r'^output/network$', 'sourcenet.views.output_network'),
    ( r'^output/articles$', 'sourcenet.views.output_articles'),
    #( r'^output/display$', 'mysite.sourcenet.views.output_display'),

)