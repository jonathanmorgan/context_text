# load DBI, RPostgreSQL
#install.packages( "DBI" )
#install.packages( "RPostgreSQL" )
library( "DBI" )
library( "RPostgreSQL" )

# create DB connection
driver <- dbDriver( "PostgreSQL" )
dbUsername <- ""
dbPassword <- ""
dbName <- ""
connection <- dbConnect( driver, user=dbUsername, password=dbPassword, dbname=dbName )

# test connection
dbListTables( connection )

# do stuff with connection!
