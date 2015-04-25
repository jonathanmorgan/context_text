# load DBI, RPostgreSQL
#install.packages( "DBI" )
#install.packages( "RPostgreSQL" )
library( "DBI" )
library( "RPostgreSQL" )

# create DB connection
driver <- dbDriver( "PostgreSQL" )
db_username <- ""
db_password <- ""
db_name <- ""
connection <- dbConnect( driver, user=db_username, password=db_password, dbname=db_name )

# test connection
dbListTables( connection )

# do stuff with connection!
