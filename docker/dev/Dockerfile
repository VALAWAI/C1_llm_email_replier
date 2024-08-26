# syntax=docker/dockerfile:experimental
FROM python:3.9.19-bullseye

ARG LLM_MODEL=HuggingFaceH4/zephyr-7b-beta

RUN apt-get -qy update && \
    apt-get -qy full-upgrade && \
    apt-get -qy install pip && \
	pip install -U "huggingface_hub[cli]" && \
	huggingface-cli download $LLM_MODEL 
	
WORKDIR /app
COPY setup.py .
RUN pip install -e .
RUN python setup.py test

RUN echo "PS1='\[\033[01;32m\]c1_llm_email_replier@dev\[\033[00m\]:\[\033[01;34m\]\w\[\033[00m\] \$ '" >> /root/.bashrc
RUN echo "alias testAll=\"pushd /app;python setup.py test;popd\"" >> /root/.bashrc
