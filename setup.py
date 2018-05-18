from distutils.core import setup
import os
from os import path

here = path.abspath(path.dirname(__file__))
with open(path.join(here, 'README.md')) as f:
  long_description = f.read()

# Single source important information
exec(open('lib/sjb/constants.py').read())

setup(
    name=program,
    author=__author__,
    version=__version__,
    description=description,
    long_description=long_description,
    url='https://github.com/sicklybeans/sjb_todo',
    package_dir={'': 'lib'},
    packages=['sjb','sjb.td','sjb.common'],
    scripts=['bin/sjb-todo'],
    license='MIT License'
)
