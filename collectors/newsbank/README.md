# NewsBank collector

## Introduction

These Collector files are an example of how to pull articles from an external source and store them in the sourcenet database tables.

They are based on interacting with the NewsBank article repository's web interface.  This program interacts with the newsbank web database via HTTP, using BeautifulSoup to parse and extract article data from HTML.

## Installation

This collector depends on classes that are a part of the python_utilities github repository:

https://github.com/jonathanmorgan/python_utilities

See that repo for more information on downloading and installing (it is easy, though - just clone the repository and place it somewhere in your python path.)

If you followed the directions in sourcenet's README.md file, clone python utilities into the research folder alongside sourcenet:

        git clone https://github.com/jonathanmorgan/python_utilities.git

## Usage

To run the collector:
* the script run_collector.py is used to retrieve articles from the web.  It accepts the following command line options:
    * -s | --start_date             - Start date of date range to collect, in YYYY-MM-DD format.
    * -e | --end_date               - End date of date range to collect, in YYYY-MM-DD format.
    * -d | --single_date            - Single date to collect, in YYYY-MM-DD format.
    * -l | --date_list              - List of dates to collect, in YYYY-MM-DD format, separated by commas.
    * -o | --output_directory       - Path of directory into which we will place articles that we gather.
    * -p | --place_code             - Place code of news organization whose papers we will gather.  Defaults to Grand Rapids Press (GRPB).  Detroit News = DTNB.
    * -m | --output_to_database     - If present, parses and stores articles into database in addition to storing them on the file system.
    * -f | --output_to_files        - If present, stores article HTML on the file system (to path in --output_directory).
    * -i | --ignore_missing_issues  - If present, allows for gaps in date range where issues are missing.
    * -a | --email_from             - Email address from which you want status emails to be sent.
    * -b | --email_to               - Email address(es - if multiple, comma-separated list) to which you want status emails to be sent.

* the script run_databaser.py is a convenience script for looping over articles stored on the file system and placing them into the database.  It can be used if you need to first store articles to the file system, then want to parse them and load them into the database later.

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