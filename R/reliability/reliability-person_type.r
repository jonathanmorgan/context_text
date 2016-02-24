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

# if no personType, default to "subject".
if ( exists( "filterOnLabel" ) == FALSE ) {

    # no label specified for filtering.  Default to "".
    filterOnLabel <- ""

}

# create output file name based on person type.
outputFile <- paste( personType, "-person_type_results.txt", sep = "" )

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
#coder1PersonType <- dataFrame[ "coder1_person_type_int" ]
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
coder1PersonType <- dataFrame$coder1_person_type_int
coder2PersonType <- dataFrame$coder2_person_type_int

# matrix of Person Type values for each person
typeMatrix1v2Tall <- cbind( coder1PersonType, coder2PersonType )
typeMatrix1v2Wide <- t( typeMatrix1v2Tall )

# OR just...
#typeMatrix1v2Wide <- rbind( coder1PersonType, coder2PersonType )

# test agreement.
testAgreement( typeMatrix1v2Tall, labelIN = "Person Type - Compare coder 1 and 2 - all included", fileIN = outputFile )

# filter to omit where either one or the other did not detect the person.
#filteredDF <- dataFrame[ !( ( is.na( coder1PersonType ) ) | ( is.null( coder1PersonType ) ) | ( is.na( coder2PersonType ) ) | ( is.null( coder2PersonType ) ) ), ]
filteredDF <- dataFrame[ !( ( coder1PersonType == 0 ) | ( coder2PersonType == 0 ) ), ]

# get columns to compare
coder1PersonType <- filteredDF$coder1_person_type_int
coder2PersonType <- filteredDF$coder2_person_type_int

# matrix of Person Type values for each person
typeMatrix1v2Tall <- cbind( coder1PersonType, coder2PersonType )

# test agreement.
testAgreement( typeMatrix1v2Tall, labelIN = "Person Type - Compare coder 1 and 2 - filter - only joint detection", fileIN = outputFile )

#==============================================================================#
# Compare coder 2 and 3
#==============================================================================#

# get columns to compare
coder2PersonType <- dataFrame$coder2_person_type_int
coder3PersonType <- dataFrame$coder3_person_type_int

# Person Type 2 v. 3 - convert to matrix
typeMatrix2v3Tall <- cbind( coder2PersonType, coder3PersonType )

# testAgreement
testAgreement( typeMatrix2v3Tall, labelIN = "Person Type - Compare coder 2 and 3 - all included", fileIN = outputFile )

# filter to omit where either one or the other did not detect the person.
#filteredDF <- dataFrame[ !( ( is.na( coder2PersonType ) ) | ( is.null( coder2PersonType ) ) | ( is.na( coder3PersonType ) ) | ( is.null( coder3PersonType ) ) ), ]
filteredDF <- dataFrame[ !( ( coder2PersonType == 0 ) | ( coder3PersonType == 0 ) ), ]

# get columns to compare
coder2PersonType <- filteredDF$coder2_person_type_int
coder3PersonType <- filteredDF$coder3_person_type_int

# Person Type 2 v. 3 - convert to matrix
typeMatrix2v3Tall <- cbind( coder2PersonType, coder3PersonType )

# test agreement.
testAgreement( typeMatrix2v3Tall, labelIN = "Person Type - Compare coder 2 and 3 - filter - only joint detection", fileIN = outputFile )

#==============================================================================#
# Compare coder 1 and 3
#==============================================================================#

# get columns to compare
coder1PersonType <- dataFrame$coder1_person_type_int
coder3PersonType <- dataFrame$coder3_person_type_int

# convert to matrix
typeMatrix1v3Tall <- cbind( coder1PersonType, coder3PersonType )

# percentage agreement - wants the cbind matrix, not the rbind one.
testAgreement( typeMatrix1v3Tall, labelIN = "Person Type - Compare coder 1 and 3 - all included", fileIN = outputFile )

# filter to omit where either one or the other did not detect the person.
#filteredDF <- dataFrame[ !( ( is.na( coder1PersonType ) ) | ( is.null( coder1PersonType ) ) | ( is.na( coder3PersonType ) ) | ( is.null( coder3PersonType ) ) ), ]
filteredDF <- dataFrame[ !( ( coder1PersonType == 0 ) | ( coder3PersonType == 0 ) ), ]

# get columns to compare
coder1PersonType <- filteredDF$coder1_person_type_int
coder3PersonType <- filteredDF$coder3_person_type_int

# Person Type 1 v. 3 - convert to matrix
typeMatrix1v3Tall <- cbind( coder1PersonType, coder3PersonType )

# test agreement.
testAgreement( typeMatrix1v3Tall, labelIN = "Person Type - Compare coder 1 and 3 - filter - only joint detection", fileIN = outputFile )
