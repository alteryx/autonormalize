from autonormalize.classes import (
    Dependencies,
    DfdDependencies,
    LHSs,
    find_closure
)


def assert_equal_dependency_dics(dep1, dep2):

    assert set(dep1.keys()) == set(dep2.keys())

    for rhs in dep1.keys():
        one = map(frozenset, dep1[rhs])
        two = map(frozenset, dep2[rhs])
        assert set(one) == set(two)


def assert_equal_cand_keys(keys1, keys2):
    assert set(map(frozenset, keys1)) == set(map(frozenset, keys2))


def to_frozenset(elem):
    return (frozenset(elem[0]), elem[1])


def assert_equal_tuple_rels(rels1, rels2):
    one = map(to_frozenset, rels1)
    two = map(to_frozenset, rels2)
    assert set(one) == set(two)


def test_all_sets_and_add_dep():
    lhss = LHSs(['a', 'b', 'c', 'd', 'e', 'f', 'g'])
    assert lhss.all_sets() == set()
    set_1 = frozenset(['a', 'c', 'd'])
    lhss.add_dep(set_1)
    assert lhss.all_sets() == set([set_1])
    set_2 = frozenset(['a', 'c', 'e', 'f', 'g'])
    set_3 = frozenset(['b'])
    lhss.add_dep(set_2)
    lhss.add_dep(set_3)
    assert lhss.all_sets() == set([set_1, set_2, set_3])


def test_contains_subset():
    lhss = LHSs(['a', 'b', 'c', 'd', 'e', 'f', 'g'])
    set_1 = frozenset(['a', 'c', 'd'])
    lhss.add_dep(set_1)
    set_2 = frozenset(['a', 'c', 'e', 'f', 'g'])
    set_3 = frozenset(['g'])
    lhss.add_dep(set_2)
    lhss.add_dep(set_3)
    assert lhss.contains_subset(set_1)
    assert lhss.contains_subset(frozenset(['a', 'c', 'd', 'f']))
    assert not lhss.contains_subset(frozenset(['b']))


def test_contains_superset():
    lhss = LHSs(['a', 'b', 'c', 'd', 'e', 'f', 'g'])
    set_1 = frozenset(['a', 'c', 'd', 'e', 'g'])
    lhss.add_dep(set_1)
    set_2 = frozenset(['a', 'c', 'e', 'f'])
    set_3 = frozenset(['b', 'c'])
    lhss.add_dep(set_2)
    lhss.add_dep(set_3)
    assert lhss.contains_superset(set_1)
    assert lhss.contains_superset(frozenset(['a', 'c', 'f']))
    assert not lhss.contains_superset(frozenset(['a', 'b', 'c']))


def test_LHSs_add_dep_and_all_sets():
    lhss = LHSs(['a', 'b', 'c', 'd', 'e', 'f', 'g'])
    assert lhss.all_sets() == set()
    set_1 = frozenset(['a', 'c', 'd', 'e', 'g'])
    lhss.add_dep(set_1)
    assert lhss.all_sets() == set([set_1])
    set_2 = frozenset(['a', 'c', 'e', 'f'])
    lhss.add_dep(set_2)
    assert lhss.all_sets() == set([set_1, set_2])
    set_3 = frozenset(['b', 'c'])
    lhss.add_dep(set_3)
    assert lhss.all_sets() == set([set_1, set_2, set_3])


def test_add_unique_lhs():
    dependencies = DfdDependencies(["name", "age", "height", "weight", "location", "speed", "rating", "experience", "mother"])
    dependencies.add_unique_lhs("name")
    assert_equal_dependency_dics(dependencies.serialize(), {"rating": [["name"]], "age": [["name"]],
                                                            "height": [["name"]], "weight": [["name"]],
                                                            "location": [["name"]], "speed": [["name"]],
                                                            "experience": [["name"]], "mother": [["name"]], "name": []})


