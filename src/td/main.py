#!/usr/bin/python3
import os,sys,argparse
import td.classes
import td.fileio
import td.display


PROGRAM='sjb_todo'
USAGE='''\
sjb_todo command [<args>]

Where command can be:
  add   Add a new todo item to the todo list
  show  Shows the todos from the todo list
'''


def _add_arguments_generic(parser):
  """Adds argparse arguments that apply universally to all commands."""
  parser.add_argument(
    '--file', type=str,
    help='Manually specify a todo file to work with')


class Program(object):

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
    p = argparse.ArgumentParser(
      prog = PROGRAM + ' add',
      description='Add a todo entry to your todo list')

    ## Core required arguments
    p.add_argument(
      'text', type=str, help='The text of this todo entry')
    p.add_argument(
      '--urgent', dest='priority', action='store_const',
      const=td.classes.PriorityEnum.URGENT.value,
      help='Sets this todo item as an urgent todo')
    p.add_argument(
      '--longterm', dest='priority', action='store_const',
      const=td.classes.PriorityEnum.LONG_TERM.value,
      help='Sets this todo item as a long term todo')
    _add_arguments_generic(p)
    args = p.parse_args(sys.argv[2:])

    # Load todo list, add an entry, then save the results
    tl = td.fileio.load_todo_list(fname=args.file)
    todo = td.classes.Todo(args.text, priority=args.priority)
    tl.add_todo(todo)
    td.fileio.save_todo_list(tl, fname=args.file)

  def show(self):
    p = argparse.ArgumentParser(
      prog = PROGRAM + ' show',
      description='Show the todo list or a subsection of it')
    _add_arguments_generic(p)
    args = p.parse_args(sys.argv[2:])
    
    tl = td.fileio.load_todo_list(fname=args.file)
    todos = tl.get_todos()
    td.display.display_todos(todos)

if __name__ == '__main__':
  Program()