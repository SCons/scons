#!/bin/bash

# store starting working directory
OLD_WD=$PWD

# determine working directory of shell script
WD=$(dirname "$(readlink -f "$0")")

cd $WD

# call docker container with local user
xhost +local:docker
export DOCKERUID=$(id -u)
export DOCKERGID=$(id -g)
docker-compose up -d

cd $OLD_WD

