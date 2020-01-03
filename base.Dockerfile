FROM python:3.8-buster

ENV LANGUAGE=en_US.utf-8 LANG=en_US.utf-8 LC_ALL=en_US.utf-8 INSIDE_DOCKER=1

# Install 'build-base' meta-package for gcc and other packages needed
RUN apt-get update && apt-get install -y iproute2 g++

# Install unixODBC driver and Microsoft ODBC driver
RUN curl https://packages.microsoft.com/keys/microsoft.asc -o microsoft.asc
RUN yes ''|apt-key add microsoft.asc
RUN curl https://packages.microsoft.com/config/debian/10/prod.list > /etc/apt/sources.list.d/mssql-release.list
RUN apt-get update
RUN ACCEPT_EULA=Y apt-get install -y msodbcsql17
RUN apt-get install unixodbc-dev

# Create and set /esimport as the working directory for this container
WORKDIR /esimport

# When the child image builds, copy the current folder's source files into /esimport
# except files ignored in .dockerignore
ONBUILD COPY . /esimport

