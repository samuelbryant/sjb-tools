import time, enum


def _default_if_none(value, default):
  """Returns value if it is not None, otherwise default."""
  if value is None:
    return(default)
  else:
    return(value)


class PriorityEnum(enum.Enum):
  DEFAULT = 1
  URGENT = 2
  LONG_TERM = 3


class Todo:

  def __init__(
    self, text, priority=None, tags=None, finished=None, created_date=None, finished_date=None, id=None):
    # Values that should be set at construction time
    self.text = text
    self.priority = _default_if_none(priority, PriorityEnum.DEFAULT.value)
    self.tags = _default_if_none(tags, set())

    # Values that should only be set when reading from file
    self.finished = finished
    self.created_date = created_date
    self.finished_date = finished_date
    self.id = id

    # Validate todo: maybe should not be called from constructor.
    self.validate()

  def validate(self):
    """Validates that the values of this item are sensible.

    This method should be called twice: The first time at the end of the
    initialization code to make sure the user is not misusing the constructor.
    The second time should be before saving to a database to make sure that
    manipulations made to this item after initialization were valid.
    
    These two possible reasons for calling correspond to two different states: 
      1 If the id is set, then this TODO is assumed to be loaded from a todo
        list. In this is the case, created_date and finished should also be set
      2 If the id is not set, then finished, created_date, finished_date should
        all be None.

    Raises:
      InvalidTodoError: If validation fails
    """
    if not isinstance(self.text, str) or str == '':
      raise InvalidTodoError('Bad todo text: '+str(text))
    if not isinstance(self.tags, set):
      raise InvalidTodoError('Bad tags (not a set): '+str(self.tags))
    if not self.priority in [e.value for e in PriorityEnum]:
      raise InvalidTodoError('Bad priority: '+str(self.priority))

    if self.id is not None:
      if not isinstance(self.id, int):
        raise InvalidTodoError('Non int id: '+str(self.id))
      if not isinstance(self.finished, bool):
        raise InvalidTodoError('Non bool finished state: '+str(self.finished))
      # TODO: More thorough date validation. (also below)
      if not isinstance(self.created_date, float):
        raise InvalidTodoError('Non float created_date: '+str(self.created_date))
      # Finished items must have finished dates.
      if self.finished and not isinstance(self.finished_date, float):
          raise InvalidTodoError('Todo finished but no finished_date')
      # Non-finished items must not have finished dates.
      if not self.finished and self.finished_date is not None:
        raise InvalidTodoError('Non finished todo has finished_date')
    if self.id is None:
      if self.finished is not None:
        raise InvalidTodoError('No id set, but has not none finished: '+str(self.finished))
      if self.created_date is not None:
        raise InvalidTodoError('No id set, but has created_date: '+str(self.created_date))
      if self.finished_date is not None:
        raise InvalidTodoError('No id set, but has finished_date: '+str(self.finished_date))


class TodoList:
  """Class that represents a list of todo entries. 

  It is typically read from a file at the start of a session and written to a
  file at the end of a session. It also has methods for updating entries and
  querying subsets of the full list.
  """

  def __init__(self, modified_date=None, src_fname=None):
    self.src_fname = src_fname
    self.modified = False
    self.modified_date = modified_date
    self.last_todo_id = 0
    
    # Maps holding cheat sheet meta data.
    self.todos = []
    self.tag_set = set()
    self.id_set = set()

  def _set_next_todo_id(self):
    """Returns a suitable ID for a new item and increments ID state."""
    self.last_todo_id += 1
    return(self.last_todo_id)

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
      raise ProgrammingError('TodoList.add_todo', 'Old Todo missing ID!')
    # Make sure any new todo does not have an id
    if not initial_load and todo.id:
      raise ProgrammingError('Todo.add_todo', 'New Todo already has ID')
    
    if not initial_load:
      todo.id = self._set_next_todo_id()
      todo.created_date = time.time()
      todo.finished = False

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


class InvalidTodoError(Error):
  """Exception raised when todo validation fails.

  This most likely indicates an issue with either encoding, decoding, or 
  reading a todo list made by a prior version.
  """
  def __init__(self, msg):
    self.message = '%s: %s' % \
      ('InvalidTodoError', msg)
    

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
