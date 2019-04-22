# python imports
from __future__ import print_function
import json

# python utilities
from python_utilities.network.http_helper import Http_Helper

# import AlchemyAPI object
# installation instructions: https://github.com/ubergrape/pycalais
from calais.base.client import Calais

# context_text imports
from context_text.models import Article
from context_text.models import Article_Text

# declare functions
def print_calais_json( json_IN ):

    # loop over the stuff in the response:
    item_counter = 0
    current_container = json_IN
    for item in current_container.keys():
    
        item_counter += 1
        print( "==> " + str( item_counter ) + ": " + item )
        
        current_property = "_type"
        if ( current_property in current_container[ item ] ):
            current_property_value = current_container[ item ][ current_property ]
            print( "----> " + current_property + ": " + current_property_value )
            if ( ( current_property_value == "Quotation" ) or ( current_property_value == "Person" ) ):
                print( current_container[ item ] )
            #-- END check to see if type is "Quotation" --#
        #-- END current_property --#
        current_property = "_typeGroup"
        if ( current_property in current_container[ item ] ):
            current_property_value = current_container[ item ][ current_property ]
            print( "----> " + current_property + ": " + current_property_value )
        #-- END current_property --#
        current_property = "commonname"
        if ( current_property in current_container[ item ] ):
            current_property_value = current_container[ item ][ current_property ]
            print( "----> " + current_property + ": " + current_property_value )
        #-- END current_property --#
        current_property = "name"
        if ( current_property in current_container[ item ] ):
            current_property_value = current_container[ item ][ current_property ]
            print( "----> " + current_property + ": " + current_property_value )
        #-- END current_property --#
        current_property = "person"
        if ( current_property in current_container[ item ] ):
            current_property_value = current_container[ item ][ current_property ]
            print( "----> " + current_property + ": " + current_property_value )
        #-- END current_property --#
        
    #-- END loop over items --#
    
#-- END function print_calais_json --#


# declare variables

# Direct call to Calais REST API
calais_REST_API_URL = "http://api.opencalais.com/tag/rs/enrich"
calais_api_key = "8dpcmw82wtpr4m3q5ju28ybw"
calais_submitter = "context_text-testing"

# calais API package - pycalais
my_calais_API = None

# article to analyze
article_id = -1
article = None
article_text = None
article_body_html = ""
article_body_text = ""

# HTTP_Helper
my_http_helper = None
requests_response = None

# response
calais_response = None
entity_list = None
entity_type = ""
entity_text = ""
person_name = ""
person_name_to_entity_map = {}

# "relations" request type (subject-verb-object NLP sentence parsing)
relations_response = None
relation_action = None
relation_action_text = ""
relation_action_verb_text = ""
relation_subject = None
relation_subject_text = ""

# create Calais instance
my_calais_API = Calais( calais_api_key, submitter = calais_submitter )

# retrieve an article to try out.
article_id = 327069
article = Article.objects.get( id = article_id )

# then, get text.
article_text = article.article_text_set.get()

# retrieve article body
article_body_html = article_text.get_content()
article_body_text = article_text.get_content_sans_html()

#================================================================================
# pycalais
#================================================================================

# try the API - uses 
calais_response = my_calais_API.analyze( article_body_text )

# to see the raw response body:
calais_raw_response = calais_response.raw_response

# look for entities
calais_response.entities

# loop over the entities:
print( "=============================================" )
print( "calais_response.entities" )
print( "=============================================" )
print_calais_json( calais_response.entities )

# look for relations
calais_response.relations

# loop over the relations:
print( "=============================================" )
print( "calais_response.relations" )
print( "=============================================" )
print_calais_json( calais_response.relations )

#================================================================================
# Roll your own request
#================================================================================

# make a POST request using Http_Helper.
my_http_helper = Http_Helper()

# set up call to REST API.
my_http_helper.set_http_header( "x-calais-licenseID", calais_api_key, None )

# NOTE - does not deal well with HTML - send it raw text!
my_http_helper.set_http_header( "Content-Type", "TEXT/RAW", None )

my_http_helper.set_http_header( "outputformat", "Application/JSON", None )
my_http_helper.set_http_header( "submitter", "context_text testing", None )

# request type
my_http_helper.request_type = Http_Helper.REQUEST_TYPE_POST

# make the request - NOTE - does not deal well with HTML - send it raw text!
requests_response = my_http_helper.load_url_requests( calais_REST_API_URL, data_IN = article_body_text )

# raw text:
requests_raw_text = requests_response.text

# convert to a json object:
requests_response_json = requests_response.json()

# loop over the stuff in the response:
print( "=============================================" )
print( "requests_response_json" )
print( "=============================================" )
print_calais_json( requests_response_json )


'''
# response will be in json - get entities
entity_list = combined_response[ "entities" ]

# loop over entities, look for people.
for entity in entity_list:

    # type
    entity_type = entity[ "type" ]
    entity_text = entity[ "text" ]
    
    # person?
    if ( entity_type == "Person" ):
    
        # person_name = entity_text
        person_name = entity_text
        
        print( "==> Person: " + person_name )
        
        person_name_to_entity_map[ person_name ] = entity
        
    #-- END check to see if person. --#

#-- END loop over entities --#

# now, try relation extraction - subject-verb-object parsing
relations_response = my_alchemy_API.relations( 'text', article_body_text )

# get relations
relations_list = relations_response[ "relations" ]

# loop
for relation in relations_list:

    # get action (verb) and subject (actor)
    relation_action = relation[ "action" ]
    relation_subject = relation[ "subject" ]
    
    # from action, get actual verb text, root verb
    relation_action_text = relation_action[ "text" ]
    relation_action_verb_text = relation_action[ "verb" ][ "text" ]
    
    # from subject, get actual text
    relation_subject_text = relation_subject[ "text" ]

    # output summary
    print( "==> Subject: " + relation_subject_text + "; Action: " + relation_action_text + "; verb: " + relation_action_verb_text )
    
    # for each, look for the people found above in the subject.
    for name, entity in person_name_to_entity_map.items():
    
        # check to see if the current name is in the current subject.
        if ( relation_subject_text.find( name ) > -1 ):
    
            # yes - person is in subject.
            print( "====> Person " + name + " is in subject " + relation_subject_text )
    
        #-- END check to see if person is in subject. --#
    
    #-- END loop over people in article. --#

    # check to see if the verb is a said verb...

#-- END loop over relations --#
'''