# source this to emulate the remote (AWS) environment with a
# local musite web database.
export RDS_DB_NAME="mutodb"
export RDS_HOSTNAME='localhost'
export RDS_PASSWORD=<password-for-local-site-database>
export RDS_PORT="5433"
export RDS_USER="muuser"
# ADVANCED:
#
# Consider putting these into the local virtual environment
# postactivate hook. Subsequently remove them from the pre- or
# postdeactivate hook with,
# unset RDS_DB_NAME
# unset ...
#   etc.
#   .
