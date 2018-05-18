#!/usr/bin/env python3.6
from setuptools import setup
import os
import sys
from os import path

here = path.abspath(path.dirname(__file__))
with open(path.join(here, 'README.md')) as f:
  long_description = f.read()

# Single source important information
exec(open('lib/sjb/constants.py').read())

if sys.version_info[0] != 3:
    print('This script requires Python 3')
    exit(1)

setup(
    name=program,
    author=__author__,
    version=__version__,
    description=description,
    install_requires=[
        'future>=0.16.0',
        'configobj >= 5.0.6'
    ],
    long_description=long_description,
    url='https://github.com/sicklybeans/sjb_todo',
    package_dir={'': 'lib'},
    packages=['sjb','sjb.td','sjb.common'],
    scripts=['bin/sjb-todo'],
    license='MIT License'
)
