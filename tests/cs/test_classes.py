import pytest
import unittest.mock as mock
import sjb.cs.classes
from sjb.cs.classes import Entry
from sjb.cs.classes import EntryMatcherTags
from sjb.cs.classes import CheatSheet
import sjb.common.base as base


class TestEntry(object):

  def make_entry(self, clue='a clue', answer='an answer', primary='primary tag', oid=3, tags=['a', 'b']):
    return Entry(clue, answer, primary, tags, oid=oid)

  def test_init_tags_set(self):
    t = Entry('a clue', 'an answer', 'primarytag', ['a', 'b'])
    assert isinstance(t.tags, set)

  def test_oid_write_once(self):
    t = Entry('a clue', 'an answer', 'primarytag', ['a', 'b'])
    assert not t.oid
    t.oid = 5
    assert t.oid == 5
    with pytest.raises(base.ReadOnlyError):
      t.oid = 6

  def test_oid_readonly(self):
    t = Entry('a clue', 'an answer', 'primarytag', ['a', 'b'], oid=4)
    assert t.oid == 4
    with pytest.raises(base.ReadOnlyError):
      t.oid = 5

  def test_equality(self):
    t1 = self.make_entry()
    t2 = self.make_entry()
    assert t1 == t2

    t1 = self.make_entry(oid=1)
    t2 = self.make_entry(oid=2)
    assert t1 != t2
    t1 = self.make_entry()
    t2 = self.make_entry(clue='new clue')
    assert t1 != t2
    t1 = self.make_entry()
    t2 = self.make_entry(answer='new answer')
    assert t1 != t2
    t1 = self.make_entry()
    t2 = self.make_entry(primary='new primary')
    assert t1 != t2
    t1 = self.make_entry(tags=['a', 'b'])
    t2 = self.make_entry(tags=['a', 'b', 'c'])
    assert t1 != t2
    t1 = self.make_entry(tags=['a', 'b'])
    t2 = self.make_entry(tags=['b', 'a'])
    assert t1 == t2

  def test_from_dict_goodvalues(self):
    d = {
      'clue': 'a clue',
      'answer': 'an answer',
      'primary': 'p tag',
      'tags': ['tag1', 'tag2'],
      'oid': 3
    }
    t = Entry.from_dict(d)
    assert t.clue == 'a clue'
    assert t.answer == 'an answer'
    assert t.primary == 'p tag'
    assert t.tags == set({'tag1', 'tag2'})
    assert t.oid == 3


MOCK_TIME = 4163.5411422

