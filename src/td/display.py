import os,textwrap,sys
import td.classes


def _repr_tags(tags):
  return((tags and '#' + ', #'.join(tags)) or '')

def _repr_priority(priority):
  if priority is td.classes.PriorityEnum.DEFAULT.value:
    return ' '
  elif  priority is td.classes.PriorityEnum.URGENT.value:
    return '!'
  elif priority is td.classes.PriorityEnum.LONG_TERM.value:
    return 'L'
  else:
    raise td.classes.ProgrammingError(
      'display._repr_priority', 'Illegal priority argument: '+str(priority))

def repr_todo(todo, simple=False):
  """Returns a string reprentation of a todo item.
  
  This outputs todo items with the following format:
    53  ! This is the todo item text #tag1,#tag2
  Where 53 is the ID, the '!' is because the item is Urgent, and tag1,tag2 are the tags.

  Returns:
    str: String representation of a todo item.
  """
  return '%-3d %1s %s %s' % (todo.id, _repr_priority(todo.priority), todo.text, _repr_tags(todo.tags))

def display_todo(todo):
  print(repr_todo(todo))

def display_todos(todo_list):
  for todo in todo_list:
    display_todo(todo)
