"""Module containing all core class definitions for this program."""
import copy
import sjb.common.base


## Global constants which determine search method.
SEARCH_AND = 0
SEARCH_OR = 1


class EntryMatcherTags(sjb.common.base.ItemMatcher):
  """Class that matches entries using their tags."""

  def __init__(self, tags, andor=SEARCH_OR):
    """Initializes an EntryMatcherTag

    Arguments:
      andor: Determines if ALL conditions must be met or ANY condition must be
        met. Should be SEARCH_AND or SEARCH_OR
      tags: Set of tags to match (can be primary or secondary.)
    """
    self.tags = tags
    self.andor = andor

  def matches(self, item):
    """Returns true if the item has any/all of the specified tags."""
    if not super().matches(item):
      return False
    if not self.tags:
      return True

    if self.andor is SEARCH_AND:
      for tag in self.tags:
        if tag != item.primary and tag not in item.tags:
          return False
      return True

    elif self.andor is SEARCH_OR:
      for tag in self.tags:
        if tag == item.primary or tag in item.tags:
          return True
      return False
    else:
      raise sjb.common.base.IllegalStateError(
        'Entry.matches', 'invalid andor argument '+str(self.andor))


class Entry(sjb.common.base.Item):
  """Class representing an entry in a cheat sheet"""

  def __init__(self, clue, answer, primary, tags, oid=None):
    super().__init__(oid)
    # Values that should be set at construction time
    self.clue = clue
    self.answer = answer
    self.primary = primary
    self.tags = set(tags) if tags is not None else set()

  def __eq__(self, other):
    """Returns true if self and other have identical fields."""
    if not super().__eq__(other): return False
    if self.clue != other.clue: return False
    if self.primary != other.primary: return False
    if self.tags != other.tags: return False
    if self.answer != other.answer: return False
    return True

  def _validate(self):
    """Validates that the values of this item are sensible.

    This method should be called twice: The first time at the end of the
    initialization code to make sure the user is not misusing the constructor.
    The second time should be before saving to a database to make sure that
    manipulations made to this item after initialization were valid.

    Raises:
      sjb.common.base.ValidationError: If validation fails
    """
    super()._validate()
    if not self.clue or not isinstance(self.clue, str):
      raise sjb.common.base.ValidationError('Bad entry clue: '+str(self.clue))
    if not self.primary or not isinstance(self.primary, str):
      raise sjb.common.base.ValidationError('Bad primary: '+str(self.primary))
    if not self.answer or not isinstance(self.answer, str):
      raise sjb.common.base.ValidationError('Bad answer: '+str(self.answer))
    if not isinstance(self.tags, set):
      raise sjb.common.base.ValidationError('Bad tags: '+str(self.tags))

    if self.oid is not None and not isinstance(self.oid, int):
      raise sjb.common.base.ValidationError('Bad oid: '+str(self.oid))

  def _to_dict(self):
    """Converts data to a dict suitable for writing to a file as json.

    Returns:
      dict: stable dict of values suitable to be written as JSON.
    """
    return {
      'oid': self.oid,
      'primary': self.primary,
      'tags': sorted(list(self.tags)),
      'clue': self.clue,
      'answer': self.answer
    }

  @staticmethod
  def from_dict(json_dict):
    """Constructs Entry from dict (which was loaded from a JSON file).

    Args:
      json_dict: Dict containing the necessary fields for an Entry object.

    Returns:
      Entry: Entry object represented by the dict.
   """
    e = Entry(
      clue=json_dict['clue'],
      answer=json_dict['answer'],
      primary=json_dict['primary'],
      tags=set(json_dict['tags']),
      oid=json_dict['oid'])
    return e

