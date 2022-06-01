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
python manage.py loaddata context_text_unittest_auth_data.json
python manage.py loaddata context_text_unittest_django_config_data.json
python manage.py loaddata context_text_unittest_data.json
python manage.py loaddata context_text_unittest_taggit_data.json

