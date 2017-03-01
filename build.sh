#!/bin/sh

REV_COUNT=`git rev-list HEAD --count`

fpm -s python -t rpm \
  --python-install-lib /usr/lib/python2.7/site-packages \
  --depends python-setuptools \
  --depends python-yaml \
  --iteration $REV_COUNT \
  setup.py

# Dependencies
fpm --python-install-lib /usr/lib/python2.7/site-packages -s python -t rpm click
fpm --python-install-lib /usr/lib/python2.7/site-packages -s python -t rpm testinfra
fpm --python-install-lib /usr/lib/python2.7/site-packages -s python -t rpm pytest
fpm --python-install-lib /usr/lib/python2.7/site-packages -s python -t rpm pytest-xdist
fpm --python-install-lib /usr/lib/python2.7/site-packages -s python -t rpm execnet
fpm --python-install-lib /usr/lib/python2.7/site-packages -s python -t rpm apipkg
