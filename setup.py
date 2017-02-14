#!/usr/bin/env python

from setuptools import setup, find_packages


setup(
    name='ESImport',
    version='1.0.0',
    url='http://www.elevenwireless.com/',
    description='ElasticSearch Import Project',
    author='Eleven Wireless Inc',
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    install_require=[
        'PyYAML==3.12',
        'pyodbc==4.0.6',
        'elasticsearch==5.2.0',
    ],
)
