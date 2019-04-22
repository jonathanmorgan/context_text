# For this to work, you'll need to have run either of the following, including
#    all of the prerequisite files listed in each file:
#    - context_text/R/sna/igraph/sna-igraph-network_stats.r
#    - context_text/R/sna/statnet/sna-statnet-network_stats.r
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
#humanAuthorsSharedNetworkData <- humanNetworkData[ c( 3, 6, 9, 11, 12, 13, 14, 16, 21, 43, 44, 63, 169, 310 ), ]

# subsetting based on person IDs.
humanAuthorsSharedIDs <- c( 46, 23, 29, 161, 36, 425, 302, 66, 69, 73, 591, 84, 217, 223 )
humanAuthorsSharedNetworkData <- humanNetworkData[ humanNetworkData$person_id %in% humanAuthorsSharedIDs , ]

# human - make data
humanAuthorsSharedMeanDegree <- mean( humanAuthorsSharedNetworkData$degree )
humanAuthorsSharedMaxDegree <- max( humanAuthorsSharedNetworkData$degree )
humanAuthorsSharedMeanTieWeightGE0 <- mean( humanAuthorsSharedNetworkData$meanTieWeightGE0 )
humanAuthorsSharedMeanTieWeightGE1 <- mean( humanAuthorsSharedNetworkData$meanTieWeightGE1 )

# calais - subsetting based on position of authors who had shared sources.
#calaisAuthorsSharedNetworkData <- calaisNetworkData[ c( 3, 6, 9, 11, 12, 13, 16, 21, 44, 63, 169, 310 ), ]

# subsetting based on person IDs.
calaisAuthorsSharedIDs <- c( 46, 23, 29, 161, 36, 425, 302, 66, 69, 591, 84, 223 )
calaisAuthorsSharedNetworkData <- calaisNetworkData[ calaisNetworkData$person_id %in% calaisAuthorsSharedIDs , ]

# calais - make data
calaisAuthorsSharedMeanDegree <- mean( calaisAuthorsSharedNetworkData$degree )
calaisAuthorsSharedMaxDegree <- max( calaisAuthorsSharedNetworkData$degree )
calaisAuthorsSharedMeanTieWeightGE0 <- mean( calaisAuthorsSharedNetworkData$meanTieWeightGE0 )
calaisAuthorsSharedMeanTieWeightGE1 <- mean( calaisAuthorsSharedNetworkData$meanTieWeightGE1 )

#==============================================================================#
# Do some regression to see if article or source count predict source sharing.
#==============================================================================#

#------------------------------------------------------------------------------#
# first, set up data frames (from results of running python script:
#    context_text/examples/analysis/analysis-person_info.py)
#------------------------------------------------------------------------------#

# human coder, all authors.
humanIdVector <- c( 387, 394, 13, 3, 46, 23, 29, 30, 161, 36, 425, 302, 178, 566, 443, 377, 66, 505, 69, 73, 74, 332, 591, 336, 84, 599, 217, 348, 350, 223, 340, 460 )
humanSourceCountsVector <- c( 5, 7, 14, 6, 30, 12, 10, 10, 18, 18, 5, 15, 13, 0, 4, 2, 16, 4, 24, 6, 15, 3, 23, 8, 19, 8, 11, 1, 1, 7, 2, 1 )
humanSharedCountsVector <- c( 0, 0, 0, 0, 10, 7, 1, 0, 10, 7, 2, 2, 0, 0, 0, 0, 12, 0, 7, 1, 0, 0, 1, 0, 7, 0, 1, 0, 0, 7, 0, 0 )
humanArticleCountsVector <- c( 2, 1, 5, 4, 10, 3, 4, 3, 5, 5, 2, 6, 6, 1, 1, 2, 4, 1, 9, 2, 8, 1, 6, 3, 6, 4, 6, 1, 1, 1, 1, 1 )
humanAuthorsDF <- data.frame( humanIdVector, humanSourceCountsVector, humanSharedCountsVector, humanArticleCountsVector )
names( humanAuthorsDF ) <- c( "authorID", "sourceCount", "sharedCount", "articleCount" )

