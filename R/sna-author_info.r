# For this to work, you'll need to have run either of the following, including
#    all of the prerequisite files listed in each file:
#    - sourcenet/R/igraph/sna-igraph-network_stats.r
#    - sourcenet/R/statnet/sna-statnet-network_stats.r
# Also assumes that you haven't re-ordered the <type>NetworkData data frames.

#==============================================================================#
# information for all authors - source_type = 2 (reporter) or 4 (both source and reporter)
#==============================================================================#

# source_type = 2 (reporter) or 4 (both source and reporter)

# human
humanAuthorsNetworkData <- humanNetworkData[ humanNetworkData$person_type == 2 | humanNetworkData$person_type == 4, ]
humanAuthorsMeanDegree <- mean( humanAuthorsNetworkData$degree )
humanAuthorsMaxDegree <- max( humanAuthorsNetworkData$degree )
humanAuthorsMeanTieWeightGE0 <- mean( humanAuthorsNetworkData$meanTieWeightGE0 )
humanAuthorsMeanTieWeightGE1 <- mean( humanAuthorsNetworkData$meanTieWeightGE1 )

# calais
calaisAuthorsNetworkData <- calaisNetworkData[ calaisNetworkData$person_type == 2 | calaisNetworkData$person_type == 4, ]
calaisAuthorsMeanDegree <- mean( calaisAuthorsNetworkData$degree )
calaisAuthorsMaxDegree <- max( calaisAuthorsNetworkData$degree )
calaisAuthorsMeanTieWeightGE0 <- mean( calaisAuthorsNetworkData$meanTieWeightGE0 )
calaisAuthorsMeanTieWeightGE1 <- mean( calaisAuthorsNetworkData$meanTieWeightGE1 )

#==============================================================================#
# Generate information on individual reporters who have shared sources (subset
#    of all authors).
#==============================================================================#

# human - subsetting based on position of authors who had shared sources.
humanAuthorsSharedNetworkData <- humanNetworkData[ c( 3, 6, 9, 11, 12, 13, 14, 16, 21, 43, 44, 63, 169, 310 ), ]
humanAuthorsSharedMeanDegree <- mean( humanAuthorsSharedNetworkData$degree )
humanAuthorsSharedMaxDegree <- max( humanAuthorsSharedNetworkData$degree )
humanAuthorsSharedMeanTieWeightGE0 <- mean( humanAuthorsSharedNetworkData$meanTieWeightGE0 )
humanAuthorsSharedMeanTieWeightGE1 <- mean( humanAuthorsSharedNetworkData$meanTieWeightGE1 )

# calais
calaisAuthorsSharedNetworkData <- calaisNetworkData[ c( 3, 6, 9, 11, 12, 13, 16, 21, 44, 63, 169, 310 ), ]
calaisAuthorsSharedMeanDegree <- mean( calaisAuthorsSharedNetworkData$degree )
calaisAuthorsSharedMaxDegree <- max( calaisAuthorsSharedNetworkData$degree )
calaisAuthorsSharedMeanTieWeightGE0 <- mean( calaisAuthorsSharedNetworkData$meanTieWeightGE0 )
calaisAuthorsSharedMeanTieWeightGE1 <- mean( calaisAuthorsSharedNetworkData$meanTieWeightGE1 )
