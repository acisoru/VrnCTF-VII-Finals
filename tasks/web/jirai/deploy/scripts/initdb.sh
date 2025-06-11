#!/bin/bash
set -e

echo "######### Starting to execute SH script... #########"

# If you have credentials for your DB uncomment the following two lines
USER_NAME='admin_user'
PASSWORD='omegaomegaomegaomega'

echo "ScyllaDB is up - executing CQL scripts"
for cql_file in ./scylla_scripts/*.cql;
do
  cqlsh scylla -u "${USER_NAME}" -p "${PASSWORD}" -f "${cql_file}" ;
  echo "######### Script ""${cql_file}"" executed!!! #########"
done

echo "Database initialization completed successfully"
echo "######### Execution of SH script is finished! #########"
echo "######### Stopping temporary instance! #########"