#!/usr/bin/env python

from setuptools import setup, find_packages

setup(name='tap-amazon-mws',
      version='0.0.1',
      description='Singer.io tap for extracting data from the Amazon MWS API',
      author='Fishtown Analytics',
      url='http://fishtownanalytics.com',
      classifiers=['Programming Language :: Python :: 3 :: Only'],
      py_modules=['tap_amazon_mws'],
      install_requires=[
          'tap-framework==0.0.4',
          'mws',
      ],
      entry_points='''
          [console_scripts]
          tap-amazon-mws=tap_amazon_mws:main
      ''',
      packages=find_packages(),
      package_data={
          'tap_amazon_mws': [
              'schemas/*.json'
          ]
      })
