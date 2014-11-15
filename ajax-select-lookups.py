"""
To add a new ajax select:
- Include the import for the model class you will be selecting from at the top of this file (put it in alphabetical order).
- In this file, make a new class that extends LookupParent for the model you want to lookup using AJAX-selects (It is OK to just copy one of the other ones here).  Place it in alphabetical order in the file.
- Modify the get_query() and get_objects() methods to reference the correct model, fields in that model.
- In settings.py, add a line for your new channel to the AJAX_LOOKUP_CHANNELS property, like this, for contributor:
    'contributor' : ('events.ajax-select-lookups', 'ContributorLookup'),
- In admin.py, either add or edit a form attribute to include your channel, and to tell the admin which field to map to which AJAX lookup.  So, for example, in Article, there is the following line:
    form = make_ajax_form( Article, dict( related_articles = 'article', events = 'event' ) )
This line says, for Article, when entering 'related_articles' field, lookup using the 'article' AJAX lookup channel and for the events field use 'event' AJAX lookup channel.  The field names are the names from the model class definition, and can be any type of relation.  Channel names are the keys in AJAX_LOOKIP_CHANNELS in your settings.py file.  So, If you were to add a lookup for contributor, then you'd have:
    form = make_ajax_form( Article, dict( related_articles = 'article', events = 'event', contributors = 'contributor' ) )
"""

from sourcenet.models import Article
from sourcenet.models import Organization
from sourcenet.models import Person
from django.db.models import Q


#===============================================================================#
# Parent Lookup class
#===============================================================================#

class LookupParent( object ):

    my_class = None

    def format_result( self, instance_IN ):

        """ the search results display in the dropdown menu.  may contain html and multiple-lines. will remove any |  """

        # return reference
        string_OUT = ''

        # try converting to string.  If exception, try calling method
        #    output_as_string() instead.
        try:

            # first, try using str()
            string_OUT = str( instance_IN )

        except:

            # if we get here, exception converting.  Try output_as_string()
            string_OUT = instance_IN.output_as_string( True )

        return string_OUT

    #-- END method format_result() --#


    def format_item( self, instance_IN ):

        """ the display of a currently selected object in the area below the search box. html is OK """

         # return reference
        string_OUT = ''
        
        # try converting to string.  If exception, try calling method
        #    output_as_string() instead.
        try:
            
            # first, try using str()
            string_OUT = str( instance_IN )
            
        except:
            
            # if we get here, exception converting.  Try output_as_string()
            string_OUT = instance_IN.output_as_string( True )

        return string_OUT

    #-- END method format_item() --#


    def get_instance_query( self, q, request, class_IN ):

        """
            return a query set if q passed in is an integer, and that number is
            the ID of one of the records in our class's database table.  You
            also have access to request.user if needed.
        """

        # return reference
        query_set_OUT = None

        # define variables
        my_class = None
        q_int = -1
        q_instance = ''

        # store class
        my_class = class_IN

        # is the q a number?
        try:

            # try casting the query string to int.
            q_int = int( q )

            # it is an int.  See if there is a match for this ID.
            q_instance = my_class.objects.get( pk = q_int )

            # got a match?
            if ( q_instance ):

                # it is a match - return query set with that article in it.
                query_set_OUT = my_class.objects.filter( Q( pk__in = [ q ] ) )

            else:

                # no match found.  Return None.
                query_set_OUT = None

            #-- END check to see if we got an instance. --#

        except:

            # not an integer.  set found to false.
            #found_instance = False
            query_set_OUT = None

        #-- END attempt to pull in instance by ID --#

        return query_set_OUT

    #-- END method get_instance_query() --#

#-- END class LookupParent --#


#===============================================================================#
# Individual child Lookup classes
#===============================================================================#


class ArticleLookup( LookupParent ):

    my_class = Article	

    def get_query( self, q, request ):

        """
        return a query set.  you also have access to request.user if needed
        """

        # return reference
        query_set_OUT = None

        # is the q a number and is it the ID of an article?
        query_set_OUT = self.get_instance_query( q, request, self.my_class )

        # got anything back?
        if ( query_set_OUT is None ):

            # No exact match for q as ID.  Return search of text in contributor.
            query_set_OUT = self.my_class.objects.filter( Q( unique_identifier__icontains = q ) | Q( headline__icontains = q ) )

        #-- END retrieval of query set when no ID match. --#

        return query_set_OUT

    #-- END method get_query --#


    def get_objects(self,ids):

        """
        given a list of ids, return the objects ordered as you would like them
            on the admin page.  This is for displaying the currently selected
            items (in the case of a ManyToMany field)
        """
        return self.my_class.objects.filter(pk__in=ids).order_by( 'unique_identifier', 'headline' )

    #-- END method get_objects --#

#-- END class ArticleLookup --#


class OrganizationLookup( LookupParent ):

    my_class = Organization

    def get_query( self, q, request ):

        """
        return a query set.  you also have access to request.user if needed
        """

        # return reference
        query_set_OUT = None

        # is the q a number and is it the ID of an contributor?
        query_set_OUT = self.get_instance_query( q, request, self.my_class )

        # got anything back?
        if ( query_set_OUT is None ):

            # No exact match for q as ID.  Return search of text in contributor.
            query_set_OUT = self.my_class.objects.filter( Q( name__icontains = q ) | Q( description__icontains = q ) )

        #-- END retrieval of query set when no ID match. --#

        return query_set_OUT

    #-- END method get_query --#


    def get_objects(self,ids):

        """
        given a list of ids, return the objects ordered as you would like them
            on the admin page.  This is for displaying the currently selected
            items (in the case of a ManyToMany field)
        """
        return self.my_class.objects.filter(pk__in=ids).order_by( 'name', 'description' )

    #-- END method get_objects --#

#-- END class OrganizationLookup --#


class PersonLookup( LookupParent ):

    my_class = Person
    
    def get_query( self, q, request ):

        """
        return a query set.  you also have access to request.user if needed
        """

        # return reference
        query_set_OUT = None

        # define variables

        # is the q a number and is it the ID of an contributor?
        query_set_OUT = self.get_instance_query( q, request, self.my_class )

        # got anything back?
        if ( query_set_OUT is None ):

            # No exact match for q as ID.  Return search of text in contributor.
            query_set_OUT = self.my_class.objects.filter( Q( first_name__icontains = q ) | Q( middle_name__icontains = q ) | Q( last_name__icontains = q ) | Q( full_name_string__icontains = q ) )

        #-- END retrieval of query set when no ID match. --#

        return query_set_OUT

    #-- END method get_query --#


    def get_objects(self,ids):

        """
        given a list of ids, return the objects ordered as you would like them
            on the admin page.  This is for displaying the currently selected
            items (in the case of a ManyToMany field)
        """
        return self.my_class.objects.filter(pk__in=ids).order_by('last_name','first_name','middle_name')

    #-- END method get_objects --#

#-- END class PersonLookup --#