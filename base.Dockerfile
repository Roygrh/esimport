FROM python:3.8-buster

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

