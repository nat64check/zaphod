#!/usr/bin/env bash

n=0
until [ ${n} -ge 3 ]
   do
    psql -v ON_ERROR_STOP=0 --username "postgres" --dbname "postgres" <<-EOSQL && break
        CREATE USER zaphod WITH PASSWORD '${PGPASSWORD}';
        ALTER USER zaphod WITH PASSWORD '${PGPASSWORD}';
        CREATE DATABASE zaphod WITH OWNER zaphod TEMPLATE template_postgis;
EOSQL

    echo "Retrying in 5" >&2
    n=$[$n+1]
    sleep 5
done
