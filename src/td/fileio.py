"""Module responsible for reading/writing todo list json to file."""
import os
import json
import warnings
import td.classes


def _encode_todo(todo):
  todo.validate()
  return {
    'oid': todo.oid,
    'tags': list(todo.tags),
    'priority': todo.priority,
    'text': todo.text,
    'finished': todo.finished,
    'created_date': todo.created_date,
    'finished_date': todo.finished_date,
  }

def _decode_todo(json_object):
  return td.classes.Todo(
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
      'todos': [_encode_todo(todo) for todo in todo_list.todos]
    }
  }

def _get_default_todo_file():
  if 'XDG_DATA_HOME' in os.environ:
    return os.environ['XDG_DATA_HOME']+'/'+'sjb_todo/todo.json'
  return os.environ['HOME']+'/.local/share/sjb_todo/todo.json'

def save_todo_list(todo_list, fname=None):
  """Saves a todo list to a json file."""
  ob_js = _encode_todo_list(todo_list)

  fname = fname or todo_list.src_fname or _get_default_todo_file()
  json_file = open(fname, "w")
  json_file.write(json.dumps(ob_js, indent=2))

def load_todo_list(fname=None):
  """Loads a todo list from a json file.

  Arguments:
    fname: str an optional file name to read the todo list from.

  Returns:
    TodoList: object with contents given by the loaded file.
  """
  fname = fname or _get_default_todo_file()

  # Attempt to open
  if not os.path.isfile(fname):
    warnings.warn('No todo list file found', UserWarning)
    return td.classes.TodoList(src_fname=fname)

  json_file = open(fname)
  obj = json.load(json_file)['todo_list']
  modified_date = obj['modified_date'] if 'modified_date' in obj else None

  # Create new blank todo list
  todo_list = td.classes.TodoList(modified_date=modified_date, src_fname=fname)

  # Add todos to todo list
  for todo_json in obj['todos']:
    todo = _decode_todo(todo_json)
    todo_list.add_todo(todo, initial_load=True)

  return todo_list
