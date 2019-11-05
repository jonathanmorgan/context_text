# context_text

[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.3523019.svg)](https://doi.org/10.5281/zenodo.3523019)

<!-- TOC -->

context_text is a django application for capturing and analyzing networks of news based on articles.  In order for database migrations to work, you need to use 1.7+.  south_migrations are present, but they won't be updated going forward.

It is built upon and depends on the base context django application: [https://github.com/jonathanmorgan/context](https://github.com/jonathanmorgan/context)

# Installation and configuration

Below, there used to be detailed instructions for installing all the things to get django running on apache with a PostgreSQL database backend on an Ubuntu server (these are preserved for reference in `archive/README-manual_install.md`.  Now, I've created ansible scripts with all the steps that you can configure and run against Ubuntu 18.04 or 16.04 (VM, cloud server, or physical machine).

These scripts are in my "ansible-patterns" repository: [https://github.com/jonathanmorgan/ansible-patterns](https://github.com/jonathanmorgan/ansible-patterns)

These ansible scripts can also be used to just setup a server with virtualenvwrapper, postgresql, apache, django, jupyterhub, and R, without context.  See the readme for detailed instructions.

Chances are I'll make dockerfile(s) for this eventually, too, but for now, there's ansible.

I've left in a few notes below, regarding different package and installation choices, but the best doc is the ansible repo.

## Python packages

- depending on database:

    - postgresql - psycopg2 - Before you can connect to Postgresql with this code, you need to do the following (based on [http://initd.org/psycopg/install/](http://initd.org/psycopg/install/)):

        - install the PostgreSQL client if it isn't already installed.  On linux, you'll also need to install a few dev packages (python-dev, libpq-dev) ( [source](http://initd.org/psycopg/install/) ).
        - install the psycopg2 python package.  Install using pip (`sudo pip install psycopg2`).  
        
    - mysql - mysqlclient - Before you can connect to MySQL with this code, you need to do the following:
    
        - mysqlclient

            - install the MySQL client if it isn't already installed.  On linux, you'll also need to install a few dev packages (python-dev, libmysqlclient-dev) ( [source](http://codeinthehole.com/writing/how-to-set-up-mysql-for-python-on-ubuntu/) ).
            - install the mysqlclient python package using pip (`(sudo) pip install mysqlclient`).

- python packages that I find helpful:

    - ipython - `(sudo) pip install ipython`

- Natural Language Processing (NLP) APIs, if you are building your own thing (I don't use Alchemy API right now, and I built my own OpenCalais client):

    - To use Alchemy API, clone the `Alchemy_API` python client into your django project's root folder:
    
        - `git clone https://github.com/alchemyapi/alchemyapi_python`
        
    - To use the pycalais package for OpenCalais's REST API, clone the pycalais git repository into your django project directory, then copy the calais folder into your django project directory:
    
        - `git clone https://github.com/ubergrape/pycalais`
        - `cp ./calais ../`
        
        - You can also use python_utilities.network.http_helper.Http_Helper to connect directly (or requests package) see the sample code in /examples/NLP/OpenCalais_API.py for more details.

## settings.py - Configure logging, database, applications:

The following are some django settings you might want to tweak in the settings.py file in your django project.  If you created a project named "research", this will be located at `research/research/settings.py`.

### logging

Edit the `research/research/settings.py` file and update it with details of your logging configuration
    
- Example that logs any messages INFO and above to standard out:

        import logging

        logging.basicConfig(
            level = logging.INFO,
            format = '%(asctime)s - %(levelname)s - %(name)s - %(message)s'
        )

- Example that logs any messages INFO and above to a file:

        import logging

        logging.basicConfig(
            level = logging.INFO,
            format = '%(asctime)s - %(levelname)s - %(name)s - %(message)s',
            filename = '<log_folder>/django-research.log',
            filemode = 'w'
        )

    - WHERE `<log_folder>` is a folder that any users that will be used to interact with context_text have access to.  This includes the user your web server runs as (for admins and other django web pages) and the user you use to develop, and so that might run things from the python shell.

        - the easiest way to get this working:

            - make the `<log_folder>` somewhere outside the web root.
            - set the permissions on `<log_folder>` to 777.
            - create the file `django-research.log` there.
            - set its permissions also to 777.

        - This is not necessarily optimally secure, but truly securing this is beyond the scope of this README.

- You can set `level` to any of the following, which are organized from most detail (`logging.DEBUG`) to least (`logging.CRITICAL`):

    - `logging.DEBUG`
    - `logging.INFO`
    - `logging.WARNING`
    - `logging.ERROR`
    - `logging.CRITICAL`

- Python logging HOWTO: [https://docs.python.org/2/howto/logging.html](https://docs.python.org/2/howto/logging.html)
- Python logging cookbook: [https://docs.python.org/2/howto/logging-cookbook.html](https://docs.python.org/2/howto/logging-cookbook.html)

### database

Edit the research/research/settings.py file and update it with details of your database configuration.

In general, for any database other than sqlite3, in your database system of choice you'll need to:

- create a database for django to use (I typically use `research`).

    - postgresql - at the unix command line:
    
            # su to the postgres user
            su - postgres
            
            # create the database at the unix shell
            #createdb <database_name>
            createdb research

- create a database user for django to use that is not an admin (I typically use `django_user`).

    - postgresql - at the unix command line:
    
            # su to the postgres user
            su - postgres
            
            # create the user at the unix shell
            #createuser --interactive -P <username>
            createuser --interactive -P django_user

- give the django database user all privileges on the django database.
- place connection information for the database - connecting as your django database user to the django database - in settings.py.

An example for postgresql looks like this:

    DATABASES = {
        'default': {        
            # PostgreSQL - research
            'ENGINE': 'django.db.backends.postgresql', # Add 'postgresql', 'mysql', 'sqlite3' or 'oracle'.
            'NAME': 'research',                      # Or path to database file if using sqlite3.
            'USER': 'django_user',                      # Not used with sqlite3.
            'PASSWORD': '<db_password>',                  # Not used with sqlite3.
            'HOST': 'localhost',                      # Set to empty string for localhost. Not used with sqlite3.
            'PORT': '5432',                      # Set to empty string for default. Not used with sqlite3.
        },
    }

More information:
    
- [https://docs.djangoproject.com/en/dev/intro/tutorial01/#database-setup](https://docs.djangoproject.com/en/dev/intro/tutorial01/#database-setup)
- [https://docs.djangoproject.com/en/dev/ref/settings/#databases](https://docs.djangoproject.com/en/dev/ref/settings/#databases)

# Testing

## Basic tests

- test by going to the URL:

        http://<your_server>/research/admin/

- and then logging in with the django superuser created by ansible scripts.
- to test coding pages, test by going to the URL:

        http://<your_server>/research/context_text/index

- log in with your django superuser user.
- You should see a home page for context_text with a welcome message and a header that lists out the pages in the context_text application.

## Unit Tests

The context_text project has a small but growing set of unit tests that can be auto-run.  These tests use django's testing framework, based on the Python `unittest` package.

### Configuration

#### OpenCalais API configuration

In order to run unit tests using OpenCalais's API, you'll need to:

- Create a Thompson Reuters ID ( [https://iameui-eagan-prod.thomsonreuters.com/iamui/UI/createUser?app_id=Bold&realm=Bold](https://iameui-eagan-prod.thomsonreuters.com/iamui/UI/createUser?app_id=Bold&realm=Bold) ).

    - after submitting form, open email from Thompson Reuters with subject something like "Please confirm your email address for your new Open PermID | Calais user account" and click the link to activate your profile.
   
- Get your API token ()

    - browse to the Open Calais site ( [http://www.opencalais.com/](http://www.opencalais.com/) ).
    - click the "Login" button in the upper right.
    - log in with your username and password.
    - Once you are logged in, click on your username (your email address) in the upper right corner, then in the dropdown that results, click on "Display my Token".  Your API token will appear in a box labeled "YOUR TOKEN".  Copy it down and save it in a safe place.

- Store that token and only that token in a file named "`open_calais_access_token.txt`" in the root of your django project/site (the same folder where `manage.py` lives).

#### Database configuration

In order to run unit tests, your database configuration in `settings.py` will need to be connecting to the database with a user who is allowed to create databases.  When django runs unit tests, it creates a test database, then deletes it once testing is done.
- _NOTE: This means the database user you use for unit testing SHOULD NOT be the user you'd use in production.  The production database user should not be able to do anything outside a given database._

### Running unit tests

To run unit tests, at the command line in your django project/site folder (where `manage.py` lives):

    python manage.py test context_text.tests
    
Specific sets of tests:

- OpenCalais API (v.2)

    - test OpenCalais configuration:

            python manage.py test context_text.tests.open_calais.test_open_calais_config

    - test OpenCalais automated coding (assumes configuration tests passed):

            python manage.py test context_text.tests.open_calais.test_open_calais_api 

- ArticleCoder (using ManualArticleCoder)

    - test basic methods in ArticleCoder that are re-used by all coding methods:

            python manage.py test context_text.tests.article_coder.test_article_coder

- ManualArticleCoder
            
    - test methods in ManualArticleCoder specific to manual coding:

            python manage.py test context_text.tests.manual_article_coder.test_manual_article_coder
            
- context_text model instances:

    - test Article model
    
            python manage.py test context_text.tests.models.test_Article_model

    - test Article_Data model
    
            python manage.py test context_text.tests.models.test_Article_Data_model

    - test Newspaper model
    
            python manage.py test context_text.tests.models.test_Newspaper_model

    - test Organization (and AbstractOrganization) model
    
            python manage.py test context_text.tests.models.test_Organization_model

    - test Person (and AbstractPerson) model
    
            python manage.py test context_text.tests.models.test_Person_model

- export from context_text to context base:

    - test basic export:
    
            python manage.py test context_text.tests.export.to_context_base.test_export_to_context

## Test data

There is a set of test data stored in the `fixtures` folder inside this django application.  The files:

- **_`context_text_unittest_auth_data.json`_** - User data for article-coding comparison.
- **_`context_text_unittest_django_config_data.json`_** - configuration properties for context_text (in particular, for external APIs).
- **_`context_text_unittest_data.json`_** - actual context_text data - needs to be loaded after "`auth`" data so users who did coding are in database when coding data is loaded.
- **_`context_text_unittest_taggit_data.json`_** - tag data for context_text data (broken at the moment, since it relies on django's content types, and they are dynamically assigned and so not guaranteed to be the same for a given object type across runs of the unit tests).

### Using unittest data for development

### Using unittest data for development

- create a database where the unit test data can live.  I usually call it the name of the main production database ("`research`") followed by "`_test`".  Easiest way to do this is to just create the database, then give the same user you use for your production database the same access they have for production for this test database as well.

    - postgresql example, where production database name is "`research`" and database user is "`django_user`":

            CREATE DATABASE research_test;
            GRANT ALL PRIVILEGES ON DATABASE research_test TO django_user;

- update the DATABASES dictionary in settings.py of the application that contains context_text to point to your test database (in easy example above, could just change the 'NAME' attribute in the 'default' entry to "`research_test`" rather than "`research`".
- cd into your django application's home directory, activate your virtualenv if you created one, then run "`python manage.py migrate`" to create all the tables in the database.

        cd <django_app_directory>
        workon research
        python manage.py migrate

- use the command "`python manage.py createsuperuser`" to make an admin user, for logging into the django admins.

        python manage.py createsuperuser

- load the unit test fixtures into the database:

        python manage.py loaddata context_text_unittest_auth_data.json
        python manage.py loaddata context_text_unittest_django_config_data.json
        python manage.py loaddata context_text_unittest_data.json
        python manage.py loaddata context_text_unittest_taggit_data.json

# Collecting Articles

There is an example application in context_text/collectors/newsbank that you can use as a template for how to gather data and then store it in the database.  It interacts with the newsbank web database, using BeautifulSoup to parse and extract article data.

# Filtering and tagging articles:

To filter and tag sets of articles, use the page: 'http://<your_server>/research/context_text/article/filter/'

This page allows you to filter on:

- Start Date (YYYY-MM-DD)
- End Date (YYYY-MM-DD):    
- * Fancy date range:   
- Publications: 
- Article Tag List (comma-delimited):   
- Unique Identifier List (comma-delimited): 
- Article ID IN List (comma-delimited): 
- String Section Name IN List (comma-delimited):

Then either see a summary of articles that fit your filter, look at details on each matching article, or apply one or more tags to all of the articles matched by your filter criteria.

# Coding articles:

context_text includes a set of pages that can be used to code articles by hand, and then view article coding:

- to code people (subjects, sources, and authors) in articles, use: `http://<your_server>/research/context_text/article/code/`

    - Setup:
    
        - make sure that any user you want to be able to code articles is configured in django as "staff" (and so able to access admins).  They don't need to actually have any access privileges, they just need to be "staff".
    
    - See directions for coding in `context_text/protocol/protocol-capturing_people_in_articles.pdf`.

- to view an article's meta-data and text: `http://<your_server>/research/context_text/article/view/`
- to view an article's coding: `http://<your_server>/research/context_text/article/article_data/view/`

You can also use the django admin pages, but the process is much more cumbersome - there are a lot of interrelated tables that are populated during the process of coding, and so it is better to use the coding form above and let the software deal with making all the correct underlying data.  It is helpful to use the admins for managing Article_Data, however, if you need to clear out coding for a coder, either because of an error or as part of testing.

## Automated Coding

### Setting up a user for the automated coding process

Before you do automated coding, you'll need to create a django user named "automated" to which the coding can be attributed.  To do this:

- Open the django admin: `http://<your_server>/context_text/admin/`

- Log in with the admin user you created when you initialized the database above.

- Once you are logged in, in the "Authentication and Administration" section of the admin, click on "Users".

- You'll see a list of users that have been created in django.  If there is not one named "automated", you'll need to create one.  To start creating a user, click the "Add User +" button in the upper right hand corner of the page.

- This will load a screen where you'll enter a username and a password twice.  Enter a username and password, and then click the "Save" button in the lower right corner.

- Make sure the "automated" user appears in the list.  This user has no ability to access the admin.  It just exists so the automated coding process can link its coding to this user.


### OpenCalais REST API

To use the OpenCalais REST API to code articles, you'll need to first set up a few pieces of information in the django_config application.

Create the following configuration properties, each with the Application value "OpenCalais_REST_API":

    - `open_calais_api_key` - should contain your Open Calais API key.  For more information on getting an Open Calais API key, see: [http://www.opencalais.com/APIkey](http://www.opencalais.com/APIkey)
    - `submitter` - string that identifies the program that is invoking the API - should start with "context_text-", then identify more specifically your project. 
    
Then, the most reliable way to code large numbers of articles is to use the file `context_text/examples/articles/article_coding.py` as a template to set up and run a set of articles through the coder.

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

Once you have coded your articles, you can output network data from them by going to the web page `http://<your_server>/research/context_text/output/network`.  This page outputs a form that lets you select articles and people to include in your network, then will output network data based on what you select.

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

            from context_text.export.network_data_output import NetworkDataOutput

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

For more detailed examples, see the `*.r` R source code files in `context_text/R/`.

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

Copyright 2010-present (2019) Jonathan Morgan

This file is part of [http://github.com/jonathanmorgan/context_text](http://github.com/jonathanmorgan/context_text).

context_text is free software: you can redistribute it and/or modify
it under the terms of the GNU Lesser General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

context_text is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU Lesser General Public License
along with [http://github.com/jonathanmorgan/context_text](http://github.com/jonathanmorgan/context_text).  If not, see
[http://www.gnu.org/licenses/](http://www.gnu.org/licenses/).
