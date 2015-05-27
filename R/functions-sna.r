#==============================================================================#
# Imports
#==============================================================================#


#==============================================================================#
# Functions
#==============================================================================#


calculateColumnMean <- function( columnIN, minValueToIncludeIN = NULL ) {

    # Function: calculateColumnMean()
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

    # check to see if min value is set.
    if ( is.null( minValueToIncludeIN ) == FALSE ) {

    }

} #-- END function calculateColumnMean
