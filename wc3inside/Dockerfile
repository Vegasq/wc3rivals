FROM alpine:3.8

MAINTAINER Mykola Yakovliev

RUN apk add --no-cache python3 && \
    python3 -m ensurepip && \
    rm -r /usr/lib/python*/ensurepip && \
    pip3 install --upgrade pip setuptools && \
    if [ ! -e /usr/bin/pip ]; then ln -s pip3 /usr/bin/pip ; fi && \
    if [[ ! -e /usr/bin/python ]]; then ln -sf /usr/bin/python3 /usr/bin/python; fi && \
    rm -r /root/.cache

COPY dist/wc3inside-0.0.1-py3-none-any.whl /tmp/
RUN pip3 install /tmp/wc3inside-0.0.1-py3-none-any.whl

ENTRYPOINT $CMD
