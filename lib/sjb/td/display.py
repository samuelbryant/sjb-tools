"""Module responsible for representing todo items and writing to terminal."""
from __future__ import (absolute_import, division,
                        print_function, unicode_literals)
from builtins import *

import sjb.common.misc
import sjb.td.classes


def _repr_tags(tags):
  return '#' + ', #'.join(tags) if tags else ''

def _repr_priority(priority):
  if priority is sjb.td.classes.PriorityEnum.DEFAULT.value:
    return ' '
  elif  priority is sjb.td.classes.PriorityEnum.URGENT.value:
    return '!'
  elif priority is sjb.td.classes.PriorityEnum.LONG_TERM.value:
    return 'L'
  else:
    raise Exception('should never happen')

def repr_todo(todo):
  """Returns a string reprentation of a todo item.

  This outputs todo items with the following format:
    53  ! This is the todo item text #tag1,#tag2
  Where 53 is the oid, the '!' is because the item is Urgent, and tag1,tag2
  are the tags.

  Returns:
    str: String representation of a todo item.
  """
  return sjb.common.misc.indent_paragraph(
    '%-3d %1s %s %s' % (
      todo.oid, _repr_priority(todo.priority), todo.text,
      _repr_tags(todo.tags)), 6)

def display_todo(todo):
  """Prints a string representation of a todo item to stdout."""
  print(repr_todo(todo))

def display_todos(todo_list):
  """Prints a string representation of a todo list to stdout."""
  for todo in todo_list:
    display_todo(todo)
