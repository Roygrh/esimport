# Project's Dockerfile, uses the official Docker Python 3 image based on 
# Alpine Linux. See: https://hub.docker.com/_/python/
# All system and Python dependencies required by the project app should go here.
FROM python:3.6-alpine
LABEL authors="Walid ZIOUCHE <wziouche@gmail.com>"

ENV LC_ALL=C.UTF-8 LANG=C.UTF-8

# Install 'build-base' meta-package for gcc and other packages needed
# to compile dependencies listed in requirements.txt
RUN apk add --update --no-cache build-base libffi-dev openssl-dev git \
            libxml2-dev libxslt-dev unixodbc-dev freetds freetds-dev g++

# Create and set /gpnsreports as the working directory for this container
WORKDIR /esimport

# Install Python dependencies but first Make sure we have the latest pip version
COPY . /esimport
# upgrade pip, install cython (required by mssql)
RUN pip install --upgrade pip && pip install -e .

# Some clean-ups
RUN apk del build-base git && rm -rf /var/cache/apk/*

ENTRYPOINT ["esimport"]
CMD ["sync"]