# human coder, only authors with shared sources.
humanSharedIdVector <- c( 46, 23, 29, 161, 36, 425, 302, 66, 69, 73, 591, 84, 217, 223 )
humanSharedSourceCountsVector <- c( 30, 12, 10, 18, 18, 5, 15, 16, 24, 6, 23, 19, 11, 7 )
humanSharedSharedCountsVector <- c( 10, 7, 1, 10, 7, 2, 2, 12, 7, 1, 1, 7, 1, 7 )
humanSharedArticleCountsVector <- c( 10, 3, 4, 5, 5, 2, 6, 4, 9, 2, 6, 6, 6, 1 )
humanSharedDF <- data.frame( humanSharedIdVector, humanSharedSourceCountsVector, humanSharedSharedCountsVector, humanSharedArticleCountsVector )
names( humanSharedDF ) <- c( "authorID", "sourceCount", "sharedCount", "articleCount" )

# computer coder, all authors.
compyIdVector <- c( 387, 394, 13, 3, 46, 23, 29, 30, 161, 36, 425, 302, 178, 566, 443, 377, 66, 505, 69, 73, 74, 332, 591, 336, 84, 599, 217, 350, 223, 758, 340, 460 )
compySourceCountsVector <- c( 5, 6, 14, 5, 25, 10, 11, 10, 14, 14, 5, 16, 12, 1, 4, 2, 15, 3, 23, 6, 16, 3, 21, 9, 17, 8, 11, 1, 5, 1, 2, 1 )
compySharedCountsVector <- c( 0, 0, 0, 0, 7, 6, 1, 0, 7, 5, 2, 2, 0, 0, 0, 0, 10, 0, 6, 0, 0, 0, 1, 0, 6, 0, 0, 0, 5, 0, 0, 0 )
compyArticleCountsVector <- c( 2, 1, 5, 4, 10, 3, 4, 3, 5, 5, 2, 6, 6, 1, 1, 2, 4, 1, 9, 2, 8, 1, 6, 3, 6, 4, 6, 1, 1, 1, 1, 1 )
compyAuthorsDF <- data.frame( compyIdVector, compySourceCountsVector, compySharedCountsVector, compyArticleCountsVector )
names( compyAuthorsDF ) <- c( "authorID", "sourceCount", "sharedCount", "articleCount" )

# computer coder, only authors with shared sources.
compySharedIdVector <- c( 46, 23, 29, 161, 36, 425, 302, 66, 69, 591, 84, 223 )
compySharedSourceCountsVector <- c( 25, 10, 11, 14, 14, 5, 16, 15, 23, 21, 17, 5 )
compySharedSharedCountsVector <- c( 7, 6, 1, 7, 5, 2, 2, 10, 6, 1, 6, 5 )
compySharedArticleCountsVector <- c( 10, 3, 4, 5, 5, 2, 6, 4, 9, 6, 6, 1 )
compySharedDF <- data.frame( compySharedIdVector, compySharedSourceCountsVector, compySharedSharedCountsVector, compySharedArticleCountsVector )
names( compySharedDF ) <- c( "authorID", "sourceCount", "sharedCount", "articleCount" )

#------------------------------------------------------------------------------#
# regression
#------------------------------------------------------------------------------#

# all human-coded authors:
humanLmResults <- lm( sharedCount ~ sourceCount + articleCount, data = humanAuthorsDF )

# all computer-coded authors:
compyLmResults <- lm( sharedCount ~ sourceCount + articleCount, data = compyAuthorsDF )

#------------------------------------------------------------------------------#
# means of counts from python file
#------------------------------------------------------------------------------#

# Article Count
humanAuthorsMeanArticleCount <- mean( humanAuthorsDF$articleCount )
humanAuthorsSharedMeanArticleCount <- mean( humanSharedDF$articleCount )
compyAuthorsMeanArticleCount <- mean( compyAuthorsDF$articleCount )
compyAuthorsSharedMeanArticleCount <- mean( compySharedDF$articleCount )

# Source Count
humanAuthorsMeanSourceCount <- mean( humanAuthorsDF$sourceCount )
humanAuthorsSharedMeanSourceCount <- mean( humanSharedDF$sourceCount )
compyAuthorsMeanSourceCount <- mean( compyAuthorsDF$sourceCount )
compyAuthorsSharedMeanSourceCount <- mean( compySharedDF$sourceCount )

# Shared Count
humanAuthorsMeanSharedCount <- mean( humanAuthorsDF$sharedCount )
humanAuthorsSharedMeanSharedCount <- mean( humanSharedDF$sharedCount )
compyAuthorsMeanSharedCount <- mean( compyAuthorsDF$sharedCount )
compyAuthorsSharedMeanSharedCount <- mean( compySharedDF$sharedCount )
