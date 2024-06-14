#!/bin/bash

export GLEBOORU_WATCH=0

dockercompose="docker-compose.dev.yml"
windowsdockercompose="docker-compose.dev.windows.yml"

if [ "$1" == "-w" ] || [ "$1" == "--watch" ]; then
    export GLEBOORU_WATCH=1
fi

if [ "$OSTYPE" == "msys" ] || [ "$OSTYPE" == "cygwin" ] || [ "$OSTYPE" == "win32" ]; then
    sed 's/platform: linux\/arm64$//' $dockercompose > $windowsdockercompose
    dockercompose=$windowsdockercompose
fi

#docker compose -f $dockercompose up -d sql nginx && docker compose -f $dockercompose up --build --force-recreate server client
docker compose -f $dockercompose up -d sql && docker compose -f $dockercompose up --build --force-recreate server client nginx