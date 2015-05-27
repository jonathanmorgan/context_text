# link to good doc on qaptest(){sna} function: http://www.inside-r.org/packages/cran/sna/docs/qaptest

# First, need to load data - see (or just source() ) the file "sna-load_data.r".
# source( "sna-load_data.r" )
# does the following (among other things):
# Start with loading in tab-delimited files.
#humanNetworkData <- read.delim( "human-sourcenet_data-20150504-002453.tab", header = TRUE, row.names = 1, check.names = FALSE )
#calaisNetworkData <- read.delim( "puter-sourcenet_data-20150504-002507.tab", header = TRUE, row.names = 1, check.names = FALSE )

# remove the right-most column, which contains non-tie info on nodes.
#humanNetworkTies <- humanNetworkData[ , -ncol( humanNetworkData ) ]
#calaisNetworkTies <- calaisNetworkData[ , -ncol( calaisNetworkData )]

# convert each to a matrix
#humanNetworkMatrix <- as.matrix( humanNetworkTies )
#calaisNetworkMatrix <- as.matrix( calaisNetworkTies )

# imports
# install.packages( "sna" )
# install.packages( "statnet" )
library( "sna" )

# package up data for calling qaptest() - first make 3-dimensional array to hold
#    our two matrices - this is known as a "graph set".
g <- array( dim = c( 2, ncol( humanNetworkMatrix ), nrow( humanNetworkMatrix ) ) )

# then, place each matrix in one dimension of the array.
g[ 1, , ] <- humanNetworkMatrix
g[ 2, , ] <- calaisNetworkMatrix

# first, try a graph correlation
graph_correlation <- sna::gcor( humanNetworkMatrix, calaisNetworkMatrix )
graph_correlation

# try a qaptest...
qapGcorResult <- sna::qaptest( g, sna::gcor, g1 = 1, g2 = 2 )
summary( qapGcorResult )
plot( qapGcorResult )

# graph covariance...
graphCovariance <- sna::gcov( humanNetworkMatrix, calaisNetworkMatrix )
graphCovariance

# try a qaptest...
qapGcovResult <- sna::qaptest( g, sna::gcov, g1 = 1, g2 = 2 )
summary( qapGcovResult )
plot( qapGcovResult )

# Hamming Distance
graphHammingDist <- sna::hdist( humanNetworkMatrix, calaisNetworkMatrix )
graphHammingDist

# try a qaptest...
qapHdistResult <- sna::qaptest( g, sna::hdist, g1 = 1, g2 = 2 )
summary( qapHdistResult )
plot( qapHdistResult )

# graph structural correlation?
#graphStructCorrelation <- gscor( humanNetworkMatrix, calaisNetworkMatrix )
#graphStructCorrelation
