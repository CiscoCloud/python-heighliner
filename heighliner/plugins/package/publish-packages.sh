#!/bin/bash

ARTIFACT_SEARCH=${1}
SERVER=${2}
TARGET_DIR=${3}

(echo "cd ${TARGET_DIR}"; echo "put ${ARTIFACT_SEARCH}"; echo "bye")|sftp -b - $SERVER

