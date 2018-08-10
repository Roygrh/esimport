# Project's Dockerfile, uses the official Docker Python 3 image based on 
# Alpine Linux. See: https://hub.docker.com/_/python/
# All system and Python dependencies required by the project app should go here.
FROM amazonlinux:2017.09

ENV LANG=en_US.utf-8
ENV LC_ALL=en_US.utf-8
ENV INSIDE_DOCKER=1

# Install 'build-base' meta-package for gcc and other packages needed
RUN yum update -y && yum install -y python36-devel freetds freetds-devel \
        gcc-c++ unixODBC unixODBC-devel git nano

COPY ./docker/odbcinst.ini /etc/odbcinst.ini
COPY ./docker/odbc.ini /etc/odbc.ini
COPY ./docker/freetds.conf /etc/freetds.conf

# Create and set /gpnsreports as the working directory for this container
WORKDIR /esimport

# RUN printf '[FreeTDS]\nDescription=FreeTDS Driver\nDriver=/usr/lib/libtdsodbc.so\n' > /etc/odbcinst.ini

# Install Python dependencies but first Make sure we have the latest pip version
COPY . /esimport

# upgrade pip, install cython (required by mssql)
RUN pip-3.6 install -r dev-requirements.txt

ENTRYPOINT ["esimport"]
CMD ["sync"]
