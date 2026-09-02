#! /usr/bin/env bash

set -e
set -x

# MongoDB is schemaless: create indexes and seed the first superuser.
# (Replaces the Alembic migrations of the original PostgreSQL template.)
python app/initial_data.py
