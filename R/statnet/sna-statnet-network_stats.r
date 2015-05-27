# First, need to load data into statnet network object.  For
#    more details on that, see the files "sna-load_data.r" and
#    "sna-statnet_init.r".
# assumes that working directory for statnet is sourcenet/R/statnet.
# setwd( ".." )
# source( "sna-load_data.r" )
# setwd( "statnet" )
# source( "sna-statnet-init.r" )

# results in:
# - humanNetworkStatnet - statnet network with human-coded network in it.
# - calaisNetworkStatnet - statnet network with computer-coded network in it.

# Links:
# - manual (PDF): http://cran.r-project.org/web/packages/sna/sna.pdf
# - good notes: http://www.shizukalab.com/toolkits/sna/node-level-calculations

# Also, be advised that statnet and igraph don't really play nice together.
#    If you'll be using both, best idea is to have a workspace for each.

#==============================================================================#
# statnet
#==============================================================================#

# make sure you've loaded the statnet library (includes sna)
# install.packages( "statnet" )
library( statnet )

#==============================================================================#
# NODE level
#==============================================================================#

# Use the degree function in the sna package to create vector of degree values
#    for each node.  Make sure to pass the gmode parameter to tell it that the
#    graph is not directed (gmode = "graph", instead of "digraph").
# Doc: http://www.inside-r.org/packages/cran/sna/docs/degree
humanDegreeVector <- sna::degree( humanNetworkStatnet, gmode = "graph" )
calaisDegreeVector <- sna::degree( calaisNetworkStatnet, gmode = "graph" )

# If you have other libraries loaded that also implement a degree function, you
#    can also call this with package name:
#humanDegreeVectorSna <- sna::degree( humanNetworkStatnet, gmode = "graph" )
#calaisDegreeVectorSna <- sna::degree( calaisNetworkStatnet, gmode = "graph" )

# output the vectors
humanDegreeVector
calaisDegreeVector

# Take the degree and associate it with each node as a node attribute.
#    (%v% is a shortcut for the get.vertex.attribute command)
humanNetworkStatnet %v% "degree" <- humanDegreeVector
calaisNetworkStatnet %v% "degree" <- calaisDegreeVector

# want more info on the degree function?  You can get to it eventually through
#    the following:
help( package = "sna" )
??sna::degree

# what is the average (mean) degree?
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

# subset vector to get only those that are above mean
humanAboveMeanVector <- humanDegreeVector[ humanDegreeVector > humanDegreeMean ]
calaisAboveMeanVector <- calaisDegreeVector[ calaisDegreeVector > calaisDegreeMean ]

# calculate and plot degree distributions

# human
humanDegreeFrequenciesTable <- table( humanDegreeVector )

# calais
calaisDegreeFrequenciesTable <- table( calaisDegreeVector )

#==============================================================================#
# NETWORK level
#==============================================================================#

# graph-level degree centrality
humanDegreeCentrality <- sna::centralization( humanNetworkStatnet, sna::degree, mode = "graph" )
calaisDegreeCentrality <- sna::centralization( calaisNetworkStatnet, sna::degree, mode = "graph" )

# node-level undirected betweenness
humanBetweenness <- sna::betweenness( humanNetworkStatnet, gmode = "graph", cmode = "undirected" )
calaisBetweenness <- sna::betweenness( calaisNetworkStatnet, gmode = "graph", cmode = "undirected" )

# graph-level betweenness centrality
humanBetweennessCentrality <- sna::centralization( humanNetworkStatnet, sna::betweenness, mode = "graph", cmode = "undirected" )
calaisBetweennessCentrality <- sna::centralization( calaisNetworkStatnet, sna::betweenness, mode = "graph", cmode = "undirected" )

# graph-level connectedness
humanConnectedness <- sna::connectedness( humanNetworkStatnet )
calaisConnectedness <- sna::connectedness( calaisNetworkStatnet )

#==============================================================================#
# output attributes to data frame
#==============================================================================#

# if you want to just work with the traits of the nodes/vertexes, you can
#    combine the attribute vectors into a data frame.

# first, output network object to see what attributes you have
humanNetworkStatnet
calaisNetworkStatnet

# then, combine node attributes into a data frame.
humanNodeAttributeDF <- data.frame( id = humanNetworkStatnet %v% "vertex.names", person_type = humanNetworkStatnet %v% "person_type", degree = humanNetworkStatnet %v% "degree" )
calaisNodeAttributeDF <- data.frame( id = calaisNetworkStatnet %v% "vertex.names", person_type = calaisNetworkStatnet %v% "person_type", degree = calaisNetworkStatnet %v% "degree" )
