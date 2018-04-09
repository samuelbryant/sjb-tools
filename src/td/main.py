#!/usr/bin/python3
import os,sys,argparse
import td.classes
import td.fileio
import td.display


PROGRAM='sjb_todo'
USAGE='''\
sjb_todo command [<args>]

Where command can be:
  add      Add a new todo item to the todo list
  complete Marks a todo item as completed
  remove   Removes a todo item entirely from the cheatsheet
  update   Updates some fields from a todo item in todo list.
  show     Shows the todos from the todo list
'''


def _set_arg(string):
  return(set(string.split(',')))


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
      '--tags', type=_set_arg,
      help='Comma separated list of tags for this todo item')
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
    todo = td.classes.Todo(args.text, priority=args.priority, tags=args.tags)
    tl.add_todo(todo)
    td.fileio.save_todo_list(tl, fname=args.file)

  def update(self):
    p = argparse.ArgumentParser(
      prog = PROGRAM + ' update',
      description='Alter any of the fields of a todo item')

    p.add_argument(
      'id', type=int,
      help='ID of the entry you wish to update')
    p.add_argument(
      '--text', type=str, help='The text for this todo item')
    p.add_argument(
      '--tags', type=_set_arg,
      help='Comma separated list of tags for this todo item')
    p.add_argument(
      '--urgent', dest='priority', action='store_const',
      const=td.classes.PriorityEnum.URGENT.value,
      help='Sets this todo item as an urgent todo')
    p.add_argument(
      '--default', dest='priority', action='store_const',
      const=td.classes.PriorityEnum.DEFAULT.value,
      help='Sets this todo items priority to default')
    p.add_argument(
      '--longterm', dest='priority', action='store_const',
      const=td.classes.PriorityEnum.LONG_TERM.value,
      help='Sets this todo item as a long term todo')
    _add_arguments_generic(p)
    args = p.parse_args(sys.argv[2:])

    # Load todo list, add an entry, then save the results.
    tl = td.fileio.load_todo_list(fname=args.file)
    updated = tl.update_todo(
      args.id, text=args.text, priority=args.priority, tags=args.tags)
    # Save Todo list to file.
    td.fileio.save_todo_list(tl, fname=args.file)
    td.display.display_todo(updated)

  def show(self):
    p = argparse.ArgumentParser(
      prog = PROGRAM + ' show',
      description='Show the todo list or a subsection of it')
    p.add_argument(
      '--urgent', dest='priority', action='store_const',
      const=td.classes.PriorityEnum.URGENT.value,
      help='Only show urgent todos')
    p.add_argument(
      '--longterm', dest='priority', action='store_const',
      const=td.classes.PriorityEnum.LONG_TERM.value,
      help='Only show todos with priority "long term"')
    p.add_argument(
      '--default', dest='priority', action='store_const',
      const=td.classes.PriorityEnum.DEFAULT.value,
      help='Only show todos with priority "default"')
    p.add_argument(
      '--completed', dest='completed', action='store_const', const=True, 
      default=False, help='If set, will only show completed items. Otherwise this will only show uncompleted items')
    p.add_argument(
      '--tags', type=_set_arg,
      help='Only show todos which match this comma separated list of tags')
    _add_arguments_generic(p)
    args = p.parse_args(sys.argv[2:])
    
    tl = td.fileio.load_todo_list(fname=args.file)
    todos = tl.get_todos(
      priority=args.priority, tags=args.tags, finished=args.completed)
    td.display.display_todos(todos)

  def complete(self):
    p = argparse.ArgumentParser(
      prog = PROGRAM + ' complete',
      description='Marks a todo item as completed')
    p.add_argument(
      'id', type=int, help='ID of the todo you wish to mark as completed')
    p.add_argument(
      '--prompt', dest='force', action='store_const', const=0, default=1,
      help='Prompt the user before marking the item as completed')
    _add_arguments_generic(p)
    args = p.parse_args(sys.argv[2:])

    tl = td.fileio.load_todo_list(fname=args.file)
    
    # If not in force mode, ask user before proceeding.
    todo = tl.get_todo(args.id)
    if not args.force:
      question=\
        'The todo item given by id '+str(args.id)+' is:\n' + \
        td.display.repr_todo(todo, simple=False) + \
        '\nAre you sure you want to mark it as completed? '
      cont = td.display.prompt_yes_no(question, default=False)
      if not cont:
        exit(0)

    completed = tl.complete_todo(args.id)
    td.fileio.save_todo_list(tl, fname=args.file)

    td.display.display_todo(completed)

  def remove(self):
    p = argparse.ArgumentParser(
      prog = PROGRAM + ' remove',
      description='Remove a todo from list completely (this does NOT mark it as done)')
    p.add_argument('id', type=int, help='ID of the todo you wish to delete')
    p.add_argument(
      '--f', dest='force', action='store_const', const=1, default=0,
      help='Force: dont ask before completing the removal')
    _add_arguments_generic(p)
    args = p.parse_args(sys.argv[2:])

    tl = td.fileio.load_todo_list(fname=args.file)
    
    # If not in force mode, ask user before proceeding.
    todo = tl.get_todo(args.id)
    if not args.force:
      question=\
        'The todo item given by id '+str(args.id)+' is:\n' + \
        td.display.repr_todo(todo, simple=False) + \
        '\nAre you sure you want to delete it? '
      cont = td.display.prompt_yes_no(question, default=False)
      if not cont:
        exit(0)

    removed = tl.remove_todo(args.id)
    td.fileio.save_todo_list(tl, fname=args.file)


if __name__ == '__main__':
  Program()