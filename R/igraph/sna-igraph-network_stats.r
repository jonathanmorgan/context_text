# First, need to load SNA functions and load data into statnet network object.
#    For more details on that, see the files "functions-sna.r",
#    "sna-load_data.r" and "sna-igraph_init.r".
#
# assumes that working directory for statnet is sourcenet/R/igraph
# setwd( ".." )
# source( "functions-sna.r" )
# source( "sna-load_data.r" )
# setwd( "igraph" )
# source( "sna-igraph-init.r" )

# results in (among other things):
# - humanNetworkData - data frame with human-generated network data matrix in it, including columns on the right side for any node-specific attributes.
# - calaisNetworkData - data frame with computer-generated network data matrix in it, including columns on the right side for any node-specific attributes.
# - humanNetworkTies - data frame with only human-generated network data matrix in it, no node-specific attributes.
# - calaisNetworkTies - data frame with only computer-generated network data matrix in it, no node-specific attributes.
# - humanNetworkMatrix - matrix with only human-generated network data matrix in it, no node-specific attributes.
# - calaisNetworkMatrix - matrix with only computer-generated network data matrix in it, no node-specific attributes.
# - humanNetworkIgraph - igraph network with human-coded network in it, including node-specific attributes.
# - calaisNetworkIgraph - igraph network with computer-coded network in it, including node-specific attributes.

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

#==============================================================================#
# NODE level
#==============================================================================#

# try calling the degree() function on an igraph object.  Returns a number vector with names.
humanDegreeVector <- igraph::degree( humanNetworkIgraph )
calaisDegreeVector <- igraph::degree( calaisNetworkIgraph )

# For help with igraph::degree function:
??igraph::degree

# append the degrees to the network as a vertex attribute.
V( humanNetworkIgraph )$degree <- humanDegreeVector
V( calaisNetworkIgraph )$degree <- calaisDegreeVector

# add these also to their respective data frames.
humanNetworkData$degree <- humanDegreeVector
calaisNetworkData$degree <- calaisDegreeVector

# calculate the mean of the degrees.
humanDegreeMean <- mean( humanDegreeVector )
calaisDegreeMean <- mean( calaisDegreeVector )

# what is the standard deviation of these degrees?
humanDegreeSd <- sd( humanDegreeVector )
calaisDegreeSd <- sd( calaisDegreeVector )

# what is the variance of these degrees?
humanDegreeVar <- var( humanDegreeVector )
calaisDegreeVar <- var( calaisDegreeVector )

# what is the max value among these degrees?
humanDegreeMax <- max( humanDegreeVector )
calaisDegreeMax <- max( calaisDegreeVector )

# calculate and plot degree distributions

# human
humanDegreeFrequenciesTable <- table( humanDegreeVector )
humanDegreeDistribution <- igraph::degree.distribution( humanNetworkIgraph )
plot( humanDegreeDistribution, xlab = "human node degree" )
lines( humanDegreeDistribution )

# calais
calaisDegreeFrequenciesTable <- table( calaisDegreeVector )
calaisDegreeDistribution<- igraph::degree.distribution( calaisNetworkIgraph )
plot( calaisDegreeDistribution, xlab = "calais node degree" )
lines( calaisDegreeDistribution)

# subset vector to get only those that are above mean
humanAboveMeanVector <- humanDegreeVector[ humanDegreeVector > humanDegreeMean ]
calaisAboveMeanVector<- calaisDegreeVector[ calaisDegreeVector > calaisDegreeMean ]

# node-level transitivity
# create transitivity vectors.
humanTransitivityVector <- igraph::transitivity( humanNetworkIgraph, type = "local" )
calaisTransitivityVector <- igraph::transitivity( calaisNetworkIgraph, type = "local" )

# And, if you want averages of these:
humanMeanTransitivity <- mean( humanTransitivityVector, na.rm = TRUE )
calaisMeanTransitivity <- mean( calaisTransitivityVector, na.rm = TRUE )

# calculate author mean degree
humanAuthorDegreeMean <- calcAuthorMeanDegree( humanNetworkData )
calaisAuthorDegreeMean <- calcAuthorMeanDegree( calaisNetworkData )

# calculate source mean degree
humanSourceDegreeMean <- calcSourceMeanDegree( humanNetworkData )
calaisSourceDegreeMean <- calcSourceMeanDegree( calaisNetworkData )


#==============================================================================#
# NETWORK level
#==============================================================================#

# graph-level degree centrality
humanDegreeCentrality <- igraph::centralization.degree( humanNetworkIgraph )
calaisDegreeCentrality <- igraph::centralization.degree( calaisNetworkIgraph )

# graph-level undirected betweenness
humanBetweennessCentrality <- igraph::centralization.betweenness( humanNetworkIgraph, directed = FALSE )
calaisBetweennessCentrality <- igraph::centralization.betweenness( calaisNetworkIgraph, directed = FALSE )

# node-level undirected betweenness
humanBetweenness <- humanBetweennessCentrality$res
calaisBetweenness <- calaisBetweennessCentrality$res

# graph-level transitivity
humanTransitivity <- igraph::transitivity( humanNetworkIgraph, type = "global" )
calaisTransitivity <- igraph::transitivity( calaisNetworkIgraph, type = "global" )

# graph-level density
humanDensity <- igraph::graph.density( humanNetworkIgraph )
calaisDensity <- igraph::graph.density( calaisNetworkIgraph )

#==============================================================================#
# output attributes to data frame
#==============================================================================#

# if you want to just work with the traits of the nodes/vertexes, you can
#    combine the attribute vectors into a data frame.

# first, output igraph object to see what attributes you have
humanNetworkIgraph
calaisNetworkIgraph

# then, combine them into a data frame.
humanNodeAttributeDF <- data.frame( id = V( humanNetworkIgraph )$name, person_type = V( humanNetworkIgraph )$person_type, degree = V( humanNetworkIgraph )$degree )
calaisNodeAttributeDF <- data.frame( id = V( calaisNetworkIgraph )$name, person_type = V( calaisNetworkIgraph )$person_type, degree = V( calaisNetworkIgraph )$degree )
