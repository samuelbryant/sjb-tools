"""Module responsible for implementing the command line front end."""
from __future__ import (absolute_import, division,
                        print_function, unicode_literals)
from builtins import *

import argparse
import collections
import operator
import sys
import sjb.constants
import sjb.cs.classes
import sjb.cs.display
import sjb.cs.fileio
import sjb.common.misc

PROGRAM = 'sjb-cheatsheet'
DESCRIPTION = 'A simple CLI program to create, maintain and edit cheat sheets.'
CMD_METAVAR = 'command'
CMDS = collections.OrderedDict([
  ('add', [
    'Add a new entry to the cheat sheet',
    'The "add" command adds a new cheat sheet entry to the cheat sheet list.']),
  ('info', [
    'Shows meta info about the cheat sheet',
    'The "info" command shows meta information about the cheat sheet list like which tags exist and how many entries have each tag.']),
  ('lists', [
    'Lists all of the cheat sheet lists stored in the data directory',
    'The "lists" command displays the short name of all the cheat sheet lists in the program data directory. These correspond to the allowed values for the "-l" argument.']),
  ('remove', [
    'Removes an item entirely from the cheat sheet list',
    'The "remove" command removes an item from the cheat sheet list.']),
  ('show', [
    'Shows the items from the cheat sheet',
    'The "show" command displays all of the entries in a cheat sheet list or a subset of them. It has arguments to filter displayed results by tags.']),
  ('update', [
    'Updates some fields from an item in a cheat sheet',
    'The "update" command can overwrite existing cheat sheet items with new values. Any attribute not explicitly specified will not be changed.'
    ])
])

PROMPT = 1
FORCE = 0


def _set_arg(string):
  return set(string.split(','))


def _tags_arg(string):
  """Pulls out primary tag (first tag) from the others"""
  tags = string.split(',')
  return (tags[0], set(tags[1:]))

def _add_arg_oid(parser, help='the ID of the target item'):
  parser.add_argument('oid', metavar='id', type=int, help=help)

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

def _add_arg_style(parser, default=None):
  parser.add_argument(
    '--style', type=int,
    choices=sjb.cs.display.FORMAT_CHOICES, default=default,
    help='Specifies which format style is used when displaying entries.')

