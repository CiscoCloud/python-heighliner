#!/bin/bash

SERVICE=${1}
VERSION=${2}

echo "Building service: $SERVICE $VERSION"

fpm -s dir -t rpm -m $GERRIT_CHANGE_OWNER_EMAIL --url $BUILD_URL \
    --name service-$SERVICE --version $VERSION \
    --description "CCS Service Package" \
    --prefix /opt/ccs/services/$SERVICE \
    --exclude .git --exclude Vagrantfile \
    --epoch 1 \
    .
