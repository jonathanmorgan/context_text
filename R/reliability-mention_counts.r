#==============================================================================#
# Initialization/Preconditions
#==============================================================================#

# Before you run this code, you need to do the following:
# - connect to the database.  Example is in db_connect.r, in this same folder.
# source( "db_connect.r" )
# - Initialize the functions contained in reliability_functions.r, also in this same folder.
# source( "reliability_functions.r" )
# - If you want to filter on a label, declare the label in filter_on_label

# if no person_type, default to "source".
if ( exists( "filter_on_label" ) == FALSE ) {

    # no label specified for filtering.  Default to "".
    filter_on_label <- ""

}

# create output file name based on person type.
output_file <- "mention_count_results.txt"

#==============================================================================#
# Retrieve data
#==============================================================================#

# execute query to pull in information from reliability ties table.
query_string <- ""

# build query string using person_type
query_string <- "SELECT * FROM sourcenet_analysis_reliability_ties"

# got a filter_on_label?
if ( filter_on_label != "" ) {

    # yes.  Add a WHERE clause for matching the label.
    query_string <- paste( query_string, " WHERE label = '", filter_on_label, "'", sep = "" )

}

# add ORDER BY
query_string <- paste( query_string, " ORDER BY person_id, relation_person_id ASC;", sep = "" )

# run query
result_set <- dbSendQuery( connection, query_string )

# retrieve rows into data.frame
data_frame <- fetch( result_set, n = -1 )

# test data.frame fetch - get column names, row, column count
colnames( data_frame )
nrow( data_frame )
ncol( data_frame )

# close result set
dbClearResult( result_set )

# get columns to compare
coder1_mention_count <- data_frame$coder1_mention_count
coder2_mention_count <- data_frame$coder2_mention_count
coder3_mention_count <- data_frame$coder3_mention_count

# Try a different way of building matrix.   THIS DOESN'T WORK!
#coder1_detected <- data_frame[ "coder1_detected" ]
# return dataframes, not vectors. Must be vectors to combine into a matrix.

#==============================================================================#
# Compare coder 1 and 2
#==============================================================================#

# convert to matrix, then transpose so oriented as alpha function expects.
#    Alpha function expects matrix with a row per coder, with each column
#    representing a case each coded.  cbind() takes the two columns retrieved
#    from the database and places them side-by-side as columns, resulting in a
#    matrix where each row is a case, each column is a coder.  rbind() uses the
#    vectors as rows, resulting in a row per coder, which is what kripp.alpha()
#    function expects.  If you use cbind(), you'll need to transpose using the
#    t() function to get the data in the form kripp.alpha() wants.  Note,
#    however, that it appears that some functions in package irr expect
#    the opposite orientation, so make sure you look at what each expects.

# matrix of mention count values for each person
mention_matrix_1v2_tall <- cbind( coder1_mention_count, coder2_mention_count )
mention_matrix_1v2_wide <- t( mention_matrix_1v2_tall )

# OR just...
#mention_matrix_1v2_wide <- rbind( coder1_mention_count, coder2_mention_count )

# test agreement - wants the cbind matrix, not the rbind one.
test_agreement( mention_matrix_1v2_tall, label_IN = "Mention counts - Compare coder 1 and 2", file_IN = output_file )

#==============================================================================#
# Compare coder 2 and 3
#==============================================================================#

# detected 2 v. 3 - convert to matrix
#mention_matrix_2v3_tall <- cbind( coder2_mention_count, coder3_mention_count )

# test agreement - wants the cbind matrix, not the rbind one.
#test_agreement( mention_matrix_2v3_tall, label_IN = "Mention counts - Compare coder 2 and 3", file_IN = output_file )

#------------------------------------------------------------------------------#
# Compare coder 1 and 3
#------------------------------------------------------------------------------#

# convert to matrix
#mention_matrix_1v3_tall <- cbind( coder1_mention_count, coder3_mention_count )

# test agreement - wants the cbind matrix, not the rbind one.
#test_agreement( mention_matrix_1v3_tall, label_IN = "Mention counts - Compare coder 1 and 3", file_IN = output_file )
