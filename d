#!/bin/bash

GLEBOORU_WATCH=0

if [ "$1" == "-w" ] || [ "$1" == "--watch" ]; then
    GLEBOORU_WATCH=1
fi

docker-compose -f dev-docker-compose.yml up --build -d sql nginx && GLEBOORU_WATCH=$GLEBOORU_WATCH docker-compose -f dev-docker-compose.yml up --build --force-recreate server client
