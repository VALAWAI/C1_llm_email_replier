#!/bin/bash
if ! docker stats --no-stream >/dev/null 2>&1; then
    echo "Docker does not seem to be running, run it first and retry"
    exit 1
else
	DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
	pushd $DIR > /dev/null
	TAG=$(grep --max-count=1 "__version__" src/c1_llm_email_replier/__init__.py  | awk -F "\"" '{ print $2 }')

	DOCKER_ARGS=""
	PLATFORMS=""
	while [[ $# -gt 0 ]]; do
      case $1 in
        -nc|--no-cache)
          DOCKER_ARGS="$DOCKER_ARGS --no-cache"
          shift # past argument
          ;;
        -t|--tag)
          TAG="$2"
          shift # past argument
          shift # past value
          ;;
        -p|--platform)
          PLATFORMS="$2"
          shift # past argument
          shift # past value
          ;;
        -dp|--default-platforms)
          PLATFORMS="linux/amd64,linux/arm64"
          shift # past argument
          ;;
        -h|--help*)
          echo "	-nc|--no-cache			Build a docker image without using the cache."
          echo "	-t|--tag <tag>			Build a docker image with a the **<tag>** name."
          echo "	-p|--platform <platforms>	Specify the architectures to build the docker."
          echo "	-dp|--default-platforms		Uses the default platforms (linux/arm64, linux/amd64)."
          echo "	-h|--help			Show a help message that explains these parameters."
          exit 0
          ;;
        *)
          echo "Unknown option $1"
          exit 1
          ;;
      esac
    done

	pushd $DIR > /dev/null
	if [[ -z $PLATFORMS ]];
	then
		DOCKER_BUILDKIT=1 docker build $DOCKER_ARGS --pull -f docker/main/Dockerfile -t valawai/c1_llm_email_replier:$TAG .
	else
		if docker buildx ls 2>/dev/null| grep -q c1_llm_email_replier_builder;
		then
  			DOCKER_BUILDKIT=1 docker buildx use c1_llm_email_replier_builder
		else
  			DOCKER_BUILDKIT=1 docker buildx create --name c1_llm_email_replier_builder --platform=$PLATFORMS --use
		fi
		DOCKER_ARGS="$DOCKER_ARGS --platform=$PLATFORMS"
		DOCKER_ARGS="$DOCKER_ARGS -f docker/main/Dockerfile"
		DOCKER_ARGS="$DOCKER_ARGS -t valawai/c1_llm_email_replier:$TAG"
		DOCKER_ARGS="$DOCKER_ARGS --cache-from=type=local,src=.c1_llm_email_replier-docker-cache"
		DOCKER_ARGS="$DOCKER_ARGS --cache-to=type=local,dest=.c1_llm_email_replier-docker-cache"
		DOCKER_ARGS="$DOCKER_ARGS --push"
		DOCKER_BUILDKIT=1 docker buildx build $DOCKER_ARGS .
	fi
	popd > /dev/null
fi
