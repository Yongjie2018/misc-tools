FROM ubuntu:latest

RUN mkdir -p /tests/scripts
COPY ./loop-filecopy.sh /tests/scripts/loop-filecopy.sh

WORKDIR /tests/scripts

ENTRYPOINT ["/tests/scripts/loop-filecopy.sh"]
