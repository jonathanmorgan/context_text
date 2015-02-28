# imports

# nameparser
from nameparser import HumanName

# sourcenet Person model
from sourcenet.models import Article_Author
from sourcenet.models import Article_Source
from sourcenet.models import Person
from sourcenet.models import Person_Newspaper

# constants-ish

# STATUSes
STATUS_FOUND = "found"
STATUS_NEW = "new"
STATUS_NONE = "None"

# control!
DO_UPDATE_PERSONS = False

def print_HumanName( human_name_IN ):

    print( "HumanName: \"" + unicode( human_name_IN ) + "\"" )
    print( "- title: " + human_name_IN.title )
    print( "- first: " + human_name_IN.first ) 
    print( "- middle: " + human_name_IN.middle )
    print( "- last: " + human_name_IN.last )
    print( "- suffix: " + human_name_IN.suffix )
    print( "- nickname: " + human_name_IN.nickname )

#-- END function print_HumanName() --#

def get_person_lookup_status( person_IN ):
    
    # return reference
    status_OUT = ""
    
    # declare variables
    
    if ( person_IN is not None ):
    
        if ( ( person_IN.id ) and ( person_IN.id > 0 ) ):
        
            # there is an ID, so this is not a new record.
            status_OUT = STATUS_FOUND
            
        else:
        
            # Person returne, but no ID, so this is a new record - not found.
            status_OUT = STATUS_NEW
            
        #-- END check to see if ID present in record returned. --#
            
    else:
    
        # None - either multiple matches (eek!) or error.
        status_OUT = STATUS_NONE
    
    #-- END check to see if None. --#

    return status_OUT
    
#-- END function get_person_lookup_status() --#

# declare variables
name = ""
parsed = None
manual = None
test1 = None
test2 = None
name_part_list = []
name_part_count = -1

# lookups for two-part names.
hn_first = None
hn_first_last = None
hn_last = None
person_first = None
person_first_last = None
person_last = None
status_first = ""
status_first_last = ""
status_last = ""

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

# Store problematic name:
name = "Van Conway"

# In original article, this is a first name and a last name.

# let nameparser parse
parsed = HumanName( name )

# look at how that turned out:
print( "Parsed HumanName for " + name + ":" )
print_HumanName( parsed )

# now, make a second HumanName instance.
manual = HumanName()

# look at how that turned out:
print( "Empty HumanName?:" )
print_HumanName( manual )

# override parsed values with correct name parts
manual.first = "Van"
manual.last = "Conway"

# look at how that turned out:
print( "after manual configuration:" )
print_HumanName( manual )

# now, try some lookups

# let the lookup parse the name.
test1 = Person.look_up_person_from_name( name )
print( "test1 = " + str( test1 ) )

# pass in manually configured HumanName
test2 = Person.look_up_person_from_name( name, manual )
print( "test2 = " + str( test2 ) )

# how to best deal with two word names?
name_part_list = name.split()
name_part_count = len( name_part_list )

print( "Name list: " + str( name_part_list ) + "; len: " + str( name_part_count ) )

# first, see if two words.
if ( name_part_count == 2 ):

    # yes.  See if parsed name has first and last name.
    if ( ( parsed.first == "" ) or ( parsed.last == "" ) ):
    
        # no, parser results in empty first name or last name.  See if there is a
        #    match for the three most likely potential interpretations of a two-
        #    word name - all first, all last, or first-last.

        # both in first
        hn_first = HumanName()
        hn_first.first = name
        person_first = Person.get_person_for_name( name, create_if_no_match_IN = True, parsed_name_IN = hn_first )
        status_first = get_person_lookup_status( person_first )
        print( "status from all in first name: " + status_first )
    
        # first then last
        hn_first_last = HumanName()
        hn_first_last.first = name_part_list[ 0 ]
        hn_first_last.last = name_part_list[ 1 ]
        person_first_last = Person.get_person_for_name( name, create_if_no_match_IN = True, parsed_name_IN = hn_first_last )
        status_first_last = get_person_lookup_status( person_first_last )
        print( "status from all in first name: " + status_first_last )

        # both in last
        hn_last = HumanName()
        hn_last.last = name
        person_last = Person.get_person_for_name( name, create_if_no_match_IN = True, parsed_name_IN = hn_last )
        status_last = get_person_lookup_status( person_last )
        print( "status from all in first name: " + status_last )
    
    else:
    
        # Name parsed as two words, so go with parsed name?
        pass
    
    #-- END check to see if both first and last name. --#

#-- END check to see if two-part name. --#

# look for people with same full-string name.

# exactly the same.

# with the name parts inside, in the same order

# just the first and last name?

# update persons?

# test out name part standardization and full name generation.

test_person = Person.objects.filter( pk = 518 ).get()
test_person.save()

# convert Person's name to HumanName instance
test_HumanName = test_person.to_HumanName()

test_person = Person.objects.filter( pk = 531 ).get()
test_person.save()

if ( DO_UPDATE_PERSONS == True ):

    # get all persons.
    person_qs = Person.objects.all()
    
    # loop.
    for current_person in person_qs:
    
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

        # got any newspapers?
        if ( len( current_person_newspaper_list ) > 0 ):
        
            # yes.  loop.
            for current_person_newspaper in current_person_newspaper_list:
            
                # see if Person_Newspaper for this newspaper.
                person_newspaper_qs = current_person.person_newspaper_set.filter( newspaper = current_person_newspaper )
                if ( person_newspaper_qs.count() == 0 ):
                
                    # No. Relate newspaper to person.
                    temp_instance = Person_Newspaper()

                    # set values
                    temp_instance.person = current_person
                    temp_instance.newspaper = current_person_newspaper
                    # temp_instance.notes = ""
                    
                    # save.
                    temp_instance.save()
                
                # -- END check to see if Person_Newspaper for current paper. --#
            
            #-- END loop over person's related newspapers. --#
    
        #-- END check to see if newspapers --#
    
    #-- END loop over persons.
    
#-- END check to see if we do update. --#