#!/bin/bash
set -e

psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "$POSTGRES_DB" <<-EOSQL
    CREATE USER postgres WITH PASSWORD 'postgres' SUPERUSER;
    ALTER USER postgres WITH PASSWORD 'postgres';
    CREATE DATABASE library_db;
    GRANT ALL PRIVILEGES ON DATABASE library_db TO postgres;
EOSQL

# Configure pg_hba.conf to allow connections from all hosts
echo "host all all 0.0.0.0/0 trust" >> /var/lib/postgresql/data/pg_hba.conf
echo "host all all ::/0 trust" >> /var/lib/postgresql/data/pg_hba.conf
