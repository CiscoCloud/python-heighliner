#!/bin/bash

REPO=${1}
VERSION=${2}
DESTINATION=${3}

echo "Building repo: $REPO $VERSION"

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
  sed -r 's/[0-9]+:[0-9]+:[0-9]+ //' > ${REPO}_CHANGELOG

fpm -s dir -t rpm -m 'cis-devops@cisco.com' \
    --name repo-$REPO --version $VERSION \
    --iteration $RELEASE --rpm-changelog ${REPO}_CHANGELOG \
    --description "CCS Repo Package" \
    --prefix $DESTINATION/$REPO \
    --exclude .git --exclude Vagrantfile \
    --exclude ${REPO}_CHANGELOG \
    --exclude *.deb \
    --epoch 1 \
    .