class CheatSheet(sjb.common.base.ItemList):
  """Class that represents an entire cheat sheet.

  It is typically read from a file at the start of a session and written to a
  file at the end of a session. It has methods for querying a subset of the
  full entries.
  """

  def __init__(self, version=None, modified_date=None):
    super().__init__(version=version, modified_date=modified_date)

    # Maps holding cheat sheet meta data.
    self._primary_map = {}
    self._tag_set = set()

  @property
  def tag_set(self):
    """set(str): TODO: Set of tags in this CheatSheet."""
    return self._tag_set

  @property
  def primary_map(self):
    """TODO: Dict mapping primary tags to lists of entries."""
    return self._primary_map

  def add_item(self, item, initial_load=False):
    """Adds an entry to this cheatsheet.

    Args:
      item: The Entry object to add. It should only have an oid set if it was
        loaded from cheat sheet file.
      initial_load: Indicates that this entry object is from the cheat sheet
        file and is not a new addition to the cheat sheet.

    Raises:
      cheatsheet.base_classes.IllegalStateError: If initial_load is False but
        entry has an oid OR if initial_load is True but entry lacks an oid.
    """
    super().add_item(item, initial_load=initial_load)
    self._update_object_maps(item)

  def remove_item(self, oid):
    """Removes the entry with the specified oid and updates meta data.

    Returns:
      Entry: The removed entry object.

    Raises:
      sjb.common.base.InvalidIDError: If no item has a matching oid.
    """
    removed = super().remove_item(oid)
    self._recompute_object_maps()
    return removed

  def update_item(self, oid, clue=None, answer=None, primary=None, tags=None):
    """Updates entry given by oid and returns the result.

    Only arguments that are not None will be updated. If no entry is found at
    that oid, an Error is raised. The meta objects are updated to reflect the
    new contents of the entry.

    Returns:
      Entry: The newly updated entry object.

    Raises:
      sjb.common.base.InvalidIDError: If no item has a matching oid.
    """
    item = self.get_item(oid)
    original_item = copy.deepcopy(item)

    item.primary = primary if primary is not None else item.primary
    item.clue = clue if clue is not None else item.clue
    item.answer = answer if answer is not None else item.answer
    item.tags = tags if tags is not None else item.tags

    # Mark as modified only if the object is changed.
    if original_item != item:
      self._mark_modified()
      self._recompute_object_maps()

    return item

  def get_new_tags(self, primary, tags):
    """Computes set of primary and tags that are not in database.

    Arguments:
      primary: str primary tag to check if present in primary set.
      tags: set(str) of tags to check if present in tag set.

    Returns:
      # TODO: of primary + all tags that are new to database.
    """
    new_elts = tags - self._tag_set
    if primary not in self._primary_map:
      new_elts.add(primary)
    return new_elts

  def _update_object_maps(self, item):
    """Updates meta objects to reflect the contents of item."""
    if item.primary not in self._primary_map.keys():
      self._primary_map[item.primary] = []
    self._primary_map[item.primary].append(item)

    for tag in item.tags:
      self._tag_set.add(tag)
    self._tag_set.add(item.primary)

  def _recompute_object_maps(self):
    """Recomputes all meta object maps like tag_set, primary_to_entries, etc.

    This should be used after making a non-trivial change to the list like
    modifying an elements tags or removing an element.
    """
    self._primary_map = {}
    self._tag_set = set()

    for item in self._items:
      self._update_object_maps(item)

  def to_dict(self):
    """Converts data to a dict suitable for writing to a file as json.

    Returns:
      dict: stable dict of values suitable to be written as JSON.
    """
    return {
      'cheatsheet': {
        'version': self.version,
        'modified_date': self.modified_date,
        'entries': [e._to_dict() for e in self.items]
      }
    }

  @staticmethod
  def from_dict(json_dict):
    """Constructs CheatSheet from dict (which was loaded from a JSON file).

    Args:
      json_dict: Dict containing the necessary fields for a CheatSheet.

    Returns:
      CheatSheet: Object represented by the dict.
    """
    json_dict = json_dict['cheatsheet']
    modified_date = json_dict.get('modified_date', None)
    version = json_dict.get('version', None)
    l = CheatSheet(version=version, modified_date=modified_date)

    # Add entries to cheat sheet
    for item_json in json_dict['entries']:
      item = Entry.from_dict(item_json)
      l.add_item(item, initial_load=True)

    return l
