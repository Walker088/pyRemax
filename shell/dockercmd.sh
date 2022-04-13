#!/usr/bin/env bash

export $(grep -v '^#' .proj.env | xargs)

dockerBuild() {
    docker build \
        --build-arg GECKODRIVER_VER="$DOCKER_GECKODRIVER_VER" \
        --build-arg FIREFOX_VER="$DOCKER_FIREFOX_VER" \
        -t $DOCKER_IMG_NAME:$DOCKER_IMG_VERSION_TAG .
}

dockerRun() {
    docker run -d --name $DOCKER_CONTAINER_NAME $DOCKER_IMG_NAME:$DOCKER_IMG_VERSION_TAG
}

dockerDown() {
    docker stop $DOCKER_CONTAINER_NAME
    docker rm $DOCKER_CONTAINER_NAME
}

dockerStart() {
    docker start $DOCKER_CONTAINER_NAME
}

dockerStop() {
    docker stop $DOCKER_CONTAINER_NAME
}

if [[ $# -eq 0 ]] ; then
    echo 'Please provide one of the arguments (e.g., bash shell/dockercmd.sh build):
    1 > build
    2 > start
    3 > stop
    3 > run
    3 > rm'

elif [[ $1 == build ]]; then
    dockerBuild

elif [[ $1 == start ]]; then
    dockerStart

elif [[ $1 == stop ]]; then
    dockerStop

elif [[ $1 == run ]]; then
    dockerRun

elif [[ $1 == rm ]]; then
    dockerDown
fi
