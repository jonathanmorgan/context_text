#==============================================================================#
# Imports
#==============================================================================#

# install and load irr package (irr = inter-rater reliability).
#install.packages( "irr" )
library( irr )

#==============================================================================#
# Functions
#==============================================================================#

# Function: output_agree_results
#
# Accepts the results of a call to agree() from the irr library.  Outputs them.
output_agree_results <- function( result_IN ) {

    cat( "Agree results:\n" )
    cat( paste( "- Method: ", result_IN$method, "\n" ) )
    cat( paste( "- Subjects: ", result_IN$subjects, "\n" ) )
    cat( paste( "- Raters: ", result_IN$raters, "\n" ) )
    cat( paste( "- Name: ", result_IN$irr.name, "\n" ) )
    cat( paste( "- Value: ", result_IN$value, "\n" ) )
    cat( "\n" )

}

# Function: output_kripp_results
#
# Accepts the results of a call to kripp.alpha() from the irr library.  Outputs
#    them.
output_kripp_results <- function( result_IN ) {

    cat( "Krippendorf's Alpha results:\n" )
    cat( paste( "- Method: ", result_IN$method, "\n" ) )
    cat( paste( "- Level: ", result_IN[ "data.level" ], "\n" ) )
    cat( paste( "- Subjects: ", result_IN$subjects, "\n" ) )
    cat( paste( "- Raters: ", result_IN$raters, "\n" ) )
    cat( paste( "- Name: ", result_IN$irr.name, "\n" ) )
    cat( paste( "- Alpha: ", result_IN$value, "\n" ) )
    cat( "\n" )

}

# Function: test_agreement()
#
# Accepts a matrix with coders as columns and observations per coder as rows.
#    Calculates percentage agreement and Krippendorf's Alpha for the matrix,
#    outputs the results.
#
# Hint: to make matrix, use cbind on vectors of coding results per coder.
test_agreement <- function( coding_matrix_IN, label_IN = "test_agreement" ) {

    # return reference
    status_OUT <- "Success!"

    # declare variables
    coding_matrix_tall <- NULL
    coding_matrix_wide <- NULL
    agree_result <- NULL
    kripp_result <- NULL

    # output label
    cat( "\n#==============================================================================#\n")
    cat( paste( label_IN, "\n" ) )
    cat( "#==============================================================================#\n\n")

    # store matrix passed in in tall, then transpose so we have wide.
    coding_matrix_tall <- coding_matrix_IN
    coding_matrix_wide <- t( coding_matrix_tall )

    # percentage agreement - wants the cbind matrix, not the rbind one.
    agree_result <- agree( coding_matrix_tall )
    output_agree_results( agree_result )

    # Scott's Pi?

    # run Krippendorf's Alpha (not a good match to data - no variance)
    kripp_result <- kripp.alpha( coding_matrix_wide, method = "nominal" )
    output_kripp_results( kripp_result )

    kripp_result <- kripp.alpha( coding_matrix_wide, method = "ordinal" )
    output_kripp_results( kripp_result )

    kripp_result <- kripp.alpha( coding_matrix_wide, method = "interval" )
    output_kripp_results( kripp_result )

    kripp_result <- kripp.alpha( coding_matrix_wide, method = "ratio" )
    output_kripp_results( kripp_result )

    return( status_OUT )

} #-- END function test_agreement() --#
