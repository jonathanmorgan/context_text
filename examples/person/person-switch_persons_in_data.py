from __future__ import unicode_literals

# imports

# context_text imports
from context_text.data.person_data import PersonData

# constants-ish

# control!
DO_UPDATES = False

# declare variables
FROM_person_id = None
TO_person_id = None
switch_status = None
status_message_list = []
status_message = ""

# first, set the IDs of the persons we will be switching from and to.
#FROM_person_id = 136 # Matt VandenBunte
#TO_person_id = 591 # Matt VandeBunte

FROM_person_id = 318 # Myron Kulka
TO_person_id = 599 # Myron Kukla

# call PersonData.switch_persons_in_data()
switch_status = PersonData.switch_persons_in_data( FROM_person_id, TO_person_id, do_updates_IN = DO_UPDATES )

# Output summary
print( "switch_status = " + str( switch_status.status_code ) )

# status messages
status_message_list = switch_status.get_message_list()
for status_message in status_message_list:

    # output status message:
    print( "- " + status_message )

#-- END loop over status message list. --#
