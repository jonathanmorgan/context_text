# loading and prepping data based in part on: http://www.shizukalab.com/toolkits/sna/sna_data

# imports

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
