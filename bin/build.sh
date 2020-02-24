#!/usr/bin/env bash
set -e

BASEDIR=$(dirname "$0")
DC_FILE=${BASEDIR}/../docker-compose.yml

if [ "${1:-}" = "start" ]; then
    docker-compose -f ${DC_FILE} up -d
elif [ "${1:-}" = "kill" ]; then
    docker-compose -f ${DC_FILE} down
    exit 0
fi

loader_cmd="python -m loader"
api_cmd="cd /src && python -m pytest -vv"

for service in loader api
do
    cmd="${service}_cmd"
    docker-compose -f ${DC_FILE} exec -e COLUMNS="`tput cols`" -e LINES="`tput lines`" ${service} bash -l -c "${!cmd}"
done
