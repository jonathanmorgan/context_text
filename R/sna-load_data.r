# loading and prepping data based in part on: http://www.shizukalab.com/toolkits/sna/sna_data

#==============================================================================#
# imports
#==============================================================================#

# load in "sourcenet/R/functions-sna.r"
source( "functions-sna.r" )

# includes:
# - function calculateListMean() - mean(), but with optional argument that lets
#    you set a minimum threshhold value for inclusion in the calculation.

#==============================================================================#
# code
#==============================================================================#

# first, need to load in the two matrices we want to compare.
# Start with loading in tab-delimited files.
humanNetworkData <- read.delim( "human-sourcenet_data-20150504-002453.tab", header = TRUE, row.names = 1, check.names = FALSE )
calaisNetworkData <- read.delim( "puter-sourcenet_data-20150504-002507.tab", header = TRUE, row.names = 1, check.names = FALSE )

# remove the right-most column, which contains non-tie info on nodes.
humanNetworkTies <- humanNetworkData[ , -ncol( humanNetworkData ) ]
calaisNetworkTies <- calaisNetworkData[ , -ncol( calaisNetworkData ) ]

# convert each to a matrix
humanNetworkMatrix <- as.matrix( humanNetworkTies )
calaisNetworkMatrix <- as.matrix( calaisNetworkTies )

# get person type vectors
humanPersonTypes <- humanNetworkData[ , ncol( humanNetworkData ) ]
calaisPersonTypes <- calaisNetworkData[ , ncol( calaisNetworkData ) ]

# create vector of average tie weights (mean of values in any cell with value
#    greater than 0 - if no ties, returns 0).
humanMeanTieWeights <- apply( humanNetworkTies, 1, calculateListMean, minValueToIncludeIN = 1 )
calaisMeanTieWeights <- apply( calaisNetworkTies, 1, calculateListMean, minValueToIncludeIN = 1 )

# And, if you want averages of these:
humanMeanTieWeightWithZeroes <- mean( humanMeanTieWeights )
humanMeanTieWeightNoZeroes <- calculateListMean( humanMeanTieWeights, minValueToIncludeIN = 1 )
calaisMeanTieWeightWithZeroes <- mean( calaisMeanTieWeights )
calaisMeanTieWeightNoZeroes <- calculateListMean( calaisMeanTieWeights, minValueToIncludeIN = 1 )
