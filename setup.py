#!/usr/bin/env python
################################################################################
# Copyright 2002-2017 Eleven Wireless Inc.  All rights reserved.
#
# This file is the sole property of Eleven Wireless Inc. and can not be used
# or distributed without the expressed written permission of
# Eleven Wireless Inc.
################################################################################

from setuptools import setup, find_packages

setup(
    name="esimport",
    version="1.0.0",
    url="http://www.elevenwireless.com/",
    description="ElasticSearch Import Project",
    author="Eleven Wireless Inc",
    packages=find_packages(exclude=["*.tests", "*.tests.*", "tests.*", "tests"]),
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        "setuptools==75.5.0",
        "click==8.1.7",
        "elasticsearch==8.16.0",
        "hiredis==3.0.0",
        "pyodbc==5.2.0",
        "python-dateutil==2.9.0.post0",
        "PyYAML==6.0.2",
        "redis==5.2.0",
        "requests==2.32.3",
        "urllib3==2.2.3",
        "boto3==1.35.59",
        "orjson==3.10.11",
        "pydantic==2.9.2",
        "python-dotenv==1.0.1",
        "datadog==0.50.1",
    ],
    entry_points={"console_scripts": ["esimport = esimport:cli"]},
)
