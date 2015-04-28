# link to good doc on qaptest(){sna} function: http://www.inside-r.org/packages/cran/sna/docs/qaptest

# imports
library( "sna" )

# first, need to load in the two matrices we want to compare.
# Start with loading in tab-delimited files.
human_network_data <- read.delim( "sourcenet_data-20150427-175642.tab", header = TRUE, row.names = 1, check.names = FALSE )
calais_network_data <- read.delim( "sourcenet_data-20150427-175701.tab", header = TRUE, row.names = 1, check.names = FALSE )

# remove the right-most column, which contains non-tie info on nodes.
human_network_ties <- human_network_data[ , -ncol( human_network_data ) ]
calais_network_ties <- calais_network_data[ , -ncol( calais_network_data )]

# convert each to a matrix
human_network_matrix <- as.matrix( human_network_ties )
calais_network_matrix <- as.matrix( calais_network_ties )

# package up data for calling qaptest()
