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
        query_string <- paste( query_string, " AND label = '", filter_on_label_IN, "'", sep = "" )

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
test_agreement <- function( coding_matrix_IN, label_IN = "test_agreement", file_IN = "", cor_use_IN = "all.obs", cor_method_IN = "pearson" ) {

    # return reference
    status_OUT <- "Success!"

    # declare variables
    coding_matrix_tall <- NULL
    coding_matrix_wide <- NULL
    tall_column_count <- -1
    column_number <- -1
    cor_result <- NULL
    agree_result <- NULL
    kripp_result <- NULL

    # store matrix passed in in tall, then transpose so we have wide.
    coding_matrix_tall <- coding_matrix_IN
    tall_column_count <- ncol( coding_matrix_tall )
    coding_matrix_wide <- t( coding_matrix_tall )

    # got a file passed in?
    if ( file_IN != "" ){

        # yes - open it for output.
        sink( file_IN, append=TRUE, split=TRUE )

    }

    # output label
    cat( "\n#=============================================================================#\n" )
    cat( paste( label_IN, "\n" ) )
    cat( "#=============================================================================#\n\n" )

    # also output variance and standard deviation of each list, and a
    #    correlation coefficient, just for diagnostics.
    for( column_number in 1 : tall_column_count ) {

        # output variance and standard deviation for this column.
        cat( paste( "var col", column_number, " = ", var( coding_matrix_tall[ , column_number ] ), "\n", sep = "" ) )
        cat( paste( "sd col", column_number, " = ", sd( coding_matrix_tall[ , column_number ] ), "\n", sep = "" ) )

    } #-- END loop over columns for variance and standard deviation --#

    # output correlations between columns.
    cor_result <- cor( coding_matrix_tall, use = cor_use_IN, method = cor_method_IN )

    # loop over columns in cor_result
    for( column_number in 1 : tall_column_count ) {

        # then, loop through rows to to output - from 1 to column_number - 1.
        if ( column_number > 1 ) {

            for( row_number in 1 : ( tall_column_count - 1 ) ) {

                # output the correlation coefficient.
                cat( paste( cor_method_IN, " r[", row_number, ",", column_number, "] = ", cor_result[ row_number, column_number ], "\n", sep = "" ) )

            } #-- END loop over rows. --#

        } #-- END check to make sure we aren't in first column. --#

    } #-- END loop over columns --#

    cat( "\n\n" )

    # got a file passed in?
    if ( file_IN != "" ){

        # return output to the terminal.
        sink()

    }

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
