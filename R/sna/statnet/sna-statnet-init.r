# First, need to load data - see (or just source() ) the file "sna-load_data.r".

# setwd( ".." )  # go back up to root R directory.
# source( "sna-load_data.r" )
# setwd( "statnet" )  # come back.

# does the following (among other things):
# Start with loading in tab-delimited files.
#humanNetworkData <- read.delim( "human-sourcenet_data-20150504-002453.tab", header = TRUE, row.names = 1, check.names = FALSE )
#calaisNetworkData <- read.delim( "puter-sourcenet_data-20150504-002507.tab", header = TRUE, row.names = 1, check.names = FALSE )

# remove the right-most column, which contains non-tie info on nodes.
#humanNetworkTies <- humanNetworkData[ , -ncol( humanNetworkData ) ]
#calaisNetworkTies <- calaisNetworkData[ , -ncol( calaisNetworkData ) ]

# convert each to a matrix
#humanNetworkMatrix <- as.matrix( humanNetworkTies )
#calaisNetworkMatrix <- as.matrix( calaisNetworkTies )

# get person type vectors
#humanPersonTypes <- humanNetworkData[ , ncol( humanNetworkData ) ]
#calaisPersonTypes <- calaisNetworkData[ , ncol( calaisNetworkData ) ]


#==============================================================================#
# statnet
#==============================================================================#

# make sure you've loaded the statnet library
# install.packages( "statnet" )
library( "statnet" )

# convert matrices to statnet network object instance.
humanNetworkStatnet <- network( humanNetworkMatrix, matrix.type = "adjacency", directed = FALSE )
calaisNetworkStatnet <- network( calaisNetworkMatrix, matrix.type = "adjacency", directed = FALSE )

# If you have a file of attributes (each attribute is a column, with attribute
#    name the column name), you can associate those attributes when you create
#    the network.
# Also works with vectors of attributes that were in the original data file.
# attribute help: http://www.inside-r.org/packages/cran/network/docs/loading.attributes

# load attribute file:
#tab_attribute_test1 <- read.delim( "tab-test1-attribute_data.txt", header = TRUE, row.names = 1, check.names = FALSE )

# convert matrix to statnet network object instance.
#test1_statnet <- network( tab_test1_matrix, matrix.type = "adjacency", directed = FALSE, vertex.attr = tab_attribute_test1 )

# look at information now.
#test1_statnet

# Network attributes:
#  vertices = 314
#  directed = FALSE
#  hyper = FALSE
#  loops = FALSE
#  multiple = FALSE
#  bipartite = FALSE
#  total edges= 309
#    missing edges= 0
#    non-missing edges= 309
#
# Vertex attribute names:
#    person_type vertex.names
#
# No edge attributes

# - OR - you can just add the attribute values to an existing network.
#test1_statnet%v%"person_type" <- tab_attribute_test1$person_type
humanNetworkStatnet%v%"person_type" <- humanPersonTypes
calaisNetworkStatnet%v%"person_type" <- calaisPersonTypes

# WARNING from http://www.inside-r.org/packages/cran/network/docs/loading.attributes
# Note: order of attributes in the data frame MUST match order of vertex ids
#    otherwise the attribute will get assigned to the wrong vertex

# list out the person_type attribute values
#humanNetworkStatnet%v%"person_type"
#calaisNetworkStatnet%v%"person_type"

# to see information about network, just type the object name:
humanNetworkStatnet
calaisNetworkStatnet

# example output:
# ---------------
# Network attributes:
#   vertices = 339
#   directed = FALSE
#   hyper = FALSE
#   loops = FALSE
#   multiple = FALSE
#   bipartite = FALSE
#   total edges= 312
#     missing edges= 0
#     non-missing edges= 312
#
# Vertex attribute names:
#     person_type vertex.names
#
# No edge attributes
