"""Module responsible for representing todo items and writing to terminal."""
from __future__ import (absolute_import, division,
                        print_function, unicode_literals)
from builtins import *

import sjb.common.misc


## Global constants that determine the format of the display output
FORMAT_STYLE_SIMPLE = 1
FORMAT_STYLE_FULL = 2
FORMAT_STYLE_DEFAULT = FORMAT_STYLE_FULL
FORMAT_CHOICES = [FORMAT_STYLE_SIMPLE, FORMAT_STYLE_FULL]


def display_entry(entry, format_style=None):
  """Prints a string representation of a cheat sheet entry to stdout."""
  print(entry_repr(entry, format_style))

def display_entries(entries, format_style=None):
  """Prints a string representation of a cheat sheet to stdout."""
  print(entry_repr_heading(format_style))
  for entry in entries:
    print(entry_repr(entry, format_style))

def entry_repr_heading(format_style=None):
  """Prints a string heading corresponding to a cheat sheet list to stdout."""
  if format_style is None:
    format_style = FORMAT_STYLE_DEFAULT
  if format_style is FORMAT_STYLE_SIMPLE:
    return _entry_repr_simple.heading
  elif format_style is FORMAT_STYLE_FULL:
    return _entry_repr_full.heading
  else:
    raise Exception('This should never happen')

def entry_repr(entry, format_style=None):
  """Returns a string reprentation of a cheat sheet entry.

  Arguments:
    format_style: int indicating which output format should be used.

  Returns:
    str: String representation of a cheat sheet item.
  """
  if format_style is None:
    format_style = FORMAT_STYLE_DEFAULT
  if format_style is FORMAT_STYLE_SIMPLE:
    return _entry_repr_simple(entry)
  elif format_style is FORMAT_STYLE_FULL:
    return _entry_repr_full(entry)
  else:
    raise Exception('This should never happen')

def _repr_tags(tags):
  return '#' + ', #'.join(tags) if tags else ''

def _entry_repr_full(entry):
  """Gets the string representation of the entry.

  This one formats like:
  ID  primary   clue
                answer ....
                answer line 2 #tag1,#tag2

  Returns:
    str: a string representation of this entry.
  """
  rep = '%-3d %-10s %s\n%s\n%s' % (
    entry.oid, entry.primary, entry.clue, entry.answer, _repr_tags(entry.tags))
  rep = sjb.common.misc.indent_paragraph(rep, 15)
  return rep
  # return line1 + '\n' + line2
_entry_repr_full.heading = '%-3s %-10s %-20s' % (
  'ID', 'Primary', 'Clues')

def _entry_repr_simple(entry):
  """Gets the string representation of the entry without tags or primary.

  Returns:
    str: a string representing an entry.
  """
  line2 = '%-3d %-20s %s' % (
    entry.oid, entry.clue, sjb.common.misc.indent_paragraph(entry.answer, 25))
  return line2
_entry_repr_simple.heading = '%-3s %-20s %s' % ('ID', 'Clue', 'Answer')