class TestCheatSheet(object):

  mock_time = mock.Mock()
  mock_time.return_value = MOCK_TIME

  def test_init(self):
    l = CheatSheet(version='0.1.3', modified_date=1234.1234)
    assert l.version == '0.1.3'
    assert l.modified_date == 1234.1234
    assert l.modified == False
    assert l.size() == 0

  def test_init_defaults(self):
    l = CheatSheet()
    assert l.version == None
    assert l.modified_date == None
    assert l.modified == False
    assert l.size() == 0

  @mock.patch('time.time', mock_time)
  def test_add_item_new(self):
    TestCheatSheet.mock_time.return_value = MOCK_TIME
    l = CheatSheet()
    i = Entry('clue1', 'answer1', 'primary1', ['a', 'b'])
    l.add_item(i, initial_load=False)

    assert l.tag_set == {'primary1', 'a', 'b'}
    assert l.size() == 1
    assert l.modified == True
    assert l.modified_date == MOCK_TIME
    assert TestCheatSheet.mock_time.called_once_with()

  @mock.patch('time.time', mock_time)
  def test_add_item_new_has_id(self):
    l = CheatSheet()
    i = Entry('clue1', 'answer1', 'primary1', ['tag1', 'tag2'], oid=1)
    with pytest.raises(base.IllegalStateError):
      l.add_item(i, initial_load=False)

  @mock.patch('time.time', mock_time)
  def test_add_item_new_primary_in_tag_set(self):
    l = CheatSheet()
    i1 = Entry('clue1', 'answer1', 'primary1', ['tag1', 'tag2'])
    i2 = Entry('clue1', 'answer1', 'primary2', ['tag2', 'tag3'])

    l.add_item(i1, initial_load=False)
    assert l.tag_set == set(['primary1', 'tag1', 'tag2'])
    l.add_item(i2, initial_load=False)
    assert l.tag_set == set(['primary1', 'primary2', 'tag1', 'tag2', 'tag3'])
    assert l.size() == 2
    assert l.modified == True

  @mock.patch('time.time', mock_time)
  def test_add_item_initial_load(self):
    l = CheatSheet(modified_date=1234.1234)
    i1 = Entry('clue1', 'answer1', 'primary1', ['tag1', 'tag2'], oid=1)
    i2 = Entry('clue2', 'answer2', 'primary1', ['tag2', 'tag3'])

    assert l.modified == False
    assert l.modified_date == 1234.1234
    l.add_item(i1, initial_load=True)
    assert l.modified == False
    assert l.modified_date == 1234.1234
    l.add_item(i2, initial_load=False)
    assert l.tag_set == set(['primary1', 'tag1', 'tag2', 'tag3'])
    assert l.size() == 2
    assert l.modified == True
    assert l.modified_date == MOCK_TIME

  @mock.patch('time.time', mock_time)
  def test_add_item_initial_load_no_id(self):
    l = CheatSheet()
    i1 = Entry('clue1', 'answer1', 'primary1', ['tag1', 'tag2'])

    with pytest.raises(base.IllegalStateError):
      l.add_item(i1, initial_load=True)
    l.add_item(i1, initial_load=False)

  def test_add_item_initial_load_dupe_id(self):
    l = CheatSheet()
    i1 = Entry('clue1', 'answer1', 'primary1', ['tag1', 'tag2'], oid=1)
    l.add_item(i1, initial_load=True)
    with pytest.raises(base.IllegalStateError):
      l.add_item(i1, initial_load=True)

  def test_get_item_new_item(self):
    l = CheatSheet()
    i1 = Entry('clue1', 'answer1', 'primary1', ['tag1', 'tag2'])
    i2 = Entry('clue2', 'answer1', 'primary1', ['tag1', 'tag2'])
    l.add_item(i1, initial_load=False)
    l.add_item(i2, initial_load=False)

    assert i2 == l.get_item(2)

  def test_get_item_old_item(self):
    l = CheatSheet()
    i1 = Entry('clue1', 'answer1', 'primary1', ['tag1', 'tag2'], oid=10)
    i2 = Entry('clue2', 'answer1', 'primary1', ['tag1', 'tag2'])
    l.add_item(i1, initial_load=True)
    l.add_item(i2, initial_load=False)

    assert i1 == l.get_item(10)

  def test_get_item_id_inc(self):
    l = CheatSheet()
    i1 = Entry('clue1', 'answer1', 'primary1', ['tag1', 'tag2'], oid=10)
    i2 = Entry('clue2', 'answer1', 'primary1', ['tag1', 'tag2'])
    l.add_item(i1, initial_load=True)
    l.add_item(i2, initial_load=False)

    assert i2 == l.get_item(11)

  def test_get_item_bad_id(self):
    l = CheatSheet()
    i1 = Entry('clue1', 'answer1', 'primary1', ['tag1', 'tag2'], oid=10)
    l.add_item(i1, initial_load=True)
    with pytest.raises(base.InvalidIDError):
      l.get_item(1)

  @mock.patch('time.time', mock_time)
  def test_remove_item(self):
    l = CheatSheet()
    i1 = Entry('clue1', 'answer1', 'primary1', ['a', 'b'], oid=3)
    l.add_item(i1, initial_load=True)

    assert l.size() == 1
    assert l.get_item(3) == i1
    assert l.tag_set == set(['primary1', 'a', 'b'])
    l.remove_item(3)
    assert l.size() == 0
    with pytest.raises(base.InvalidIDError):
      l.get_item(3)
    assert l.tag_set == set()
    assert l.modified
    assert l.modified_date == MOCK_TIME

  @mock.patch('time.time', mock_time)
  def test_remove_item_overlapping_tags(self):
    # tests that library keeps tags on removal shared with non-removed objects
    l = CheatSheet()
    i1 = Entry('clue1', 'answer1', 'primary1', ['a', 'b'], oid=1)
    i2 = Entry('clue2', 'answer1', 'primary1', ['b', 'c'], oid=2)
    l.add_item(i1, initial_load=True)
    l.add_item(i2, initial_load=True)

    assert l.tag_set == {'primary1', 'a', 'b', 'c'}
    l.remove_item(1)
    assert l.tag_set == {'primary1', 'b', 'c'} # b still there

  def test_remove_item_after_initial(self):
    # removes item that was not loaded initially
    l = CheatSheet()
    i1 = Entry('clue1', 'answer1', 'primary1', ['a', 'b'])
    l.add_item(i1, initial_load=False)

    assert l.size() == 1
    assert l.get_item(1) == i1
    assert l.tag_set == {'primary1', 'a', 'b'}
    l.remove_item(1)
    assert l.size() == 0
    with pytest.raises(base.InvalidIDError):
      l.get_item(1)
    assert l.tag_set == set()

  def test_remove_item_tagset(self):
    l = CheatSheet()
    i1 = Entry('clue1', 'answer1', 'prim1', oid=1, tags={'a', 'b', 'c'})
    i2 = Entry('clue1', 'answer1', 'prim2', oid=2, tags={'b', 'c', 'd'})
    l.add_item(i1, initial_load=True)
    l.add_item(i2, initial_load=True)

    assert l.tag_set == {'prim1', 'prim2', 'a', 'b', 'c', 'd'}
    l.remove_item(1)
    assert l.tag_set == {'prim2', 'b', 'c', 'd'}

  def test_remove_item_bad_id(self):
    l = CheatSheet()
    i1 = Entry('clue1', 'answer1', 'prim1', oid=3, tags={'a', 'b', 'c'})
    with pytest.raises(base.InvalidIDError):
      l.remove_item(1)

  def setup_initial_list(self, items):
    l = CheatSheet()
    for t in items:
      l.add_item(t, initial_load=True)
    return l

  def test_remove_item_readd_dupe_id(self):
    l = self.setup_initial_list([
      Entry('clue1', 'answer1', 'prim1', oid=1, tags={'a', 'b', 'c'}),
      Entry('clue1', 'answer1', 'prim2', oid=2, tags={'b', 'c', 'd'})
    ])

    l.remove_item(1)
    l.add_item(
      Entry('clue1', 'answer1', 'prim1', oid=1, tags=set(['a', 'b', 'c'])),
      initial_load=True)
    assert bool(l.get_item(1))

  def test_remove_item_complex(self):
    init = [
      Entry('clue1', 'answer1', 'prim1', oid=1, tags={'a', 'b'}),
      Entry('clue2', 'answer2', 'prim2', oid=2, tags={}),
      Entry('clue3', 'answer3', 'prim2', oid=10, tags={'c'}),
    ]
    newly = [
      Entry('new1', 'new1', 'prim3', tags={'b', 'd'}),
      Entry('new2', 'new2', 'prim2', tags=set())
    ]
    l = CheatSheet()
    for i in init: l.add_item(i, initial_load=True)
    for n in newly: l.add_item(n, initial_load=False)

    assert l.size() == 5
    assert l.tag_set == {'prim1', 'prim2', 'prim3', 'a','b','c','d'}
    l.remove_item(1)
    assert l.size() == 4
    assert l.tag_set == {'prim2', 'prim3', 'b','c','d'}
    assert l.modified
    l.add_item(
      Entry('clue1', 'answer1', 'prim1', tags={'a', 'b'}), initial_load=False)
    assert l.size() == 5
    assert l.tag_set == {'prim1', 'prim2', 'prim3', 'a','b','c','d'}

  @mock.patch('time.time', mock_time)
  def test_update_item_clue(self):
    init = [
      Entry('orig text 1', 'answer1', 'prim1', oid=1, tags={'a', 'b'}),
      Entry('orig text 2', 'answer2', 'prim2', oid=2, tags={}),
      Entry('orig text 3', 'answer3', 'prim2', oid=10, tags={'c'}),
    ]
    l = CheatSheet()
    for i in init: l.add_item(i, initial_load=True)

    assert not l.modified
    assert l.get_item(1).clue == 'orig text 1'
    l.update_item(1, clue='new text 1')
    assert l.get_item(1).clue == 'new text 1'
    assert l.modified
    assert l.modified_date == MOCK_TIME

  @mock.patch('time.time', mock_time)
  def test_update_item_clue(self):
    init = [
      Entry('orig text 1', 'answer1', 'prim1', oid=1, tags={'a', 'b'}),
    ]
    l = CheatSheet()
    for i in init: l.add_item(i, initial_load=True)

    assert not l.modified
    assert l.get_item(1).answer == 'answer1'
    l.update_item(1, answer='answer new')
    assert l.get_item(1).answer == 'answer new'
    assert l.modified
    assert l.modified_date == MOCK_TIME

  @mock.patch('time.time', mock_time)
  def test_update_item_tags(self):
    init = [
      Entry('orig text 1', 'answer1', 'prim1', oid=1, tags={'a', 'b'}),
      Entry('orig text 2', 'answer2', 'prim2', oid=2, tags={}),
      Entry('orig text 3', 'answer3', 'prim2', oid=10, tags={'c'}),
    ]
    l = CheatSheet()
    for i in init: l.add_item(i, initial_load=True)

    assert l.tag_set == {'prim1', 'prim2', 'a', 'b', 'c'}
    assert l.get_item(1).tags == {'a', 'b'}
    l.update_item(1, tags={'a', 'd'})
    assert l.tag_set == {'prim1', 'prim2', 'a', 'd', 'c'}
    assert l.get_item(1).tags == {'a', 'd'}
    assert l.modified
    assert l.modified_date == MOCK_TIME

  @mock.patch('time.time', mock_time)
  def test_update_item_primary(self):
    init = [
      Entry('orig text 1', 'answer1', 'prim1', oid=1, tags={'a', 'b'}),
      Entry('orig text 2', 'answer2', 'prim2', oid=2, tags={}),
      Entry('orig text 3', 'answer3', 'prim2', oid=10, tags={'c'}),
    ]
    l = CheatSheet()
    for i in init: l.add_item(i, initial_load=True)

    assert l.primary_set == {'prim1', 'prim2'}
    assert l.tag_set == {'prim1', 'prim2', 'a', 'b', 'c'}
    assert l.get_item(1).primary == 'prim1'
    l.update_item(1, primary='prim3')
    assert l.primary_set == {'prim3', 'prim2'}
    assert l.tag_set == {'prim3', 'prim2', 'a', 'b', 'c'}
    assert l.get_item(1).primary == 'prim3'
    assert l.modified
    assert l.modified_date == MOCK_TIME
    l.update_item(2, primary='prim3')
    assert l.primary_set == {'prim3', 'prim2'}
    assert l.tag_set == {'prim3', 'prim2', 'a', 'b', 'c'}
    assert l.get_item(2).primary == 'prim3'

  def test_update_item_tags_to_set(self):
    l = CheatSheet()
    l.add_item(
      Entry('1', 'c1', 'prim1', tags={'a', 'b'}, oid=1), initial_load=True)
    l.update_item(1, tags=['a', 'b'])
    assert l.get_item(1).tags == {'a', 'b'}
    assert not l.modified

  def test_update_item_nochange(self):
    l = CheatSheet()
    l.add_item(
      Entry('c1', 'a1', 'prim1', tags={'a', 'b'}, oid=1), initial_load=True)
    l.update_item(1, clue='c1', answer='a1', primary='prim1', tags={'b', 'a'})
    assert not l.modified
    assert l.modified_date == None

  def test_update_item_bad_id(self):
    l = CheatSheet()
    l.add_item(Entry('orig text 1', 'answer1', 'prim1', tags={'a', 'b'}, oid=1), initial_load=True)
    with pytest.raises(base.InvalidIDError):
      l.update_item(6, clue='stuff')

  def test_query_all(self):
    init = [
      Entry('c1', 'a1', 'p1', tags={'a', 'b'}, oid=2),
      Entry('c1', 'a1', 'b', tags={'a'}, oid=1),
      Entry('c1', 'a1', 'a', tags=set(), oid=11),
      Entry('c1', 'a1', 'p1', tags={'a'}, oid=3),
      Entry('c1', 'a1', 'p1', tags={'b'}, oid=5),
      Entry('c1', 'a1', 'p1', tags={'dog'}, oid=10),
    ]
    matcher = EntryMatcherTags(set())
    exp = [0, 1, 2, 3, 4, 5]

    l = CheatSheet()
    for i in init: l.add_item(i, initial_load=True)
    ret = l.query_items(matcher)
    assert len(ret) == len(exp)
    for ind in exp:
      assert init[ind] in ret

  def test_query_tag(self):
    init = [
      Entry('c1', 'a1', 'p1', tags={'a', 'b'}, oid=2),
      Entry('c1', 'a1', 'b', tags={'a'}, oid=1),
      Entry('c1', 'a1', 'a', tags=set(), oid=11),
      Entry('c1', 'a1', 'p1', tags={'a'}, oid=3),
      Entry('c1', 'a1', 'p1', tags={'b'}, oid=5),
      Entry('c1', 'a1', 'p1', tags={'dog'}, oid=10),
    ]
    matcher = EntryMatcherTags({'a'})
    exp = [0, 1, 2, 3]

    l = CheatSheet()
    for i in init: l.add_item(i, initial_load=True)
    ret = l.query_items(matcher)
    assert len(ret) == len(exp)
    for ind in exp:
      assert init[ind] in ret

  def test_query_tag_or(self):
    init = [
      Entry('c1', 'a1', 'p1', tags={'a', 'b'}, oid=2),
      Entry('c1', 'a1', 'b', tags={'a'}, oid=1),
      Entry('c1', 'a1', 'a', tags=set(), oid=11),
      Entry('c1', 'a1', 'p1', tags={'a'}, oid=3),
      Entry('c1', 'a1', 'p1', tags={'b'}, oid=5),
      Entry('c1', 'a1', 'p1', tags={'dog'}, oid=10),
    ]
    matcher = EntryMatcherTags({'a', 'b'}, sjb.cs.classes.SEARCH_OR)
    exp = [0, 1, 2, 3, 4]

    l = CheatSheet()
    for i in init: l.add_item(i, initial_load=True)
    ret = l.query_items(matcher)
    assert len(ret) == len(exp)
    for ind in exp:
      assert init[ind] in ret

  def test_query_tag_and(self):
    init = [
      Entry('c1', 'a1', 'p1', tags={'a', 'b'}, oid=2),
      Entry('c1', 'a1', 'b', tags={'a'}, oid=1),
      Entry('c1', 'a1', 'a', tags=set(), oid=11),
      Entry('c1', 'a1', 'p1', tags={'a'}, oid=3),
      Entry('c1', 'a1', 'p1', tags={'b'}, oid=5),
      Entry('c1', 'a1', 'p1', tags={'dog'}, oid=10),
    ]
    matcher = EntryMatcherTags({'a', 'b'}, sjb.cs.classes.SEARCH_AND)
    exp = [0, 1]

    l = CheatSheet()
    for i in init: l.add_item(i, initial_load=True)
    ret = l.query_items(matcher)
    assert len(ret) == len(exp)
    for ind in exp:
      assert init[ind] in ret

  def test_validate_new_item(self):
    l = CheatSheet()
    l.add_item(Entry(clue='clue', answer='answer', primary='prim', tags=set()))
    l.validate()

  def test_validate_non_int_id(self):
    l = CheatSheet()
    l.add_item(Entry(clue='clue', answer='answer', primary='prim', tags=set(), oid=1.2), initial_load=True)
    with pytest.raises(base.ValidationError):
      l.validate()

  def test_validate_invalid_clue(self):
    l = CheatSheet()
    l.add_item(Entry(clue='clue', answer='answer', primary='prim', tags=set()))
    l.validate()
    with pytest.raises(base.ValidationError):
      l = CheatSheet()
      l.add_item(Entry(clue='', answer='answer', primary='prim', tags=set()))
      l.validate()
    with pytest.raises(base.ValidationError):
      l = CheatSheet()
      l.add_item(Entry(clue=341, answer='answer', primary='prim', tags=set()))
      l.validate()
    with pytest.raises(base.ValidationError):
      l = CheatSheet()
      l.add_item(Entry(clue=None, answer='answer', primary='prim', tags=set()))
      l.validate()

  def test_validate_invalid_answer(self):
    l = CheatSheet()
    l.add_item(Entry(clue='clue', answer='answer', primary='prim', tags=set()))
    l.validate()
    with pytest.raises(base.ValidationError):
      l = CheatSheet()
      l.add_item(Entry(clue='clue', answer='', primary='prim', tags=set()))
      l.validate()
    with pytest.raises(base.ValidationError):
      l = CheatSheet()
      l.add_item(Entry(clue='clue', answer=None, primary='prim', tags=set()))
      l.validate()
    with pytest.raises(base.ValidationError):
      l = CheatSheet()
      l.add_item(Entry(clue='clue', answer=345, primary='prim', tags=set()))
      l.validate()

  def test_validate_invalid_primary(self):
    l = CheatSheet()
    l.add_item(Entry(clue='clue', answer='answer', primary='prim', tags=set()))
    l.validate()
    with pytest.raises(base.ValidationError):
      l = CheatSheet()
      l.add_item(Entry(clue='clue', answer='', primary='', tags=set()))
      l.validate()
    with pytest.raises(base.ValidationError):
      l = CheatSheet()
      l.add_item(Entry(clue='clue', answer=None, primary=None, tags=set()))
      l.validate()
    with pytest.raises(base.ValidationError):
      l = CheatSheet()
      l.add_item(Entry(clue='clue', answer=345, primary=341, tags=set()))
      l.validate()

  def test_validate_invalid_tags(self):
    l = CheatSheet()
    l.add_item(Entry(clue='c', answer='a', primary='prim', tags={'a'}))
    l.validate()
    with pytest.raises(base.ValidationError):
      l = CheatSheet()
      l.add_item(Entry(clue='c', answer='a', primary='prim', tags={'a', ''}))
      l.validate()
    with pytest.raises(base.ValidationError):
      l = CheatSheet()
      l.add_item(Entry(clue='c', answer='a', primary='prim', tags={'a', 34}))
      l.validate()
    with pytest.raises(base.ValidationError):
      l = CheatSheet()
      l.add_item(Entry(clue='c', answer='a', primary='prim', tags={'a', None}))
      l.validate()

  def test_validate_primary_is_tag(self):
    l = CheatSheet()
    l.add_item(Entry(clue='c', answer='a', primary='prim', tags={'a'}))
    l.validate()
    with pytest.raises(base.ValidationError):
      l = CheatSheet()
      l.add_item(Entry(clue='c', answer='a', primary='prim', tags={'a', 'prim'}))
      l.validate()

  def test_validate_nonset_tags(self):
    l = CheatSheet()
    l.add_item(Entry(clue='c', answer='a', primary='prim', tags={'a'}))
    l.validate()
    with pytest.raises(base.ValidationError):
      l = CheatSheet()
      l.add_item(Entry(clue='c', answer='a', primary='prim', tags=set()))
      l.get_item(1).tags = ['a']
      l.validate()

  def test_primary_map(self):
    l = CheatSheet()
    i1 = l.add_item(Entry(clue='c', answer='a', primary='p1', tags={'a'}))
    i2 = l.add_item(Entry(clue='c', answer='a', primary='p1', tags={'a'}))
    i3 = l.add_item(Entry(clue='c', answer='a', primary='p3', tags={'a'}))
    i4 = l.add_item(Entry(clue='c', answer='a', primary='p4', tags={'a'}))

    assert i1 in l.primary_map['p1']
    assert i2 in l.primary_map['p1']
    assert [i3] == l.primary_map['p3']
    assert [i4] == l.primary_map['p4']
    assert len(l.primary_map['p1']) == 2
    l.remove_item(3)
    assert 'p3' not in l.primary_map

  @mock.patch('time.time', mock_time)
  def test_to_dict(self):
    l = CheatSheet(version='version str', modified_date=1234.1234)
    init = [
      Entry('c1', 'a1', 'p1', tags={'a', 'b'}, oid=2),
      Entry('c2', 'a2', 'p2', tags={'a', 'a'}, oid=1),
      Entry('c3', 'a3', 'p2', tags=set(), oid=11)
    ]
    init_exp = [{
      'oid': 2,
      'clue': 'c1', 'answer': 'a1', 'primary': 'p1', 'tags': ['a', 'b']
    },{
      'oid': 1,
      'clue': 'c2', 'answer': 'a2', 'primary': 'p2', 'tags': ['a']
    },{
      'oid': 11,
      'clue': 'c3', 'answer': 'a3', 'primary': 'p2', 'tags': []
    }]
    new = [
      Entry('c4', 'a4', 'p4', tags={'c'}),
      Entry('c5', 'a5', 'p5', tags={'d'})
    ]
    new_exp = [{
      'oid': 12,
      'clue': 'c4', 'answer': 'a4', 'primary': 'p4', 'tags': ['c']
    },{
      'oid': 13,
      'clue': 'c5', 'answer': 'a5', 'primary': 'p5', 'tags': ['d']
    }]

    for i in init:
      l.add_item(i, initial_load=True)
    for n in new:
      l.add_item(n, initial_load=False)

    d = l.to_dict()['cheatsheet']
    assert d['version'] == 'version str'
    assert d['modified_date'] == MOCK_TIME
    assert len(d.keys()) == 3
    todos = d['entries']
    assert len(todos) == 5
    for e in init_exp:
      assert e in todos
    for e in new_exp:
      assert e in todos

  def test_from_dict(self):
    d = {'cheatsheet': {
      'version': 'version str',
      'modified_date': 1234.1234,
      'entries': [{
        'oid': 2,
        'clue': 'c1', 'answer': 'a1', 'primary': 'p1', 'tags': ['a', 'b'],
      },{
        'oid': 1,
        'clue': 'c2', 'answer': 'a2', 'primary': 'p2', 'tags': ['a']
      },{
        'oid': 11,
        'clue': 'c3', 'answer': 'a3', 'primary': 'p2', 'tags': []
      },{
        'oid': 12,
        'clue': 'c4', 'answer': 'a4', 'primary': 'p4', 'tags': ['c']
      },{
        'oid': 13,
        'clue': 'c5', 'answer': 'a5', 'primary': 'p5', 'tags': ['d']
      }]}}
    exp_items = [
      Entry('c1', 'a1', 'p1', tags={'a', 'b'}, oid=2),
      Entry('c2', 'a2', 'p2', tags={'a', 'a'}, oid=1),
      Entry('c3', 'a3', 'p2', tags=set(), oid=11),
      Entry('c4', 'a4', 'p4', tags={'c'}, oid=12),
      Entry('c5', 'a5', 'p5', tags={'d'}, oid=13)
    ]
    l = CheatSheet.from_dict(d)
    assert not l.modified
    assert l.version == 'version str'
    assert l.modified_date == 1234.1234
    assert l.size() == 5
    for t in l.items:
      assert t in exp_items
    assert l.tag_set == {'p1','p2','p4','p5','a','b','c','d'}

  def test_entry_matcher_bad_andor(self):
    with pytest.raises(base.IllegalStateError):
      EntryMatcherTags({'a'}, andor=14)
    with pytest.raises(base.IllegalStateError):
      EntryMatcherTags({'a'}, andor=None)
    with pytest.raises(base.IllegalStateError):
      EntryMatcherTags({'a'}, andor='zebra')
