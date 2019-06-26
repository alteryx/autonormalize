import pytest

import classes
from classes import BitIndexSet, LHSs, DfdDependencies, Dependencies, find_closure

from normalize import normalize


def test_to_set():
    attr = set([1, 2, 5, 6, 9])
    bit_set = BitIndexSet(10, attr)
    assert attr == bit_set.to_set()


def test_is_subset():
    bit_set_1 = BitIndexSet(10, set([1, 2, 5, 6, 9]))
    bit_set_2 = BitIndexSet(10, set([1, 5, 6]))
    bit_set_3 = BitIndexSet(10, set([1, 2, 7]))
    assert bit_set_1.is_subset(bit_set_1)
    assert bit_set_2.is_subset(bit_set_1)
    assert not bit_set_1.is_subset(bit_set_2)
    assert not bit_set_3.is_subset(bit_set_1)


def test_is_superset():
    bit_set_1 = BitIndexSet(10, set([1, 2, 5, 6, 9]))
    bit_set_2 = BitIndexSet(10, set([1, 5, 6]))
    bit_set_3 = BitIndexSet(10, set([1, 2, 7]))
    assert bit_set_1.is_superset(bit_set_1)
    assert bit_set_1.is_superset(bit_set_2)
    assert not bit_set_2.is_superset(bit_set_1)
    assert not bit_set_1.is_superset(bit_set_3)


def test_get_compliment():
    bit_set_1 = BitIndexSet(10, set([1, 2, 5, 6, 9]))
    bit_set_2 = BitIndexSet(10, set([1, 2, 7]))
    assert bit_set_1.get_compliment(4).to_set() == set([0, 3, 7, 8])
    assert bit_set_2.get_compliment(0).to_set() == set([3, 4, 5, 6, 8, 9])


def test_difference():
    bit_set_1 = BitIndexSet(10, set([1, 2, 5, 6, 9]))
    bit_set_2 = BitIndexSet(10, set([1, 5, 6]))
    bit_set_1.difference(bit_set_2)
    assert bit_set_1.to_set() == set([2, 9])
    bit_set_2.difference(BitIndexSet(10, set([3, 8, 9])))
    assert bit_set_2.to_set() == set([1, 5, 6])


def test_eq():
    bit_set_1 = BitIndexSet(10, set([1, 2, 5, 6, 9]))
    bit_set_2 = BitIndexSet(10, set([1, 2, 5, 6, 9]))
    assert bit_set_1 == bit_set_2


def test_hash():
    bit_set_1 = BitIndexSet(10, set([1, 2, 5, 6, 9]))
    bit_set_2 = BitIndexSet(10, set([1, 5, 6]))
    set_test = set()
    set_test.add(bit_set_1)
    set_test.add(bit_set_2)
    assert bit_set_1 in set_test
    assert bit_set_2 in set_test


def test_iter():
    lst = [1, 2, 5, 6, 9]
    bit_set_1 = BitIndexSet(10, set(lst))
    compare = []
    for x in bit_set_1:
        compare.append(x)
    assert lst == compare


def test_all_sets_and_add_dep():
    lhss = LHSs([0, 1, 2, 4, 6, 7, 8, 9, 10, 14, 15, 16], True)
    assert lhss.all_sets() == set()
    bit_index_1 = BitIndexSet(16, set([1, 2, 4]))
    lhss.add_dep(bit_index_1)
    assert lhss.all_sets() == set([bit_index_1])
    bit_index_2 = BitIndexSet(16, set([1, 4, 7, 8, 9]))
    bit_index_3 = BitIndexSet(16, set([8]))
    lhss.add_dep(bit_index_2)
    lhss.add_dep(bit_index_3)
    assert lhss.all_sets() == set([bit_index_1, bit_index_2, bit_index_3])


def test_contains_subset():
    lhss = LHSs([0, 1, 2, 4, 6, 7, 8, 9, 10, 14, 15, 16], True)
    bit_index_1 = BitIndexSet(16, set([1, 2, 4]))
    lhss.add_dep(bit_index_1)
    bit_index_2 = BitIndexSet(16, set([1, 4, 7, 8, 9]))
    bit_index_3 = BitIndexSet(16, set([8]))
    lhss.add_dep(bit_index_2)
    lhss.add_dep(bit_index_3)
    assert lhss.contains_subset(bit_index_1)
    assert lhss.contains_subset(BitIndexSet(15, set([8, 9, 10])))
    assert not lhss.contains_subset(BitIndexSet(15, set([14, 15, 16])))


def test_contains_superset():
    lhss = LHSs([0, 1, 2, 4, 6, 7, 8, 9, 10, 14, 15, 16], True)
    bit_index_1 = BitIndexSet(16, set([1, 2, 4]))
    lhss.add_dep(bit_index_1)
    bit_index_2 = BitIndexSet(16, set([1, 4, 7, 8, 9]))
    bit_index_3 = BitIndexSet(16, set([8]))
    lhss.add_dep(bit_index_2)
    lhss.add_dep(bit_index_3)
    assert lhss.contains_superset(bit_index_1)
    assert lhss.contains_superset(BitIndexSet(15, set([1, 4, 8])))
    assert not lhss.contains_superset(BitIndexSet(15, set([1, 4, 8, 10])))


