Installing SourceNet
====================

To install:

* required python modules (install with pip):

    * nameparser
    
* install and configure django to talk with a database (http://docs.djangoproject.com/en/dev/intro/tutorial01/).

* install and configure a django application named "research" (including setting up database in settings.py).

    * In the folder where you want your application, run:
    
            django-admin.py startproject research

    * This creates the following folder structure and files (among others):

            /research

                manage.py

                /research

                    settings.py
    
    * Edit the research/research/settings.py file and update it with details of your database configuration (https://docs.djangoproject.com/en/dev/intro/tutorial01/#database-setup).

* install and configure the sourcenet application.

    * move sourcenet into your django application directory.

    * initialize the database - go into directory where manage.py is installed, and run "python manage.py syncdb".

    * configure your web server so it knows of your wsgi.py file.  If apache, need to make sure mod_wsgi is installed, add something like this to the apache config:
    
        WSGIDaemonProcess sourcenet-1 threads=10 display-name=%{GROUP}
        WSGIProcessGroup sourcenet-1
        WSGIScriptAlias /sourcenet <path_to_django_app>/<app_name>/<app_name>/wsgi.py
    
* play (and hope it doesn't break!).

Processing articles
===================

* The Article model contains code for processing articles and creating network data from them.

    * Article.process_articles(): this method is a class method, is used to batch process articles.  It can be passed parameters in **kwargs to tell it what ranges and types of articles to process:

        * Article.PARAM_START_DATE - python datetime instance that has start date of date range we want to process.

        * Article.PARAM_END_DATE - python datetime instance that has end date of date range we want to process.

        * Article.PARAM_SINGLE_DATE - python datetime instance that date of articles we want to process.

    * Article.do_automated_processing(): the method do_automated_processing() is a container method for all automated processing you can do to an article.  It accepts some flags in **kwargs so you can control what you process:

        * Article.PARAM_AUTOPROC_ALL - if this is set to true, does all implemented automated processing.

        * Article.PARAM_AUTOPROC_AUTHORS - if this is set to true, processes the authors/bylines of an article.