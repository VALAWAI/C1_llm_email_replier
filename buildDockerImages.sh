#!/bin/bash
if ! docker stats --no-stream >/dev/null 2>&1; then
    echo "Docker does not seem to be running, run it first and retry"
    exit 1
else
	DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
	pushd $DIR > /dev/null
	VERSION=$(grep --max-count=1 "version='" setup.py  | awk -F "'" '{ print $2 }')
	DOCKER_ARGS=""
	if [ "no-cache" = "$1" ];
	then
		DOCKER_ARGS="$DOCKER_ARGS --no-cache"
		TAG=${2:-$VERSION}
	else
		TAG=${1:-$VERSION}
	fi
	pushd $DIR > /dev/null

	DOCKER_BUILDKIT=1 docker build $DOCKER_ARGS -f docker/main/Dockerfile -t valawai/c1_llm_email_replier:$TAG .
	popd > /dev/null
fi
