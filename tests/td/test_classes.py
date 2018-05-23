import pytest
import unittest.mock as mock
from sjb.td.classes import PriorityEnum
from sjb.td.classes import Todo
from sjb.td.classes import TodoMatcher
from sjb.td.classes import TodoList
import sjb.common.base as base


class TestTodo(object):

  def make_todo(self, oid=3):
    return Todo(
      'some text', priority=PriorityEnum.URGENT, tags=['tag1', 'tag2'],
      finished=True, created_date='1527001163.5411422',
      finished_date='1527015163.5411422', oid=oid)

  def test_init_tags_set(self):
    t = Todo('some text', tags=['a', 'b'])
    assert(isinstance(t.tags, set))

  def test_init_default_priority(self):
    t = Todo('some text', priority=None)
    assert(t.priority == PriorityEnum.DEFAULT.value)
    t = Todo('some text', priority=PriorityEnum.URGENT.value)
    assert(t.priority == PriorityEnum.URGENT.value)

  def test_init_default_finished(self):
    t = Todo('some text')
    assert(t.finished == False)
    t = Todo('some text', finished=True)
    assert(t.finished == True)

  def test_oid_write_once(self):
    t = Todo('some text', oid=None)
    assert(not t.oid)
    t.oid = 5
    assert(t.oid == 5)
    with pytest.raises(base.ReadOnlyError):
      t.oid = 6

  def test_oid_readonly(self):
    t = Todo('some text', oid=4)
    assert(t.oid == 4)
    with pytest.raises(base.ReadOnlyError):
      t.oid = 5

  def test_equality_same_oid(self):
    t1 = Todo('some text', oid=3)
    t2 = Todo('diff text', oid=3)
    assert(t1 != t2)

    t1 = Todo('same text', oid=3)
    t2 = Todo('same text', oid=3)
    assert(t1 == t2)

  def test_equality_tag_order(self):
    t1 = Todo('some text', tags=set(['a', 'b', 'tag']), oid=3)
    t2 = Todo('some text', tags=set(['a', 'b', 'tag']), oid=3)
    assert(t1 == t2)

    t1 = Todo('some text', tags=['a', 'b', 'tag'], oid=3)
    t2 = Todo('some text', tags=set(['a', 'b', 'tag']), oid=3)
    assert(t1 == t2)

    t1 = Todo('some text', tags=['tag', 'b', 'a', 'tag'], oid=3)
    t2 = Todo('some text', tags=set(['a', 'b', 'tag']), oid=3)
    assert(t1 == t2)

    t1 = Todo('some text', tags=['tag', 'a', 'a', 'tag'], oid=3)
    t2 = Todo('some text', tags=set(['a', 'b', 'tag']), oid=3)
    assert(t1 != t2)

  def test_equality_all_same(self):
    t1 = self.make_todo()
    t2 = self.make_todo()
    assert(t1 == t2)

  def test_equality_diff_text(self):
    t1 = self.make_todo()
    t2 = self.make_todo()
    t2.text = 'diff text'
    assert(t1 != t2)

  def test_equality_diff_priority(self):
    t1 = self.make_todo()
    t2 = self.make_todo()
    t2.priority = PriorityEnum.LONG_TERM
    assert(t1 != t2)

  def test_equality_diff_finished(self):
    t1 = self.make_todo()
    t2 = self.make_todo()
    t2.finished = False
    assert(t1 != t2)

  def test_equality_diff_created_date(self):
    t1 = self.make_todo()
    t2 = self.make_todo()
    t1.created_date = '1527004163.5411422'
    t2.created_date = '1527004163.5411411'
    assert(t1 != t2)

  def test_equality_diff_finished_date(self):
    t1 = self.make_todo()
    t2 = self.make_todo()
    t1.finished_date = '1527004163.5411422'
    t2.finished_date = '1527004163.5411411'
    assert(t1 != t2)

  def test_equality_diff_oid(self):
    t1 = self.make_todo(oid=4)
    t2 = self.make_todo(oid=1)
    assert(t1 != t2)

  def test_from_dict_goodvalues(self):
    d = {
      'text': 'some text',
      'tags': ['one', 'two'],
      'priority': 1,
      'finished': False,
      'created_date': '1527004163.5411422',
      'finished_date': '1527004113.5411422',
      'oid': 3
    }
    t = Todo.from_dict(d)
    assert(t.text == 'some text')
    assert(t.tags == set({'one', 'two'}))
    assert(t.priority == PriorityEnum.URGENT.value)
    assert(t.finished == False)
    assert(t.created_date == '1527004163.5411422')
    assert(t.finished_date == '1527004113.5411422')
    assert(t.oid == 3)


