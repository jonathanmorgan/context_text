# imports
from sourcenet.models import Article
from sourcenet.models import Article_Data
from sourcenet.models import Article_Source

# Django imports
from django.db.models import Q
from django.contrib.auth.models import User

# six
import six

# declare variables
article_data_qs = None
user1 = None
user2 = None
contact_type_count_dict = {}
current_article_data = None
article_source_qs = None
source_count_dict = {}
invalid_source_count_dict = {}
source_count = -1
current_article_source = None
source_person_id = -1
source_type = ""
individual_source_count = -1
contact_type = ""
contact_type_count = -1
valid_contact_type_list = []
source_person_count = -1

# declare variables for seeing if invalid people are also valid.
invalid_person_id = -1
invalid_person_count = -1
person_id = -1
person_count = -1

# variables for storing tags.
current_article = None
current_article_id = -1
current_article_tags = None
current_tag = None
tag_dict_name_tag_instance = "tag_instance"
current_tag_name = ""
current_tag_info_dict = {}
tag_counter = -1
tag_dict_name_count = "tag_count"
tag_article_id_list = []
tag_dict_name_article_id_list = "article_id_list"
tag_to_info_map = {}

# first, get article data objects.
article_data_qs = Article_Data.objects.all()

# next set up basic filters to match the network output I've been testing

# filter pub dates
article_data_qs = article_data_qs.filter( article__pub_date__gte = '2009-12-06' )
article_data_qs = article_data_qs.filter( article__pub_date__lte = '2009-12-12' )
print( "- count after date filtering: " + str( article_data_qs.count() ) ) # 151

# filter newspaper
article_data_qs = article_data_qs.filter( article__newspaper_id = 1 )
print( "- count after paper filtering: " + str( article_data_qs.count() ) ) # 121

# now, need to see how many have Article_Data coded by either brianbowe or
#    jonathanmorgan.

# get users.
user1 = User.objects.get( username = 'jonathanmorgan' )
user2 = User.objects.get( username = 'brianbowe' )
article_data_qs = article_data_qs.filter( coder__in = [ user1, user2 ] )
print( "- count after coder filtering: " + str( article_data_qs.count() ) ) # 121

# limit to one per article.
article_data_qs = article_data_qs.order_by( "article_id" )
article_data_qs = article_data_qs.distinct( "article_id" )
print( "- after distinct( \"article\" ) filtering: " + str( article_data_qs.count() ) ) # 121

# valid contact types.
#valid_contact_type_list = [ Article_Source.SOURCE_CONTACT_TYPE_DIRECT, Article_Source.SOURCE_CONTACT_TYPE_EVENT, Article_Source.SOURCE_CONTACT_TYPE_OTHER ]
valid_contact_type_list = [ Article_Source.SOURCE_CONTACT_TYPE_DIRECT, Article_Source.SOURCE_CONTACT_TYPE_EVENT ]

# now, count how many article_source of each contact type.
contact_type_count_dict = {}
source_count_dict = {}
source_count = 0
individual_source_count = 0
invalid_source_count_dict = {}
source_person_count = 0


#===============================================================================
# Loop over Article_Data instances.
#===============================================================================
for current_article_data in article_data_qs:

    # get list of article sources.
    article_source_qs = current_article_data.article_source_set.all()
    
#===============================================================================
# Article information.
#===============================================================================

    # get article.
    current_article = current_article_data.article
    current_article_id = current_article.id
    
    # print( "====> article: " + str( current_article ) )
    
    # get tags for this article.
    current_article_tags = current_article.tags.all()
    
    # got any tags?
    if ( ( current_article_tags is not None ) and ( len( current_article_tags ) > 0 ) ):
    
        # yes - for each tag, look it up in tag_to_info_map.  If tag is already
        #    in map, get info dict, update it (increment count, add ID to list).
        #    If not in map, make info dict, init count to 1 and list to have id
        #    of current article, then relate info to tag name.
        for current_tag in current_article_tags:
        
            # retrieve tag name
            current_tag_name = current_tag.name
        
            # print( "========> tag: " + current_tag_name )
            # print( tag_to_info_map )
            
            # look for tag in tag_to_info_map.
            if ( current_tag_name in tag_to_info_map ):
            
                # yes - get info dictionary.
                current_tag_info_dict = tag_to_info_map.get( current_tag_name, {} )
                
                # get existing info
                tag_counter = current_tag_info_dict.get( tag_dict_name_count, 0 )
                tag_article_id_list = current_tag_info_dict.get( tag_dict_name_article_id_list, [] )
            
                # update info
                tag_counter = tag_counter + 1
                tag_article_id_list.append( current_article_id )
                
                # update info dictionary
                current_tag_info_dict[ tag_dict_name_count ] = tag_counter
                current_tag_info_dict[ tag_dict_name_article_id_list ] = tag_article_id_list
                
                # dictionary is an object, should be referred to by reference in
                #    tag_to_info_map, so no need to update the map.
            
            else:

                # create info dictionary.
                current_tag_info_dict = {}
                current_tag_info_dict[ tag_dict_name_tag_instance ] = current_tag
                current_tag_info_dict[ tag_dict_name_count ] = 1
                current_tag_info_dict[ tag_dict_name_article_id_list ] = [ current_article_id, ]
                
                # store in tag_to_info_map
                tag_to_info_map[ current_tag_name ] = current_tag_info_dict

            #-- END check to see if tag already in map. --#
        
        #-- END loop over tags. --#
    
    #-- END check to see if any tags assigned to this article --#

