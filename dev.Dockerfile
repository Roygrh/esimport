from registry.gitlab.com/distrodev/esimport:base


# upgrade pip, install cython (required by mssql)
RUN pip3 install --upgrade pip \
    && pip install -e .

# env variables for sql server host/ip in msodbc.ini
ENV MSSQL_HOST=mssql
ENV DEV=true

RUN /esimport/docker-entrypoint.sh