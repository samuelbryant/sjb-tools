"""Module containing tiny generically reusable code.
# TODO: Eventually this should be made more robust. Code that deals with
different things should be put into different modules.
"""
from __future__ import (absolute_import, division,
                        print_function, unicode_literals)
from builtins import *

import os
import sys
import textwrap

def _get_num_cols():
  return int(os.popen('stty size', 'r').read().split()[1])

def indent_paragraph(paragraph, indent_size):
  """Indents a paragraph except the first line."""
  width = _get_num_cols() - indent_size

  # Have to treat new lines specially
  lines = paragraph.split('\n')
  indented = [textwrap.wrap(line, width=width) for line in lines]
  indented = [y for x in indented for y in x]

  prefix = '\n' + (' ' * indent_size)
  return prefix.join(indented)

def prompt_yes_no(question, default=None):
  """Asks a yes/no question and returns either True or False."""
  prompt = (default is True and 'Y/n') or (default is False and 'y/N') or 'y/n'
  valid = {'yes': True, 'ye': True, 'y': True, 'no': False, 'n': False}

  while True:
    choice = input(question + prompt + ': ').lower()

    if not choice and default is not None:
      return default
    if choice in valid:
      return valid[choice]
    else:
      sys.stdout.write("Invalid reponse\n")