def test_add_LHSs():
    lhss_weight = LHSs(set(["name", "age", "height", "weight", "location", "speed", "rating", "experience", "mother"]))
    lhss_weight.add_dep(frozenset(["name"]))
    lhss_weight.add_dep(frozenset(["age", "height"]))
    lhss_age = LHSs(set(["name", "age", "height", "weight", "location", "speed", "rating", "experience", "mother"]))
    lhss_age.add_dep(frozenset(["name"]))
    dependencies = DfdDependencies(["name", "age", "height", "weight", "location", "speed", "rating", "experience", "mother"])
    dependencies.add_LHSs("age", lhss_age)
    assert_equal_dependency_dics(dependencies.serialize(), {"rating": [], "age": [["name"]], "height": [], "weight": [],
                                                            "location": [], "speed": [],
                                                            "experience": [], "mother": [], "name": []})
    dependencies.add_LHSs("weight", lhss_weight)
    assert_equal_dependency_dics(dependencies.serialize(), {"rating": [], "age": [["name"]], "height": [],
                                                            "weight": [["name"], ["age", "height"]], "location": [], "speed": [],
                                                            "experience": [], "mother": [], "name": []})


def test_add_and_remove_dep():
    dep_dic = {'A': [], 'B': [['A']], 'C': [['D', 'G'], ['A']],
               'D': [['A'], ['C', 'G']], 'E': [['D', 'G'], ['A'], ['C']],
               'F': [['A'], ['B']], 'G': [['A'], ['C', 'D']]}
    dependencies = Dependencies(dep_dic)
    dependencies.add_dep('B', ['C'])
    assert_equal_dependency_dics(dependencies.serialize(),
                                 {'A': [], 'B': [['A'], ['C']], 'C': [['D', 'G'], ['A']],
                                  'D': [['A'], ['C', 'G']], 'E': [['D', 'G'], ['A'], ['C']],
                                  'F': [['A'], ['B']], 'G': [['A'], ['C', 'D']]})
    dependencies.remove_dep('B', ['C'])
    assert_equal_dependency_dics(dependencies.serialize(), dep_dic)


def test_tuple_relations():
    dep_dic = {'A': [], 'B': [['A']], 'C': [['D', 'G'], ['A']],
               'D': [['A'], ['C', 'G']], 'E': [['D', 'G'], ['A'], ['C']]}
    dependencies = Dependencies(dep_dic)
    tuple_comp = [(['D', 'G'], 'C'), (['A'], 'C'), (['A'], 'B'),
                  (['D', 'G'], 'E'), (['A'], 'E'), (['C'], 'E'),
                  (['A'], 'D'), (['C', 'G'], 'D')]
    assert_equal_tuple_rels(dependencies.tuple_relations(), tuple_comp)
    # assert set(dependencies.tuple_relations()) == set(tuple_comp)


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
    dependencies.remove_implied_extroneous()
    assert_equal_cand_keys(dependencies.find_candidate_keys(), [{'A', 'G'}, {'B', 'G'}, {'E', 'G'}])


def test_find_partial_deps():
    dep_dic = {
        'A': [['B']], 'B': [['E'], ['A', 'D']], 'C': [['E', 'F']],
        'D': [['A']], 'E': [['A']], 'F': [['G']], 'G': []}
    dependencies = Dependencies(dep_dic, ['A', 'G'])
    dependencies.remove_implied_extroneous()
    partial_deps = [(['A'], 'D'), (['G'], 'F'), (['A'], 'B'), (['A'], 'E')]
    assert_equal_tuple_rels(dependencies.find_partial_deps(), partial_deps)


def test_find_closure():
    dep_dic = {
        'A': [['B']], 'B': [['E'], ['A', 'D']], 'C': [['E', 'F']],
        'D': [['A']], 'E': [['A']], 'F': [['G']], 'G': []}
    dependencies = Dependencies(dep_dic)
    rels = dependencies.tuple_relations()
    clos = {'A', 'B', 'D', 'E'}
    assert find_closure(rels, ['A']) == clos


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
    dep = Dependencies(dep_dic, ['A', 'B', 'C'])
    dep.remove_implied_extroneous()
    assert dep.find_trans_deps() == [(['F'], 'D')]


def test_equi_atttrs():
    dep_dic = {'A': [['B']], 'B': [['A']], 'C': [], 'D': [['A']]}
    dep = Dependencies(dep_dic, ['A', 'C'])
    assert dep.equiv_attrs('A', 'B')
    assert not dep.equiv_attrs('A', 'D')
