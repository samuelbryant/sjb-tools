"""Module responsible for reading/writing todo list json to file."""
from __future__ import (absolute_import, division,
                        print_function, unicode_literals)
from builtins import *

import os
import json
import warnings
import sjb.common.config
import sjb.td.classes

_SUITE = 'sjb'
_APP = 'todo'
_DEFAULT_LIST_FILE = 'todo'
_LIST_FILE_EXTENSION = '.json'

def _get_default_list_file(list=None):
  """Gets the full pathname of the todo file named list.

  Args:
    list: str a short name giving the local list file name, e.g. 'chores'. This
      should not contain a file extension.
  """
  list = list or _DEFAULT_LIST_FILE
  return os.path.join(
    sjb.common.config.get_user_app_data_dir(_APP, suite_name=_SUITE),
    list + _LIST_FILE_EXTENSION)

def get_all_list_files():
  """Returns a list of all the todo file lists stored in the data directory.

  Returns:
    List of the local file names (without the extensions) for all of the todo
      lists stored in the data directory.
  """
  dir = sjb.common.config.get_user_app_data_dir(_APP, suite_name=_SUITE)
  files = os.listdir(dir)
  matching = []
  for f in files:
    if not os.path.isfile(os.path.join(dir, f)):
      continue
    # Check that it has correct extension.
    if not f.endswith(_LIST_FILE_EXTENSION):
      continue
    matching.append(f[0:(len(f)-len(_LIST_FILE_EXTENSION))])
  return matching

def _encode_todo(todo):
  todo.validate()
  return {
    'oid': todo.oid,
    'tags': sorted(list(todo.tags)),
    'priority': todo.priority,
    'text': todo.text,
    'finished': todo.finished,
    'created_date': todo.created_date,
    'finished_date': todo.finished_date,
  }

def _decode_todo(json_object):
  return sjb.td.classes.Todo(
    text=json_object['text'],
    tags=set(json_object['tags']),
    priority=json_object['priority'],
    finished=json_object['finished'],
    created_date=json_object['created_date'],
    finished_date=json_object['finished_date'],
    oid=json_object['oid'])

def _encode_todo_list(todo_list):
  return {
    'todo_list': {
      'modified_date': todo_list.modified_date,
      'todos': [_encode_todo(todo) for todo in todo_list.items]
    }
  }

def save_todo_list(todo_list, list=None, listpath=None):
  """Saves a todo list to a json file.

  Arguments:
    list: str An optional local list name to save the todo list as. The
      resulting file is saved in the default application directory with the
      local file name 'list.json'. This argument is mututally exclusive with
      listpath.
    listpath: str An optional full path name to save the todo list to.
      This argument is mututally exclusive with listpath.

  Raises:
    Exception: If both list and listpath are given.
  """
  if list and listpath:
    raise Exception(
      'Cannot set both list and listpath args (this should never happen')

  # First check list/listpath arguments, then try the file that the todo list
  # was read from. If none of those exist, use the default list file.
  # TODO: reconsider this logic. Is this really the best behavior?
  if list:
    fname = _get_default_list_file(list=list)
  else:
    fname = listpath or todo_list.source_filename or _get_default_list_file()


  ob_js = _encode_todo_list(todo_list)
  json_file = open(fname, "w")
  json_file.write(json.dumps(ob_js, indent=2))

def load_todo_list(list=None, listpath=None):
  """Loads a todo list from a json file.

  Arguments:
    list: str An optional local list name to read the todo list from. This
      looks for a file in the default application directory with the local
      file name 'list.json'. This argument is mututally exclusive with
      listpath.
    listpath: str An optional full path name to read the todo list from.
      This argument is mututally exclusive with listpath.

  Returns:
    TodoList: object with contents given by the loaded file.

  Raises:
    Exception: If both list and listpath are given.
  """
  if list is not None and listpath is not None:
    raise Exception(
      'Cannot set both list and listpath args (this should never happen.)')

  fname = listpath or _get_default_list_file(list=list)

  # Attempt to open
  if not os.path.isfile(fname):
    # TODO: Improve this
    warnings.warn('No todo list file found', UserWarning)
    return sjb.td.classes.TodoList(source_fname=fname)

  json_file = open(fname)
  obj = json.load(json_file)['todo_list']
  modified_date = obj['modified_date'] if 'modified_date' in obj else None

  # Create new blank todo list
  todo_list = sjb.td.classes.TodoList(
    modified_date=modified_date, source_fname=fname)

  # Add todos to todo list
  for todo_json in obj['todos']:
    todo = _decode_todo(todo_json)
    todo_list.add_item(todo, initial_load=True)

  return todo_list
