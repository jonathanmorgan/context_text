# imports

# sourcenet Person model
from sourcenet.models import Article_Author
from sourcenet.models import Article_Source
from sourcenet.models import Person

# constants-ish

# control!
DO_UPDATES = False

# declare variables
FROM_person_id = None
TO_person_id = None
FROM_person = None
TO_person = None
article_author_id_list = []
article_author_qs = None
article_author = None
article_author_id = -1
article_author_count = -1
article_source_id_list = []
article_source_qs = None
article_source = None
article_source_id = -1
article_source_count = -1

# first, set the IDs of the persons we will be switching from and to.

#FROM_person_id = 136 # Matt VandenBunte
#TO_person_id = 591 # Matt VandeBunte

FROM_person_id = 318 # Myron Kulka
TO_person_id = 599 # Myron Kukla

# Look up Person instances for each.
FROM_person = Person.objects.get( id = FROM_person_id )
TO_person = Person.objects.get( id = TO_person_id )

# make sure we found one for each.
if ( ( FROM_person is not None ) and ( TO_person is not None ) ):

    # find all Article_Source and Article_Author records that refer the the FROM
    #    person.
    article_author_qs = FROM_person.sourcenet_article_author_original_person_set.all()
    article_source_qs = FROM_person.sourcenet_article_source_original_person_set.all()
    
    # loop over author records
    for article_author in article_author_qs:
    
        # get ID, add to list.
        article_author_id = article_author.id
        article_author_id_list.append( article_author_id )
        
        # do updates?
        if ( DO_UPDATES == True ):
                    
            # yes.
            
            # then set article_author.person to article_author.original_person.
            article_author.person = article_author.original_person
            
            # empty out article_author.original_person.
            article_author.original_person = None

            # save
            article_author.save()
        
        #-- END check to see if we update. --#
    
    #-- END loop over authors --#

    # loop over source records
    for article_source in article_source_qs:
    
        # get ID, add to list.
        article_source_id = article_source.id
        article_source_id_list.append( article_source_id )
        
        # do updates?
        if ( DO_UPDATES == True ):
        
            # yes.
            
            # then set article_source.person to article_source.original_person.
            article_source.person = article_source.original_person
            
            # empty out article_source.original_person.
            article_source.original_person = None

            # save
            article_source.save()
        
        #-- END check to see if we update. --#
    
    #-- END loop over sources --#

else:

    print( "ERROR - don't have both FROM and TO persons." )
    
#-- END check to see if we have FROM and TO persons. --#

# Output summary
print( "UNDO switching associated person." )
print( "- FROM: " + str( FROM_person ) )
print( "- TO: " + str( TO_person ) )

# do updates?
if ( DO_UPDATES == True ):

    print( "\nDO_UPDATES = True, UPDATED THE FOLLOWING:")

else:

    print( "\nDO_UPDATES = False, NO CHANGES MADE!")

#-- END check to see if we made updates or not --#article_author_count = len( article_author_id_list )

article_author_count = len( article_author_id_list )
article_source_count = len( article_source_id_list )

print( "\nUpdating " + str( article_author_count ) + " Article_Author instances: " + str( article_author_id_list ) )
print( "Updating " + str( article_source_count ) + " Article_Source instances: " + str( article_source_id_list ) )