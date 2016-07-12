#!/usr/bin/env python
# -*- coding: utf-8 -*-

from setuptools import setup, find_packages

setup(
      name='rauc_hawkbit',
      description='hawkBit client for RAUC',
      version='0.0',
      author='Bastian Stender and Enrico Joerns',
      author_email='entwicklung@pengutronix.de',
      license='LGPL-2.1',
      install_requires=[
          'aiohttp',
          'gbulb==0.2'
      ],
      packages=find_packages(),
      include_package_data=True,
      zip_safe=False,
      scripts=[
          'bin/rauc-hawkbit-client'
      ]
)
