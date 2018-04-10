"""Module responsible for representing todo items and writing to terminal."""
import os
import textwrap
import sys
import td.classes

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

def _get_num_cols():
  return int(os.popen('stty size', 'r').read().split()[1])

def _indent_paragraph(paragraph, indent_size):
  width = _get_num_cols() - indent_size

  # Have to treat new lines specially
  lines = paragraph.split('\n')
  indented = [textwrap.wrap(line, width=width) for line in lines]
  indented = [y for x in indented for y in x]

  prefix = '\n' + (' ' * indent_size)
  return prefix.join(indented)

def _repr_tags(tags):
  return '#' + ', #'.join(tags) if tags else ''

def _repr_priority(priority):
  if priority is td.classes.PriorityEnum.DEFAULT.value:
    return ' '
  elif  priority is td.classes.PriorityEnum.URGENT.value:
    return '!'
  elif priority is td.classes.PriorityEnum.LONG_TERM.value:
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
  return _indent_paragraph(
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
