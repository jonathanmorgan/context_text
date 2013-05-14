# sourcenet

sourcenet is a django application for capturing and analyzing networks of news based on articles.

## Installation

- required python modules (install with pip):

    - nameparser - `(sudo) pip install nameparser`
    - django - `(sudo) pip install django` (1.5.X preferred, latest 1.4.X should work, too)
    - beautiful soup 4 - `(sudo) pip install beautifulsoup4`

- install and configure a django application named "research" (including setting up database in settings.py).

    - In the folder where you want your application, run:

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

## Configuration:

- in research/research/settings/py:

    - Edit the research/research/settings.py file and update it with details of your database configuration (https://docs.djangoproject.com/en/dev/intro/tutorial01/#database-setup).

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
                'sourcenet',
            )

    - initialize the database - go into directory where manage.py is installed, and run "python manage.py syncdb".

    - To access the admins, you need to install a web server on your machine, configure it so it can run python WSGI applications (for apache, install mod_wsgi), then configure your web server so it knows of research/research/wsgi.py.  If apache, need to make sure mod_wsgi is installed, add something like this to the apache config:

            WSGIDaemonProcess sourcenet-1 threads=10 display-name=%{GROUP}
            WSGIProcessGroup sourcenet-1
            WSGIScriptAlias /sourcenet <path_to_django_app>/<app_name>/<app_name>/wsgi.py

## Collecting Articles

There is an example application in sourcenet/collectors/newsbank that you can use as a template for how to gather data and then store it in the database.  It interacts with the newsbank web database, using BeautifulSoup to parse and extract article data.

## Coding articles:

To code articles by hand, use the django admin pages (access to which should have been enabled once you configured your web server so it knows of the wsgi.py file above).  The article model's admin page has been implemented so it is relatively easy to use to code articles, and if you want to refine or alter what is collected, you can alter it in sourcenet/admins.py.

A draft content analysis protocol for assessing sources in a way that can be used to generate network data is in sourcenet/protocol/sourcenet_CA_protocol.pdf.

## Creating Network Data

- The Article model contains code for processing articles and creating network data from them.

    - Article.process_articles(): this method is a class method, is used to batch process articles.  It can be passed parameters in **kwargs to tell it what ranges and types of articles to process:

        - Article.PARAM_START_DATE - python datetime instance that has start date of date range we want to process.

        - Article.PARAM_END_DATE - python datetime instance that has end date of date range we want to process.

        - Article.PARAM_SINGLE_DATE - python datetime instance that date of articles we want to process.

    - Article.do_automated_processing(): the method do_automated_processing() is a container method for all automated processing you can do to an article.  It accepts some flags in **kwargs so you can control what you process:

        - Article.PARAM_AUTOPROC_ALL - if this is set to true, does all implemented automated processing.

        - Article.PARAM_AUTOPROC_AUTHORS - if this is set to true, processes the authors/bylines of an article.

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