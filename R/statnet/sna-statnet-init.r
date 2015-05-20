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

# get person type vectors
#human_person_types <- human_network_data[ , ncol( human_network_data ) ]
#calais_person_types <- calais_network_data[ , ncol( calais_network_data ) ]

#==============================================================================#
# statnet
#==============================================================================#

# make sure you've loaded the statnet library
# install.packages( "statnet" )
library( "statnet" )

# convert matrices to statnet network object instance.
human_network_statnet <- network( human_network_matrix, matrix.type = "adjacency", directed = FALSE )
calais_network_statnet <- network( calais_network_matrix, matrix.type = "adjacency", directed = FALSE )

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
human_network_statnet%v%"person_type" <- human_person_types
calais_network_statnet%v%"person_type" <- calais_person_types

# WARNING from http://www.inside-r.org/packages/cran/network/docs/loading.attributes
# Note: order of attributes in the data frame MUST match order of vertex ids
#    otherwise the attribute will get assigned to the wrong vertex

# list out the person_type attribute values
#human_network_statnet%v%"person_type"
#calais_network_statnet%v%"person_type"

# to see information about network, just type the object name:
human_network_statnet
calais_network_statnet

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
