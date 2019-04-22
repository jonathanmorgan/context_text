# loading and prepping data based in part on: http://www.shizukalab.com/toolkits/sna/sna_data

#==============================================================================#
# imports
#==============================================================================#

# load in "context_text/R/sna/functions-sna.r"
source( "functions-sna.r" )

# includes:
# - function calculateListMean() - mean(), but with optional argument that lets
#    you set a minimum threshhold value for inclusion in the calculation.

#==============================================================================#
# code
#==============================================================================#

# first, need to load in the two matrices we want to compare.
# Start with loading in tab-delimited files.
humanNetworkData <- read.delim( "./data/sourcenet_data-20150812-012632-human.tab", header = TRUE, row.names = 1, check.names = FALSE )
calaisNetworkData <- read.delim( "./data/sourcenet_data-20150812-012701-compy.tab", header = TRUE, row.names = 1, check.names = FALSE )

# remove the right-most 2 columns, which contains non-tie info on nodes.
#humanNetworkTies <- humanNetworkData[ , c( -( ncol( humanNetworkData ) - 1 ), -ncol( humanNetworkData ) ) ]
#calaisNetworkTies <- calaisNetworkData[ , c( -( ncol( calaisNetworkData ) -1 ), -ncol( calaisNetworkData ) ) ]

# OR, remove the attribute columns using their names.
attrColumnNames <- names( humanNetworkData ) %in% c( "person_id", "person_type" )
humanNetworkTies <- humanNetworkData[ , !attrColumnNames ]
attrColumnNames <- names( calaisNetworkData ) %in% c( "person_id", "person_type" )
calaisNetworkTies <- calaisNetworkData[ , !attrColumnNames ]

# convert each to a matrix
humanNetworkMatrix <- as.matrix( humanNetworkTies )
calaisNetworkMatrix <- as.matrix( calaisNetworkTies )

# get person type vectors
humanPersonTypes <- humanNetworkData[ , ncol( humanNetworkData ) ]
calaisPersonTypes <- calaisNetworkData[ , ncol( calaisNetworkData ) ]

# get person ID vectors
humanPersonTypes <- humanNetworkData[ , ncol( humanNetworkData ) - 1 ]
calaisPersonTypes <- calaisNetworkData[ , ncol( calaisNetworkData ) - 1 ]

# calculate vectors of average tie weights for calais and human data for all
#    ties (including 0s) and just ties >= 1, and add each as columns to data
#    frame <type>NetworkData.

# human - include ties Greater than or equal to 0 (GE0)
humanMeanTieWeightGE0Vector <- apply( humanNetworkMatrix, 1, calculateListMean )
humanNetworkData$meanTieWeightGE0 <- humanMeanTieWeightGE0Vector

# human - include ties Greater than or equal to 1 (GE1)
humanMeanTieWeightGE1Vector <- apply( humanNetworkMatrix, 1, calculateListMean, minValueToIncludeIN = 1 )
humanNetworkData$meanTieWeightGE1 <- humanMeanTieWeightGE1Vector

# calais - include ties Greater than or equal to 0 (GE0)
calaisMeanTieWeightGE0Vector <- apply( calaisNetworkMatrix, 1, calculateListMean )
calaisNetworkData$meanTieWeightGE0 <- calaisMeanTieWeightGE0Vector

# calais - include ties Greater than or equal to 1 (GE1)
calaisMeanTieWeightGE1Vector <- apply( calaisNetworkMatrix, 1, calculateListMean, minValueToIncludeIN = 1 )
calaisNetworkData$meanTieWeightGE1 <- calaisMeanTieWeightGE1Vector

# Run above against tie matrices. Could also run against <type>NetworkTies data
#    frames:
#humanMeanTieWeightGE1Vector <- apply( humanNetworkTies, 1, calculateListMean, minValueToIncludeIN = 1 )
#calaisMeanTieWeightGE1Vector <- apply( calaisNetworkTies, 1, calculateListMean, minValueToIncludeIN = 1 )

# And, if you want averages of these:
humanMeanTieWeightWithZeroes <- mean( humanNetworkData$meanTieWeightGE1 )
humanMeanTieWeightNoZeroes <- calculateListMean( humanNetworkData$meanTieWeightGE1, minValueToIncludeIN = 1 )
calaisMeanTieWeightWithZeroes <- mean( calaisNetworkData$meanTieWeightGE1 )
calaisMeanTieWeightNoZeroes <- calculateListMean( calaisNetworkData$meanTieWeightGE1, minValueToIncludeIN = 1 )
