"""Module containing all core class definitions for this program."""
import time
import enum


def _default_if_none(value, default):
  """Returns value if it is not None, otherwise default."""
  if value is None:
    return default
  return value


class PriorityEnum(enum.Enum):
  """Enum representing the priority of a todo item."""
  DEFAULT = 1
  URGENT = 2
  LONG_TERM = 3


class Todo(object):
  """Simple class representing a todo item."""

  def __init__(
      self, text, priority=None, tags=None, finished=None, created_date=None,
      finished_date=None, oid=None):
    # Values that should be set at construction time
    self.text = text
    self.priority = _default_if_none(priority, PriorityEnum.DEFAULT.value)
    self.tags = _default_if_none(tags, set())

    # Values that should only be set when reading from file
    self.finished = finished
    self.created_date = created_date
    self.finished_date = finished_date
    self.oid = oid

    # Validate todo: maybe should not be called from constructor.
    self.validate()

  def matches(self, priority=None, tags=None, finished=None):
    """Returns true only if todo matches ALL conditions."""
    if priority is not None and priority is not self.priority:
      return False
    for tag in (tags or []):
      if not tag in self.tags:
        return False
    if finished is not None and self.finished is not finished:
      return False
    return True

  def validate(self):
    """Validates that the values of this item are sensible.

    This method should be called twice: The first time at the end of the
    initialization code to make sure the user is not misusing the constructor.
    The second time should be before saving to a database to make sure that
    manipulations made to this item after initialization were valid.

    These two possible reasons for calling correspond to two different states:
      1 If the oid is set, then this TODO is assumed to be loaded from a todo
        list. In this is the case, created_date and finished should also be set
      2 If the oid is not set, then finished, created_date, finished_date should
        all be None.

    Raises:
      InvalidTodoError: If validation fails
    """
    if not self.text or not isinstance(self.text, str):
      raise InvalidTodoError(
        'Bad todo text: '+str(self.text))
    if not isinstance(self.tags, set):
      raise InvalidTodoError('Bad tags (not a set): '+str(self.tags))
    if not self.priority in [e.value for e in PriorityEnum]:
      raise InvalidTodoError('Bad priority: '+str(self.priority))

    if self.oid is not None:
      if not isinstance(self.oid, int):
        raise InvalidTodoError('Non int oid: '+str(self.oid))
      if not isinstance(self.finished, bool):
        raise InvalidTodoError('Non bool finished state: '+str(self.finished))
      # TODO: More thorough date validation. (also below)
      if not isinstance(self.created_date, float):
        raise InvalidTodoError(
          'Non float created_date: '+str(self.created_date))
      # Finished items must have finished dates.
      if self.finished and not isinstance(self.finished_date, float):
        raise InvalidTodoError('Todo finished but no finished_date')
      # Non-finished items must not have finished dates.
      if not self.finished and self.finished_date is not None:
        raise InvalidTodoError('Non finished todo has finished_date')
    if self.oid is None:
      if self.finished is not None:
        raise InvalidTodoError(
          'No oid set, but has not none finished: '+str(self.finished))
      if self.created_date is not None:
        raise InvalidTodoError(
          'No oid set, but has created_date: '+str(self.created_date))
      if self.finished_date is not None:
        raise InvalidTodoError(
          'No oid set, but has finished_date: '+str(self.finished_date))