def test_LHSs_add_dep_and_all_sets():
    lhss = LHSs(set([1, 2, 4, 5, 6, 7, 8, 10, 13, 14, 15]), True)
    assert lhss.all_sets() == set()
    bis_1 = BitIndexSet(16, set([1, 2, 4]))
    lhss.add_dep(bis_1)
    assert lhss.all_sets() == set([bis_1])
    bis_2 = BitIndexSet(16, set([15]))
    lhss.add_dep(bis_2)
    assert lhss.all_sets() == set([bis_1, bis_2])
    bis_3 = BitIndexSet(16, set([1, 4, 13]))
    lhss.add_dep(bis_3)
    assert lhss.all_sets() == set([bis_1, bis_2, bis_3])


def test_contains_subset_lhss():
    lhss = LHSs(set([1, 2, 4, 5, 6, 7, 8, 10, 13, 14, 15]), True)
    bis_1 = BitIndexSet(16, set([1, 2, 4]))
    lhss.add_dep(bis_1)
    bis_2 = BitIndexSet(16, set([15]))
    lhss.add_dep(bis_2)
    bis_3 = BitIndexSet(16, set([1, 4, 13]))
    lhss.add_dep(bis_3)
    assert lhss.contains_subset(bis_1)
    assert lhss.contains_subset(BitIndexSet(16, set([1, 4, 5, 6, 13])))
    assert not lhss.contains_subset(BitIndexSet(16, set([1, 2, 14])))


def test_contains_superset_lhss():
    lhss = LHSs(set([1, 2, 4, 5, 6, 7, 8, 10, 13, 14, 15]), True)
    bis_1 = BitIndexSet(16, set([1, 2, 4]))
    lhss.add_dep(bis_1)
    bis_2 = BitIndexSet(16, set([15]))
    lhss.add_dep(bis_2)
    bis_3 = BitIndexSet(16, set([1, 4, 13]))
    lhss.add_dep(bis_3)
    assert lhss.contains_superset(bis_1)
    assert lhss.contains_superset(BitIndexSet(16, set([1, 4])))
    assert not lhss.contains_superset(BitIndexSet(16, set([14, 15])))


def test_add_LHS():
    dependencies = DfdDependencies(["name", "age", "height", "weight", "location", "speed", "rating", "experience", "mother"])
    dependencies.add_LHS(1, BitIndexSet(9, set([0])))
    assert dependencies.serialize() == {"rating": [], "age": [["name"]], "height": [], "weight": [], "location": [], "speed": [],
        "experience": [], "mother": [], "name": []}
    dependencies.add_LHS(3, BitIndexSet(9, set([1, 2])))
    assert dependencies.serialize() == {
        "rating": [], "age": [["name"]], "height": [],
        "weight": [["age", "height"]], "location": [], "speed": [],
        "experience": [], "mother": [], "name": []
        }
    dependencies.add_LHS(3, BitIndexSet(9, set([0])))
    assert dependencies.serialize() == {"rating": [], "age": [["name"]], "height": [], "weight": [["name"], ["age", "height"]], "location": [], "speed": [],
        "experience": [], "mother": [], "name": []}


def test_add_LHSs():
    lhss_weight = LHSs(set([0, 1, 2, 4, 5, 6, 7]), True)
    lhss_weight.add_dep(BitIndexSet(9, set([0])))
    lhss_weight.add_dep(BitIndexSet(9, set([1, 2])))
    lhss_age = LHSs(set([0, 2, 4, 5, 6, 7]), True)
    lhss_age.add_dep(BitIndexSet(9, set([0])))
    dependencies = DfdDependencies(["name", "age", "height", "weight", "location", "speed", "rating", "experience", "mother"])
    dependencies.add_LHSs(1, lhss_age)
    assert dependencies.serialize() == {"rating": [], "age": [["name"]], "height": [], "weight": [], "location": [], "speed": [],
        "experience": [], "mother": [], "name": []}
    dependencies.add_LHSs(3, lhss_weight)
    assert dependencies.serialize() == {"rating": [], "age": [["name"]], "height": [], "weight": [["name"], ["age", "height"]], "location": [], "speed": [],
        "experience": [], "mother": [], "name": []}


def test_add_and_remove_dep():
    dep_dic = {'A': [], 'B': [['A']], 'C': [['D', 'G'], ['A']],
        'D': [['A'], ['C', 'G']], 'E': [['D', 'G'], ['A'], ['C']],
        'F': [['A'], ['B']], 'G': [['A'], ['C', 'D']]}
    dependencies = Dependencies(dep_dic)
    dependencies.add_dep('B', ['C'])
    assert dependencies.serialize() == {'A': [],
        'B': [['A'], ['C']], 'C': [['D', 'G'], ['A']],
        'D': [['A'], ['C', 'G']], 'E': [['D', 'G'], ['A'], ['C']],
        'F': [['A'], ['B']], 'G': [['A'], ['C', 'D']]}
    dependencies.remove_dep('B', ['C'])
    assert dependencies.serialize() == dep_dic


