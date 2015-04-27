#==============================================================================#
# Imports
#==============================================================================#

# install and load irr package (irr = inter-rater reliability).
#install.packages( "irr" )
library( irr )

#==============================================================================#
# Functions
#==============================================================================#


# Function: query_reliability_data()
#
# Accepts person_type and filter_on_label values.  Creates Query to pull back
#    records with person type and label passed in when either value is present.
#
# Returns the ResultSet.
query_reliability_data <- function( person_type_IN, filter_on_label_IN = "" ) {

    # return reference
    result_set_OUT <- NULL

    # declare variables
    query_string <- ""

    # build query string using person_type
    query_string <- paste( "SELECT * FROM sourcenet_analysis_reliability_names WHERE person_type = '", person_type_IN, "'", sep = "" )

    # got a filter_on_label?
    if ( filter_on_label_IN != "" ) {

        # yes.  Add a WHERE clause for matching the label.
        query_string <- paste( query_string, " AND label = '", filter_on_label, "'", sep = "" )

    }

    # add ORDER BY
    query_string <- paste( query_string, " ORDER BY id ASC;", sep = "" )

    cat( query_string )

    # run query
    result_set_OUT <- dbSendQuery( connection, query_string )

    return( result_set_OUT )

} #-- END functon query_reliability_data() --#


# Function: output_agree_results
#
# Accepts the results of a call to agree() from the irr library.  Outputs them.
output_agree_results <- function( result_IN, file_IN = "" ) {

    # got a file passed in?
    if ( file_IN != "" ){

        # yes - open it for output.
        sink( file_IN, append=TRUE, split=TRUE )

    }

    cat( "Agree results:\n" )
    cat( paste( "- Method: ", result_IN$method, "\n" ) )
    cat( paste( "- Subjects: ", result_IN$subjects, "\n" ) )
    cat( paste( "- Raters: ", result_IN$raters, "\n" ) )
    cat( paste( "- Name: ", result_IN$irr.name, "\n" ) )
    cat( paste( "- Value: ", result_IN$value, "\n" ) )
    cat( "\n" )

    # got a file passed in?
    if ( file_IN != "" ){

        # return output to the terminal.
        sink()

    }

} #-- END function output_agree_results() --#

# Function: output_kripp_results
#
# Accepts the results of a call to kripp.alpha() from the irr library.  Outputs
#    them.
output_kripp_results <- function( result_IN, file_IN = "" ) {

    # got a file passed in?
    if ( file_IN != "" ){

        # yes - open it for output.
        sink( file_IN, append=TRUE, split=TRUE )

    }

    cat( "Krippendorf's Alpha results:\n" )
    cat( paste( "- Method: ", result_IN$method, "\n" ) )
    cat( paste( "- Level: ", result_IN[ "data.level" ], "\n" ) )
    cat( paste( "- Subjects: ", result_IN$subjects, "\n" ) )
    cat( paste( "- Raters: ", result_IN$raters, "\n" ) )
    cat( paste( "- Name: ", result_IN$irr.name, "\n" ) )
    cat( paste( "- Alpha: ", result_IN$value, "\n" ) )
    cat( "\n" )

    # got a file passed in?
    if ( file_IN != "" ){

        # return output to the terminal.
        sink()

    }

} #-- END function output_kripp_results() --#

# Function: test_agreement()
#
# Accepts a matrix with coders as columns and observations per coder as rows.
#    Calculates percentage agreement and Krippendorf's Alpha for the matrix,
#    outputs the results.
#
# Hint: to make matrix, use cbind on vectors of coding results per coder.
test_agreement <- function( coding_matrix_IN, label_IN = "test_agreement", file_IN = "" ) {

    # return reference
    status_OUT <- "Success!"

    # declare variables
    coding_matrix_tall <- NULL
    coding_matrix_wide <- NULL
    agree_result <- NULL
    kripp_result <- NULL

    # got a file passed in?
    if ( file_IN != "" ){

        # yes - open it for output.
        sink( file_IN, append=TRUE, split=TRUE )

    }

    # output label
    cat( "\n#==============================================================================#\n" )
    cat( paste( label_IN, "\n" ) )
    cat( "#==============================================================================#\n\n" )

    # got a file passed in?
    if ( file_IN != "" ){

        # return output to the terminal.
        sink()

    }

    # store matrix passed in in tall, then transpose so we have wide.
    coding_matrix_tall <- coding_matrix_IN
    coding_matrix_wide <- t( coding_matrix_tall )

    # percentage agreement - wants the cbind matrix, not the rbind one.
    agree_result <- agree( coding_matrix_tall )
    output_agree_results( agree_result, file_IN )

    # Scott's Pi?

    # run Krippendorf's Alpha (not a good match to data - no variance)
    kripp_result <- kripp.alpha( coding_matrix_wide, method = "nominal" )
    output_kripp_results( kripp_result, file_IN )

    kripp_result <- kripp.alpha( coding_matrix_wide, method = "ordinal" )
    output_kripp_results( kripp_result, file_IN )

    kripp_result <- kripp.alpha( coding_matrix_wide, method = "interval" )
    output_kripp_results( kripp_result, file_IN )

    kripp_result <- kripp.alpha( coding_matrix_wide, method = "ratio" )
    output_kripp_results( kripp_result, file_IN )

    return( status_OUT )

} #-- END function test_agreement() --#