class TestTodoList(object):

  mock_time = mock.Mock()
  mock_time.return_value = 4163.5411422

  def test_init(self):
    l = TodoList(version='0.1.3', modified_date='1527004163.5411422')
    assert(l.version == '0.1.3')
    assert(l.modified_date == '1527004163.5411422')
    assert(l.modified == False)
    assert(l.size() == 0)

  @mock.patch('time.time', mock_time)
  def test_add_item_new(self):
    l = TodoList()
    item = Todo('new toto item')
    l.add_item(item, initial_load=False)

    assert(item.created_date == 4163.5411422)
    assert(item.finished == False)
    assert(not item.finished_date)
    assert(l.size() == 1)
    assert(l.modified == True)

  @mock.patch('time.time', mock_time)
  def test_add_item_new_has_id(self):
    l = TodoList()
    item = Todo('new toto item', oid=1)
    with pytest.raises(base.IllegalStateError):
      l.add_item(item, initial_load=False)

  @mock.patch('time.time', mock_time)
  def test_add_item_new_tag_set(self):
    l = TodoList()
    i1 = Todo('old item', tags=['tag1', 'tag2'])
    i2 = Todo('new item', tags=['tag2', 'tag3'])

    l.add_item(i1, initial_load=False)
    assert(l.get_tags() == set(['tag1', 'tag2']))
    l.add_item(i2, initial_load=False)
    assert(l.get_tags() == set(['tag1', 'tag2', 'tag3']))
    assert(l.size() == 2)
    assert(l.modified == True)

  @mock.patch('time.time', mock_time)
  def test_add_item_initial_load(self):
    l = TodoList()
    i1 = Todo(
      'old item', oid=1, tags=['tag1', 'tag2'], created_date='some date')
    i2 = Todo('new item', oid=2, tags=['tag2', 'tag3'], finished=True)

    assert(l.modified == False)
    l.add_item(i1, initial_load=True)
    l.add_item(i2, initial_load=True)
    assert(i1.created_date == 'some date')
    assert(i2.finished == True)
    assert(l.get_tags() == set(['tag1', 'tag2', 'tag3']))
    assert(l.size() == 2)
    assert(l.modified == False)

  @mock.patch('time.time', mock_time)
  def test_add_item_initial_load_no_id(self):
    l = TodoList()
    i1 = Todo('old item', tags=['tag1', 'tag2'])

    with pytest.raises(base.IllegalStateError):
      l.add_item(i1, initial_load=True)
    l.add_item(i1, initial_load=False)

  def test_add_item_initial_load_dupe_id(self):
    l = TodoList()
    l.add_item(Todo('new todo item', oid=5), initial_load=True)
    with pytest.raises(base.IllegalStateError):
      l.add_item(Todo('new todo item', oid=5), initial_load=True)

  def test_get_item_new_item(self):
    l = TodoList()
    i1 = Todo('old toto item')
    i2 = Todo('new toto item')
    l.add_item(i1, initial_load=False)
    l.add_item(i2, initial_load=False)

    assert(i2 == l.get_item(2))

  def test_get_item_old_item(self):
    l = TodoList()
    i1 = Todo('old toto item', oid=10)
    i2 = Todo('new toto item')
    l.add_item(i1, initial_load=True)
    l.add_item(i2, initial_load=False)

    assert(i1 == l.get_item(10))

  def test_get_item_id_inc(self):
    l = TodoList()
    i1 = Todo('old toto item', oid=10)
    i2 = Todo('new toto item')
    l.add_item(i1, initial_load=True)
    l.add_item(i2, initial_load=False)

    assert(i2 == l.get_item(11))

  def test_get_item_bad_id(self):
    l = TodoList()
    i1 = Todo('old toto item', oid=10)
    l.add_item(i1, initial_load=True)
    with pytest.raises(base.InvalidIDError):
      l.get_item(1)

  @mock.patch('time.time', mock_time)
  def test_complete_item(self):
    l = TodoList()
    i1 = Todo('old toto item', oid=3, tags=set(['a', 'b']))
    l.add_item(i1, initial_load=True)

    assert(not l.get_item(3).finished)
    l.complete_item(3, set_complete=True)
    assert(l.get_item(3).finished)
    assert(l.get_item(3).finished_date == 4163.5411422)
    assert(l.get_item(3).created_date != 4163.5411422)

  @mock.patch('time.time', mock_time)
  def test_complete_item_reverse(self):
    l = TodoList()
    i1 = Todo('old toto item', oid=3, tags=set(['a', 'b']))
    l.add_item(i1, initial_load=True)
    l.complete_item(3, set_complete=True)
    assert(l.get_item(3).finished)
    assert(l.get_item(3).finished_date == 4163.5411422)
    l.complete_item(3, set_complete=False)
    assert(not l.get_item(3).finished)
    assert(not l.get_item(3).finished_date)

  @mock.patch('time.time', mock_time)
  def test_complete_item_already_completed(self):
    l = TodoList()
    i1 = Todo('old toto item', oid=3, tags=set(['a', 'b']))
    l.add_item(i1, initial_load=True)
    l.complete_item(3, set_complete=True)
    with pytest.raises(base.IllegalStateError):
      l.complete_item(3, set_complete=True)

  @mock.patch('time.time', mock_time)
  def test_complete_item_already_not_completed(self):
    l = TodoList()
    i1 = Todo('old toto item', oid=3, tags=set(['a', 'b']))
    l.add_item(i1, initial_load=True)
    with pytest.raises(base.IllegalStateError):
      l.complete_item(3, set_complete=False)

  def test_remove_item(self):
    l = TodoList()
    i1 = Todo('old toto item', oid=3, tags=set(['a', 'b']))
    l.add_item(i1, initial_load=True)

    assert(l.size() == 1)
    assert(l.get_item(3) == i1)
    assert(l.get_tags() == set(['a', 'b']))
    l.remove_item(3)
    assert(l.size() == 0)
    with pytest.raises(base.InvalidIDError):
      l.get_item(3)
    assert(l.get_tags() == set())
    assert(l.modified)

  def test_remove_item_after_initial(self):
    l = TodoList()
    i1 = Todo('old toto item', tags=set(['a', 'b']))
    l.add_item(i1, initial_load=False)

    assert(l.size() == 1)
    assert(l.get_item(1) == i1)
    assert(l.get_tags() == set(['a', 'b']))
    l.remove_item(1)
    assert(l.size() == 0)
    with pytest.raises(base.InvalidIDError):
      l.get_item(1)
    assert(l.get_tags() == set())

  def test_remove_item_tagset(self):
    l = TodoList()
    i1 = Todo('old toto item', oid=1, tags=set(['a', 'b', 'c']))
    i2 = Todo('old toto item', oid=2, tags=set(['b', 'c', 'd']))
    l.add_item(i1, initial_load=True)
    l.add_item(i2, initial_load=True)

    assert(l.get_tags() == set(['a', 'b', 'c', 'd']))
    l.remove_item(1)
    assert(l.get_tags() == set(['b', 'c', 'd']))

  def test_remove_item_bad_id(self):
    l = TodoList()
    i1 = Todo('old toto item', oid=3, tags=set(['a', 'b']))
    with pytest.raises(base.InvalidIDError):
      l.remove_item(1)

  def setup_initial_list(self, todos):
    l = TodoList()
    for t in todos:
      l.add_item(t, initial_load=True)
    return l

  def test_remove_item_readd_dupe_id(self):
    l = self.setup_initial_list([
      Todo('old toto item', oid=1, tags=set(['a', 'b', 'c'])),
      Todo('old toto item', oid=2, tags=set(['b', 'c', 'd']))
    ])

    l.remove_item(1)
    l.add_item(
      Todo('old toto item', oid=1, tags=set(['a', 'b', 'c'])),
      initial_load=True)
    assert(bool(l.get_item(1)))

  def test_remove_item_complex(self):
    l = self.setup_initial_list([
      Todo('first todo item', oid=1, tags=set(['a', 'b'])),
      Todo('2nd todo item', oid=2, tags=set()),
      Todo('3rd', oid=10, tags=set(['c']))
    ])
    newly = [
      Todo('new item', tags=set(['b', 'd'])),
      Todo('new item 2', tags=set())
    ]
    for n in newly:
      l.add_item(n, initial_load=False)

    assert(l.size() == 5)
    assert(l.get_tags() == set(['a','b','c','d']))
    l.remove_item(1)
    assert(l.size() == 4)
    assert(l.get_tags() == set(['b','c','d']))
    assert(l.modified)
    l.add_item(
      Todo('first todo item', tags=set(['a', 'b'])), initial_load=False)
    assert(l.size() == 5)
    assert(l.get_tags() == set(['a','b','c','d']))

  def test_update_item_text(self):
    l = self.setup_initial_list([
      Todo('original text', oid=1, tags=set(['a', 'b'])),
      Todo('2nd todo item', oid=2, tags=set()),
      Todo('3rd', oid=10, tags=set(['c']))
    ])
    assert(l.get_item(1).text == 'original text')
    l.update_item(1, text='new text')
    assert(l.get_item(1).text == 'new text')
    assert(l.get_tags() == set(['a','b','c']))
    assert(l.modified)

  def test_update_item_tags(self):
    l = self.setup_initial_list([
      Todo('first todo item', oid=1, tags=set(['a', 'b'])),
      Todo('2nd todo item', oid=2, tags=set()),
      Todo('3rd', oid=10, tags=set(['c']))
    ])
    assert(l.get_tags() == set(['a','b','c']))
    l.update_item(1, tags=['a','d'])
    assert(l.get_tags() == set(['a','d','c']))
    assert(l.modified)

  def test_update_item_priority(self):
    l = self.setup_initial_list([
      Todo('original text', oid=1, tags=set(['a', 'b'])),
      Todo('2nd todo item', oid=2, tags=set()),
      Todo('3rd', oid=10, tags=set(['c']))
    ])
    assert(l.get_item(1).priority == PriorityEnum.DEFAULT.value)
    l.update_item(1, priority=PriorityEnum.URGENT.value)
    assert(l.get_item(1).priority == PriorityEnum.URGENT.value)
    assert(l.get_tags() == set(['a','b','c']))
    assert(l.modified)

  def test_update_item_nochange(self):
    l = self.setup_initial_list([
      Todo('first todo item', oid=1, tags=set(['a', 'b'])),
      Todo('2nd todo item', oid=2, tags=set()),
      Todo('3rd', oid=10, tags=set(['c']))
    ])

    l.update_item(1, text='first todo item', priority=PriorityEnum.DEFAULT.value, tags=set(['a', 'b']))
    assert(not l.modified)

  def test_update_item_bad_id(self):
    l = self.setup_initial_list([
      Todo('first todo item', oid=1, tags=set(['a', 'b'])),
      Todo('2nd todo item', oid=2, tags=set()),
      Todo('3rd', oid=10, tags=set(['c']))
    ])
    with pytest.raises(base.InvalidIDError):
      l.update_item(6, text='stuff')

  def test_query_all(self):
    lib = [
      Todo('first todo item', oid=1, tags=set(['d', 'a', 'b'])),
      Todo('2nd todo item', oid=2, priority=PriorityEnum.URGENT.value),
      Todo('3rd', oid=10, tags=set(['c'])),
      Todo('4th', oid=3, finished=True, tags=set(['c'])),
      Todo('3rd', oid=11, tags=set(['a', 'b', 'e']))
    ]
    l = self.setup_initial_list(lib)

    ret = l.query_items(TodoMatcher())
    for t in lib:
      assert(t in ret)

  def test_query_priority(self):
    lib = [
      Todo('first todo item', oid=1, tags=set(['d', 'a', 'b'])),
      Todo('2nd todo item', oid=2, priority=PriorityEnum.URGENT.value),
      Todo('3rd', oid=10, tags=set(['c'])),
      Todo('4th', oid=3, finished=True, tags=set(['c'])),
      Todo('3rd', oid=11, tags=set(['a', 'b', 'e']))
    ]
    l = self.setup_initial_list(lib)

    ret = l.query_items(TodoMatcher(priority=PriorityEnum.URGENT.value))
    assert(ret == [lib[1]])

  def test_query_tag(self):
    lib = [
      Todo('first todo item', oid=1, tags=set(['d', 'a', 'b'])),
      Todo('2nd todo item', oid=2, priority=PriorityEnum.URGENT.value),
      Todo('3rd', oid=10, tags=set(['a', 'c'])),
      Todo('4th', oid=3, finished=True, tags=set(['c'])),
      Todo('3rd', oid=11, tags=set(['a', 'b', 'e']))
    ]
    l = self.setup_initial_list(lib)

    ret = l.query_items(TodoMatcher(tags=['a']))
    assert(len(ret) == 3)
    assert(lib[0] in ret)
    assert(lib[2] in ret)
    assert(lib[4] in ret)

  def test_query_tags(self):
    lib = [
      Todo('first todo item', oid=1, tags=set(['d', 'a', 'b'])),
      Todo('2nd todo item', oid=2, priority=PriorityEnum.URGENT.value),
      Todo('3rd', oid=10, tags=set(['c'])),
      Todo('4th', oid=3, finished=True, tags=set(['c'])),
      Todo('3rd', oid=11, tags=set(['a', 'b', 'e']))
    ]
    l = self.setup_initial_list(lib)

    ret = l.query_items(TodoMatcher(tags=['a', 'b']))
    assert(len(ret) == 2)
    assert(lib[0] in ret)
    assert(lib[4] in ret)

  def test_query_tags_finished(self):
    lib = [
      Todo('first todo item', oid=1, tags=set(['d', 'a', 'b'])),
      Todo('2nd todo item', oid=2, priority=PriorityEnum.URGENT.value),
      Todo('3rd', oid=10, tags=set(['c'])),
      Todo('4th', oid=3, finished=True, tags=set(['c'])),
      Todo('3rd', oid=11, tags=set(['a', 'b', 'e']))
    ]
    l = self.setup_initial_list(lib)

    ret = l.query_items(TodoMatcher(finished=True))
    assert(ret == [lib[3]])

  def test_query_tags_not_finished(self):
    lib = [
      Todo('first todo item', oid=1, tags=set(['d', 'a', 'b'])),
      Todo('2nd todo item', oid=2, priority=PriorityEnum.URGENT.value),
      Todo('3rd', oid=10, tags=set(['c'])),
      Todo('4th', oid=3, finished=True, tags=set(['c'])),
      Todo('3rd', oid=11, tags=set(['a', 'b', 'e']))
    ]
    l = self.setup_initial_list(lib)

    ret = l.query_items(TodoMatcher(finished=False))
    assert(len(ret) == 4)
    assert(lib[0] in ret)
    assert(lib[1] in ret)
    assert(lib[2] in ret)
    assert(lib[4] in ret)

  def run_validate(self, todos):
    l = TodoList()
    for t in todos:
      l.add_item(t, initial_load=True)
    l.validate()

  def test_validate_new_item(self):
    l = TodoList()
    l.add_item(Todo('some text'))
    l.validate()

  def test_validate_okay_not_finished(self):
    self.run_validate([Todo(
      'some text',
      priority=PriorityEnum.URGENT.value,
      tags=set(['some', 'tags']),
      finished=False,
      created_date=1234.1234,
      finished_date=None,
      oid=1)])

  def test_validate_okay_finished(self):
    self.run_validate([Todo(
      'some text',
      priority=PriorityEnum.URGENT.value,
      tags=set(['some', 'tags']),
      finished=True,
      created_date=1234.2134,
      finished_date=1234.1234,
      oid=1)])

  def test_validate_non_int_id(self):
    self.run_validate([Todo('a string', oid=1, created_date=1234.1234)])
    with pytest.raises(base.ValidationError):
      self.run_validate([Todo('a string', oid=1.1, created_date=1234.1234)])

  def test_validate_no_creation_date(self):
    self.run_validate([Todo('a string', oid=1, created_date=1234.1234)])
    with pytest.raises(base.ValidationError):
      self.run_validate([Todo('a string', oid=1)])

  def test_validate_non_float_created_date(self):
    self.run_validate([Todo('a string', oid=1, created_date=1234.1234)])
    with pytest.raises(base.ValidationError):
      self.run_validate([Todo('a string', oid=1, created_date=1234)])

  def test_validate_empty_text(self):
    self.run_validate([Todo('string', oid=1, created_date=1234.1234)])
    with pytest.raises(base.ValidationError):
      self.run_validate([Todo('', oid=1, created_date=1234.1234)])

  def test_validate_nonstr_text(self):
    self.run_validate([Todo('string', oid=1, created_date=1234.1234)])
    with pytest.raises(base.ValidationError):
      self.run_validate([Todo(54, oid=1, created_date=1234.1234)])

  def test_validate_nonset_tags(self):
    l = TodoList()
    l.add_item(Todo('some text'))
    l.get_item(1).tags = set(['a', 'b'])
    l.validate()
    with pytest.raises(base.ValidationError):
      l.get_item(1).tags = ['a', 'b']
      l.validate()

  def test_validate_invalid_priority(self):
    l = TodoList()
    l.add_item(Todo('some text'))
    l.get_item(1).priority = PriorityEnum.URGENT.value
    l.validate()
    with pytest.raises(base.ValidationError):
      l.get_item(1).priority = None
      l.validate()
    with pytest.raises(base.ValidationError):
      l.get_item(1).priority = 16
      l.validate()
    with pytest.raises(base.ValidationError):
      l.get_item(1).priority = 'cactus'
      l.validate()
    l.get_item(1).priority = PriorityEnum.DEFAULT.value
    l.validate()

  def test_validate_finished_no_date(self):
    l = TodoList()
    l.add_item(Todo('some text'))
    l.get_item(1).finished = True
    l.get_item(1).finished_date = 1234.1234
    l.validate()
    with pytest.raises(base.ValidationError):
      l.get_item(1).finished = True
      l.get_item(1).finished_date = None
      l.validate()

  def test_validate_finished_non_float_date(self):
    l = TodoList()
    l.add_item(Todo('some text'))
    l.get_item(1).finished = True
    l.get_item(1).finished_date = 1234.1234
    l.validate()
    with pytest.raises(base.ValidationError):
      l.get_item(1).finished = True
      l.get_item(1).finished_date = 1234
      l.validate()

  def test_validate_not_finished_has_finished_date(self):
    l = TodoList()
    l.add_item(Todo('some text'))
    l.get_item(1).finished = True
    l.get_item(1).finished_date = 1234.1234
    l.validate()
    with pytest.raises(base.ValidationError):
      l.get_item(1).finished = False
      l.get_item(1).finished_date = 1234.1234
      l.validate()

  def test_validate_finished_not_bool(self):
    l = TodoList()
    l.add_item(Todo('some text'))
    l.get_item(1).finished = True
    l.get_item(1).finished_date = 1234.1234
    l.validate()
    with pytest.raises(base.ValidationError):
      l.get_item(1).finished = 'ham'
      l.get_item(1).finished_date = 1234.1234
      l.validate()

  def test_validate_finished_None(self):
    l = TodoList()
    l.add_item(Todo('some text'))
    l.get_item(1).finished = False
    l.validate()
    with pytest.raises(base.ValidationError):
      l.get_item(1).finished = None
      l.validate()

  @mock.patch('time.time', mock_time)
  def test_modified_date_add_new(self):
    l = TodoList(version='version str', modified_date=1234.1234)
    assert(l.modified_date == 1234.1234)
    l.add_item(Todo('a new todo'))
    assert(l.modified_date == 4163.5411422)

  @mock.patch('time.time', mock_time)
  def test_modified_date_update(self):
    l = TodoList(version='version str', modified_date=1234.1234)
    assert(l.modified_date == 1234.1234)
    l.add_item(Todo('a new todo', oid=1, created_date=4.4), initial_load=True)
    assert(l.modified_date == 1234.1234)
    l.update_item(1, text='howdy')
    assert(l.modified_date == 4163.5411422)

  @mock.patch('time.time', mock_time)
  def test_modified_date_remove(self):
    l = TodoList(version='version str', modified_date=1234.1234)
    assert(l.modified_date == 1234.1234)
    l.add_item(Todo('a new todo', oid=1, created_date=4.4), initial_load=True)
    assert(l.modified_date == 1234.1234)
    l.remove_item(1)
    assert(l.modified_date == 4163.5411422)

  @mock.patch('time.time', mock_time)
  def test_to_dict(self):
    l = TodoList(version='version str', modified_date=1234.1234)
    init = [
      Todo('text 1', oid=1, created_date=1234.1),
      Todo('text 2', oid=2, created_date=1234.2, finished=True, finished_date=2345.2),
      Todo('text 5', oid=5, created_date=1234.5, tags=['c', 'd'])
    ]
    init_exp = [{
        'oid': 1,
        'text': 'text 1',
        'priority': PriorityEnum.DEFAULT.value,
        'tags': [],
        'finished': False,
        'created_date': 1234.1,
        'finished_date': None
      },{
        'oid': 2,
        'text': 'text 2',
        'priority': PriorityEnum.DEFAULT.value,
        'tags': [],
        'finished': True,
        'created_date': 1234.2,
        'finished_date': 2345.2
      },{
        'oid': 5,
        'text': 'text 5',
        'priority': PriorityEnum.DEFAULT.value,
        'tags': ['c', 'd'],
        'finished': False,
        'created_date': 1234.5,
        'finished_date': None
      }
    ]
    new = [Todo('new item 1'), Todo('new item 2')]
    new_exp = [{
        'oid': 6,
        'text': 'new item 1',
        'priority': PriorityEnum.DEFAULT.value,
        'tags': [],
        'finished': False,
        'created_date': 4163.5411422,
        'finished_date': None
      }, {
        'oid': 7,
        'text': 'new item 2',
        'priority': PriorityEnum.DEFAULT.value,
        'tags': [],
        'finished': False,
        'created_date': 4163.5411422,
        'finished_date': None
      }
    ]

    for i in init:
      l.add_item(i, initial_load=True)
    for n in new:
      l.add_item(n, initial_load=False)

    d = l.to_dict()['todo_list']
    assert(d['version'] == 'version str')
    assert(d['modified_date'] == 4163.5411422)
    assert(len(d.keys()) == 3)
    todos = d['todos']
    assert(len(todos) == 5)
    for e in init_exp:
      assert(e in todos)
    for e in new_exp:
      assert(e in todos)

  def test_from_dict(self):
    d = {'todo_list': {
      'version': 'version str',
      'modified_date': 4.1,
      'todos': [{
        'oid': 1,
        'tags': [],
        'priority': PriorityEnum.URGENT.value,
        'text': 'text 1',
        'finished': False,
        'created_date': 1234.1,
        'finished_date': None
      }, {
        'oid': 2,
        'tags': [],
        'priority': PriorityEnum.DEFAULT.value,
        'text': 'text 2',
        'finished': True,
        'created_date': 1234.2,
        'finished_date': 2345.2
      }, {
        'oid': 5,
        'tags': ['c', 'd'],
        'priority': PriorityEnum.DEFAULT.value,
        'text': 'text 5',
        'finished': False,
        'created_date': 1234.5,
        'finished_date': None
      }, {
        'oid': 6,
        'tags': [],
        'priority': PriorityEnum.DEFAULT.value,
        'text': 'new item 1',
        'finished': False,
        'created_date': 4163.5411422,
        'finished_date': None
      }, {
        'oid': 7,
        'tags': [],
        'priority': PriorityEnum.DEFAULT.value,
        'text': 'new item 2',
        'finished': False,
        'created_date': 4163.5411422,
        'finished_date': None}]}}
    exp_todos = [
      Todo('text 1', oid=1, created_date=1234.1, priority=PriorityEnum.URGENT.value),
      Todo('text 2', oid=2, created_date=1234.2, finished=True, finished_date=2345.2),
      Todo('text 5', oid=5, created_date=1234.5, tags=['c', 'd']),
      Todo('new item 1', oid=6, created_date=4163.5411422),
      Todo('new item 2', oid=7, created_date=4163.5411422)
    ]
    l = TodoList.from_dict(d)
    assert(not l.modified)
    assert(l.version == 'version str')
    assert(l.modified_date == 4.1)

    assert(l.size() == 5)
    for t in l.items:
      assert t in exp_todos
