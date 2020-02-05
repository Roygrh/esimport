from registry.gitlab.com/distrodev/esimport:base

# Create Microsoft ODBC DSN file
RUN sh setup_db.bash

# upgrade pip, install cython (required by mssql)
RUN pip3 install --upgrade pip \
    && pip install -r dev-requirements.txt \
    && pip install -e .

# Disable parent images entrypoint
ENTRYPOINT []

CMD ["esimport"]
