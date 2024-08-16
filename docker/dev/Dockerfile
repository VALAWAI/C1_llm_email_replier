# syntax=docker/dockerfile:experimental
FROM openjdk:21-jdk-slim-bookworm

USER root
ENV JAVA_HOME="/usr/local/openjdk-21"
SHELL ["/bin/bash", "-c"]
RUN apt-get update && \
    apt-get -qy full-upgrade && \
    apt-get install -qy curl unzip zip sed nano && \
    curl -sSL https://get.docker.com/ | sh && \
	curl -s "https://get.sdkman.io" | bash && \
	/bin/bash -c "source \"$HOME/.sdkman/bin/sdkman-init.sh\" && sdk install quarkus"

WORKDIR /app

RUN echo "PS1='\[\033[01;32m\]c1_llm_email_replier@dev\[\033[00m\]:\[\033[01;34m\]\w\[\033[00m\] \$ '" >> /root/.bashrc
RUN echo "alias mvn=\"/app/mvnw -Dstyle.color=always -Dquarkus-log-max-startup-records=100000\"" >> /root/.bashrc
RUN echo "alias mvnd=\"mvn -Dmaven.surefire.debug=\\\"-Xdebug -Xrunjdwp:transport=dt_socket,server=y,suspend=y,address=0.0.0.0:5005 -Xnoagent -Djava.compiler=NONE\\\"\"" >> /root/.bashrc
RUN echo "alias startServer=\"mvn clean compile quarkus:dev -DdebugHost=0.0.0.0\"" >> /root/.bashrc
RUN echo "/app/checkUpdate.sh" >> /root/.bashrc
