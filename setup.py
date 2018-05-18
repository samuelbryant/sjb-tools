from distutils.core import setup
import os
from os import path

here = path.abspath(path.dirname(__file__))
with open(path.join(here, 'README.md')) as f:
  long_description = f.read()




setup(
    name='sjb-todo',
    author='Sam Bryant',
    version='0.1.1.4',
    description='A simple CLI program to create, maintain and edit todo lists',
    long_description=long_description,
    #long_description_content_type='text/markdown',
    url='https://github.com/sicklybeans/sjb_todo',
    package_dir={'': 'lib'},
    packages=['sjb','sjb.td','sjb.common'],
    scripts=['bin/sjb-todo'],
    ## packages=['sjb',],
    license='MIT License'
)
