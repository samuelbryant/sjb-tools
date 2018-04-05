import time


class Todo:

  def __init__(self, text, tags={}, finished=False, created_date=None, finished_date=None, id=None):
    self.text = text
    self.tags = set(tags)
    self.finished = finished
    self.created_date = created_date
    self.finished_date = finished_date
    self.id = id

class TodoList:

  def __init__(self, modified_date=None, src_fname=None):
    self.src_fname = src_fname
    self.modified = False
    self.modified_date = modified_date
    self.last_todo_id = 0
    
    # Maps holding cheat sheet meta data.
    self.todos = []
    self.tag_set = set()
    self.id_set = set()

  def get_todo(self, id):
    """Returns todo with the given id.

    Returns:
      Todo: the todo with the matching ID.

    Raises:
      InvalidIDError: If no todo has a matching ID.
    """
    for t in self.todos:
      if id is t.id:
        return t
    raise InvalidIDError(
      'TodoList.get_todo', 'non-existent todo id '+str(id))

  def get_todos(self):
    return self.todos

  def add_todo(self, todo, initial_load=False):
    """Adds a todo to this todo list.

    Args:
      todo: The Todo object to add. Several attributes should only be set if 
        this object is loaded initially from a file: id, completed_date, 
        creation_date, finished 
      initial_load: Indicates that this todo object is loaded from a todo and
        thus is not a new addition to the todo list.

    Raises:
      ProgrammingError: If not initial_load but the todo object already has an
        ID.
      ProgrammingError: If initial_load but the todo object has no ID.
    """

    # Make sure any 'init load' todo already has an id
    if initial_load and not todo.id:
      raise ProgrammingError(
        'TodoList.add_todo', 'missing ID on initial_load Todo')

    if not initial_load:
      # Make sure any new todo does not have any protected field set.
      if todo.id or todo.created_date or todo.finished_date:
        raise ProgrammingError(
          'Todo.add_todo', 'Added Todo already has some protected fields set')
      # Set the id, creation date,
      todo.id = self.last_todo_id + 1
      self.last_todo_id += 1
      self.created_date = time.time()

      # Mark todo list as modified
      self._mark_modified()

    # Actually add the element.
    self.todos.append(todo)
    self._update_object_maps(todo)

  def _update_object_maps(self, todo):
    """Updates meta object maps like tag_set to reflect contents of todo.

    Raises:
      IllegalStateError: If a duplicate ID is encountered.
    """
    
    # Sanity check: Make sure there are no duplicate IDs.
    if todo.id in self.id_set:
      raise IllegalStateError(
        'TodoList._update_object_maps', 'duplicate ID found.')
    self.id_set.add(todo.id)


    for tag in todo.tags:
      self.tag_set.add(tag)

    # Set last_id to the highest ID.
    if todo.id > self.last_todo_id:
      self.last_todo_id = todo.id

  def _recompute_object_maps(self):
    """Recomputes all meta object maps like tag_set, etc.

    This should be used after making a non-trivial change to the list like modifying an elements tags or removing an element.
    """
    self.tag_set = set()
    self.id_set = set()
    self.last_todo_id = 0

    for todo in self.todos:
      self._update_object_maps(todo)
    
  def _mark_modified(self):
    """Marks the  TodoList as modified at the given time.

    This uses the current time if no timestamp is specified.
    """
    self.modified=True
    self.modified_date=time.time()


class Error(Exception):
  """Base class for exceptions for this program."""
  pass


class InvalidIDError(Error):
  """Exception raised when a specified todo ID does not exist."""

  def __init__(self, method, msg):
    self.message = '%s in method %s\n\tMSG: %s' % \
      ('InvalidIDError', method, msg)
    

class ProgrammingError(Error):
  """Exception used to signal something that should never happen.

  This indicates that there is an error in my code somewhere."""
  def __init__(self, method, msg):
    self.message = '%s in method %s\n\tMSG: %s' % \
      ('ProgrammingError', method, msg)


class IllegalStateError(Error):
  """Exception used to signal something is wrong, but its not clear why."""
  def __init__(self, method, msg):
    self.message = '%s in method %s\n\tMSG: %s' % \
      ('IllegalStateError', method, msg)
