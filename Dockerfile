FROM debian:jessie

RUN apt update
RUN apt install -y curl apt-transport-https
RUN apt install -y python3 python3-dev python3-pip
RUN apt install -y unixodbc-dev freetds-bin tdsodbc

# Setup database client unixODBC and freetds
ADD docker/setup_db.bash /tmp
RUN /tmp/setup_db.bash

ADD docker/auto.key /etc/ssh/docker.auto.key
# Needs deployment ssh key
RUN pip3 install git+git@bitbucket.org:distrodev/esimport.git

ENTRYPOINT ["esimport"]
CMD ["sync"]
