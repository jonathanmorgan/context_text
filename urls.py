from __future__ import unicode_literals

'''
Copyright 2010-2015 Jonathan Morgan

This file is part of http://github.com/jonathanmorgan/sourcenet.

sourcenet is free software: you can redistribute it and/or modify it under the terms of the GNU Lesser General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.

sourcenet is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.

You should have received a copy of the GNU Lesser General Public License along with http://github.com/jonathanmorgan/sourcenet. If not, see http://www.gnu.org/licenses/.
'''

# import djanfgo.conf.urls.defaults stuff.
#from django.conf.urls.defaults import *
from django.conf.urls import patterns
from django.conf.urls import include
from django.conf.urls import url

# and import stuff to use the admin's login page for all authentication.
from django.contrib.auth import views as auth_views

# import polls from mysite
from sourcenet.models import Article

'''
# !tastypie API
# import tastypie stuff, so we can make REST-ful API
from tastypie.api import Api
from sourcenet.tastypie_api.sourcenet_api import ArticleResource

# initialize sourcenet API, v1
v1_api = Api( api_name='v1' )

# register resources
v1_api.register( ArticleResource() )
'''

# polls-specific URL settings, intended to be included in master urls.py file.
#urlpatterns = patterns( 'mysite.polls.views',
urlpatterns = patterns( '',
    # Example:
    # url(r'^mysite/', include('mysite.foo.urls')),

    # migrated from master urls.py, so left in old lines to show how I changed
    #    it, just commented them out.
    # And now, abstracting out to generic views, so commenting and changing
    #    again.

    #url( r'^polls/$', 'mysite.polls.views.index' ),
    #url( r'^$', 'index' ),
    #url( r'^$', 'django.views.generic.list_detail.object_list', info_dict ),

    #url( r'^polls/(?P<poll_id_IN>\d+)/$', 'mysite.polls.views.detail' ),
    #url( r'^(?P<poll_id_IN>\d+)/$', 'detail' ),
    #url( r'^(?P<object_id>\d+)/$', 'django.views.generic.list_detail.object_detail', info_dict ),

    #url( r'^polls/(?P<poll_id_IN>\d+)/results/$', 'mysite.polls.views.results' ),
    #url( r'^(?P<poll_id_IN>\d+)/results/$', 'results' ),
    #url( r'^(?P<object_id>\d+)/results/$', 'django.views.generic.list_detail.object_detail', dict( info_dict, template_name='polls/results.html' ), 'poll_results'),

    #url( r'^polls/(?P<poll_id_IN>\d+)/vote/$', 'mysite.polls.views.vote' ),
    #url( r'^(?P<poll_id_IN>\d+)/vote/$', 'vote' ),
    #url( r'^(?P<poll_id_IN>\d+)/vote/$', 'mysite.polls.views.vote'),

    # Uncomment the admin/doc line below and add 'django.contrib.admindocs'
    # to INSTALLED_APPS to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    #url(r'^admin/', include(admin.site.urls)),

    # left in all the stuff above as a sample.  Making an output view, to let a
    #    user specify what they want in output, and then an output/display view
    #    to display the results of the rendering.
    url( r'^output/network$', 'sourcenet.views.output_network'),
    url( r'^output/articles$', 'sourcenet.views.output_articles'),
    #( r'^output/display$', 'mysite.sourcenet.views.output_display'),

    # link the default authentication page to the admin login page.
    url( r'^accounts/login/$', auth_views.login ),
    
    # created a view to log people out that redirects to server root.    
    url( r'^accounts/logout/$', 'sourcenet.views.logout' ),

    # article views
    url( r'^article/view/$', 'sourcenet.views.article_view' ),
    url( r'^article/article_data/view/$', 'sourcenet.views.article_view_article_data' ),

    # article coding page
    url( r'^article/code/', 'sourcenet.views.article_code' ),

    # !tastypie API
    # APIs
    #url( r'^api/', include( v1_api.urls) ),

)
