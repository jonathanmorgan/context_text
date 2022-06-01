#!/bin/bash

# project home folder path is folder where "manage.py" file lives.
django_project_home_path="."
if [[ -n "$1" ]]
then    
    $django_project_home_path="${1}"

    # cd into django project home
    cd "${django_project_home_path}"
fi

# load data fixtures
python manage.py loaddata context_text_unittest_export_auth_data.json
python manage.py loaddata context_text_unittest_django_config_data.json
python manage.py loaddata context_text_unittest_export_data.json
python manage.py loaddata context_text_unittest_export_taggit_data.json
python manage.py loaddata context-sourcenet_entity_and_relation_types.json

