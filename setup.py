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
        "click==7.0",
        "elasticsearch==5.2.0",
        "hiredis==1.0.1",
        "pyodbc==4.0.27",
        "python-dateutil==2.8.1",
        "PyYAML==5.1",
        "sentry-sdk==1.9.0",
        "redis==4.4.4",
        "requests==2.20.0",
        "urllib3==1.24.2",
        "boto3==1.10.28",
        "orjson==2.1.1",
        "pydantic==1.0",
        "python-dotenv==0.10.3",
        "datadog==0.47.0"
    ],
    entry_points={"console_scripts": ["esimport = esimport:cli"]},
)
