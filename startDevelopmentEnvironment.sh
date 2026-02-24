#!/bin/bash

# Function to handle errors and cleanup the directory stack
function handle_failure(){
    if [ "$1" -ne 0 ]; then
        echo "Error: $2"
        # Return to the original directory and clear the stack before exiting
        pushd -0 && dirs -c > /dev/null
        exit 1
    fi
}

# Ensure we are not running inside an existing container
if [ -f /.dockerenv ]; then
   echo "Execution blocked: Already inside a Docker container."
else
    # Setup working directory paths
    SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
    pushd "$SCRIPT_DIR" >/dev/null

    # --- Dependency Check: Master Of VALAWAI (MOV) ---
    pushd ../ >/dev/null
    if [ ! -d MOV ]; then
        # Check if the MOV image exists even if source is missing
        if [ -z "$(docker images -q valawai/mov:latest 2> /dev/null)" ]; then
            echo "Critical Error: MOV docker image not found and MOV source directory is missing."
            pushd -0 && dirs -c > /dev/null
            exit 1
        fi
    else
        pushd MOV >/dev/null
        if [ -z "$(docker images -q valawai/mov:latest 2> /dev/null)" ]; then
            # Image is missing; build it from source
            ./buildDockerImages.sh -t latest
            handle_failure $? "Failed to build the MOV image from source."
        else
            # Check if source code has been updated since the last image build
            LATEST_SRC_COMMIT_DATE=$(TZ=UTC0 git log -1 --quiet --date=local --format="%cd" --date=format-local:'%Y-%m-%dT%H:%M:%S.000000000Z')
            CURRENT_IMG_CREATE_DATE=$(docker inspect -f '{{ .Created }}' valawai/mov:latest)
            
            if [[ "$LATEST_SRC_COMMIT_DATE" > "$CURRENT_IMG_CREATE_DATE" ]]; then
                echo "MOV source updates detected. Rebuilding MOV image..."
                ./buildDockerImages.sh -t latest
                handle_failure $? "Failed to rebuild the MOV image."
            fi
        fi
        popd >/dev/null
    fi
    popd >/dev/null

    # --- Configuration and Environment Setup ---
    BUILD_OPTS=""
    if [ "$1" = "no-cache" ]; then
        BUILD_OPTS="$BUILD_OPTS --no-cache"
        if [ -e .env ]; then
            source .env
        fi
        # Clear local database data for a clean slate
        rm -rf "${MONGO_LOCAL_DATA:-~/mongo_data/movDB}"
    fi

    # Explicit component naming to avoid 'autonomy' placeholder slips
    COMPONENT_ID="c1_llm_email_replier"
    DEV_IMAGE_TAG="valawai/$COMPONENT_ID:dev"
    DEV_CONTAINER_NAME="${COMPONENT_ID}_dev"

    # --- Build and Execution ---
    echo "Initializing development environment for: $COMPONENT_ID"
    DOCKER_BUILDKIT=1 docker build $BUILD_OPTS --pull -f docker/dev/Dockerfile -t "$DEV_IMAGE_TAG" .
    handle_failure $? "Build failed for environment image: $DEV_IMAGE_TAG"
    
    # Launch supporting infrastructure (RabbitMQ, MongoDB, MOV)
    docker compose -f docker/dev/docker-compose.yml up -d
    handle_failure $? "Failed to start required background services."
        
    # Set runtime parameters for the interactive container
    RUNTIME_PARAMS="--rm --name $DEV_CONTAINER_NAME --add-host=host.docker.internal:host-gateway -v /var/run/docker.sock:/var/run/docker.sock -it"
    
    # macOS specific fix for Testcontainers
    if [[ "$OSTYPE" == "darwin"* ]]; then
        RUNTIME_PARAMS="$RUNTIME_PARAMS -e TESTCONTAINERS_HOST_OVERRIDE=docker.for.mac.host.internal"
    fi

    # Enter the interactive shell
    docker run $RUNTIME_PARAMS -v "${PWD}":/app "$DEV_IMAGE_TAG" /bin/bash

    # Cleanup services upon exiting the bash shell
    ./stopDevelopmentEnvironment.sh

    popd >/dev/null
fi