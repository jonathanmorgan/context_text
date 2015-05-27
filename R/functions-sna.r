#==============================================================================#
# Imports
#==============================================================================#


#==============================================================================#
# Functions
#==============================================================================#


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
