# imports
from sourcenet.models import Article
from sourcenet.models import Article_Data
from sourcenet.models import Article_Subject

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
#valid_contact_type_list = [ Article_Subject.SOURCE_CONTACT_TYPE_DIRECT, Article_Subject.SOURCE_CONTACT_TYPE_EVENT, Article_Subject.SOURCE_CONTACT_TYPE_OTHER ]
valid_contact_type_list = [ Article_Subject.SOURCE_CONTACT_TYPE_DIRECT, Article_Subject.SOURCE_CONTACT_TYPE_EVENT ]

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
    article_source_qs = current_article_data.get_quoted_article_sources_qs()
    
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
        if ( ( source_type is not None ) and ( source_type == Article_Subject.SOURCE_TYPE_INDIVIDUAL ) ):
        
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
