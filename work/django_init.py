import datetime
import os
import sys

# path to folder where "manage.py" lives in your django project.
project_path = "/home/jonathanmorgan/work/django/research/"

# Tell django where settings are.
os.environ.setdefault( "DJANGO_SETTINGS_MODULE", "research.settings" )
sys.path.append( project_path )

# OPTIONAL - This is so my local_settings.py gets loaded.
#os.chdir( project_path )

# This is so models get loaded.
from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()

print( "django initialized at " + str( datetime.datetime.now() ) )
