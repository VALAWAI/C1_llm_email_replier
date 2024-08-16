#!/bin/bash
if [ -f /.dockerenv ]; then
   echo "You can not stop the development environment inside a docker container"
else
	DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
	pushd $DIR >/dev/null
	docker compose -f docker/dev/docker-compose.yml down
	if [ "$(docker container ls |grep c1_llm_email_replier_dev |wc -l)" -gt "0" ]
	then
		docker stop c1_llm_email_replier_dev
	fi
	popd >/dev/null
fi