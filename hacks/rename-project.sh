#! /usr/bin/env bash

if [ "${1}" == "" ]; then
        echo "Usage: make init NEW_PROJECT_NAME='<new-project-name>'"
        exit 1
fi

export NAME="${1}"
export UNDERSCORE_NAME
UNDERSCORE_NAME="$(echo "${NAME}" | tr '-' '_')"

find . -type f -not -path './.git/*' -exec sed -i "s/prom-http-sd/${NAME}/g" {} \;
find . -type f -not -path './.git/*' -exec sed -i "s/prom_http_sd/${UNDERSCORE_NAME}/g" {} \;

find . -type d -not -path './.git/*' -name "*prom-http-sd*" -exec bash -c 'mv "$1" "${1//prom-http-sd/${NAME}}" ' _ {} \;
find . -type d -not -path './.git/*' -name "*prom_http_sd*" -exec bash -c 'mv "$1" "${1//prom_http_sd/${UNDERSCORE_NAME}}" ' _ {} \;
