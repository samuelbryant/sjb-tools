"""Module containing all core class definitions for this program."""
from __future__ import (absolute_import, division,
                        print_function, unicode_literals)
from builtins import *

import time
import copy
import enum
import sjb.common.base


class PriorityEnum(enum.Enum):
  """Enum representing the priority of a todo item."""
  URGENT = 1
  DEFAULT = 2
  LONG_TERM = 3


class TodoMatcher(sjb.common.base.ItemMatcher):
  """Class that matches todo items using some set of conditions."""

  def __init__(self, tags=None, priority=None, finished=None):
    """Initializes an object that matches Todo Items.

    Args:
      tags: If not None, then this checks if Todo objects have ALL tags.
      priority: If not None, this checks if Todo objects have same priority.
      finished: If not None, this checks if Todo objects have same finished.
    """
    self.tags = tags
    self.priority = priority
    self.finished = finished

  def matches(self, item):
    """Returns true only if todo matches ALL conditions."""
    if self.priority is not None and item.priority is not self.priority:
      return False
    for tag in (self.tags or []):
      if not tag in item.tags:
        return False
    if self.finished is not None and item.finished is not self.finished:
      return False
    return True


class Todo(sjb.common.base.Item):
  """Simple class representing a todo item."""

  def __init__(
      self, text, priority=None, tags=None, finished=None, created_date=None,
      finished_date=None, oid=None):
    super().__init__(oid)
    # Values that should be set at construction time
    self.text = text
    if priority is not None:
      self.priority = priority
    else:
      self.priority = PriorityEnum.DEFAULT.value
    self.tags = tags if tags is not None else set()

    # Values that should only be set when reading from file
    self.finished = finished
    self.created_date = created_date
    self.finished_date = finished_date

    # Validate todo: maybe should not be called from constructor.
    self.validate()

  def __eq__(self, other):
    """Returns true if self and other have identical fields."""
    if not super().__eq__(other): return False
    if self.text != other.text: return False
    if self.priority != other.priority: return False
    if self.tags != other.tags: return False
    if self.finished != other.finished: return False
    if self.created_date != other.created_date: return False
    if self.finished_date != other.finished_date: return False
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
      2 If the oid is not set, then finished, created_date, finished_date
        should all be None.

    Raises:
      sjb.common.base.ValidationError: If validation fails
    """
    super().validate()
    if not self.text or not isinstance(self.text, str):
      raise sjb.common.base.ValidationError('Bad todo text: '+str(self.text))
    if not isinstance(self.tags, set):
      raise sjb.common.base.ValidationError('Bad tags: '+str(self.tags))
    if self.priority not in [e.value for e in PriorityEnum]:
      raise sjb.common.base.ValidationError('Bad priority: '+str(self.priority))

    # If it has an ID, it should have other values as well.
    if self.oid is not None:
      if not isinstance(self.oid, int):
        raise sjb.common.base.ValidationError('Non int oid: '+str(self.oid))
      if not isinstance(self.finished, bool):
        raise sjb.common.base.ValidationError(
          'Non bool finished state: '+str(self.finished))
      # TODO: More thorough date validation. (also below)
      if not isinstance(self.created_date, float):
        raise sjb.common.base.ValidationError(
          'Non float created_date: '+str(self.created_date))
      # Finished items must have finished dates.
      if self.finished and not isinstance(self.finished_date, float):
        raise sjb.common.base.ValidationError(
          'Todo finished but no finished_date')
      # Non-finished items must not have finished dates.
      if not self.finished and self.finished_date is not None:
        raise sjb.common.base.ValidationError(
          'Non finished todo has finished_date')
    if self.oid is None:
      if self.finished is not None:
        raise sjb.common.base.ValidationError(
          'No oid set, but has not none finished: '+str(self.finished))
      if self.created_date is not None:
        raise sjb.common.base.ValidationError(
          'No oid set, but has created_date: '+str(self.created_date))
      if self.finished_date is not None:
        raise sjb.common.base.ValidationError(
          'No oid set, but has finished_date: '+str(self.finished_date))


class TodoList(sjb.common.base.ItemList):
  """Class that represents a list of todo entries.

  It is typically read from a file at the start of a session and written to a
  file at the end of a session. It also has methods for updating entries and
  querying subsets of the full list.
  """

  def __init__(self, version=None, modified_date=None, source_fname=None):
    super().__init__(
      version=version, modified_date=modified_date, source_fname=source_fname)

    # Maps holding cheat sheet meta data.
    self._tag_set = set()

  @property
  def tag_set(self):
    """set(str): Set of tags in this list"""
    return self._tag_set

  def add_item(self, item, initial_load=False):
    """Adds a todo to this todo list.

    Args:
      item: The Todo object to add. Several attributes should only be set if
        this object is loaded initially from a file: oid, completed_date,
        creation_date, finished
      initial_load: Indicates that this todo object is loaded from a todo and
        thus is not a new addition to the todo list.

    Raises:
      cheatsheet.base_classes.IllegalStateError: If initial_load is False but
        item has an oid OR if initial_load is True but item lacks an oid.
    """
    super().add_item(item, initial_load=initial_load)

    # set creation date and finished state for new items.
    if not initial_load:
      item.created_date = time.time()
      item.finished = False

    self._update_object_maps(item)

  def complete_item(self, oid, set_complete=True):
    """Marks the todo with the specified oid as completed.

    Args:
      oid: The id of the item to mark as completed.
      set_completed: Optinal completion state to set item to. If false, will
        attempt to mark a completed item as not completed.

    Returns:
      Todo: The completed todo object.

    Raises:
      sjb.common.base.InvalidIDError: If no todo has a matching oid.
      sjb.common.base.IllegalStateError: If the todo is already completed or
        if set_complete is False and the item is not complted.
    """
    item = self.get_item(oid)

    if set_complete and item.finished:
      raise sjb.common.base.IllegalStateError(
        'TodoList.complete_todo', 'specified todo was already completed')
    elif not set_complete and not item.finished:
      raise sjb.common.base.IllegalStateError(
        'TodoList.complete_todo', 'specified todo was not already completed')
    if set_complete:
      item.finished = True
      item.finished_date = time.time()
      self._mark_modified()
    else:
      item.finished = False
      item.finished_date = None

    ## TODO: Not needed yet, but may be needed if maps are completion aware.
    # self._recompute_object_maps()
    return item

  def remove_item(self, oid):
    """Removes the todo item with the specified oid and updates meta data.

    Returns:
      Todo: The removed Todo object.

    Raises:
      sjb.common.base.InvalidIDError: If no item has a matching oid.
    """
    removed = super().remove_item(oid)
    self._recompute_object_maps()
    return removed

  def update_item(self, oid, text=None, priority=None, tags=None):
    """Updates todo item given by oid and returns result.

    Only arguments that are not None will be updated. If no todo is found at
    that oid, an Error is raised. The meta objects are updated to reflect the
    new contents of the todo item.

    Returns:
      Todo: The newly updated todo object.

    Raises:
      sjb.common.base.InvalidIDError: If no item has a matching oid.
    """
    item = self.get_item(oid)
    original_item = copy.deepcopy(item)

    item.text = text if text is not None else item.text
    item.priority = priority if priority is not None else item.priority
    item.tags = tags if tags is not None else item.tags

    if original_item != item:
      self._mark_modified()
      self._recompute_object_maps()

    return item

  def get_new_tags(self, tags):
    """Computes set of tags that are not in database.

    Arguments:
      tags: set(str) of tags to check if present in tag set.

    Returns:
      Set: of all tags that are new to database.
    """
    return tags - self._tag_set

  def _update_object_maps(self, item):
    """Updates meta objects to reflect the contents of item."""
    for tag in item.tags:
      self._tag_set.add(tag)

  def _recompute_object_maps(self):
    """Recomputes all meta object maps like tag_set, etc.

    This should be used after making a non-trivial change to the list like
    modifying an elements tags or removing an element.
    """
    self._tag_set = set()
    for item in self.items:
      self._update_object_maps(item)
