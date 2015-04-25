# load DBI, RPostgreSQL
#install.packages( "DBI" )
#install.packages( "RPostgreSQL" )
library( "DBI" )
library( "RPostgreSQL" )

# create DB connection
driver <- dbDriver( "PostgreSQL" )
db_username <- ""
db_password <- ""
db_name <- ""
connection <- dbConnect( driver, user=db_username, password=db_password, dbname=db_name )

# test connection
dbListTables( connection )

# execute query to pull in the source information from reliability table.
result_set <- dbSendQuery( connection, "SELECT * FROM sourcenet_analysis_reliability_names WHERE person_type = 'source' ORDER BY id ASC;" )

# retrieve rows into data.frame
data_frame <- fetch( result_set, -1 )

# test data.frame fetch - get column names, row, column count
colnames( data_frame )
nrow( data_frame )
ncol( data_frame )

# close result set
dbClearResult( result_set )

# install and load irr package (irr = inter-rater reliability).
#install.packages( "irr" )
library( irr )

# now, try krippendorf's alpha

# get columns to compare
coder1_detected <- data_frame$coder1_detected
coder1_person_id <- data_frame$coder1_person_id
coder2_detected <- data_frame$coder2_detected
coder2_person_id <- data_frame$coder2_person_id
coder3_detected <- data_frame$coder3_detected
coder3_person_id <- data_frame$coder3_person_id


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
detected_matrix_1v2 <- cbind( coder1_detected, coder2_detected )
detected_matrix_1v2 <- t( 1v2_detected_matrix )

# OR just...
detected_matrix_1v2 <- rbind( coder1_detected, coder2_detected )

# run Krippendorf's Alpha
kripp.alpha( detected_matrix_1v2, method = "nominal" )
kripp.alpha( detected_matrix_1v2, method = "ordinal" )
kripp.alpha( detected_matrix_1v2, method = "interval" )
kripp.alpha( detected_matrix_1v2, method = "ratio" )

# detected 2 v. 3 - convert to matrix
detected_matrix_2v3 <- rbind( coder2_detected, coder3_detected )

# run Krippendorf's Alpha
kripp.alpha( detected_matrix_2v3, method = "nominal" )
kripp.alpha( detected_matrix_2v3, method = "ordinal" )
kripp.alpha( detected_matrix_2v3, method = "interval" )
kripp.alpha( detected_matrix_2v3, method = "ratio" )

# Try a different way of building matrix.   THIS DOESN'T WORK!
#jm_source_count <- data_frame[ "jm_source_count" ]
#bb_source_count <- data_frame[ "bb_source_count" ]
# return dataframes, not vectors. Must be vectors to combine into a matrix.

# convert to matrix
detected_matrix_1v3 <- rbind( coder1_detected, coder3_detected )

# run Krippendorf's Alpha
kripp.alpha( detected_matrix_1v3, method = "nominal" )
kripp.alpha( detected_matrix_1v3, method = "ordinal" )
kripp.alpha( detected_matrix_1v3, method = "interval" )
kripp.alpha( detected_matrix_1v3, method = "ratio" )
