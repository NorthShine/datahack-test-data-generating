#!/usr/bin/env python

from distutils.core import setup

from setuptools import setup, find_packages

setup(
    name='no_spark_in_my_home',
    version='0.1.2',
    author=['scripthound, nomilkinmyhome'],
    install_requires=[
        'faker',
        'pyspark'
    ],
    setup_requires=['wheel', 'faker', 'pyspark'],
    packages=find_packages(include=['src', 'src.*'])
)