class TodoList(object):
  """Class that represents a list of todo entries.

  It is typically read from a file at the start of a session and written to a
  file at the end of a session. It also has methods for updating entries and
  querying subsets of the full list.
  """

  def __init__(self, modified_date=None, src_fname=None):
    self.src_fname = src_fname
    self.modified = False
    self.modified_date = modified_date
    self.last_todo_oid = 0

    # Maps holding cheat sheet meta data.
    self.todos = []
    self.tag_set = set()
    self.oid_set = set()

  def _set_next_todo_oid(self):
    """Returns a suitable oid for a new item and increments oid state."""
    self.last_todo_oid += 1
    return self.last_todo_oid

  def get_todo_index(self, oid):
    """Returns the index of the todo with the given oid.

    Returns:
      int: the index in self.todos of the todo with the matching oid.

    Raises:
      InvalidIDError: If no todo has a matching oid.
    """
    for i in range(len(self.todos)):
      if oid is self.todos[i].oid:
        return i
    raise InvalidIDError(
      'TodoList.get_todo_index', 'non-existent todo oid '+str(oid))

  def get_todo(self, oid):
    """Returns todo with the given oid.

    Returns:
      Todo: the todo with the matching oid.

    Raises:
      InvalidIDError: If no todo has a matching ID.
    """
    for todo in self.todos:
      if oid is todo.oid:
        return todo
    raise InvalidIDError(
      'TodoList.get_todo', 'non-existent todo oid '+str(oid))

  def get_todos(self, priority=None, tags=None, finished=None):
    """Gets a list of todos that match the given conditions.

    Currently the method is configured to use AND logic (all conditions must
    be satisfied.)

    Arguments:
      priority: If not None, will only return items matching the given
        priority.
      tags: If not None, will only return items matching all of the given tags.
      finished: If not None, will only return items with the given finished
        status.

    Returns:
      list: List of todo items matching criteria.
    """
    return(
      [todo for todo in self.todos if todo.matches(priority, tags, finished)])

  def get_new_tags(self, tags):
    """Computes set of tags that are not in database.

    Arguments:
      tags: set(str) of tags to check if present in tag set.

    Returns:
      Set: of all tags that are new to database.
    """
    return tags - self.tag_set

  def add_todo(self, todo, initial_load=False):
    """Adds a todo to this todo list.

    Args:
      todo: The Todo object to add. Several attributes should only be set if
        this object is loaded initially from a file: oid, completed_date,
        creation_date, finished
      initial_load: Indicates that this todo object is loaded from a todo and
        thus is not a new addition to the todo list.

    Raises:
      ProgrammingError: If not initial_load but the todo object already has an
        oid.
      ProgrammingError: If initial_load but the todo object has no oid.
    """

    # Make sure any 'init load' todo already has an oid
    if initial_load and not todo.oid:
      raise ProgrammingError('TodoList.add_todo', 'Old Todo missing oid!')
    # Make sure any new todo does not have an oid
    if not initial_load and todo.oid:
      raise ProgrammingError('Todo.add_todo', 'New Todo already has oid')

    if not initial_load:
      todo.oid = self._set_next_todo_oid()
      todo.created_date = time.time()
      todo.finished = False

      # Mark todo list as modified
      self._mark_modified()

    # Actually add the element.
    self.todos.append(todo)
    self._update_object_maps(todo)

  def complete_todo(self, oid):
    """Marks the todo with the specified oid as completed.

    Returns:
      Todo: The completed todo object.

    Raises:
      InvalidIDError: If no todo has a matching oid.
      IllegalStateError: If the todo is already completed.
    """
    todo = self.get_todo(oid)
    if todo.finished:
      raise IllegalStateError(
        'TodoList.complete_todo', 'specified todo was already completed')
    todo.finished = True
    todo.finished_date = time.time()
    self._mark_modified()
    ## TODO: Not needed yet, but may be needed if maps are completion aware.
    # self._recompute_object_maps()
    return todo

  def remove_todo(self, oid):
    """Removes the todo item with the specified oid and updates meta data.

    Returns:
      Todo: The removed Todo object.

    Raises:
      InvalidIDError: If no todo has a matching oid.
    """
    index = self.get_todo_index(oid)
    removed = self.todos.pop(index)
    # Mark as modified and recompute meta maps.
    self._mark_modified()
    self._recompute_object_maps()
    return removed

  def update_todo(self, oid, text=None, priority=None, tags=None):
    """Updates todo item given by oid and returns result.

    Only arguments that are not None will be updated. If no todo is found at
    that oid, an Error is raised. The meta objects are updated to reflect the
    new contents of the todo item.

    Returns:
      Todo: The newly updated todo object.

    Raises:
      InvalidIDError: If no todo has a matching oid.
    """
    todo = self.get_todo(oid)

    if text is not None or priority is not None or tags is not None:
      todo.text = _default_if_none(text, todo.text)
      todo.priority = _default_if_none(priority, todo.priority)
      todo.tags = _default_if_none(tags, todo.tags)
      self._mark_modified()
      self._recompute_object_maps()

    return todo

  def _update_object_maps(self, todo):
    """Updates meta object maps like tag_set to reflect contents of todo.

    Raises:
      IllegalStateError: If a duplicate oid is encountered.
    """

    # Sanity check: Make sure there are no duplicate oids.
    if todo.oid in self.oid_set:
      raise IllegalStateError(
        'TodoList._update_object_maps', 'duplicate oid found.')
    self.oid_set.add(todo.oid)

    for tag in todo.tags:
      self.tag_set.add(tag)

    # Set last_oid to the highest oid.
    if todo.oid > self.last_todo_oid:
      self.last_todo_oid = todo.oid

  def _recompute_object_maps(self):
    """Recomputes all meta object maps like tag_set, etc.

    This should be used after making a non-trivial change to the list like
    modifying an elements tags or removing an element.
    """
    self.tag_set = set()
    self.oid_set = set()
    self.last_todo_oid = 0

    for todo in self.todos:
      self._update_object_maps(todo)

  def _mark_modified(self):
    """Marks the  TodoList as modified at the given time.

    This uses the current time if no timestamp is specified.
    """
    self.modified = True
    self.modified_date = time.time()


class Error(Exception):
  """Base class for exceptions for this program."""
  pass


class InvalidIDError(Error):
  """Exception raised when a specified todo oid does not exist."""

  def __init__(self, method, msg):
    super(InvalidIDError, Error).__init__()
    self.message = '%s in method %s\n\tMSG: %s' % \
      ('InvalidIDError', method, msg)


class InvalidTodoError(Error):
  """Exception raised when todo validation fails.

  This most likely indicates an issue with either encoding, decoding, or
  reading a todo list made by a prior version.
  """
  def __init__(self, msg):
    super(InvalidTodoError, Error).__init__()
    self.message = '%s: %s' % ('InvalidTodoError', msg)


class ProgrammingError(Error):
  """Exception used to signal something that should never happen.

  This indicates that there is an error in my code somewhere."""
  def __init__(self, method, msg):
    super(ProgrammingError, Error).__init__()
    self.message = '%s in method %s\n\tMSG: %s' % \
      ('ProgrammingError', method, msg)


class IllegalStateError(Error):
  """Exception used to signal something is wrong, but its not clear why."""
  def __init__(self, method, msg):
    super(IllegalStateError, Error).__init__()
    self.message = '%s in method %s\n\tMSG: %s' % \
      ('IllegalStateError', method, msg)
