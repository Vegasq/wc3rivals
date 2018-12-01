FROM ubuntu:18.04

MAINTAINER Mykola Yakovliev

ARG GATEWAY

RUN apt-get update
RUN apt-get install apt-utils -y
RUN apt-get install python3-pip -y

COPY dist/wc3inside-0.0.1-py3-none-any.whl /tmp/
RUN pip3 install /tmp/wc3inside-0.0.1-py3-none-any.whl

ENTRYPOINT $CMD
