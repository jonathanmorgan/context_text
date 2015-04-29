# First, need to load data into either statnet or igraph network object.  For
#    more details on that, see the file "sna-load_data.r".

# Good notes:
# - http://www.shizukalab.com/toolkits/sna/node-level-calculations

# Also, be advised that statnet and igraph don't really play nice together.
#    If you'll be using both, best idea is to have a workspace for each.

#==============================================================================#
# igraph - more basic SNA package:
#==============================================================================#

# Good notes:
# - http://assemblingnetwork.wordpress.com/2013/06/10/network-basics-with-r-and-igraph-part-ii-of-iii/

# make sure you've loaded the igraph library
# install.packages( "igraph" )
library( igraph )

# assuming that our igraph network object is in reference test1_igraph.

# try calling the degree() function on an igraph object.  Returns a number vector with names.
degree_vector <- degree( test1_igraph )

# For help with igraph::degree function:
??igraph::degree

# calculate the mean of the degrees.
avg_degree <- mean( degree_vector )

# append the degrees to the network as a vertex attribute.
V( test1_igraph )$degree <- degree_vector

# if you want to just work with the traits of the nodes/vertexes, you can
#    combine the attribute vectors into a data frame.

# first, output igraph object to see what attributes you have
test1_igraph

# then, combine them into a data frame.
node_attribute_df <- data.frame( id = V( test1_igraph )$name, person_type = V( test1_igraph )$person_type, degree = V( test1_igraph )$degree )

#==============================================================================#
# statnet
#==============================================================================#

# make sure you've loaded the statnet library
# install.packages( "statnet" )
library( statnet )

# assuming that our statnet network object is in reference test1_statnet.

# Use the degree function in the sna package to create vector of degree values
#    for each node.  Make sure to pass the gmode parameter to tell it that the
#    graph is not directed (gmode = "graph", instead of "digraph").
# Doc: http://www.inside-r.org/packages/cran/sna/docs/degree
degree_vector <- degree( test1_statnet, gmode = "graph" )

# If you have other libraries loaded that also implement a degree function, you
#    can also call this with package name:
degree_vector <- sna::degree( test1_statnet, gmode = "graph" )

# output the vector
degree_vector

# want more info on the degree function?  You can get to it eventually through
#    the following:
help( package = "sna" )
??sna::degree

# what is the average (mean) degree?
avg_degree <- mean( degree_vector )

# subset vector to get only those that are above mean
above_mean_vector <- degree_vector[ degree_vector > avg_degree ]

# Take the degree and associate it with each node as a node attribute.
#    (%v% is a shortcut for the get.vertex.attribute command)
test1_statnet %v% "degree" <- degree_vector

# if you want to just work with the traits of the nodes/vertexes, you can
#    combine the attribute vectors into a data frame.

# first, output network object to see what attributes you have
test1_statnet

# then, combine them into a data frame.
node_attribute_df <- data.frame( id = test1_statnet %v% "vertex.names", person_type = test1_statnet %v% "person_type", degree = test1_statnet %v% "degree" )