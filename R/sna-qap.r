# link to good doc on qaptest(){sna} function: http://www.inside-r.org/packages/cran/sna/docs/qaptest

# imports
# install.packages( "sna" )
# install.packages( "statnet" )
library( "sna" )

# first, need to load in the two matrices we want to compare.
# Start with loading in tab-delimited files.
human_network_data <- read.delim( "sourcenet_data-20150429-002603.tab", header = TRUE, row.names = 1, check.names = FALSE )
calais_network_data <- read.delim( "sourcenet_data-20150429-002619.tab", header = TRUE, row.names = 1, check.names = FALSE )

# remove the right-most column, which contains non-tie info on nodes.
human_network_ties <- human_network_data[ , -ncol( human_network_data ) ]
calais_network_ties <- calais_network_data[ , -ncol( calais_network_data )]

# convert each to a matrix
human_network_matrix <- as.matrix( human_network_ties )
calais_network_matrix <- as.matrix( calais_network_ties )

# package up data for calling qaptest() - first make 3-dimensional array to hold
#    our two matrices - this is known as a "graph set".
g <- array( dim = c( 2,341,341 ) )

# then, place each matrix in one dimension of the array.
g[ 1, , ] <- human_network_matrix
g[ 2, , ] <- calais_network_matrix

# first, just try a graph correlation
graph_correlation <- gcor( human_network_matrix, calais_network_matrix )
graph_correlation

# try a qaptest...
qap_result <- qaptest( g, gcor, g1 = 1, g2 = 2 )
summary( qap_result )
plot( qap_result )
