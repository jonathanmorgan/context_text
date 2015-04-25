#==============================================================================#
# Initialization/Preconditions
#==============================================================================#

# Before you run this code, you need to do the following:
# - connect to the database.  Example is in db_connect.r, in this same folder.
# - Initialize the functions contained in reliability_functions.r, also in this same folder.

#==============================================================================#
# Retrieve data
#==============================================================================#

# adjust to either pull in source data or author data.

# execute query to pull in the source information from reliability table.

# including situations where one detected the person and the other did not.
result_set <- dbSendQuery( connection, "SELECT * FROM sourcenet_analysis_reliability_names WHERE person_type = 'source' ORDER BY id ASC;" )

# OR execute query to pull in the author information from reliability table.
#result_set <- dbSendQuery( connection, "SELECT * FROM sourcenet_analysis_reliability_names WHERE person_type = 'author' ORDER BY id ASC;" )

# retrieve rows into data.frame
data_frame <- fetch( result_set, -1 )

# test data.frame fetch - get column names, row, column count
colnames( data_frame )
nrow( data_frame )
ncol( data_frame )

# close result set
dbClearResult( result_set )

# Try a different way of building matrix.   THIS DOESN'T WORK!
#coder1_person_id <- data_frame[ "coder1_person_id" ]
# return dataframes, not vectors. Must be vectors to combine into a matrix.

#==============================================================================#
# Compare coder 1 and 2 (the humans)
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

# get columns to compare
coder1_person_id <- data_frame$coder1_person_id
coder2_person_id <- data_frame$coder2_person_id

# matrix of person lookup values for each person
lookup_matrix_1v2_tall <- cbind( coder1_person_id, coder2_person_id )
lookup_matrix_1v2_wide <- t( lookup_matrix_1v2_tall )

# OR just...
#lookup_matrix_1v2_wide <- rbind( coder1_person_id, coder2_person_id )

# test agreement.
test_agreement( lookup_matrix_1v2_tall, label_IN = "Person Lookup - Compare coder 1 and 2 - all included" )

# filter to omit where either one or the other did not detect the person.
filtered_df <- data_frame[ !( ( coder1_person_id == 0 ) | ( coder2_person_id == 0 ) ), ]

# get columns to compare
coder1_person_id <- filtered_df$coder1_person_id
coder2_person_id <- filtered_df$coder2_person_id

# matrix of person lookup values for each person
lookup_matrix_1v2_tall <- cbind( coder1_person_id, coder2_person_id )

# test agreement.
test_agreement( lookup_matrix_1v2_tall, label_IN = "Person Lookup - Compare coder 1 and 2 - filter - only joint detection" )

#==============================================================================#
# Compare coder 2 and 3
#==============================================================================#

# get columns to compare
coder2_person_id <- data_frame$coder2_person_id
coder3_person_id <- data_frame$coder3_person_id

# person lookup 2 v. 3 - convert to matrix
lookup_matrix_2v3_tall <- cbind( coder2_person_id, coder3_person_id )

# test_agreement
test_agreement( lookup_matrix_2v3_tall, label_IN = "Person Lookup - Compare coder 2 and 3 - all included" )

# filter to omit where either one or the other did not detect the person.
filtered_df <- data_frame[ !( ( coder2_person_id == 0 ) | ( coder3_person_id == 0 ) ), ]

# get columns to compare
coder2_person_id <- filtered_df$coder2_person_id
coder3_person_id <- filtered_df$coder3_person_id

# person lookup 2 v. 3 - convert to matrix
lookup_matrix_2v3_tall <- cbind( coder2_person_id, coder3_person_id )

# test agreement.
test_agreement( lookup_matrix_1v2_tall, label_IN = "Person Lookup - Compare coder 2 and 3 - filter - only joint detection" )

#==============================================================================#
# Compare coder 1 and 3
#==============================================================================#

# get columns to compare
coder1_person_id <- data_frame$coder1_person_id
coder3_person_id <- data_frame$coder3_person_id

# convert to matrix
lookup_matrix_1v3_tall <- cbind( coder1_person_id, coder3_person_id )

# percentage agreement - wants the cbind matrix, not the rbind one.
test_agreement( lookup_matrix_1v3_tall, label_IN = "Person Lookup - Compare coder 1 and 3 - all included" )

# filter to omit where either one or the other did not detect the person.
filtered_df <- data_frame[ !( ( coder1_person_id == 0 ) | ( coder3_person_id == 0 ) ), ]

# get columns to compare
coder1_person_id <- filtered_df$coder1_person_id
coder3_person_id <- filtered_df$coder3_person_id

# person lookup 1 v. 3 - convert to matrix
lookup_matrix_1v3_tall <- cbind( coder1_person_id, coder3_person_id )

# test agreement.
test_agreement( lookup_matrix_1v3_tall, label_IN = "Person Lookup - Compare coder 1 and 3 - filter - only joint detection" )
