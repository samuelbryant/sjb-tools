"""Module responsible for reading/writing todo list json to file."""
import os
import json
import warnings
import sjb.common.config
import sjb.td.classes

_SUITE = 'sjb'
_APP = 'todo'
_DEFAULT_LIST_FILE = 'todo'
_LIST_FILE_EXTENSION = '.json'


def initialize_environment():
  """Checks that necessary user dirs exist and creates them if not.

  Raises:
    FileExistsError: if one of the required files already exists but it is of
      the wrong type (e.g. its a file instead of a directory).
    PermissionError: if program lacks permissions to create a needed directory.
    Exception: any other issue in setting up environment.
  """
  sjb.common.config.initialize_environment(_APP, suite_name=_SUITE)


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

  # TODO: Temporary replacement of poor validation-in-encoding code
  for item in todo_list.items:
    item.validate()

  json_file = open(fname, 'w')
  json_file.write(json.dumps(todo_list.to_dict(), indent=2))
  json_file.close()

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

  # If file doesn't exist, return a new blank cheat sheet.
  if not os.path.isfile(fname):
    # TODO: Improve this
    warnings.warn('No todo list file found', UserWarning)
    return sjb.td.classes.TodoList(source_fname=fname)

  json_file = open(fname)
  json_dict = json.load(json_file)
  json_file.close()
  return sjb.td.classes.TodoList.from_dict(json_dict, fname)
