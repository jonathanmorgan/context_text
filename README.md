# sourcenet

<!-- TOC -->

sourcenet is a django application for capturing and analyzing networks of news based on articles.  In order for database migrations to work, you need to use 1.7.  south_migrations are present, but they won't be updated going forward.

# Installation and configuration

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

    - If you might want to try to run the newsbank collector, you'll also need python\_utilities.  Clone python\_utilities into the research folder alongside sourcenet:

            git clone https://github.com/jonathanmorgan/python_utilities.git

## Configure database, applications:

- in research/research/settings.py:

    - Edit the research/research/settings.py file and update it with details of your database configuration
    
        - [https://docs.djangoproject.com/en/dev/intro/tutorial01/#database-setup](https://docs.djangoproject.com/en/dev/intro/tutorial01/#database-setup)
        - [https://docs.djangoproject.com/en/dev/ref/settings/#databases](https://docs.djangoproject.com/en/dev/ref/settings/#databases)

    - add 'sourcenet' to your list of INSTALLED\_APPS:

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
            )

    - initialize the database - go into directory where manage.py is installed, and run `python manage.py migrate`.
    
            python manage.py migrate

        - the django.contrib.admin application will already be uncommented by default, so you'll have to make an admin user at this point, as well.  You should do this now, make a note of username and password.  You'll need it later.


## Enable django admins:
        
- you need to install a web server on your machine (apache works well).

- configure it so it can run python WSGI applications.  For apache, install mod_wsgi:

        (sudo) apt-get install libapache2-mod-wsgi

- configure your web server so it knows of research/research/wsgi.py.  You'll add something like the following to the apache config:

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

    - If you are using virtualenv, make sure to add the path to your virtualenv's site-packages to the WSGIPythonPath directive in addition to the site directory, with the paths separated by a colon.  If you use virtualenvwrapper, the path will be something like: `<home_dir>/.virtualenvs/<virtualenv_name>/local/lib/python2.7/site-packages`.

    - If you are using apache 2.2 on ubuntu, I'd put it in `/etc/apache2/conf.d`, in a file named `django-sourcenet`.

    - If you are using apache 2.4 on ubuntu 13.10 or greater:

        - place this file in /etc/apache2/conf-available, naming it "django-sourcenet.conf".
        
        - make sure to uncomment `Require all granted` in the file above, and comment out `Allow from all`.
        
        - enable it with the a2enconf command:
    
                (sudo) a2enconf django-sourcenet

- Update the wsgi.py file (`<django_project_dir>/research/wsgi.py`):

    - Add a line that adds your project's directory to the python path:

            # Add the app's directory to the PYTHONPATH
            sys.path.append( '<django_project_dir>/research' )
        
    - If you are using virtualenv:
    
        - import the `site` packge:
        
                import site
                
        - Add the `site-packages` of the desired virtualenv:
                
                # Add the site-packages of the desired virtualenv
                site.addsitedir( '<virtualenv_home_dir>/.virtualenvs/sourcenet/local/lib/python2.7/site-packages' )
        
        - Activate your virtualenv:
        
                # Activate your virtualenv
                activate_env = os.path.expanduser( "<virtualenv_home_dir>/.virtualenvs/sourcenet/bin/activate_this.py" )
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
                
                # Add the site-packages of the desired virtualenv
                site.addsitedir( '<virtualenv_home_dir>/.virtualenvs/sourcenet/local/lib/python2.7/site-packages' )
                
                # Add the app's directory to the PYTHONPATH
                sys.path.append( '<django_project_dir>/research' )
                
                os.environ.setdefault("DJANGO_SETTINGS_MODULE", "research.settings")
                
                # Activate your virtualenv
                activate_env = os.path.expanduser( "<virtualenv_home_dir>/.virtualenvs/sourcenet/bin/activate_this.py" )
                execfile( activate_env, dict( __file__ = activate_env ) )
                
                from django.core.wsgi import get_wsgi_application
                application = get_wsgi_application()
                
            make sure to replace:
            
            - `<virtualenv_home_dir>` with the full path to the directory where your virtualenvwrapper `.virtualenvs` folder lives (usually your user's home directory).
            - `<django_project_dir>` with the full path to the directory where you installed your django project.

- More details on installing apache and mod_wsgi: [https://docs.djangoproject.com/en/dev/howto/deployment/wsgi/modwsgi/](https://docs.djangoproject.com/en/dev/howto/deployment/wsgi/modwsgi/)

- open up the `settings.py` file in `<project_folder>/research` and:

    - make sure the following are in the INSTALLED_APPLICATIONS list to get the admins to work.

            'django.contrib.admin',
            'django.contrib.admindocs',
            
    - In django 1.6 and up, the django.contrib.admin line should already be present and uncommented, and you'll have to just add the admindocs line.
            
- if 'django.contrib.admin' was commented out and you uncommented it, you'll need to initialize the database for the admins - go into directory where manage.py is installed, and run `python manage.py migrate`.  Make a note of the admin username and password.  You'll need it to log in to the admins.
    
    - In django 1.6 and up, the django.contrib.admin application will already be uncommented by default, so you'll have done this above.

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

- in your web root, create a folder named "static" directly in your webroot to hold static files for applications (in ubuntu, the default webroot is /var/www):

        (sudo) mkdir static
        
- open up the `settings.py` file in `<project_folder>/research` and update the STATIC_ROOT variable so it contains the path to the "static" directory you created in teh step above.  Ubuntu example:

        STATIC_ROOT = '/var/www/static'
    
- run the following command to initialize static files for your applications (have to sudo if the folder is in webroot, owned by root):

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
                'ajax_select',
            )
        
    - add the following to the bottom of the file:
    
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

- add a line to resesarch/urls.py to enable the sourcenet URLs (in `research.sourcenet.urls`) to the urlpatterns structure.

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
            
### Test!

- test by going to the URL:

        http://<your_server>/sourcenet/sourcenet/output/network

# Collecting Articles

There is an example application in sourcenet/collectors/newsbank that you can use as a template for how to gather data and then store it in the database.  It interacts with the newsbank web database, using BeautifulSoup to parse and extract article data.

# Coding articles:

To code articles by hand, use the django admin pages (access to which should have been enabled once you configured your web server so it knows of the wsgi.py file above).  The article model's admin page has been implemented so it is relatively easy to use to code articles, and if you want to refine or alter what is collected, you can alter it in sourcenet/admins.py.

A draft content analysis protocol for assessing sources in a way that can be used to generate network data is in sourcenet/protocol/sourcenet_CA_protocol.pdf.

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

# License

Copyright 2010-present (2014) Jonathan Morgan

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