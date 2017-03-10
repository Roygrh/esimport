FROM debian:jessie

ENV LC_ALL=C.UTF-8
ENV LANG=C.UTF-8

RUN apt update
RUN apt install -y curl apt-transport-https git
RUN apt install -y python3 python3-dev python3-pip
RUN apt install -y unixodbc-dev freetds-bin tdsodbc

# Setup database client unixODBC and freetds
ADD docker/setup_db.bash /tmp
RUN /tmp/setup_db.bash

ADD docker/auto.key /etc/ssh/docker.auto.key
ADD docker/auto.key.pub /etc/ssh/docker.auto.key.pub
ADD docker/ssh_config /tmp
RUN cat /tmp/ssh_config >> /etc/ssh/ssh_config
RUN ssh -o StrictHostKeyChecking=no bitbucket.org
# Needs ssh access key
RUN pip3 install git+ssh://git@bitbucket.org/distrodev/esimport.git@develop

ENTRYPOINT ["esimport"]
CMD ["sync"]
