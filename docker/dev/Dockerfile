FROM python:3-slim

ENV LLM_MODEL=HuggingFaceH4/zephyr-7b-beta
ENV RABBITMQ_HOST=host.docker.internal

RUN --mount=type=cache,target=/var/cache/apt,sharing=locked \
  --mount=type=cache,target=/var/lib/apt,sharing=locked \
  apt -qy update && apt-get -qy install pip curl

RUN --mount=type=cache,target=/root/.cache/pip pip install -U "huggingface_hub"

RUN --mount=type=cache,target=/root/.cache/huggingface hf download $LLM_MODEL 
	
WORKDIR /build
COPY pyproject.toml .
COPY LICENSE .
COPY *.md .
COPY src/ src/
RUN --mount=type=cache,target=/root/.cache/pip pip install -e . && pip install hatch

WORKDIR /app

RUN echo "PS1='\[\033[01;32m\]c1_llm_email_replier@dev\[\033[00m\]:\[\033[01;34m\]\w\[\033[00m\] \$ '" >> /root/.bashrc
RUN echo "alias run=\"python src/c1_llm_email_replier\"" >> /root/.bashrc
RUN echo "alias testAll=\"hatch clean;hatch test\"" >> /root/.bashrc
RUN echo "alias test=\"hatch clean;hatch test -vv \"" >> /root/.bashrc
RUN echo "alias coverage=\"hatch clean;hatch test --cover\"" >> /root/.bashrc
RUN echo "alias fmt=\"hatch fmt --unsafe-fixes\"" >> /root/.bashrc
