#!/usr/bin/env python

from setuptools import setup, find_packages

setup(name='singer-tap-amazon-mws',
      version='0.0.3',
      description='Singer.io tap for extracting data from the Amazon MWS API. Forked from https://github.com/fishtown-analytics/tap-amazon-mws',
      author='ian@mcallisternevins.com',
      url='https://github.com/imcallister/singer-tap-amazon-mws',
      classifiers=['Programming Language :: Python :: 3 :: Only'],
      py_modules=['singer_tap_amazon_mws'],
      install_requires=[
          'tap-framework==0.0.4',
          'mws',
      ],
      entry_points='''
          [console_scripts]
          singer-tap-amazon-mws=singer_tap_amazon_mws:main
      ''',
      packages=find_packages(),
      package_data={
          'singer_tap_amazon_mws': [
              'schemas/*.json'
          ]
      })
