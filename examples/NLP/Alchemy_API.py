# python imports
from __future__ import print_function
import json

# import AlchemyAPI object
# installation instructions: http://www.alchemyapi.com/developers/getting-started-guide/using-alchemyapi-with-python/
from alchemyapi_python.alchemyapi import AlchemyAPI

# context_text imports
from context_text.models import Article
from context_text.models import Article_Text

# declare variables
my_alchemy_API = None
article_id = -1
article = None
article_text = None
article_body_html = ""
article_body_text = ""

# "combined" request type - entities, keywords and concepts
combined_response = None
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

# create AlchemyAPI instance
my_alchemy_API = AlchemyAPI()

# retrieve an article to try out.
article_id = 327069
article = Article.objects.get( id = article_id )

# then, get text.
article_text = article.article_text_set.get()

# retrieve article body
article_body_html = article_text.get_content()
article_body_text = article_text.get_content_sans_html()

# try the API - combined - not available for HTML.
combined_response = my_alchemy_API.combined( 'text', article_body_text )

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