#!/usr/bin/env bash

SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )
TARGET_FILE=~/.scons/site_scons/site_init.py

mkdir -p ~/.scons/site_scons

if [ ! -f "${TARGET_FILE}" ]
then
    echo "File ${TARGET_FILE} does not exist"
    echo "We will add one which supports reproducible builds"
    cp ${SCRIPT_DIR}/reproducible_site_init.py ${TARGET_FILE}
else
    echo "File ${TARGET_FILE} already exists"
    echo "We will not overwrite it. Please copy the content"
    echo "from ${SCRIPT_DIR}/reproducible_site_init.py"
fi
