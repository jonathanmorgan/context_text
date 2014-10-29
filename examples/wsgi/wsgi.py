"""
WSGI config for research project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/1.6/howto/deployment/wsgi/
"""
# imports
import sys
import os

# put my application on python path
sys.path.append( '<django_project_dir>/research' )

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "research.settings")

from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()
