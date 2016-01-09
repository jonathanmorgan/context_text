# sourcenet

<!-- TOC -->

sourcenet is a django application for capturing and analyzing networks of news based on articles.  In order for database migrations to work, you need to use 1.7.  south_migrations are present, but they won't be updated going forward.

# Installation and configuration

## OS packages

If you want to make use of a tastypie XML API for sourcenet information, you'll need to install the "lxml" python package, and to do that, you might need some operating system libraries installed so it will compile.

On Ubuntu, for example, you'll need:

- libxml2
- libxml2-dev
- libxslt1-dev

to install:

    sudo apt-get install libxml2 libxml2-dev libxslt1-dev

If you want to use a YAML API, you'll also need to install libyaml and libyaml-dev:

    sudo apt-get install libyaml-dev

## virtualenv and virtualenvwrapper

if you are on a shared or complicated server (and who isn't, really?), using virtualenv and virtualenvwrapper to create isolated python environments for specific applications can save lots of headaches.  To do this:

- Detailed documentation: [http://virtualenvwrapper.readthedocs.org/en/latest/install.html](http://virtualenvwrapper.readthedocs.org/en/latest/install.html)

- first, install virtualenv and virtualenvwrapper in all the versions of python you might use:

    - `(sudo) pip install virtualenv`
    - `(sudo) pip install virtualenvwrapper`
    
- next, you'll need to update environment variables (assuming linux, for other OS, see documentation at link above).  Add the following to your shell startup file (on ubuntu, .bashrc is invoked by .profile, so I do this in .bashrc):

        export WORKON_HOME=$HOME/.virtualenvs
        export PROJECT_HOME=$HOME/work/virtualenvwrapper-projects
        source /usr/local/bin/virtualenvwrapper.sh

- restart your shell so these settings take effect.

- use virtualenvwrapper to create a virtualenv for sourcenet:

        # for system python:
        mkvirtualenv sourcenet --no-site-packages

        # if your system python is python 3, and you want to use python 2 (since sourcenet is python 2 at the moment):
        mkvirtualenv sourcenet --no-site-packages -p /usr/bin/python2.7

- activate the virtualenv

        workon sourcenet
        
- now you are in a virtual python environment independent of the system's.  If you do this, in the examples below, you don't need to use `sudo` when you use pip, etc.

## Python packages

- required python packages (install with pip):

    - django - `(sudo) pip install django` - 1.7.X - latest 1.4.X, 1.5.X, or 1.6.X should work, too, but migrations won't - south migrations are no longer being updated.
    - nameparser - `(sudo) pip install nameparser`
    - bleach - `(sudo) pip install bleach`
    - beautiful soup 4 - `(sudo) pip install beautifulsoup4`
    - django-ajax-selects - `(sudo) pip install django-ajax-selects`
    - requests - `(sudo) pip install requests`
    - django-taggit - `(sudo) pip install django-taggit`
    - mechanize - `(sudo) pip install mechanize`
    
- depending on database:

    - postgresql - psycopg2 - Before you can connect to Postgresql with this code, you need to do the following (based on [http://initd.org/psycopg/install/](http://initd.org/psycopg/install/)):

        - install the PostgreSQL client if it isn't already installed.  On linux, you'll also need to install a few dev packages (python-dev, libpq-dev) ( [source](http://initd.org/psycopg/install/) ).
        - install the psycopg2 python package.  Install using pip (`sudo pip install psycopg2`).  
        
    - mysql - MySQL-python - Before you can connect to MySQL with this code, you need to do the following:
    
        - install the MySQL client if it isn't already installed.  On linux, you'll also need to install a few dev packages (python-dev, libmysqlclient-dev) ( [source](http://codeinthehole.com/writing/how-to-set-up-mysql-for-python-on-ubuntu/) ).
        - install the MySQLdb python package.  To install, you can either install through your operating system's package manager (ubuntu, for example, has package "python-mysqldb") or using pip (`sudo pip install MySQL-python`).


- python packages that I find helpful:

    - ipython - `(sudo) pip install ipython`

- requirements.txt contains all of these things, assumes you will use postgresql and so includes psycopg2.  To install requirements using requirements.txt:

    - `(sudo) pip install -r sourcenet/requirements.txt`
    
- Natural Language Processing (NLP):

    - To use Alchemy API, clone the `Alchemy_API` python client into your django project's root folder:
    
        - `git clone https://github.com/alchemyapi/alchemyapi_python`
        
    - To use OpenCalais's REST API, clone the pycalais git repository into your django project directory, then copy the calais folder into your django project directory:
    
        - `git clone https://github.com/ubergrape/pycalais`
        - `cp ./calais ../`
        
        - You can also use python_utilities.network.http_helper.Http_Helper to connect directly (or requests package) see the sample code in /examples/NLP/OpenCalais_API.py for more details.

- Tastypie, REST APIs, and user-friendly coding pages

    Some pages that make it easy for users to code up sourcing in articles use angular JS for presentation, and reference a REST-ful API implemented using TastyPie - [http://tastypieapi.org/](http://tastypieapi.org/).  TastyPie requires the following python packages:

    - python-mimeparse
    - python-dateutil
    - lxml
    - defusedxml
    - pyyaml
    - django-tastypie
    
    requirements-tastypie.txt contains all of these packages, can be used to install them all at once:
    
    - `(sudo) pip install -r sourcenet/requirements-tastypie.txt`

## Install "research" django project

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

    - You'll also need python\_utilities.  Clone python\_utilities into the research folder alongside sourcenet:

            git clone https://github.com/jonathanmorgan/python_utilities.git

    - And you'll need django\_config.  Clone django\_config into the research folder alongside sourcenet:

            git clone https://github.com/jonathanmorgan/django_config.git

## settings.py - Configure logging, database, applications:

The following are all changes to `research/research/settings.py`.  You'll configure logging, database information, and applications, then you'll save the file and initialize the database.  Make sure to save the file once you are done making changes.

### logging

Edit the `research/research/settings.py` file and update it with details of your logging configuration
    
- Example that logs any messages INFO and above to standard out:

        import logging

        logging.basicConfig(
            level = logging.INFO,
            format = '%(asctime)s - %(levelname)s - %(name)s - %(message)s'
        )

- Example that logs any messages INFO and above to a file:

        import logging

        logging.basicConfig(
            level = logging.INFO,
            format = '%(asctime)s - %(levelname)s - %(name)s - %(message)s',
            filename = '<log_folder>/django-sourcenet.log',
            filemode = 'w'
        )

    - WHERE `<log_folder>` is a folder that any users that will be used to interact with sourcenet have access to.  This includes the user your web server runs as (for admins and other django web pages) and the user you use to develop, and so that might run things from the python shell.

        - the easiest way to get this working:

            - make the `<log_folder>` somewhere outside the web root.
            - set the permissions on `<log_folder>` to 777.
            - create the file `django-sourcenet.log` there.
            - set its permissions also to 777.

        - This is not necessarily optimally secure, but truly securing this is beyond the scope of this README.

- You can set `level` to any of the following, which are organized from most detail (`logging.DEBUG`) to least (`logging.CRITICAL`):

    - `logging.DEBUG`
    - `logging.INFO`
    - `logging.WARNING`
    - `logging.ERROR`
    - `logging.CRITICAL`

- Python logging HOWTO: [https://docs.python.org/2/howto/logging.html](https://docs.python.org/2/howto/logging.html)
- Python logging cookbook: [https://docs.python.org/2/howto/logging-cookbook.html](https://docs.python.org/2/howto/logging-cookbook.html)

### database

Edit the research/research/settings.py file and update it with details of your database configuration
    
- [https://docs.djangoproject.com/en/dev/intro/tutorial01/#database-setup](https://docs.djangoproject.com/en/dev/intro/tutorial01/#database-setup)
- [https://docs.djangoproject.com/en/dev/ref/settings/#databases](https://docs.djangoproject.com/en/dev/ref/settings/#databases)

### applications

Edit the `research/research/settings.py` file and add 'sourcenet', 'django\_config', and 'taggit' to your list of INSTALLED\_APPS:

        INSTALLED_APPS = (
            'django.contrib.auth',
            'django.contrib.contenttypes',
            'django.contrib.sessions',
            'django.contrib.sites',
            'django.contrib.messages',
            'django.contrib.staticfiles',
            # Uncomment the next line to enable the admin:
            'django.contrib.admin',
            # Uncomment the next line to enable admin documentation:
            # 'django.contrib.admindocs',
            'sourcenet',
            'django_config',
            'taggit',
        )

- you can also add sourcenet and django_config using the new django Config classes, rather than the app name:

        INSTALLED_APPS = (
            'django.contrib.auth',
            'django.contrib.contenttypes',
            'django.contrib.sessions',
            'django.contrib.sites',
            'django.contrib.messages',
            'django.contrib.staticfiles',
            # Uncomment the next line to enable the admin:
            'django.contrib.admin',
            # Uncomment the next line to enable admin documentation:
            # 'django.contrib.admindocs',
            'sourcenet.apps.SourcenetConfig',
            'django_config.apps.Django_ConfigConfig',
            'taggit',
        )

- add settings properties that tell django how to log people in and out.

        # login configuration
        LOGIN_URL = '/sourcenet/sourcenet/accounts/login/'
        LOGIN_REDIRECT_URL = '/sourcenet/sourcenet/output/network/'
        LOGOUT_URL = '/'

- set the SESSION_COOKIE_NAME to sourcenet.

        SESSION_COOKIE_NAME = 'sourcenet'

- save the file.
    
### initialize the database

Once you've made the changes above, save the `settings.py` file, then go into the `research` directory where manage.py is installed, and run `python manage.py migrate`.

    python manage.py migrate

- the django.contrib.admin application will already be uncommented by default, so you'll have to make an admin user at this point, as well.  You should do this now, make a note of username and password.  You'll need it later.

        python manage.py createsuperuser


## Enable django admins:
        
- Install apache and mod-wsgi (as root):

    - you need to install a web server on your machine (apache works well).

            (sudo) apt-get install apache2

    - configure it so it can run python WSGI applications.  For apache, install mod_wsgi:

            (sudo) apt-get install libapache2-mod-wsgi

        then enable it:

            (sudo) a2enmod wsgi

        and restart apache:

            (sudo) service apache2 restart

- Update your django project's wsgi.py file to reflect your Python environment (`<path_to_django_project_parent>/research/wsgi.py`):

    - Add a line that adds your project's directory to the python path:

            # Add the app's directory to the PYTHONPATH
            sys.path.append( '<path_to_django_project_parent>/research' )
        
    - If you are using virtualenv:
    
        - import the `site` packge:
        
                import site
                
        - Add the `site-packages` of the desired virtualenv:
                
                # Add the site-packages of the desired virtualenv
                site.addsitedir( '<.virtualenvs_parent_dir>/.virtualenvs/sourcenet/local/lib/python2.7/site-packages' )
        
        - Activate your virtualenv:
        
                # Activate your virtualenv
                activate_env = os.path.expanduser( "<.virtualenvs_parent_dir>/.virtualenvs/sourcenet/bin/activate_this.py" )
                execfile( activate_env, dict( __file__ = activate_env ) )
        
        - here's how it all should look:
    
                """
                WSGI config for research project.
                
                It exposes the WSGI callable as a module-level variable named ``application``.
                
                For more information on this file, see
                https://docs.djangoproject.com/en/1.6/howto/deployment/wsgi/
                """
                
                # imports
                import os
                import sys
                import site
                from django.core.wsgi import get_wsgi_application
                                
                # Add the site-packages of the desired virtualenv
                site.addsitedir( '<.virtualenvs_parent_dir>/.virtualenvs/sourcenet/local/lib/python2.7/site-packages' )
                
                # Add the app's directory to the PYTHONPATH
                sys.path.append( '<path_to_django_project_parent>/research' )
                
                # Set DJANGO_SETTINGS_MODULE
                os.environ.setdefault("DJANGO_SETTINGS_MODULE", "research.settings")
                
                # Activate your virtualenv
                activate_env = os.path.expanduser( "<.virtualenvs_parent_dir>/.virtualenvs/sourcenet/bin/activate_this.py" )
                execfile( activate_env, dict( __file__ = activate_env ) )
                
                # load django application
                application = get_wsgi_application()
                
            make sure to replace:
            
            - `<.virtualenvs_parent_dir>` with the full path to the directory in which your virtualenvwrapper `.virtualenvs` folder lives (usually your user's home directory).
            - `<path_to_django_project_parent>` with the full path to the directory in which you installed your django project.

- configure your web server so it knows of research/research/wsgi.py.  You'll add something like the following to the apache config:

        WSGIDaemonProcess sourcenet-1 threads=10 display-name=%{GROUP} python-path=<path_to_django_project_parent>/research:<.virtualenvs_parent_dir>/.virtualenvs/<virtualenv_name>/local/lib/python2.7/site-packages 

        # set python path as part of WSGIDaemonProcess --> WSGIDaemonProcess sourcenet-1 ... python-path=
        # no virualenv
        # ... python-path=<path_to_django_project_parent>/research
        # virtualenv (or any other paths, each separated by colons)
        # ... python-path=<path_to_django_project_parent>/research:<.virtualenvs_parent_dir>/.virtualenvs/<virtualenv_name>/local/lib/python2.7/site-packages

        WSGIProcessGroup sourcenet-1
        WSGIScriptAlias /sourcenet <path_to_django_project_parent>/research/research/wsgi.py process-group=sourcenet-1
        
        <Directory <path_to_django_project_parent>/research/research>
            <Files wsgi.py>
                # apache 2.4:
                Require all granted
                # apache 2.2 or earlier:
                #Order deny,allow
                #Allow from all
            </Files>
        </Directory>

    - WHERE:
        
        - `<path_to_django_project_parent>` is the directory in which you created the "research" django project.
        
        - `<.virtualenvs_parent_dir>` is usually the home directory of your user (`/home/<username>`).
    
    - If you are using virtualenv, make sure to add the path to your virtualenv's site-packages to the python-path directive in addition to the site directory, with the paths separated by a colon.  If you use virtualenvwrapper, the path will be something like: `<home_dir>/.virtualenvs/<virtualenv_name>/local/lib/python2.7/site-packages`.

    - If you are using apache 2.2 on ubuntu, I'd put it in `/etc/apache2/conf.d`, in a file named `django-sourcenet`.

    - If you are using apache 2.4 on ubuntu 13.10 or greater:

        - place this file in /etc/apache2/conf-available, naming it "django-sourcenet.conf".
        
        - make sure to uncomment `Require all granted` in the file above, and comment out `Allow from all`.
        
        - enable it with the a2enconf command, then restart apache (just to be safe):
    
                (sudo) a2enconf django-sourcenet
                (sudo) service apache2 restart

- More details on installing apache and mod_wsgi: [https://docs.djangoproject.com/en/dev/howto/deployment/wsgi/modwsgi/](https://docs.djangoproject.com/en/dev/howto/deployment/wsgi/modwsgi/)

- open up the `settings.py` file in `<project_folder>/research` and:

    - make sure the following are in the INSTALLED_APPS list to get the admins to work.

            'django.contrib.admin',
            'django.contrib.admindocs',
            
    - In django 1.6 and up, the django.contrib.admin line should already be present and uncommented, and you'll have to just add the admindocs line.
            
- if 'django.contrib.admin' was commented out and you uncommented it, you'll need to initialize the database for the admins - go into directory where manage.py is installed, and run `python manage.py migrate`.  Make a note of the admin username and password.  You'll need it to log in to the admins.
    
    - In django 1.6 and up, the django.contrib.admin application will already be uncommented by default, so you'll have done this above when you "`migrate`"-ed.

- open up the `urls.py` file in the folder where settings.py lives and add the following line to the urlpatterns variable to complete admin documentation setup:

        url( r'^admin/doc/', include( 'django.contrib.admindocs.urls' ) ),

    urls.py should look like the following once you are done:

        from django.conf.urls import patterns, include, url
        
        from django.contrib import admin
        admin.autodiscover()
        
        urlpatterns = patterns('',

            # Examples:
            # url(r'^$', 'research.views.home', name='home'),
            # url(r'^blog/', include('blog.urls')),
        
            url( r'^admin/', include( admin.site.urls ) ),
            url( r'^admin/doc/', include( 'django.contrib.admindocs.urls' ) ),

        )

### Static file support:

- [https://docs.djangoproject.com/en/dev/howto/static-files/](https://docs.djangoproject.com/en/dev/howto/static-files/)

- in your web root, create a folder named "static" directly in your webroot to hold static files for applications (in ubuntu 14.04 and greater, the default webroot is /var/www/html):

        (sudo) mkdir static
        
- update the permissions on the static directory so you update them if not root.  You can either do this by making it world readable (potentially a security risk), or you can change the ownership to a group that your user is a member of, then change the permissions to 775 (so group writable, but not world-writable).

        (sudo) chmod 777 static
        
        # OR
        (sudo) chgrp <group_name> static
        (sudo) chmod 775 static

- open up the `settings.py` file in `<project_folder>/research` and update the STATIC_ROOT variable so it contains the path to the "static" directory you created in teh step above.  Ubuntu example:

        STATIC_ROOT = '/var/www/html/static'
    
- run the following command to initialize static files for your applications (have to sudo if the folder is in webroot, owned by root if you changed permissions to 777, should not need `sudo`):

        (sudo) python manage.py collectstatic
        
### Test!

- test by going to the URL:

        http://<your_server>/sourcenet/admin/

## Enable django-ajax-selects for easy lookup of people, articles, and organizations in coding pages.

- get the admins working.

- add the following to resesarch/settings.py:

    - add 'ajax_select' to your list of INSTALLED\_APPS.  Result:

            INSTALLED_APPS = (
                'django.contrib.admin',
                'django.contrib.admindocs',
                'django.contrib.auth',
                'django.contrib.contenttypes',
                'django.contrib.sessions',
                'django.contrib.messages',
                'django.contrib.staticfiles',
                'sourcenet',
                'taggit',
                'ajax_select',
            )
        
    - add the following to the bottom of the `settings.py` file:
    
            AJAX_LOOKUP_CHANNELS = {

                # the simplest case, pass a DICT with the model and field to search against :
                #'track' : dict(model='music.track',search_field='title'),
                # this generates a simple channel
                # specifying the model Track in the music app, and searching against the 'title' field
            
                # or write a custom search channel and specify that using a TUPLE
                'article' : ( 'sourcenet.ajax-select-lookups', 'ArticleLookup' ),
                'organization' : ( 'sourcenet.ajax-select-lookups', 'OrganizationLookup' ),
                'person' : ( 'sourcenet.ajax-select-lookups', 'PersonLookup' ),
                # this specifies to look for the class `PersonLookup` in the `sourcenet.ajax-select-lookups` module

            }
            
            # magically include jqueryUI/js/css
            AJAX_SELECT_BOOTSTRAP = True
            AJAX_SELECT_INLINES = 'inline'    

- add the following to resesarch/urls.py to enable django-ajax-selects URL lookups.

    - Add:

            # django-ajax-selects URLs
            from ajax_select import urls as ajax_select_urls
            
        and

            # django-ajax-select URLs
            url( r'^admin/lookups/', include( ajax_select_urls ) ),

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
            
## Enable sourcenet network data output pages

- get the admins working.

- add a line to resesarch/urls.py to enable the sourcenet URLs (in `sourcenet.urls`) to the urlpatterns structure.

    - Add:

            # sourcenet URLs:
            url( r'^sourcenet/', include( 'sourcenet.urls' ) ),

    - Result:

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
                
                # sourcenet URLs:
                url( r'^sourcenet/', include( 'sourcenet.urls' ) ),

            )
            
### Test!

- test by going to the URL:

        http://<your_server>/sourcenet/sourcenet/output/network

# Collecting Articles

There is an example application in sourcenet/collectors/newsbank that you can use as a template for how to gather data and then store it in the database.  It interacts with the newsbank web database, using BeautifulSoup to parse and extract article data.

# Coding articles:

To code articles by hand, use the django admin pages (access to which should have been enabled once you configured your web server so it knows of the wsgi.py file above).  The article model's admin page has been implemented so it is relatively easy to use to code articles, and if you want to refine or alter what is collected, you can alter it in sourcenet/admins.py.

A draft content analysis protocol for assessing sources in a way that can be used to generate network data is in `sourcenet/protocol/sourcenet_CA_protocol.pdf`.

## Automated Coding

### Setting up a user for the automated coding process

Before you do automated coding, you'll need to create a django user named "automated" to which the coding can be attributed.  To do this:

- Open the django admin: `http://<your_server>/sourcenet/admin/`

- Log in with the admin user you created when you initialized the database above.

- Once you are logged in, in the "Authentication and Administration" section of the admin, click on "Users".

- You'll see a list of users that have been created in django.  If there is not one named "automated", you'll need to create one.  To start creating a user, click the "Add User +" button in the upper right hand corner of the page.

- This will load a screen where you'll enter a username and a password twice.  Enter a username and password, and then click the "Save" button in the lower right corner.

- Make sure the "automated" user appears in the list.  This user has no ability to access the admin.  It just exists so the automated coding process can link its coding to this user.


### OpenCalais REST API

To use the OpenCalais REST API to code articles, you'll need to first set up a few pieces of information in the django_config application.

Create the following configuration properties, each with the Application value "OpenCalais_REST_API":

    - `open_calais_api_key` - should contain your Open Calais API key.  For more information on getting an Open Calais API key, see: [http://www.opencalais.com/APIkey](http://www.opencalais.com/APIkey)
    - `submitter` - string that identifies the program that is invoking the API - should start with "sourcenet-", then identify more specifically your project. 
    
Then, the most reliable way to code large numbers of articles is to use the file `sourcenet/examples/articles/article_coding.py` as a template to set up and run a set of articles through the coder.

# Creating Network Data

- The Article model contains code for processing articles and creating network data from them.

    - Article.process_articles(): this method is a class method, is used to batch process articles.  It can be passed parameters in **kwargs to tell it what ranges and types of articles to process:

        - Article.PARAM\_START\_DATE - python datetime instance that has start date of date range we want to process.

        - Article.PARAM\_END\_DATE - python datetime instance that has end date of date range we want to process.

        - Article.PARAM\_SINGLE\_DATE - python datetime instance that date of articles we want to process.

    - Article.do\_automated\_processing(): the method do\_automated\_processing() is a container method for all automated processing you can do to an article.  It accepts some flags in **kwargs so you can control what you process:

        - Article.PARAM\_AUTOPROC\_ALL - if this is set to true, does all implemented automated processing.

        - Article.PARAM\_AUTOPROC\_AUTHORS - if this is set to true, processes the authors/bylines of an article.

# Outputting Network Data

Once you have coded your articles, you can output network data from them by going to the web page `http://<your_server>/sourcenet/sourcenet/output/network`.  This page outputs a form that lets you select articles and people to include in your network, then will output network data based on what you select.

- If you are generating multiple network slices across time periods, you will want to use the "Select People" section of the form (on the right) and enter a fancy date range that includes each date range for all of the slices you are making, so the matrices that result are of the same dimensions (same set of people for each - all people in all slices).

- Syntax for fancy date range fields: For date range fields, enter any number of paired date ranges, where dates are in the format YYYY-MM-DD, dates are separated by the string " to ", and each pair of dates is separated by two pipes ("||").

        Example: 2009-12-01 to 2009-12-31||2010-02-01 to 2010-02-28
        
- For an idea of how you can invoke the network data outputter programmatically, see the `output_network()` method in the file `views.py`.

- Parameters you can set to filter network creation can be seen on the web page for outputting network data.  If you want to interact programmatically, they are listed in the class /export/network_output.py, and you can see the expected values in the method `create_query_set()`.

## Article selection parameters

Article parameters - For convenience, here is a list that was current at the time of this update of parameters you can use.  For each, the list contains the string displayed on the web page, then the actual parameter names:
    
- _"Start Date (YYYY-MM-DD)"_ - `start_date` - publication date - articles will be included that were published on or after this date.
- _"End Date (YYYY-MM-DD)"_ - `end_date` - publication date - articles will be included that were published on or before this date.
- _"* Fancy date range"_ - `date_range` - For date range fields, enter any number of paired date ranges, where dates are in the format YYYY-MM-DD, dates are separated by the string " to ", and each pair of dates is separated by two pipes ("||").  Example: 2009-12-01 to 2009-12-31||2010-02-01 to 2010-02-28
- _"Publications"_ - `publications` - list of IDs of newspapers you want included.
- _"Coders"_ - `coders` - list of IDs of coders whose data you want included.
- _"Topics"_ - `topics` - list of IDs of topics whose data you want included.
- _"Unique Identifier List (comma-delimited)"_ - `unique_identifiers` - list of unique identifiers of articles whose data you want included.
- _"Allow duplicate articles"_ - `allow_duplicate_articles` - allow duplicate articles.  There can be multiple coders and they might have coded the same article.  If this is set to "No", then it will only include one instance of coding for a given article.
- _"Include capacities"_ - `?` - ?
- _"Exclude capacities"_ - `?` - ?
- _not on form_ - `header_prefix` -  for output, optional prefix you want appended to front of column header names.

## Output configuration parameters

- _"Download As File?"_ - `network_download_as_file` - If "Yes", result of rendering network data is downloaded by browser.  If "No", just outputs network data in text box at top of page.
- _"Include Render Details?"_ - `include_render_details` - If "Yes", includes detail on articles and people included in network in output.  If "No", just outputs network data.
- _"Data Format"_ - `output_type` - type of output you want.  Currently support:
    - Simple Matrix - custom format for UCINet
    - CSV Matrix - network matrix rendered as CSV data, with first row and first column containing node labels.
    - Tab-Delimited Matrix - network matrix rendered as tab-delimited text data, with first row and first column containing node labels.
- _"Data Output Type"_ - `data_output_type` - What exactly you want included in the rendered data.  Choices:
    - Just Network - just the network data, no attribute data.
    - Just Attributes - just the node attribute data, no network data.
    - Network + Attribute Columns - network data, plus attributes as additional columns in the matrix.
    - Network + Attribute Rows - network data, plus attributes as additional rows in the matrix.
- _"Network Label"_ - `?` - When outputting CSV for UCINet, this is the line before the start of the lines of CSV data, which UCINet reads as the network name for display inside the program.
- _"Include headers?"_ - `?` - ?

## Person selection parameters

Person parameters - When using the "Select People" area to specify separate filter criteria for the people to include in the network data, it will filter out unknown people.  If you leave the "Select people" fields empty, your network data will include people of all types ("unknown", "source", "reporter").  Unknowns are probaby not useful for network data, so I'll probably eventually add a flag to filter out unknowns.  You can use the following fields to filter the people who are included in your network data:

- _"People from (YYYY-MM-DD)"_ - `person_start_date` - publication date - articles will be included that were published on or after this date.
- _"People to (YYYY-MM-DD)"_ - `person_end_date` - publication date - articles will be included that were published on or before this date.
- _"* Fancy person date range"_ - `person_date_range` - For date range fields, enter any number of paired date ranges, where dates are in the format YYYY-MM-DD, dates are separated by the string " to ", and each pair of dates is separated by two pipes ("||").  Example: 2009-12-01 to 2009-12-31||2010-02-01 to 2010-02-28
- _"Person Publications"_ - `person_publications` - list of IDs of newspapers you want included.
- _"Person Coders"_ - `person_coders` - list of IDs of coders whose data you want included.
- _"Person Topics"_ - `person_topics` - list of IDs of topics whose data you want included.
- _"Unique Identifier List (comma-delimited)"_ - `person_unique_identifiers` - list of unique identifiers of articles whose data you want included.
- _"Person Allow duplicate articles"_ - `person_allow_duplicate_articles` - allow duplicate articles.  There can be multiple coders and they might have coded the same article.  If this is set to "No", then it will only include one instance of coding for a given article.

## What gets output

### type: Simple Matrix

The results of network generation are output in a text box at the top of the page named "Output:".  In this box, the output is broken out into 3 sections:

If render details are requested:

- _parameter overview_ - this is a list of the "Article selection parameters" and "Person selection parameters" that were passed to the network data creation process, for use in debugging.
- _article overview_ - count of and list of articles included in the analysis.  For each article, outputs a counter, the ID of the article, and the article's headline.

Network data:

- _network data output_ - Actual delimited network matrix (values in a row are separated by two spaces - "  ") and labels for each column (and row - the matrix is symmetric).  More precisely, contains:
    - N - count of people (rows/columns) in the network matrix.
    - delimited network data matrix, one row to a line, with values in the row separated by two spaces ("  ").  There will be N rows and columns.
    - list of length N of person type ID for each person in the matrix.  Can be used in UCINet to assign person type values to each node for analysis.
    - labels for each column/row.  The label consists of a counter of the people, each person's system ID, and then the type of the person.  There are two different versions of this list included:
        - list of column/row labels (ordered top-to-bottom for columns, left-to-right for rows) for each column/row, one to a line.
        - list of column/row labels all in one line, values in quotation marks, each value separated by a comma, for use in analysis (inclusion in a spreadsheet, etc.).

### type: CSV Matrix

The results of network generation are output in a text box at the top of the page named "Output:".  In this box, the output is broken out into 3 sections:

If render details are requested:

- _parameter overview_ - this is a list of the "Article selection parameters" and "Person selection parameters" that were passed to the network data creation process, for use in debugging.
- _article overview_ - count of and list of articles included in the analysis.  For each article, outputs a counter, the ID of the article, and the article's headline.

Network data:

- _network data output_ - Actual delimited network matrix (one row to a line, first row and column are string node identifiers, values in each row separated by commas - ",").  More precisely, contains:
    - If render details requested: N - count of people (rows/columns) in the network matrix.
    - If network requested: delimited network data matrix, one row to a line, with values in the row separated by commas (",").  There will be N+1 rows and columns - first row is a header row, containing labels for the person each column represents; first column is labels for the person each row represents.  The matrix is symmetric.
    - If attribute columns requested: Last column in each row in the CSV document contains person type ID for each person in the matrix.
    - If attribute rows requested: Last row in CSV document is person type ID for each person in the matrix, organized by column.

### type: Tab-Delimited Matrix

The results of network generation are output in a text box at the top of the page named "Output:".  In this box, the output is broken out into 3 sections:

If render details are requested:

- _parameter overview_ - this is a list of the "Article selection parameters" and "Person selection parameters" that were passed to the network data creation process, for use in debugging.
- _article overview_ - count of and list of articles included in the analysis.  For each article, outputs a counter, the ID of the article, and the article's headline.

Network data:

- _network data output_ - Actual delimited network matrix (one row to a line, first row and column are string node identifiers, values in each row separated by tabs - "\t").  More precisely, contains:
    - If render details requested: N - count of people (rows/columns) in the network matrix.
    - If network requested: delimited network data matrix, one row to a line, with values in the row separated by tabs ("\t").  There will be N+1 rows and columns - first row is a header row, containing labels for the person each column represents; first column is labels for the person each row represents.  The matrix is symmetric.
    - If attribute columns requested: Last column in each row in the document contains person type ID for each person in the matrix.
    - If attribute rows requested: Last row in document is person type ID for each person in the matrix, organized by column.

## Adding a new output type

To add a new output type, do the following:

- create a new class that extends NetworkDataOutputter.
- in this new class:
    - _see class `NDO_SimpleMatrix` in file `export/ndo_simple_matrix.py` for an example._
    - make sure to import the NetworkDataOutputter abstract class:

            from sourcenet.export.network_data_output import NetworkDataOutput

    - implement a `__init__()` method that calls parent method, and overrides fields specific to your output type, especially output type, mime type, and file extension.  Example from `NDO_CSVMatrix` (file `export/ndo_csv_matrix.py`):

            def __init__( self ):
        
                # call parent's __init__()
                super( NDO_CSVMatrix, self ).__init__()
        
                # override things set in parent.
                self.output_type = self.MY_OUTPUT_TYPE
                self.debug = "NDO_CSVMatrix debug:\n\n"
        
                # initialize variables.
                self.csv_string_buffer = None
                self.csv_writer = None
                self.delimiter = ","
        
                # variables for outputting result as file
                self.mime_type = "text/csv"
                self.file_extension = "csv"
        
            #-- END method __init__() --#

    - implement the `render_network_data()` method.  A few notes:
        - this method will be called by the `render()` method in class `NetworkDataOutput` (file `export/network_data_output.py`).  That method takes care of figuring out what people should be in the network and figuring out ties based on included articles.  You just need to take this information and render network data.
        - how to get important data:
            - `self.get_master_person_list()` - retrieves list of all people (nodes) that must be included in the network data that you output, sorted by ID.  Could be more people here than are in the set of articles (for the case of data that will be compared across time periods).
            - `self.get_person_type( person_id )` - retrieves person type for a given person (node).
            - `self.get_person_type_id( person_id )` - retrieves person type ID for a given person (node).
            - `self.get_relations_for_person( person_id )` - retrieves list of relations for a given person (node).
        - if you are creating network data, you'll want to use the master person list to see what nodes are in the network, then the results of `get_relations_for_person()` to see what ties are present for each person.  So, if you are making a matrix:
            - loop over a copy of the master person list as your control for making rows, one per person.  Then, for each person:
                - retrieve a new copy of the master person list.
                - loop over it to generate columns for the row.  For each person:
                    - see if there is a relation.
                        - If yes, set column value to 1 (or a weight, or whatever you are doing...).
                        - If no, set column value to 0.
    - add a constant for the output type this class will implement named `MY_OUTPUT_TYPE`, and in an overridden `__init__()` method, set `self.output_type = MY_OUTPUT_TYPE`.
- In the `NetworkOutput` class, in file `export/network_output.py`):
    - add an import statement to import your new class to the imports section, near the top of the file.
    - add the output type value for your new output class as a constant-ish at the top, named `NETWORK_OUTPUT_TYPE_<TYPE>`.
    - add the output type and its display string to the list of tuples stored in NETWORK_OUTPUT_TYPE_CHOICES_LIST.
    - in the method `get_NDO_instance()`, add an `elif` to the conditional that maps types to instantiation of objects for each type that creates an instance of your new class when type matches the constant you created in the step above.
    
## Working with network data in R

To work with network data into R, first you read either a CSV or tab-delimited network matrix in as a data frame.  Then, convert to an R matrix object.  From there, you can load the matrix into your SNA package of choice (examples for igraph and statnet below).

For more detailed examples, see the `*.r` R source code files in `sourcenet/R/`.

### Import a CSV file

To read in a CSV matrix file:

    # comma-delimited:
    csv_test1 <- read.csv( "csv-test1.csv", header = TRUE, row.names = 1, check.names = FALSE )
    
    # just use the first 314 rows (omit the person_type row, the last row, for now).
    csv_test1_network <- csv_test1[ -nrow( csv_test1 ), ]
    
    # convert to a matrix
    csv_test1_matrix <- as.matrix( csv_test1_network )

### Import a tab-delimited file

To read in a tab-delimited matrix file:

    # tab-delimited:
    tab_test1 <- read.delim( "tab-test1-data.txt", header = TRUE, row.names = 1, check.names = FALSE )
    
    # just use the first 314 rows (omit the person_type row, the last row, for now).
    tab_test1_network <- tab_test1[ -nrow( tab_test1 ), ]
    
    # convert to a matrix
    tab_test1_matrix <- as.matrix( tab_test1_network )
        
### Load matrix into igraph

To load an imported matrix into igraph ([http://igraph.org/index.html](http://igraph.org/index.html)):

    library( igraph )

    # convert matrix to igraph graph object instance.
    test1_igraph <- graph.adjacency( tab_test1_matrix, mode = "undirected", weighted = TRUE )
    
    # more details on graph.adjacency(): http://igraph.org/r/doc/graph.adjacency.html
    
    # to see count of nodes and edges, just type the object name:
    test1_igraph
    
    # Will output something like:
    #
    # IGRAPH UNW- 314 309 -- 
    # + attr: name (v/c), weight (e/n)
    #
    # in the first line, "UNW-" are traits of graph:
    # - 1 - U = undirected ( directed would be "D" )
    # - 2 - N = named or not ( "-" instead of "N" )
    # - 3 - W = weighted
    # - 4 - B = bipartite ( "-" = not bipartite )
    # 314 is where node count goes, 309 is edge count.
    # The second line gives you information about the 'attributes' associated with the graph. In this case, there are two attributes, name and weight.  Next to each attribute name is a two-character construct that looks like "(v/c)".  The first letter is the thing the attribute is associated with (g = graph, v = vertex or node, e = edge).  The second is the type of the attribute (c = character data, n = numeric data).  So, in this case:
    # - name (v/c) - the name attribute is a vertex/node attribute - the "v" in "(v/c)" - where the values are character data - the "c" in "(v/c)".
    # - weight (e/n) - the weight attribute is an edge attribute - the "e" in "(e/n)" - where the values are numeric data - the "n" in "(e/n)".
    # - based on: http://www.shizukalab.com/toolkits/sna/sna_data
    
    # to reference a vertex attribute's values, use V( <network> )$<attribute_name>

    # output the names for the nodes in the graph:
    V( test1_igraph )$name

    # use last row in original data file to make person_type an attribute of each node.

    # first, get just the data frame row with person types (the last row):
    person_types_row <- tab_test1[ 315, ]

    # Convert to a list of numbers.
    person_types_list <- as.numeric( person_types_row )

    # set vertex/node attribute person_type
    V( test1_igraph )$person_type <- person_types_list
    
    # look at graph and person_type attribute values
    test1_igraph
    V( test1_igraph )$person_type

### Load matrix into statnet

To load an imported matrix into statnet ([http://www.statnet.org/](http://www.statnet.org/)):

    library( statnet )
    
    # convert matrix to statnet network object instance.
    test1_statnet <- network( tab_test1_matrix, matrix.type = "adjacency", directed = FALSE )

    # to see information about network, just type the object name:
    test1_statnet
    
    # Output example:
    # Network attributes:
    #  vertices = 314 
    #  directed = FALSE 
    #  hyper = FALSE 
    #  loops = FALSE 
    #  multiple = FALSE 
    #  bipartite = FALSE 
    #  total edges= 309 
    #    missing edges= 0 
    #    non-missing edges= 309 
    #
    # Vertex attribute names: 
    #    vertex.names 
    #
    # No edge attributes
        
    # If you have a file of attributes (each attribute is a column, with
    #    attribute name the column name), you can associate those attributes
    #    when you create the network.
    # attribute help: http://www.inside-r.org/packages/cran/network/docs/loading.attributes
    
    # load attribute file:
    tab_attribute_test1 <- read.delim( "tab-test1-attribute_data.txt", header = TRUE, row.names = 1, check.names = FALSE )
    
    # convert matrix to statnet network object instance.
    test1_statnet <- network( tab_test1_matrix, matrix.type = "adjacency", directed = FALSE, vertex.attr = tab_attribute_test1 )
    
    # look at information now.
    test1_statnet

    # Network attributes:
    #  vertices = 314 
    #  directed = FALSE 
    #  hyper = FALSE 
    #  loops = FALSE 
    #  multiple = FALSE 
    #  bipartite = FALSE 
    #  total edges= 309 
    #    missing edges= 0 
    #    non-missing edges= 309 
    #
    # Vertex attribute names: 
    #    person_type vertex.names 
    #
    # No edge attributes
    
    # - OR - you can just add the attribute values to an existing network.
    test1_statnet%v%"person_type" <- tab_attribute_test1$person_type
    
    # list out the person_type attribute values
    test1_statnet%v%"person_type"

## Importing data into UCINet

To import data into UCINet:

- select your filter criteria, then choose the CSV Matrix output type and render output.
- click in output text area, press Ctrl-A (Windows/linux) or Cmd-A (Mac) to select everything in the text area, then Ctrl-C (windows/linux) or Cmd-C (mac) to copy the entire contents.
- open a text document and paste the entire contents into the text document.
- If you want to keep the full original output:

    - save that document and open another.
    - in the original, just copy the portion of the file from after:
    
            =======================
            network data output:
            =======================
            
            N = 314
            
        to before (at the bottom of the file):

            =======================
            END network data output
            =======================
        
    - save this portion into another file with file extension ".csv".
- If you don't care about the full original output:

    - delete everything from the following up:
    
            =======================
            network data output:
            =======================
            
            N = 314

        and remove the following from the bottom of the file:
        
            =======================
            END network data output
            =======================
        
    - save the file with the file extension ".csv".
    
- Open Microsoft Excel, and use it to open your .csv file.
- Save the resulting document as an Excel file.
- Open UCINet.
- Open the "Excel Matrix Editor".
- Open the Excel file you created.
- Select and remove the bottom row for now (it is person types, not ties).
- Click "Save" in the menu bar, then choose "Save active sheet as UCINET dataset".
- Choose a name and location to save, and you are done!

# Testing

The sourcenet project has a small but growing set of unit tests that once can auto-run.  These tests use django's testing framework, based on the Python `unittest` package.

## Unit Tests

### Configuration

#### OpenCalais API configuration

In order to run unit tests using OpenCalais's API, you'll need to:

- Create a Thompson Reuters ID ( [https://iameui-eagan-prod.thomsonreuters.com/iamui/UI/createUser?app_id=Bold&realm=Bold](https://iameui-eagan-prod.thomsonreuters.com/iamui/UI/createUser?app_id=Bold&realm=Bold) ).

    - after submitting form, open email from Thompson Reuters with subject something like "Please confirm your email address for your new Open PermID | Calais user account" and click the link to activate your profile.
   
- Get your API token ()

    - browse to the Open Calais site ( [http://www.opencalais.com/](http://www.opencalais.com/) ).
    - click the "Login" button in the upper right.
    - log in with your username and password.
    - Once you are logged in, click on your username (your email address) in the upper right corner, then in the dropdown that results, click on "Display my Token".  Your API token will appear in a box labeled "YOUR TOKEN".  Copy it down and save it in a safe place.

- Store that token and only that token in a file named "`open_calais_access_token.txt`" in the root of your django project/site (the same folder where `manage.py` lives).

#### Database configuration

In order to run unit tests, your database configuration in `settings.py` will need to be connecting to the database with a user who is allowed to create databases.  When django runs unit tests, it creates a test database, then deletes it once testing is done.
- _NOTE: This means the database user you use for unit testing SHOULD NOT be the user you'd use in production.  The production database user should not be able to do anything outside a given database._

### Running unit tests

To run unit tests, at the command line in your django project/site folder (where `manage.py` lives):

    python manage.py test sourcenet.tests
    
Specific sets of tests:

- OpenCalais API (v.2)

    - test OpenCalais configuration:

            python manage.py test sourcenet.tests.open_calais.tests-open_calais-config

    - test OpenCalais automated coding (assumes configuration tests passed):

            python manage.py test sourcenet.tests.open_calais.tests-open_calais-api 

## Test data

There is a set of test data stored in the `fixtures` folder inside this django application.  The files:

- **_`sourcenet_unittest_auth_data.json`_** - User data for article-coding comparison.
- **_`sourcenet_unittest_django_config_data.json`_** - configuration properties for sourcenet (in particular, for external APIs).
- **_`sourcenet_unittest_data.json`_** - actual sourcenet data - needs to be loaded after "`auth`" data so users who did coding are in database when coding data is loaded.
- **_`sourcenet_unittest_taggit_data.json`_** - tag data for sourcenet data (broken at the moment, since it relies on django's content types, and they are dynamically assigned and so not guaranteed to be the same for a given object type across runs of the unit tests).

### Using unittest data for development

- create a database where the unit test data can live.  The name should be "test_", followed by the name of your main production database.  Easiest way to do this is to just create the database, then give the same user you use for your production database the same access they have for production for this test database as well.

    - postgresql example, where production database name is "`sourcenet`" and database user is "`django_user`":

            CREATE DATABASE test_sourcenet;
            GRANT ALL PRIVILEGES ON DATABASE test_sourcenet TO django_user;

- update the DATABASES dictionary in settings.py of the application that contains sourcenet to point to your test database (in easy example above, could just change the 'NAME' attribute in the 'default' entry to "`test_sourcenet`" rather than "`sourcenet`".
- cd into your django application's home directory, activate your virtualenv if you created one, then run "`python manage.py migrate`" to create all the tables in the database.

        cd <django_app_directory>
        workon sourcenet
        python manage.py migrate

- use the command "`python manage.py createsuperuser`" to make an admin user, for logging into the django admins.

        python manage.py createsuperuser

- load the unit test fixtures into the database:

        python manage.py loaddata sourcenet_unittest_auth_data.json
        python manage.py loaddata sourcenet_unittest_django_config_data.json
        python manage.py loaddata sourcenet_unittest_data.json
        python manage.py loaddata sourcenet_unittest_taggit_data.json

# License

Copyright 2010-present (2016) Jonathan Morgan

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