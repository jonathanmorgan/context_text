# sourcenet

sourcenet is a django application for capturing and analyzing networks of news based on articles.

## Installation and configuration

- required python modules (install with pip):

    - nameparser - `(sudo) pip install nameparser`
    - django - `(sudo) pip install django` (1.6.X preferred, latest 1.4.X or 1.5.X should work, too)
    - beautiful soup 4 - `(sudo) pip install beautifulsoup4`
    - south - `(sudo) pip install south`

### Install "research" django project

- install a django project named "research".

    - In the folder where you want your project, run:

            django-admin.py startproject research

    - This creates the following folder structure and files (among others):

            /research
                manage.py
                /research
                    settings.py

    - move sourcenet into your django application directory using the git program to clone it from github:

            git clone https://github.com/jonathanmorgan/sourcenet.git

    - If you might want to try to run the newsbank collector, you'll also need python\_utilities.  Clone python\_utilities into the research folder alongside sourcenet:

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

    - add 'sourcenet' to your list of INSTALLED\_APPS:

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
                'sourcenet',
            )

    - Initialize the sourcenet tables using south:
    
            python manage.py migrate sourcenet

### Enable django admins:
        
- you need to install a web server on your machine (apache works well).

- configure it so it can run python WSGI applications.  For apache, install mod_wsgi:

        (sudo) apt-get install libapache2-mod-wsgi

- configure your web server so it knows of research/research/wsgi.py.  If apache, add something like this to the apache config (in ubuntu, for example, I'd put it in `/etc/apache2/conf.d`, in a file named `django-sourcenet`):

        WSGIDaemonProcess sourcenet-1 threads=10 display-name=%{GROUP}
        WSGIProcessGroup sourcenet-1
        WSGIScriptAlias /sourcenet <path_to_django_project>/research/research/wsgi.py
        
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

    - place this file in /etc/apache2/conf-available, naming it "django-sourcenet.conf".
    
    - make sure to uncomment `Require all granted` in the file above, and comment out `Allow from all`.
    
    - enable it with the a2enconf command:

            (sudo) a2enconf django-sourcenet

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

        http://<your_server>/sourcenet/admin/

### Enable sourcenet network data output pages

- get the admins working.

- add a line to enable the sourcenet URLs (in `research.sourcenet.urls`) to the urlpatterns structure.

    - Add:

            url( r'^sourcenet/', include( 'sourcenet.urls' ) ),

    - Result:

            urlpatterns = patterns('',
                # Examples:
                # url(r'^$', 'research.views.home', name='home'),
                # url(r'^research/', include('research.foo.urls')),
                url( r'^sourcenet/', include( 'sourcenet.urls' ) ),
            
                # Uncomment the admin/doc line below to enable admin documentation:
                url( r'^admin/doc/', include( 'django.contrib.admindocs.urls' ) ),
            
                # Uncomment the next line to enable the admin:
                url( r'^admin/', include( admin.site.urls ) ),
            )
            
#### Test!

- test by going to the URL:

        http://<your_server>/sourcenet/sourcenet/output/network

## Collecting Articles

There is an example application in sourcenet/collectors/newsbank that you can use as a template for how to gather data and then store it in the database.  It interacts with the newsbank web database, using BeautifulSoup to parse and extract article data.

## Coding articles:

To code articles by hand, use the django admin pages (access to which should have been enabled once you configured your web server so it knows of the wsgi.py file above).  The article model's admin page has been implemented so it is relatively easy to use to code articles, and if you want to refine or alter what is collected, you can alter it in sourcenet/admins.py.

A draft content analysis protocol for assessing sources in a way that can be used to generate network data is in sourcenet/protocol/sourcenet_CA_protocol.pdf.

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

Once you have coded your articles, you can output network data from them by going to the web page `http://<your_server>/sourcenet/sourcenet/output/network`.  This page outputs a form that lets you select articles and people to include in your network, then will output network data based on what you select.

- If you are generating multiple network slices across time periods, you will want to use the "Select People" section of the form (on the right) and enter a fancy date range that includes each date range for all of the slices you are making, so the matrices that result are of the same dimensions (same set of people for each - all people in all slices).

- Syntax for fancy date range fields: For date range fields, enter any number of paired date ranges, where dates are in the format YYYY-MM-DD, dates are separated by the string " to ", and each pair of dates is separated by two pipes ("||").

        Example: 2009-12-01 to 2009-12-31||2010-02-01 to 2010-02-28

## License

Copyright 2010-2013 Jonathan Morgan

This file is part of [http://github.com/jonathanmorgan/sourcenet](http://github.com/jonathanmorgan/sourcenet).

sourcenet is free software: you can redistribute it and/or modify
it under the terms of the GNU Lesser General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

sourcenet is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU Lesser General Public License
along with [http://github.com/jonathanmorgan/sourcenet](http://github.com/jonathanmorgan/sourcenet).  If not, see
[http://www.gnu.org/licenses/](http://www.gnu.org/licenses/).