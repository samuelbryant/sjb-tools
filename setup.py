from distutils.core import setup
import os
import git
from os import path

here = path.abspath(path.dirname(__file__))
with open(path.join(here, 'README.md'), encoding='utf-8') as f:
  long_description = f.read()

setup(
    name='sjb-todo',
    author='Sam Bryant',
    version_format='{tag}.dev{commitcount}+{gitsha}',
    setup_requires=['setuptools-git-version'],
    description='A simple CLI program to create, maintain and edit todo lists',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/sicklybeans/sjb_todo',
    # TODO
    package_dir={'': 'lib'},
    py_modules=['sjb.td', 'sjb.common'],
    scripts=['bin/sjb-todo'],
    ## packages=['sjb',],
    license='MIT License'
)
