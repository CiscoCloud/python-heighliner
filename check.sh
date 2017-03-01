#!/bin/bash
set -e

sudo pip install -r test-requirements.txt

pep8 heighliner
nosetests
