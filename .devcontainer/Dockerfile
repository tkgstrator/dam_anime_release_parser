FROM python:3.10-slim

ARG USERNAME=python
ARG GROUPNAME=python
ARG UID=1000
ARG GID=1000

RUN groupadd -g $GID $GROUPNAME
RUN useradd -m -s /bin/bash -u $UID -g $GID $USERNAME

USER python

WORKDIR /app