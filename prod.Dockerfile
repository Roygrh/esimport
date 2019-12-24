FROM registry.gitlab.com/distrodev/esimport:base

# Create Microsoft ODBC DSN file
# msodbc is to be fetch fro ma prod S3 bucket at build time in `master` branch
RUN odbcinst -i -s -f msodbc.ini -l

# upgrade pip, install cython (required by mssql)
RUN pip3 install --upgrade pip && pip install -e .
