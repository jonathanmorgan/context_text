from __future__ import unicode_literals

'''
Copyright 2010-2015 Jonathan Morgan

This file is part of http://github.com/jonathanmorgan/context_text.

context_text is free software: you can redistribute it and/or modify it under the terms of the GNU Lesser General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.

context_text is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.

You should have received a copy of the GNU Lesser General Public License along with http://github.com/jonathanmorgan/context_text. If not, see http://www.gnu.org/licenses/.
'''

# import djanfgo.conf.urls.defaults stuff.
#from django.conf.urls.defaults import *
from django.conf.urls import include
from django.conf.urls import url

# and import stuff to use the admin's login page for all authentication.
from django.contrib.auth import views as auth_views

# import polls from mysite
import context_text.views
from context_text.models import Article

'''
# !tastypie API
# import tastypie stuff, so we can make REST-ful API
from tastypie.api import Api
from context_text.tastypie_api.context_text_api import ArticleResource

# initialize context_text API, v1
v1_api = Api( api_name='v1' )

# register resources
v1_api.register( ArticleResource() )
'''

# context_text URL settings, intended to be included in master urls.py file.
urlpatterns = [

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
    
    # index page
    url( r'^index$', context_text.views.index, name = "context_text-index" ),

    # left in all the stuff above as a sample.  Making an output view, to let a
    #    user specify what they want in output, and then an output/display view
    #    to display the results of the rendering.
    url( r'^output/network$', context_text.views.output_network, name = "context_text-output_network" ),
    url( r'^output/articles$', context_text.views.output_articles, name = "context_text-output_articles" ),
    #( r'^output/display$', 'mysite.context_text.views.output_display'),

    # link the default authentication page to the admin login page.
    #url( r'^accounts/login/$', auth_views.LoginView.as_view( template_name = "registration/login.html" ), name = "context_text-login" ),
    
    # created a view to log people out that redirects to server root.    
    #url( r'^accounts/logout/$', context_text.views.logout, name = "context_text-logout" ),

    # article views
    url( r'^article/view/$', context_text.views.article_view, name = "context_text-article_view" ),
    url( r'^article/article_data/view/$', context_text.views.article_view_article_data, name = "context_text-article_view_article_data" ),
    url( r'^article/article_data/view_with_text/$', context_text.views.article_view_article_data_with_text, name = "context_text-article_view_article_data_with_text" ),

    # filter and process articles
    url( r'^article/filter/$', context_text.views.filter_articles, name = "context_text-filter_articles" ),    
    
    # article coding pages
    url( r'^article/code/list/', context_text.views.article_coding_list, name = "context_text-article_coding_list" ),
    url( r'^article/code/view/ambiguities/', context_text.views.article_coding_view_person_ambiguities, name = "context_text-article_coding_view_person_ambiguities" ),
    url( r'^article/code/', context_text.views.article_code, name = "context_text-article_code" ),

    # filter and process Person records
    url( r'^person/filter/$', context_text.views.person_filter, name = "context_text-person_filter" ),
    url( r'^person/merge/$', context_text.views.person_merge, name = "context_text-person_merge" ),
    
    # Article_Data
    url( r'^article_data/filter/$', context_text.views.article_data_filter, name = "context_text-article_data_filter" ),
    
]