<!-- TOC -->

# context_text

context_text is a django application for capturing and analyzing networks of news based on articles.

## Installation and configuration

- required python modules (install with pip):

    - nameparser - `(sudo) pip install nameparser`
    - django - `(sudo) pip install django` (1.6.X preferred, latest 1.4.X or 1.5.X should work, too)
    - beautiful soup 4 - `(sudo) pip install beautifulsoup4`
    - south - `(sudo) pip install south`
    - django-ajax-selects

### Install "research" django project

- install a django project named "research".

    - In the folder where you want your project, run:

            django-admin.py startproject research

    - This creates the following folder structure and files (among others):

            /research
                manage.py
                /research
                    settings.py

    - move context_text into your django application directory using the git program to clone it from github:

            git clone https://github.com/jonathanmorgan/context_text.git

    - If you might want to try to run the newsbank collector, you'll also need python\_utilities.  Clone python\_utilities into the research folder alongside context_text:

            git clone https://github.com/jonathanmorgan/python_utilities.git

### Configure database, applications:

- in research/research/settings.py:

    - Edit the research/research/settings.py file and update it with details of your database configuration
    
        - [https://docs.djangoproject.com/en/dev/intro/tutorial01/#database-setup](https://docs.djangoproject.com/en/dev/intro/tutorial01/#database-setup)
        - [https://docs.djangoproject.com/en/dev/ref/settings/#databases](https://docs.djangoproject.com/en/dev/ref/settings/#databases)

    - add 'south' to your list of INSTALLED\_APPS:

            INSTALLED_APPS = (
                'django.contrib.auth',
                'django.contrib.contenttypes',
                'django.contrib.sessions',
                'django.contrib.sites',
                'django.contrib.messages',
                'django.contrib.staticfiles',
                # Uncomment the next line to enable the admin:
                # 'django.contrib.admin',
                # Uncomment the next line to enable admin documentation:
                # 'django.contrib.admindocs',
                'south',
            )

    - initialize the database - go into directory where manage.py is installed, and run `python manage.py syncdb`.
    
        - In django 1.6, the django.contrib.admin application will already be uncommented by default, so you'll have to make an admin user at this point, as well.  You should do this now, make a note of username and password.  You'll need it later.

    - add 'context_text' to your list of INSTALLED\_APPS:

            INSTALLED_APPS = (
                'django.contrib.auth',
                'django.contrib.contenttypes',
                'django.contrib.sessions',
                'django.contrib.sites',
                'django.contrib.messages',
                'django.contrib.staticfiles',
                # Uncomment the next line to enable the admin:
                # 'django.contrib.admin',
                # Uncomment the next line to enable admin documentation:
                # 'django.contrib.admindocs',
                'south',
                'context_text',
            )

    - Initialize the context_text tables using south:
    
            python manage.py migrate context_text

### Enable django admins:
        
- you need to install a web server on your machine (apache works well).

- configure it so it can run python WSGI applications.  For apache, install mod_wsgi:

        (sudo) apt-get install libapache2-mod-wsgi

- configure your web server so it knows of research/research/wsgi.py.  If apache, add something like this to the apache config (in ubuntu, for example, I'd put it in `/etc/apache2/conf.d`, in a file named `django-context_text`):

        WSGIDaemonProcess context_text-1 threads=10 display-name=%{GROUP}
        WSGIProcessGroup context_text-1
        WSGIScriptAlias /context_text <path_to_django_project>/research/research/wsgi.py
        
        # Python path
        # no virualenv
        WSGIPythonPath <path_to_django_project>/research
        # virtualenv (or any other paths, each separated by colons)
        #WSGIPythonPath /path/to/mysite.com:/path/to/your/venv/lib/python2.X/site-packages
        
        <Directory <path_to_django_project>/research/research>
            <Files wsgi.py>
                Order deny,allow
                # apache 2.4:
                #Require all granted
                # apache 2.2 or earlier:
                Allow from all
            </Files>
        </Directory>

- If you are using apache 2.4 on ubuntu 13.10:

    - place this file in /etc/apache2/conf-available, naming it "django-context_text.conf".
    
    - make sure to uncomment `Require all granted` in the file above, and comment out `Allow from all`.
    
    - enable it with the a2enconf command:

            (sudo) a2enconf django-context_text

- Add a line that sets your python path to the wsgi.py file (<project_folder>/research/wsgi.py):

        sys.path.append( '<project_folder>/research' )

- More details on installing apache and mod_wsgi: [https://docs.djangoproject.com/en/dev/howto/deployment/wsgi/modwsgi/](https://docs.djangoproject.com/en/dev/howto/deployment/wsgi/modwsgi/)

- open up the `settings.py` file in `<project_folder>/research` and:

    - follow the instructions there for uncommenting lines in INSTALLED_APPLICATIONS to get the admins to work.

            # Uncomment the next line to enable the admin:
            'django.contrib.admin',
            # Uncomment the next line to enable admin documentation:
            'django.contrib.admindocs',
            
    - In django 1.6, the django.contrib.admin line should already be uncommented, and you'll have to just add the admindocs line.
            
- if 'django.contrib.admin' was commented out and you uncommented it, you'll need to initialize the database for the admins - go into directory where manage.py is installed, and run `python manage.py syncdb`.  Make a note of the admin username and password.  You'll need it to log in to the admins.
    
    - In django 1.6, the django.contrib.admin application will already be uncommented by default, so you'll have done this above.

- open up the `urls.py` file in the folder where settings.py lives and follow the instructions there for uncommenting lines to get the admins to work.

        from django.conf.urls import patterns, include, url
        
        # Uncomment the next two lines to enable the admin:
        from django.contrib import admin
        admin.autodiscover()
        
        urlpatterns = patterns('',
            # Examples:
            # url(r'^$', 'research.views.home', name='home'),
            # url(r'^research/', include('research.foo.urls')),
        
            # Uncomment the admin/doc line below to enable admin documentation:
            url(r'^admin/doc/', include('django.contrib.admindocs.urls')),
        
            # Uncomment the next line to enable the admin:
            url(r'^admin/', include(admin.site.urls)),
        )

    - In django 1.6, the admin.site.urls line should already be uncommented, and you'll have to just add the admindocs line.
        
#### Static file support:

- [https://docs.djangoproject.com/en/dev/howto/static-files/](https://docs.djangoproject.com/en/dev/howto/static-files/)

- in your web root, create a folder named "static" directly in your webroot to hold static files for applications (in ubuntu, the default webroot is /var/www):

        (sudo) mkdir static
        
- open up the `settings.py` file in `<project_folder>/research` and update the STATIC_ROOT variable so it contains the path to the "static" directory you created in teh step above.  Ubuntu example:

        STATIC_ROOT = '/var/www/static'
    
- run the following command to initialize static files for your applications (have to sudo if the folder is in webroot, owned by root):

        (sudo) python manage.py collectstatic
        
#### Test!

- test by going to the URL:

        http://<your_server>/context_text/admin/

### Enable django-ajax-selects for easy lookup of people, articles, and organizations in coding pages.

- get the admins working.

- add the following to resesarch/settings.py:

    - add 'django-ajax-selects' to your list of INSTALLED\_APPS.  Result:

            INSTALLED_APPS = (
                'django.contrib.auth',
                'django.contrib.contenttypes',
                'django.contrib.sessions',
                'django.contrib.sites',
                'django.contrib.messages',
                'django.contrib.staticfiles',
                # Uncomment the next line to enable the admin:
                # 'django.contrib.admin',
                # Uncomment the next line to enable admin documentation:
                # 'django.contrib.admindocs',
                'south',
                'context_text',
                'django-ajax-selects',
            )
        
    - add the following to the bottom of the file:
    
            AJAX_LOOKUP_CHANNELS = {

                # the simplest case, pass a DICT with the model and field to search against :
                #'track' : dict(model='music.track',search_field='title'),
                # this generates a simple channel
                # specifying the model Track in the music app, and searching against the 'title' field
            
                # or write a custom search channel and specify that using a TUPLE
                'article' : ( 'context_text.ajax-select-lookups', 'ArticleLookup' ),
                'organization' : ( 'context_text.ajax-select-lookups', 'OrganizationLookup' ),
                'person' : ( 'context_text.ajax-select-lookups', 'PersonLookup' ),
                # this specifies to look for the class `PersonLookup` in the `context_text.ajax-select-lookups` module

            }
            
            # magically include jqueryUI/js/css
            AJAX_SELECT_BOOTSTRAP = True
            AJAX_SELECT_INLINES = 'inline'    

- add the following to resesarch/urls.py to enable djang-ajax-selects URL lookups.

    - Add:

            from ajax_select import urls as ajax_select_urls
            
        and

            url( r'^context_text/', include( 'context_text.urls' ) ),

    - Example Result:

            from django.conf.urls import patterns, include, url
            
            # django-ajax-selects URLs
            from ajax_select import urls as ajax_select_urls
            
            # Uncomment the next two lines to enable the admin:
            from django.contrib import admin
            admin.autodiscover()
            
            urlpatterns = patterns('',

                # Examples:
                # url(r'^$', 'research.views.home', name='home'),
                # url(r'^research/', include('research.foo.urls')),
                
                # django-ajax-select URLs
                url( r'^admin/lookups/', include( ajax_select_urls ) ),
                
                # Uncomment the admin/doc line below to enable admin documentation:
                url( r'^admin/doc/', include( 'django.contrib.admindocs.urls' ) ),
            
                # Uncomment the next line to enable the admin:
                url( r'^admin/', include( admin.site.urls ) ),

            )
            
### Enable context_text network data output pages

- get the admins working.

- add a line to resesarch/urls.py to enable the context_text URLs (in `research.context_text.urls`) to the urlpatterns structure.

    - Add:

            url( r'^context_text/', include( 'context_text.urls' ) ),

    - Result:

            urlpatterns = patterns('',
                # Examples:
                # url(r'^$', 'research.views.home', name='home'),
                # url(r'^research/', include('research.foo.urls')),
                url( r'^context_text/', include( 'context_text.urls' ) ),
            
                # Uncomment the admin/doc line below to enable admin documentation:
                url( r'^admin/doc/', include( 'django.contrib.admindocs.urls' ) ),
            
                # Uncomment the next line to enable the admin:
                url( r'^admin/', include( admin.site.urls ) ),
            )
            
#### Test!

- test by going to the URL:

        http://<your_server>/research/context_text/output/network

## Collecting Articles

There is an example application in context_text/collectors/newsbank that you can use as a template for how to gather data and then store it in the database.  It interacts with the newsbank web database, using BeautifulSoup to parse and extract article data.

## Coding articles:

To code articles by hand, use the django admin pages (access to which should have been enabled once you configured your web server so it knows of the wsgi.py file above).  The article model's admin page has been implemented so it is relatively easy to use to code articles, and if you want to refine or alter what is collected, you can alter it in context_text/admins.py.

A draft content analysis protocol for assessing sources in a way that can be used to generate network data is in context_text/protocol/context_text_CA_protocol.pdf.

## Creating Network Data

- The Article model contains code for processing articles and creating network data from them.

    - Article.process_articles(): this method is a class method, is used to batch process articles.  It can be passed parameters in **kwargs to tell it what ranges and types of articles to process:

        - Article.PARAM\_START\_DATE - python datetime instance that has start date of date range we want to process.

        - Article.PARAM\_END\_DATE - python datetime instance that has end date of date range we want to process.

        - Article.PARAM\_SINGLE\_DATE - python datetime instance that date of articles we want to process.

    - Article.do\_automated\_processing(): the method do\_automated\_processing() is a container method for all automated processing you can do to an article.  It accepts some flags in **kwargs so you can control what you process:

        - Article.PARAM\_AUTOPROC\_ALL - if this is set to true, does all implemented automated processing.

        - Article.PARAM\_AUTOPROC\_AUTHORS - if this is set to true, processes the authors/bylines of an article.

## Outputting Network Data

Once you have coded your articles, you can output network data from them by going to the web page `http://<your_server>/research/context_text/output/network`.  This page outputs a form that lets you select articles and people to include in your network, then will output network data based on what you select.

- If you are generating multiple network slices across time periods, you will want to use the "Select People" section of the form (on the right) and enter a fancy date range that includes each date range for all of the slices you are making, so the matrices that result are of the same dimensions (same set of people for each - all people in all slices).

- Syntax for fancy date range fields: For date range fields, enter any number of paired date ranges, where dates are in the format YYYY-MM-DD, dates are separated by the string " to ", and each pair of dates is separated by two pipes ("||").

        Example: 2009-12-01 to 2009-12-31||2010-02-01 to 2010-02-28
        
- For an idea of how you can invoke the network data outputter programmatically, see the `output_network()` method in the file `views.py`.

- Parameters you can set to filter network creation can be seen on the web page for outputting network data.  If you want to interact programmatically, they are listed in the class /export/network_output.py, and you can see the expected values in the method `create_query_set()`.

    - For convenience, here is a list that was current at the time of this update of parameters you can use:
    
        - _`start_date`_ - publication date - articles will be included that were published on or after this date.
        - _`end_date`_ - publication date - articles will be included that were published on or before this date.
        - _`date_range`_ - For date range fields, enter any number of paired date ranges, where dates are in the format YYYY-MM-DD, dates are separated by the string " to ", and each pair of dates is separated by two pipes ("||").  Example: 2009-12-01 to 2009-12-31||2010-02-01 to 2010-02-28
        - _`publications`_ - list of IDs of newspapers you want included.
        - _`coders`_ - list of IDs of coders whose data you want included.
        - _`topics`_ - list of IDs of topics whose data you want included.
        - _`unique_identifiers`_ - list of unique identifiers of articles whose data you want included.
        - _`header_prefix`_ -  for output, optional prefix you want appended to front of column header names.
        - _`output_type`_ - type of output you want, currently only CSV for UCINet is supported.
        - _`allow_duplicate_articles`_ - allow duplicate articles...  Not sure this is relevant anymore.

## License

Copyright 2010-present (2014) Jonathan Morgan

This file is part of [http://github.com/jonathanmorgan/context_text](http://github.com/jonathanmorgan/context_text).

context_text is free software: you can redistribute it and/or modify
it under the terms of the GNU Lesser General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

context_text is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU Lesser General Public License
along with [http://github.com/jonathanmorgan/context_text](http://github.com/jonathanmorgan/context_text).  If not, see
[http://www.gnu.org/licenses/](http://www.gnu.org/licenses/).