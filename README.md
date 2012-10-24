This is going to be great.  More details to come.

Installing SourceNet
====================

To install:
* install and configure django to talk with a database (http://docs.djangoproject.com/en/dev/intro/tutorial01/).
* install and configure a django application named "research" (including setting up database in settings.py).
* install and configure the sourcenet application.
    * move sourcenet into your django application directory.
    * initialize the database - go into directory where manage.py is installed, and run "python manage.py syncdb".
    * configure your web server so it knows of your wsgi.py file.  If apache, need to make sure mod_wsgi is installed, add something like this to the apache config:
    
        WSGIDaemonProcess sourcenet-1 threads=10 display-name=%{GROUP}
        WSGIProcessGroup sourcenet-1
        WSGIScriptAlias /sourcenet <path_to_django_app>/<app_name>/<app_name>/wsgi.py
    
* play (and hope it doesn't break!).
