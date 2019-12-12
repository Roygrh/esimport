FROM amazonlinux:2
  
ENV LANG=en_US.utf-8 LC_ALL=en_US.utf-8 INSIDE_DOCKER=1

# Install 'build-base' meta-package for gcc and other packages needed
RUN yum update -y && yum install -y python3-devel iproute gcc-c++ git nano

# Install unixODBC driver and Microsoft ODBC driver
ADD https://packages.microsoft.com/rhel/7/prod/msodbcsql17-17.3.1.1-1.x86_64.rpm /
ADD http://mirror.centos.org/centos/7/os/x86_64/Packages/unixODBC-2.3.1-14.el7.x86_64.rpm /
ADD http://mirror.centos.org/centos/7/os/x86_64/Packages/unixODBC-devel-2.3.1-14.el7.x86_64.rpm /
RUN yum install -y unixODBC-2.3.1-14.el7.x86_64.rpm unixODBC-devel-2.3.1-14.el7.x86_64.rpm
RUN ACCEPT_EULA=Y yum install -y msodbcsql17-17.3.1.1-1.x86_64.rpm

# Create and set /gpnsreports as the working directory for this container
WORKDIR /esimport

# Install Python dependencies but first Make sure we have the latest pip version
COPY . /esimport

# Create Microsoft ODBC DSN file
RUN sh docker/setup_db.bash

# upgrade pip, install cython (required by mssql)
RUN pip3 install --upgrade pip && pip install -r dev-requirements.txt

# set up esimport
RUN pip install -e .
