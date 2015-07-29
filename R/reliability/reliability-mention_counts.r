#==============================================================================#
# Initialization/Preconditions
#==============================================================================#

# Before you run this code, you need to do the following:
# - connect to the database.  Example is in db_connect.r, in this same folder.
# source( "db_connect.r" )
# - Initialize the functions contained in reliability_functions.r, also in this same folder.
# source( "functions-reliability.r" )
# - If you want to filter on a label, declare the label in filterOnLabel

# if no filterOnLabel, default to "".
if ( exists( "filterOnLabel" ) == FALSE ) {

    # no label specified for filtering.  Default to "".
    filterOnLabel <- ""

}

# create output file name based on person type.
outputFile <- "mention_count_results.txt"

#==============================================================================#
# Retrieve data
#==============================================================================#

# execute query to pull in information from reliability ties table.
queryString <- ""

# build query string using person_type
queryString <- "SELECT * FROM sourcenet_analysis_reliability_ties"

# got a filterOnLabel?
if ( filterOnLabel != "" ) {

    # yes.  Add a WHERE clause for matching the label.
    queryString <- paste( queryString, " WHERE label = '", filterOnLabel, "'", sep = "" )

}

# add ORDER BY
queryString <- paste( queryString, " ORDER BY person_id, relation_person_id ASC;", sep = "" )
queryString

# run query
resultSet <- dbSendQuery( connection, queryString )

# retrieve rows into data.frame
dataFrame <- fetch( resultSet, n = -1 )

# test data.frame fetch - get column names, row, column count
colnames( dataFrame )
nrow( dataFrame )
ncol( dataFrame )

# close result set
dbClearResult( resultSet )

# get columns to compare
coder1MentionCount <- dataFrame$coder1_mention_count
coder2MentionCount <- dataFrame$coder2_mention_count
coder3MentionCount <- dataFrame$coder3_mention_count

# Try a different way of building matrix.   THIS DOESN'T WORK!
#coder1_detected <- dataFrame[ "coder1_detected" ]
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
mentionMatrix1v2Tall <- cbind( coder1MentionCount, coder2MentionCount )
mentionMatrix1v2Wide <- t( mentionMatrix1v2Tall )

# OR just...
#mentionMatrix1v2Wide <- rbind( coder1MentionCount, coder2MentionCount )

# test agreement - wants the cbind matrix, not the rbind one.
testAgreement( mentionMatrix1v2Tall, labelIN = "Mention counts - Compare coder 1 and 2", fileIN = outputFile )

#==============================================================================#
# Compare coder 2 and 3
#==============================================================================#

# detected 2 v. 3 - convert to matrix
#mentionMatrix2v3Tall <- cbind( coder2MentionCount, coder3MentionCount )

# test agreement - wants the cbind matrix, not the rbind one.
#testAgreement( mentionMatrix2v3Tall, labelIN = "Mention counts - Compare coder 2 and 3", fileIN = outputFile )

#------------------------------------------------------------------------------#
# Compare coder 1 and 3
#------------------------------------------------------------------------------#

# convert to matrix
#mentionMatrix1v3Tall <- cbind( coder1MentionCount, coder3MentionCount )

# test agreement - wants the cbind matrix, not the rbind one.
#testAgreement( mentionMatrix1v3Tall, labelIN = "Mention counts - Compare coder 1 and 3", fileIN = outputFile )
