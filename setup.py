#!/usr/bin/env python3.6
from setuptools import setup
import os
import sys
from os import path

here = path.abspath(path.dirname(__file__))
with open(path.join(here, 'README.md')) as f:
  long_description = f.read()

# Single source important information
exec(open('sjb/constants.py').read())

if sys.version_info[0] != 3:
    print('This script requires Python 3')
    exit(1)

setup(
    name=program,
    author=__author__,
    author_email='sbryant1014@gmail.com',
    version=__version__,
    description=description,
    install_requires=[
        'future >= 0.16.0',
        'configobj >= 5.0.6'
    ],
    python_requires='>=3',
    long_description=long_description,
    url='https://github.com/sicklybeans/sjb-tools',
    packages=['sjb', 'sjb.common', 'sjb.cs', 'sjb.td'],
    entry_points={
        'console_scripts': [
            'sjb-todo=sjb.td.main:main',
            'sjb-cheatsheet=sjb.cs.main:main'
        ],
    },
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Environment :: Console',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Topic :: Office/Business'
    ],
    license='MIT License'
)
