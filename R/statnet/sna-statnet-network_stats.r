# First, need to load data into statnet network object.  For
#    more details on that, see the files "sna-load_data.r" and
#    "sna-statnet_init.r".
# source( "sna-load_data.r" )
# source( "sna-statnet-init.r" )

# results in:
# - human_network_statnet - statnet network with human-coded network in it.
# - calais_network_statnet - statnet network with computer-coded network in it.

# Links:
# - manual (PDF): http://cran.r-project.org/web/packages/sna/sna.pdf
# - good notes: http://www.shizukalab.com/toolkits/sna/node-level-calculations

# Also, be advised that statnet and igraph don't really play nice together.
#    If you'll be using both, best idea is to have a workspace for each.

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
human_degree_vector <- degree( human_network_statnet, gmode = "graph" )
calais_degree_vector <- degree( calais_network_statnet, gmode = "graph" )

# If you have other libraries loaded that also implement a degree function, you
#    can also call this with package name:
#human_degree_vector_sna <- sna::degree( human_network_statnet, gmode = "graph" )
#calais_degree_vector_sna <- sna::degree( calais_network_statnet, gmode = "graph" )

# output the vectors
human_degree_vector
calais_degree_vector

# Take the degree and associate it with each node as a node attribute.
#    (%v% is a shortcut for the get.vertex.attribute command)
human_network_statnet %v% "degree" <- human_degree_vector
calais_network_statnet %v% "degree" <- calais_degree_vector

# want more info on the degree function?  You can get to it eventually through
#    the following:
help( package = "sna" )
??sna::degree

# what is the average (mean) degree?
human_degree_mean <- mean( human_degree_vector )
calais_degree_mean <- mean( calais_degree_vector )

# what is the standard deviation of these degrees?
human_degree_sd <- sd( human_degree_vector )
calais_degree_sd <- sd( calais_degree_vector )

# what is the variance of these degrees?
human_degree_var <- var( human_degree_vector )
calais_degree_var <- var( calais_degree_vector )

# subset vector to get only those that are above mean
human_above_mean_vector <- human_degree_vector[ human_degree_vector > human_degree_mean ]
calais_above_mean_vector <- calais_degree_vector[ calais_degree_vector > calais_degree_mean ]

# graph-level degree centrality
human_degree_centrality <- centralization( human_network_statnet, degree, mode = "graph" )
calais_degree_centrality <- centralization( calais_network_statnet, degree, mode = "graph" )

# node-level undirected betweenness
human_betweenness <- betweenness( human_network_statnet, gmode = "graph", cmode = "undirected" )
calais_betweenness <- betweenness( calais_network_statnet, gmode = "graph", cmode = "undirected" )

# graph-level betweenness centrality
human_betweenness_centrality <- centralization( human_network_statnet, betweenness, mode = "graph", cmode = "undirected" )
calais_betweenness_centrality <- centralization( calais_network_statnet, betweenness, mode = "graph", cmode = "undirected" )

# graph-level connectedness
human_connectedness <- connectedness( human_network_statnet )
calais_connectedness <- connectedness( calais_network_statnet )

#==============================================================================#
# output attributes to data frame
#==============================================================================#

# if you want to just work with the traits of the nodes/vertexes, you can
#    combine the attribute vectors into a data frame.

# first, output network object to see what attributes you have
human_network_statnet
calais_network_statnet

# then, combine node attributes into a data frame.
human_node_attribute_df <- data.frame( id = human_network_statnet %v% "vertex.names", person_type = human_network_statnet %v% "person_type", degree = human_network_statnet %v% "degree" )
calais_node_attribute_df <- data.frame( id = calais_network_statnet %v% "vertex.names", person_type = calais_network_statnet %v% "person_type", degree = calais_network_statnet %v% "degree" )
