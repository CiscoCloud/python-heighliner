#!/bin/bash

SERVICE=${1}
VERSION=${2}

echo "Building service: $SERVICE $VERSION"

if [ -n "$GERRIT_BRANCH" ]; then
  REV_BRANCH=$GERRIT_BRANCH
else
  REV_BRANCH=`git symbolic-ref -q --short HEAD`
fi

REV_FORMATTED_BRANCH=`echo "$REV_BRANCH" | tr /_\- .`
REV_COUNT=`git rev-list HEAD --count`
SHORT_HASH=`git rev-parse --short HEAD`

RELEASE=$REV_COUNT
if [[ -n $REV_FORMATTED_BRANCH && $REV_FORMATTED_BRANCH != "master" ]]; then
  RELEASE="${RELEASE}.${REV_FORMATTED_BRANCH}"
fi
echo $RELEASE

git log --format="* %cd %aN%n- (%h) %s%d%n" --date=local -10 | \
  sed -r 's/[0-9]+:[0-9]+:[0-9]+ //' > ${SERVICE}_CHANGELOG

fpm -s dir -t rpm -m $GERRIT_CHANGE_OWNER_EMAIL --url $BUILD_URL \
    --name service-$SERVICE --version $VERSION \
    --iteration $RELEASE --rpm-changelog ${SERVICE}_CHANGELOG \
    --description "CCS Service Package" \
    --prefix /opt/ccs/services/$SERVICE \
    --exclude .git --exclude Vagrantfile \
    --exclude ${SERVICE}_CHANGELOG \
    --epoch 1 \
    .