def test_tuple_relations():
    dep_dic = {'A': [], 'B': [['A']], 'C': [['D', 'G'], ['A']],
        'D': [['A'], ['C', 'G']], 'E': [['D', 'G'], ['A'], ['C']]}
    dependencies = Dependencies(dep_dic)
    tuple_comp = [(['D', 'G'], 'C'), (['A'], 'C'), (['A'], 'B'),
        (['D', 'G'], 'E'), (['A'], 'E'), (['C'], 'E'),
        (['A'], 'D'), (['C', 'G'], 'D')]
    assert dependencies.tuple_relations() == tuple_comp


def test_remove_implied_extroneous():
    dep_dic = {'A': [], 'B': [['A']], 'C': [['A', 'B']]}
    dependencies = Dependencies(dep_dic)
    dependencies.remove_implied_extroneous()
    assert dependencies.serialize() == {'A': [], 'B': [['A']], 'C': [['A']]}


# def test_remove_redundant():
#     dep_dic = {'A': [], 'B': [['A']], 'C': [['B']], 'D': [['A'], ['C']]}
#     dependencies = Dependencies(dep_dic)
#     dependencies.remove_redundant()
#     assert dependencies.serialize() == {'A': [], 'B': [['A']], 'C': [['B']], 'D': [['A']]}


def test_find_candidate_keys():
    dep_dic = {
        'A': [['B']], 'B': [['E'], ['A', 'D']], 'C': [['E', 'F']],
        'D': [['A']], 'E': [['A']], 'F': [['G']], 'G': []}
    dependencies = Dependencies(dep_dic)
    dependencies.prep()
    assert dependencies.find_candidate_keys() == [{'A', 'G'}, {'B', 'G'}, {'E', 'G'}]


def test_find_partial_deps():
    dep_dic = {
        'A': [['B']], 'B': [['E'], ['A', 'D']], 'C': [['E', 'F']],
        'D': [['A']], 'E': [['A']], 'F': [['G']], 'G': []}
    dependencies = Dependencies(dep_dic)
    dependencies.prep()
    partial_deps = [(['A'], 'D'), (['G'], 'F')]
    assert dependencies.find_partial_deps() == partial_deps


def test_find_closure():
    dep_dic = {
        'A': [['B']], 'B': [['E'], ['A', 'D']], 'C': [['E', 'F']],
        'D': [['A']], 'E': [['A']], 'F': [['G']], 'G': []}
    dependencies = Dependencies(dep_dic)
    rels = dependencies.tuple_relations()
    clos = {'A', 'B', 'D', 'E'}
    assert find_closure(rels, ['A']) == clos


# def test_remove_partial_deps():
#     dep_dic = {
#         'A': [['B']], 'B': [['E'], ['A', 'D']], 'C': [['E', 'F']],
#         'D': [['A']], 'E': [['A']], 'F': [['G']], 'G': []}
#     dependencies = Dependencies(dep_dic)
#     dependencies.prep()
#     new = remove_partial_deps(dependencies)
#     for x in new:
#         assert x.find_partial_deps() == []
    # assert len(new) == 3
    # assert new[0].serialize() == {'A': [['B']], 'B': [['A']], 'C': [['A', 'G']], 'G': []}
    # assert new[1].serialize() == {'F': [['G']], 'G': []}
    # assert new[2].serialize() == {'A': [], 'D': [['A']], 'E': [['A']]}


def test_from_rels():
    dep_dic = {
        'A': [['B']], 'B': [['E'], ['A', 'D']], 'C': [['E', 'F']],
        'D': [['A']], 'E': [['A']], 'F': [['G']], 'G': []}
    dependencies = Dependencies(dep_dic)
    rels = dependencies.tuple_relations()
    dependencies_new = Dependencies.from_rels(rels)
    assert dependencies.serialize() == dependencies_new.serialize()


def test_find_trans_deps():
    dep_dic = {
        'A': [], 'B': [], 'C': [], 'D': [['F']],
        'E': [['A', 'B', 'C', 'D']], 'F': [['A', 'B']]}
    dep = Dependencies(dep_dic)
    dep.prep()
    assert dep.find_trans_deps() == [(['F'], 'D')]


# def test_remove_trans_deps():
#     dep_dic = {
#         'A': [], 'B': [], 'C': [], 'D': [['F']],
#         'E': [['A', 'B', 'C', 'D']], 'F': [['A', 'B']]}
#     dep = Dependencies(dep_dic)
#     dep.prep()
#     new = remove_trans_deps(dep)
#     for x in new:
#         assert x.find_trans_deps() == []


def test_normalize():
    dep_dic = {
        'A': [], 'B': [], 'C': [], 'D': [['F']],
        'E': [['A', 'B', 'C', 'D']], 'F': [['A', 'B']]}
    dep = Dependencies(dep_dic)
    new = normalize(dep)
    for x in new:
        assert x.find_trans_deps() == []
        assert x.find_partial_deps() == []



# TO DO: organize tests into different files, real life dataset example test!!!!


