from __future__ import unicode_literals

from django.apps import AppConfig


class Context_TextConfig(AppConfig):

    name = 'context_text'

    default_auto_field = 'django.db.models.AutoField'
    # if you have lots of rows:
    # default_auto_field = 'django.db.models.BigAutoField'

#-- END AppConfig class Context_TextConfig --#
