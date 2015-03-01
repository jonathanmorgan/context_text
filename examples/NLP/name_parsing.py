# imports

# nameparser
from nameparser import HumanName

# sourcenet Person model
from sourcenet.models import Article_Author
from sourcenet.models import Article_Source
from sourcenet.models import Person
from sourcenet.models import Person_Newspaper

# constants-ish

# declare variables
name = ""
parsed = None
manual = None
test1 = None
test2 = None
test3 = None
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

# full-name testing
full_name_test = ""

# Store problematic name:
name = "Van Conway"

# In original article, this is a first name and a last name.

# let nameparser parse
parsed = HumanName( name )

# look at how that turned out:
print( "Parsed HumanName for " + name + ":" )
print( Person.HumanName_to_str( parsed ) )

# now, make a second HumanName instance.
manual = HumanName()

# look at how that turned out:
print( "Empty HumanName?:" )
print( Person.HumanName_to_str( manual ) )

# override parsed values with correct name parts
manual.first = "Van"
manual.last = "Conway"

# look at how that turned out:
print( "after manual configuration:" )
print( Person.HumanName_to_str( manual ) )

# now, try some lookups

# let the lookup parse the name.
test1 = Person.look_up_person_from_name( name )
print( "test1 = " + str( test1 ) )

# pass in manually configured HumanName
test2 = Person.look_up_person_from_name( name, manual )
print( "test2 = " + str( test2 ) )

# try exact match
test3 = Person.look_up_person_from_name( name, manual, do_strict_match_IN = True )
print( "test3 (strict) = " + str( test3 ) )

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
        status_first = Person.get_person_lookup_status( person_first )
        print( "status from both in first: " + status_first )
    
        # first then last
        hn_first_last = HumanName()
        hn_first_last.first = name_part_list[ 0 ]
        hn_first_last.last = name_part_list[ 1 ]
        person_first_last = Person.get_person_for_name( name, create_if_no_match_IN = True, parsed_name_IN = hn_first_last )
        status_first_last = Person.get_person_lookup_status( person_first_last )
        print( "status from first then last: " + status_first_last )

        # both in last
        hn_last = HumanName()
        hn_last.last = name
        person_last = Person.get_person_for_name( name, create_if_no_match_IN = True, parsed_name_IN = hn_last )
        status_last = Person.get_person_lookup_status( person_last )
        print( "status from both in last: " + status_last )
    
    else:
    
        # Name parsed as two words, so go with parsed name?
        pass
    
    #-- END check to see if both first and last name. --#

#-- END check to see if two-part name. --#

# look for people with same full-string name.

# get full name from parsed.
full_name_test = unicode( parsed )
print( "FULL NAME - looking for \"" + full_name_test + "\"" )

full_name_qs = Person.objects.filter( full_name_string__iexact = full_name_test )
full_name_count = full_name_qs.count()
if ( full_name_count > 0 ):

    for full_name_match in full_name_qs:
    
        print( "- FULL NAME - full name match: " + str( full_name_match ) )
        
    #-- END loop over full name matches --#
    
else:

    print( "- FULL NAME - no full name match for \"" + full_name_test + "\"" )

#-- END check to see if any matches. --#

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

# Make a person with middle name set to None.
person_create_test = Person()
person_create_test.first_name = "Van"
person_create_test.middle_name = None
person_create_test.last_name = "Clyborn"
person_create_test.nickname = ""
#person_create_test.save()