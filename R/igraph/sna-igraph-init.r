# First, need to load data - see (or just source() ) the file "sna-load_data.r".
# setwd( ".." )  # go back up to root R directory.
# source( "sna-load_data.r" )
# setwd( "igraph" )  # come back.

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
# igraph - more basic SNA package:
#==============================================================================#

# make sure you've loaded the igraph library
# install.packages( "igraph" )
library( igraph )

# convert matrix to igraph graph object instance.
humanNetworkIgraph <- graph.adjacency( humanNetworkMatrix, mode = "undirected", weighted = TRUE )
calaisNetworkIgraph <- graph.adjacency( calaisNetworkMatrix, mode = "undirected", weighted = TRUE )

# more details on graph.adjacency(): http://igraph.org/r/doc/graph.adjacency.html

# to see count of nodes and edges, just type the object name:
humanNetworkIgraph
calaisNetworkIgraph

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
V( humanNetworkIgraph )$name
V( calaisNetworkIgraph )$name

# add the person_types to the network.

# set vertex/node attribute person_type
V( humanNetworkIgraph )$person_type <- humanPersonTypes
V( calaisNetworkIgraph )$person_type <- calaisPersonTypes

# OR use function:
#humanNetworkIgraph <- set.vertex.attribute( humanNetworkIgraph, "person_type", value = humanPersonTypes )
#calaisNetworkIgraph <- set.vertex.attribute( calaisNetworkIgraph, "person_type", value = calaisPersonTypes )

# look at graph and person_type attribute values
humanNetworkIgraph
V( humanNetworkIgraph )$person_type
calaisNetworkIgraph
V( calaisNetworkIgraph )$person_type
