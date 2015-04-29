# based on: http://www.shizukalab.com/toolkits/sna/sna_data

# First, read a delimited file of network data in to a data frame in R.

# tab-delimited:
tab_test1 <- read.delim( "tab-test1-data.txt", header = TRUE, row.names = 1, check.names = FALSE )

# comma-delimited:
csv_test1 <- read.csv( "csv-test1.csv", header = TRUE, row.names = 1, check.names = FALSE )

#------------------------------------------------------------------------------#
# If extra data on nodes stored in rows at the end of the file:
#------------------------------------------------------------------------------#

# - person_type value for each person is last row of values.

# To just get ties, use the first 314 rows (omit the person_type row for now).
tab_test1_network <- tab_test1[ 1 : 314, ]
csv_test1_network <- csv_test1[ 1 : 314, ]

# better...
tab_test1_network <- tab_test1[ -nrow( tab_test1 ), ]
csv_test1_network <- csv_test1[ -nrow( csv_test1 ), ]

# convert to a matrix
tab_test1_matrix <- as.matrix( tab_test1_network )
csv_test1_matrix <- as.matrix( csv_test1_network )

# they appear to be identical.  Using tab one from here on.

#------------------------------------------------------------------------------#
# If extra data on nodes stored as columns at right of the file:
#------------------------------------------------------------------------------#

# example: person_type value for each person is last column of values.

# To just get ties, use all but the last column.
tab_test1_network <- tab_test1[ , -ncol( tab_test1 ) ]

# convert to a matrix
tab_test1_matrix <- as.matrix( tab_test1_network )

#==============================================================================#
# igraph - more basic SNA package:
#==============================================================================#

# make sure you've loaded the igraph library
# install.packages( "igraph" )
library( igraph )

# convert matrix to igraph graph object instance.
test1_igraph <- graph.adjacency( tab_test1_matrix, mode = "undirected", weighted = TRUE )

# more details on graph.adjacency(): http://igraph.org/r/doc/graph.adjacency.html

# to see count of nodes and edges, just type the object name:
test1_igraph

# Will output something like:
#
# IGRAPH UNW- 314 309 --
# + attr: name (v/c), weight (e/n)
#
# in the first line, "UNW-" are traits of graph:
# - 1 - U = undirected ( directed would be "D" )
# - 2 - N = named or not ( "-" instead of "N" )
# - 3 - W = weighted
# - 4 - B = bipartite ( "-" = not bipartite )
# 314 is where node count goes, 309 is edge count.
# The second line gives you information about the 'attributes' associated with the graph. In this case, there are two attributes, name and weight.  Next to each attribute name is a two-character construct that looks like "(v/c)".  The first letter is the thing the attribute is associated with (g = graph, v = vertex or node, e = edge).  The second is the type of the attribute (c = character data, n = numeric data).  So, in this case:
# - name (v/c) - the name attribute is a vertex/node attribute - the "v" in "(v/c)" - where the values are character data - the "c" in "(v/c)".
# - weight (e/n) - the weight attribute is an edge attribute - the "e" in "(e/n)" - where the values are numeric data - the "n" in "(e/n)".
# - based on: http://www.shizukalab.com/toolkits/sna/sna_data

# to reference a vertex attribute's values, use V( <network> )$<attribute_name>
# output the names for the nodes in the graph:
V( test1_igraph )$name

# use last row in original data file to make person_type an attribute of each node.

# first, get just the data frame row with person types (the last row):
person_types_row <- tab_test1[ 315, ]

# OR - use the nrow() function to just get the last row - breaks down if multiple attribute rows.
#person_types_row <- tab_test1[ nrow( tab_test1), ]

# populate list we will use to set node person_type attribute

# Don't just do these - they don't convert to simple list/vector, contain remnants of data frame
#person_types_list <- person_types_row
#person_types_list <- c( person_types_row )

# Convert to a list of numbers.
person_types_list <- as.numeric( person_types_row )

# Try this if you have character attribute...
#person_types_list <- unname( unlist( person_types_row ) )

# set vertex/node attribute person_type
V( test1_igraph )$person_type <- person_types_list

# OR use function:
#test1_igraph <- set.vertex.attribute( test1_igraph, "person_type", value = person_types_list )

# look at graph and person_type attribute values
test1_igraph
V( test1_igraph )$person_type

#==============================================================================#
# statnet
#==============================================================================#

# make sure you've loaded the statnet library
# install.packages( "statnet" )
library( statnet )

# convert matrix to statnet network object instance.
test1_statnet <- network( tab_test1_matrix, matrix.type = "adjacency", directed = FALSE )

# to see information about network, just type the object name:
test1_statnet

# Output example:
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
#    vertex.names
#
# No edge attributes

# If you have a file of attributes (each attribute is a column, with attribute
#    name the column name), you can associate those attributes when you create
#    the network.
# attribute help: http://www.inside-r.org/packages/cran/network/docs/loading.attributes

# load attribute file:
tab_attribute_test1 <- read.delim( "tab-test1-attribute_data.txt", header = TRUE, row.names = 1, check.names = FALSE )

# convert matrix to statnet network object instance.
test1_statnet <- network( tab_test1_matrix, matrix.type = "adjacency", directed = FALSE, vertex.attr = tab_attribute_test1 )

# look at information now.
test1_statnet

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
test1_statnet%v%"person_type" <- tab_attribute_test1$person_type

# WARNING from http://www.inside-r.org/packages/cran/network/docs/loading.attributes
# Note: order of attributes in the data frame MUST match order of vertex ids
#    otherwise the attribute will get assigned to the wrong vertex

# list out the person_type attribute values
test1_statnet%v%"person_type"
