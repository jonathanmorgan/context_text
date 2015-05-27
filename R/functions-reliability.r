#==============================================================================#
# Imports
#==============================================================================#

# install and load irr package (irr = inter-rater reliability).
#install.packages( "irr" )
library( irr )

#==============================================================================#
# Functions
#==============================================================================#


queryReliabilityData <- function( personTypeIN, filterOnLabelIN = "" ) {

    # Function: queryReliabilityData()
    #
    # Accepts personTypeIN and optional filterOnLabelIN values.  Creates Query
    #    to pull back records with person type and label passed in when either
    #    value is present.
    #
    # Returns the ResultSet.

    # return reference
    resultSetOUT <- NULL

    # declare variables
    queryString <- ""

    # build query string using personTypeIN
    queryString <- paste( "SELECT * FROM sourcenet_analysis_reliability_names WHERE person_type = '", personTypeIN, "'", sep = "" )

    # got a filterOnLabelIN?
    if ( filterOnLabelIN != "" ) {

        # yes.  Add a WHERE clause for matching the label.
        queryString <- paste( queryString, " AND label = '", filterOnLabelIN, "'", sep = "" )

    }

    # add ORDER BY
    queryString <- paste( queryString, " ORDER BY id ASC;", sep = "" )

    cat( queryString )

    # run query
    resultSetOUT <- dbSendQuery( connection, queryString )

    return( resultSetOUT )

} #-- END functon queryReliabilityData() --#


outputAgreeResults <- function( resultIN, fileIN = "" ) {

    # Function: outputAgreeResults
    #
    # Accepts the results of a call to irr::agree() from the irr library and an
    #    optional path to a file where output should be stored.
    #
    # Outputs results, to file if file path was passed in.

    # got a file passed in?
    if ( fileIN != "" ){

        # yes - open it for output.
        sink( fileIN, append=TRUE, split=TRUE )

    }

    cat( "Agree results:\n" )
    cat( paste( "- Method: ", resultIN$method, "\n" ) )
    cat( paste( "- Subjects: ", resultIN$subjects, "\n" ) )
    cat( paste( "- Raters: ", resultIN$raters, "\n" ) )
    cat( paste( "- Name: ", resultIN$irr.name, "\n" ) )
    cat( paste( "- Value: ", resultIN$value, "\n" ) )
    cat( "\n" )

    # got a file passed in?
    if ( fileIN != "" ){

        # return output to the terminal.
        sink()

    }

} #-- END function outputAgreeResults() --#

outputKrippResults <- function( resultIN, fileIN = "" ) {

    # Function: outputKrippResults
    #
    # Accepts the results of a call to kripp.alpha() from the irr library and an
    #    optional path to a file where output should be stored.
    #
    # Outputs results, to file if file path was passed in.

    # got a file passed in?
    if ( fileIN != "" ){

        # yes - open it for output.
        sink( fileIN, append=TRUE, split=TRUE )

    }

    cat( "Krippendorf's Alpha results:\n" )
    cat( paste( "- Method: ", resultIN$method, "\n" ) )
    cat( paste( "- Level: ", resultIN[ "data.level" ], "\n" ) )
    cat( paste( "- Subjects: ", resultIN$subjects, "\n" ) )
    cat( paste( "- Raters: ", resultIN$raters, "\n" ) )
    cat( paste( "- Name: ", resultIN$irr.name, "\n" ) )
    cat( paste( "- Alpha: ", resultIN$value, "\n" ) )
    cat( "\n" )

    # got a file passed in?
    if ( fileIN != "" ){

        # return output to the terminal.
        sink()

    }

} #-- END function outputKrippResults() --#

testAgreement <- function( codingMatrixIN, labelIN = "testAgreement", fileIN = "", corUseIN = "all.obs", corMethodIN = "pearson" ) {

    # Function: testAgreement()
    #
    # Accepts a matrix with coders as columns and observations per coder as rows.
    #    Calculates percentage agreement and Krippendorf's Alpha for the matrix,
    #    outputs the results.
    #
    # Arguments:
    # - codingMatrixIN - matrix that contains columns of values to be tested.
    # - labelIN - optional label to use when outputting the results.
    # - fileIN - optional path to file where results should be output.
    # - corUseIN - optional directive to instruct simple correlation which records to include.  Defaults to "all.obs", all rows.
    # - corMethodIN - optional directive to instruct which correlation to use to test simple correlation. Defaults to "pearson", Pearson's product-moment correlation.
    #
    # Hint: to make matrix, use cbind on vectors of coding results per coder.

    # return reference
    statusOUT <- "Success!"

    # declare variables
    codingMatrixTall <- NULL
    codingMatrixWide <- NULL
    tallColumnCount <- -1
    columnNumber <- -1
    rowNumber <- -1
    corResult <- NULL
    agreeResult <- NULL
    krippResult <- NULL

    # store matrix passed in in tall, then transpose so we have wide.
    codingMatrixTall <- codingMatrixIN
    tallColumnCount <- ncol( codingMatrixTall )
    codingMatrixWide <- t( codingMatrixTall )

    # got a file passed in?
    if ( fileIN != "" ){

        # yes - open it for output.
        sink( fileIN, append=TRUE, split=TRUE )

    }

    # output label
    cat( "\n#=============================================================================#\n" )
    cat( paste( labelIN, "\n" ) )
    cat( "#=============================================================================#\n\n" )

    # also output variance and standard deviation of each list, and a
    #    correlation coefficient, just for diagnostics.
    for( columnNumber in 1 : tallColumnCount ) {

        # output variance and standard deviation for this column.
        cat( paste( "var col", columnNumber, " = ", var( codingMatrixTall[ , columnNumber ] ), "\n", sep = "" ) )
        cat( paste( "sd col", columnNumber, " = ", sd( codingMatrixTall[ , columnNumber ] ), "\n", sep = "" ) )

    } #-- END loop over columns for variance and standard deviation --#

    # output correlations between columns.
    corResult <- cor( codingMatrixTall, use = corUseIN, method = corMethodIN )

    # loop over columns in corResult
    for( columnNumber in 1 : tallColumnCount ) {

        # then, loop through rows to to output - from 1 to columnNumber - 1.
        if ( columnNumber > 1 ) {

            for( rowNumber in 1 : ( tallColumnCount - 1 ) ) {

                # output the correlation coefficient.
                cat( paste( corMethodIN, " r[", rowNumber, ",", columnNumber, "] = ", corResult[ rowNumber, columnNumber ], "\n", sep = "" ) )

            } #-- END loop over rows. --#

        } #-- END check to make sure we aren't in first column. --#

    } #-- END loop over columns --#

    cat( "\n\n" )

    # got a file passed in?
    if ( fileIN != "" ){

        # return output to the terminal.
        sink()

    }

    # percentage agreement - wants the cbind matrix, not the rbind one.
    agreeResult <- irr::agree( codingMatrixTall )
    outputAgreeResults( agreeResult, fileIN )

    # Scott's Pi?

    # run Krippendorf's Alpha (not a good match to data - no variance)
    krippResult <- irr::kripp.alpha( codingMatrixWide, method = "nominal" )
    outputKrippResults( krippResult, fileIN )

    krippResult <- irr::kripp.alpha( codingMatrixWide, method = "ordinal" )
    outputKrippResults( krippResult, fileIN )

    krippResult <- irr::kripp.alpha( codingMatrixWide, method = "interval" )
    outputKrippResults( krippResult, fileIN )

    krippResult <- irr::kripp.alpha( codingMatrixWide, method = "ratio" )
    outputKrippResults( krippResult, fileIN )

    return( statusOUT )

} #-- END function testAgreement() --#
