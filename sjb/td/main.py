#!/usr/bin/python3.6
"""Module responsible for implementing the command line front end."""
from __future__ import (absolute_import, division,
                        print_function, unicode_literals)
from builtins import *

import argparse
import collections
import sys
import os
import sjb.constants
import sjb.common.misc
import sjb.td.classes
import sjb.td.fileio
import sjb.td.display
from sjb.td.classes import PriorityEnum

PROGRAM = 'sjb-todo'
DESCRIPTION = 'A simple CLI program to create, maintain and edit todo lists'
CMD_METAVAR = 'command'
CMD_HELP = collections.OrderedDict([
  ('add', 'Add a new todo item to the todo list'),
  ('complete', 'Marks a todo item as completed'),
  ('info', 'Shows meta info about the todo list'),
  ('lists', 'Lists all of the todo lists stored in the data directory'),
  ('remove', 'Removes a todo item entirely from the todo list'),
  ('show', 'Shows the todos from the todo list'),
  ('update', 'Updates some fields from a todo item in todo list')
])

PROMPT = 1
FORCE = 0


def _set_arg(string):
  return set(string.split(','))

def _add_arg_force(parser, verb, default=PROMPT):
  g = parser.add_mutually_exclusive_group()
  g.add_argument(
    '-f', '--force', dest='prompt', action='store_const', const=FORCE,
    default=default,
    help=('never prompts user before ' + verb + (
      ' (default)' if default is FORCE else '')))
  g.add_argument(
    '-i', '--prompt', dest='prompt', action='store_const', const=PROMPT,
    default=default,
    help=('asks user before ' + verb + (
      ' (default)' if default is PROMPT else '')))

def _add_arg_tags(parser, help):
  parser.add_argument('--tags', metavar='tags', type=_set_arg, help=help)

def _add_arg_priority(
    parser, helpmsg, default=sjb.td.classes.PriorityEnum.DEFAULT.value):
  parser.add_argument(
    '--priority', type=int, default=default, help=helpmsg,
    choices=[e.value for e in sjb.td.classes.PriorityEnum])

def _add_arg_oid(parser, help='the ID of the target todo'):
  parser.add_argument('oid', metavar='id', type=int, help=help)

def _add_arg_list(parser):
  # Arguments specifying the list file to work with
  list_group = parser.add_mutually_exclusive_group()
  list_group.add_argument(
    '-l', dest='list', metavar='name', type=str,
    help='the short name of the list file to read and write from. This is the local file name without an extension. The list file is assumed to be in the default data directory for this application.')
  list_group.add_argument(
    '--listpath', metavar='file', type=str,
    help='the full path name of the list file to read and write from')

def _no_args(parser):
  """Message displayed when no arguments are given."""
  parser.print_help(sys.stderr)
  sys.stderr.write('\nMissing the required argument: command\n')
  sys.exit(2)


