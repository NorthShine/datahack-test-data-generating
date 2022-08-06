#!/usr/bin/env python

from distutils.core import setup

from setuptools import setup, find_packages

setup(
    name='no_spark_in_my_home',
    version='0.1.3',
    author=['scripthound, nomilkinmyhome'],
    install_requires=[
        'faker',
        'pyspark',
        'pandas',
    ],
    setup_requires=['wheel', 'faker', 'pyspark', 'pandas'],
    packages=find_packages(include=['src', 'src.*'])
)