#===============================================================================
# Article Sources.
#===============================================================================

    # loop over sources for current article.
    for current_article_source in article_source_qs:
    
        # increment source_count
        source_count += 1
    
        # increment the counter for the source person.
        source_person_id = current_article_source.person_id
        source_person_count = source_count_dict.get( source_person_id, 0 )
        source_person_count += 1
        source_count_dict[ source_person_id ] = source_person_count

        # get source type
        source_type = current_article_source.source_type
        
        # only process if individual
        if ( ( source_type is not None ) and ( source_type == Article_Source.SOURCE_TYPE_INDIVIDUAL ) ):
        
            # increment counter.
            individual_source_count += 1
            
            # it is an individual get source_contact_type
            contact_type = current_article_source.source_contact_type
            
            # increment the counter for contact_type.
            contact_type_count = contact_type_count_dict.get( contact_type, 0 )
            contact_type_count += 1
            contact_type_count_dict[ contact_type ] = contact_type_count
            
            # valid contact type?
            if contact_type not in valid_contact_type_list:
            
                # invalid contact type - output details on source.
                print( "- source with invalid contact type ( " + contact_type + " ): " + str( current_article_source ) )
                
                # increment the counter for the invalid source person.
                source_person_count = invalid_source_count_dict.get( source_person_id, 0 )
                source_person_count += 1
                invalid_source_count_dict[ source_person_id ] = source_person_count
            
            #-- END check to see if valid contact type. --#
            
        #-- END check to see if "individual" --#
        
    #-- END loop over sources --#
    
#-- END loop over article data. --#

#===============================================================================
# Sources with contact types other than those we included.
#===============================================================================

invalid_person_id = -1
invalid_person_count = -1
person_count = -1

# see if the invalid people are in the plain old source dict.
for invalid_person_id, invalid_person_count in six.iteritems( invalid_source_count_dict ):

    # see if person is in actual source map.
    if invalid_person_id in source_count_dict:
    
        # yes.  See if counts differ.
        person_count = source_count_dict.get( invalid_person_id, 0 )
        if ( person_count > invalid_person_count ):
        
            print( "- Person " + str( invalid_person_id ) + " is both invalid and valid." )
            
        else:
        
            print( "- Person " + str( invalid_person_id ) + " is invalid." )
            
        #-- END check to see if person was both valid and invalid source. --#
    
    #-- END check to see if person in actual map. --#
    
#-- END loop over invalid sources --#

print( "- After looping over data, total source = " + str( source_count ) +"; individuals = " + str( individual_source_count ) )
print( contact_type_count_dict )

#===============================================================================
# Article tag summary.
#===============================================================================

# print( tag_to_info_map )
print( "====> Tag summary:" )

# output summary of tags assigned to the articles.
for current_tag_name, current_tag_info_dict in six.iteritems( tag_to_info_map ):

    # get details for this tag.
    current_tag = current_tag_info_dict.get( tag_dict_name_tag_instance, None )
    current_tag_name = current_tag.name
    tag_counter = current_tag_info_dict.get( tag_dict_name_count, 0 )
    tag_article_id_list = current_tag_info_dict.get( tag_dict_name_article_id_list, [] )

    # output details
    print( "- tag \"" + current_tag_name + "\": count = " + str( tag_counter ) )
    print( "    - article ID list: " + str( tag_article_id_list ) )
    
#-- END loop over tags assigned to selected articles. --#