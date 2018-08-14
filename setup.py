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
    name='esimport',
    version='1.0.0',
    url='http://www.elevenwireless.com/',
    description='ElasticSearch Import Project',
    author='Eleven Wireless Inc',
    packages=find_packages(exclude=["*.tests", "*.tests.*", "tests.*", "tests"]),
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        'click==6.7',
        'elasticsearch==5.2.0',
        'hiredis==0.2.0',
        'pyodbc==4.0.22',
        'python-dateutil==2.6.1',
        'PyYAML==3.12',
        'raven==6.5.0',
        'redis==2.10.6',
        'six==1.11.0',
        'requests==2.19.1',
        'urllib3==1.23'
    ],
    entry_points={
        'console_scripts': ['esimport = esimport:cli']
    }
)
