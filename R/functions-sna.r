#==============================================================================#
# Imports
#==============================================================================#


#==============================================================================#
# Functions
#==============================================================================#


calcAuthorMeanDegree <- function( dataFrameIN, includeBothIN = TRUE ) {

    # Function calcAuthorMeanDegree()
    #
    # Filters data frame to just authors using dataFrameIN$person_type (2 or 4),
    #    then calculates and returns the mean of the column dataFrameIN$degree.
    #
    # preconditions: data frame passed in must have $person_type and $degree
    #    columns.

    # return reference
    valueOUT <- -1

    # declare variables
    authorDF <- NULL

    # filter data frame
    authorDF <- dataFrameIN[ dataFrameIN$person_type == 2 | dataFrameIN$person_type == 4, ]

    # include both?
    if ( includeBothIN == FALSE ){

        # don't include both - just person_type = 2.
        authorDF <- authorDF[ authorDF$person_type == 2, ]

    }

    # calculate mean of $degree column.
    valueOUT <- mean( authorDF$degree )

    # return value
    return( valueOUT )

} #-- END function calcAuthorMeanDegree() --#


calcSourceMeanDegree <- function( dataFrameIN, includeBothIN = TRUE ) {

    # Function calcSourceMeanDegree()
    #
    # Filters data frame to just sources using dataFrameIN$person_type (3 or 4),
    #    then calculates and returns the mean of the column dataFrameIN$degree.
    #
    # preconditions: data frame passed in must have $person_type and $degree
    #    columns.

    # return reference
    valueOUT <- -1

    # declare variables
    sourceDF <- NULL

    # filter data frame
    sourceDF <- dataFrameIN[ dataFrameIN$person_type == 3 | dataFrameIN$person_type == 4, ]

    # include both?
    if ( includeBothIN == FALSE ){

        # don't include both - just person_type = 3.
        sourceDF <- sourceDF[ sourceDF$person_type == 3, ]

    }

    # calculate mean of $degree column.
    valueOUT <- mean( sourceDF$degree )

    # return value
    return( valueOUT )

} #-- END function calcSourceMeanDegree() --#


calculateListMean <- function( listIN, minValueToIncludeIN = NULL, excludeNaNIN = TRUE ) {

    # Function: calculateListMean()
    #
    # Accepts column/vector to get mean for and optional minimum value we want
    #    included in the calculation (so you can only look at values greater
    #    than 0, for example, or 10).  Filters column/vector to just contain
    #    values that meet filter criteria, then call mean().
    #
    # Returns the mean.

    # return reference
    valueOUT <- NULL

    # declare variables
    workingList <- NULL
    listLength <- -1

    # check to see if min value is set.
    if ( !is.null( minValueToIncludeIN ) ) {

        # we have a minimum value.  Filter out all entries in column/vector that
        #    are less than that value.
        workingList <- listIN[ listIN >= minValueToIncludeIN ]

    } else {

        # no minimum value.  Just use column/vector passed in.
        workingList <- as.vector( listIN, mode = "numeric" )

    }

    # anything in list?
    listLength <- length( workingList )
    if ( listLength > 0 ) {

        # yes. calculate mean on working list.
        valueOUT <- mean( workingList, na.rm = excludeNaNIN )

    } else {

        # no - return...?
        valueOUT <- 0

    }

    # return value
    return( valueOUT )

} #-- END function calculateListMean
