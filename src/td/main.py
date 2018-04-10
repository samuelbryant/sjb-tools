#!/usr/bin/python3
"""Module responsible for implementing the command line front end."""
import sys
import argparse
import td.classes
import td.fileio
import td.display


PROGRAM = 'sjb_todo'
USAGE = '''\
sjb_todo command [<args>]

Where command can be:
  add      Add a new todo item to the todo list
  complete Marks a todo item as completed
  info    Shows meta info about cheatsheet
  remove   Removes a todo item entirely from the cheatsheet
  update   Updates some fields from a todo item in todo list.
  show     Shows the todos from the todo list
'''


def _set_arg(string):
  return set(string.split(','))


def _add_arguments_generic(parser):
  """Adds argparse arguments that apply universally to all commands."""
  parser.add_argument(
    '--file', type=str,
    help='Manually specify a todo file to work with')


class Program(object):
  """Class responsible for implementing command line front end."""

  def __init__(self):
    parser = argparse.ArgumentParser(
      description='Todo list program', usage=USAGE)
    parser.add_argument('command', type=str, help='Command to run')
    args = parser.parse_args(sys.argv[1:2])

    if not hasattr(self, args.command):
      print('Unrecognized command: '+str(args.command))
      parser.print_help()
      exit(1)

    # use dispatch pattern to invoke method with same name
    getattr(self, args.command)()

  def add(self):
    """Implements the 'add' command."""
    parser = argparse.ArgumentParser(
      prog=PROGRAM + ' add',
      description='Add a todo entry to your todo list')

    ## Core required arguments
    parser.add_argument(
      'text', type=str, help='The text of this todo entry')
    parser.add_argument(
      '--tags', type=_set_arg,
      help='Comma separated list of tags for this todo item')
    parser.add_argument(
      '--urgent', dest='priority', action='store_const',
      const=td.classes.PriorityEnum.URGENT.value,
      help='Sets this todo item as an urgent todo')
    parser.add_argument(
      '--longterm', dest='priority', action='store_const',
      const=td.classes.PriorityEnum.LONG_TERM.value,
      help='Sets this todo item as a long term todo')
    parser.add_argument(
      '--f', dest='force', action='store_const', const=1, default=0,
      help='Force: doesnt ask before adding an entry with new tags')
    _add_arguments_generic(parser)
    args = parser.parse_args(sys.argv[2:])

    # Load todo list, add an entry, then save the results
    tl = td.fileio.load_todo_list(fname=args.file)
    todo = td.classes.Todo(args.text, priority=args.priority, tags=args.tags)

    # Check if any tag is new and prompts user before continuing.
    new_tags = tl.get_new_tags(args.tags)
    if new_tags and not args.force:
      question = (
        'The following tags are not present in the database: ' + \
        ', '.join(new_tags) + \
        '\nAre you sure you want to add this todo entry? ')
      cont = td.display.prompt_yes_no(question, default=True)
      if not cont:
        exit(0)

    tl.add_todo(todo)
    td.fileio.save_todo_list(tl, fname=args.file)

    td.display.display_todo(todo)

  def info(self):
    """Implements the 'info' command."""
    parser = argparse.ArgumentParser(
      prog=PROGRAM + ' info',
      description='Shows meta-information about the todo list')
    _add_arguments_generic(parser)
    args = parser.parse_args(sys.argv[2:])

    tl = td.fileio.load_todo_list(fname=args.file)

    tag_set = tl.tag_set
    todos = tl.todos
    num_urgent, num_closed, num_open = 0, 0, 0
    for todo in todos:
      if todo.finished:
        num_closed += 1
      else:
        num_open += 1
      if todo.priority == td.classes.PriorityEnum.URGENT:
        num_urgent += 1

    print('Todo list information:')
    print('  %-25s %s' % ('Number of todos', len(todos)))
    print('  %-25s %s' % ('Number of open', num_open))
    print('  %-25s %s' % ('Number of closed', num_closed))
    print('  %-25s %s' % ('Number of urgent', num_urgent))
    print('  %-25s %s' % ('Number tags', len(tag_set)))
    print('  %-25s %s' % ('Tag list', ', '.join(tag_set)))

  def update(self):
    """Implements the 'update' command."""
    parser = argparse.ArgumentParser(
      prog=PROGRAM + ' update',
      description='Alter any of the fields of a todo item')

    parser.add_argument(
      'oid', type=int,
      help='ID of the entry you wish to update')
    parser.add_argument(
      '--text', type=str, help='The text for this todo item')
    parser.add_argument(
      '--tags', type=_set_arg,
      help='Comma separated list of tags for this todo item')
    parser.add_argument(
      '--urgent', dest='priority', action='store_const',
      const=td.classes.PriorityEnum.URGENT.value,
      help='Sets this todo item as an urgent todo')
    parser.add_argument(
      '--default', dest='priority', action='store_const',
      const=td.classes.PriorityEnum.DEFAULT.value,
      help='Sets this todo items priority to default')
    parser.add_argument(
      '--longterm', dest='priority', action='store_const',
      const=td.classes.PriorityEnum.LONG_TERM.value,
      help='Sets this todo item as a long term todo')
    _add_arguments_generic(parser)
    args = parser.parse_args(sys.argv[2:])

    # Load todo list, add an entry, then save the results.
    tl = td.fileio.load_todo_list(fname=args.file)
    updated = tl.update_todo(
      args.oid, text=args.text, priority=args.priority, tags=args.tags)
    # Save Todo list to file.
    td.fileio.save_todo_list(tl, fname=args.file)
    td.display.display_todo(updated)

  def show(self):
    """Implements the 'show' command."""
    parser = argparse.ArgumentParser(
      prog=PROGRAM + ' show',
      description='Show the todo list or a subsection of it')
    parser.add_argument(
      '--urgent', dest='priority', action='store_const',
      const=td.classes.PriorityEnum.URGENT.value,
      help='Only show urgent todos')
    parser.add_argument(
      '--longterm', dest='priority', action='store_const',
      const=td.classes.PriorityEnum.LONG_TERM.value,
      help='Only show todos with priority "long term"')
    parser.add_argument(
      '--default', dest='priority', action='store_const',
      const=td.classes.PriorityEnum.DEFAULT.value,
      help='Only show todos with priority "default"')
    parser.add_argument(
      '--completed', dest='completed', action='store_const', const=True,
      default=False, help='If set, will only show completed items. Otherwise' \
        ' this will only show uncompleted items')
    parser.add_argument(
      '--tags', type=_set_arg,
      help='Only show todos which match this comma separated list of tags')
    _add_arguments_generic(parser)
    args = parser.parse_args(sys.argv[2:])

    tl = td.fileio.load_todo_list(fname=args.file)
    todos = tl.get_todos(
      priority=args.priority, tags=args.tags, finished=args.completed)
    td.display.display_todos(todos)

  def complete(self):
    """Implements the 'complete' command."""
    parser = argparse.ArgumentParser(
      prog=PROGRAM + ' complete',
      description='Marks a todo item as completed')
    parser.add_argument(
      'oid', type=int, help='ID of the todo you wish to mark as completed')
    parser.add_argument(
      '--prompt', dest='force', action='store_const', const=0, default=1,
      help='Prompt the user before marking the item as completed')
    _add_arguments_generic(parser)
    args = parser.parse_args(sys.argv[2:])

    tl = td.fileio.load_todo_list(fname=args.file)

    # If not in force mode, ask user before proceeding.
    todo = tl.get_todo(args.oid)
    if not args.force:
      question = 'The todo item given by id '+str(args.oid)+' is:\n' + \
        td.display.repr_todo(todo) + \
        '\nAre you sure you want to mark it as completed? '
      cont = td.display.prompt_yes_no(question, default=False)
      if not cont:
        exit(0)

    completed = tl.complete_todo(args.oid)
    td.fileio.save_todo_list(tl, fname=args.file)

    td.display.display_todo(completed)

  def remove(self):
    """Implements the 'remove' command."""
    parser = argparse.ArgumentParser(
      prog=PROGRAM + ' remove',
      description='Remove a todo from list completely (this does NOT mark it' \
        'as done)')
    parser.add_argument(
      'oid', type=int, help='ID of the todo you wish to delete')
    parser.add_argument(
      '--f', dest='force', action='store_const', const=1, default=0,
      help='Force: dont ask before completing the removal')
    _add_arguments_generic(parser)
    args = parser.parse_args(sys.argv[2:])

    tl = td.fileio.load_todo_list(fname=args.file)

    # If not in force mode, ask user before proceeding.
    todo = tl.get_todo(args.oid)
    if not args.force:
      question = \
        'The todo item given by oid '+str(args.oid)+' is:\n' + \
        td.display.repr_todo(todo) + \
        '\nAre you sure you want to delete it? '
      cont = td.display.prompt_yes_no(question, default=False)
      if not cont:
        exit(0)

    tl.remove_todo(args.oid)
    td.fileio.save_todo_list(tl, fname=args.file)


if __name__ == '__main__':
  Program()
