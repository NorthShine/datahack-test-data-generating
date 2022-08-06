#!/usr/bin/env python

from distutils.core import setup

from setuptools import setup, find_packages

setup(
    name='no_spark_in_my_home',
    version='0.1.0',
    setup_requires=['wheel', 'faker', 'pyspark'],
    packages=find_packages(include=['src', 'src.*'])
)