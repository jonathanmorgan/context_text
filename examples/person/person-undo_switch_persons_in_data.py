# imports

# sourcenet Person model
from sourcenet.models import Article_Author
from sourcenet.models import Article_Subject
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
article_subject_id_list = []
article_subject_qs = None
article_subject = None
article_subject_id = -1
article_subject_count = -1

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

    # find all Article_Subject and Article_Author records that refer the the FROM
    #    person.
    article_author_qs = FROM_person.sourcenet_article_author_original_person_set.all()
    article_subject_qs = FROM_person.sourcenet_article_subject_original_person_set.all()
    
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

    # loop over subject records
    for article_subject in article_subject_qs:
    
        # get ID, add to list.
        article_subject_id = article_subject.id
        article_subject_id_list.append( article_subject_id )
        
        # do updates?
        if ( DO_UPDATES == True ):
        
            # yes.
            
            # then set article_subject.person to article_subject.original_person.
            article_subject.person = article_subject.original_person
            
            # empty out article_subject.original_person.
            article_subject.original_person = None

            # save
            article_subject.save()
        
        #-- END check to see if we update. --#
    
    #-- END loop over subjects --#

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
article_subject_count = len( article_subject_id_list )

print( "\nUpdating " + str( article_author_count ) + " Article_Author instances: " + str( article_author_id_list ) )
print( "Updating " + str( article_subject_count ) + " Article_Subject instances: " + str( article_subject_id_list ) )