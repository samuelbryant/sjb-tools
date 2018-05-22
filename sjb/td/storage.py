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

class NoListFileError(Exception):
  """Raised when user tries to load a non-existent list."""
  pass

class IOError(Exception):
  """Raised on generic problem with writing things to/from OS."""
  pass

class Storage(object):
  """Class encapsulating environment information like where to write stuff."""

  def __init__(self, listname=None):
    self._listname = listname or _DEFAULT_LIST_FILE

  def _get_list_file(self):
    return os.path.join(
      sjb.common.config.get_user_app_data_dir(_APP, suite_name=_SUITE),
      '%s%s' % (self._listname, _LIST_FILE_EXTENSION))

  def get_list_name(self):
    """Returns the short name of the list for this storage object."""
    return self._listname

  @staticmethod
  def get_all_list_files():
    """Returns a list of all the available list files in the data directory."""
    d = sjb.common.config.get_user_app_data_dir(_APP, suite_name=_SUITE)
    files = os.listdir(d)
    matching = []
    for f in files:
      if not os.path.isfile(os.path.join(d, f)):
        continue
      # check that it has correct extension.
      if not f.endswith(_LIST_FILE_EXTENSION):
        continue
      matching.append(f[0:(len(f)-len(_LIST_FILE_EXTENSION))])
    return matching

  def save_list(self, todo_list):
    fname = self._get_list_file()

    # create parent directory as needed
    if not os.path.isdir(os.path.dirname(fname)):
      os.makedirs(os.path.dirname(fname))

    # TODO: Temporary replacement of poor validation-in-encoding code
    for item in todo_list.items:
      item.validate()

    json_file = open(fname, 'w')
    json_file.write(json.dumps(todo_list.to_dict(), indent=2))
    json_file.close()

  def load_list(self):
    """Loads the todo list.

    The name of the todo list is specified at initialization time.

    Returns:
      TodoList: object with contents given by the loaded file.

    Raises:
      NoListFileError: If the file does not exist.
      IOError: If a file-like object exists but is wrong type (i.e. a dir).
    """
    fname = self._get_list_file()

    if not os.path.isfile(fname):
      if os.path.exists(fname):
        raise IOError('list file exists but is of wrong filetype')
      raise NoListFileError()

    json_file = open(fname, 'r')
    json_dict = json.load(json_file)
    json_file.close()
    return sjb.td.classes.TodoList.from_dict(json_dict, fname)