def _add_arg_list(parser):
  # Arguments specifying the list file to work with
  list_group = parser.add_mutually_exclusive_group()
  list_group.add_argument(
    '-l', dest='list', type=str, metavar='name',
    help='the short name of the cheatsheet file to read and write from. This is the local file name without an extension. The cheatsheet file is assumed to be in the default data directory for this application.')
  list_group.add_argument(
    '--listpath', metavar='file', type=str,
    help='the full path name of the cheatsheet file to read and write from')


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
  
    # Sub commands
    cmds = parser.add_subparsers(title='Commands can be', metavar=CMD_METAVAR)
    cmds.required = True

    # Set up subcommand arguments
    for cmd in CMDS:
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
      'add', help=CMDS['add'][0], description=CMDS['add'][1])
    cmd.set_defaults(run=self.add)

    _add_arg_force(cmd, verb='adding new tags or list files')
    _add_arg_list(cmd)
    _add_arg_style(cmd)
    cmd.add_argument(
      'tags', type=_tags_arg,
      help='comma separated list of tags. The first tag is the "primary" tag')
    cmd.add_argument(
      'clue', type=str,
      help='the short string by which to identify this cheatsheet entry')
    cmd.add_argument(
      'answer', type=str,
      help='the full explanation of this entry. Can be as long as required')

  def add(self, args):
    # Load cheatsheet, add an entry, then save the results
    cs = sjb.cs.fileio.load_cheatsheet(list=args.list, listpath=args.listpath)
    entry = sjb.cs.classes.Entry(
      args.clue, args.answer, primary=args.tags[0], tags=args.tags[1])

    # Check if any tag or the primary is new and prompt user before continuing.
    new_elts = cs.get_new_tags(args.tags[0], args.tags[1])
    if new_elts and args.prompt is not FORCE:
      question = (
        'The following tags are not present in the database: ' + \
        ', '.join(new_elts) + \
        '\nAre you sure you want to add this element? ')
      cont = sjb.common.misc.prompt_yes_no(question, default=True)
      if not cont:
        exit(0)

    cs.add_item(entry)
    sjb.cs.fileio.save_cheatsheet(cs, list=args.list, listpath=args.listpath)

    # Print the results.
    sjb.cs.display.display_entry(entry, format_style=args.style)

  def _set_args_info(self, cmds):
    cmd = cmds.add_parser(
      'info', help=CMDS['info'][0], description=CMDS['info'][1])
    cmd.set_defaults(run=self.info)
    _add_arg_list(cmd)

  def info(self, args):
    cs = sjb.cs.fileio.load_cheatsheet(list=args.list, listpath=args.listpath)

    primary_map = cs.primary_map
    tag_set = cs.tag_set
    entries = cs.items
    primary_count = {key: len(primary_map[key]) for key in primary_map}
    sorted_primary = sorted(
      primary_count.items(), key=operator.itemgetter(1), reverse=True)

    print('Cheat sheet information:')
    print('  %-25s %s' % ('Number of entries', len(entries)))
    print('  %-25s %s' % ('Number primary tags', len(primary_map.keys())))
    print('  %-25s %s' % ('Number of tags', len(tag_set)))
    print('  %-25s %s' % ('Tag list', ', '.join(tag_set)))
    print('%-27s %s' % ('Primary key', 'Count'))
    for key, count in sorted_primary:
      print('  %-25s %d' % (key, count))

  def _set_args_lists(self, cmds):
    cmd = cmds.add_parser(
      'lists', help=CMDS['lists'][0], description=CMDS['lists'][1])
    cmd.set_defaults(run=self.lists)

  def lists(self, args):
    lists = sjb.cs.fileio.get_all_list_files()
    print('Cheatsheets: ' + ', '.join(lists))

  def _set_args_show(self, cmds):
    cmd = cmds.add_parser(
      'show', help=CMDS['show'][0], description=CMDS['show'][1])
    cmd.set_defaults(run=self.show)
    cmd.add_argument(
      '--tags', type=_set_arg,
      help='only show entries which match this comma separated list of tags')

    g = cmd.add_mutually_exclusive_group()
    g.add_argument(
      '--or', dest='andor', action='store_const',
      const=sjb.cs.classes.SEARCH_OR,
      default=sjb.cs.classes.SEARCH_OR,
      help='show entries which match ANY of the given conditions')
    g.add_argument(
      '--and', dest='andor', action='store_const',
      const=sjb.cs.classes.SEARCH_AND,
      default=sjb.cs.classes.SEARCH_OR,
      help='only show entries which match ALL of the given conditions')
    _add_arg_list(cmd)
    _add_arg_style(cmd)

  def show(self, args):
    # Special handling. If no format style is given and the user gave some
    # filter, then we display the simple style. e.g. if I type show 'bash', I
    # dont want to see 'bash' in every entry.
    if not args.style and args.tags:
      args.style = sjb.cs.display.FORMAT_STYLE_SIMPLE

    # Load cheat sheet, find matching entries, and print
    cs = sjb.cs.fileio.load_cheatsheet(list=args.list, listpath=args.listpath)
    matcher = sjb.cs.classes.EntryMatcherTags(args.tags, args.andor)
    entries = cs.query_items(matcher)
    if entries:
      sjb.cs.display.display_entries(entries, format_style=args.style)
    else:
      print('No entries found')

  def _set_args_remove(self, cmds):
    cmd = cmds.add_parser(
      'remove', help=CMDS['remove'][0], description=CMDS['remove'][1])
    cmd.set_defaults(run=self.remove)
    _add_arg_oid(cmd, help='ID of the item you wish to delete')
    _add_arg_force(cmd, verb='removing the cheatsheet item', default=PROMPT)
    _add_arg_list(cmd)
    _add_arg_style(cmd)

  def remove(self, args):
    # Load cheat sheet
    cs = sjb.cs.fileio.load_cheatsheet(list=args.list, listpath=args.listpath)

    # If not in force mode, ask user before proceeding.
    entry = cs.get_item(args.oid)
    if args.prompt is not FORCE:
      question = (
        'The entry given by oid '+str(args.oid)+' is:\n' + \
        sjb.cs.display.entry_repr(entry, format_style=args.style) + \
        '\nAre you sure you want to delete it? ')
      cont = sjb.common.misc.prompt_yes_no(question, default=False)
      if not cont:
        exit(0)

    removed = cs.remove_item(args.oid)
    sjb.cs.fileio.save_cheatsheet(cs, list=args.list, listpath=args.listpath)

    # Print the results only on force mode (otherwise user just saw item).
    if args.prompt is not FORCE:
      print('Removed entry:')
      sjb.cs.display.display_entry(removed, format_style=args.style)

  def _set_args_update(self, cmds):
    cmd = cmds.add_parser(
      'update', help=CMDS['update'][0], description=CMDS['update'][1])
    cmd.set_defaults(run=self.update)
    _add_arg_oid(cmd, help='ID of the item you wish to update')
    cmd.add_argument(
      '--tags', metavar='tags', type=_tags_arg,
      help='comma separated list of tags. The first tag is the "primary" tag')
    cmd.add_argument(
      '--clue', metavar='clue', type=str,
      help='the short string by which to identify this cheatsheet entry')
    cmd.add_argument(
      '--answer', metavar='answer', type=str,
      help='the full explanation of this entry. Can be as long as required')
    _add_arg_force(cmd, verb='updating the item', default=FORCE)
    _add_arg_list(cmd)
    _add_arg_style(cmd)

  def update(self, args):
    # Load cheat sheet
    cs = sjb.cs.fileio.load_cheatsheet(list=args.list, listpath=args.listpath)

    # Prompt user before continuing
    item = cs.get_item(args.oid)
    if args.prompt is not FORCE:
      question = (
        'The item given by oid '+str(args.oid)+' is:\n' + \
        sjb.cs.display.entry_repr(item, format_style=args.style) + \
        '\nAre you sure you want to continue? ')
      cont = sjb.common.misc.prompt_yes_no(question, default=True)
      if not cont:
        exit(0)

    # Update entry in local CheatSheet object.
    updated = cs.update_item(
      args.oid, clue=args.clue, answer=args.answer,
      primary=args.tags[0] if args.tags else None,
      tags=args.tags[1] if args.tags else None)
    # Save CheatSheet object to file.
    sjb.cs.fileio.save_cheatsheet(cs, list=args.list, listpath=args.listpath)

    # Print the results.
    sjb.cs.display.display_entry(updated, format_style=args.style)


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
