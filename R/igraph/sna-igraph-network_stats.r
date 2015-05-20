# First, need to load data into statnet network object.  For
#    more details on that, see the files "sna-load_data.r" and
#    "sna-statnet_init.r".
# source( "sna-load_data.r" )
# source( "sna-igraph-init.r" )

# results in:
# - human_network_igraph - igraph network with human-coded network in it.
# - calais_network_igraph - igraph network with computer-coded network in it.

# Links:
# - CRAN page: http://cran.r-project.org/web/packages/igraph/index.html
# - Manual (PDF): http://cran.r-project.org/web/packages/igraph/igraph.pdf
# - intro.: http://horicky.blogspot.com/2012/04/basic-graph-analytics-using-igraph.html
# - good notes: http://www.shizukalab.com/toolkits/sna/node-level-calculations

# Also, be advised that statnet and igraph don't really play nice together.
#    If you'll be using both, best idea is to have a workspace for each.

#==============================================================================#
# igraph
#==============================================================================#

# Good notes:
# - http://assemblingnetwork.wordpress.com/2013/06/10/network-basics-with-r-and-igraph-part-ii-of-iii/

# make sure you've loaded the igraph library
# install.packages( "igraph" )
library( igraph )

# assuming that our igraph network object is in reference test1_igraph.

# try calling the degree() function on an igraph object.  Returns a number vector with names.
human_degree_vector <- degree( human_network_igraph )
calais_degree_vector <- degree( calais_network_igraph )

# For help with igraph::degree function:
??igraph::degree

# append the degrees to the network as a vertex attribute.
V( human_network_igraph )$degree <- human_degree_vector
V( calais_network_igraph )$degree <- calais_degree_vector

# calculate the mean of the degrees.
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
human_degree_centrality <- centralization.degree( human_network_igraph )
calais_degree_centrality <- centralization.degree( calais_network_igraph )

# graph-level undirected betweenness
human_betweenness_centrality <- centralization.betweenness( human_network_igraph, directed = FALSE )
calais_betweenness_centrality <- centralization.betweenness( calais_network_igraph, directed = FALSE )

# node-level undirected betweenness
human_betweenness <- human_betweenness_centrality$res
calais_betweenness <- calais_betweenness_centrality$res

# graph-level connectedness
human_connectedness <- connectedness( human_network_igraph )
calais_connectedness <- connectedness( calais_network_igraph )

#==============================================================================#
# output attributes to data frame
#==============================================================================#

# if you want to just work with the traits of the nodes/vertexes, you can
#    combine the attribute vectors into a data frame.

# first, output igraph object to see what attributes you have
human_network_igraph
calais_network_igraph

# then, combine them into a data frame.
human_node_attribute_df <- data.frame( id = V( human_network_igraph )$name, person_type = V( human_network_igraph )$person_type, degree = V( human_network_igraph )$degree )
calais_node_attribute_df <- data.frame( id = V( calais_network_igraph )$name, person_type = V( calais_network_igraph )$person_type, degree = V( calais_network_igraph )$degree )
