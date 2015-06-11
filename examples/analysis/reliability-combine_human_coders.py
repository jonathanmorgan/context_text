from __future__ import unicode_literals

# python library imports
import copy

# python package imports
import six

# django imports
from django.contrib.auth.models import User

# sourcenet imports
from sourcenet.models import Analysis_Reliability_Names
from sourcenet.models import Article
from sourcenet.models import Person

# declare variables
coder_rs = None
current_coder = None
current_coder_id = -1
coder_index = -1
coder_id_to_index_dict = {}
coder_id_to_instance_dict = {}

# declare variables - information on combining
combine_index_list = [ 1, 3 ]
new_label = "prelim_network_combined"

# declare variables - processing
reliability_qs = None
reliability_name_row = None
reliability_row_id = -1
new_reliability_row = None
current_article = None
article_data_qs = None
current_coder = None
article_data = None

# get coders we want to include in analysis.
coder_rs = User.objects.filter( id__in = [ 2, 4, 6 ] )

# set up coder maps.
coder_index = 0
for current_coder in coder_rs:

    # increment coder index
    coder_index = coder_index + 1

    # get coder's user id
    current_coder_id = current_coder.id
    
    # add to ID-to-instance map
    coder_id_to_instance_dict[ current_coder_id ] = current_coder
    
    # add to ID-to-index map
    coder_id_to_index_dict[ current_coder_id ] = coder_index

#-- END loop over coders --#

# manually set up the ID to index map so the humans both map to 1, automated
#    maps to 2.
coder_id_to_index_dict[ 6 ] = 1
coder_id_to_index_dict[ 2 ] = 2
coder_id_to_index_dict[ 4 ] = 3

# loop over "sourcenet_analysis_reliability_names" with label = 'prelim_network'
reliability_qs = Analysis_Reliability_Names.objects.filter( label = 'prelim_network' )

# order by article ID ASC
reliability_qs = reliability_qs.order_by( 'article_id', 'id' )

# loop!
for reliability_name_row in reliability_qs:

    # get ID of current row
    reliability_row_id = reliability_name_row.pk

    # to start, copy the current reliability row...
    new_reliability_row = copy.copy( reliability_name_row )
    
    # ...empty the primary key ('pk')...
    new_reliability_row.pk = None
    
    # ...and set 'label' to new_label.
    new_reliability_row.label = new_label

    # get article for row
    current_article = reliability_name_row.article
    
    # get Article_Data for article.
    article_data_qs = current_article.article_data_set
    
    # try to get article data for coder with ID of 6.
    try:

        # get coder with ID 6
        current_coder = coder_id_to_instance_dict[ 6 ]
        
        # try to retrieve article data for coder 6.
        article_data = article_data_qs.get( coder = current_coder )
        
        # if we get here, there is a coder 6.  Do nothing more.
        print( "- ID: " + str( reliability_row_id ) + " - NO CHANGE" )
        
    except:
    
        # if exception, chances are it was that the get() failed - no
        #    Article_Data for coder 6.
        
        # make sure there is Article_Data for coder 4.
        try:
        
            # get coder with ID 6
            current_coder = coder_id_to_instance_dict[ 4 ]
            
            # try to retrieve article data for coder 6.
            article_data = article_data_qs.get( coder = current_coder )
            
            # if we get here, there is a coder 4, and no 6.  In the new
            #    reliability row, set the coder1 values to those from coder 3.
            new_reliability_row.coder1 = current_coder
            new_reliability_row.coder1_detected = new_reliability_row.coder3_detected
            new_reliability_row.coder1_person_id = new_reliability_row.coder3_person_id
            new_reliability_row.coder1_source_type = new_reliability_row.coder3_source_type
            
            # if we get here, there is a coder 6.  Do nothing more.
            print( "- ID: " + str( reliability_row_id ) + " - USED 3 FOR 1" )
            
        except:
        
            print( "- ID: " + str( reliability_row_id ) + " - ERROR - no Article_Data for either coder 6 or coder 4.  Should never happen." )
            
        #-- END try/except for coder 4 Article_Data --#
        
    #-- END try/except for coder 6 Article_Data --#
    
    # save the new reliability row.
    new_reliability_row.save()

#-- END loop over Analysis_Reliability_Names rows. --#