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
COPY requirements.txt .
COPY LICENSE .
COPY *.md .
COPY asyncapi.yaml .
COPY C1_llm_email_replier/ C1_llm_email_replier/

RUN pip install -e .

ENV RABBITMQ_HOST=mov-mq
ENV RABBITMQ_PORT=5672.
ENV RABBITMQ_USERNAME=mov.
ENV RABBITMQ_PASSWORD=password
ENV RABBITMQ_MAX_RETRIES=100
ENV RABBITMQ_RETRY_SLEEP=3

ENV REPLY_MAX_NEW_TOKENS=256.
ENV REPLY_TEMPERATURE=0.7
ENV REPLY_TOP_K=50
ENV REPLY_TOP_P=0.95
ENV REPLY_SYSTEM_PROMPT="You are a polite chatbot who always try to provide solutions to the customers problems."

ENV LOG_CONSOLE_LEVEL=DEBUG
ENV LOG_FILE_LEVEL=DEBUG
ENV LOG_FILE_MAX_BYTES=1000000
ENV LOG_FILE_BACKUP_COUNT=5

CMD ["python", "C1_llm_email_replier"]