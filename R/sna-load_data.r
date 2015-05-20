# loading and prepping data based in part on: http://www.shizukalab.com/toolkits/sna/sna_data

# imports

# first, need to load in the two matrices we want to compare.
# Start with loading in tab-delimited files.
human_network_data <- read.delim( "human-sourcenet_data-20150504-002453.tab", header = TRUE, row.names = 1, check.names = FALSE )
calais_network_data <- read.delim( "puter-sourcenet_data-20150504-002507.tab", header = TRUE, row.names = 1, check.names = FALSE )

# remove the right-most column, which contains non-tie info on nodes.
human_network_ties <- human_network_data[ , -ncol( human_network_data ) ]
calais_network_ties <- calais_network_data[ , -ncol( calais_network_data ) ]

# convert each to a matrix
human_network_matrix <- as.matrix( human_network_ties )
calais_network_matrix <- as.matrix( calais_network_ties )
# First, read a delimited file of network data in to a data frame in R.

# get person type vectors
human_person_types <- human_network_data[ , ncol( human_network_data ) ]
calais_person_types <- calais_network_data[ , ncol( calais_network_data ) ]
