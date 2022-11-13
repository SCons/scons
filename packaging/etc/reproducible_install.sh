#!/usr/bin/env bash

set -e
set -x

SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )

mkdir -p ~/.site_scons

if [ ! -f "~/.site_scons/site_init.py" ]
then
    echo "File ~/.site_scons/site_init.py does not exist"
    echo "We will add one which supports reproducible builds"
    cp ${SCRIPT_DIR}/site_init.py ~/.site_scons/site_init.py
else
    echo "File ~/.site_scons/site_init.py already exists"
    echo "We will not overwrite it. Please copy the content"
    echo "from ${SCRIPT_DIR}/site_init.py"
fi
