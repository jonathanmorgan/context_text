#==============================================================================#
# Initialization/Preconditions
#==============================================================================#

# Before you run this code, you need to do the following:
# - connect to the database.  Example is in db_connect.r, in this same folder.
# source( "db_connect.r" )
# - Initialize the functions contained in reliability_functions.r, also in this same folder.
# source( "functions-reliability.r" )
# - Set personType to either "author" or "subject"
# - If you want to filter on a label, declare the label in filterOnLabel

# if no personType, default to "subject".
if ( exists( "personType" ) == FALSE ){

    # no person type.  Default to "subject".
    personType <- "subject"

}

# if no filterOnLabel, default to "".
if ( exists( "filterOnLabel" ) == FALSE ) {

    # no label specified for filtering.  Default to "".
    filterOnLabel <- ""

}

# create output file name based on person type.
outputFile <- paste( personType, "-name_detection_results.txt", sep = "" )

#==============================================================================#
# Retrieve data
#==============================================================================#

# execute query to pull in the information from reliability table.
resultSet <- queryReliabilityData( personType, filterOnLabel )

# retrieve rows into data.frame
dataFrame <- fetch( resultSet, n = -1 )

# test data.frame fetch - get column names, row, column count
colnames( dataFrame )
nrow( dataFrame )
ncol( dataFrame )

# close result set
dbClearResult( resultSet )

# get columns to compare
coder1Detected <- dataFrame$coder1_detected
coder2Detected <- dataFrame$coder2_detected
coder3Detected <- dataFrame$coder3_detected

# Try a different way of building matrix.   THIS DOESN'T WORK!
#coder1Detected <- dataFrame[ "coder1_detected" ]
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

# matrix of detected values for each person
detectedMatrix1v2Tall <- cbind( coder1Detected, coder2Detected )
detectedMatrix1v2Wide <- t( detectedMatrix1v2Tall )

# OR just...
#detectedMatrix1v2Wide <- rbind( coder1Detected, coder2Detected )

# test agreement - wants the cbind matrix, not the rbind one.
testAgreement( detectedMatrix1v2Tall, labelIN = "Person Detection - Compare coder 1 and 2", fileIN = outputFile )

#==============================================================================#
# Compare coder 2 and 3
#==============================================================================#

# detected 2 v. 3 - convert to matrix
detectedMatrix2v3Tall <- cbind( coder2Detected, coder3Detected )

# test agreement - wants the cbind matrix, not the rbind one.
testAgreement( detectedMatrix2v3Tall, labelIN = "Person Detection - Compare coder 2 and 3", fileIN = outputFile )

#------------------------------------------------------------------------------#
# Compare coder 1 and 3
#------------------------------------------------------------------------------#

# convert to matrix
detectedMatrix1v3Tall <- cbind( coder1Detected, coder3Detected )

# test agreement - wants the cbind matrix, not the rbind one.
testAgreement( detectedMatrix1v3Tall, labelIN = "Person Detection - Compare coder 1 and 3", fileIN = outputFile )
