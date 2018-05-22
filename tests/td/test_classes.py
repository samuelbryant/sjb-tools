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
  mock_time.return_value = '4163.5411422'

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

    assert(item.created_date == '4163.5411422')
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
    assert(l.get_item(3).finished_date == '4163.5411422')
    assert(l.get_item(3).created_date != '4163.5411422')

  @mock.patch('time.time', mock_time)
  def test_complete_item_reverse(self):
    l = TodoList()
    i1 = Todo('old toto item', oid=3, tags=set(['a', 'b']))
    l.add_item(i1, initial_load=True)
    l.complete_item(3, set_complete=True)
    assert(l.get_item(3).finished)
    assert(l.get_item(3).finished_date == '4163.5411422')
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

  def test_remove_item_readd_dupe_id(self):
    l = TodoList()
    i1 = Todo('old toto item', oid=1, tags=set(['a', 'b', 'c']))
    i2 = Todo('old toto item', oid=2, tags=set(['b', 'c', 'd']))
    l.add_item(i1, initial_load=True)
    l.add_item(i2, initial_load=True)

    l.remove_item(1)

    l.add_item(i1, initial_load=True)

    assert(bool(l.get_item(1)))

  def test_remove_item_complex(self):
    l = TodoList()
    initial = [
      Todo('first todo item', oid=1, tags=set(['a', 'b'])),
      Todo('2nd todo item', oid=2, tags=set()),
      Todo('3rd', oid=10, tags=set(['c']))
    ]
    newly = [
      Todo('new item', tags=set(['b', 'd'])),
      Todo('new item 2', tags=set())
    ]
    for t in initial:
      l.add_item(t, initial_load=True)
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

  def test_update_item(self):
    pass

  def test_to_dict(self):
    pass

  def test_from_dict(self):
    pass

  def test_query(self):
    pass

  def test_validate(self):
    pass
