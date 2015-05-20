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
# igraph - more basic SNA package:
#==============================================================================#

# make sure you've loaded the igraph library
# install.packages( "igraph" )
library( igraph )

# convert matrix to igraph graph object instance.
human_network_igraph <- graph.adjacency( human_network_matrix, mode = "undirected", weighted = TRUE )
calais_network_igraph <- graph.adjacency( calais_network_matrix, mode = "undirected", weighted = TRUE )

# more details on graph.adjacency(): http://igraph.org/r/doc/graph.adjacency.html

# to see count of nodes and edges, just type the object name:
human_network_igraph
calais_network_igraph

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
V( human_network_igraph )$name
V( calais_network_igraph )$name

# add the person_types to the network.

# set vertex/node attribute person_type
V( human_network_igraph )$person_type <- human_person_types
V( calais_network_igraph )$person_type <- calais_person_types

# OR use function:
#human_network_igraph <- set.vertex.attribute( human_network_igraph, "person_type", value = human_person_types )
#calais_network_igraph <- set.vertex.attribute( calais_network_igraph, "person_type", value = calais_person_types )

# look at graph and person_type attribute values
human_network_igraph
V( human_network_igraph )$person_type
calais_network_igraph
V( calais_network_igraph )$person_type
