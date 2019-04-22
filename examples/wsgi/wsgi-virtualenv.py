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
site.addsitedir( '<$HOME>/.virtualenvs/context_text/local/lib/python2.7/site-packages' )

# Add the app's directory to the PYTHONPATH
sys.path.append( '<django_project_dir>/research' )

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "research.settings")

# Activate your virtualenv
activate_env = os.path.expanduser( "<$HOME>/.virtualenvs/context_text/bin/activate_this.py" )
execfile( activate_env, dict( __file__ = activate_env ) )

from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()
