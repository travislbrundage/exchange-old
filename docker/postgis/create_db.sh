#!/bin/bash
set -e

POSTGRES="psql --username ${POSTGRES_USER}"
POSTGIS="psql --username ${POSTGRES_USER} --dbname exchange_data"

PGPASSWORD='${DB_PASS}'
DJANGO="psql --username ${DB_USER} --dbname exchange"
GEOSERVER="psql --username ${DB_USER} --dbname exchange_data"

$POSTGRES <<EOSQL
CREATE DATABASE exchange OWNER ${DB_USER};
CREATE DATABASE exchange_data OWNER ${DB_USER};
EOSQL

$POSTGIS <<EOSQL
CREATE EXTENSION postgis;
EOSQL

$DJANGO <<EOSQL
create schema django;
EOSQL

$GEOSERVER <<EOSQL
create schema data;
EOSQL