class Program(object):
  """Class responsible for implementing command line front end."""

  def __init__(self):
    parser = argparse.ArgumentParser(
      prog=PROGRAM,
      formatter_class=_SubcommandHelpFormatter,
      description=DESCRIPTION,
      epilog='Use %(prog)s '+CMD_METAVAR+' -h to get help on individual commands')
    parser.add_argument(
      '-v', '--version', action='version', version='%(prog)s ' + sjb.constants.__version__)

    # Sub command parser
    cmds = parser.add_subparsers(title='Commands can be', metavar=CMD_METAVAR)
    cmds.required = True

    # Set up subcommand arguments
    for cmd in CMD_HELP:
      getattr(self, '_set_args_%s' % cmd)(cmds)

    # When no arguments are present, just show help message
    if len(sys.argv) <= 1:
      parser.print_help(sys.stderr)
      sys.stderr.write('\nMissing the required argument: command\n')
      sys.exit(2)

    # Call command
    args = parser.parse_args(sys.argv[1:])
    args.run(args)

  def _set_args_add(self, cmds):
    cmd = cmds.add_parser(
      'add', help=CMD_HELP['add'],
      description='The add command adds a new todo entry to the todo list.')
    cmd.set_defaults(run=self.add)
    _add_arg_tags(cmd, 'comma separated list of tags for this todo')
    _add_arg_priority(
      cmd, 'sets the priority level of this todo (%s)' % (', '.join(
        ['%d=%s' % (e.value, e.name) for e in PriorityEnum])))
    _add_arg_force(cmd, verb='adding new tags or list files', default=PROMPT)
    _add_arg_list(cmd)
    cmd.add_argument('text', type=str, help='the text of this todo item')

  def _set_args_complete(self, cmds):
    cmd = cmds.add_parser(
      'complete', help=CMD_HELP['complete'],
      description='The complete command marks the specified todo item as completed. This also sets the completion date to be the current time. You can also mark a completed item as not-completed with the --undo flag.')
    cmd.set_defaults(run=self.complete)
    cmd.add_argument(
      '--undo', dest='set_complete', action='store_const', const=False,
      default=True,
      help='when set, will mark completed items as not completed')
    _add_arg_oid(cmd, help='ID of the todo you wish to mark as completed')
    _add_arg_force(cmd, verb='making changes', default=FORCE)
    _add_arg_list(cmd)

  def _set_args_info(self, cmds):
    cmd_info = cmds.add_parser(
      'info', help=CMD_HELP['info'],
      description='The info command shows meta information about the todo list like which tags exist and how many todos have each tag.')
    cmd_info.set_defaults(run=self.info)
    _add_arg_list(cmd_info)

  def _set_args_lists(self, cmds):
    cmd = cmds.add_parser(
      'lists', help=CMD_HELP['lists'],
      description='The lists command displays the short name of all of the todo list files in the program data directory. These correspond to the allowed values for the -l argument.')
    cmd.set_defaults(run=self.lists)

  def _set_args_remove(self, cmds):
    cmd = cmds.add_parser(
      'remove', help=CMD_HELP['remove'],
      description='The remove command removes a todo item from the todo list')
    cmd.set_defaults(run=self.remove)
    _add_arg_oid(cmd, help='ID of the item you wish to delete')
    _add_arg_force(cmd, verb='removing the todo', default=PROMPT)
    _add_arg_list(cmd)

  def _set_args_show(self, cmds):
    cmd = cmds.add_parser(
      'show', help=CMD_HELP['show'],
      description='The show command can be used to display all of the entries in a given todo list or just a subset of them. It has arguments to filter by completion status and tags.')
    cmd.set_defaults(run=self.show)
    _add_arg_priority(
      cmd, 'only show items with this priority', default=None)
    cmd.add_argument(
      '--completed', dest='completed', action='store_const', const=True,
      default=False, help='will only show completed items. Default is to only show uncompleted items')
    _add_arg_tags(cmd, help='only show todos with all of the given tags')
    _add_arg_list(cmd)

  def _set_args_update(self, cmds):
    cmd = cmds.add_parser(
      'update', help=CMD_HELP['update'],
      description='The update command can overwrite existing todo entries with new values. Any attribute not explicitly specified will not be changed.')
    cmd.set_defaults(run=self.update)
    _add_arg_oid(cmd, help='ID of the item you wish to update')
    cmd.add_argument('--text', type=str, metavar='text', help='updated text for this todo item')
    _add_arg_tags(
      cmd, 'updated comma separated list of tags for this todo item')
    _add_arg_priority(cmd, 'updated priority for this todo item', default=None)
    _add_arg_force(cmd, verb='updating the item', default=FORCE)
    _add_arg_list(cmd)

  def add(self, args):
    # Load todo list, add an entry, then save the results
    tl = sjb.td.fileio.load_todo_list(list=args.list, listpath=args.listpath)
    todo = sjb.td.classes.Todo(
      args.text, priority=args.priority, tags=args.tags)

    # Check if any tag is new and prompts user before continuing.
    args.tags = args.tags or set()
    new_tags = tl.get_new_tags(args.tags)
    if new_tags and args.prompt is not FORCE:
      print('hello')
      question = (
        'The following tags are not present in the database: ' + \
        ', '.join(new_tags) + \
        '\nAre you sure you want to add this todo entry? ')
      cont = sjb.common.misc.prompt_yes_no(question, default=True)
      if not cont:
        exit(0)

    tl.add_item(todo)
    sjb.td.fileio.save_todo_list(tl, list=args.list, listpath=args.listpath)

    sjb.td.display.display_todo(todo)

  def complete(self, args):
    tl = sjb.td.fileio.load_todo_list(list=args.list, listpath=args.listpath)

    # If not in force mode, ask user before proceeding.
    todo = tl.get_item(args.oid)
    if args.prompt is not FORCE:
      question = 'The todo item given by id '+str(args.oid)+' is:\n' + \
        sjb.td.display.repr_todo(todo) + \
        '\nAre you sure you want to mark it as %s? ' % (
          'finished' if args.set_complete else 'unfinished')
      cont = sjb.common.misc.prompt_yes_no(question, default=False)
      if not cont:
        exit(0)

    updated = tl.complete_item(args.oid, set_complete=args.set_complete)
    sjb.td.fileio.save_todo_list(tl, list=args.list, listpath=args.listpath)

    sjb.td.display.display_todo(updated)

  def info(self, args):
    tl = sjb.td.fileio.load_todo_list(list=args.list, listpath=args.listpath)

    tag_set = tl.tag_set
    todos = tl.items
    num_urgent, num_closed, num_open = 0, 0, 0
    for todo in todos:
      if todo.finished:
        num_closed += 1
      else:
        num_open += 1
      if todo.priority == sjb.td.classes.PriorityEnum.URGENT:
        num_urgent += 1

    print('Todo list information:')
    print('  %-25s %s' % ('Number of todos', len(todos)))
    print('  %-25s %s' % ('Number of open', num_open))
    print('  %-25s %s' % ('Number of closed', num_closed))
    print('  %-25s %s' % ('Number of urgent', num_urgent))
    print('  %-25s %s' % ('Number tags', len(tag_set)))
    print('  %-25s %s' % ('Tag list', ', '.join(tag_set)))

  def lists(self, args):
    lists = sjb.td.fileio.get_all_list_files()
    print('Todo Lists: ' + ', '.join(lists))

  def remove(self, args):
    tl = sjb.td.fileio.load_todo_list(list=args.list, listpath=args.listpath)

    # If not in force mode, ask user before proceeding.
    todo = tl.get_item(args.oid)
    if args.prompt is not FORCE:
      question = \
        'The todo item given by oid '+str(args.oid)+' is:\n' + \
        sjb.td.display.repr_todo(todo) + \
        '\nAre you sure you want to delete it? '
      cont = sjb.common.misc.prompt_yes_no(question, default=False)
      if not cont:
        exit(0)

    tl.remove_item(args.oid)
    sjb.td.fileio.save_todo_list(tl, list=args.list, listpath=args.listpath)

  def update(self, args):
    # Load todo list, add an entry, then save the results.
    tl = sjb.td.fileio.load_todo_list(list=args.list, listpath=args.listpath)

    # Prompt user before continuing
    item = tl.get_item(args.oid)
    if args.prompt is not FORCE:
      question = (
        'The item given by oid '+str(args.oid)+' is:\n' + \
        sjb.td.display.repr_todo(item) + \
        '\nAre you sure you want to continue? ')
      cont = sjb.common.misc.prompt_yes_no(question, default=True)
      if not cont:
        exit(0)

    updated = tl.update_item(
      args.oid, text=args.text, priority=args.priority, tags=args.tags)
    # Save Todo list to file.
    sjb.td.fileio.save_todo_list(tl, list=args.list, listpath=args.listpath)
    sjb.td.display.display_todo(updated)

  def show(self, args):
    tl = sjb.td.fileio.load_todo_list(list=args.list, listpath=args.listpath)
    matcher = sjb.td.classes.TodoMatcher(
      tags=args.tags, priority=args.priority, finished=args.completed)
    items = tl.query_items(matcher)
    sjb.td.display.display_todos(items)


class _SubcommandHelpFormatter(argparse.RawDescriptionHelpFormatter):
  """Hacky fix that removes double line on commands."""
  def _format_action(self, action):
    parts = super(argparse.RawDescriptionHelpFormatter, self)._format_action(action)
    if action.nargs == argparse.PARSER:
      parts = "\n".join(parts.split("\n")[1:])
    return parts


def main(test=False):
  """Main entrypoint for this application. Called from the frontend script."""
  Program()
