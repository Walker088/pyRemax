#!/usr/bin/env bash

export $(xargs < .proj.env)

flywayBaseline() {
    docker run --rm --network host -v "$(pwd)/flyway:/flyway/sql"\
    flyway/flyway:$FLYWAY_VERSION baseline -url=$FLYWAY_URL -schemas=$PG_SCHEMA -user=$PG_USER -password=$PG_PASS
}

flywayMigrate() {
    docker run --rm --network host -v "$(pwd)/flyway:/flyway/sql"\
    flyway/flyway:$FLYWAY_VERSION migrate -url=$FLYWAY_URL -schemas=$PG_SCHEMA -user=$PG_USER -password=$PG_PASS -baselineOnMigrate=true
}

flywayInfo() {
    docker run --rm --network host -v "$(pwd)/flyway:/flyway/sql"\
    flyway/flyway:$FLYWAY_VERSION info -url=$FLYWAY_URL -schemas=$PG_SCHEMA -user=$PG_USER -password=$PG_PASS
}

if [[ $# -eq 0 ]] ; then
    echo 'Please provide one of the arguments (e.g., bash flywayCmd.sh info):
    1 > info
    2 > baseline
    3 > migrate'

elif [[ $1 == info ]]; then
    flywayInfo

elif [[ $1 == baseline ]]; then
    flywayBaseline

elif [[ $1 == migrate ]]; then
    flywayMigrate
fi
