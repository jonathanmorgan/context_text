# link to good doc on qaptest(){sna} function: http://www.inside-r.org/packages/cran/sna/docs/qaptest

# First, need to load data - see (or just source() ) the file "sna-load_data.r".
# source( "sna-load_data.r" )
# does the following (among other things):
# Start with loading in tab-delimited files.
#human_network_data <- read.delim( "human-sourcenet_data-20150504-002453.tab", header = TRUE, row.names = 1, check.names = FALSE )
#calais_network_data <- read.delim( "puter-sourcenet_data-20150504-002507.tab", header = TRUE, row.names = 1, check.names = FALSE )

# remove the right-most column, which contains non-tie info on nodes.
#human_network_ties <- human_network_data[ , -ncol( human_network_data ) ]
#calais_network_ties <- calais_network_data[ , -ncol( calais_network_data )]

# convert each to a matrix
#human_network_matrix <- as.matrix( human_network_ties )
#calais_network_matrix <- as.matrix( calais_network_ties )

# imports
# install.packages( "sna" )
# install.packages( "statnet" )
library( "sna" )

# package up data for calling qaptest() - first make 3-dimensional array to hold
#    our two matrices - this is known as a "graph set".
g <- array( dim = c( 2, ncol( human_network_matrix ), nrow( human_network_matrix ) ) )

# then, place each matrix in one dimension of the array.
g[ 1, , ] <- human_network_matrix
g[ 2, , ] <- calais_network_matrix

# first, try a graph correlation
graph_correlation <- gcor( human_network_matrix, calais_network_matrix )
graph_correlation

# try a qaptest...
qap_gcor_result <- qaptest( g, gcor, g1 = 1, g2 = 2 )
summary( qap_gcor_result )
plot( qap_gcor_result )

# graph covariance...
graph_covariance <- gcov( human_network_matrix, calais_network_matrix )
graph_covariance

# try a qaptest...
qap_gcov_result <- qaptest( g, gcov, g1 = 1, g2 = 2 )
summary( qap_gcov_result )
plot( qap_gcov_result )

# Hamming Distance
graph_hamming_dist <- hdist( human_network_matrix, calais_network_matrix )
graph_hamming_dist

# try a qaptest...
qap_hdist_result <- qaptest( g, hdist, g1 = 1, g2 = 2 )
summary( qap_hdist_result )
plot( qap_hdist_result )

# graph structural correlation?
#graph_struct_correlation <- gscor( human_network_matrix, calais_network_matrix )
#graph_struct_correlation
