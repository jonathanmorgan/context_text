# imports

# sourcenet Person model
from sourcenet.models import Article_Author
from sourcenet.models import Article_Source
from sourcenet.models import Person
from sourcenet.models import Person_Newspaper

# constants-ish

# control!
DO_UPDATE_PERSONS = False

# declare variables

# name standardization and meta-data creation.
test_HumanName = None
test_person = None
person_qs = None
current_person = None
current_person_author_qs = None
current_person_author = None
current_person_source_qs = None
current_person_source = None
current_person_article_data = None
current_person_article = None
current_person_newspaper_list = []
current_person_newspaper = None
person_newspaper_qs = None
temp_instance = None

# test out name part standardization and full name generation.

test_person = Person.objects.filter( pk = 518 ).get()
test_person.save()

# convert Person's name to HumanName instance
test_HumanName = test_person.to_HumanName()

test_person = Person.objects.filter( pk = 531 ).get()
test_person.save()

# update persons?
if ( DO_UPDATE_PERSONS == True ):

    # get all persons.
    person_qs = Person.objects.all()
    
    # loop.
    for current_person in person_qs:
    
        print( "Current person: " + str( current_person ) )

        # save, to clean name parts and generate full name string.
        current_person.save()
        
        # build list of related newspapers
        current_person_newspaper_list = []
        
        # check to see if there is an Article_Author or Article_Source for the
        #    person.
        current_person_author_qs = Article_Author.objects.filter( person = current_person )
        
        # got any Article_Author records?
        if ( current_person_author_qs.count() > 0 ):
        
            # got at least one author record.
            for current_person_author in current_person_author_qs:
            
                # get article_data
                current_person_article_data = current_person_author.article_data
                
                # get article
                current_person_article = current_person_article_data.article
                
                # get newspaper
                current_person_newspaper = current_person_article.newspaper
                
                # is newspaper in list?
                if ( current_person_newspaper not in current_person_newspaper_list ):
                
                    # append it.
                    current_person_newspaper_list.append( current_person_newspaper )
                    
                #-- END check to see if newspaper in newspaper list. --#
                
            #-- END loop over Article_Author records. --#
            
        # end check to see if related Article_Author records. --#
        
        # check to see if there is an Article_Author or Article_Source for the
        #    person.
        current_person_source_qs = Article_Source.objects.filter( person = current_person )
        
        # got any Article_Source records?
        if ( current_person_source_qs.count() > 0 ):
        
            # got at least one source record.
            for current_person_source in current_person_source_qs:
            
                # get article_data
                current_person_article_data = current_person_source.article_data
                
                # get article
                current_person_article = current_person_article_data.article
                
                # get newspaper
                current_person_newspaper = current_person_article.newspaper
                
                # is newspaper in list?
                if ( current_person_newspaper not in current_person_newspaper_list ):
                
                    # append it.
                    current_person_newspaper_list.append( current_person_newspaper )
                    
                #-- END check to see if newspaper in newspaper list. --#
                
            #-- END loop over Article_Source records. --#
            
        # end check to see if related Article_Source records. --#
        
        print( "- Newspaper list: " + str( current_person_newspaper_list ) )

        # got any newspapers?
        if ( len( current_person_newspaper_list ) > 0 ):
        
            # yes.  loop.
            for current_person_newspaper in current_person_newspaper_list:

                # add newspaper for person
                current_person.associate_newspaper( current_person_newspaper )
                     
            #-- END loop over person's related newspapers. --#
    
        #-- END check to see if newspapers --#
    
    #-- END loop over persons.
    
else:

    print( "DO_UPDATE_PERSONS is set to false.  If you want this script to do anything, edit its source and change DO_UPDATE_PERSONS to True." )

#-- END check to see if we do update. --#