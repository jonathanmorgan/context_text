#==============================================================================#
# Initialization/Preconditions
#==============================================================================#

# Before you run this code, you need to do the following:
# - connect to the database.  Example is in db_connect.r, in this same folder.
# source( "db_connect.r" )
# - Initialize the functions contained in reliability_functions.r, also in this same folder.
# source( "functions-reliability.r" )
# - Set personType to either "author" or "source"
# - If you want to filter on a label, declare the label in filterOnLabel

# if no personType, default to "source".
if ( exists( "personType" ) == FALSE ){

    # no person type.  Default to "source".
    personType <- "source"

}

# if no personType, default to "source".
if ( exists( "filterOnLabel" ) == FALSE ) {

    # no label specified for filtering.  Default to "".
    filterOnLabel <- ""

}

# create output file name based on person type.
outputFile <- paste( personType, "-person_lookup_results.txt", sep = "" )

#==============================================================================#
# Retrieve data
#==============================================================================#

# execute query to pull in person data from reliability table.
resultSet <- queryReliabilityData( personType, filterOnLabel )

# retrieve rows into data.frame
dataFrame <- fetch( resultSet, n = -1 )

# test data.frame fetch - get column names, row, column count
colnames( dataFrame )
nrow( dataFrame )
ncol( dataFrame )

# close result set
dbClearResult( resultSet )

# Try a different way of building matrix.   THIS DOESN'T WORK!
#coder1PersonId <- dataFrame[ "coder1_person_id" ]
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
coder1PersonId <- dataFrame$coder1_person_id
coder2PersonId <- dataFrame$coder2_person_id

# matrix of person lookup values for each person
lookupMatrix1v2Tall <- cbind( coder1PersonId, coder2PersonId )
lookupMatrix1v2Wide <- t( lookupMatrix1v2Tall )

# OR just...
#lookupMatrix1v2Wide <- rbind( coder1PersonId, coder2PersonId )

# test agreement.
testAgreement( lookupMatrix1v2Tall, labelIN = "Person Lookup - Compare coder 1 and 2 - all included", fileIN = outputFile )

# filter to omit where either one or the other did not detect the person.
filteredDF <- dataFrame[ !( ( coder1PersonId == 0 ) | ( coder2PersonId == 0 ) ), ]

# get columns to compare
coder1PersonId <- filteredDF$coder1_person_id
coder2PersonId <- filteredDF$coder2_person_id

# matrix of person lookup values for each person
lookupMatrix1v2Tall <- cbind( coder1PersonId, coder2PersonId )

# test agreement.
testAgreement( lookupMatrix1v2Tall, labelIN = "Person Lookup - Compare coder 1 and 2 - filter - only joint detection", fileIN = outputFile )

#==============================================================================#
# Compare coder 2 and 3
#==============================================================================#

# get columns to compare
coder2PersonId <- dataFrame$coder2_person_id
coder3PersonId <- dataFrame$coder3_person_id

# person lookup 2 v. 3 - convert to matrix
lookupMatrix2v3Tall <- cbind( coder2PersonId, coder3PersonId )

# testAgreement
testAgreement( lookupMatrix2v3Tall, labelIN = "Person Lookup - Compare coder 2 and 3 - all included", fileIN = outputFile )

# filter to omit where either one or the other did not detect the person.
filteredDF <- dataFrame[ !( ( coder2PersonId == 0 ) | ( coder3PersonId == 0 ) ), ]

# get columns to compare
coder2PersonId <- filteredDF$coder2_person_id
coder3PersonId <- filteredDF$coder3_person_id

# person lookup 2 v. 3 - convert to matrix
lookupMatrix2v3Tall <- cbind( coder2PersonId, coder3PersonId )

# test agreement.
testAgreement( lookupMatrix2v3Tall, labelIN = "Person Lookup - Compare coder 2 and 3 - filter - only joint detection", fileIN = outputFile )

#==============================================================================#
# Compare coder 1 and 3
#==============================================================================#

# get columns to compare
coder1PersonId <- dataFrame$coder1_person_id
coder3PersonId <- dataFrame$coder3_person_id

# convert to matrix
lookupMatrix1v3Tall <- cbind( coder1PersonId, coder3PersonId )

# percentage agreement - wants the cbind matrix, not the rbind one.
testAgreement( lookupMatrix1v3Tall, labelIN = "Person Lookup - Compare coder 1 and 3 - all included", fileIN = outputFile )

# filter to omit where either one or the other did not detect the person.
filteredDF <- dataFrame[ !( ( coder1PersonId == 0 ) | ( coder3PersonId == 0 ) ), ]

# get columns to compare
coder1PersonId <- filteredDF$coder1_person_id
coder3PersonId <- filteredDF$coder3_person_id

# person lookup 1 v. 3 - convert to matrix
lookupMatrix1v3Tall <- cbind( coder1PersonId, coder3PersonId )

# test agreement.
testAgreement( lookupMatrix1v3Tall, labelIN = "Person Lookup - Compare coder 1 and 3 - filter - only joint detection", fileIN = outputFile )
