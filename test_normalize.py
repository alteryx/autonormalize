import pytest

from classes import Dependencies

from normalize import normalize, find_most_comm, split_on_dep


def test_normalize():

    # how to test that relations remain the same???

    # check that there are no new relations?
    # there can be less however?
    dep_dic = {
        'A': [], 'B': [], 'C': [], 'D': [['F']],
        'E': [['A', 'B', 'C', 'D']], 'F': [['A', 'B']]}
    dep = Dependencies(dep_dic)
    new = normalize(dep)
    dep_dic = dep.serialize()
    for x in new:
        assert x.find_trans_deps() == []
        assert x.find_partial_deps() == []
        dic = x.serialize()
        for rhs in dic:
            for lhs in dic[rhs]:
                assert lhs in dep_dic[rhs]


def test_find_most_comm():
    rels = [(set(['a']), 'b'), (set(['b']), 'c'), (set(['b']), 'a'),
            (set(['d']), 'a')]
    assert find_most_comm(rels) == set(['b'])
    rels = [(set(['a', 'c']), 'b'), (set(['b']), 'c'), (set(['b']), 'a'),
            (set(['d']), 'a'), (set(['a', 'c']), 'b')]
    assert find_most_comm(rels) == set(['b'])


def test_split_on_dep():
    dep_dic = {'A': [], 'B': [], 'C': [['A'], ['B']], 'D': [['B']]}
    new = split_on_dep(['B'], Dependencies(dep_dic))
    assert new[0].serialize() == {'A': [], 'B': []}
    assert new[1].serialize() == {'B': [], 'C': [['B']], 'D': [['B']]}