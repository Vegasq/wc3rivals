FROM ubuntu:18.04

MAINTAINER Mykola Yakovliev

RUN apt-get update
RUN apt-get install apt-utils -y
RUN apt-get install python3-pip -y
RUN apt-get install git -y
RUN echo "    IdentityFile ~/.ssh/id_rsa" >> /etc/ssh/ssh_config
RUN cd /tmp && git clone git@github.com:Vegasq/enemies.wc3inside.com.git
RUN pip install -r /tmp/classicbnet/requirements.txt
RUN cd /tmp/classicbnet && python setup.py install
EXPOSE 8080

CMD ["wc3inside-server"]